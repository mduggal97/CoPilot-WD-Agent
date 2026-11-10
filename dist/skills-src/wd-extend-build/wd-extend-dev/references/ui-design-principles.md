# UI design principles - how to design an ENGAGING PMD app (the craft layer)

Our suite is deep on UI MECHANICS (widget props in pmd.md/widget-catalog.md, chart vocab in
charts.md) and on the architecture-choice mindset (solutioning.md). This file is the layer
BETWEEN them: the visual-craft/design-PRINCIPLE guidance that makes a PMD page or dashboard
engaging, scannable, and usable - not just functional. Everything here is expressible in the
Extend PMD model (sections/columnWidthRatios, cards, readOnlyText/hint, chart props,
empty-state placeholders); we do NOT hand-write HTML/CSS for the apps.

(Modeled 2026-08-28 from community design skills on skillsmp.com - generic design principles,
genericized to PMD; brand color remains the darker-BoW palette, not changed here.)

## 0. Frame it before you lay it out - the 5 anchors

Before authoring a page or dashboard, fix five anchors (run this at solutioning, feeds wd-discovery):
- **Purpose** - the single task this surface serves.
- **Audience** - who uses it repeatedly, and what THEY prioritize (an approver scans; a clerk enters).
- **Tone** - match the domain: an internal admin/finance tool is DENSE and QUIET, not marketing chrome.
- **Memorable detail** - one thing that makes it feel considered (a clear status system, a good empty state).
- **Constraints** - accessibility, the Workday theme, existing app conventions to stay consistent with.
Design for repeated daily use, not first impression.

**Task-first lock (before you open the wireframe tool):** for each screen, lock TWO sentences first -
"the user's task in one sentence" and "the Workday state after success" (the record/BP/data that
exists when they finish). If you cannot state both crisply, the screen is not ready to lay out. This
keeps every screen anchored to a real task and a verifiable outcome, not a collection of widgets.

## 1. Dashboards - start from the operator's question, not the layout

Design every dashboard to answer four questions, in this order top-left (most decision-critical) first:
1. **Is it healthy?** (overview / status)  2. **Where is the bottleneck?** (performance)
3. **What changed?** (trend/delta)  4. **What action should someone take?**
Panel order: Overview -> status -> capacity/resources -> domain-specific.
**Actionability test:** reject any panel/tile that does not drive a decision - a chart that answers
no question is decoration, cut it.

## 2. Charts - make "good vs bad" legible at a glance (house default)

The chart MECHANICS are in charts.md; the DISCIPLINE (promote these from optional to default on any
client-facing dashboard):
- Pick the chart type from the DECISION it supports, not the data shape.
- Every chart carries a **title**, **unit-labelled axes** (`measurementAxisOptions.axisTitle`), and a
  **threshold/target reference line** (`comparisonLineValue` / `targetLineDataSet`) so the reader sees
  target-vs-actual instantly.
- **Conclusion-style titles:** the title states the FINDING, not the subject - "Spend up 12% vs plan,"
  not "Spend by month." A chart whose title is a noun makes the reader do the analysis; a chart whose
  title is the takeaway lands immediately. (Where the finding is dynamic, compute it into the title text.)
- `accessibilityMode` pattern fills on any chart that carries meaning by color (charts.md), AND pick a
  **colorblind-safe series palette** - distinguishable when desaturated to grayscale, never red-vs-green
  as the only signal. Sanity check: if the chart still reads with color removed, it passes.

## 3. Page layout conventions

- **Width by job:** narrow for a settings/single-record form; wide for lists/tables; full-bleed only for
  an immersive view. (Expressed via `section`/`columnWidthRatios` + which container you choose.)
- **Placement:** table ACTIONS above the grid, right-aligned; SEARCH/FILTERS above, left-aligned; ALERTS
  at the top of the page or the top of the relevant section, never mid-content.
- **Side detail over a page hop:** when navigating away would break the user's context (editing one row
  of a long list, a quick detail view), use an in-page detail section/pod (grid `onRowSelect` toggle,
  widget-catalog.md) instead of a page navigation - and always guard unsaved edits ("discard changes?").
- **Searchable over typed (HOUSE GUARDRAIL, 2026-08-31):** never make a user TYPE a value that
  Workday can look up. Any field whose value exists in the tenant (roles, workers, orgs, usage types,
  items, reports) is an `instanceList` picker backed by a WQL/endpoint search (`onSearch` + deferred
  invoke - pmd-gotchas), NOT a free-text field. Free text is reserved for values Workday genuinely
  cannot know (external IDs, file paths, ad-hoc comments). Corollary: when one selection constrains
  another (role -> its enabled usage types, method -> its valid references), make the second field a
  DEPENDENT dropdown populated in the first field's `onChange` (`setValues`) so invalid combinations
  are unpickable - validation by construction beats validation by error message. (Proven pattern:
  Role Pairing addRolePair/addMappedReport, 2026-08-31.)

## 4. Cards / pods - an information-density budget

Keep each surface scannable by capping what it carries:
- **One idea per card/pod/section.** If it needs more, split it.
- A **dashboard tile** shows one KPI + one supporting detail (label + impl line - feedback_visual_deck_style).
- If a grid of tiles grows past **~6**, group, tab, or paginate.
This is the PMD expression of the reader's own accessibility rule (chunk it, one idea per line).

