#!/usr/bin/env python3
"""Cross-analysis of Thunderstorm vs Tinycast (all git history), with baselines.

Signals that are robust to the systematic "Thunderstorm" prefix rename and to
AI paraphrase, which verify/compare.py does not measure:
  A. type names (de-prefixed) declared on both sides
  B. string literals shared verbatim (UI text, keys, messages)
  C. comments shared (normalised)
  D. enum case-name sets/orders shared
  E. ordered runs of string literals (data tables) shared
  F. per-file best counterpart by renamed fingerprints
Every Tinycast hit carries the date of the first commit that introduced it.
Usage: xanalyze.py OUTDIR TS_SOURCES TINYCAST_REPO [BASELINE_NAME=PATH ...]
"""
import collections, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "ts_verify"))
import similarity as sim  # noqa: E402

OUT, TS, TC = sys.argv[1], sys.argv[2], sys.argv[3]
BASELINES = [a.split("=", 1) for a in sys.argv[4:]]
os.makedirs(OUT, exist_ok=True)

DECL = re.compile(r"\b(struct|class|enum|protocol|actor|typealias)\s+([A-Za-z_][A-Za-z0-9_]*)")
FUNC = re.compile(r"\bfunc\s+([A-Za-z_][A-Za-z0-9_]*)")
VARD = re.compile(r"\b(?:var|let)\s+([A-Za-z_][A-Za-z0-9_]*)")
CASE = re.compile(r"^\s*(?:indirect\s+)?case\s+([^\n]+)", re.M)
PREFIX = re.compile(r"\bThunderstorm(?=[A-Z_])|\bthunderstorm(?=[A-Z])")


def deprefix(s):
    return PREFIX.sub("", s)


def humps(n):
    return len(re.findall(r"[A-Z][a-z0-9]", n)) + (1 if n[:1].islower() else 0)


def comments(text):
    out = []
    for m in re.finditer(r"//+[^\n]*|/\*.*?\*/", text, re.S):
        line = text.count("\n", 0, m.start()) + 1
        body = re.sub(r"^/+\s*|^/\*+|\*+/$", "", m.group(0)).strip()
        body = re.sub(r"\s*\n\s*\*?\s*", " ", body)
        norm = re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", body.lower())).strip()
        if len(norm) >= 30 and len(norm.split()) >= 5 and not norm.startswith("mark"):
            out.append((norm, line, body[:200]))
    return out


def enum_cases(text):
    """enum name -> ordered list of case names (top-level cases of that enum body)."""
    res = {}
    for m in re.finditer(r"\benum\s+([A-Za-z_][A-Za-z0-9_]*)[^{]*\{", text):
        start, depth, i = m.end(), 1, m.end()
        while i < len(text) and depth:
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        body = text[start:i - 1]
        # keep only depth-0 lines of the body
        flat, d = [], 0
        for ch in body:
            if ch == "{":
                d += 1
            elif ch == "}":
                d -= 1
            elif d == 0:
                flat.append(ch)
        names = []
        for cm in CASE.finditer("".join(flat)):
            for part in re.split(r",(?![^(]*\))", cm.group(1)):
                nm = re.match(r"\s*`?([A-Za-z_][A-Za-z0-9_]*)", part)
                if nm:
                    names.append(nm.group(1))
        if len(names) >= 4:
            res[m.group(1)] = names
    return res


class Side:
    def __init__(self):
        self.types = collections.defaultdict(list)    # name -> [(label, line)]
        self.funcs = collections.defaultdict(list)
        self.vars = collections.defaultdict(list)
        self.strings = collections.defaultdict(list)  # norm -> [(label, line, raw)]
        self.comments = collections.defaultdict(list)
        self.enums = []                               # (label, enum, cases)
        self.strseq = []                              # (label, [(norm, line)])

    def add(self, label, text, lang, strip=False):
        if strip:
            text = deprefix(text)
        if lang == "swift":
            for m in DECL.finditer(text):
                self.types[m.group(2)].append((label, text.count("\n", 0, m.start()) + 1))
            for m in FUNC.finditer(text):
                self.funcs[m.group(1)].append((label, text.count("\n", 0, m.start()) + 1))
            for m in VARD.finditer(text):
                self.vars[m.group(1)].append((label, text.count("\n", 0, m.start()) + 1))
            for en, cs in enum_cases(text).items():
                self.enums.append((label, en, cs))
        try:
            _, _, strs = sim.lex(text, lang)
        except Exception:
            strs = []
        seq = []
        for val, line, ml in strs:
            v = val.strip()
            if ml or len(v) > 400:
                continue
            n = re.sub(r"\s+", " ", v)
            n = re.sub(r"(?i)thunderstorm|tinycast|droppy", "<APP>", n)
            seq.append((n, line))
            if len(n) >= 14 and (" " in n or "." in n or "_" in n):
                self.strings[n].append((label, line, v[:200]))
        self.strseq.append((label, seq))
        for norm, line, raw in comments(text):
            self.comments[norm].append((label, line, raw))


def lang(path):
    return sim.lang_of(path)


