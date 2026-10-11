#!/usr/bin/env python3
"""Static scan of a Droppy.app bundle against Thunderstorm / Tinycast sources.

Reads every file of the bundle as bytes (nothing is executed) and extracts
printable UTF-8 runs, plus the keys/values of .strings/.stringsdict plists.
Usage: binscan.py OUTJSON APP TS_SOURCES DROPLET_0926_SRC TINYCAST_REPO
"""
import collections, json, os, plistlib, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "ts_verify"))
import similarity as sim  # noqa: E402

OUT, APP, TS, D26, TC = sys.argv[1:6]
RUN = re.compile(rb"(?:[\x20-\x7e]|[\xc2-\xdf][\x80-\xbf]|[\xe0-\xef][\x80-\xbf]{2}|[\xf0-\xf4][\x80-\xbf]{3}){4,}")
DECL = re.compile(r"\b(?:struct|class|enum|protocol|actor)\s+([A-Za-z_][A-Za-z0-9_]*)")
VARD = re.compile(r"\b(?:var|let)\s+([A-Za-z_][A-Za-z0-9_]*)\s*[:=]")


def bundle_text():
    runs, plist_strings = set(), set()
    for dp, _, fns in os.walk(APP):
        for fn in fns:
            p = os.path.join(dp, fn)
            if os.path.islink(p):
                continue
            data = open(p, "rb").read()
            if fn.endswith((".strings", ".stringsdict")):
                try:
                    obj = plistlib.loads(data)
                    def walk(o):
                        if isinstance(o, dict):
                            for k, v in o.items():
                                plist_strings.add(str(k)); walk(v)
                        elif isinstance(o, list):
                            for v in o: walk(v)
                        elif isinstance(o, str):
                            plist_strings.add(o)
                    walk(obj)
                except Exception:
                    pass
            for m in RUN.finditer(data):
                runs.add(m.group(0).decode("utf-8", "ignore"))
    return runs, plist_strings


def tree_info(root):
    types, props, strs = set(), set(), set()
    for p in sim.walk(root, {".swift"}):
        t = sim.read_text(p)
        types.update(DECL.findall(t))
        props.update(VARD.findall(t))
        try:
            _, _, ss = sim.lex(t, "swift")
        except Exception:
            ss = []
        for v, _, ml in ss:
            if not ml and 3 <= len(v) <= 300 and "\\(" not in v:
                strs.add(v)
    return types, props, strs


