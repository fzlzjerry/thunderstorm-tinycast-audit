# Thunderstorm 与 Tinycast 代码来源审计报告

> English version: [REPORT.md](REPORT.md) · 并排证据：[EVIDENCE.md](EVIDENCE.md)

> 审计对象：Thunderstorm（Droppy 内置启动器，GitLab `droppyformac1/thunderstorm`，快照 `2ecde78`）与 Tinycast（GitHub `abue-ammar/tinycast`，`126c998d`，全部 990 个提交 / 120 个远程分支）
> 审计日期：2026-10-12
> 审计问题：Thunderstorm 是否抄袭（派生自）Tinycast？
> 方法：本地仓库逐模块比对 + git 历史溯源 + 公开时间线核查 + 量化相似度（含独立基线）+ 对每条发现做独立的反驳性复核 + Droppy 15.2.2-beta.1（合作前）/ 16.0.0 / 16.0.1 发布二进制的静态对比。本报告只陈述技术事实与推断，不构成法律意见。
> 说明：本审计在人工主导下借助 AI 代理（Claude Code）完成，包括逐模块分析与独立的反驳性复核；所有关键结论都附有可公开核验的出处（文件与行号、git 提交、公开网页），并可用 `scripts/` 中的脚本复现。欢迎任何一方指出错误。

---

## 0. 结论摘要

| # | 结论 | 确定程度 |
|---|---|---|
| 1 | **Thunderstorm 曾直接使用 Tinycast 代码，这一点 Droppy 自己有书面记录。** Droppy 在其公开的 Droplet Store 仓库 MR !66（2026-09-26）的 NOTICE 中写明：私有提交 `66c274b99`、`0e1c336a7`（均为 09-21）把 Tinycast 启动器的机制和外观"一比一"移植进**内置** Thunderstorm；09-26 的 `6e9447d72` 只是"以相同的度量和行为"重写，并仍将这些文件署名给 Tinycast。 | 确证（对方自述 + 本审计独立印证） |
| 2 | **10-11 公开的"已重写"源码仍残留 Tinycast 的表达性内容，且删除了署名。** 最典型的是 13 条与 Tinycast 相似度 ≥0.9 的注释/文案（其中 9 条归一化后完全相同，3 条为一方完整包含另一方），两个独立基线都是 0；另有整张配色透明度表、菜单动效常量、自造 API 名（`armedHover`、`disarmHoverHighlight(pointerAt:)`、`BarButtonChrome`）、数据模型遗留键名、会议服务表顺序、提示词骨架等。这些在 Tinycast 中大多早于 9 月，部分出自 Tinycast 的第三方贡献者，方向只能是 Tinycast → Thunderstorm。同一批文件在 09-26 的 droplet 版本中带有"adapted from Tinycast, Copyright (C) 2026 Abue Ammar"的版权头，10-11 版本里没有了。 | 确证 |
| 2b | **已发布的 Droppy 16.0.0 / 16.0.1 也含有可辨认的 Tinycast 派生内容（二进制核查，见 3.7）。** 两个版本中都有：Droppy 自己 NOTICE 署名给 Tinycast 的那批启动器组件，其类型和字段结构与 Tinycast 设计一致（如 `ThunderstormBarButton` 的字段顺序与 Tinycast `BarButton` 完全相同、`ScrollRequest` 的 UUID 戳设计）；Tinycast 的搜索框提示语 "Search for apps and commands…"（与 "Search your Mac" 并存，无法确定实际显示哪条）；quicklink 的持久化键名 `openWithBundleID`（与 Tinycast 的字段名相同）。整个应用包中没有任何 Tinycast 署名或许可声明，而其他 5 个第三方来源都附了声明。**合作前的 15.2.2-beta.1（09-09）中这些组件全部不存在**（见 3.8），因此来源方向可以独立证明，不依赖 Droppy 的自述。 | 确证（二进制只能看到类型、字段、枚举和字符串，看不到注释和函数体） |
| 3 | 因此，Droppy 博客所说的残留"are texts, not code"（是文本不是代码）、"Not a single Droppy user ever received his code"（没有一个 Droppy 用户收到过他的代码），以及 MR !77 所说的"built-in Thunderstorm (no Tinycast code)"（内置 Thunderstorm 不含 Tinycast 代码），**至少对启动器外壳不成立**：残留不只是界面文字，还包括源码注释、调校常量、组件分解和 API 形态。README 的"凡建立在 Tinycast 代码上的部分均已撤回、移除并重写"有歧义：重写确实发生过（见 3.4），droplet 也确实下架了，但重写没有清除可溯源的 Tinycast 内容。 | 确证 |
| 4 | **没有发现大段逐字复制，也没有"只改名、不改结构"的整文件移植。** 最长相同片段 5 行，与独立基线持平；按文件的指纹分布也与基线重合。启动器底层机制（滚动、悬停追踪、按键路由）、Raycast 扩展 JS 运行时（Node 进程 vs JavaScriptCore）、AI/MCP、计算器解析器、词典、备份引擎、Raycast 导入等大量部分是不同实现，并深度依赖 Droppy 自有的宿主服务。 | 高 |
| 5 | Tinycast 作者指控的"把整个 Tinycast 代码库喂给 AI"：**现有证据既不能证实，也不能排除。** Thunderstorm 自带的 `compare.py` 的低分不能当作反证：本审计的 AI 改写对照实验中，一个 100% 派生的文件得分为 0.000。但对"整体逐文件移植"的说法，现有数据也不支持。可以确认的是：派生集中在启动器外壳和若干功能的局部；设计和规格层面的借鉴（功能拆分、交互规则、文档化的规格）覆盖面更广。 | 中 |
| 6 | **时间线**：Thunderstorm 的名称、图标和基础搜索**早于** Tinycast（Wayback 2026-05-12 快照已有）。但现行版本的大部分功能（计算器与换算、quicklinks、snippets、Raycast 扩展、窗口布局、笔记、备份等）在 Tinycast 出现之前都没有任何公开记录，且集中在 9 月 21–27 日合作期间或之后才出现。 | 高 |
| 7 | **图标指控不成立**：Thunderstorm 的名称和闪电图标早于 Tinycast；两者造型不同；Tinycast 的闪电（07-13）取自 SVG Repo 的现成素材。 | 高 |
| 8 | **许可与署名存在实质问题（需法律意见）**：Tinycast 是 AGPL-3.0；Thunderstorm 公开版是 GPL-3.0 + Commons Clause，版权只署 Jordy Spruit，源码中没有任何 Tinycast 署名；Droppy 自己在 MR !77 写明"合作许可已不再提供"。 | 事实确定；法律定性待定 |

**一句话结论**：Thunderstorm 不是 Tinycast 的整体复制品，有相当部分是 Droppy 独立的实现；但它在 2026 年 9 月确实吸收了 Tinycast 的代码与设计（Droppy 自己承认过），其中可从二进制辨认的部分（组件结构、字段名、提示语）随 Droppy 16.0 发给了用户，且没有署名；10-11 公开的"重写版"也没有清理干净：启动器外壳中仍有可定年、可溯源到 Tinycast 的注释、常量、API 和数据残留。Droppy 所说的"are texts, not code""Not a single Droppy user ever received his code"以及内置版"no Tinycast code"都不符合事实；说"整个代码库被抄"也超出了证据。

---

## 1. 审计范围、材料与局限

### 1.1 材料
- Thunderstorm：256 个 Swift 文件，115,395 行；`verify/compare.py`、`verify/similarity.py`；README、LICENSE（GPL-3.0 + Commons Clause）。
- Tinycast：798 个应用 Swift 文件（119,430 行）+ 103 个测试文件（38,599 行）+ Raycast JS 运行时；git 全历史 990 个提交（main 上 804 个）、120 个远程分支、116 个标签。
- 公开资料（只读）：Droppy 官网 changelog / 博客 / API、Internet Archive 快照、GitLab Droplet Store 仓库的 MR 描述和 diff、Tinycast GitHub releases、Tinycast 作者的 X 帖文本（经 api.fxtwitter.com 读取，附带的图片和视频未查看）、GitHub DMCA 公示库。
- 已发布二进制：Droppy 15.2.2-beta.1（09-09，合作前基线）、16.0.0 与 16.0.1 的官方 DMG（来源为 getdroppy.app 发布接口所指向的 `droppy-releases.jordylegrand.workers.dev`，MD5 与服务器 ETag 一致，校验和见 `data/binary/dmg_checksums.txt`）。只读挂载、只做静态分析，没有运行其中任何程序。
- 独立基线：两个与本案无关、未公开的 macOS Swift 项目（下称基线 A，约 5.7 万行；基线 B，约 9.2 万行；已剔除第三方库、构建产物和副本），用同样的方法与 Tinycast 比较，用来衡量"巧合"水平。

### 1.2 方法
1. 复现 Thunderstorm 自带的 `compare.py`，并做去前缀实验、基线对照和参数敏感性分析。
2. 自写比对：类型名、字符串字面量、注释、枚举 case 集合、有序字面量片段，以及注释和文案的近似匹配（词三元组）；每个命中都标注它在 Tinycast 历史中首次出现的提交与日期。
3. 13 个模块各由一名分析员（AI 代理）逐段对照源码（含 Tinycast 的历史版本）。每份结果交给一名独立的复核员（另一个 AI 代理），要求他尝试推翻每条发现：是否由 Raycast 规范或 Apple 样板决定、是否为协议常量、是否为通用词汇或巧合、方向是否可能相反。
4. 横向分析：git 历史取证、公开发布时间线、比对方法审查（含 AI 改写对照实验）。
5. 三方比对：Tinycast ↔ Droppy 09-26 droplet 版（带 Tinycast 署名）↔ 10-11 公开版。

