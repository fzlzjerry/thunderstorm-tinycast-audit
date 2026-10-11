# Thunderstorm vs. Tinycast: an independent code-provenance audit

On 11 October 2026 the author of [Tinycast](https://github.com/abue-ammar/tinycast), a free AGPL-3.0 launcher for macOS, publicly accused [Droppy](https://getdroppy.app) of copying Tinycast's code base into Thunderstorm, the launcher built into Droppy. The same day Droppy published [Thunderstorm's source](https://gitlab.com/droppyformac1/thunderstorm) with a comparison tool reporting 0.24% shared code.

This repository is an independent audit of the two code bases, their histories, Droppy's public records and three released Droppy builds.

- **Full report (English):** [REPORT.md](REPORT.md)
- **完整报告（中文）：** [REPORT.zh-CN.md](REPORT.zh-CN.md)
- **Side-by-side evidence with permalinks:** [EVIDENCE.md](EVIDENCE.md)
- **Addendum, public timeline before Tinycast (submitted by Droppy):** [ADDENDUM.md](ADDENDUM.md)

## Findings in brief

1. **Thunderstorm did take code and design from Tinycast, and Droppy recorded this itself.** A NOTICE in Droppy's public Droplet Store ([MR !66](https://gitlab.com/droppyformac1/droplets/-/merge_requests/66), 26 Sep) says two private commits on 21 Sep ported the Tinycast launcher's mechanisms and look "one to one" into the built-in Thunderstorm, and that the 26 Sep rewrite kept "the same metrics and behaviour" and was still credited to Tinycast.
2. **The direction is proven independently.** The Tinycast-shaped launcher components (hover arming, `BarButton` / `BarButtonChrome`, `RightClickCatcher` with a nested `CatcherView`, a UUID-stamped scroll request, …) are **absent** from Droppy 15.2.2-beta.1 (signed 9 Sep) and **present** in Droppy 16.0.0 (signed 27 Sep), with Tinycast's names, nesting and field order. They existed in Tinycast's public repository weeks to months earlier (June–September).
3. **Droppy 16.0 shipped these components to users without any Tinycast credit**, together with Tinycast's search prompt and a Tinycast quicklink field name. No licence notice in the app mentions Tinycast. This contradicts the statement in Droppy's blog post that "Not a single Droppy user ever received his code."
4. **The "rewritten" source published on 11 Oct still contains traceable Tinycast material, with the credit removed:** 13 comments / UI strings with ≥0.9 similarity to Tinycast (independent baselines: 0), a whole colour-opacity table, animation constants, coined API names, legacy data-model keys and an AI prompt skeleton, which is more than the leftover "texts, not code" the blog post describes. Several of these sentences were written by Tinycast's outside contributors weeks before the collaboration.
5. **It is not a wholesale copy.** There is no large verbatim copying (longest identical run: 5 lines, the same as unrelated baselines), no rename-only file ports, and large parts of Thunderstorm (Raycast-extension runtime, AI, calculator parser, backup, dictionary, …) are different implementations built on Droppy's own services. Whether the code base as a whole was "fed to AI" can be neither proven nor ruled out.
6. **Thunderstorm's name and icon predate Tinycast** (Internet Archive, 12 May 2026), so the icon accusation does not hold. Droppy's public Discord and Reddit posts also show Thunderstorm named in a public release on 20 March 2026 and offered to every beta user on 14 June 2026 as a Spotlight-style launcher with system actions, before Tinycast's repository existed ([ADDENDUM.md](ADDENDUM.md)). Many of its current features (calculator, quicklinks, snippets, Raycast extensions, window layouts, backup), however, first appear around or after the September collaboration.
7. Thunderstorm's own `compare.py` reproduces its 0.24%, but that metric cannot detect rewritten code: in a control experiment a 100%-derived rewrite scored 0.000. The same run's renamed-fingerprint share (2.77%, 1.6–2.2× the baselines) is not reported in its README.

The report grades each finding, lists what was downgraded or refuted during verification, and states what cannot be determined (Thunderstorm's repository has no development history; Droppy's private history and unreleased builds were not available).

## About this audit

- **Not a legal opinion.** It establishes technical facts about origin and similarity. Whether any of it infringes the AGPL is a question for lawyers.
- **Method.** Module-by-module comparison of both code bases (including Tinycast's full git history), git forensics, public timeline reconstruction from archived pages and GitLab merge requests, quantitative similarity against two unrelated macOS Swift code bases as baselines, and static analysis of the official Droppy 15.2.2-beta.1, 16.0.0 and 16.0.1 DMGs (nothing was executed).
- **AI-assisted.** The analysis was carried out under human direction with AI agents (Claude Code): one agent per module, each finding then attacked by an independent verifier agent. Every key claim cites a file and line, a commit or a public URL, and can be reproduced with the scripts here.
- **Corrections welcome.** If you are involved, or find an error, please open an issue.

## Repository layout

| Path | Contents |
|---|---|
| `REPORT.md`, `REPORT.zh-CN.md` | Full report in English and Chinese |
| `EVIDENCE.md` | ~20 strongest items as side-by-side excerpts with permalinks, plus the binary comparison table |
| `scripts/` | Analysis scripts and usage ([scripts/README.md](scripts/README.md)) |
| `data/` | Raw outputs of `compare.py` (full history, prefix stripped, embedded JS, 26 Sep droplet), sensitivity table, identifier / string / comment / enum matches, prose matches |
| `data/binary/` | Stored-property tables of Thunderstorm types in the three Droppy builds, bundle scans, DMG checksums |

Not included: Droppy installers or code extracted from them, the 26 Sep droplet source (see MR !66), raw AI-agent transcripts, or anything from the baseline code bases.

## Quick verification

```bash
git clone https://gitlab.com/droppyformac1/thunderstorm.git
git clone https://github.com/abue-ammar/tinycast.git

# A comment from Tinycast's third day (30 Jun 2026) inside a Droppy-only file:
grep -n "Selection wins over hover when a row is both" thunderstorm/Sources/ThunderstormDropletLibraryRow.swift
git -C tinycast log --all --reverse -S"Selection wins over hover when a row is both" --format="%h %ad %an" --date=short | head -1

# Thunderstorm's own comparison
python3 -I thunderstorm/verify/compare.py --ours thunderstorm/Sources --theirs tinycast --history
```

## License

- **Report text, evidence write-ups and data** (`README.md`, `REPORT.md`, `REPORT.zh-CN.md`, `EVIDENCE.md`, `data/`): [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE). You may share and adapt them, including commercially, as long as you give credit and link back to this repository.
- **Scripts** (`scripts/`): [MIT](scripts/LICENSE).
- **Exception, third-party excerpts:** quoted source code, comments and documentation from Tinycast and Thunderstorm (in `EVIDENCE.md`, the reports and `data/`) remain the property of their copyright holders under their own licences: Tinycast, AGPL-3.0-or-later, © Abue Ammar and contributors; Thunderstorm, GPL-3.0 with the Commons Clause, © Jordy Spruit. They are reproduced only for the purposes of commentary and criticism and are not covered by the licences above.
