# Output formats - choosing and producing each

Different audiences need different formats; flexibility here is the point. Always keep an EDITABLE source (.bmpr for wireframes, .drawio for flows) plus whatever presentation format the moment needs.

| Need | Format | How |
|---|---|---|
| Wireframe editable source | `.bmpr` | Generate per balsamiq-bmpr.md; the user's Balsamiq is the editor of record |
| Wireframe draft preview | PNG (PIL render) | `bmpr_render.py` - clearly a draft; never the final embed |
| Wireframe final embed | PNG from the user's Balsamiq PDF/PNG export | Render PDF->PNG via PyMuPDF (`fitz`) at ~300dpi, crop margins + page marker, embed ~720px wide (`pdftoppm` is not installed - use PyMuPDF) |
| Process-flow editable source | `.drawio` | Template + builder per process-flow.md |
| Flow/diagram embed | PNG | Headless draw.io export (command in process-flow.md) |
| Crisp diagrams for web/docs | SVG | draw.io `--format svg`; or author simple flowcharts directly as SVG when draw.io isn't warranted |
| Client review packet | PDF | Balsamiq export (wireframes); draw.io `--format pdf` (flows) |
| Wireframe when Balsamiq is blocked | draw.io XML + PNG export | draw.io desktop supports wireframing when Balsamiq or the Balsamiq MCP is unavailable (e.g. corporate browser policy). Label clearly as a wireframe draft. The Balsamiq `.bmpr` remains the editable source of record - plan a Balsamiq hand-off to produce it when access is restored; the draw.io draft is a working sketch, not the sign-off artifact. |
| Clickable walkthrough draft | HTML | Single-file HTML with one `<section>` per screen and anchor links wired to the buttons - useful to *feel* a flow before build; label it DRAFT, it is not a deliverable of record |
| Client uses Visio/Lucidchart | `.drawio` XML | Both tools import drawio XML - produce that rather than native formats |

Rules that hold across formats:

- The design doc's embedded image and the editable source must match - regenerate the embed on every source change (wd-design-doc's same-day update rhythm).
- Version the sources alongside the design doc version (`<App>_wireframe_v1.3.bmpr`) so a signed design pins its visuals.
- Cloud-synced folders (e.g. OneDrive) can lock files against reads - copy to the scratchpad before opening programmatically.

## Two more diagram TYPES worth reaching for - and Mermaid as an input path

Beyond wireframes and swimlane process flows, two diagram *types* earn their place on
orchestration/O4I work, where the interesting thing is timing and lifecycle, not screens:

- **Sequence diagram** - the ordered call exchange between participants (page/user ->
  orchestration -> Workday SOAP/REST -> external system, request then response, including
  retries and error branches). Best when the question is "in what order does what call
  whom" across an O4I flow or a multi-hop integration.
- **State-machine diagram** - the lifecycle of one request or record (e.g. Draft ->
  Submitted -> In Approval -> Approved/Denied -> Posted), with the events that drive each
  transition. Best when the question is "what states can this thing be in and what moves
  it between them" - a natural fit for BP-backed request objects.

**Mermaid as an input path (capability note, not an engine spec):** Mermaid text
(`sequenceDiagram`, `stateDiagram-v2`) is a compact, diffable way to *author* either
type, and that text can be rendered/exported to the presentation formats above (SVG/PNG/PDF)
for embedding - so a Mermaid block is a legitimate starting point, not just a scratch
sketch. Keep the editable source alongside the embed like any other diagram.

**Mermaid is an authoring path, not a layout engine (live-use finding, 2026-11-05).** Auto-laying a Mermaid flowchart out (e.g. the Figma connector's `generate_diagram` into FigJam) drops subgraph titles, renders heading nodes as flow steps and produces tall portrait pages. For a swimlane or any stakeholder-facing flow, script the placement instead: draw.io XML via `process_flow_builder.py`, or a Figma DESIGN file via the connector's `use_figma` (vectors with `ARROW_LINES` end caps for elbow arrows, 4-point polygons for decisions), keeping the script as the editable source.

These stay app-level: sequence/state diagrams describe one app or flow's internals.
System-LEVEL landscape and per-workstream integration maps belong to **wd-systems-diagrams**,
not here - and everything in this file is **wd-design-visuals**'s to own (wireframes,
wireflows, process flows, and now these two types). Route by that boundary, don't duplicate.
(Diagram-type additions folded in from external skillsmp `archify`.)