### 1.3 局限（请先读这一节）
- **Thunderstorm 的"提交记录"基本无法审计。** 公开仓库只有 2 个提交（10-11 一次性导入 115,139 行，加一个 README 图标提交）。README 引用的 Droppy 提交 `a4def4dc9` 不在仓库中，Droppy 主仓库是私有的（GitHub `iordv/Droppy` 自 2026-02-23 起因一宗无关的 DMCA 返回 451；GitLab `droppyformac1/droppy` 返回 404）。所以任何文件或函数何时写、谁写、如何演化，都无法从 Thunderstorm 一侧核实。
- README 用作基线的"Droppy 2026 年 6 月全量代码"未公开，无法复现。
- 已分析 Droppy 15.2.2-beta.1 / 16.0.0 / 16.0.1 的发布二进制（见 3.7、3.8），但二进制已剥离符号，只能看到类型名、存储属性名、枚举 case 和字符串常量，看不到注释、函数名和函数体。拿不到内部 / nightly / insider 构建。
- Tinycast 的大型外部 PR 以 squash 方式合并，PR 内部历史不可见；git 署名无法核实真实身份。
- 相似性证据只能说明来源与相似程度。"是否构成 AGPL 意义上的派生作品"属于法律问题。

---

## 2. 背景与双方说法

| 时间 | 事件 | 来源 |
|---|---|---|
| 2026-02-10/23 | Atoll（另一款 GPL-3.0 的 macOS 开源项目）的版权人就 6 个文件对 `iordv/Droppy` 提出 DMCA，仓库被 GitHub 屏蔽。**与本案无关，仅作背景**，也说明此后 Droppy 源码不可公开访问。 | github/dmca 公示 |
| 2026-03-16（自述） | Droppy 称 Thunderstorm 随 13.1 首发（剪贴板搜索 + 命令目录，35 个文件）。**无法核实**：changelog 中没有 13.0/13.1 条目，03-15、03-29、04-13 的首页快照都没有 Thunderstorm。 | Droppy 博客、README |
| 2026-05-12 | Wayback 首页快照首次出现 Thunderstorm（"通用搜索与剪贴板启动器"）。**这是早于 Tinycast 的独立证据。** | web.archive.org |
| 2026-06-14/15 | 14.1.0-beta：Spotlight 式搜索条、文件操作、系统动作、quit all / eject all。没有计算器、quicklinks、snippets、扩展、AI、窗口管理。 | Wayback 存档的 changelog.json |
| 2026-06-28/29 | Tinycast 仓库首个提交（"initial mockup done"）；07-10 由 GPL-3.0 改为 AGPL-3.0（`eaa581dd`）。 | Tinycast git |
| 2026-09-21 | Droppy 私有提交 `66c274b99`（"Make Thunderstorm behave like the Tinycast launcher, not just look like it"）与 `0e1c336a7`（"Give Thunderstorm the Tinycast launcher one to one"）。 | Droppy 自己的 NOTICE（MR !66） |
| 2026-09-23 | MR !22：完整的 Tinycast（上游 `d93a09b`）作为 droplet 运行在 Droppy 内，描述写明它"取代 Thunderstorm"。 | GitLab droplets |
| 2026-09-26 | `6e9447d72` 以"相同的度量和行为"重写；MR !64 删除 Tinycast droplet；MR !66 以 AGPL 发布 Thunderstorm droplet，NOTICE 逐文件署名 Tinycast。 | 同上 |
| 2026-09-27 | MR !72（分支 `codex/thunderstorm-tinycast-parity`）："Thunderstorm 1.1.0：用 Tinycast 的非 AI 引擎替换部分启动器"，加入 Raycast 扩展、snippets、quicklinks、窗口布局与 Rooms、笔记、备份等；3 小时后 MR !77 下架，理由是引擎为 Tinycast（AGPL）、合作许可已不再提供，并称"Droppy 保留不含 Tinycast 代码的内置 Thunderstorm"。同日博客宣布内置 Thunderstorm 支持 Raycast 扩展，所列功能与 MR !72 几乎一一对应。 | GitLab droplets、Droppy 博客 |
| 2026-09-27/28 | Droppy 16.0.0：changelog 标注 09-27，只写"重建 Thunderstorm"；Wayback 显示 09-27 15:20 UTC 时最新版仍是 15.2.2-beta.1，故实际上线在 09-27 15:20 UTC 至 09-28 之间（README 写 09-28）。16.0.1 于 09-28 21:40 UTC 发布，截至 10-12 仍是最新稳定版。 | changelog、/api/releases/latest、Wayback |
| 2026-10-11 12:21 UTC | Tinycast 作者在 X 发帖指控 Droppy "rip off" 整个 Tinycast 代码库并用 AI 改写；同时提到闪电 logo、付费销售、残留占位文本。 | X（经 fxtwitter 读取） |
| 2026-10-11 16:56 UTC | Thunderstorm 源码提交（指控发出约 4.5 小时后）；README 称当天做了"最后一轮替换残留名称、标签和占位文本"，并称这是"下一次 Droppy 更新"的代码，不对应任何已发布版本。 | Thunderstorm git、GitLab |

---

## 3. 提交记录分析

### 3.1 Thunderstorm 仓库
- 2 个提交，作者和提交者都是 Jordy Spruit `<hi@getdroppy.app>`：`e5c02a12`（10-11 18:56 +0200，导入全部源码、许可证与 verify 脚本），`2ecde783`（19:05，加入图标和徽章）。对象库共 282 个对象，全部可达，没有悬空对象、标签或其他分支。
- **结论**：这是一个经过整理的单次快照，不含任何开发历史，无法回答"哪段代码何时由谁写入、是否从 Tinycast 改来"。
- 源码内部可见的日期线索：注释中自引用的日期只有 2026-09-01、09-06、09-27（"Alpha: early, and in testing (Jordy, 2026-09-27)"）、09-29、10-04/05、10-10，没有任何早于 9 月的。这是弱证据，但与"现存代码大多写于 9–10 月"相符。
- 对 Thunderstorm 有利的线索：代码里有面向旧版本设置的迁移逻辑（如 `thunderstormFavoriteApplicationPaths`、`migrateLegacySpotIfNeeded`），说明此前确实存在已发布、并保存过用户设置的早期 Thunderstorm。
- 风格指纹：Thunderstorm 约 1.5 万行注释中只有 1.19% 超过 80 列（它习惯在约 76 列折行）。而与 Tinycast 逐字相同的单行注释恰好落在这 1% 里，例如 "Selection wins over hover…" 94 列、"Identical metrics…" 81 列。这符合"照搬 Tinycast 的单行注释、没有按自己的习惯重新折行"的情形。

### 3.2 Tinycast 仓库
- 规模与节奏：990 个提交；按月份为 6 月 16 个、7 月 255 个、8 月 181 个、9 月 355 个、10 月（截至 10-10）183 个；116 个标签，从 v0.1.0-alpha.4（07-03）到 v0.11.19（10-10）。
- 作者：abue-ammar 约 789 个提交，另有约 67 位外部作者（Jonas List 43、Clément Knoderer 25、notsoshu 22……），时区分布在 +0200 到 +0800 之间。
- 有机演化的迹象：初期典型的个人提交噪声（"fixed""much better""excelent work"）；07-27 起改为编号 PR 并附长篇说明；2 次 revert；08-05 至 08-07 的大规模重构（`Core/` 拆入 `Features/<Name>/`，并写下命名词汇表，如 PaletteViewModel 改为 PaletteState）；类型逐步演化（如 `BarButton` → `BarButtonChrome(.capsule/.menu)` → `.rounded` → `isSelected/isCompact`）。
- **两次注释压缩**（对判断方向很关键）：`946c5907`（08-07，#197）把 181 个多行注释块压成单行；`fde9228c`（08-29，#382）再压缩 397 块。许多 Tinycast 单行注释的现行措辞诞生于这两次压缩。**Thunderstorm 中出现的全部是压缩后的措辞**，所以其来源只能是 08-07 之后的 Tinycast 文件版本。
- 合作痕迹：在 Tinycast 全部分支的提交信息和 diff 中搜索 droppy / droplet / spruit / thunderstorm 等词，结果为 0（仅 2 个与 Raycast 图标名、emoji 关键词相关的误报）。Tinycast droplet 的宿主层位于 Droppy 的 droplets 仓库，不在 Tinycast 仓库内，这与 MR !22 的描述一致。

### 3.3 Droppy 侧的公开"提交记录"：Droplet Store MR
由于 Thunderstorm 本身没有历史，Droppy 公开的 Droplet Store 仓库（`gitlab.com/droppyformac1/droplets`，09-22 创建）的 MR 是目前能看到的、最接近 Droppy 开发记录的材料。相关 MR 均由账号 `droppyformac` 提交，多条带有 "Generated with Claude Code" 标记。

