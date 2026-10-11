# Scripts

All scripts only read files (and `git` objects); none of them executes code from the audited projects. Run them with `python3 -I` (Python 3.9+, no dependencies).

## Setup

```bash
git clone https://gitlab.com/droppyformac1/thunderstorm.git
git clone https://github.com/abue-ammar/tinycast.git

# xanalyze.py, fuzzy.py, sens.py and binscan.py reuse Thunderstorm's own lexer and
# fingerprinting code, unmodified. Copy it next to the scripts:
mkdir -p scripts/ts_verify
cp thunderstorm/verify/similarity.py thunderstorm/verify/compare.py scripts/ts_verify/
```

## What each script does

| Script | Purpose | Example |
|---|---|---|
| `xanalyze.py` | Type names (with the `Thunderstorm` prefix removed), functions, properties, string literals, comments, enum case sets and ordered literal sequences that also occur anywhere in Tinycast's full git history, each with the date and commit of its first appearance. Optional extra codebases are measured the same way as baselines. | `python3 -I scripts/xanalyze.py out/ thunderstorm/Sources tinycast [name=/path/to/baseline ...]` |
| `fuzzy.py` | Near-duplicate prose: for every comment block and multi-word string literal, the most similar comment/string in Tinycast's history (word-trigram Jaccard or containment). | `python3 -I scripts/fuzzy.py out/prose.json tinycast thunderstorm=thunderstorm/Sources` |
| `sens.py` | Sensitivity of `compare.py`'s renamed-fingerprint share to the window size `K` and to the `DF_MAX` boilerplate filter. | `python3 -I scripts/sens.py tinycast thunderstorm=thunderstorm/Sources` |
| `fieldmd.py` | Parses `__swift5_fieldmd` in a thin arm64 Mach-O and lists every type's stored-property / enum-case names. Use `lipo -thin arm64 Droppy.app/Contents/MacOS/Droppy -output droppy_arm64` first. | `python3 -I scripts/fieldmd.py droppy_arm64 fields.json` |
| `binscan.py` | Scans an app bundle's bytes and `.strings` tables for Thunderstorm type names (10-11 source vs. the 09-26 droplet source), Tinycast identifiers and Tinycast UI strings. | `python3 -I scripts/binscan.py out.json Droppy.app thunderstorm/Sources droplet-0926/ tinycast` |
| `anchor_excerpts.py` | Produces the excerpts in `EVIDENCE.md`: finds an anchor text in a file (optionally at a git revision) and returns the surrounding lines with exact line numbers. Input: `evidence_spec.json`. | `python3 -I scripts/anchor_excerpts.py scripts/evidence_spec.json thunderstorm tinycast out.json` |

## Thunderstorm's own check

```bash
python3 -I thunderstorm/verify/compare.py --ours thunderstorm/Sources --theirs tinycast --history
```

This reproduces the README's numbers (longest run 5 lines, literal fingerprints 0.24%). The same run also prints the renamed-fingerprint share (2.77%), which the README does not report. See `REPORT.md` §5 for why this tool cannot detect rewritten code.

## Droppy binaries

The official DMGs are available from the URLs returned by `https://getdroppy.app/api/releases/latest` (e.g. `https://droppy-releases.jordylegrand.workers.dev/app-releases/Droppy-16.0.0.dmg`; betas under `/app-releases/beta/`). Checksums of the files analysed are in `data/binary/dmg_checksums.txt`. Mount read-only (`hdiutil attach -readonly -nobrowse -noautoopen`) and copy the app out; there is no need to run it.
