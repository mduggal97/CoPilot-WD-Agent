# Balsamiq .bmpr generation - file format, layout conventions, arrow geometry

Everything here was verified on delivered wireframes. Deviating from these conventions produced client rejections or corrupt files; follow them exactly.

## Durable tooling

These two scripts are **not shipped with the skill** - if they're not on your machine, regenerate them from the build-specs in [scripts.md](scripts.md) (don't rely on a hardcoded `_Design Tools\` path):
- `wireframe_builder.py` - generates a .bmpr in the house structure (pass a Balsamiq-saved .bmpr as the schema donor)
- `bmpr_render.py` - PIL PNG preview (the draft placeholder)

Editable `.bmpr` sources live in each app's client folder next to its design doc.

## File format - .bmpr is a SQLite database

Tables: `INFO` (SchemaVersion 2.0, ArchiveFormat bmpr, ArchiveRevision), `BRANCHES` (one row id `Master`; attributes include `"fontFace":"Balsamiq Sans","skinName":"sketch"`), `RESOURCES` (ID = uppercase UUID, BRANCHID = `Master`, ATTRIBUTES = `{"kind":"mockup","name":...,"trashed":false,"order":<float>}`, DATA = the mockup JSON), plus THUMBNAILS/USERS/COMMENTS.

**Always clone a known-good, Balsamiq-saved .bmpr for the schema** (composite PK on RESOURCES, COMMENTS FKs) - a hand-written schema produces "Unable to load project". Then delete/insert RESOURCES rows. One mockup = one board; all screens live on one canvas as frames. **No donor on hand?** (fresh engagement, no prior wireframes - no donor ships with this skill): ask the user for ANY Balsamiq-saved `.bmpr` from a past project, or have them open Balsamiq, create an empty project, and save it - a freshly-saved empty project IS a valid schema donor. Do not attempt to hand-write the schema.

**(!) Generate ONLY proven control typeIDs.** Balsamiq silently drops a mockup containing control types it can't handle - the file opens but reports **"nothing to import"** with no error naming the culprit (cost two real round-trips on one build - a delivered task app - 2026-07-30; the mockup `version` value was a red herring - working files carry "6.0", "7.0", and "13.0" alike). The verified-importing vocabulary from delivered files: `Text, BrowserWindow, Button, HRule, Canvas, ComboBox, TextInput, CheckBox, DateChooser, iPhone, ProgressBar, RadioButton, NumericStepper, Arrow, Table`. Do NOT emit `TitleWindow, DataGrid, TextArea, ButtonBar, IconLabel, HorizontalScrollBar` or any other type not on the proven list - even if it's a real Balsamiq control, our generated encoding of it has never survived import. (DataGrid/Table are banned by the grid convention anyway.) After generating any .bmpr, verify: every typeID  in  proven list, RESOURCES row has `kind:"mockup"` + `trashed:false` + BRANCHID `Master`, unique control IDs, and the INFO ArchiveAttributes `name` matches the project (a leftover donor name confuses the user).

- Mockup DATA: `{"mockup":{"controls":{"control":[...]},"mockupW","mockupH","measuredW","measuredH","version":"7.0"}}`
- Control envelope: `{ID, typeID, zOrder, x, y, measuredW, measuredH, properties}` (+ optional `w`,`h`). Verified typeIDs: BrowserWindow, iPhone (`properties.model:"IPhoneX"`), Text, TextInput, ComboBox, DateChooser, NumericStepper, CheckBox, SearchBox, Button, ProgressBar, Canvas (`{color,borderColor}` ints), HRule, Table, Arrow, Icon.
- Text + bold: `properties.jsonText = {"v":1,"dom":[[...runs...]]}`; a run is a string or `{"type":"bold","children":["txt"]}`. Read-only "Label: **value**" = ONE Text control with a bold run - never a TextInput for non-editable display.

## Layout conventions (client-approved structure)

- **Vertical wireflow**: screens stacked in a single column, grouped into numbered flow sections (bold `SECTION` heading + HRule). Branches (one page -> two targets): two columns under the source, each target under the button that opens it.
- **Yellow annotation notes to the RIGHT** of each screen (below for side-by-side rows). Build them manually: light-yellow Canvas (fill `16643026`, border `14268749`, ~380px wide) + a Text on top - do NOT use the StickyNote control (renders with an unremovable red washi-tape strip). First line bold short title, then 1-3 layperson sentences. Notes never overlap a frame. The "How to read this diagram" intro note goes above the Home page.
- Note text sizing: one `dom` entry per paragraph and SET THE TEXT CONTROL'S `w` - Balsamiq wraps at `w`; pre-wrapping the string doubles the line count and overflows. Estimate box height conservatively: chars/line ~ `(w-24)/10`, line-height ~ 22, height = `18 + linesx22` (older 14+linesx15 sizing ran tight - over-estimate).
- **Content INSIDE the BrowserWindow chrome**: chrome is ~72px tall - body header at y+86, desktop content from y+126, ~30px side padding; size each window to its content (+~48px pad). Mobile (iPhone frame): bold centered title ~y+66, content from ~y+112.
- **Real grids from primitives** - the Table control renders blank cells and can't hold Buttons. Build: Canvas header bar + Text header labels + Text data cells + real Buttons in the Actions cell + HRule row separators. Actions column FIRST (leftmost); multi-button cells stack vertically.
- OK/Cancel left-aligned; Home/landing = card layout (title + description + link, 2x2). Red inline callouts for enhancement designs (color `13369344`, size 11: "< NEW field...", "< CHANGED...") plus a key line at top.

## Arrow geometry (the hard-won part)

- Arrow properties: `{"loopRendering":"true","p0":{x,y},"p1":{x,y},"p2":{x,y}}` with `w`/`h` = the bbox. **`p0`/`p2` are endpoints in bbox pixels; `p1` is a FRACTION (0..1) curve-bend ratio, NOT pixels.** Absolute-midpoint p1 shoots arrows off-canvas.
- Attach connectors **center of the triggering button's bottom edge -> center of the target page's top edge** (compute from stored rects; corner offsets look "floating"). Arrows never anchor to controls - position endpoints yourself.
- Curve control: near-vertical arrows -> Balsamiq default `{0.564, 0.154}`; wide diagonals -> keep y low (~0.11), shift x toward the target (~0.72 rightward / ~0.28 leftward). **Never `{0.5, 0.5}`** - reads as a straight/odd line (client-rejected). Straight arrow = p1 at the absolute midpoint + `"leftArrow":"false"` (rarely wanted).
- Keep the down-path clear: triggering demo row LAST in hub grids; nav buttons bottom-right; leave a channel gap in bottom nav rows so the arrow passes between buttons.
- **When repositioning a shape, move its arrow x/y AND p0/p2 by the same delta** - forgetting one desynchronizes the visual.
- Best process for arrow fidelity: generate screens -> user opens/saves once in Balsamiq -> recompute ONLY the arrows on the saved file. Verify curve intent by sampling the quadratic `B(t) = (1-t)^2P0 + 2(1-t)t/C + t^2P2` where `C = (p1.x/w, p1.y/h)` in bbox-local coords.
- Arrows get a final human pass - expect the user to nudge a few p1 values in Balsamiq; their returned .bmpr becomes canonical.

## Programmatic verification before handoff

Script these checks: (a) no two page frames overlap; (b) no note Canvas overlaps a frame or another note; (c) no arrow segment (sampled p0->p2 curve) passes through a frame that is neither source nor target; (d) **INTRA-frame collisions**: within each frame, no control rectangle intersects another (tolerate intentional composites - Canvas+Text cards, header-bar text, HRule separators crossing cells) - buttons overlapping a grid shipped in a client-reviewed export once (2026-07-30), so this check is mandatory; (e) **frames sized to fit content**: every frame >= content extent + ~48px padding, content starts below the ~72px BrowserWindow chrome and keeps ~15px clear of the frame's inner border (Balsamiq draws the window border inside the rect). Grow frames rather than shrinking content; recompute mockupW/H after. These catch real bugs without opening Balsamiq. Then render the PIL preview as the draft placeholder.

Cloud upload + clean-PDF export can be automated through the user's browser session - see [balsamiq-cloud-roundtrip.md](balsamiq-cloud-roundtrip.md) (there is no Balsamiq public API; the UI is the only path).

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **`_Design Tools\` path** - where the builders (`wireframe_builder.py`, `bmpr_render.py`) live on your machine; if absent, regenerate from the build-specs in [scripts.md](scripts.md).
- **Schema-donor `.bmpr`** - a known-good, Balsamiq-saved `.bmpr` from the engagement to clone the SQLite schema from.

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).