| MR | 时间（UTC） | 内容 |
|---|---|---|
| !22 | 09-23 12:17 | Tinycast 1.0.0 droplet：以上游 `d93a09b` 构建的完整 Tinycast 在 Droppy 内运行，"取代 Thunderstorm" |
| !40 | 09-23 起 | Tinycast 1.1.1：把 Thunderstorm 用户的别名、收藏、快捷键迁移进 Tinycast |
| !64 | 09-26 15:20 | 删除 Tinycast droplet，"Thunderstorm 重新成为 Droppy 的启动器" |
| !66 | 09-26 19:44 | Thunderstorm 1.0.0 droplet（AGPL-3.0-or-later），附 NOTICE.md，逐文件列出改编自 Tinycast 的部分 |
| !72 | 09-27 13:25 | 分支 `codex/thunderstorm-tinycast-parity`："用 Tinycast 的非 AI 引擎替换部分启动器"，带入 Raycast 扩展（含 Tinycast 的 JavaScriptCore 运行时）、snippets、quicklinks、窗口布局与 Rooms、笔记、备份等；宿主集成在私有 `droppy!3460/!3461` |
| !77 | 09-27 16:19 | 下架 Thunderstorm droplet：引擎是 Tinycast（AGPL），合作许可已不再提供；"Droppy 保留不含 Tinycast 代码的内置 Thunderstorm" |

MR !66 NOTICE 的要点（转述）：
- 私有提交 `66c274b99`（09-21）从 Tinycast palette 移植了：滚动意图、浮动栏之间的选中跟随、细覆盖滚动条（`ThunderstormScrolling`）；"指针移动才启用悬停"（`ThunderstormPointerState`）；`ThunderstormPanel.sendEvent` 与"打开时解除悬停"（`ThunderstormWindowController`，来自 Tinycast `PalettePanel.swift` / `PaletteWindowController.swift`）；底栏菜单（`ThunderstormView`）；图标光栅化（`ThunderstormIconProvider`）。
- 私有提交 `0e1c336a7`（09-21）让启动器的布局、字体和颜色"一比一"跟随 Tinycast palette：`ThunderstormStyle`（当时叫 `ThunderstormTheme`）、`ThunderstormLauncherChrome`、`ThunderstormLayout`、`ThunderstormView`、`ThunderstormActionMenu`（由该提交创建）。
- `6e9447d72`（09-26）把 Scrolling、Theme/Style、chrome 的边缘溶解和控件、动作菜单"重写为 Droppy 自己的代码，度量和行为不变"，并说明这些文件**仍然署名 Tinycast**。

**这些说法与本审计的独立发现高度吻合**：第 6 节中证据最强的两个模块（palette-view、palette-window）正是 NOTICE 点名的这批文件。

### 3.4 三方比对：09-26 droplet 版 ↔ 10-11 公开版
从 MR !66 取得 09-26 的 droplet 源码（54 个文件，其中 NOTICE 点名的文件都带有 "Parts of this file are adapted from Tinycast, Copyright (C) 2026 Abue Ammar" 版权头），与 10-11 公开版中的 28 个同名文件比较：

- NOTICE 点名的启动器文件，两版之间的指纹包含度很低：Scrolling 0.01、PointerState 0.00、ActionMenu 0.08、Layout 0.05、View 0.10、WindowController 0.13、LauncherChrome 0.13、Style 0.18。**说明 09-26 之后又重写了一遍。**
- 但 Tinycast 的逐字注释**在两版中都存在**："Open disarmed: a pointer already over a row must not highlight it."（WindowController）、"Identical metrics in both states, so typing…"、"Snap to the origin on the first row so its header shows too."、"Never conditionally mounted…"（View）、"Selection wins over hover when a row is both…"（09-26 在 LauncherChrome，10-11 出现在 Droppy 独有的 DropletLibraryRow 中）。
- 09-26 版有 Tinycast 版权头；10-11 版没有任何 Tinycast 署名。
- NOTICE 未点名的文件（SearchService、UtilityIntentEngine、UsageStore 等，属 Droppy 自有代码）两版高度相似，最长相同片段达 102 行，说明比对方法本身能识别出同源代码。

**解读**：10-11 公开版的启动器外壳确实经过了第二轮重写，但重写保留了 Droppy 自己两周前还标注为"改编自 Tinycast"的文本和设计元素，同时移除了署名。

### 3.5 抄袭方向的判断
- Thunderstorm 源码在 10-11 前不可公开读取；源码注释和内部标识符也无法从发布的二进制中还原。因此，**凡是在 Tinycast 中早于 9 月出现、又逐字出现在 Thunderstorm 中的注释，方向只能是 Tinycast → Thunderstorm**（或纯属巧合；但两个基线的近似注释命中都是 0）。
- 有三条最强的注释出自 Tinycast 的第三方贡献者（zkmn73 #208，08-11；notsoshu #318，08-23；Ales M #880，09-18），时区与 Droppy 作者不同，排除了"Droppy 作者以化名向 Tinycast 投稿"的解释。
- 需要注意：Droplet Store 仓库自 09-23 起公开了 Tinycast droplet 的源码，自 09-26 起公开了 Thunderstorm droplet 的源码。因此，**Tinycast 在 09-26 之后新增、又与 Thunderstorm 相同的元素，理论上可能是反向流动**，需要逐条判断（见 3.6）。另外，用户可见的界面文字可以从 Droppy 二进制中看到，方向推理对这类元素要打折扣。

### 3.6 合作结束后才出现在 Tinycast 中的元素
| 元素 | Tinycast 首见 | 评估 |
|---|---|---|
| Paste Sequentially（Thunderstorm 中叫 "Paste One by One"，内部标识仍是 `paste-sequentially`） | 09-29（`44e475f4` → #1221，09-30，含测试与 settle 修复） | 最有分量：`idleTimeout` 同为 60、遍历方式同构、内部名未改。**二进制核查：16.0.0 / 16.0.1（09-28）中没有 `paste-sequentially` 和 `ThunderstormClipboardSequence`**，排除了"Droppy 先在发布版中有此功能"。方向为 Tinycast → Thunderstorm 的可能性高，且发生在合作结束之后 |
| Keep Calculating（⌘↵ 把答案回填搜索框） | 10-05（#1324，源自 10-03 的 issue #1297） | Tinycast 侧来源自然。16.0.x 中没有这一功能，也没有 10-11 版的类型化计算器（`ThunderstormCalc*`）。方向倾向 Tinycast → Thunderstorm，但独立想到同一功能的可能不能排除 |
| 会议详情页 | 10-02（#1265） | ⌘I/⌘O 是 macOS 惯例，参会状态由 EventKit 决定；中偏弱 |
| AI 回复中的 LaTeX 数学 | 09-30（#1238） | 渲染引擎完全不同；不构成证据 |
| "Runs on this Mac. Nothing leaves it." | 实际 09-13 至 09-19 已逐步成形 | 应归为合作期内；常见隐私表述，中偏弱 |
| QuicklinkEditorScreen 等类型名 | 10-10（#1488） | 由两边已有的命名惯例即可推出；弱 |

### 3.7 已发布二进制核查：Droppy 16.0.0 / 16.0.1
**材料**：官方 DMG，16.0.0（build 16009999，64.7 MB）与 16.0.1（build 16019999，67.2 MB），均由 "Developer ID Application: Jordy Spruit (NARHG44L48)" 签名。16.0.0 的签名时间戳为 **2026-09-27 22:14 UTC**，正好落在 §2 根据 Wayback 推出的上线窗口（09-27 15:20 UTC 至 09-28）内；16.0.1 为 09-28 21:31 UTC，与发布接口的 21:40 UTC 吻合。主程序为 x86_64 + arm64 通用二进制，符号表已剥离，但 Swift 反射元数据（`__swift5_fieldmd` / `__swift5_reflstr`）和字符串常量仍在。本审计自写解析器读取字段描述符，得到每个类型的存储属性名和枚举 case 名（16.0.0 共 4,870 个描述符，其中 266 个属于 Thunderstorm）。

**发现**