def load_tree(root, strip=False):
    s = Side()
    for p in sorted(sim.walk(root, sim.CODE_EXT)):
        lg = lang(p)
        if lg:
            s.add(os.path.relpath(p, root), sim.read_text(p), lg, strip)
    return s


def git(*args):
    return subprocess.run(["git", "-C", TC] + list(args), capture_output=True, text=True, check=True).stdout


def blob_first_seen():
    """blob sha -> (unix time, short commit, subject) of the earliest commit introducing it."""
    seen = {}
    cur = None
    out = git("log", "--all", "--reverse", "--date-order", "--format=C\t%H\t%ct\t%s", "--raw", "--no-abbrev", "--no-renames")
    for row in out.splitlines():
        if row.startswith("C\t"):
            _, h, ct, subj = row.split("\t", 3)
            cur = (int(ct), h[:9], subj[:90])
        elif row.startswith(":") and cur:
            meta = row.split("\t")[0].split()
            sha = meta[3]
            if set(sha) != {"0"} and (sha not in seen or cur[0] < seen[sha][0]):
                seen[sha] = cur
    return seen


def load_history():
    s = Side()
    listing = git("rev-list", "--all", "--objects")
    wanted = {}
    for row in listing.splitlines():
        sha, _, path = row.partition(" ")
        if path and lang(path) and sha not in wanted and "node_modules" not in path and not path.startswith("website/"):
            wanted[sha] = path
    batch = subprocess.Popen(["git", "-C", TC, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha, path in wanted.items():
        batch.stdin.write(f"{sha}\n".encode()); batch.stdin.flush()
        header = batch.stdout.readline().decode().split()
        if len(header) < 3:
            continue
        data = batch.stdout.read(int(header[2])); batch.stdout.read(1)
        if header[1] != "blob" or int(header[2]) > 3_000_000:
            continue
        s.add(f"{path}@{sha}", data.decode("utf-8", "replace"), lang(path))
    batch.stdin.close(); batch.wait()
    return s


def first(hits, fs):
    best = None
    for h in hits:
        label = h[0]
        sha = label.split("@")[1] if "@" in label else None
        when = fs.get(sha) if sha else None
        if when and (best is None or when[0] < best[0][0]):
            best = (when, h)
    if not best:
        h = hits[0]
        return {"tc": f"{h[0].split('@')[0]}:{h[1]}", "first_seen": None}
    (t, c, subj), h = best
    import datetime
    return {"tc": f"{h[0].split('@')[0]}:{h[1]}", "first_seen": datetime.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"),
            "commit": c, "subject": subj}


COMMON_WORDS = set("""view model store state item items row list screen settings page panel button
mode kind status style result results entry action actions command commands option options config
configuration error value item key type data info manager service provider context section sections
""".split())


def distinctive_type(n):
    words = re.findall(r"[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z0-9]+", n)
    return len(words) >= 2 and not all(w.lower() in COMMON_WORDS for w in words)


def main():
    print("loading tinycast history ...", flush=True)
    fs = blob_first_seen()
    tc = load_history()
    print("tinycast blobs:", len(tc.strseq), flush=True)
    sides = {"thunderstorm": load_tree(TS, strip=True)}
    for name, path in BASELINES:
        sides[name] = load_tree(path)
    summary = {}
    for name, side in sides.items():
        res = {}
        # A. types
        tnames = [n for n in side.types if len(n) >= 4]
        shared = [n for n in tnames if n in tc.types]
        dist = [n for n in tnames if distinctive_type(n)]
        dshared = [n for n in dist if n in tc.types]
        res["types"] = {"declared": len(tnames), "shared": len(shared), "distinctive_declared": len(dist),
                        "distinctive_shared": len(dshared),
                        "distinctive_shared_rate": round(len(dshared) / max(1, len(dist)), 4),
                        "items": sorted([dict(name=n, ts=f"{side.types[n][0][0]}:{side.types[n][0][1]}", **first(tc.types[n], fs))
                                         for n in dshared], key=lambda d: d["name"])}
        # funcs / vars (distinctive: >=3 humps, len>=14)
        for kind, table, ctable in (("funcs", side.funcs, tc.funcs), ("vars", side.vars, tc.vars)):
            dn = [n for n in table if humps(n) >= 3 and len(n) >= 14]
            ds = [n for n in dn if n in ctable]
            res[kind] = {"distinctive_declared": len(dn), "distinctive_shared": len(ds),
                         "rate": round(len(ds) / max(1, len(dn)), 4),
                         "items": sorted([dict(name=n, ts=f"{table[n][0][0]}:{table[n][0][1]}", **first(ctable[n], fs)) for n in ds],
                                         key=lambda d: d["name"])}
        # B. strings
        ss = [n for n in side.strings if n in tc.strings]
        res["strings"] = {"candidates": len(side.strings), "shared": len(ss),
                          "rate": round(len(ss) / max(1, len(side.strings)), 4),
                          "items": sorted([dict(text=n[:200], ts=f"{side.strings[n][0][0]}:{side.strings[n][0][1]}", **first(tc.strings[n], fs))
                                           for n in ss], key=lambda d: d["ts"])}
        # C. comments
        cs = [n for n in side.comments if n in tc.comments]
        res["comments"] = {"candidates": len(side.comments), "shared": len(cs),
                           "rate": round(len(cs) / max(1, len(side.comments)), 4),
                           "items": [dict(text=side.comments[n][0][2], ts=f"{side.comments[n][0][0]}:{side.comments[n][0][1]}", **first(tc.comments[n], fs))
                                     for n in cs]}
        # D. enum case sets
        tc_enums = collections.defaultdict(list)
        for label, en, cases in tc.enums:
            tc_enums[frozenset(cases)].append((label, en, cases))
        tc_by_case = collections.defaultdict(set)
        for i, (label, en, cases) in enumerate(tc.enums):
            for c in cases:
                tc_by_case[c].add(i)
        enum_hits = []
        for label, en, cases in side.enums:
            cand = collections.Counter()
            for c in set(cases):
                for i in tc_by_case.get(c, ()):
                    cand[i] += 1
            best = None
            for i, _ in cand.most_common(20):
                tl, ten, tcs = tc.enums[i]
                inter = len(set(cases) & set(tcs))
                jac = inter / len(set(cases) | set(tcs))
                if best is None or jac > best[0]:
                    best = (jac, i, inter)
            if best and best[0] >= 0.5 and best[2] >= 4:
                tl, ten, tcs = tc.enums[best[1]]
                # longest common subsequence for order
                a, b = cases, tcs
                dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
                for x in range(len(a)):
                    for y in range(len(b)):
                        dp[x + 1][y + 1] = dp[x][y] + 1 if a[x] == b[y] else max(dp[x][y + 1], dp[x + 1][y])
                h = (tl, 0)
                enum_hits.append(dict(ts=f"{label}:{en}", ts_cases=len(cases), tc=f"{tl.split('@')[0]}:{ten}", tc_cases=len(tcs),
                                      shared=best[2], jaccard=round(best[0], 3), lcs=dp[-1][-1],
                                      first_seen=first([(tl, 0)], fs).get("first_seen"), cases=cases[:60]))
        # dedupe by ts enum keeping best
        bt = {}
        for e in enum_hits:
            if e["ts"] not in bt or (e["jaccard"], e["lcs"]) > (bt[e["ts"]]["jaccard"], bt[e["ts"]]["lcs"]):
                bt[e["ts"]] = e
        res["enums"] = {"enums_declared": len(side.enums), "matched": len(bt),
                        "items": sorted(bt.values(), key=lambda e: (-e["shared"], -e["jaccard"]))}
        # E. ordered string-literal runs (len>=4, each literal len>=2), first per our file
        idx = collections.defaultdict(list)
        for fid, (label, seq) in enumerate(tc.strseq):
            for j, (n, _) in enumerate(seq):
                if len(n) >= 2:
                    idx[n].append((fid, j))
        runs = []
        for label, seq in side.strseq:
            live = {}
            for i, (n, line) in enumerate(seq):
                nxt = {}
                hits = idx.get(n, ()) if len(n) >= 2 else ()
                if len(hits) <= 3000:
                    for fid, j in hits:
                        st = live.get((fid, j - 1))
                        nxt[(fid, j)] = st if st is not None else i
                for (fid, j), st in live.items():
                    if (fid, j + 1) not in nxt and i - st >= 4:
                        runs.append((label, st, i - 1, fid, j))
                live = nxt
            for (fid, j), st in live.items():
                if len(seq) - st >= 4:
                    runs.append((label, st, len(seq) - 1, fid, j))
        best = {}
        for label, a, b, fid, j in runs:
            k = (label, a)
            if k not in best or (b - a) > (best[k][2] - best[k][1]):
                best[k] = (label, a, b, fid, j)
        ritems = []
        seqs = dict(side.strseq)
        for (label, a, b, fid, j) in best.values():
            seq = seqs[label]
            tl, tseq = tc.strseq[fid]
            ln = b - a + 1
            vals = [s for s, _ in seq[a:b + 1]]
            # skip runs made of very short/common tokens only
            if sum(len(v) for v in vals) < 30:
                continue
            ritems.append(dict(length=ln, ts=f"{label}:{seq[a][1]}-{seq[b][1]}",
                               tc=f"{tl.split('@')[0]}:{tseq[j - ln + 1][1]}-{tseq[j][1]}",
                               first_seen=first([(tl, 0)], fs).get("first_seen"), sample=vals[:12]))
        ritems.sort(key=lambda r: -r["length"])
        res["string_runs"] = {"runs_ge4": len(ritems), "longest": ritems[0]["length"] if ritems else 0,
                              "total_literals_in_runs": sum(r["length"] for r in ritems), "items": ritems[:300]}
        summary[name] = {k: {kk: vv for kk, vv in v.items() if kk != "items"} for k, v in res.items()}
        with open(os.path.join(OUT, f"x_{name}.json"), "w") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        print(name, json.dumps(summary[name], ensure_ascii=False), flush=True)
    with open(os.path.join(OUT, "x_summary.json"), "w") as f:
        json.dump(summary, f, indent=1)


if __name__ == "__main__":
    main()
