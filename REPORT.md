# Code Provenance Audit: Thunderstorm (Droppy) vs. Tinycast

> 中文版：[REPORT.zh-CN.md](REPORT.zh-CN.md) · Side-by-side evidence: [EVIDENCE.md](EVIDENCE.md)

> **Subjects:** Thunderstorm, the launcher built into the macOS app Droppy (GitLab `droppyformac1/thunderstorm`, snapshot `2ecde78`), and Tinycast (GitHub `abue-ammar/tinycast`, `126c998d`, all 990 commits / 120 remote branches)
> **Audit date:** 2026-10-12
> **Question:** Is Thunderstorm copied from (derived from) Tinycast?
> **Method:** module-by-module source comparison, git history forensics, public timeline reconstruction, quantitative similarity measurement against independent baselines, adversarial verification of every finding, and static comparison of the shipped Droppy binaries 15.2.2-beta.1 (before the collaboration), 16.0.0 and 16.0.1. This report states technical facts and inferences only. It is not a legal opinion.
> **Note:** The audit was carried out under human direction with the help of AI agents (Claude Code), for both the per-module analysis and the independent adversarial review. Every key conclusion cites a publicly checkable source (file and line, git commit, public web page) and can be reproduced with the scripts in `scripts/`. Corrections from either party are welcome.

---

## 0. Summary of findings

| # | Finding | Confidence |
|---|---|---|
| 1 | **Thunderstorm directly used Tinycast code, and Droppy documented this itself.** In the NOTICE attached to MR !66 (2026-09-26) in its public Droplet Store repository, Droppy states that private commits `66c274b99` and `0e1c336a7` (both 09-21) ported the Tinycast launcher's mechanisms and look "one to one" into the **built-in** Thunderstorm, and that `6e9447d72` (09-26) rewrote that code "with the same metrics and behaviour" while still crediting those files to Tinycast. | Confirmed (Droppy's own record, independently corroborated) |
| 2 | **The "rewritten" source published on 10-11 still carries expressive content from Tinycast, with the credit removed.** Most notably, 13 comments / UI strings match Tinycast with a similarity of ≥0.9 (9 identical after normalisation, 3 where one fully contains the other); both independent baselines score 0. There is also an entire colour-opacity table, menu animation constants, coined API names (`armedHover`, `disarmHoverHighlight(pointerAt:)`, `BarButtonChrome`), leftover data-model key names, the order of a meeting-service table and the skeleton of an AI prompt. Most of these predate September in Tinycast, several were written by Tinycast's outside contributors, so the direction can only be Tinycast → Thunderstorm. The same files carried an "adapted from Tinycast, Copyright (C) 2026 Abue Ammar" header in the 09-26 droplet version; the 10-11 version does not. | Confirmed |
| 2b | **The released Droppy 16.0.0 / 16.0.1 also contain recognisable Tinycast-derived content (binary analysis, §3.7).** Both versions contain the launcher components that Droppy's own NOTICE credits to Tinycast, with type and field structures that match Tinycast's design (e.g. `ThunderstormBarButton`'s fields are in exactly the same order as Tinycast's `BarButton`; the UUID-stamped `ScrollRequest`); Tinycast's search-field prompt "Search for apps and commands…" (present alongside "Search your Mac"; which one was displayed cannot be determined); and the quicklink storage key `openWithBundleID`, the same name as Tinycast's field. The app bundle contains no Tinycast credit or licence notice anywhere, although five other third-party sources are credited. **None of these components exist in the pre-collaboration 15.2.2-beta.1 (09-09)** (§3.8), so the direction is proven independently of Droppy's own account. | Confirmed (binaries expose type, field, enum and string names only, not comments or function bodies) |
| 3 | Therefore the statements in Droppy's blog post that the leftovers "are texts, not code" and that "Not a single Droppy user ever received his code", and MR !77's description of the "built-in Thunderstorm (no Tinycast code)", **do not hold, at least for the launcher shell**: what remains is not only UI text but also source comments, tuned constants, component decomposition and API shapes. The README's "everything built on Tinycast's code is withdrawn, removed and rewritten" is ambiguous: a rewrite did happen (§3.4) and the droplet was withdrawn, but the rewrite did not remove the traceable Tinycast content. | Confirmed |
| 4 | **No large verbatim copying and no "rename-only" whole-file ports were found.** The longest identical stretch is 5 lines, the same as the independent baselines, and the per-file fingerprint distribution overlaps with the baselines. The launcher's low-level mechanisms (scrolling, hover tracking, key routing), the Raycast-extension JS runtime (Node process vs. JavaScriptCore), AI/MCP, the calculator parser, the dictionary, the backup engine and the Raycast importer are different implementations, built on Droppy's own host services. | High |
| 5 | The Tinycast author's claim that the "entire Tinycast code base" was "fed to AI": **the evidence can neither confirm nor rule it out.** The low score from Thunderstorm's own `compare.py` is not evidence against it: in this audit's AI-rewrite control experiment, a 100%-derived file scored 0.000. But the data also do not support a "whole codebase ported file by file" claim. What can be established is that derivation is concentrated in the launcher shell and in parts of several features, with broader borrowing at the level of design and specification (feature decomposition, interaction rules, documented specs). | Medium |
| 6 | **Timeline:** Thunderstorm's name, icon and basic search **predate** Tinycast (Wayback snapshot of 2026-05-12). But most features of the current version (calculator and conversions, quicklinks, snippets, Raycast extensions, window layouts, notes, backup, etc.) have no public record before Tinycast existed, and appear around or after the 21–27 September collaboration. | High |
| 7 | **The icon accusation does not hold:** Thunderstorm's name and bolt icon predate Tinycast; the two bolts look different; Tinycast's bolt (07-13) is stock artwork from SVG Repo. | High |
| 8 | **Licensing and attribution raise real issues (legal advice needed):** Tinycast is AGPL-3.0; the published Thunderstorm is GPL-3.0 + Commons Clause, copyright Jordy Spruit only, with no Tinycast credit anywhere in the source; Droppy itself wrote in MR !77 that the "collaboration permission … is no longer given". | Facts established; legal characterisation open |

**In one sentence:** Thunderstorm is not a wholesale copy of Tinycast, and a substantial part of it is Droppy's own work; but in September 2026 it did absorb Tinycast's code and design (as Droppy itself recorded), the parts of that which can be identified in a binary (component structure, field names, a prompt) shipped to users in Droppy 16.0 without credit, and the "rewritten" version published on 10-11 was not cleaned up: the launcher shell still contains datable, traceable Tinycast comments, constants, APIs and data. Droppy's statements that what remained "are texts, not code", that "Not a single Droppy user ever received his code", and that the built-in Thunderstorm has "no Tinycast code" are contrary to the evidence; saying "the entire codebase was copied" goes beyond it.

---

## 1. Scope, materials and limitations