| # | 发现 | 意义 |
|---|---|---|
| B1 | 16.0.0 中有 Droppy NOTICE 点名、署名给 Tinycast 的那批启动器组件：`ThunderstormPointerState`（字段 `hoverArmed`、`commandHeld`、`menuOpen`、`armingDistance`、`restingPoint`）、`ThunderstormArmedHover`、`ThunderstormBarButton` / `ThunderstormBarButtonChrome {capsule, rounded}`、`ThunderstormKeyCap.Style {outline, filled}`、`ThunderstormMenuCircleButton`、`ThunderstormHeaderBackButton`、`ThunderstormRightClickCatcher`、`ThunderstormMenuItem`（已用 `beginsGroup`）。 | 这些组件随 16.0 发给了用户 |
| B2 | `ThunderstormBarButton` 的字段依次为 `chrome, isSelected, isCompact, action, label, hovered`，与 Tinycast `BarButton`（`isSelected` / `isCompact` 由第三方 Ales M 在 09-18 #880 加入）的属性顺序完全相同；`KeyCap.Style` 的 `outline, filled` 与 Tinycast `KeyCapChip` 相同。 | 发布版的组件结构与 Tinycast 09-18 之后的版本一致 |
| B3 | 16.0.0 有 `ThunderstormScrollRequest`：`Goal { resetToTop, revealSelection }` 加每次新生成的 `UUID` 戳。这与 09-26 droplet 版相同，对应 Tinycast `ScrollIntent`（Equatable + `nonce = UUID()`，07-30）的设计。10-11 公开版已改为 `ScrollChannel`，并在注释中把 UUID 戳称为"以前的做法"。 | 发布版用的是 Droppy 自己承认移植自 Tinycast"滚动意图"的那套设计 |
| B4 | Tinycast 的搜索框提示语 **"Search for apps and commands…"**（Tinycast 07-04 起使用）以代码使用的字符串常量形式出现在 16.0.0 / 16.0.1 主程序中，紧挨 `settings:thunderstorm`、"Filter this folder" 等字符串；在 09-26 droplet 版中，它正是 `searchPlaceholder` 的返回值。10-11 公开版的 `searchPlaceholder` 改为返回 "Search your Mac"（文件夹浏览时为 "Filter this folder…"）。但 16.0.x 的本地化表里**同时**有 "Search your Mac"，二进制无法确定 16.0 实际显示的是哪一条。 | 与 Droppy 博客自认的"搜索框提示语漏进 16.0"相符，二进制提供了旁证 |
| B5 | 16.0.x 中 `ThunderstormQuicklink` 的 CodingKeys 为 `id, name, link, keyword, isFallback, openWithBundleID`。`openWithBundleID` 是 Tinycast `Quicklink` 使用的字段名（08-03/04），Raycast 的导出格式中没有这个键名；10-11 版改为 `preferredAppBundleID`，并把 `openWithBundleID` 列为"早期构建写过的"旧键。 | 用户用 16.0.x 保存的 quicklink 数据，使用的是与 Tinycast 相同的字段名 |
| B6 | 整个应用包附有 5 份第三方声明（ThunderstormEmojiAnnotations、LinearMouse、AI 助手图标、thock、OCR 参考），**没有任何一份提到 Tinycast**；全包没有 "Tinycast"（大写）或 "Abue" 字样。 | 发布版中没有对 Tinycast 的署名 |
| B7 | 只有两处小写的 `tinycast`：`app.getdroppy.droplet.tinycast` 和 `com.tinycast.extensions.oauth`（Tinycast 在 08-25 #325 引入的 OAuth 钥匙串服务名），都位于 `DropletCatalogBridge` 中处理"退役 droplet 继任和清理"的宿主代码旁边。 | 最合理的解释是清理已下架的 Tinycast droplet 留下的数据，**不作为抄袭证据** |
| B8 | 16.0.0 已内置 Thunderstorm 自己的 Raycast 扩展 Node 宿主脚本（618 行，其中 563 行与 10-11 版按顺序一致），没有 Tinycast 的 JavaScriptCore 运行时。 | 支持"扩展运行时架构独立"；也说明这部分代码在 16.0 中已经存在（09-27 博客称要到 16.0 之后才交付，可能是未对用户开放） |

**16.0.x 与 10-11 公开快照的关系**
- 10-11 源码中的 899 个 Thunderstorm 类型，只有 179 个出现在 16.0.0 中。这个数字是下界：没有存储属性的类型或被编译器优化掉的类型不会出现在反射元数据里（例如 16.0 显然有样式定义，但 `ThunderstormStyle` 查不到）。所以**单个类型的缺失不能作为证据**，下面只引用整个模块的类型全部缺失的情况。不在 16.0.x 里的包括：Quick Actions（18 个类型）、AI 聊天与 MCP、类型化计算器（`ThunderstormCalc*`）、Markdown 笔记窗口、会议与相机、Workspaces 与窗口布局、Paste One by One 等。这与 README"这是下一次更新的代码"一致：**10-11 快照中相当大一部分模块从未随稳定版发布**，是在 16.0.1（09-28）之后才进入发布构建或才写成的。
- 16.0.0 处于 09-26 droplet 版与 10-11 公开版之间：它已有 10-11 的 `ScrollDriver`、`SlimScroller`、`KeepsSelectionInView`，但仍保留 09-26 的 `ScrollRequest`，还没有 10-11 新增的 `ScrollChannel`、`HoverTracker`。说明启动器外壳在 16.0.1 之后**又改过一轮**，第 6 节中的逐字注释是在这轮修改后依然保留下来的。
- 10-11 版有两处迁移代码读取"早期构建"写下的数据：Quicklink 的 `iconSymbol` / `openWithBundleID` / `isEnabled`（Tinycast `Quicklink` 的三个字段名），以及 Workspaces 的 `auto, focus, stack, columns, grid, custom`（Tinycast `RoomLayoutKind` 的原始值）。但 16.0.x 中的 quicklink 只写了其中的 `openWithBundleID`，而且**根本没有 Workspaces**。所以这些"早期构建"至少部分是从未作为稳定版发布的内部、nightly 或 droplet 构建。结合 MR !72（09-27 曾把 Tinycast 的 quicklinks、Rooms 等非 AI 引擎移植进 Thunderstorm droplet）来看，**10-11 版的 quicklink 和 Workspaces 很可能由那条使用 Tinycast 数据模型的移植线演变而来**。这是推断，需要 Droppy 内部构建或私有历史才能证实。

**对 Droppy 说法的影响**：博客说"It was removed before any update went out, so no Droppy user ever got his code"（在任何更新发布前就已移除，所以没有 Droppy 用户拿到过他的代码），并把 Thunderstorm 使用 Tinycast 部分的事放在一个"从未发布的测试版"里。按 Droppy 自己 09-26 NOTICE 的署名标准（"these files are credited to Tinycast all the same"），这批启动器组件随 16.0.0 / 16.0.1 发给了用户，且没有附任何 Tinycast 署名。此外，Tinycast 的提示语和与 Tinycast 相同的 quicklink 字段名也在发布版中。二进制看不到注释和函数体，所以无法逐行判断 16.0 的实现与 Tinycast 的相似程度；但"没有 Droppy 用户拿到过他的代码"这一说法与上述事实不符。

### 3.8 合作前基线：Droppy 15.2.2-beta.1
为了不依赖 Droppy 自己的 NOTICE、独立判断这些组件的来源，本审计又检查了合作开始前最近的一个公开 beta 构建 15.2.2-beta.1（此后只有 09-12 的一个 nightly，16.0 之前发布接口一直以它为最新 beta）（48.0 MB，来源同上；build 15220001；签名时间 **2026-09-09 07:40 UTC**，早于 NOTICE 所记的 09-21 移植提交和 09-23 的 Tinycast droplet）。

| 项目 | 15.2.2-beta.1（09-09） | 16.0.0（09-27） | Tinycast 首见 |
|---|---|---|---|
| 带字段的 Thunderstorm 类型 / 不同的 Thunderstorm 标识符 | 114 / 90 | 266 / 230 | — |
| 悬停"上膛"机制（`ThunderstormPointerState`：`armingDistance`、`restingPoint`、`hoverArmed`；`ThunderstormArmedHover`） | **无**（旧版行视图 `ResultRowCompact` 只有普通的 `isHovered`；`ThunderstormPanel` 无任何字段） | 有 | 07-24 / 08-05 / 08-11 |
| `ThunderstormBarButton` / `ThunderstormBarButtonChrome {capsule, rounded}` | 无 | 有（字段顺序同 Tinycast） | 07-10 / 08-14；`isSelected`、`isCompact` 09-18 |
| `ThunderstormKeyCap` / `KeyCaps`（`Style {outline, filled}`） | 无 | 有 | 06-30 |
| `ThunderstormMenuCircleButton`、`ThunderstormHeaderBackButton` | 无 | 有 | 07-10、09-08/09 |
| `ThunderstormRightClickCatcher` 及内嵌 `CatcherView` | 无 | 有（嵌套类型名也是 `CatcherView`） | 06-29 |
| `ThunderstormScrollRequest`（UUID 戳）、`SlimScroller`、`KeepsSelectionInView` | 无 | 有 | 07-30（ScrollIntent）等 |
| `ThunderstormSectionHeader`、`ThunderstormEmptyResults`、`ThunderstormActionMenu` / `ThunderstormMenuItem`（`beginsGroup`） | 无 | 有 | 06-28 至 09-10 |
| 搜索框提示语 "Search for apps and commands…" | 无 | 有 | 07-04 |
| "Search your Mac" | **有**（Droppy 原有的本地化字符串） | 有（仍在本地化表中） | — |
| quicklink（`openWithBundleID`） | 无（没有 quicklink 功能） | 有 | 08-03/04 |
| 旧版启动器界面类型（`ThunderstormGlassSurface`、`ResultRowCompact`、`ResultActionBar`、`StatusRow`、`LeadingGlyph`） | 有 | **全部消失** | — |

**结论**
1. **抄袭方向可以独立证明，不再依赖 Droppy 的自述。** 这些 Tinycast 自造的组件名和结构，在 09-09 的 Droppy 发布版中都不存在；在 Tinycast 中它们早已出现（多数在 6–8 月，最晚的 09-18），并有完整的有机演化记录；在 09-27 的 16.0.0 中，它们与 Tinycast 的命名、嵌套结构、字段顺序一致地出现，同时 Droppy 原有的启动器界面类型被整体替换。Tinycast 的源码自 6 月起一直公开在 GitHub 上，反方向（Tinycast 从 Droppy 复制）在时间上不成立。这与 Droppy NOTICE 的说法吻合，但现在有了独立的二进制证据。
2. **搜索框提示语的来龙去脉得到证实。** "Search your Mac" 是 Droppy 合作前就有的字符串；Tinycast 的 "Search for apps and commands…" 在 16.0 中新出现；10-11 版又改回 "Search your Mac"。这与 Droppy 博客"漏进 16.0、已改回"的说法一致。
3. **功能出现的时间窗口**：quicklinks、snippets（含关键词展开）、Script Commands、Raycast 扩展（Droppy 自己的 Node 运行时，约 40 个类型）、资料库与备份、词典、菜单搜索、窗口切换、计算器历史、Apple Shortcuts 等，都是在 09-09 到 09-27 之间才首次出现在 Droppy 中。这份清单与 MR !72（09-27，把 Tinycast 的非 AI 功能移植进 droplet）和同日博客列出的功能几乎一致。不过，这些功能中有不少在代码层面是独立实现（见第 4、6 节），时间重合本身只说明"在接触 Tinycast 源码的同一时期加入"，不等于逐项复制。
4. **弱证据（仅作记录）**：16.0.0 的本地化表（已译成多种语言）中有几条 Tinycast emoji 界面文案作为键存在，例如 "Paste and Keep Window Open"、"Move Up in Pinned"、"Keys & Technical"、"Shapes & Punctuation"（Tinycast 08-10 至 09-15）。15.2.2 中没有；16.0 的程序代码也不引用它们，属于残留条目。它们说明这些文案在 09-09 到 09-27 之间进入过 Droppy 主应用的字符串目录，但来自内置 Thunderstorm 还是 Tinycast droplet 的宿主桥接代码，无法判断。Droppy 自己的 emoji 选择器在 15.2.2 中已经存在。

