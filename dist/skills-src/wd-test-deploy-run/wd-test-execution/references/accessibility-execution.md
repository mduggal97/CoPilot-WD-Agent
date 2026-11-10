# Accessibility execution - verifying a11y against the BUILT app

Design-time accessibility is captured as an NFR (wd-design-doc nfr-accessibility.md section 1);
this reference is how you VERIFY it against the running app by driving the Browser pane. It is a
browser-driven execution method, the a11y arm of the standard run loop (execution-workflow.md):
same preflight, same evidence discipline, same Pass/Fail/Blocked report - the difference is WHAT
you assert (perceivable/operable/understandable behavior) and HOW (keyboard + accessibility tree,
not just the visual render).

Scenario DERIVATION stays in wd-testing (accessibility scenarios are derived there from the design's
NFR rows); this reference owns the execution mechanics. Route failures back to wd-testing
defect-triage.md like any other Fail.

---

## The conformance bar - confirm it before you run

Default target: **WCAG 2.1 AA** (the common commercial/508 bar; Section 508 references WCAG 2.1 AA).
**Confirm the client's required level** before running - higher-ed and government clients often
mandate AA in contract, some scope AAA for specific criteria, and the design doc's stated target
(nfr-accessibility.md) may carry app-specific exclusions ("inherited from Workday PMD except where
noted"). Test to the level the design commits to; a stricter client contract level overrides the
default. Record the level under test in the run report header so a Pass is scoped to a known bar.

**PMD inherits most AA behavior from standard Workday UI** - so the highest-yield targets are the
app-SPECIFIC choices that break inheritance: custom `richText`/status colors, icon-only buttons,
placeholder-only inputs, hover-only reveals, custom grids, and error surfacing. Test those hardest.

---

## What to check - the seven execution checks

Run each against every primary flow's PMD pages (the same pages your functional scenarios cover).
Each check names its assertion tool and its WCAG anchor.

### 1. Keyboard-only navigation + focus order

- **Method:** drive with `computer` key presses only - `Tab` / `Shift+Tab` to move, `Enter`/`Space`
  to activate, arrow keys within composite widgets (grids, radio groups), `Esc` to dismiss. Do NOT
  click. After each `Tab`, `read_page` and confirm which element reports focus.
- **Assert:** every interactive control (inputs, pickers, grid cells, OK/Cancel/Submit, icon
  buttons) is reachable and operable by keyboard; focus order follows a sensible reading order (not
  a scrambled DOM order); no keyboard trap (you can always Tab back out, and `Esc` closes
  modals/breakouts). A required path that needs the mouse (e.g. a hover-only reveal) is a Fail.
- **WCAG:** 2.1.1 Keyboard, 2.1.2 No Keyboard Trap, 2.4.3 Focus Order.

### 2. Visible focus indicator

- **Method:** at each `Tab` stop, screenshot; where the indicator is subtle, `javascript_tool`
  INSPECT-only to read the focused element's computed outline/box-shadow (`document.activeElement`
  + `getComputedStyle`). Inspect only - never modify the page.
- **Assert:** the focused control shows a visible focus indicator that meets the contrast bar
  against adjacent colors. Custom-styled controls that suppress the default outline without
  replacing it are a Fail.
- **WCAG:** 2.4.7 Focus Visible (contrast per 1.4.11).

### 3. Accessible name / label (screen-reader sensibility)

- **Method:** `read_page` returns the accessibility tree - each control's role + accessible NAME
  are what a screen reader announces. Walk the tree and check every input/picker/grid column/button.
  `find` by expected label to confirm the name resolves.
- **Assert:** every control has a real accessible name (from a `<label>`, `aria-label`, or
  `aria-labelledby`) - NOT placeholder-only, NOT the empty string, NOT "button" for an icon-only
  control. Grid columns carry header semantics; headings use real heading levels in reading order.
  A control that appears in the tree with no name (or a generic role-only name) is a Fail.
- **WCAG:** 1.1.1 Non-text Content, 1.3.1 Info and Relationships, 4.1.2 Name/Role/Value, 2.4.6
  Headings and Labels.

### 4. Color contrast

- **Method:** for body text and any custom `richText`/status color, `javascript_tool` INSPECT-only
  to read computed foreground + background colors, then compute the ratio (or `zoom` a region for a
  visual read). `resize_window` colorScheme to also check dark mode if the app themes.
