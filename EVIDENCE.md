# Side-by-side evidence

Excerpts re-extracted directly from both repositories by anchor text, with exact line numbers and permalinks. Thunderstorm: snapshot `2ecde78` (2026-10-11). Tinycast: `126c998d` (2026-10-10) unless a historical commit is named. First-seen dates come from `git log --all --reverse -S`. See [REPORT.md](REPORT.md) §6 for context and the verification of each item.

## E1. "Open disarmed": verbatim comment followed by the same call

Identical comment in the panel's `show()`, immediately followed by a call with the same name and first argument label, `disarmHoverHighlight(pointerAt: NSEvent.mouseLocation)`. In Tinycast the wording was produced on 2026-08-07 (`946c5907`) by compacting a longer 07-24 comment; Thunderstorm has the compacted form.

*Tinycast first seen: 2026-08-07 (wording) / 2026-08-11 (`disarmHoverHighlight`)*

[Thunderstorm `Sources/ThunderstormWindowController.swift:230-236`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormWindowController.swift#L230-236)

```swift

        // Open disarmed: a pointer already over a row must not highlight it.
        ThunderstormPointerState.shared.disarmHoverHighlight(pointerAt: NSEvent.mouseLocation, reason: "show")
        // Arrive from nothing: transparent, the surface a touch small, and
        // drawn that way before the window is ordered in. The scale is the
        // container layer's (`ThunderstormArrivalContainerView`), so SwiftUI
        // lays nothing out under a scaled geometry.
```

[Tinycast `Tinycast/Palette/PaletteWindowController.swift:77-86`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Palette/PaletteWindowController.swift#L77-L86)

```swift
            if NSApp.modalWindow == nil { panel.level = .palette }
            // Open disarmed: a pointer already over a row must not highlight it.
            core.palette.disarmHoverHighlight(pointerAt: NSEvent.mouseLocation)
            // Re-resolve the anchor now, then hold it so resizes never move the window.
            anchor = nil
            // Size and place before ordering front, so a compact summon never flashes.
            positionPanel(panel, collapsed: core.paletteCoordinator.paletteIsCollapsed)
            // Flush first-mount layout off-screen, so the safe-area settle isn't visible.
            panel.contentView?.layoutSubtreeIfNeeded()
            core.inputSourceSwitcher.beginSession(
```

## E2. "Identical metrics in both states": verbatim comment over the same modifier sequence

Same comment, and the same three modifiers in the same order (fixed height, top padding, full width), renamed only.

*Tinycast first seen: 2026-08-07*

[Thunderstorm `Sources/ThunderstormView.swift:540-543`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormView.swift#L540-543)

```swift
        // Identical metrics in both states, so typing can't move the search bar.
        .frame(height: ThunderstormStyle.Metric.searchRowHeight)
        .padding(.top, ThunderstormStyle.Metric.searchRowInset)
        .frame(maxWidth: .infinity)
```

[Tinycast `Tinycast/Palette/RootPaletteView.swift:767-770`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Palette/RootPaletteView.swift#L767-L770)

```swift
        // Identical metrics in both states, so typing can't move the search bar.
        .frame(height: metrics.size.headerHeight)
        .padding(.top, metrics.size.headerPadding)
        .frame(maxWidth: .infinity)
```

## E3. Search-bar header: two comments in the same places, one by a Tinycast outside contributor

"Matches the list rows and section headers' own indent below." was written by outside contributor zkmn73 (PR #208, 2026-08-11); "Every sub-screen leaves the same way…" was added with `HeaderBackButton` in #504 (2026-09-09). Both appear in the same order in Thunderstorm's header, above the same gutter → back-button/icon slot structure.

*Tinycast first seen: 2026-08-11 and 2026-09-09*

[Thunderstorm `Sources/ThunderstormView.swift:486-495`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormView.swift#L486-495)

```swift
        HStack(alignment: .center, spacing: 0) {
            // Matches the list rows and section headers' own indent below.
            searchRowSideColumn(width: ThunderstormStyle.Gap.standard * 2)
            // Every sub-screen leaves the same way, so the slot reads the
            // same on all of them.
            if isSubScreen || palette.argumentBar != nil {
                ThunderstormHeaderBackButton(depth: screenDepth, action: headerBack)
                    .notchButtonTransition()
            } else {
                Image(systemName: "magnifyingglass")
```

[Tinycast `Tinycast/Palette/RootPaletteView.swift:677-684`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Palette/RootPaletteView.swift#L677-L684)

```swift
        HStack(alignment: .center, spacing: 0) {
            // Matches the list rows and section headers' own indent below.
            headerGutter(width: metrics.spacing.md * 2)
            // Every sub-screen leaves the same way, so the slot reads the same on all of them.
            if vm.mode != .launcher {
                HeaderBackButton(help: backHelp, action: goBack)
            } else {
                Image(systemName: vm.mode.systemImage)
```

## E4. "Never conditionally mounted": comment plus a structurally identical click-away catcher

Comment by outside contributor notsoshu (PR #318, 2026-08-23, whose commit message documents the bug). Thunderstorm merges it with the neighbouring inline comment ("the way a native menu's does") and carries the same four-modifier overlay, including `.onChanged`, which Tinycast adopted only on 2026-09-18 (#864). Tinycast's version shown is from that commit; Thunderstorm lacks the `.onRightClick` line Tinycast added on 09-12.

*Tinycast first seen: 2026-08-23; `.onChanged` 2026-09-18*

[Thunderstorm `Sources/ThunderstormView.swift:336-344`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormView.swift#L336-344)

```swift
        // Never conditionally mounted: unmounting strands SwiftUI's hover
        // target and eats clicks. Hit-tested only while a menu is up, when a
        // press anywhere else dismisses it, the way a native menu's does.
        .overlay {
            Color.black.opacity(0.001)
                .contentShape(Rectangle())
                .gesture(DragGesture(minimumDistance: 0).onChanged { _ in dismissMenus() })
                .allowsHitTesting(shownMenu != nil)
        }
```

[Tinycast `Tinycast/Palette/RootPaletteView.swift:293-300` @ `e25bd13b`](https://github.com/abue-ammar/tinycast/blob/e25bd13bc0c9297583b7ee3efa19c7975932b55b/Tinycast/Palette/RootPaletteView.swift#L293-L300)

```swift
                // Never conditionally mounted: unmounting strands SwiftUI's hover target and eats clicks.
                .overlay {
                    Color.black.opacity(0.001)
                        .contentShape(Rectangle())
                        // Not a tap: a drifting press must still dismiss, the way a native menu's does.
                        .gesture(DragGesture(minimumDistance: 0).onChanged { _ in closeMenus() })
                        .onRightClick { closeMenus() }
                        .allowsHitTesting(menuOpen)
```

## E5. "Snap to the origin": the same list modifier chain and verbatim comment

padding (horizontal / top / bottom) → hide system scrollers → edge dissolve → thin scrollbar → this comment → keep the selection in view with an inline first-row test. Thunderstorm has no "origin" concept of its own; the same comment also appears in Droppy's droplet-library view (`ThunderstormDropletsLibraryView.swift:122`).

*Tinycast first seen: 2026-08-07*

[Thunderstorm `Sources/ThunderstormView.swift:2643-2651`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormView.swift#L2643-2651)

```swift
                .padding(.top, ThunderstormStyle.Gap.tight)
                .padding(.bottom, ThunderstormStyle.Gap.standard)
                .thunderstormSuppressesSystemScrollers()
            }
            .thunderstormEdgeDissolve()
            .thunderstormSlimScrollbar()
            // Snap to the origin on the first row so its header shows too.
            .thunderstormKeepsSelectionInView(
                scroller,
```

[Tinycast `Tinycast/Features/Launcher/UI/LauncherList.swift:189-196`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Features/Launcher/UI/LauncherList.swift#L189-L196)

```swift
                        .padding(.bottom, metrics.spacing.md)
                        .hideNativeScrollers()
                        .scrollOriginAnchor()
                    }
                    .edgeDissolve()
                    .thinScrollbar()
                    // Snap to the origin on the first row so its header shows too.
                    .scrollFollowsSelection(
```

## E6. "Selection wins over hover": verbatim comment over the same fill logic, in a Droppy-only file

The comment dates from Tinycast's third day (2026-06-30). In Thunderstorm it sits in the droplet-library row, a Droppy-only concept, above the same three-way fill. `compare.py` itself ranks this file highest in all of Thunderstorm (renamed containment 0.212).

*Tinycast first seen: 2026-06-30*

[Thunderstorm `Sources/ThunderstormDropletLibraryRow.swift:61-66`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormDropletLibraryRow.swift#L61-66)

```swift
    /// Selection wins over hover when a row is both; otherwise hover shows its fainter layer.
    private var fill: Color {
        if isSelected { return ThunderstormStyle.Ink.selectedRow }
        if hovered { return ThunderstormStyle.Ink.hoveredRow }
        return .clear
    }
```

[Tinycast `Tinycast/Features/Launcher/UI/LauncherList.swift:245-250`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Features/Launcher/UI/LauncherList.swift#L245-L250)

```swift
    /// Selection wins over hover when a row is both; otherwise hover shows its fainter layer.
    private var fill: Color {
        if selected { return Theme.Colors.selection }
        if hovered { return Theme.Colors.rowHover }
        return .clear
    }
```

## E7. Footer "actionGroup" sharing one glass capsule

Same function name, near-identical doc comment, `HStack(spacing: 2)`, primary-action button with a ↵ key cap, then an "Actions" button with ⌘ K, padded and clipped into one glass capsule.

*Tinycast first seen: 2026-07-11*

[Thunderstorm `Sources/ThunderstormView.swift:2376-2390`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormView.swift#L2376-2390)

```swift
    /// The primary action and the Actions toggle sharing one glass capsule.
    private func actionGroup(primaryTitle: String) -> some View {
        HStack(spacing: 2) {
            ThunderstormBarButton(action: { actions.runPrimary() }) {
                HStack(spacing: ThunderstormStyle.Gap.snug) {
                    Text(verbatim: primaryTitle)
                        .font(ThunderstormStyle.Fonts.footer)
                        .foregroundStyle(.primary)
                        .lineLimit(1)
                    if let primaryKeyCaps {
                        ThunderstormKeyCaps(caps: primaryKeyCaps)
                    } else {
                        ThunderstormKeyCap(text: "↵")
                    }
                }
```

[Tinycast `Tinycast/Palette/RootPaletteView.swift:945-959`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Palette/RootPaletteView.swift#L945-L959)

```swift
    /// The footer control group: primary action and the Actions toggle sharing one glass capsule.
    private func actionGroup(
        pillLabel: String, formPrimaryShortcut: Bool, primaryActionEnabled: Bool, showActions: Bool
    ) -> some View {
        HStack(spacing: 2) {
            BarButton(action: activateSelection) {
                HStack(spacing: metrics.spacing.sm) {
                    Text(pillLabel)
                        .font(metrics.typography.bar)
                        .foregroundStyle(pillTint)
                    if formPrimaryShortcut {
                        HStack(spacing: metrics.spacing.xxs) {
                            KeyCapChip(text: "⌘", style: .outline)
                            KeyCapChip(text: "↵", style: .outline)
                        }
```

## E8. Colour-opacity table: 11 (dark, light) pairs identical and in the same order

Every Thunderstorm pair appears in Tinycast's `Theme.Colors` in the same relative order (Tinycast interleaves extra entries such as emoji and control-hover colours). The light-mode values were hand-tuned in Tinycast on 2026-08-19 (#274).

*Tinycast first seen: 2026-08-19 (light values), 2026-09-13 (menuSymbol 0.70)*

[Thunderstorm `Sources/ThunderstormStyle.swift:127-137`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormStyle.swift#L127-137)

```swift
        static let selectedRow = ink(dark: 0.10, light: 0.09)
        static let hoveredRow = ink(dark: 0.05, light: 0.045)
        static let hoveredMenuItem = ink(dark: 0.10, light: 0.09)
        static let divider = ink(dark: 0.10, light: 0.12)
        static let controlFill = ink(dark: 0.10, light: 0.08)
        static let outline = ink(dark: 0.20, light: 0.18)
        static let primary = ink(dark: 1.0, light: 1.0)
        static let secondary = ink(dark: 0.60, light: 0.60)
        static let tertiary = ink(dark: 0.40, light: 0.42)
        static let menuGlyph = ink(dark: 0.70, light: 0.70)
        static let iconBackdrop = ink(dark: 0.06, light: 0.06)
```

[Tinycast `Tinycast/DesignSystem/Theme.swift:450-476`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/DesignSystem/Theme.swift#L450-L476)

```swift
        static let selection = ramp(dark: 0.10, light: 0.09)
        /// Mouse hover: a fainter layer, visually distinct from selection.
        static let rowHover = ramp(dark: 0.05, light: 0.045)
        /// Emoji grid chrome: a quiet tile at rest, with two legible rings on interaction.
        static let emojiCell = ramp(dark: 0.045, light: 0.04)
        static let emojiHoverBorder = ramp(dark: 0.42, light: 0.34)
        static let emojiSelectionBorder = ramp(dark: 0.92, light: 0.72)
        static let emojiInnerBorder = adaptive(
            dark: .srgbInk(0, alpha: 0.72), light: .srgbInk(1, alpha: 0.72))
        static let menuHover = ramp(dark: 0.10, light: 0.09)
        static let separator = ramp(dark: 0.10, light: 0.12)
        /// Small control surfaces: kbd chips, glyph tiles.
        static let controlSurface = ramp(dark: 0.10, light: 0.08)
        /// A pointer over a control should lift it above its resting surface.
        static let controlHover = ramp(dark: 0.16, light: 0.14)
        /// A held control is stronger than hover, so mouse-down always reads.
        static let controlPressed = ramp(dark: 0.24, light: 0.20)
        /// Control borders: outlined kbd chips.
        static let border = ramp(dark: 0.20, light: 0.18)
        /// Alpha 1, so a call site can dim it with `.opacity` and land on the value it replaced.
        static let textPrimary = ramp(dark: 1.0, light: 1.0)
        static let textSecondary = ramp(dark: 0.60, light: 0.60)
        static let textTertiary = ramp(dark: 0.40, light: 0.42)
        static let menuSymbol = ramp(dark: 0.70, light: 0.70)
        static let noteText = ramp(dark: 0.90, light: 0.85)
        static let iconPlaceholder = ramp(dark: 0.06, light: 0.06)
        /// The faint wash behind the Onboarding header.
```

## E9. Menu animation: "the reference launcher's menu panel motion"

Thunderstorm's own comment names a "reference launcher". Scale 0.94, expansion `timingCurve(0.2, 0.7, 0.2, 1)` at 0.10 s and exit `timingCurve(0.4, 0, 1, 1)` (0.18 s in `ThunderstormStyle.Motion`) are Tinycast's `MenuMotion` constants; 0.10 s is the value Tinycast moved to on 2026-09-18 (from 0.14).

*Tinycast first seen: 2026-09-13; 0.10 s on 2026-09-18*

[Thunderstorm `Sources/ThunderstormView.swift:408-421`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormView.swift#L408-421)

```swift
    /// A menu grows out of the corner it hangs off and fades in with it,
    /// then shrinks back into that corner on the way out: the reference
    /// launcher's menu panel motion, one curve each way.
    private func menuTransition(anchor: UnitPoint) -> AnyTransition {
        guard !reduceMotion else { return .opacity }
        return .opacity.combined(with: .scale(scale: 0.94, anchor: anchor))
    }

    private var menuMotion: Animation? {
        if reduceMotion { return nil }
        return shownMenu == nil
            ? .timingCurve(0.4, 0, 1, 1, duration: ThunderstormStyle.Motion.menuOut)
            : .timingCurve(0.2, 0.7, 0.2, 1, duration: ThunderstormStyle.Motion.menuIn)
    }
```

[Tinycast `Tinycast/DesignSystem/Theme.swift:363-372`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/DesignSystem/Theme.swift#L363-L372)

```swift
        static let entryScale: CGFloat = 0.94
        static let maximumScale: CGFloat = 1.003
        static let exitScaleDelta: CGFloat = 0.04
        static let expansionDuration: TimeInterval = 0.10
        static let settleDuration: TimeInterval = 0.05
        static let exitDuration: TimeInterval = 0.18
        static let expansionTiming = CAMediaTimingFunction(controlPoints: 0.2, 0.7, 0.2, 1)
        static let settleTiming = CAMediaTimingFunction(controlPoints: 0.42, 0, 0.58, 1)
        static let exitTiming = CAMediaTimingFunction(controlPoints: 0.4, 0, 1, 1)
        /// Starts promptly and eases gently into the chevron's final direction.
```

## E10. `BarButtonChrome` / `BarButton`: same API shape, including parameters Thunderstorm never uses

Two-case enum (`capsule`, `rounded`) returning an `AnyShape`, and a button with `chrome = .capsule`, `isSelected = false`, `isCompact = false`, `action`, `label`, `@State hovered` in the same order. `isSelected` / `isCompact` were added in Tinycast by outside contributor Ales M on 2026-09-18 (#880); in Thunderstorm `.rounded`, `isSelected` and `isCompact` are never used outside the declaration.

*Tinycast first seen: 2026-07-10 (BarButton), 2026-08-14 (BarButtonChrome), 2026-09-18 (isSelected/isCompact)*

[Thunderstorm `Sources/ThunderstormLauncherChrome.swift:64-97`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormLauncherChrome.swift#L64-97)

```swift
enum ThunderstormBarButtonChrome {
    case capsule
    case rounded

    var shape: AnyShape {
        switch self {
        case .capsule:
            return AnyShape(Capsule(style: .continuous))
        case .rounded:
            return AnyShape(RoundedRectangle(cornerRadius: ThunderstormStyle.Corner.footerButton, style: .continuous))
        }
    }
}

/// A plain button inside a footer glass group: it shows a faint fill under
/// the pointer, a firmer one when selected.
struct ThunderstormBarButton<Label: View>: View {
    var chrome: ThunderstormBarButtonChrome = .capsule
    var isSelected = false
    var isCompact = false
    let action: () -> Void
    @ViewBuilder let label: () -> Label

    @State private var hovered = false

    init(
        chrome: ThunderstormBarButtonChrome = .capsule,
        isSelected: Bool = false,
        isCompact: Bool = false,
        action: @escaping () -> Void,
        @ViewBuilder label: @escaping () -> Label
    ) {
        self.chrome = chrome
        self.isSelected = isSelected
```

[Tinycast `Tinycast/DesignSystem/BarButton.swift:22-52`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/DesignSystem/BarButton.swift#L22-L52)

```swift
enum BarButtonChrome {
    case capsule
    case rounded

    func shape(_ metrics: InterfaceMetrics) -> AnyShape {
        switch self {
        case .capsule:
            return AnyShape(Capsule())
        case .rounded:
            return AnyShape(
                RoundedRectangle(cornerRadius: metrics.radius.barControl, style: .continuous))
        }
    }
}

/// A palette bar control, bare until hover; hover lives here so its owner never re-renders.
struct BarButton<Label: View>: View {
    var chrome: BarButtonChrome = .capsule
    var isSelected = false
    /// `sm` padding, so a 16-point glyph frame makes a square as tall as the bar.
    var isCompact = false
    let action: () -> Void
    @ViewBuilder let label: Label
    @State private var hovered = false
    @Environment(\.metrics) private var metrics

    var body: some View {
        let shape = chrome.shape(metrics)
        return Button(action: action) {
            label
                .padding(.horizontal, isCompact ? metrics.spacing.sm : metrics.spacing.md)
```

## E11. Hover arming: same 3 pt threshold and the one identifier that was not renamed

Both arm row hover only after the pointer moves more than 3 pt from a resting point, and disarm on keys or scrolling. Thunderstorm renamed every sibling member (armingDistance, restingPoint, hoverArmed, …) but kept `disarmHoverHighlight(pointerAt:)`.

*Tinycast first seen: 2026-08-11 (`slop = 3`, `disarmHoverHighlight`)*

[Thunderstorm `Sources/ThunderstormPointerState.swift:45-73`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormPointerState.swift#L45-73)

```swift
    /// How far the pointer must travel from where it rested before hover
    /// switches on, so a nudge of the desk does not count as a choice.
    private let armingDistance: CGFloat = 3
    private var restingPoint: CGPoint?

    private init() {}

    func pointerDidMove(to location: CGPoint) {
        guard !hoverArmed else { return }
        guard let restingPoint else {
            restingPoint = location
            return
        }
        let dx = location.x - restingPoint.x
        let dy = location.y - restingPoint.y
        guard dx * dx + dy * dy >= armingDistance * armingDistance else { return }
        hoverArmed = true
        log("armed")
    }

    /// Switches hover off until the pointer travels again from `location`.
    /// Without `reanchors`, the previous resting point stays the reference.
    func disarmHoverHighlight(pointerAt location: CGPoint, reason: String = "", reanchors: Bool = true) {
        if reanchors || restingPoint == nil {
            restingPoint = location
        }
        guard hoverArmed else { return }
        hoverArmed = false
        log("disarmed \(reason)")
```

[Tinycast `Tinycast/Palette/HoverArming.swift:1-12`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Palette/HoverArming.swift#L1-L12)

```swift
import CoreGraphics

/// When pointer movement is choosing a row rather than drift; arming lives on `PaletteState`.
enum HoverArming {
    /// A wheel click nudges the mouse a point or two, and a gesture ends with no displacement.
    private static let slop: CGFloat = 3

    static func isDeliberate(_ pointer: CGPoint, from anchor: CGPoint) -> Bool {
        hypot(pointer.x - anchor.x, pointer.y - anchor.y) > slop
    }
}
```

[Tinycast `Tinycast/Palette/PaletteState.swift:238-248`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Palette/PaletteState.swift#L238-L248)

```swift

    /// Movement is measured from where the pointer stands now: drift is not a new choice.
    func disarmHoverHighlight(pointerAt location: CGPoint) {
        hoverAnchor = location
        dropHoverHighlight()
    }

    private func dropHoverHighlight() {
        guard hoverHighlightArmed else { return }
        hoverHighlightArmed = false
        hoverDisarmToken = UUID()
```

## E12. File-search header lists Tinycast's filter order, contradicting Thunderstorm's own enum

The header lists "All, Folders, Documents, Images, Audio, Video, Archives", exactly the seven cases of Tinycast's `FileSearchFilter`, followed by Thunderstorm's additions. Thunderstorm's actual enum is ordered differently (anyKind, documents, pdfs, images, videos, audio, code, archives, folders) with a "folders last" rationale.

*Tinycast first seen: 2026-09-12*

[Thunderstorm `Sources/ThunderstormFileSearchScreen.swift:11-13`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormFileSearchScreen.swift#L11-13)

```swift
//  Quick Look, ⌘K every action (`ThunderstormFileActions`), ⌘P the filter:
//  All, Folders, Documents, Images, Audio, Video, Archives, Code, and a
//  Finder tag. With the filter up, ↑ ↓ ← → move through it, ↵ or a digit
```

[Thunderstorm `Sources/ThunderstormFileSearch.swift:37-48`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormFileSearch.swift#L37-48)

```swift
/// only for files the Mac has no type for.
enum ThunderstormFileTypeFilter: String, CaseIterable, Identifiable, Sendable {
    case anyKind
    case documents
    case pdfs
    case images
    case videos
    case audio
    case code
    case archives
    case folders
```

[Tinycast `Tinycast/Features/FileSearch/Model/FileSearchFilter.swift:4-13`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Features/FileSearch/Model/FileSearchFilter.swift#L4-L13)

```swift
/// The Search Files header filter. See docs/features/file-search.md#type-filter.
enum FileSearchFilter: CaseIterable, Sendable {
    case all
    case folders
    case documents
    case images
    case audio
    case video
    case archives
```

## E13. "A list that reorders as you use it is unscannable"

The sentence existed in Tinycast only between 2026-09-04 and 09-23. Thunderstorm keeps it, with a different implementation underneath (borrowed rationale).

*Tinycast first seen: 2026-09-04*

[Thunderstorm `Sources/ThunderstormAppIndex.swift:635-637`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormAppIndex.swift#L635-637)

```swift
    /// The whole install set, sorted by title. The opening list stays
    /// alphabetical: a list that reorders as you use it is unscannable.
    func allApplications() async -> [ThunderstormIndexedItem] {
```

[Tinycast `Tinycast/Features/Launcher/Service/AppIndex.swift:477-479` @ `cb46dba0`](https://github.com/abue-ammar/tinycast/blob/cb46dba0dfbbb75f52a0b9450c8e1295a260e733/Tinycast/Features/Launcher/Service/AppIndex.swift#L477-L479)

```swift
        let q = query.trimmingCharacters(in: .whitespaces)
        // The opening list stays alphabetical: a list that reorders as you use it is unscannable.
        guard !q.isEmpty else { return apps }
```

## E14. Fix Grammar prompt: same skeleton and verbatim clauses

Same four parts (correct spelling, grammar and punctuation; preserve wording/tone/formatting and line breaks; "change only what is wrong"; "If nothing is wrong" → return the text unchanged). Thunderstorm's other three prompts were rewritten in its own style; this one was not.

*Tinycast first seen: 2026-08-27*

[Thunderstorm `Sources/AI/QuickActions/ThunderstormQuickActionStore.swift:132-138`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/AI/QuickActions/ThunderstormQuickActionStore.swift#L132-138)

```swift
        switch self {
        case .fixGrammar:
            return "Correct the spelling, grammar and punctuation of the text. Keep its language, meaning, wording, "
                + "tone and formatting, including line breaks, lists and Markdown, and change only what is wrong. "
                + "If nothing is wrong, reply with the text exactly as it is."
        case .rewrite:
            return "Rewrite the text so it reads clearly and naturally. Keep its language and meaning, keep it about "
```

[Tinycast `Tinycast/Features/QuickActions/Model/QuickActionPrompt.swift:18-23`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Features/QuickActions/Model/QuickActionPrompt.swift#L18-L23)

```swift

                Correct spelling, grammar and punctuation in the text. Preserve the writer's \
                wording, voice, formatting and line breaks — change only what is wrong. If nothing \
                is wrong, return the text unchanged.
                """
        case .rewrite:
```

## E15. Quicklink: "earlier builds" wrote Tinycast's field names

Thunderstorm reads `iconSymbol`, `openWithBundleID` and `isEnabled` as legacy keys, which are the persisted field names of Tinycast's `Quicklink`. The released Droppy 16.0.x stores `openWithBundleID` as a live key (see the binary section below).

*Tinycast first seen: 2026-08-04 / 2026-08-30*

[Thunderstorm `Sources/Library/ThunderstormQuicklinks.swift:83-90`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/Library/ThunderstormQuicklinks.swift#L83-90)

```swift
    /// The names earlier builds wrote three of the fields under, in a
    /// library or a backup. Read when the current name is absent, never
    /// written.
    private enum EarlierCodingKeys: String, CodingKey {
        case symbol = "iconSymbol"
        case app = "openWithBundleID"
        case active = "isEnabled"
    }
```

[Tinycast `Tinycast/Features/Quicklinks/Model/Quicklink.swift:9-23`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Features/Quicklinks/Model/Quicklink.swift#L9-L23)

```swift
    let id: UUID
    var name: String
    /// The raw destination template; may still contain `{argument}`-style placeholders.
    var link: String
    /// Bundle id of the app to open with, or nil for the system default handler.
    var openWithBundleID: String?
    /// SF Symbol override; nil takes the glyph the detected destination suggests.
    var iconSymbol: String?
    /// Off keeps the row and everything attached to it, but nothing may offer or open it.
    var isEnabled: Bool
    var showsInRootSearch: Bool
    /// A stamp rather than a flag, so the pinned block is ordered by *when* you pinned.
    var pinnedAt: Date?
    var createdAt: Date
```

## E16. Workspaces: legacy values are Tinycast's `RoomLayoutKind`

`auto, focus, stack, columns, grid, custom` in order, the raw values of Tinycast's room layouts (adapted from the MIT project Rooms, which uses `mine` where Tinycast uses `custom`). Droppy 16.0.x has no Workspaces feature at all, so these values were written by unreleased builds.

*Tinycast first seen: 2026-09-25*

[Thunderstorm `Sources/Windows/ThunderstormWorkspaces.swift:88-98`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/Windows/ThunderstormWorkspaces.swift#L88-98)

```swift
        /// The values earlier builds wrote in `workspaces.json` and in
        /// backups, read so a saved choice survives.
        private static let earlierValues: [String: Arrangement] = [
            "auto": .bestFit,
            "focus": .mainAndSide,
            "stack": .cascade,
            "columns": .sideBySide,
            "grid": .tiles,
            "custom": .asLeft,
        ]
```

[Tinycast `Tinycast/Features/WindowManagement/Model/RoomLayoutKind.swift:5-13`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Features/WindowManagement/Model/RoomLayoutKind.swift#L5-L13)

```swift
enum RoomLayoutKind: String, Codable, CaseIterable, Sendable {
    /// Focus, Columns or Grid, whichever gives every window a comfortable size; Stack otherwise.
    case auto
    case focus
    case stack
    case columns
    case grid
    case custom
    /// Exactly where the windows were when the arrangement was remembered.
```

## E17. Meeting services: Tinycast's ten named providers in the same order

Thunderstorm lists the same ten services in the same order (`goTo` for `gotoMeeting`) and appends its own at the end.

*Tinycast first seen: 2026-08-22/23*

[Thunderstorm `Sources/Meetings/ThunderstormMeetingLinks.swift:26-40`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/Meetings/ThunderstormMeetingLinks.swift#L26-40)

```swift
enum ThunderstormMeetingService: String, Sendable {
    case zoom
    case googleMeet
    case teams
    case webex
    case jitsi
    case whereby
    case chime
    case goTo
    case blueJeans
    case skype
    case faceTime
    case slack
    case other
```

[Tinycast `Tinycast/Features/Calendar/Model/MeetingLink.swift:88-100`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/Features/Calendar/Model/MeetingLink.swift#L88-L100)

```swift
    enum Provider: String, CaseIterable, Sendable {
        case zoom
        case googleMeet
        case teams
        case webex
        case jitsi
        case whereby
        case chime
        case gotoMeeting
        case blueJeans
        case skype
        /// Any other http(s) link the event carries — joinable, just not identifiable.
        case generic
```

## E18. Calculator parser header paraphrases Tinycast's calculator documentation

Same rules and examples, in the same order: implicit multiplication (`3x3`), `5 3` is a search, relative percentages (`10kg + 20%` is 12 kg), compound amounts in the first unit, a bare number taking its neighbour's unit (`5kg + 5`). The wording matches the 2026-09-13 version of Tinycast's docs. The parser itself is a different algorithm (spec-level derivation).

*Tinycast first seen: 2026-07-29 to 2026-09-13*

[Thunderstorm `Sources/Calculator/ThunderstormCalcParser.swift:5-16`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/Calculator/ThunderstormCalcParser.swift#L5-16)

```swift
//  The calculator's grammar and arithmetic, on values that carry a unit, a
//  currency or a percent:
//
//  - implicit multiplication ("4(2+3)", "2pi", "3x3"), but never between
//    two bare numbers ("5 3" is a search);
//  - `mod` for modulo, while % stays a percent: relative with + and −
//    ("10kg + 20%" is 12 kg), absolute with × and ÷;
//  - compound amounts ("5 ft 3 in", "1h 30min") in their first unit, a
//    bare number taking its neighbour's unit ("5kg + 5"), and the last unit
//    named setting the answer's unit ("1 m + 20 cm" is 120 cm);
//  - temperatures add only within one scale;
//  - functions, constants, comparisons and bitwise operators.
```

[Tinycast `website/content/docs/features/calculator.md:45-59` @ `c8767a50`](https://github.com/abue-ammar/tinycast/blob/c8767a50dd2aefc8860d3160962219386dc78e29/website/content/docs/features/calculator.md#L45-L59)

```markdown
| `10kg to lb + 3lb`  | converts, then adds                          |

**Units side by side are one amount, not a sum.** `5 feet 3 inches` is `5.25 ft` and `1hr 30min` is
`1.5 hr`, answered in the _first_ unit. They bind together first, so `5w * 3h 30min` means
`5w * (3h 30min)`, and `90km / 1h 30min` gives `60 km/h`.

A bare number takes the unit next to it: `5kg+5` is `10 kg`, and `$10 + 5` is `15.00 USD`.

Percentages are relative for `+` and `-` (`10kg + 20%` is `12 kg`) and a plain share for `*` and `/`
(`10kg * 3%` is `0.3 kg`, `10kg / 25%` is `40 kg`).

A unit on its own converts to something useful: `1m` gives feet and inches, `1hr` gives 60 min.

Measurements combine into area, volume, speed and more:
```

## E19. Incomplete rename: `beginsGroup` stored, `startsSection` still the parameter label

Thunderstorm's menu item stores `beginsGroup` but its initializer keeps Tinycast's `startsSection:` label (used at ~109 call sites).

*Tinycast first seen: 2026-09-10 (#537, outside contributor)*

[Thunderstorm `Sources/ThunderstormActionMenu.swift:16-42`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/ThunderstormActionMenu.swift#L16-42)

```swift
    let id: String
    let title: String
    let symbolName: String
    /// Draws a divider above this item.
    let beginsGroup: Bool
    /// The action's keyboard shortcut. The menu shows it on the right, and
    /// the launcher runs the action with it straight from the list while the
    /// row is highlighted (`ThunderstormView.runActionChord`). A row that
    /// declares none takes its id's standard one
    /// (`ThunderstormActionShortcuts`), if there is one.
    let chord: ThunderstormKeyChord?
    /// Key caps shown at the trailing edge, e.g. ["⌘", "↵"].
    let shortcut: [String]?
    let isDestructive: Bool
    let isEnabled: Bool
    let action: @MainActor () -> Void

    /// `shortcut` takes key caps (["⇧", "⌘", "F"]) and `chord` a chord;
    /// either one both shows the shortcut and makes it work.
    init(
        id: String,
        title: String,
        symbolName: String,
        startsSection: Bool = false,
        shortcut: [String]? = nil,
        chord: ThunderstormKeyChord? = nil,
        isDestructive: Bool = false,
```

[Tinycast `Tinycast/DesignSystem/PopoverMenu.swift:21-31`](https://github.com/abue-ammar/tinycast/blob/126c998d87cd7e93bd5e3437098d9c646eb6a714/Tinycast/DesignSystem/PopoverMenu.swift#L21-L31)

```swift
struct PopoverMenuItem {
    let title: String
    let icon: PopoverMenuIcon
    let isLoading: Bool
    let isEnabled: Bool
    var sectionTitle: String?
    var startsSection: Bool
    var shortcut: String?
    /// A value the row states rather than a chord it runs — what a "Copy as" row copies.
    var detail: String?
    /// Destructive rows (delete) tint their icon + label red, matching the native menu convention.
```

## E20. Hex colour parsing: line-for-line equivalent to a form Tinycast later deleted

The `hasAlpha ? 24 : 16` ternary-shift form matches Tinycast's 2026-08-14 version, which Tinycast replaced on 2026-09-19. None of 1,668 unrelated Swift files checked use this form. Small (about six lines); LLM convergence cannot be fully excluded.

*Tinycast first seen: 2026-08-14 (removed 2026-09-19)*

[Thunderstorm `Sources/Extensions/ThunderstormExtensionNode.swift:413-424`](https://gitlab.com/droppyformac1/thunderstorm/-/blob/2ecde7836d43420b43f7f9d8cfe0c241bc2a67e0/Sources/Extensions/ThunderstormExtensionNode.swift#L413-424)

```swift
        if value.hasPrefix("#") { value.removeFirst() }
        guard value.count == 6 || value.count == 8, let number = UInt64(value, radix: 16) else {
            return nil
        }
        let hasAlpha = value.count == 8
        let red = Double((number >> (hasAlpha ? 24 : 16)) & 0xFF) / 255
        let green = Double((number >> (hasAlpha ? 16 : 8)) & 0xFF) / 255
        let blue = Double((number >> (hasAlpha ? 8 : 0)) & 0xFF) / 255
        let alpha = hasAlpha ? Double(number & 0xFF) / 255 : 1
        return Color(.sRGB, red: red, green: green, blue: blue, opacity: alpha)
    }
}
```

[Tinycast `Tinycast/Features/Extensions/UI/ExtensionImage.swift:110-120` @ `4cb914e7`](https://github.com/abue-ammar/tinycast/blob/4cb914e76dd6b9625e4e8f16f06b232910dd4637/Tinycast/Features/Extensions/UI/ExtensionImage.swift#L110-L120)

```swift
        }
        guard text.count == 6 || text.count == 8, let value = UInt32(text, radix: 16) else {
            return nil
        }
        let hasAlpha = text.count == 8
        let red = Double((value >> (hasAlpha ? 24 : 16)) & 0xff) / 255
        let green = Double((value >> (hasAlpha ? 16 : 8)) & 0xff) / 255
        let blue = Double((value >> (hasAlpha ? 8 : 0)) & 0xff) / 255
        let alpha = hasAlpha ? Double(value & 0xff) / 255 : 1
        return Color(red: red, green: green, blue: blue, opacity: alpha)
    }
```

## Binary evidence (released Droppy builds)

Static analysis of official DMGs, without executing anything. Field names come from Swift reflection metadata (`__swift5_fieldmd`); see `data/binary/`.

| Item | 15.2.2-beta.1 (signed 2026-09-09) | 16.0.0 (signed 2026-09-27) | 16.0.1 |
|---|---|---|---|
| `ThunderstormPointerState` (`hoverArmed`, `commandHeld`, `menuOpen`, `armingDistance`, `restingPoint`) | absent | present | present |
| `ThunderstormArmedHover` | absent | present | present |
| `ThunderstormBarButton` fields `chrome, isSelected, isCompact, action, label, hovered` (Tinycast `BarButton` order) | absent | present | present |
| `ThunderstormBarButtonChrome {capsule, rounded}`, `ThunderstormKeyCap.Style {outline, filled}` | absent | present | present |
| `ThunderstormRightClickCatcher` with nested `CatcherView` | absent | present | present |
| `ThunderstormScrollRequest` with `Goal {resetToTop, revealSelection}` and a UUID stamp | absent | present | present |
| `ThunderstormMenuItem` with `beginsGroup` | absent | present | present |
| `ThunderstormQuicklink` CodingKeys incl. `openWithBundleID` | absent (no quicklinks) | present | present |
| "Search for apps and commands…" (Tinycast's search prompt) | absent | present | present |
| "Search your Mac" (Droppy's own prompt) | present | present (localisation table) | present |
| Any "Tinycast" credit or licence notice | — | **none** | **none** |
