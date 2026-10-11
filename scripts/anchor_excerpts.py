#!/usr/bin/env python3
"""Locate anchor text in a file (optionally at a git revision) and print an excerpt
with exact line numbers. Spec is JSON list of
  {id, side: ts|tc, path, rev (optional), anchor, before, after}
Usage: anchor_excerpts.py SPEC.json TS_REPO TC_REPO OUT.json
"""
import json, subprocess, sys

SPEC, TS, TC, OUT = sys.argv[1:5]
spec = json.load(open(SPEC))
res = []
for s in spec:
    repo = TS if s["side"] == "ts" else TC
    if s.get("rev"):
        r = subprocess.run(["git", "-C", repo, "show", f"{s['rev']}:{s['path']}"], capture_output=True, text=True)
        text = r.stdout if r.returncode == 0 else ""
    else:
        text = open(f"{repo}/{s['path']}", encoding="utf-8").read()
    lines = text.split("\n")
    hit = next((i for i, l in enumerate(lines) if s["anchor"] in l), None)
    if hit is None:
        res.append({**s, "error": "anchor not found"})
        print("NOT FOUND", s["id"], s["side"], s["path"], s["anchor"][:50])
        continue
    a = max(0, hit - s.get("before", 2)); b = min(len(lines), hit + s.get("after", 6) + 1)
    res.append({**s, "start": a + 1, "end": b, "text": "\n".join(lines[a:b])})
json.dump(res, open(OUT, "w"), indent=1, ensure_ascii=False)
print("ok", sum(1 for r in res if "text" in r), "/", len(res))