---

## 4. 代码架构对比

### 4.1 宏观统计
| 指标 | Thunderstorm | Tinycast（应用代码） |
|---|---|---|
| Swift 文件 | 256 | 798（另有 103 个测试文件） |
| 总行数 | 115,395 | 119,430（测试另计 38,599） |
| 每文件行数（中位 / 平均 / 最大） | 350 / 451 / 3,384 | 91 / 150 / 2,143 |
| 注释行占比 | 13.1% | 5.6%（有"单行注释"规范） |
| 类型数 / 函数数 | 1,291 / 4,187 | 1,922 / 5,144 |
| 目录组织 | 扁平：`Sources/` 根目录加 AI、Calculator、Extensions、Library、Meetings、Windows 六个子目录，所有类型带 `Thunderstorm` 前缀 | `Features/<名称>/{Model, Service, UI, Settings}`，另有 `Palette/`、`DesignSystem/`、`Platform/` |
| 分层约束 | 特性注册表（`ThunderstormBootstrap` 注册屏幕、条目分区、Tab 模式、参数解析器、行动作），宿主为 Droppy 的 `ExtensionDefinition` / DroppyKit | 四层：PURE（只依赖 Foundation）→ EFFECT → OBSERVABLE STATE → VIEW，由测试强制 `Model/` 不得 import AppKit/SwiftUI |
| 测试 | 无 | 103 个测试文件 |
| 可独立构建 | 否（依赖 Droppy 设计系统、宿主服务、DroppyKit） | 是 |

两者的总代码量接近，但组织方式明显不同：Thunderstorm 倾向于大文件、长注释、注册表式扩展；Tinycast 倾向于小文件、严格分层、测试驱动。

