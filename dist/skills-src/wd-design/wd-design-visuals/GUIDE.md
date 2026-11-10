---
name: wd-design-visuals
description: Create and update Workday Extend/Integration design visuals - Balsamiq wireframes (.bmpr), wireflow diagrams, swimlane process flows (draw.io), flowcharts, and app-level sequence & state-machine diagrams (incl. Mermaid input) - in multiple output formats (bmpr, drawio, SVG, PNG, HTML, PDF embed). Use this skill whenever the task mentions wireframes, mockups, screens, wireflow, process flow, swimlane, flow diagram, flowchart, sequence diagram, state machine, Mermaid, Balsamiq, draw.io/drawio, or embedding diagrams into a design document. Even "add one screen to the wireframe" goes through this skill - arrow geometry and layout conventions are easy to break.
---

# Design Visuals - Wireframes, Process Flows & App-Level Diagrams

Four diagram types live here: **wireframes** (every screen, with wireflow arrows), **process flows** (every step and exchange, in swimlanes), and - for orchestration/O4I work where timing and lifecycle matter more than screens - **sequence diagrams** (the ordered call exchange between participants) and **state-machine diagrams** (one request/record's lifecycle and the events that move it). All embed into the design doc (wd-design-doc owns the workbook; this skill owns the diagrams).

A "sequence diagram / state machine / Mermaid" request routes to [references/output-formats.md](references/output-formats.md) (section "Two more diagram TYPES worth reaching for") - Mermaid text is a legitimate authoring path for both. These stay app-level; system-LEVEL landscape maps belong to wd-systems-diagrams.

## Non-negotiable: thoroughness

Diagrams are judged complete only against an enumerated list - build the list first, then check every item appears:

- **Wireframes**: EVERY page in the app - worker, approver, admin/config, confirm/micro pages, and request-type variants. Enumerate from the PMDs (or the designed page list pre-build). Every action button gets a wireflow arrow to its resulting page.
- **Process flow**: every step and exchange - screen transitions, API/RaaS/web-service calls, BP steps (approve/deny/send-back loops), notifications.
- **Both**: plain-English layperson annotations (a director who's never seen Workday should follow the story), plus a "How to read this diagram" note.

**Before wireframe sign-off, run the design passes** in wd-extend-dev ui-design-principles.md: the task-first lock (each screen states its one-sentence task + the Workday state after success) and the adversarial UX 5-question hostile-user pass (wrong-order fill, nav-back data loss, empty first launch, dead-end state, wrong-role visibility). A wireframe with no answer to one of those is not ready to sign off.

## Wireframes - Balsamiq first (draw.io when Balsamiq isn't available)

**Check the environment BEFORE emitting a `.bmpr`.** Balsamiq depends on the desktop app plus (for the automated round-trip) MCP access - and some managed corporate environments block MCP entirely, degrading the flow to a manual import/export round-trip, or the user may have no Balsamiq at all. In that case **draw.io is the first-class wireframe alternative, not a workaround**: this skill can author WIREFRAMES in draw.io format (same as process flows), and draw.io renders itself with no desktop app in the loop - the round-trip disappears. Ask up front which format is wanted when unsure, noting the tradeoff: Balsamiq = house style + the house clean-export pipeline; draw.io = self-rendering, zero desktop/MCP dependency. Never emit a `.bmpr` the user cannot open. (Live-use finding, 2026-08-18.)

All Extend wireframes are AUTHORED in Balsamiq (`.bmpr`) where Balsamiq is available. Read [references/balsamiq-bmpr.md](references/balsamiq-bmpr.md) before generating or editing one - it holds the file-format mechanics (a .bmpr is a SQLite DB; clone a known-good file's schema), the house-preferred layout (vertical flows, yellow annotation notes to the right, curved loop connectors button->next screen, real grids from primitives), and the arrow-geometry rules that cost many iterations to learn.

**The clean-export rule (remind the user EVERY time a wireframe changes):** any render generated here (PIL preview, PNG) is a DRAFT PLACEHOLDER. The final design doc embeds the user's clean Balsamiq export (File -> Export -> PDF/PNG). After delivering any wireframe update, explicitly remind the user to open the .bmpr, review/nudge arrows, and export - then embed their export (render PDF->PNG at ~300dpi via PyMuPDF, crop margins, embed ~720px wide). The end-to-end export-and-embed workflow (and the browser-automation variant, where the extension is permitted) is in [references/balsamiq-cloud-roundtrip.md](references/balsamiq-cloud-roundtrip.md). If the user returns a hand-adjusted .bmpr, that file becomes canonical - never regenerate over it.

## Process flows - the standard swimlane template

One draw.io template for every Extend app with a UI: header container "Extend Business Objects" (custom BOs as cylinders) + a horizontal pool with **3 lanes: User / Integration-API / BP-Approval**. Read [references/process-flow.md](references/process-flow.md) for the lane contents, styles, and per-app instantiation steps. **Integration-only apps (no UI) get a tailored flowchart instead** - the 3-lane UI swimlane doesn't fit them; the reference covers that variant.

## Output formats - meet the audience where they are

[references/output-formats.md](references/output-formats.md) maps needs to formats: .bmpr (editable wireframe source), .drawio (editable flow source), PNG (design-doc embeds; headless drawio export command included), SVG (crisp docs/web), PDF (client review), HTML (clickable draft walkthroughs). Default deliverable pair: editable source + PNG embed. The render/build scripts these formats use (`bmpr_render.py`, `process_flow_builder.py`, and their regenerate-on-demand build-specs) are documented in [references/scripts.md](references/scripts.md). When a client tool dictates a different format (Visio, Lucid), produce drawio XML - both import it.

**Keep an editable source for EVERY embedded diagram - never bake one as a source-less PNG.** This holds beyond wireframes and process flows: architecture diagrams, Gantt/timeline charts, and any raster embedded in a doc need their `.drawio` (or equivalent) source kept alongside the deliverable. A source-less PNG turns a one-word text change into pixel-by-pixel raster surgery.

## Working rhythm

- Draft visuals early (a straw-man flow in the FIRST design meeting gets corrected fast - people correct better than they specify; wd-discovery uses this too).
- Update visuals in the same change set as the design tabs they illustrate; a stale diagram contradicting the Requirements tab is a defect factory.
- Verify programmatically before handoff: no overlapping frames/notes, no arrow crossing an unrelated page, all pages from the enumerated list present.

## Lifecycle neighbors

feeds wd-design-doc (UI & Wireframes / Process Flow tabs); previous = wd-discovery (the process story comes from there); next = wd-extend-dev (builders navigate by these). Program/system-LEVEL integration landscape or "architecture diagram of how systems connect" = wd-systems-diagrams (this skill is app-level only).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