## 5. Numbers - align them (big for our finance apps)

AP recon, budget variance, position costing - number columns ARE the app. House rule for numeric/
currency grid columns:
- **Right-align** numeric and currency columns; **fixed precision** per column; **parentheses for
  negatives** (a charts.md number-format option).
- Use **tabular (monospaced) figures** where the Workday theme exposes it, so digits line up and do not
  jitter as values change. Where PMD/theme cannot set it, capture the intent as a design-doc note.

## 6. States are first-class - design empty / loading / error / zero-results

Every data surface needs deliberate states, not a blank void:
- **Empty (onboarding):** show the next action ("No requests yet - Create the first").
- **Empty (populated list, filtered to nothing):** keep the list's shape/columns so the page does not jump.
- **Zero search results:** stable layout - do not collapse the surface.
- **Loading:** a visible loading state, not a frozen blank.
- **Error:** name the problem AND the recovery path.
Author these alongside the happy path (build-from-scratch.md skeletons), reusing the null-safe grid
idiom (widget-catalog.md).

## 7. Microcopy is design

User-facing text is part of the UI, not filler (config-driven UI text mechanics live in standards.md;
this is how to WRITE it):
- **Buttons:** action-verb + object ("Submit request," "Assign room") - never a bare "OK".
- **Errors:** name the problem AND suggest the fix ("Amount exceeds the par limit - lower it or request
  an exception"), not "Invalid input".
- **Empty states:** point to the next step.
- **No redundant entry:** do not ask for something the system already knows.
Voice: clear, plain, professional (deliverable-review.md / writing-quality-gate.md own the bar).

## 8. Hierarchy + motion

- The app's **primary working surface leads**; the first viewport makes the purpose obvious (utility over
  hero chrome). Type is contextual and scannable, stable across hover/focus/loading - not oversized
  decorative headers.
- **Motion only to clarify state** (loading->loaded, open->closed). No decorative animation. (PMD gives
  limited control - `animateOnLoad` on charts; the durations matter more for HTML BoW dashboards/decks.)

## 9. Accessibility - the concrete AA numbers

Bake the thresholds in (the design-doc NFR capture + BAA/sign-off gate live in wd-design-doc
nfr-accessibility.md; these are the build-side targets):
- Contrast **4.5:1** normal text, **3:1** large text + UI components.
- Interactive target **24x24 px minimum** (WCAG 2.2 SC 2.5.8); pad small icon-actions - do not ship
  pixel-tiny targets (our stacked per-row grid buttons, widget-catalog.md).
- Visible, high-contrast **focus indicator**; keyboard reachable; focus returns to the trigger on close.
- **Error messages carry a correction suggestion** (see 7).
- Usable at **400% zoom**; status changes announced (live region) where the theme allows.
Where the Workday theme constrains any of these, record it as a design-doc NFR caveat, do not silently drop it.

## 10. Self-review before you demo (the design gate)

**L0 - a 3-layer VISUAL audit, run BEFORE functional testing** (a design-quality layer above the
runtime gotcha sweep): (1) **Layout** - alignment, spacing rhythm, hierarchy, nothing crowded or
adrift; (2) **States** - empty/loading/error/zero-results actually authored (section 6), not blank;
(3) **Truncation/overflow** - long names, big numbers, many rows, small viewport - does anything clip,
wrap ugly, or push the layout. Fix L0 before you spend a functional-test cycle on a page that looks
unfinished.

**Adversarial UX pass - 5 hostile-user questions before wireframe sign-off** (wd-design-visuals runs
this at sign-off): (1) What happens if the user fills fields in the WRONG order or skips a required
one? (2) Does hitting nav-back / Cancel LOSE their entered data with no warning? (3) What does the
FIRST launch look like with zero data - is it a dead blank or a guided empty state? (4) Can a user
reach a state they cannot get OUT of (a dead-end page, a stuck flow)? (5) What does a wrong-role or
proxied-wrong-worker user see - a leak, or a clean deny? A wireframe that has no answer to one of
these is not ready to sign off.

Before a client-facing page/dashboard ships or demos, run two passes (screens x states):
- **Enumerate every view AND state:** empty / populated / loading / error / disabled; each dialog/menu;
  each tab/step; single + multi-select; success; role/permission variants. (wd-design-visuals owns the
  screens-x-states matrix in the wireframes.)
- **Visual pass:** alignment + spacing rhythm, control placement + button hierarchy, type consistency,
  truncation/overflow, focus states, icon consistency.
- **UX pass:** discoverability, step count, affordance clarity, empty/error guidance, error recovery,
  destructive-action confirmation, sensible defaults, loading feedback, accessible naming.
Quick self-score (0-10) on: color consistency, type hierarchy, spacing rhythm, component consistency,
information density, accessibility, polish (hover/loading/empty states). Registered as the "UI design
self-review" row in quality-gates.md.

## Cross-refs

Mechanics: pmd.md, widget-catalog.md, charts.md. Design mindset + toolbox: solutioning.md. Minimal
skeletons: build-from-scratch.md. Wireframes + screens-x-states matrix: wd-design-visuals. Design-doc
NFR/accessibility gate: wd-design-doc nfr-accessibility.md. Deck stat-card craft: feedback_visual_deck_style.