### 4.2 模块对应与派生程度（经复核后）
| 模块 | Thunderstorm 主要文件 | Tinycast 对应 | 复核后证据（强/中） | 派生判断 |
|---|---|---|---|---|
| 启动器面板视图与外框 | ThunderstormView、LauncherChrome、Style、Layout、ActionMenu、DropletLibraryRow 等 | Palette/RootPaletteView、DesignSystem/* | 9 / 2 | **高**：视图层改名加改写注释，设计令牌整表移植，底层机制重写 |
| 窗口控制器、滚动、悬停 | ThunderstormWindowController、Scrolling、PointerState 等 | PaletteWindowController、PalettePanel、ArmedHover、HoverArming | 8 / 0 | **高**：参照式改写，留有逐字注释与标识符 |
| 搜索、排序、应用索引 | SearchModel、SearchService、AppIndex、FuzzyMatch 等 | Launcher/* | 1 / 3 | 设计与文案层面中；代码层面低 |
| 系统命令与意图 | SystemCommands、SystemActions、Uninstaller、Deeplinks 等 | SystemActions、Uninstall、HotKeys | 0 / 2 | 中偏低 |
| 剪贴板、文件搜索、Emoji | Clipboard*、FileSearch*、PathIndex、EmojiSurface | Clipboard、FileSearch、Emoji | 2 / 1 | 中：借用设计与措辞，代码大体重写 |
| 计算器 | Calculator/* | Calculator（#483 类型化求值器） | 1 / 3 | 规格和文档层面高；代码独立（递归下降 vs Pratt） |
| AI 聊天与 Provider | AI/Chat、AI/Providers | AI/* | 0 / 0 | 低 |
| MCP 与 Quick Actions | AI/MCP、AI/QuickActions | MCP、QuickActions | 1 / 1 | 低到中（主要是一条提示词） |
| Raycast 扩展（Swift 侧） | Extensions/* | Extensions、raycast-runtime | 0 / 1 | 低到中（运行时架构独立） |
| Snippets、Quicklinks、命令 | Library/Snippet*、Quicklinks、Placeholders、ShellRunner 等 | Snippets、Quicklinks、CustomCommands | 1 / 4 | 中：按规格重写，留有兼容键 |
| 备份、Raycast 导入、资料库 | Library/LibraryBackup*、RaycastConfigImport 等 | Backup、Settings | 1 / 3 | 中 |
| 笔记、词典、菜单搜索、窗口切换 | Library/NotesWindow*、Dictionary、MenuSearch、WindowSwitcher | Notes、Dictionary、MenuSearch、WindowSwitcher | 0 / 0 | 低（代码），设计层面低到中 |
| 会议与相机、窗口管理与工作区 | Meetings/*、Windows/* | Calendar、Camera、WindowManagement（含 Rooms） | 2 / 2 | 谱系确定，代码重写 |
| **合计** | 13 个模块，143 条发现 | | **26 强 / 22 中**（另有 94 条弱、1 条被驳回） | |

### 4.3 架构层面的独立性证据
- **Raycast 扩展运行时**：Thunderstorm 为每个命令启动一个 Node 子进程，通过 stdin/stdout 交换 JSON 行；Tinycast 在进程内使用 JavaScriptCore 加 node shims。把 Thunderstorm 嵌在 Swift 字符串里的 1,632 行 JS 单独抽出比对，只有 react-reconciler 要求的 host config 样板和 `@raycast/utils` 图标 SVG 相同（两边都在复刻 Raycast 官方实现）。值得一提的是，MR !72 曾把 Tinycast 的 JavaScriptCore 运行时带入 droplet，但内置版没有采用。
- **启动器底层**：滚动驱动（AppKit 层 `constrainBoundsRect` vs SwiftUI `ScrollViewProxy`）、边缘溶解（`CAGradientLayer` vs SwiftUI 渐变遮罩）、细滚动条（`NSScroller` 子类 vs SwiftUI overlay）、按键路由（单一 NSEvent 本地监听 vs `onKeyPress` 加 `sendEvent`）、悬停追踪（弱引用表 + 动量尾段处理，Tinycast 没有）都不同。
- **数据与算法**：剪贴板存储（Droppy ClipboardManager vs SQLite+FTS）、模糊匹配与打分常量、使用频次模型、计算器解析（递归下降 vs Pratt）、词典（公开 API vs 私有 DCS + XHTML）、Raycast 导入读取器（启发式 walker，完全没有用到 Tinycast 已公开的格式知识）、备份引擎（单 JSON + id 重映射 vs AppleArchive）都不同。
- **相反的设计决定**：Eject All 包含网络卷（Tinycast 明确不弹出）；AX 报告空选区时不发 ⌘C（Tinycast 仍会发）；窗口切换器采用 Tinycast 文档明确否决的 `didActivateApplication` 方案；`json-stringify` 输出带引号（与 Raycast 一致，Tinycast 不加）。
- **Droppy 专属集成**：droplet 库、Shelf/Basket、DroppyKit、Window Snap、相机 droplet、MicrophoneMuteManager 等，Tinycast 全历史中都没有对应物。

---

## 5. 相似度量化分析

### 5.1 复现 Thunderstorm 自带的 `compare.py`
用其原样副本（`python3 -I`，对 Tinycast 全历史 6,350 个源文件 blob）运行：

| 指标 | Thunderstorm | 基线 A | 基线 B |
|---|---|---|---|
| 最长相同片段（行） | **5**（README 所报） | 5 | 4 |
| literal 指纹（保留名称） | **0.24%**（README 所报） | 0.29% | 0.12% |
| renamed 指纹（标识符归一） | **2.77%**（README 未报） | 1.77% | 1.27% |
| 共享行 / 千行 | 73.9 | 65.6 | 32.2 |
| ≥3 行片段数 | 42 | 34 | 16 |
| 单文件 renamed 最高 | 0.212（DropletLibraryRow） | 0.145 | 0.109 |

- README 的两个数字可以准确复现，没有造假。
- 去掉所有 `Thunderstorm` 前缀后重跑，结果不变（5 / 0.24% / 2.77%）。说明 literal 低分**不是**加前缀造成的，代码在 token 层面确实被重写过。
- renamed 指标在所有参数下都比基线高约 1.2–2.2 倍（K=25：3.38 / 2.03 / 1.45；K=15 且 DF≤5：14.8 / 11.3 / 10.4；K=12：39.1 / 31.8 / 28.9），属于温和偏高。
- 按 30 行滑动窗口统计（K=15），命中率 ≥40% 的窗口 Thunderstorm 占 3.27%（涉及 102 个文件），基线为 1.03% 和 1.12%，约为 3 倍。

### 5.2 `compare.py` 的盲区
| 盲区 | 位置 | 影响 |
|---|---|---|
| 比较前清空所有注释 | similarity.py `lex()` 内的 `blank()` | **大**：Thunderstorm 有 14,989 行纯注释（13%），而最强证据正好在注释里 |
| 所有字符串折叠为一个 token `S`，所有数字折叠为 `N` | `norm_tokens` | **大**：UI 文案、调校常量、数据表内容都看不到；1,632 行内嵌 JS 只算 7 个 token |
| 行级片段要求归一化后整行相等，标识符保持原样 | `norm_line` / `significant` | 任何改名、重新折行、数据表重排都会让片段断开；SwiftUI 的短修饰符行被过滤掉 |
| K=25、W=8 未经论证 | compare.py:43-44 | 一个 100% 派生的改写文件在 K=25 下得分为 0 |
| DF_MAX=5 按路径计数 | compare.py:113-130 | Tinycast 在多个界面复用的写法被当作样板丢弃（去掉了 Thunderstorm 18% 的命中，基线只有 12–13%） |
| 全树平均 | `measure()` | 局部借用被 11.5 万行稀释 |
| 没有时间维度 | `load_history` | 无法判断方向 |
| README 只报告 literal 一列 | README | 恰好是对任何改名或重写都接近 0 的那一列 |

### 5.3 AI 改写对照实验
方法审查员按"LLM 被要求用我们的风格重写"的方式，改写了 5 个 Tinycast 文件（660 行）：全部改名、调整成员顺序、改写控制流、拆分或合并函数、重写所有注释，保持行为不变。同时做了一组"只改名"的对照。

| 组别 | 最长片段 | literal（整体） | renamed（整体） | 近似注释 ≥0.5 |
|---|---|---|---|---|
| 深度改写（已知 100% 派生） | 9–10 行（来自数据表） | **1.09%** | 11.3% | 58 条中 1 条 |
| 只改名 | 20 行 | 4.8% | 95% | 56 条中 56 条 |
| Thunderstorm | 5 行 | 0.24% | 2.77% | 6,103 条中 34 条（13 条 ≥0.9） |
| 基线 | 4–5 行 | 0.12–0.29% | 1.3–1.8% | 0 |

两点结论需要同时说明：
1. **compare.py 识别不出深度改写。** 其中一个文件（DoubleTap）得分 0.000，在 798 个 Tinycast 文件中排第 400 名，与无关代码没有区别。所以 README 的低分与"独立编写"和"改写自 Tinycast"两种说法同样相容。
2. **保留文件拆分的中度改写，renamed 指纹能抓到**（中位 0.122，且能把真实来源文件排在第一）。Thunderstorm 按文件的分布（中位 0.022，最佳对应最高 0.077）与基线重合，所以**现有数据不支持"逐文件、保留结构的整体移植"**。仍无法排除的是：深度重构式改写、合并进大文件的片段级借用，以及设计层面的借用。而本审计的其他信号恰好都指向这几类情况。

### 5.4 本审计补充的、不受改名影响的信号
| 信号 | Thunderstorm | 基线 A | 基线 B |
|---|---|---|---|
| 近似注释/文案（得分 ≥0.5 / ≥0.7 / ≥0.9；样本 6,103 / 4,417 / 4,751 条） | **34 / 20 / 13** | 0 / 0 / 0 | 0 / 0 / 0 |
| 特有类型名（去前缀）与 Tinycast 重合 | **8.3%**（997 个中 83 个） | 3.2% | 0.7% |
| 字符串字面量重合（≥14 字符） | **10.8%** | 3.5% | 0.6% |
| 枚举 case 集合匹配（≥4 个共享 case，Jaccard ≥0.5） | **11 / 77** | 4 / 45 | 1 / 58 |
| 有序字面量片段（≥4 个连续） | **52 段，最长 10** | 2 段 | 1 段 |

说明：字符串和有序片段中有不少由外部规范决定（OAuth/PKCE 字段、MCP 与 Anthropic/OpenAI API、Raycast 颜色名、claude CLI 参数），复核时已逐条剔除，不计为证据。近似注释这一项受外部规范影响最小，与基线的差距也最大。

---

## 6. 关键证据（经独立复核确认）

以下按"可定年、可溯源"的程度排列。行号为 10-11 快照中的位置；"Tinycast 首见"为 `git log --all --reverse -S` 的结果。

### 6.1 逐字或近逐字的注释与文案
| # | Thunderstorm | 文本（节选） | Tinycast 首见 | 紧邻代码 |
|---|---|---|---|---|
| 1 | ThunderstormWindowController.swift:231 | "Open disarmed: a pointer already over a row must not highlight it." | 08-07（`946c5907` 由 07-24 的长版压缩而来） | 后接同名调用 `disarmHoverHighlight(pointerAt: NSEvent.mouseLocation)` |
| 2 | ThunderstormView.swift:540 | "Identical metrics in both states, so typing can't move the search bar." | 08-07（压缩版） | 三个修饰器顺序相同，仅改名 |
| 3 | ThunderstormView.swift:487 | "Matches the list rows and section headers' own indent below." | 08-11，第三方 zkmn73（#208） | header HStack 序列相同 |
| 4 | ThunderstormView.swift:489 | "Every sub-screen leaves the same way, so the slot reads the…"（重新折行） | 09-09（#504，同一提交引入 HeaderBackButton） | 同上 |
| 5 | ThunderstormView.swift:336 | "Never conditionally mounted: unmounting strands SwiftUI's hover target and eats clicks." | 08-23，第三方 notsoshu（#318，提交说明记录了该 bug 的发现过程） | `Color.black.opacity(0.001)` + `contentShape` + `DragGesture(minimumDistance: 0).onChanged` + `allowsHitTesting` 完全同构；`.onChanged` 是 09-18 #864 的修订版 |
| 6 | ThunderstormView.swift:2649；ThunderstormDropletsLibraryView.swift:122 | "Snap to the origin on the first row so its header shows too." | 08-07 | 修饰器链 padding → 隐藏系统滚动条 → 边缘溶解 → 细滚动条 → 此注释 → 选中跟随，顺序相同；第二处位于 Droppy 独有的 droplet 文件 |
| 7 | ThunderstormDropletLibraryRow.swift:61 | "Selection wins over hover when a row is both; otherwise hover shows its fainter layer." | **06-30**（建库第 3 天） | 下方 4 行 `fill` 计算同构；该文件是 compare.py 全仓 renamed 最高的文件（0.212） |
| 8 | ThunderstormView.swift:2376 | "…primary action and the Actions toggle sharing one glass capsule." | 07-11 | 同名函数 `actionGroup`、`HStack(spacing: 2)`、键帽、毛玻璃胶囊，顺序一致 |
| 9 | ThunderstormView.swift:975 | "…lands under the pointer, which chose no row of it, so it opens disarmed" | 08-29（`bf3be599`） | 后接同签名 `disarmHoverHighlight(pointerAt:)` |
| 10 | ThunderstormAppIndex.swift:635；SearchModel.swift:1248 | "The opening list stays alphabetical: a list that reorders as you use it is unscannable." | 09-04（只在 09-04 至 09-23 存在于 Tinycast） | 实现不同（借用表述） |
| 11 | ThunderstormFileSearchScreen.swift:10-12 | 文件头列出过滤器 "All, Folders, Documents, Images, Audio, Video, Archives, Code, and a Finder tag"：**前七项与 Tinycast `FileSearchFilter` 的七个 case 完全同序**（Tinycast 只有这七项，Code 和 Finder tag 是 Thunderstorm 追加的） | 09-12（`5d8dbb77`） | **与 Thunderstorm 自己的枚举顺序矛盾**（anyKind, documents, pdfs, images, videos, audio, code, archives, folders，且附有"folders last"的理由），属于未同步更新的残留 |
| 12 | ThunderstormView.swift:408-410 | 菜单动效注释自称是 "the reference launcher's menu panel motion"；常量 scale 0.94、`timingCurve(0.2,0.7,0.2,1)` 0.10、`timingCurve(0.4,0,1,1)` | 09-13 / 09-18（0.14 改为 0.10） | 五个常量全部一致 |
| 13 | ThunderstormSelectionCapture.swift:110 | "Select text in another app first." | 08-27 | 网上搜不到公共来源 |
| 14 | ThunderstormQuickActionStore.swift:134-136 | Fix Grammar 提示词：四要素骨架相同，"change only what is wrong"、"If nothing is wrong" 逐字 | 08-27（此后未改） | 其余三条提示词已按 Thunderstorm 自己的风格改写，只有这一条没改掉 |
| 15 | ThunderstormCalcParser.swift:5-16 | 文件头是 Tinycast 计算器文档 Arithmetic/Units 两节的压缩改写，示例相同（`10kg + 20%`、`5 3`、`5kg + 5`、`3x3`） | 07-29 至 09-13（措辞与 09-13 版文档吻合，与 08-19 版不符） | 解析算法不同（规格层面派生） |

### 6.2 数据、常量与设计令牌
- **配色透明度表**（ThunderstormStyle.swift:126-155）：11 组 (dark, light) 数值与 Tinycast `Theme.Colors.ramp` 逐对相同、顺序相同（selection 0.10/0.09、rowHover 0.05/0.045、separator 0.10/0.12、controlSurface 0.10/0.08、border 0.20/0.18、textTertiary 0.40/0.42、menuSymbol 0.70/0.70……）。浅色值是 Tinycast 在 08-19（#274）手工调出的。另外还带有 Tinycast 的 `.tint(.clear)` 怪癖和 frost 0.05/0.25，而 Tinycast 已在 09-23 删除这些，说明来源早于 09-23。
- **二十余项尺寸、字号、时长**及其推导公式与 Tinycast Theme / InterfaceMetrics 一致（276、36/52、28、22、菜单行高 = 图标 + 2×间距、紧凑高度 = 头部高度 + 2×头部内边距、菜单可见 5.5 行、宽 320 等），各项在 Tinycast 中有逐步演化的记录。
- **悬停"上膛"机制**：阈值都是 3pt（Tinycast `HoverArming.slop = 3`，08-11 的提交附探针测量）。同一对象里的兄弟成员都改了名（pointerDidMove、hoverArmed、restingPoint、armingDistance），唯独 `disarmHoverHighlight(pointerAt:)` 原样保留，符合"有意改名、一处漏网"的模式。
- **会议服务枚举**（ThunderstormMeetingLinks.swift:26-39）：Tinycast 的 10 个具名服务按原顺序出现（zoom、googleMeet、teams、webex、jitsi、whereby、chime、goTo、blueJeans、…），Thunderstorm 只在末尾追加（Tinycast 首见 08-22/23）。
- **音量 5% 网格吸附**：取整公式同形（±ε 后 floor+1 / ceil−1），示例同为 "37% → 40%"（Tinycast 08-02，由 1/16 步长演化而来，附测试）。
- **快捷键展开**：空闲 15 秒清空缓冲（Tinycast 07-30，第三方 PR）；Shell 运行器在 exit 127 时提示开启登录 shell，以及 8 KB 失败尾部 / 256 KB 输出上限 / 2 秒 SIGTERM→SIGKILL（Tinycast 07-29、08-29）。
- **文件搜索"最近文件"**：lastUsed 30 天 + 内容修改 3 天两条 Spotlight 查询合并；家目录展开为可见子文件夹（排除 Library），家目录根下文件单独处理（Tinycast 08-10、09-12）。

### 6.3 改名残留与数据模型遗留
- **Quicklink 旧字段名**（ThunderstormQuicklinks.swift:83-89）：`EarlierCodingKeys` 读取 "earlier builds" 写下的 `iconSymbol`、`openWithBundleID`、`isEnabled`，这正是 Tinycast `Quicklink` 的持久化字段名（08-04、08-30）；Raycast 导入器还把 `openwithbundleid` 列为候选键，而真实的 Raycast 导出里没有这个键。二进制核查显示，16.0.x 发布版实际写入的是其中的 `openWithBundleID`（见 3.7 B5）；`iconSymbol` / `isEnabled` 是哪个构建写下的，无法确定。
- **Workspaces 旧值迁移表**（ThunderstormWorkspaces.swift:88-97）：`auto, focus, stack, columns, grid, custom`，正是 Tinycast `RoomLayoutKind` 的原始值，顺序相同（09-25）。上游 MIT 项目 Rooms 用的是 `mine`，`custom` 是 Tinycast 自己的改名。
- **不完整的重命名**（ThunderstormActionMenu.swift）：存储属性叫 `beginsGroup`，构造器标签却仍是 Tinycast 的 `startsSection:`（约 109–117 处调用，Tinycast 09-10 #537）。
- **死 API**：`ThunderstormBarButtonChrome` 的 `.rounded`、`isCompact`、`isSelected` 在 Thunderstorm 中除声明外零调用，而这些参数在 Tinycast 中都有实际用途（`isSelected` / `isCompact` 是第三方 Ales M 在 09-18 #880 加入的）。照搬对方 API 而留下未用参数，是独立实现通常不会出现的痕迹。
- **自述的前身设计**（ThunderstormScrolling.swift:32-37）：注释说滚动请求"以前是带新 UUID 的值"，这正是 Tinycast `ScrollIntent(nonce: UUID())`（07-30）的设计。
- **十六进制颜色解析**（ThunderstormExtensionNode.swift:386-424）：`hasAlpha ? 24 : 16` 的三元移位写法与 Tinycast 08-14 版逐行同构，而 Tinycast 在 09-19 已删除该写法；审计者本地 1,668 个无关 Swift 文件中没有任何一处这种写法。

### 6.4 复核中被降级或驳回的典型项（说明本审计如何避免夸大）
- 剪贴板过滤器顺序、⌘. 置顶、⌘P 过滤、按住 ⌘ 显示数字：Raycast 官方手册就是这样规定的 → 降为弱。
- ⌘K 行操作菜单的多数条目（Move Favorite Up/Down、⇧⌘F、Reset Ranking、Hide from Root Search）：Raycast 规定 → 降为中。
- Raycast Icon → SF Symbol 映射大表：一致项大多被 SF Symbols 的可用性锁定，Tinycast 约 25 项最特异的映射 Thunderstorm 一个都没保留 → 降为弱。
- 占位符修饰符（uppercase / lowercase / trim / percent-encode / json-stringify / raw）、MCP/OAuth 字段、API 请求体、CLI 参数：外部规范 → 不计。
- "热键和数字键不参与排序学习"的例外集合：事实与分析员所述不符 → **驳回**。
- PhotoCapture 声明、RightClickCatcher、CalcDimension、WindowLayoutRunner 等同名类型：多为 Apple / Swift 惯用写法或领域自然命名 → 单独看为弱到中。

---

## 7. 具体指控逐项评估

| 指控（来自 Tinycast 作者） | 评估 |
|---|---|
| "拿走整个 Tinycast 代码库并喂给 AI" | **部分成立，整体未证实。** 9 月确有移植（Droppy 自认），10-11 版启动器外壳仍有可溯源残留，多个功能模块存在规格和设计层面的派生。但没有证据表明 11.5 万行整体是 Tinycast 的 AI 改写：大量模块架构不同、依赖 Droppy 宿主，按文件指纹分布与基线一致。"喂给 AI"一点，Droppy 公开承认用 AI 工具开发，MR 中也可见 Claude Code 标记与 `codex/` 分支名，但无法据此确定某段代码是否由 AI 改写 Tinycast 而来。 |
| logo 也是闪电 | **不成立。** Thunderstorm 的名称和图标早于 Tinycast（Wayback 05-12）；造型不同（双层尖角闪电 vs 圆角平面闪电）；闪电是启动器的通用意象。 |
| 作为付费产品出售 | 事实：Droppy 是付费软件，Thunderstorm 内置其中。Droppy 称付费针对整个应用。这一点本身不是技术问题，但与第 8 节的许可问题相关。 |
| 残留占位文本 | **成立，且范围比 Droppy 承认的大。** Droppy 承认搜索框提示语和 quicklink 示例漏进了 16.0（已改）；本审计在 10-11 "最后一轮清理"之后的源码中仍发现 13 条相似度 ≥0.9 的注释/文案残留（另有 21 条 0.5–0.9 的改写式近似），以及 "Look up a word…"、"Select text in another app first." 等界面文字。 |

| Droppy 的说法 | 评估 |
|---|---|
| Thunderstorm 早于 Tinycast | **名称、图标、基础搜索属实**（独立证据：05-12 快照）。但现行版本的绝大部分功能在 06-29 之前没有公开记录，"13.1 / 35 个文件"无法核实。 |
| 9 月借用时附了许可和署名 | droplet 版本（MR !66）属实；内置版是否附署名无法核实，10-11 公开版没有。 |
| 9 月底全部撤回、移除并重写（README） | **有歧义，部分成立。** droplet 确已下架；重写也确实发生了（三方比对证实 09-26 之后又重写了一遍）。但重写保留了可溯源的 Tinycast 注释、常量、API 与数据，且移除了署名，所以"建立在 Tinycast 代码上的部分已被移除"不成立。 |
| "A handful of example texts … slipped through into Droppy 16.0"；"They are texts, not code"（博客） | **不成立。** 残留包括源码注释、调校常量、配色表、API 形态、数据模型键名等代码层元素。 |
| 内置 Thunderstorm 不含 Tinycast 代码（MR !77，09-27） | **与 Droppy 自己前一天的 NOTICE 矛盾**：NOTICE 写明内置版的启动器文件在 09-21 移植自 Tinycast，09-26 重写时"度量和行为不变"并仍署名 Tinycast；10-11 版本中这些文件仍有 Tinycast 残留。 |
| 共享程度不高于 Tinycast 出现前写的代码（0.24%） | 数字可复现，但用错了指标：literal 列对任何改写都接近 0；同一次运行的 renamed 是 2.77%（基线的 1.6–2.2 倍）；"6 月 Droppy 基线"无法复现。 |
| "It was removed before any update went out, so no Droppy user ever got his code"；"Not a single Droppy user ever received his code"（博客） | **与二进制核查结果不符（见 3.7、3.8）。** 博客把 Thunderstorm 使用 Tinycast 部分的事归入"从未发布的测试版"，但这些组件在 15.2.2-beta.1 中不存在、在已发布的 16.0.0 / 16.0.1 中存在。 16.0.0 / 16.0.1 含有 Droppy 自己 NOTICE 署名给 Tinycast 的启动器组件（结构与 Tinycast 设计一致，如 `BarButton` 字段顺序、`ScrollRequest` 的 UUID 戳），还有 Tinycast 的搜索框提示语和 quicklink 字段名 `openWithBundleID`，且全包没有 Tinycast 署名。二进制看不到函数体，因此无法确定 16.0 的实现与 Tinycast 逐行相似到什么程度。 |

---

## 8. 许可与署名（事实陈述，法律定性需专业意见）
1. Tinycast 自 2026-07-10 起为 **AGPL-3.0-or-later**，版权人 Abue Ammar。
2. Droppy 在 MR !66 中曾以 AGPL 发布 Thunderstorm droplet，并以"Tinycast × Droppy 合作许可"为依据；MR !77 写明该许可"已不再提供"。
3. 10-11 公开的 Thunderstorm 以 **GPL-3.0 + Commons Clause** 发布，版权只署 Jordy Spruit，Sources 中没有任何 Tinycast 版权或许可声明。09-26 版本中同名文件的 Tinycast 版权头在 10-11 版本中被移除。
4. 如果第 6 节的残留被认定为 Tinycast 作品的受保护表达，那么有以下问题需要法律评估。判断时需注意不同证据的法律分量差别很大：源码注释和界面文案一般属于表达；思路、功能和事实数据通常不受保护；单个调校数值（如 3pt 阈值、15 秒超时）通常不受保护，而 11 组配色数值这类**整表的选择与排列**可能构成受保护的编排。
   - AGPL/GPL 要求保留版权声明和许可声明；
   - AGPL 衍生部分能否以 GPL-3.0 + Commons Clause 再许可（Commons Clause 属于 GPLv3 第 7 条所称的"进一步限制"）；
   - 内置于付费闭源宿主（Droppy）中分发的合规性。
5. Droppy 自己在 MR !77 的表述（droplet 链接 DroppyKit、在 Droppy 内运行，"均与 AGPL 不兼容"）说明它清楚 AGPL 代码不能进入 Droppy。因此，残留部分是否构成"Tinycast 代码"，正是双方争议的法律核心。

---

## 9. 综合结论
1. **派生关系：确定存在。** 证据有五重：Droppy 自己的书面记录（NOTICE、MR !72/!77、README 时间线）；独立可定年的文本残留（大多早于 9 月，部分出自 Tinycast 第三方贡献者，方向确定）；09-26 署名版与 10-11 无署名版的三方比对；已发布的 16.0.0 / 16.0.1 二进制中，Droppy 自己署名给 Tinycast 的启动器组件、Tinycast 的提示语和字段名都在，且没有任何 Tinycast 署名；合作前的 15.2.2-beta.1（09-09）中这些组件全都不存在，独立证明了方向。
1b. **发布版与未发布模块。** 可从二进制辨认的 Tinycast 派生部分（组件结构、字段名、提示语）随 16.0.x 发给了用户。10-11 快照中许多模块（AI、Quick Actions、计算器、笔记、会议、工作区、Paste One by One 等）不在任何稳定版里，其中可见的 Tinycast 痕迹（如 Fix Grammar 提示词、计算器文件头、Workspaces 旧值表、会议服务表）有两种可能来源：合作期内移植的代码一直保留到 10-11 才首次公开，或合作结束后参照 Tinycast 新写。现有材料无法区分这两种情况。唯一能确定发生在合作结束之后的是 Paste One by One：Tinycast 的 Paste Sequentially 首见于 09-29 07:26 UTC，而 09-28 21:40 UTC 发布的 16.0.1 中没有这一功能。
2. **派生类型**：以"参照式改写"为主。启动器外壳的视图层是改名加改写注释、设计令牌整表移植，底层机制重写；计算器、snippets / quicklinks、会议与工作区等是"以 Tinycast 的规格和文档为蓝本的重新实现"，留有措辞、常量和兼容键残留。没有发现大段逐字复制或"只改名"的整文件移植。
3. **规模**：强证据涉及 22 个文件，强或中等证据涉及 49 个文件（这些文件合计约 3.5 万行，但证据通常只是其中的局部段落），重心在启动器外壳。相对 11.5 万行整体，可确证的残留是局部的；设计和规格层面的借鉴覆盖面更广，但单项证明力较弱，且部分可以归因于双方共同效仿 Raycast。
4. **对双方公开说法的评价**：Droppy 的"They are texts, not code""Not a single Droppy user ever received his code"和"built-in Thunderstorm (no Tinycast code)"与事实不符，"已撤回、移除并重写"只有"重写"属实；Tinycast 方的"整个代码库被抄"超出了现有证据。较准确的描述是：Thunderstorm 在合作期间吸收了 Tinycast 的代码和设计，合作结束后的重写不彻底，现行公开版中仍有无署名的 Tinycast 派生内容，主要集中在启动器外壳。

---

## 10. 建议
**进一步取证（按价值排序）**
1. 获取 Droppy 私有历史中的 `66c274b99`、`0e1c336a7`、`6e9447d72`、`a4def4dc9` 及 9–10 月的 diff。这是回答"重写是否独立"的最直接证据。
2. 已完成 15.2.2-beta.1 / 16.0.0 / 16.0.1 的二进制核查（3.7、3.8）。还可以获取 16.0.2-nightly 或 insider 构建，确认 10-11 迁移代码所说的"早期构建"是否使用了 Tinycast 的 quicklink 和 Rooms 数据模型（需另行下载）。
3. 以 MR !72 的 diff 和 UPSTREAM.patch 为第三个参照点，与 10-11 公开版做三方比对，检查 Raycast 扩展、snippets、窗口布局等模块是否有从 droplet 版延续下来的结构。
4. 用 AST 级工具（swift-syntax 子树哈希、JPlag/Dolos）对第 6 节的热点文件做结构比对，并请不知道哪段来自哪方的人员做盲审。
5. 法律层面：请熟悉 AGPL/GPL 的律师评估残留的可版权性与许可合规问题。

**对 Droppy**：恢复对 Tinycast 的署名，或把第 6 节列出的残留（注释、配色与动效常量、`disarmHoverHighlight` / `startsSection` / `BarButtonChrome` 等 API、Quicklink 与 Workspaces 的兼容键、会议服务表、Fix Grammar 提示词、计算器文件头等）彻底按自有设计重写；更正 README 与博客中"全部撤回""只剩文本"的表述；在 `compare.py` 结果中同时报告 renamed 等指标，并说明它对改写不敏感。

**对 Tinycast**：如要主张权利，指控应落在第 6 节这些具体、可定年的残留上，而不是"整个代码库"。现有证据支持前者，不支持后者。

---

## 附录 A：可复现材料
本仓库结构：
- `EVIDENCE.md`：约 20 条最强证据的并排原文摘录（按锚点从两个仓库重新截取，行号精确），以及二进制核查结果。
- `scripts/`：本审计自写的分析脚本（`xanalyze.py`、`fuzzy.py`、`sens.py`、`binscan.py`、`fieldmd.py`、`anchor_excerpts.py` 及其输入 `evidence_spec.json`）。前三个需要把 Thunderstorm 仓库中的 `verify/similarity.py`、`verify/compare.py` 复制到脚本旁的 `ts_verify/` 子目录，用 `python3 -I` 运行；脚本只读取文件，不执行被审计代码。用法见 `scripts/README.md`。
- `data/`：compare.py 原始输出（全历史、去前缀、内嵌 JS、09-26 droplet 对比）、参数敏感性表、类型名 / 字符串 / 注释 / 枚举 / 有序片段比对结果、近似注释匹配结果；`data/binary/` 为三个 Droppy 版本中 Thunderstorm 相关类型的字段表、扫描结果和 DMG 校验和。
- 本仓库**不包含**：Droppy 安装包或从中提取的代码、09-26 droplet 源码副本（可从 GitLab MR !66 获取）、AI 代理的原始输出、基线项目的任何内容。

关键复现命令：
```bash
git clone https://gitlab.com/droppyformac1/thunderstorm.git
git clone https://github.com/abue-ammar/tinycast.git
python3 -I thunderstorm/verify/compare.py --ours thunderstorm/Sources --theirs tinycast --history
```

## 附录 B：主要公开来源
- Thunderstorm 源码：https://gitlab.com/droppyformac1/thunderstorm
- Droppy 博客：https://getdroppy.app/blog/thunderstorm-open-source ；https://getdroppy.app/blog/thunderstorm-raycast-extensions ；https://getdroppy.app/blog/droppy-16-0
- Droplet Store MR：https://gitlab.com/droppyformac1/droplets/-/merge_requests/22 、/64 、/66 、/72 、/77
- Internet Archive：https://web.archive.org/web/20260512140236/https://getdroppy.app/ ；https://web.archive.org/web/20260623155254/https://getdroppy.app/changelog.json ；https://web.archive.org/web/20260926153817/https://getdroppy.app/
- Droppy 发布接口：https://getdroppy.app/api/releases/latest ；https://getdroppy.app/changelog.json
- Tinycast：https://github.com/abue-ammar/tinycast ；https://github.com/abue-ammar/tinycast/releases
- 指控帖：https://x.com/abue_ammar/status/2109257990041981248
- Atoll DMCA（背景，与本案无关）：https://github.com/github/dmca/blob/master/2026/02/2026-02-10-atoll.md
- AlternativeTo 新闻：https://alternativeto.net/news/2026/9/droppy-16-transforms-into-extensible-platform-with-droppykit-and-raycast-extension-support/

---

*本报告以 [CC BY 4.0](LICENSE) 许可发布，脚本采用 MIT 许可。文中引用的 Tinycast 与 Thunderstorm 原文仍归各自版权人所有，受其原许可证约束（AGPL-3.0-or-later；GPL-3.0 + Commons Clause），仅用于评论与批评目的。详见 [README → License](README.md#license)。*