- **Assert:** body text >= 4.5:1; large text, UI component boundaries, and graphical/status objects
  >= 3:1. Re-check after any brand palette swap. Status/grouping is NEVER conveyed by color alone -
  it carries a second cue (text label, icon, or pattern); a RAG dot with no text label is a Fail.
- **WCAG:** 1.4.3 Contrast (Minimum), 1.4.11 Non-text Contrast, 1.4.1 Use of Color.

### 5. Error identification + association

- **Method:** drive a submit that fails validation (reuse the negative-path functional scenarios);
  `read_page` the resulting error state (Extend pages are server-rendered - a failed submit is a
  page navigation to an error/exception summary, per execution-workflow.md, not a red XHR).
- **Assert:** each error is identified in text (not color/icon alone), is programmatically tied to
  its field (the a11y tree associates the message with the input via `aria-describedby` /
  field-level error, not just a top-of-page banner), and describes how to fix it in plain language
  (no raw 400/S-codes). A banner a screen reader cannot associate with the offending field is a Fail.
- **WCAG:** 3.3.1 Error Identification, 3.3.2 Labels or Instructions, 3.3.3 Error Suggestion.

### 6. Target size

- **Method:** `javascript_tool` INSPECT-only to read the rendered width/height (bounding box) of
  interactive controls - especially icon-only buttons, grid-row action icons, and any custom
  compact control. `resize_window` to mobile if mobile is in the support matrix.
- **Assert:** interactive targets meet the size bar (WCAG 2.1 AA 2.5.5 Target Size (Enhanced) is
  44x44 CSS px where the client scopes it; the 2.2 AA minimum 2.5.8 is 24x24 - confirm which the
  client requires). Cramped icon-only controls with no spacing exception are a finding.
- **WCAG:** 2.5.5 / 2.5.8 Target Size (confirm level with client).

### 7. Reflow / zoom (where scoped)

- **Method:** `resize_window` to a narrow width (or emulate 400% zoom) and `read_page` /
  screenshot; confirm content reflows without horizontal scrolling and nothing is clipped or lost.
- **Assert:** no loss of content or function; no two-dimensional scroll for reading order.
- **WCAG:** 1.4.10 Reflow, 1.4.4 Resize Text.

---

## Evidence, recording, and routing

Same discipline as every other execution flow (execution-workflow.md):

- **Every check carries a captured observable.** A keyboard-nav Pass = the `read_page` focus trace
  (the ordered list of focused controls) plus a screenshot at key stops; a contrast Pass = the
  computed color pair + ratio; a name Pass = the a11y-tree excerpt showing role + accessible name.
  No row is "Pass" without proof - a visually fine screenshot does not prove an accessible name
  exists.
- **Name artifacts by scenario id** (e.g. `A11Y-003_focus-trace.json`, `A11Y-007_contrast.png`) into
  the running per-app/date evidence folder.
- **Report** in the same Pass/Fail/Blocked table (add the WCAG criterion to the Notes column and the
  conformance level to the run header). Keep severity/triage OUT of this report - that is wd-testing's
  call.
- **Failures route to wd-testing defect-triage.md** for bug-vs-CR-vs-doc-drift classification. An
  a11y miss against a stated AA commitment is typically a defect; a gap against a level the design
  never committed to may be a CR - triage decides, not this reference. Diagnose (locate the
  page/control), do not fix; code fixes go to wd-extend-dev.

## Boundaries

- **Scenario derivation** (which flows, which criteria matter for this app) -> **wd-testing** (from
  the design's NFR rows). This reference executes; it does not decide coverage.
- **Design-time a11y capture** (labels, contrast intent, keyboard path as a stated requirement) ->
  **wd-design-doc** nfr-accessibility.md section 1. This verifies the built result against that intent.
- **Deliverable accessibility** (the Word/PDF/PPTX/diagrams the suite SHIPS - tagged PDF, alt text,
  Section 508 on docs) -> wd-design-doc nfr-accessibility.md section 1b; that is a
  document-conformance obligation, not this app-runtime walk.
- **Marketplace VPAT / accessibility conformance statement** (the productized listing artifact) ->
  **bow-sales-enablement** accessibility-statement.md; the evidence THIS reference captures is what
  substantiates the conformance claims there, subject to that skill's claims-governance gate.