### 1.1 Materials
- Thunderstorm: 256 Swift files, 115,395 lines; `verify/compare.py`, `verify/similarity.py`; README, LICENSE (GPL-3.0 + Commons Clause).
- Tinycast: 798 app Swift files (119,430 lines) + 103 test files (38,599 lines) + a Raycast JS runtime; full git history of 990 commits (804 on main), 120 remote branches, 116 tags.
- Public sources (read only): Droppy's changelog / blog / release API, Internet Archive snapshots, MR descriptions and diffs in the GitLab Droplet Store repository, Tinycast's GitHub releases, the text of the Tinycast author's X post (read via api.fxtwitter.com; attached image and video not viewed), the GitHub DMCA repository.
- Released binaries: the official DMGs of Droppy 15.2.2-beta.1 (09-09, pre-collaboration baseline), 16.0.0 and 16.0.1 (source: `droppy-releases.jordylegrand.workers.dev`, the host that getdroppy.app's release API points to; MD5 matches the server ETag; checksums in `data/binary/dmg_checksums.txt`). Mounted read-only and analysed statically; nothing in them was executed.
- Independent baselines: two unrelated, unpublished macOS Swift codebases (baseline A, ~57k lines; baseline B, ~92k lines; third-party code, build output and copies removed), compared against Tinycast in exactly the same way to measure what coincidence looks like.

### 1.2 Method
1. Reproduce Thunderstorm's own `compare.py`, then run a prefix-stripping experiment, baselines and parameter sensitivity.
2. Purpose-written comparisons: type names, string literals, comments, enum case sets, ordered literal sequences, and near-duplicate prose (word trigrams) in comments and UI text; every hit is tagged with the commit and date of its first appearance in Tinycast's history.
3. Each of 13 modules was compared section by section (including Tinycast's historical versions) by one analyst (an AI agent). Each analysis was handed to an independent verifier (another AI agent) instructed to try to refute every finding: is it dictated by the Raycast API or Apple boilerplate, is it a protocol constant, generic vocabulary or coincidence, could the direction be reversed?
4. Cross-cutting work: git history forensics, public release timeline, review of the comparison method (including an AI-rewrite control experiment).
5. Three-way comparison: Tinycast ↔ Droppy's 09-26 droplet version (credited to Tinycast) ↔ the 10-11 public version.
6. Static comparison of three released Droppy binaries.

### 1.3 Limitations (read this first)
- **Thunderstorm's commit history is essentially unauditable.** The public repository has two commits (a one-shot import of 115,139 lines on 10-11 plus a README icon commit). The Droppy commit `a4def4dc9` referenced in the README is not in the repository, and Droppy's main repository is private (GitHub `iordv/Droppy` has returned HTTP 451 since 2026-02-23 because of an unrelated DMCA notice; GitLab `droppyformac1/droppy` returns 404). When, by whom and how any file or function was written cannot be verified from Thunderstorm's side.
- The "Droppy codebase as of June 2026" used as a baseline in the README is not public and cannot be reproduced.
- The released binaries of Droppy 15.2.2-beta.1 / 16.0.0 / 16.0.1 were analysed (§3.7, §3.8), but they are stripped: only type names, stored-property names, enum cases and string constants are visible, not comments, function names or function bodies. Internal / nightly / insider builds were not available.
- Tinycast's large outside PRs were squash-merged, so their internal history is not visible; git author names cannot be tied to real identities.
- Similarity evidence speaks to origin and degree of similarity. Whether something is a derivative work in the AGPL sense is a legal question.

---

## 2. Background and what each side has said

| Date | Event | Source |
|---|---|---|
| 2026-02-10/23 | The copyright holder of Atoll (another GPL-3.0 macOS open-source project) filed a DMCA notice against six files in `iordv/Droppy`; GitHub blocked the repository. **Unrelated to this case; listed only as background**, and because it is why Droppy's source has not been publicly readable since. | github/dmca |
| 2026-03-16 (claimed) | Droppy says Thunderstorm first shipped in 13.1 (clipboard search + command catalog, 35 files). **Not verifiable**: the changelog has no 13.0/13.1 entries, and homepage snapshots of 03-15, 03-29 and 04-13 do not mention Thunderstorm. | Droppy blog, README |
| 2026-05-12 | Thunderstorm first appears in a Wayback homepage snapshot ("Universal search and clipboard launcher, one shortcut."). **Independent evidence that it predates Tinycast.** | web.archive.org |
| 2026-06-14/15 | 14.1.0-beta: Spotlight-style search bar, file actions, system actions, quit all / eject all. No calculator, quicklinks, snippets, extensions, AI or window management. | Archived changelog.json |
| 2026-06-28/29 | Tinycast's first commit ("initial mockup done"); relicensed from GPL-3.0 to AGPL-3.0 on 07-10 (`eaa581dd`). | Tinycast git |
| 2026-09-21 | Droppy private commits `66c274b99` ("Make Thunderstorm behave like the Tinycast launcher, not just look like it") and `0e1c336a7` ("Give Thunderstorm the Tinycast launcher one to one"). | Droppy's own NOTICE (MR !66) |
| 2026-09-23 | MR !22: the complete Tinycast (upstream `d93a09b`) runs inside Droppy as a droplet; the description says it "takes over from Thunderstorm". | GitLab droplets |
| 2026-09-26 | `6e9447d72` rewrites "with the same metrics and behaviour"; MR !64 deletes the Tinycast droplet; MR !66 publishes a Thunderstorm droplet under the AGPL, whose NOTICE credits Tinycast file by file. | Same |
| 2026-09-27 | MR !72 (branch `codex/thunderstorm-tinycast-parity`), "Thunderstorm 1.1.0: port Tinycast non-AI features": replaces the partial launcher with Tinycast's non-AI engine, adding Raycast extensions, snippets, quicklinks, window layouts and Rooms, notes, backup and more. Three hours later MR !77 removes it from the Store because the engine is Tinycast (AGPL) and the collaboration permission is no longer given, and states that Droppy keeps "its own built-in Thunderstorm (no Tinycast code)". The same day a blog post announces Raycast extension support in the built-in Thunderstorm, listing features that match MR !72 almost one for one. | GitLab droplets, Droppy blog |
| 2026-09-27/28 | Droppy 16.0.0: changelog dated 09-27, saying only "rebuilt Thunderstorm"; Wayback shows 15.2.2-beta.1 still listed as latest at 09-27 15:20 UTC, so 16.0 went live between 09-27 15:20 UTC and 09-28 (the README says 09-28). 16.0.1 was published 09-28 21:40 UTC and is still the latest stable as of 10-12. | changelog, /api/releases/latest, Wayback |
| 2026-10-11 12:21 UTC | The Tinycast author posts on X that Droppy "ripped of[f]" the entire Tinycast code base and fed it to AI; also mentions the bolt logo, paid sales and leftover placeholder text. | X (read via fxtwitter) |
| 2026-10-11 16:56 UTC | Thunderstorm source commit (about 4.5 hours after the accusation); the README says a "last pass" that day replaced leftover names, labels and placeholder texts, and that this is the code for "the next Droppy update", i.e. it corresponds to no released version. | Thunderstorm git, GitLab |

---

## 3. Commit history analysis

### 3.1 The Thunderstorm repository
- Two commits, author and committer Jordy Spruit `<hi@getdroppy.app>`: `e5c02a12` (10-11 18:56 +0200; imports all sources, licence and verify scripts) and `2ecde783` (19:05; icon and badges). 282 objects, all reachable; no dangling objects, tags or other branches.
- **Conclusion:** a curated one-shot snapshot with no development history. It cannot answer when or by whom any code was written, or whether it was adapted from Tinycast.
- Dates referenced inside the source: only 2026-09-01, 09-06, 09-27 ("Alpha: early, and in testing (Jordy, 2026-09-27)"), 09-29, 10-04/05 and 10-10; none before September. Weak, but consistent with most of the current code having been written in September–October.
- In Thunderstorm's favour: migration code for older settings (e.g. `thunderstormFavoriteApplicationPaths`, `migrateLegacySpotIfNeeded`) shows that earlier, released versions of Thunderstorm existed and saved user settings.
- Style fingerprint: of Thunderstorm's ~15k comment lines only 1.19% exceed 80 columns (it wraps at about 76). The single-line comments identical to Tinycast fall exactly in that 1%, e.g. "Selection wins over hover…" (94 columns) and "Identical metrics…" (81 columns), consistent with Tinycast one-liners carried over without being re-wrapped to Thunderstorm's habit.

### 3.2 The Tinycast repository
- Size and cadence: 990 commits; 16 in June, 255 in July, 181 in August, 355 in September, 183 in October (to 10-10); 116 tags from v0.1.0-alpha.4 (07-03) to v0.11.19 (10-10).
- Authors: abue-ammar about 789 commits, plus about 67 outside authors (Jonas List 43, Clément Knoderer 25, notsoshu 22, …), in time zones from +0200 to +0800.
- Signs of organic development: early personal-commit noise ("fixed", "much better", "excelent work"); numbered PRs with long rationales from 07-27; two reverts; a large restructuring on 08-05 to 08-07 (`Core/` split into `Features/<Name>/`, with a written naming vocabulary, e.g. PaletteViewModel → PaletteState); types evolving step by step (e.g. `BarButton` → `BarButtonChrome(.capsule/.menu)` → `.rounded` → `isSelected/isCompact`).
- **Two comment compactions** (key to the direction question): `946c5907` (08-07, #197) collapsed 181 multi-line comment blocks to single lines, and `fde9228c` (08-29, #382) collapsed 397 more. Much of Tinycast's current one-line wording was born in these two commits. **Thunderstorm contains only the compacted wording**, so its source can only be Tinycast file versions from after 08-07.
- Traces of the collaboration: searching commit messages and diffs on all Tinycast branches for droppy / droplet / spruit / thunderstorm finds nothing (two false positives: a Raycast icon name and an emoji keyword). The Tinycast droplet's host layer lives in Droppy's droplets repository, not in Tinycast, consistent with MR !22.

### 3.3 Droppy's public "commit record": Droplet Store MRs
Because Thunderstorm has no history, the MRs in Droppy's public Droplet Store repository (`gitlab.com/droppyformac1/droplets`, created 09-22) are the closest thing to a Droppy development record. All relevant MRs were opened by the account `droppyformac`; many carry a "Generated with Claude Code" marker.

| MR | Time (UTC) | Content |
|---|---|---|
| !22 | 09-23 12:17 | Tinycast 1.0.0 droplet: the complete Tinycast, built from upstream `d93a09b`, running in Droppy, "takes over from Thunderstorm" |
| !40 | from 09-23 | Tinycast 1.1.1: migrates a Thunderstorm user's aliases, favourites and shortcuts into Tinycast |
| !64 | 09-26 15:20 | Deletes the Tinycast droplet; "Thunderstorm is Droppy's launcher again" |
| !66 | 09-26 19:44 | Thunderstorm 1.0.0 droplet (AGPL-3.0-or-later) with a NOTICE.md listing every file adapted from Tinycast |
| !72 | 09-27 13:25 | Branch `codex/thunderstorm-tinycast-parity`: "replaces the partial launcher with Tinycast's non-AI engine", adding Raycast extensions (with Tinycast's JavaScriptCore runtime), snippets, quicklinks, window layouts and Rooms, notes, backup and more; host integration in private `droppy!3460/!3461` |
| !77 | 09-27 16:19 | Removes the Thunderstorm droplet: its engine is Tinycast (AGPL), the collaboration permission is no longer given; "Droppy keeps its own built-in Thunderstorm (no Tinycast code)" |

Key points of the MR !66 NOTICE (paraphrased):
- Private commit `66c274b99` (09-21) ported from the Tinycast palette: the scroll intent, selection following between the floating bars and the thin overlay scrollbar (`ThunderstormScrolling`); hover armed by pointer movement (`ThunderstormPointerState`); `ThunderstormPanel.sendEvent` and opening with hover disarmed (`ThunderstormWindowController`, from Tinycast's `PalettePanel.swift` / `PaletteWindowController.swift`); the footer menus (`ThunderstormView`); icon rasterisation (`ThunderstormIconProvider`).
- Private commit `0e1c336a7` (09-21) made the launcher's layout, typography and colours follow the Tinycast palette "one to one": `ThunderstormStyle` (then `ThunderstormTheme`), `ThunderstormLauncherChrome`, `ThunderstormLayout`, `ThunderstormView`, `ThunderstormActionMenu` (created by this commit).
- `6e9447d72` (09-26) rewrote Scrolling, Theme/Style, the chrome's edge dissolve and controls and the action menu "as Droppy's own code, with the same metrics and behaviour", and these files are **credited to Tinycast all the same**.

**This matches the audit's independent findings closely:** the two modules with the strongest evidence (§6: the palette view and the window controller) are exactly the files named in the NOTICE.

### 3.4 Three-way comparison: 09-26 droplet ↔ 10-11 public version
The 09-26 droplet source was taken from MR !66 (54 files; every file named in the NOTICE carries a "Parts of this file are adapted from Tinycast, Copyright (C) 2026 Abue Ammar" header) and compared with the 28 same-named files in the 10-11 release:

- For the launcher files named in the NOTICE, fingerprint containment between the two versions is low: Scrolling 0.01, PointerState 0.00, ActionMenu 0.08, Layout 0.05, View 0.10, WindowController 0.13, LauncherChrome 0.13, Style 0.18. **So they were rewritten again after 09-26.**
- Yet Tinycast's verbatim comments **are present in both versions**: "Open disarmed: a pointer already over a row must not highlight it." (WindowController), "Identical metrics in both states, so typing…", "Snap to the origin on the first row so its header shows too.", "Never conditionally mounted…" (View), "Selection wins over hover when a row is both…" (in LauncherChrome on 09-26; in Droppy's own DropletLibraryRow on 10-11).
- The 09-26 version carries Tinycast copyright headers; the 10-11 version credits Tinycast nowhere.
- Files not named in the NOTICE (SearchService, UtilityIntentEngine, UsageStore, etc., Droppy's own code) are highly similar between the two versions, with identical stretches of up to 102 lines, which shows the method does detect shared code when it exists.

**Interpretation:** the launcher shell in the 10-11 release did go through a second rewrite, but that rewrite kept text and design elements that Droppy itself had labelled "adapted from Tinycast" two weeks earlier, and dropped the credit.

### 3.5 Direction of copying
- Thunderstorm's source was not publicly readable before 10-11, and source comments and internal identifiers cannot be recovered from released binaries. Therefore **a comment that appears in Tinycast before September and verbatim in Thunderstorm can only have travelled Tinycast → Thunderstorm** (or be coincidence; both baselines score zero for near-duplicate comments).
- Three of the strongest comments were written by Tinycast's outside contributors (zkmn73 #208, 08-11; notsoshu #318, 08-23; Ales M #880, 09-18), in time zones different from the Droppy author's, which rules out "the Droppy author contributed to Tinycast under another name".
- Caveat: the Droplet Store repository has exposed the Tinycast droplet source since 09-23 and the Thunderstorm droplet source since 09-26. **Elements Tinycast added after 09-26 that also appear in Thunderstorm could in theory have flowed the other way** and need case-by-case assessment (§3.6). User-visible UI text can also be seen in Droppy's binaries, so the direction argument is weaker for such elements.

### 3.6 Elements that appeared in Tinycast after the collaboration
| Element | First seen in Tinycast | Assessment |
|---|---|---|
| Paste Sequentially (in Thunderstorm "Paste One by One", internal identifier still `paste-sequentially`) | 09-29 (`44e475f4` → #1221, 09-30, with tests and a settle fix) | Most significant: same `idleTimeout` of 60, same traversal, internal name unchanged. **Binary check: 16.0.0 / 16.0.1 (09-28) contain neither `paste-sequentially` nor `ThunderstormClipboardSequence`**, ruling out "Droppy shipped it first". Direction Tinycast → Thunderstorm is likely, and after the collaboration ended |
| Keep Calculating (⌘↵ puts the answer back in the search field) | 10-05 (#1324, from issue #1297 on 10-03) | Organic origin on Tinycast's side. 16.0.x has neither this feature nor the 10-11 typed calculator (`ThunderstormCalc*`). Leans Tinycast → Thunderstorm, but independent invention cannot be excluded |
| Meeting details page | 10-02 (#1265) | ⌘I/⌘O are macOS conventions, attendee statuses come from EventKit; weak-to-moderate |
| LaTeX math in AI replies | 09-30 (#1238) | Completely different rendering engines; not evidence |
| "Runs on this Mac. Nothing leaves it." | Actually formed gradually 09-13 to 09-19 | Belongs to the collaboration window; a common privacy phrase; weak-to-moderate |
| QuicklinkEditorScreen and similar type names | 10-10 (#1488) | Predictable from naming conventions both projects already used; weak |

### 3.7 Binary analysis of released Droppy 16.0.0 / 16.0.1
**Material:** official DMGs, 16.0.0 (build 16009999, 64.7 MB) and 16.0.1 (build 16019999, 67.2 MB), both signed "Developer ID Application: Jordy Spruit (NARHG44L48)". 16.0.0's signing timestamp is **2026-09-27 22:14 UTC**, inside the release window inferred from Wayback in §2 (09-27 15:20 UTC to 09-28); 16.0.1's is 09-28 21:31 UTC, consistent with the release API's 21:40 UTC. The executables are universal (x86_64 + arm64) and stripped, but Swift reflection metadata (`__swift5_fieldmd` / `__swift5_reflstr`) and string constants remain. A purpose-written parser read the field descriptors, giving each type's stored-property and enum-case names (16.0.0: 4,870 descriptors, 266 of them Thunderstorm types).

**Findings**

| # | Finding | Meaning |
|---|---|---|
| B1 | 16.0.0 contains the launcher components that Droppy's NOTICE names and credits to Tinycast: `ThunderstormPointerState` (fields `hoverArmed`, `commandHeld`, `menuOpen`, `armingDistance`, `restingPoint`), `ThunderstormArmedHover`, `ThunderstormBarButton` / `ThunderstormBarButtonChrome {capsule, rounded}`, `ThunderstormKeyCap.Style {outline, filled}`, `ThunderstormMenuCircleButton`, `ThunderstormHeaderBackButton`, `ThunderstormRightClickCatcher`, `ThunderstormMenuItem` (already using `beginsGroup`). | These components shipped to users in 16.0 |
| B2 | `ThunderstormBarButton`'s fields are `chrome, isSelected, isCompact, action, label, hovered`, exactly the property order of Tinycast's `BarButton` (`isSelected` / `isCompact` added by outside contributor Ales M on 09-18, #880); `KeyCap.Style`'s `outline, filled` matches Tinycast's `KeyCapChip`. | The shipped component structure matches Tinycast as of 09-18 or later |
| B3 | 16.0.0 has `ThunderstormScrollRequest`: `Goal { resetToTop, revealSelection }` plus a fresh `UUID` stamp per request. This matches the 09-26 droplet and Tinycast's `ScrollIntent` (Equatable + `nonce = UUID()`, 07-30). The 10-11 release replaced it with `ScrollChannel`, and its comment calls UUID-stamped requests the old approach. | The shipped build used the design Droppy admits was ported from Tinycast's "scroll intent" |
| B4 | Tinycast's search-field prompt **"Search for apps and commands…"** (used by Tinycast since 07-04) is a string constant referenced by code in the 16.0.0 / 16.0.1 executable, next to `settings:thunderstorm` and "Filter this folder"; in the 09-26 droplet it is exactly what `searchPlaceholder` returns. The 10-11 `searchPlaceholder` returns "Search your Mac" ("Filter this folder…" when browsing a folder). However, 16.0.x's localisation table **also** contains "Search your Mac", so the binary cannot tell which prompt 16.0 actually displayed. | Consistent with Droppy's own admission that the search prompt slipped into 16.0; the binary corroborates it |
| B5 | In 16.0.x, `ThunderstormQuicklink`'s CodingKeys are `id, name, link, keyword, isFallback, openWithBundleID`. `openWithBundleID` is the field name Tinycast's `Quicklink` uses (08-03/04) and does not exist in Raycast's export format; the 10-11 release renames it `preferredAppBundleID` and lists `openWithBundleID` as a key "earlier builds wrote". | Quicklinks saved by users of 16.0.x use the same field name as Tinycast |
| B6 | The bundle ships five third-party notices (ThunderstormEmojiAnnotations, LinearMouse, AI assistant logos, thock, OCR references); **none mentions Tinycast**, and the words "Tinycast" (capitalised) and "Abue" appear nowhere in the bundle. | No credit to Tinycast in the released app |
| B7 | Only two lowercase `tinycast` strings exist: `app.getdroppy.droplet.tinycast` and `com.tinycast.extensions.oauth` (the OAuth keychain service Tinycast introduced on 08-25, #325), both next to host code in `DropletCatalogBridge` that handles retired-droplet succession and clean-up. | Most plausibly clean-up of data left by the withdrawn Tinycast droplet; **not counted as evidence of copying** |
| B8 | 16.0.0 already contains Thunderstorm's own Node host script for Raycast extensions (618 lines, 563 of them identical and in order with the 10-11 version) and no Tinycast JavaScriptCore runtime. | Supports "the extension runtime is architecturally independent"; also shows this code was already in 16.0 (the 09-27 post said it would ship after 16.0, so it was probably not yet user-facing) |

**How 16.0.x relates to the 10-11 snapshot**
- Of the 899 Thunderstorm types in the 10-11 source, only 179 appear in 16.0.0. This is a lower bound: types without stored properties or optimised away do not appear in reflection metadata (16.0 obviously has styling, yet `ThunderstormStyle` is not found). **The absence of a single type is therefore not evidence**; only whole modules whose types are all absent are cited. Absent from 16.0.x: Quick Actions (18 types), AI chat and MCP, the typed calculator (`ThunderstormCalc*`), the Markdown notes window, meetings and camera, Workspaces and window layouts, Paste One by One, and more. This fits the README's "the code that ships in the next Droppy update": **a large part of the 10-11 snapshot has never shipped in a stable release**, and either entered release builds or was written after 16.0.1 (09-28).
- 16.0.0 sits between the 09-26 droplet and the 10-11 release: it already has the 10-11 `ScrollDriver`, `SlimScroller` and `KeepsSelectionInView`, but keeps the 09-26 `ScrollRequest` and lacks the 10-11 `ScrollChannel` and `HoverTracker`. So the launcher shell **was changed again after 16.0.1**, and the verbatim comments in §6 survived that round too.
- Two pieces of 10-11 migration code read data written by "earlier builds": the Quicklink keys `iconSymbol` / `openWithBundleID` / `isEnabled` (the three Tinycast `Quicklink` field names) and the Workspaces values `auto, focus, stack, columns, grid, custom` (the raw values of Tinycast's `RoomLayoutKind`). But 16.0.x's quicklinks wrote only `openWithBundleID`, and 16.0.x **has no Workspaces at all**. So these "earlier builds" were, at least in part, internal, nightly or droplet builds that never shipped as stable. Together with MR !72 (on 09-27 Tinycast's quicklinks, Rooms and other non-AI engine parts were ported into the Thunderstorm droplet), **the 10-11 quicklinks and Workspaces most likely descend from that port, which used Tinycast's data models.** This is an inference; Droppy's internal builds or private history would be needed to confirm it.

**Bearing on Droppy's statements:** the blog post says "It was removed before any update went out, so no Droppy user ever got his code" and presents Thunderstorm's use of Tinycast parts as belonging to an unreleased "test version". By the attribution standard of Droppy's own 09-26 NOTICE ("these files are credited to Tinycast all the same"), these launcher components shipped to users in 16.0.0 / 16.0.1 with no Tinycast credit, together with Tinycast's prompt and a quicklink field name identical to Tinycast's. Binaries do not expose comments or function bodies, so how closely 16.0's implementation tracks Tinycast line by line cannot be determined; but "no Droppy user ever got his code" is contrary to the facts above.

### 3.8 Pre-collaboration baseline: Droppy 15.2.2-beta.1
To establish the origin of these components independently of Droppy's NOTICE, the audit also examined the most recent public beta before the collaboration, 15.2.2-beta.1 (only a 09-12 nightly followed it; the release API listed it as the latest beta until 16.0): 48.0 MB, same source, build 15220001, signed **2026-09-09 07:40 UTC**, before the 09-21 port commits in the NOTICE and the 09-23 Tinycast droplet.

| Item | 15.2.2-beta.1 (09-09) | 16.0.0 (09-27) | First seen in Tinycast |
|---|---|---|---|
| Thunderstorm types with fields / distinct Thunderstorm identifiers | 114 / 90 | 266 / 230 | — |
| Hover "arming" (`ThunderstormPointerState`: `armingDistance`, `restingPoint`, `hoverArmed`; `ThunderstormArmedHover`) | **None** (the old row view `ResultRowCompact` has a plain `isHovered`; `ThunderstormPanel` has no fields) | Present | 07-24 / 08-05 / 08-11 |
| `ThunderstormBarButton` / `ThunderstormBarButtonChrome {capsule, rounded}` | None | Present (field order as in Tinycast) | 07-10 / 08-14; `isSelected`, `isCompact` 09-18 |
| `ThunderstormKeyCap` / `KeyCaps` (`Style {outline, filled}`) | None | Present | 06-30 |
| `ThunderstormMenuCircleButton`, `ThunderstormHeaderBackButton` | None | Present | 07-10, 09-08/09 |
| `ThunderstormRightClickCatcher` with nested `CatcherView` | None | Present (nested type also named `CatcherView`) | 06-29 |
| `ThunderstormScrollRequest` (UUID stamp), `SlimScroller`, `KeepsSelectionInView` | None | Present | 07-30 (ScrollIntent) etc. |
| `ThunderstormSectionHeader`, `ThunderstormEmptyResults`, `ThunderstormActionMenu` / `ThunderstormMenuItem` (`beginsGroup`) | None | Present | 06-28 to 09-10 |
| Search prompt "Search for apps and commands…" | None | Present | 07-04 |
| "Search your Mac" | **Present** (Droppy's own localised string) | Present (still in the localisation table) | — |
| Quicklinks (`openWithBundleID`) | None (no quicklink feature) | Present | 08-03/04 |
| Old launcher UI types (`ThunderstormGlassSurface`, `ResultRowCompact`, `ResultActionBar`, `StatusRow`, `LeadingGlyph`) | Present | **All gone** | — |

**Conclusions**
1. **The direction of copying is proven independently, no longer resting on Droppy's own account.** None of these Tinycast-coined component names and structures exists in Droppy's 09-09 release; in Tinycast they appeared earlier (mostly June–August, the latest on 09-18) with a complete organic history; in 16.0.0 (09-27) they appear with Tinycast's naming, nesting and field order, while Droppy's previous launcher UI types are replaced wholesale. Tinycast's source has been public on GitHub since June, so the reverse (Tinycast copying Droppy) is impossible on the timeline. This agrees with Droppy's NOTICE, but is now backed by independent binary evidence.
2. **The story of the search prompt is confirmed.** "Search your Mac" is a Droppy string from before the collaboration; Tinycast's "Search for apps and commands…" appears in 16.0; the 10-11 release returns to "Search your Mac". This agrees with Droppy's blog ("slipped into 16.0, since changed back").
3. **Feature timing:** quicklinks, snippets (with keyword expansion), Script Commands, Raycast extensions (Droppy's own Node runtime, ~40 types), library and backup, dictionary, menu search, window switching, calculator history, Apple Shortcuts and more first appear in Droppy between 09-09 and 09-27. The list is nearly identical to MR !72 (09-27, porting Tinycast's non-AI features into the droplet) and to the same day's blog post. Many of these features are nonetheless independent at the code level (§4, §6); the overlap in timing only shows they were added in the same period in which Tinycast's source was being used, not that each was copied.
4. **Weak evidence (recorded only):** 16.0.0's localisation tables (translated into several languages) contain a few Tinycast emoji-screen strings as keys, e.g. "Paste and Keep Window Open", "Move Up in Pinned", "Keys & Technical", "Shapes & Punctuation" (Tinycast 08-10 to 09-15). They are absent from 15.2.2 and not referenced by 16.0's code, i.e. leftover entries. They show these strings entered Droppy's main string catalogue between 09-09 and 09-27, but whether via the built-in Thunderstorm or via Droppy's host bridge for the Tinycast droplet cannot be told. Droppy's own emoji picker already existed in 15.2.2.

---

## 4. Architecture comparison

### 4.1 Overall statistics
| Metric | Thunderstorm | Tinycast (app code) |
|---|---|---|
| Swift files | 256 | 798 (plus 103 test files) |
| Lines | 115,395 | 119,430 (tests: 38,599) |
| Lines per file (median / mean / max) | 350 / 451 / 3,384 | 91 / 150 / 2,143 |
| Comment-line share | 13.1% | 5.6% (has a one-line-comment rule) |
| Types / functions | 1,291 / 4,187 | 1,922 / 5,144 |
| Layout | Flat: `Sources/` plus six folders (AI, Calculator, Extensions, Library, Meetings, Windows); every type prefixed `Thunderstorm` | `Features/<Name>/{Model, Service, UI, Settings}`, plus `Palette/`, `DesignSystem/`, `Platform/` |
| Layering | Feature registry (`ThunderstormBootstrap` registers screens, entry sections, Tab modes, argument resolvers, row actions); hosted by Droppy's `ExtensionDefinition` / DroppyKit | Four layers: PURE (Foundation only) → EFFECT → OBSERVABLE STATE → VIEW, enforced by tests (`Model/` may not import AppKit/SwiftUI) |
| Tests | None | 103 test files |
| Builds on its own | No (needs Droppy's design system, host services, DroppyKit) | Yes |

The two codebases are similar in size but organised very differently: Thunderstorm favours large files, long comments and registry-style extension; Tinycast favours small files, strict layering and tests.

### 4.2 Module mapping and degree of derivation (after verification)
| Module | Main Thunderstorm files | Tinycast counterpart | Verified evidence (strong / moderate) | Assessment |
|---|---|---|---|---|
| Launcher palette view and chrome | ThunderstormView, LauncherChrome, Style, Layout, ActionMenu, DropletLibraryRow, … | Palette/RootPaletteView, DesignSystem/* | 9 / 2 | **High**: view layer renamed with paraphrased comments, design tokens carried over as whole tables, low-level mechanisms rewritten |
| Window controller, scrolling, hover | ThunderstormWindowController, Scrolling, PointerState, … | PaletteWindowController, PalettePanel, ArmedHover, HoverArming | 8 / 0 | **High**: reference-based rewrite with verbatim comments and identifiers left in |
| Search, ranking, app index | SearchModel, SearchService, AppIndex, FuzzyMatch, … | Launcher/* | 1 / 3 | Moderate at design/text level; low at code level |
| System commands and intents | SystemCommands, SystemActions, Uninstaller, Deeplinks, … | SystemActions, Uninstall, HotKeys | 0 / 2 | Low-to-moderate |
| Clipboard, file search, emoji | Clipboard*, FileSearch*, PathIndex, EmojiSurface | Clipboard, FileSearch, Emoji | 2 / 1 | Moderate: design and wording borrowed, code largely rewritten |
| Calculator | Calculator/* | Calculator (#483 typed evaluator) | 1 / 3 | High at spec/documentation level; code independent (recursive descent vs. Pratt) |
| AI chat and providers | AI/Chat, AI/Providers | AI/* | 0 / 0 | Low |
| MCP and Quick Actions | AI/MCP, AI/QuickActions | MCP, QuickActions | 1 / 1 | Low-to-moderate (mainly one prompt) |
| Raycast extensions (Swift side) | Extensions/* | Extensions, raycast-runtime | 0 / 1 | Low-to-moderate (runtime architecture independent) |
| Snippets, quicklinks, commands | Library/Snippet*, Quicklinks, Placeholders, ShellRunner, … | Snippets, Quicklinks, CustomCommands | 1 / 4 | Moderate: reimplemented from the spec, compatibility keys left in |
| Backup, Raycast import, library | Library/LibraryBackup*, RaycastConfigImport, … | Backup, Settings | 1 / 3 | Moderate |
| Notes, dictionary, menu search, window switcher | Library/NotesWindow*, Dictionary, MenuSearch, WindowSwitcher | Notes, Dictionary, MenuSearch, WindowSwitcher | 0 / 0 | Low (code); low-to-moderate (design) |
| Meetings and camera, window management and workspaces | Meetings/*, Windows/* | Calendar, Camera, WindowManagement (incl. Rooms) | 2 / 2 | Lineage established, code rewritten |
| **Total** | 13 modules, 143 findings | | **26 strong / 22 moderate** (94 weak, 1 refuted) | |

### 4.3 Architecture-level evidence of independence
- **Raycast extension runtime:** Thunderstorm starts one Node child process per command and exchanges JSON lines over stdin/stdout; Tinycast runs JavaScriptCore in-process with Node shims. Comparing the 1,632 lines of JS embedded in Thunderstorm's Swift strings, the only matches are the host-config boilerplate react-reconciler requires and the `@raycast/utils` icon SVGs (both reproduce Raycast's own implementation). Notably, MR !72 brought Tinycast's JavaScriptCore runtime into the droplet, but the built-in version did not adopt it.
- **Launcher internals:** scroll driving (AppKit `constrainBoundsRect` vs. SwiftUI `ScrollViewProxy`), edge dissolve (`CAGradientLayer` vs. a SwiftUI gradient mask), thin scrollbar (`NSScroller` subclass vs. SwiftUI overlay), key routing (one local NSEvent monitor vs. `onKeyPress` + `sendEvent`) and hover tracking (weak table plus momentum-tail handling, which Tinycast lacks) all differ.
- **Data and algorithms:** clipboard storage (Droppy's ClipboardManager vs. SQLite+FTS), fuzzy matching and scoring constants, usage model, calculator parsing (recursive descent vs. Pratt), dictionary (public API vs. private DCS + XHTML), Raycast import reader (heuristic walker that uses none of Tinycast's published format knowledge), backup engine (single JSON with id remapping vs. AppleArchive) all differ.
- **Opposite design decisions:** Eject All includes network volumes (Tinycast explicitly does not); no ⌘C when Accessibility reports an empty selection (Tinycast still sends it); the window switcher uses the `didActivateApplication` approach Tinycast's docs explicitly reject; `json-stringify` output is quoted (like Raycast; Tinycast does not quote).
- **Droppy-specific integration:** droplet library, Shelf/Basket, DroppyKit, Window Snap, the camera droplet, MicrophoneMuteManager and more have no counterpart anywhere in Tinycast's history.

---

## 5. Quantitative similarity

### 5.1 Reproducing Thunderstorm's own `compare.py`
Run on an unmodified copy (`python3 -I`, against all 6,350 source blobs in Tinycast's history):

| Metric | Thunderstorm | Baseline A | Baseline B |
|---|---|---|---|
| Longest identical stretch (lines) | **5** (as reported in the README) | 5 | 4 |
| Literal fingerprints (names kept) | **0.24%** (as reported) | 0.29% | 0.12% |
| Renamed fingerprints (identifiers normalised) | **2.77%** (not reported in the README) | 1.77% | 1.27% |
| Shared lines per 1,000 | 73.9 | 65.6 | 32.2 |
| Runs of ≥3 lines | 42 | 34 | 16 |
| Highest single-file renamed containment | 0.212 (DropletLibraryRow) | 0.145 | 0.109 |

- Both README numbers reproduce exactly; they are not fabricated.
- Stripping every `Thunderstorm` prefix and re-running changes nothing (5 / 0.24% / 2.77%). The low literal score is **not** an artefact of the prefix: the code really was rewritten at the token level.
- The renamed metric is 1.2–2.2× the baselines under every parameter setting (K=25: 3.38 / 2.03 / 1.45; K=15, DF≤5: 14.8 / 11.3 / 10.4; K=12: 39.1 / 31.8 / 28.9): mildly elevated.
- Over 30-line sliding windows (K=15), windows with ≥40% hits make up 3.27% for Thunderstorm (102 files) vs. 1.03% and 1.12% for the baselines, about 3×.

### 5.2 Blind spots of `compare.py`
| Blind spot | Where | Impact |
|---|---|---|
| All comments blanked before comparison | `blank()` in similarity.py `lex()` | **Large**: Thunderstorm has 14,989 comment-only lines (13%), and the strongest evidence is in comments |
| Every string becomes one token `S`, every number `N` | `norm_tokens` | **Large**: UI text, tuned constants and table contents are invisible; 1,632 lines of embedded JS count as 7 tokens |
| Line runs need identical normalised lines with identifiers kept | `norm_line` / `significant` | Any rename, re-wrap or table reshuffle breaks a run; short SwiftUI modifier lines are filtered out |
| K=25, W=8 not justified | compare.py:43-44 | A 100%-derived rewritten file scores 0 at K=25 |
| DF_MAX=5 counted per path | compare.py:113-130 | Idioms Tinycast reuses across screens are discarded as boilerplate (removes 18% of Thunderstorm's hits vs. 12–13% for baselines) |
| Whole-tree averaging | `measure()` | Local borrowing is diluted by 115k lines |
| No time dimension | `load_history` | Cannot tell direction |
| README reports only the literal column | README | Exactly the column that drops to ~0 under any rename or rewrite |

### 5.3 AI-rewrite control experiment
The methodology reviewer rewrote five Tinycast files (660 lines) the way an LLM would when asked to "rewrite this in our style": every identifier renamed, members reordered, control flow changed, functions split or merged, every comment reworded, behaviour preserved. A rename-only control was produced as well.

| Group | Longest run | Literal (overall) | Renamed (overall) | Near-duplicate comments ≥0.5 |
|---|---|---|---|---|
| Deep rewrite (known 100% derived) | 9–10 lines (from a data table) | **1.09%** | 11.3% | 1 of 58 |
| Rename only | 20 lines | 4.8% | 95% | 56 of 56 |
| Thunderstorm | 5 lines | 0.24% | 2.77% | 34 of 6,103 (13 ≥0.9) |
| Baselines | 4–5 lines | 0.12–0.29% | 1.3–1.8% | 0 |

Two conclusions must be stated together:
1. **`compare.py` cannot detect a deep rewrite.** One file (DoubleTap) scored 0.000 and ranked 400th of 798 Tinycast files, indistinguishable from unrelated code. So the README's low score is equally compatible with "written independently" and "rewritten from Tinycast".
2. **A moderate rewrite that keeps the file structure is caught by renamed fingerprints** (median 0.122, and the true source ranks first). Thunderstorm's per-file distribution (median 0.022, best match at most 0.077) overlaps with the baselines, so **the data do not support "a structure-preserving, file-by-file port of the whole codebase"**. Still not excluded: deep restructuring rewrites, fragment-level borrowing merged into large files, and design-level borrowing, which is where this audit's other signals point.

### 5.4 Additional signals that survive renaming
| Signal | Thunderstorm | Baseline A | Baseline B |
|---|---|---|---|
| Near-duplicate comments / UI text (score ≥0.5 / ≥0.7 / ≥0.9; 6,103 / 4,417 / 4,751 items) | **34 / 20 / 13** | 0 / 0 / 0 | 0 / 0 / 0 |
| Distinctive type names (prefix removed) shared with Tinycast | **8.3%** (83 of 997) | 3.2% | 0.7% |
| Shared string literals (≥14 chars) | **10.8%** | 3.5% | 0.6% |
| Enum case-set matches (≥4 shared cases, Jaccard ≥0.5) | **11 / 77** | 4 / 45 | 1 / 58 |
| Ordered literal sequences (≥4 in a row) | **52, longest 10** | 2 | 1 |

Many shared strings and ordered sequences are dictated by external specs (OAuth/PKCE fields, MCP and Anthropic/OpenAI APIs, Raycast colour names, claude CLI flags); these were removed one by one during verification and are not counted. Near-duplicate prose is least affected by external specs and shows the largest gap from the baselines.

---

## 6. Key evidence (independently verified)

Ordered by how datable and traceable each item is. Line numbers refer to the 10-11 snapshot; "first seen" is from `git log --all --reverse -S`. Full side-by-side excerpts: [EVIDENCE.md](EVIDENCE.md).

### 6.1 Verbatim or near-verbatim comments and text
| # | Thunderstorm | Text (excerpt) | First seen in Tinycast | Adjacent code |
|---|---|---|---|---|
| 1 | ThunderstormWindowController.swift:231 | "Open disarmed: a pointer already over a row must not highlight it." | 08-07 (`946c5907`, compacted from a longer 07-24 version) | Followed by a call with the same name, `disarmHoverHighlight(pointerAt: NSEvent.mouseLocation)` |
| 2 | ThunderstormView.swift:540 | "Identical metrics in both states, so typing can't move the search bar." | 08-07 (compacted version) | Same three modifiers in the same order, renamed |
| 3 | ThunderstormView.swift:487 | "Matches the list rows and section headers' own indent below." | 08-11, outside contributor zkmn73 (#208) | Same header HStack sequence |
| 4 | ThunderstormView.swift:489 | "Every sub-screen leaves the same way, so the slot reads the…" (re-wrapped) | 09-09 (#504, the commit that introduced HeaderBackButton) | As above |
| 5 | ThunderstormView.swift:336 | "Never conditionally mounted: unmounting strands SwiftUI's hover target and eats clicks." | 08-23, outside contributor notsoshu (#318; the commit message documents how the bug was found) | `Color.black.opacity(0.001)` + `contentShape` + `DragGesture(minimumDistance: 0).onChanged` + `allowsHitTesting`, structurally identical; `.onChanged` is the 09-18 #864 revision |
| 6 | ThunderstormView.swift:2649; ThunderstormDropletsLibraryView.swift:122 | "Snap to the origin on the first row so its header shows too." | 08-07 | Modifier chain padding → hide system scrollers → edge dissolve → thin scrollbar → this comment → selection following, in the same order; the second copy is in a Droppy-only droplet file |
| 7 | ThunderstormDropletLibraryRow.swift:61 | "Selection wins over hover when a row is both; otherwise hover shows its fainter layer." | **06-30** (third day of the repository) | The 4-line `fill` computation below is structurally identical; this file has the highest renamed containment in compare.py (0.212) |
| 8 | ThunderstormView.swift:2376 | "…primary action and the Actions toggle sharing one glass capsule." | 07-11 | Same function name `actionGroup`, `HStack(spacing: 2)`, key caps, glass capsule, same order |
| 9 | ThunderstormView.swift:975 | "…lands under the pointer, which chose no row of it, so it opens disarmed" | 08-29 (`bf3be599`) | Followed by the same `disarmHoverHighlight(pointerAt:)` call |
| 10 | ThunderstormAppIndex.swift:635; SearchModel.swift:1248 | "The opening list stays alphabetical: a list that reorders as you use it is unscannable." | 09-04 (existed in Tinycast only from 09-04 to 09-23) | Different implementation (borrowed wording) |
| 11 | ThunderstormFileSearchScreen.swift:10-12 | Header lists the filter as "All, Folders, Documents, Images, Audio, Video, Archives, Code, and a Finder tag": **the first seven are exactly the seven cases of Tinycast's `FileSearchFilter`, in order** (Tinycast has only those seven; Code and the Finder tag are Thunderstorm's additions) | 09-12 (`5d8dbb77`) | **Contradicts Thunderstorm's own enum order** (anyKind, documents, pdfs, images, videos, audio, code, archives, folders, with a "folders last" rationale): an un-updated leftover |
| 12 | ThunderstormView.swift:408-410 | The menu-animation comment calls it "the reference launcher's menu panel motion"; constants scale 0.94, `timingCurve(0.2,0.7,0.2,1)` 0.10, `timingCurve(0.4,0,1,1)` | 09-13 / 09-18 (0.14 → 0.10) | All five constants identical |
| 13 | ThunderstormSelectionCapture.swift:110 | "Select text in another app first." | 08-27 | No public source found online |
| 14 | ThunderstormQuickActionStore.swift:134-136 | Fix Grammar prompt: same four-part skeleton; "change only what is wrong" and "If nothing is wrong" verbatim | 08-27 (unchanged since) | The other three prompts were rewritten in Thunderstorm's own style; only this one was not |
| 15 | ThunderstormCalcParser.swift:5-16 | File header is a condensed paraphrase of the Arithmetic/Units sections of Tinycast's calculator docs, with the same examples (`10kg + 20%`, `5 3`, `5kg + 5`, `3x3`) | 07-29 to 09-13 (wording matches the 09-13 docs, not the 08-19 ones) | Different parsing algorithm (spec-level derivation) |

### 6.2 Data, constants and design tokens
- **Colour-opacity table** (ThunderstormStyle.swift:126-155): 11 (dark, light) pairs identical to Tinycast's `Theme.Colors.ramp`, pair for pair and in the same order (selection 0.10/0.09, rowHover 0.05/0.045, separator 0.10/0.12, controlSurface 0.10/0.08, border 0.20/0.18, textTertiary 0.40/0.42, menuSymbol 0.70/0.70, …). The light-mode values were hand-tuned in Tinycast on 08-19 (#274). It also carries Tinycast's `.tint(.clear)` quirk and frost 0.05/0.25, which Tinycast removed on 09-23, so the source predates 09-23.
- **Twenty-plus sizes, font sizes and durations** and their derivation formulas match Tinycast's Theme / InterfaceMetrics (276, 36/52, 28, 22, menu row height = icon + 2 × spacing, compact height = header height + 2 × header padding, menus show at most 5.5 rows, width 320, …), each with a step-by-step history in Tinycast.
- **Hover arming:** the threshold is 3 pt on both sides (Tinycast `HoverArming.slop = 3`, with probe measurements in the 08-11 commit). Every sibling member of the same object was renamed (pointerDidMove, hoverArmed, restingPoint, armingDistance), except `disarmHoverHighlight(pointerAt:)`, which kept its name: the pattern of deliberate renaming with one miss.
- **Meeting-service enum** (ThunderstormMeetingLinks.swift:26-39): Tinycast's 10 named services in their original order (zoom, googleMeet, teams, webex, jitsi, whereby, chime, goTo, blueJeans, …), with Thunderstorm only appending at the end (Tinycast first seen 08-22/23).
- **Volume snapping to a 5% grid:** same rounding formula (±ε then floor+1 / ceil−1), same example "37% → 40%" (Tinycast 08-02, evolved from a 1/16 step, with a test).
- **Keyword expansion:** buffer cleared after 15 s idle (Tinycast 07-30, outside PR). The shell runner suggests enabling a login shell on exit status 127, with an 8 KB failure tail, 256 KB output cap and 2 s SIGTERM → SIGKILL (Tinycast 07-29, 08-29).
- **File search "recent files":** two Spotlight queries merged, last-used within 30 days plus content-modified within 3 days; the home folder expanded into its visible subfolders (excluding Library), with files at the home root handled separately (Tinycast 08-10, 09-12).

### 6.3 Rename leftovers and data-model remnants
- **Old quicklink field names** (ThunderstormQuicklinks.swift:83-89): `EarlierCodingKeys` reads `iconSymbol`, `openWithBundleID` and `isEnabled` written by "earlier builds", exactly the persisted field names of Tinycast's `Quicklink` (08-04, 08-30). The Raycast importer also lists `openwithbundleid` as a candidate key, though real Raycast exports have no such key. The binary analysis shows that the released 16.0.x actually wrote `openWithBundleID` (§3.7 B5); which build wrote `iconSymbol` / `isEnabled` cannot be determined.
- **Workspaces migration table** (ThunderstormWorkspaces.swift:88-97): `auto, focus, stack, columns, grid, custom`, the raw values of Tinycast's `RoomLayoutKind`, in order (09-25). The upstream MIT project Rooms uses `mine`; `custom` is Tinycast's own rename.
- **Incomplete rename** (ThunderstormActionMenu.swift): the stored property is `beginsGroup`, but the initializer label is still Tinycast's `startsSection:` (about 109–117 call sites; Tinycast 09-10, #537).
- **Dead API:** `ThunderstormBarButtonChrome`'s `.rounded`, `isCompact` and `isSelected` are never used in Thunderstorm beyond their declaration, while all of them are used in Tinycast (`isSelected` / `isCompact` added by outside contributor Ales M on 09-18, #880). Unused parameters copied from someone else's API are a trace that independent implementations rarely leave.
- **Self-described predecessor** (ThunderstormScrolling.swift:32-37): the comment says scroll requests "used to be fresh UUID-stamped values", which is Tinycast's `ScrollIntent(nonce: UUID())` design (07-30).
- **Hex colour parsing** (ThunderstormExtensionNode.swift:386-424): the ternary-shift `hasAlpha ? 24 : 16` form is line-for-line equivalent to Tinycast's 08-14 version, which Tinycast deleted on 09-19; none of 1,668 unrelated Swift files on the auditor's machine use this form.

### 6.4 Items downgraded or refuted during verification (how over-claiming was avoided)
- Clipboard filter order, ⌘. to pin, ⌘P to filter, holding ⌘ to show numbers: prescribed by Raycast's official manual → downgraded to weak.
- Most ⌘K row-action menu items (Move Favorite Up/Down, ⇧⌘F, Reset Ranking, Hide from Root Search): prescribed by Raycast → downgraded to moderate.
- The large Raycast Icon → SF Symbol table: most matches are forced by which SF Symbols exist, and none of Tinycast's ~25 most idiosyncratic mappings were kept → downgraded to weak.
- Placeholder modifiers (uppercase / lowercase / trim / percent-encode / json-stringify / raw), MCP/OAuth fields, API request bodies, CLI flags: external specs → not counted.
- The exception set "hotkeys and number keys do not train ranking": the analyst's facts were wrong → **refuted**.
- Same-named types such as PhotoCapture, RightClickCatcher, CalcDimension, WindowLayoutRunner: mostly Apple/Swift idiom or natural domain naming → weak-to-moderate on their own.

---

## 7. Assessment of the specific claims

| Claim (by the Tinycast author) | Assessment |
|---|---|
| "Ripped off my entire Tinycast code base and fed it to AI" | **Partly supported, not proven as a whole.** A port did happen in September (admitted by Droppy), the 10-11 launcher shell still contains traceable leftovers, and several feature modules are derived at the spec and design level. But there is no evidence that the 115k lines as a whole are an AI rewrite of Tinycast: many modules have a different architecture and depend on Droppy's host, and the per-file fingerprint distribution matches the baselines. On "fed to AI": Droppy openly says it builds with AI tools, and its MRs show Claude Code markers and a `codex/` branch name, but this cannot establish whether any given code was produced by an AI rewriting Tinycast. |
| The logo is also a bolt | **Not supported.** Thunderstorm's name and icon predate Tinycast (Wayback 05-12); the designs differ (two-layer angular bolt vs. rounded flat bolt); a bolt is a generic launcher motif. |
| Sold as a paid product | Fact: Droppy is paid software and Thunderstorm is built into it. Droppy says payment covers the whole app. Not a technical question in itself, but relevant to the licensing issues in §8. |
| Leftover placeholder text | **Supported, and broader than Droppy admits.** Droppy admits the search prompt and quicklink example slipped into 16.0 (since changed); this audit still finds 13 comments/strings with similarity ≥0.9 (plus 21 paraphrases between 0.5 and 0.9) in the source after the 10-11 "last pass", as well as UI strings such as "Look up a word…" and "Select text in another app first." |

| Droppy's statement | Assessment |
|---|---|
| Thunderstorm predates Tinycast | **True for the name, icon and basic search** (independent evidence: 05-12 snapshot). But most current features have no public record before 06-29, and "13.1 / 35 files" cannot be verified. |
| The September borrowing came with licence and credit | True for the droplet (MR !66); for the built-in version this cannot be verified; the 10-11 release has none. |
| Everything built on Tinycast's code was withdrawn, removed and rewritten (README) | **Ambiguous, partly true.** The droplet was withdrawn, and rewriting did happen (the three-way comparison shows another rewrite after 09-26). But the rewrite kept traceable Tinycast comments, constants, APIs and data and dropped the credit, so "the parts built on Tinycast's code were removed" does not hold. |
| "A handful of example texts … slipped through into Droppy 16.0"; "They are texts, not code" (blog) | **Not supported.** The leftovers include source comments, tuned constants, a colour table, API shapes and data-model key names. |
| The built-in Thunderstorm has no Tinycast code (MR !77, 09-27) | **Contradicts Droppy's own NOTICE from the day before**, which says the built-in launcher files were ported from Tinycast on 09-21 and, after the 09-26 rewrite "with the same metrics and behaviour", are still credited to Tinycast; the 10-11 versions of these files still contain Tinycast leftovers. |
| No more shared than code written before Tinycast existed (0.24%) | The number reproduces, but it is the wrong metric: the literal column approaches 0 for any rewrite; the same run gives renamed 2.77% (1.6–2.2× the baselines); the "June Droppy baseline" cannot be reproduced. |
| "It was removed before any update went out, so no Droppy user ever got his code"; "Not a single Droppy user ever received his code" (blog) | **Contrary to the binary analysis (§3.7, §3.8).** The blog places Thunderstorm's use of Tinycast parts in an unreleased "test version", but the components are absent from 15.2.2-beta.1 and present in the released 16.0.0 / 16.0.1. 16.0.0 / 16.0.1 contain the launcher components Droppy's own NOTICE credits to Tinycast (structure matching Tinycast's design, e.g. `BarButton` field order and the UUID-stamped `ScrollRequest`), Tinycast's search prompt and the quicklink field name `openWithBundleID`, with no Tinycast credit anywhere in the bundle. Binaries do not show function bodies, so how closely 16.0's implementation follows Tinycast line by line cannot be determined. |

---

## 8. Licensing and attribution (facts; legal characterisation requires professional advice)
1. Tinycast has been **AGPL-3.0-or-later** since 2026-07-10; the copyright holder is Abue Ammar.
2. In MR !66 Droppy published the Thunderstorm droplet under the AGPL, relying on a "Tinycast × Droppy collaboration permission"; MR !77 states that this permission "is no longer given".
3. The 10-11 Thunderstorm is published under **GPL-3.0 + Commons Clause**, copyright Jordy Spruit only, with no Tinycast copyright or licence notice anywhere in Sources. The Tinycast copyright headers present in the 09-26 versions of the same files are absent from the 10-11 versions.
4. If the leftovers in §6 are found to be protected expression from Tinycast, the following need legal assessment. The evidence differs greatly in legal weight: source comments and UI text are generally expression; ideas, functionality and facts are generally not protected; single tuned values (a 3 pt threshold, a 15 s timeout) are generally not protected, while the **selection and arrangement of a whole table**, such as the 11 colour pairs, may be a protected compilation.
   - AGPL/GPL require copyright and licence notices to be preserved;
   - whether AGPL-derived parts can be relicensed under GPL-3.0 + Commons Clause (the Commons Clause is a "further restriction" in the sense of GPLv3 §7);
   - compliance of distributing them inside a paid, closed-source host (Droppy).
5. Droppy's own wording in MR !77 (the droplet links DroppyKit and runs inside Droppy, "neither AGPL-compatible") shows it is aware that AGPL code cannot go into Droppy. Whether the leftovers amount to "Tinycast code" is therefore the legal heart of the dispute.

---

## 9. Overall conclusions
1. **Derivation: established.** Five independent lines of evidence: Droppy's own written record (NOTICE, MR !72/!77, README timeline); datable textual leftovers (mostly predating September, some by Tinycast's outside contributors, direction certain); the three-way comparison between the credited 09-26 version and the uncredited 10-11 version; the released 16.0.0 / 16.0.1 binaries, which contain the launcher components Droppy credited to Tinycast, Tinycast's prompt and a Tinycast field name, with no credit; and the pre-collaboration 15.2.2-beta.1 (09-09), in which none of these components exist, independently proving the direction.
2. **Released vs. unreleased modules.** The Tinycast-derived parts identifiable in a binary (component structure, field names, a prompt) shipped to users in 16.0.x. Many modules in the 10-11 snapshot (AI, Quick Actions, calculator, notes, meetings, workspaces, Paste One by One, …) are in no stable release; the Tinycast traces in them (the Fix Grammar prompt, the calculator header, the Workspaces table, the meeting-service table) have two possible origins: code ported during the collaboration and kept until its first publication on 10-11, or new code written after the collaboration with reference to Tinycast. The available material cannot distinguish the two. The only item that can be placed after the end of the collaboration is Paste One by One: Tinycast's Paste Sequentially first appeared at 09-29 07:26 UTC, and 16.0.1 (09-28 21:40 UTC) does not have it.
3. **Type of derivation:** mainly reference-based rewriting. The launcher shell's view layer was renamed with paraphrased comments and its design tokens carried over as whole tables, while its low-level mechanisms were rewritten; the calculator, snippets / quicklinks, meetings and workspaces were reimplemented from Tinycast's specs and documentation, leaving wording, constants and compatibility keys behind. No large verbatim copying or rename-only whole-file ports were found.
4. **Scale:** strong evidence involves 22 files and strong-or-moderate evidence 49 files (about 35k lines in total, though the evidence is usually confined to particular passages), centred on the launcher shell. Relative to 115k lines, the provable leftovers are local; design- and spec-level borrowing is broader but individually weaker, and partly explained by both projects imitating Raycast.
5. **On the public statements:** Droppy's "They are texts, not code", "Not a single Droppy user ever received his code" and "built-in Thunderstorm (no Tinycast code)" are contrary to the evidence, and of "withdrawn, removed and rewritten" only "rewritten" holds; the Tinycast side's "entire codebase copied" goes beyond the evidence. A more accurate description: Thunderstorm absorbed Tinycast's code and design during the collaboration, the rewrite after it ended was incomplete, and the current public version still contains uncredited Tinycast-derived content, concentrated in the launcher shell.

---

## 10. Recommendations
**Further investigation (in order of value)**
1. Obtain Droppy's private history for `66c274b99`, `0e1c336a7`, `6e9447d72`, `a4def4dc9` and the September–October diffs. This is the most direct evidence of whether the rewrite was independent.
2. The binary analysis of 15.2.2-beta.1 / 16.0.0 / 16.0.1 is done (§3.7, §3.8). A 16.0.2 nightly or insider build would show whether the "earlier builds" referenced by the 10-11 migration code used Tinycast's quicklink and Rooms data models.
3. Use the MR !72 diffs and UPSTREAM.patch as a third reference point for a three-way comparison with the 10-11 release, to see whether the Raycast extension, snippet and window-layout modules carry structure over from the droplet.
4. Run AST-level structural comparison (swift-syntax subtree hashing, JPlag/Dolos) on the hotspot files in §6, and have reviewers who do not know which side is which do a blind review.
5. Legal: have a lawyer familiar with the AGPL/GPL assess the copyrightability of the leftovers and licence compliance.

**For Droppy:** restore credit to Tinycast, or genuinely redesign the leftovers listed in §6 (comments, colour and animation constants, APIs such as `disarmHoverHighlight` / `startsSection` / `BarButtonChrome`, the Quicklink and Workspaces compatibility keys, the meeting-service table, the Fix Grammar prompt, the calculator header, etc.); correct the "all withdrawn" and "only text" statements in the README and blog; report the renamed metric and others alongside the literal one in `compare.py` results, and state that it is insensitive to rewriting.

**For Tinycast:** any claim should rest on the specific, datable leftovers in §6 rather than on "the entire codebase". The evidence supports the former, not the latter.

---

## Appendix A: Reproducibility
Repository layout:
- `EVIDENCE.md`: side-by-side excerpts of about 20 of the strongest items (re-extracted from both repositories by anchor text, with exact line numbers), plus the binary findings.
- `scripts/`: the audit's own analysis scripts (`xanalyze.py`, `fuzzy.py`, `sens.py`, `binscan.py`, `fieldmd.py`, `anchor_excerpts.py` and its input `evidence_spec.json`). The first three need Thunderstorm's `verify/similarity.py` and `verify/compare.py` copied into a `ts_verify/` folder next to them and are run with `python3 -I`; they only read files and never execute the audited code. See `scripts/README.md`.
- `data/`: raw `compare.py` outputs (full history, prefix stripped, embedded JS, 09-26 droplet comparison), the parameter sensitivity table, type-name / string / comment / enum / ordered-sequence results and near-duplicate prose matches; `data/binary/` holds the field tables of Thunderstorm types in the three Droppy versions, scan results and DMG checksums.
- **Not included:** Droppy installers or code extracted from them, a copy of the 09-26 droplet source (available from GitLab MR !66), raw AI-agent outputs, or anything from the baseline projects.

Key command:
```bash
git clone https://gitlab.com/droppyformac1/thunderstorm.git
git clone https://github.com/abue-ammar/tinycast.git
python3 -I thunderstorm/verify/compare.py --ours thunderstorm/Sources --theirs tinycast --history
```

## Appendix B: Main public sources
- Thunderstorm source: https://gitlab.com/droppyformac1/thunderstorm
- Droppy blog: https://getdroppy.app/blog/thunderstorm-open-source ; https://getdroppy.app/blog/thunderstorm-raycast-extensions ; https://getdroppy.app/blog/droppy-16-0
- Droplet Store MRs: https://gitlab.com/droppyformac1/droplets/-/merge_requests/22 , /64 , /66 , /72 , /77
- Internet Archive: https://web.archive.org/web/20260512140236/https://getdroppy.app/ ; https://web.archive.org/web/20260623155254/https://getdroppy.app/changelog.json ; https://web.archive.org/web/20260926153817/https://getdroppy.app/
- Droppy release API: https://getdroppy.app/api/releases/latest ; https://getdroppy.app/changelog.json
- Tinycast: https://github.com/abue-ammar/tinycast ; https://github.com/abue-ammar/tinycast/releases
- The accusation: https://x.com/abue_ammar/status/2109257990041981248
- Atoll DMCA (background, unrelated): https://github.com/github/dmca/blob/master/2026/02/2026-02-10-atoll.md
- AlternativeTo news: https://alternativeto.net/news/2026/9/droppy-16-transforms-into-extensible-platform-with-droppykit-and-raycast-extension-support/

---

*This report is licensed under [CC BY 4.0](LICENSE); the scripts are MIT-licensed. Quoted excerpts from Tinycast and Thunderstorm remain under their own licences (AGPL-3.0-or-later; GPL-3.0 + Commons Clause) and are reproduced for commentary and criticism. See [README → License](README.md#license).*