def tinycast_history_info():
    types, props, strs = {}, {}, {}
    first = {}
    cur = None
    out = subprocess.run(["git", "-C", TC, "log", "--all", "--reverse", "--format=C\t%ct\t%h", "--raw", "--no-abbrev", "--no-renames"],
                         capture_output=True, text=True).stdout
    for row in out.splitlines():
        if row.startswith("C\t"):
            _, ct, h = row.split("\t"); cur = (int(ct), h)
        elif row.startswith(":") and cur:
            sha = row.split("\t")[0].split()[3]
            first.setdefault(sha, cur)
    listing = subprocess.run(["git", "-C", TC, "rev-list", "--all", "--objects"], capture_output=True, text=True).stdout
    wanted = {}
    for row in listing.splitlines():
        sha, _, path = row.partition(" ")
        if path.endswith(".swift") and sha not in wanted and not path.startswith("third-party/"):
            wanted[sha] = path
    b = subprocess.Popen(["git", "-C", TC, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    def note(d, k, sha, path):
        w = first.get(sha, (9e12, "?"))
        if k not in d or w[0] < d[k][0]:
            d[k] = (w[0], w[1], path)
    for sha, path in wanted.items():
        b.stdin.write(f"{sha}\n".encode()); b.stdin.flush()
        hd = b.stdout.readline().decode().split()
        if len(hd) < 3:
            continue
        data = b.stdout.read(int(hd[2])); b.stdout.read(1)
        if hd[1] != "blob":
            continue
        t = data.decode("utf-8", "replace")
        for n in DECL.findall(t): note(types, n, sha, path)
        for n in VARD.findall(t): note(props, n, sha, path)
        try:
            _, _, ss = sim.lex(t, "swift")
        except Exception:
            ss = []
        for v, _, ml in ss:
            if not ml and 3 <= len(v) <= 300 and "\\(" not in v:
                note(strs, v, sha, path)
    b.stdin.close(); b.wait()
    return types, props, strs


def date(ts):
    import datetime
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d") if ts < 9e12 else None


def main():
    runs, pstr = bundle_text()
    allstr = runs | pstr
    blob = "\n".join(allstr)
    ts_types, ts_props, ts_strs = tree_info(TS)
    d_types, d_props, d_strs = tree_info(D26)
    tc_types, tc_props, tc_strs = tinycast_history_info()

    def present_ident(name):
        return name in blob  # identifiers appear inside type descriptors / mangled names

    res = {"app": APP, "bundle_strings": len(allstr)}
    # 1. which Thunderstorm version shipped
    pub_t = {t for t in ts_types if t.startswith("Thunderstorm")}
    d26_t = {t for t in d_types if t.startswith("Thunderstorm")}
    only_pub, only_d26, both = pub_t - d26_t, d26_t - pub_t, pub_t & d26_t
    res["types_public_1011"] = {"n": len(pub_t), "present": sum(present_ident(t) for t in pub_t)}
    res["types_only_public"] = {"n": len(only_pub), "present": sum(present_ident(t) for t in only_pub),
                                "present_list": sorted(t for t in only_pub if present_ident(t))[:400],
                                "absent_sample": sorted(t for t in only_pub if not present_ident(t))[:400]}
    res["types_only_droplet0926"] = {"n": len(only_d26), "present": sum(present_ident(t) for t in only_d26),
                                     "present_list": sorted(t for t in only_d26 if present_ident(t)),
                                     "absent_list": sorted(t for t in only_d26 if not present_ident(t))}
    res["types_both"] = {"n": len(both), "present": sum(present_ident(t) for t in both)}
    # 2. Tinycast identifiers (non-prefixed) present in binary, not declared in Thunderstorm 10-11
    tc_only = {}
    for kind, table, mine in (("type", tc_types, ts_types | d_types), ("prop", tc_props, ts_props | d_props)):
        for n, (t, c, path) in table.items():
            if len(n) < 10 or n in mine:
                continue
            if len(re.findall(r"[A-Z]", n)) < 2:
                continue
            if re.search(r"(?<![A-Za-z0-9_])" + re.escape(n) + r"(?![A-Za-z0-9_])", blob):
                tc_only[f"{kind}:{n}"] = {"tc_first": date(t), "commit": c, "path": path}
    res["tinycast_identifiers_in_binary_not_in_thunderstorm_src"] = tc_only
    # 3. strings: Tinycast UI literals (multi-word) in bundle
    rows = []
    for s, (t, c, path) in tc_strs.items():
        if len(s.split()) < 3 or len(s) < 12:
            continue
        if s in allstr or (len(s) >= 20 and s in blob):
            rows.append({"text": s, "tc_first": date(t), "commit": c, "tc_path": path,
                         "in_ts_1011": s in ts_strs, "in_droplet_0926": s in d_strs})
    rows.sort(key=lambda r: (r["in_ts_1011"], r["tc_first"] or ""))
    res["tinycast_multiword_strings_in_bundle"] = {"n": len(rows),
                                                   "not_in_ts_1011": sum(not r["in_ts_1011"] for r in rows),
                                                   "items": rows}
    # 4. specific markers
    markers = ["Tinycast", "tinycast", "Abue", "abue-ammar", "DROPPY_EXT_DIR", "DROPPY_EXT_COMMAND", "@raycast/api",
               "paste-sequentially", "Paste One by One", "Paste Sequentially", "openWithBundleID", "iconSymbol",
               "Look up a word", "Select text in another app first.", "Keep Calculating", "hoverHighlightArmed",
               "hoverDisarmToken", "armingDistance", "restingPoint", "hoverArmed", "startsSection", "beginsGroup",
               "ThunderstormTheme", "ThunderstormStyle", "ThunderstormScrollChannel", "ThunderstormHoverTracker",
               "ThunderstormArmedHover", "ThunderstormBarButtonChrome", "ThunderstormMenuCircleButton",
               "ThunderstormHeaderBackButton", "ThunderstormRightClickCatcher", "ThunderstormPointerState",
               "ThunderstormWorkspace", "ThunderstormWindowLayout", "ThunderstormQuicklink", "ThunderstormSnippet",
               "ThunderstormExtensionSession", "ThunderstormAIChat", "ThunderstormMCP", "ThunderstormQuickAction",
               "ThunderstormCalcParser", "ThunderstormCalcLexer", "ThunderstormNotesWindow", "ThunderstormMeeting",
               "ThunderstormCamera", "ThunderstormDictionary", "ThunderstormMenuSearch", "ThunderstormLibraryBackup",
               "ThunderstormRaycastConfigImport", "ThunderstormClipboardSequence", "ThunderstormEmojiSurface",
               "ThunderstormUninstaller", "Search your Mac", "Search for apps and commands"]
    res["markers"] = {m: (m in blob) for m in markers}
    json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k not in ("tinycast_multiword_strings_in_bundle", "tinycast_identifiers_in_binary_not_in_thunderstorm_src", "types_only_public")}, ensure_ascii=False, indent=1)[:6000])
    print("types_only_public:", {k: v for k, v in res["types_only_public"].items() if k in ("n", "present")})
    print("tinycast ids in binary not in TS src:", len(tc_only))
    print("tinycast multiword strings in bundle:", res["tinycast_multiword_strings_in_bundle"]["n"],
          "of which not in TS 10-11:", res["tinycast_multiword_strings_in_bundle"]["not_in_ts_1011"])


main()
