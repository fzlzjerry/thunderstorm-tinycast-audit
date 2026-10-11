#!/usr/bin/env python3
"""Near-duplicate prose: comments and multi-word string literals.

For every comment / UI sentence on our side, find the Tinycast (all history)
comment or string with the highest word-trigram Jaccard. Paraphrase tools keep
many trigrams of explanatory prose; independent authors rarely share them.
Usage: fuzzy.py OUTJSON TINYCAST_REPO NAME=PATH [NAME=PATH ...]
"""
import collections, json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ts_verify"))
import similarity as sim  # noqa

OUT, TC = sys.argv[1], sys.argv[2]
SIDES = [a.split("=", 1) for a in sys.argv[3:]]
STOP = set("the a an of to and or in on for is it its that this with as be by at from so are was not no".split())


def words(s):
    s = re.sub(r"(?i)thunderstorm|tinycast|droppy", "app", s)
    return [w for w in re.findall(r"[a-z0-9']+", s.lower())]


def grams(ws):
    return {tuple(ws[i:i + 3]) for i in range(len(ws) - 2)}


def prose(text, lang):
    out = []
    # consecutive // lines form one comment block; /* */ is one block
    pend, pend_line, last_line = [], None, -5
    for m in re.finditer(r"//+[^\n]*|/\*.*?\*/", text, re.S):
        line = text.count("\n", 0, m.start()) + 1
        raw = m.group(0)
        if raw.startswith("/*"):
            body = re.sub(r"^/\*+|\*+/$", "", raw).strip()
            body = re.sub(r"\s*\n\s*\*?\s*", " ", body)
            out.append(("comment", line, body))
            continue
        body = re.sub(r"^/+\s*", "", raw).strip()
        if line == last_line + 1 and pend:
            pend.append(body)
        else:
            if pend:
                out.append(("comment", pend_line, " ".join(pend)))
            pend, pend_line = [body], line
        last_line = line
    if pend:
        out.append(("comment", pend_line, " ".join(pend)))
    try:
        _, _, strs = sim.lex(text, lang)
    except Exception:
        strs = []
    for v, line, ml in strs:
        if not ml and len(v.split()) >= 4 and len(v) < 300:
            out.append(("string", line, v))
    return out


def collect_tree(root):
    items = []
    for p in sorted(sim.walk(root, sim.CODE_EXT)):
        lg = sim.lang_of(p)
        for kind, line, body in prose(sim.read_text(p), lg):
            ws = words(body)
            if len(ws) >= 6:
                items.append((f"{os.path.relpath(p, root)}:{line}", kind, body, grams(ws)))
    return items


def git(*a):
    return subprocess.run(["git", "-C", TC] + list(a), capture_output=True, text=True, check=True).stdout


def collect_history():
    first = {}
    cur = None
    for row in git("log", "--all", "--reverse", "--format=C\t%ct\t%h", "--raw", "--no-abbrev", "--no-renames").splitlines():
        if row.startswith("C\t"):
            _, ct, h = row.split("\t")
            cur = (int(ct), h)
        elif row.startswith(":") and cur:
            sha = row.split("\t")[0].split()[3]
            if sha not in first:
                first[sha] = cur
    wanted = {}
    for row in git("rev-list", "--all", "--objects").splitlines():
        sha, _, path = row.partition(" ")
        if path and sim.lang_of(path) and sha not in wanted and "node_modules" not in path and not path.startswith(("website/", "third-party/")):
            wanted[sha] = path
    items = {}
    batch = subprocess.Popen(["git", "-C", TC, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha, path in wanted.items():
        batch.stdin.write(f"{sha}\n".encode()); batch.stdin.flush()
        hd = batch.stdout.readline().decode().split()
        if len(hd) < 3:
            continue
        data = batch.stdout.read(int(hd[2])); batch.stdout.read(1)
        if hd[1] != "blob" or int(hd[2]) > 3_000_000:
            continue
        for kind, line, body in prose(data.decode("utf-8", "replace"), sim.lang_of(path)):
            ws = words(body)
            if len(ws) >= 6:
                key = " ".join(ws)
                when = first.get(sha, (9e12, "?"))
                if key not in items or when[0] < items[key][3][0]:
                    items[key] = (f"{path}:{line}", kind, body, when, grams(ws))
    batch.stdin.close(); batch.wait()
    return list(items.values())


def main():
    import datetime
    tc = collect_history()
    inv = collections.defaultdict(list)
    for i, it in enumerate(tc):
        for g in it[4]:
            inv[g].append(i)
    df_cut = 200
    result = {}
    for name, path in SIDES:
        ours = collect_tree(path)
        hits = []
        for label, kind, body, gs in ours:
            cnt = collections.Counter()
            for g in gs:
                lst = inv.get(g, ())
                if len(lst) > df_cut or all(w in STOP for w in g):
                    continue
                for i in lst:
                    cnt[i] += 1
            best = None
            for i, c in cnt.most_common(8):
                tg = tc[i][4]
                inter = len(gs & tg)
                j = inter / len(gs | tg)
                ct = inter / min(len(gs), len(tg))
                score = max(j, ct if inter >= 6 else 0)
                if best is None or score > best[0]:
                    best = (score, i, j, ct, inter)
            if best and best[0] >= 0.5:
                t = tc[best[1]]
                hits.append(dict(score=round(best[0], 3), jaccard=round(best[2], 3), containment=round(best[3], 3),
                                 shared_trigrams=best[4], kind=kind, ours=label, text=body[:400],
                                 tc=t[0], tc_kind=t[1], tc_text=t[2][:400],
                                 tc_first=datetime.datetime.fromtimestamp(t[3][0], datetime.timezone.utc).strftime("%Y-%m-%d") if t[3][0] < 9e12 else None,
                                 tc_commit=t[3][1]))
        hits.sort(key=lambda h: -h["score"])
        n_c = sum(1 for o in ours if o[1] == "comment"); n_s = len(ours) - n_c
        result[name] = {"prose_items": len(ours), "comments": n_c, "strings": n_s,
                        "hits_ge_0.5": len(hits), "hits_ge_0.7": sum(h["score"] >= 0.7 for h in hits),
                        "hits_ge_0.9": sum(h["score"] >= 0.9 for h in hits), "items": hits}
        print(name, {k: v for k, v in result[name].items() if k != "items"}, flush=True)
    json.dump(result, open(OUT, "w"), indent=1, ensure_ascii=False)


main()
