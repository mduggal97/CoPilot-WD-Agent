# Scripts this skill uses - regenerate-on-demand build-specs

None of these ship as files (they lived in a hardcoded `_Design Tools\` folder). If one isn't
on your machine, Claude regenerates an equivalent from the build-spec below. Setup (Python +
Pillow) is in `wd-extend-lifecycle/references/prerequisites.md`. **Windows caveat:** the two
Balsamiq scripts hardcode `C:/Windows/Fonts/` - on Mac/Linux, ask Claude to point the font
loader at a local TTF. The final wireframe deliverable is always a clean Balsamiq export (these
renders are drafts) - see the clean-export rule in this skill.

---

### process_flow_builder.py - emits the standard Extend swimlane process-flow diagram as draw.io XML (blank template + one app instance)
- **Language / runtime:** Python 3.x, stdlib only. No shelling out.
- **Third-party deps:** none / stdlib only (`sys`).
- **OS constraints:** Cross-platform. Writes UTF-8 text files only.
- **Inputs:** Two CLI args: `argv[1]` = output path for the blank TEMPLATE diagram, `argv[2]` = output path for the app instance. No env vars, no input files. Content comes from two in-file `dict`s (`TEMPLATE`, `CC`) mapping node keys -> labels.
- **Outputs:** Two `.drawio` (mxGraphModel XML) files, one per label set. Stdout prints the two paths.
- **Method:**
  1. Define reusable draw.io style strings as module constants (AMBER box, CYL cylinder, ACTOR umlActor, LANE, LANELBL rotated lane label, CONT container, DIAM rhombus, PROC process, NOTE, LEG table, E edge, ED dashed edge).
  2. `esc()` XML-escapes text and converts `\n` -> `<br>`.
  3. `build(L)` takes a label dict and assembles `<mxCell>` strings via helpers `node(id,key,x,y,w,h,style)` (label from `L`), `raw(id,val,...)` (literal label), `edge(source,target,style,label)`.
  4. Lay out fixed geometry: title top-left (40,24); an "Extend Business Objects" header container at (300,20,900,140) with 3 cylinders; three horizontal swimlanes (User y=180 h=470, Integration y=650 h=250, BP/Approval y=900 h=620), each 1300 wide at x=60, with 34px rotated label bars.
  5. Populate lanes with fixed-coordinate nodes: actors, action/confirm/view boxes, config; API/RaaS/admin/third-party note; legend, approval rhombus, approved/denied boxes, approvers actor, Status container + event cylinders.
  6. Wire ~20 edges (solid `E` / dashed `ED`) between node ids, some labeled.
  7. Wrap body in `mxfile > diagram > mxGraphModel > root`, page 1500x1600.
  8. Write `build(TEMPLATE)` -> argv[1], `build(CC)` -> argv[2].
- **Key constants to preserve:** amber `#FFE6A0`/`#D6B656`, actor `#FFFFFF`/`#000000`, lane stroke `#666666`, lane label `#EFEFEF`/`#CCCCCC`, note fontColor `#D79B00`, edge `#404040`/`#666666`. Page `pageWidth=1500 pageHeight=1600`, `grid=0`. Lanes x=60 w=1300; header 300,20,900,140. `host="app.diagrams.net"`.
- **Gotchas:** labels MUST be XML-escaped and newlines -> `<br>` or draw.io breaks. Lane labels use `horizontal=0` (vertical text). Edges reference cells by string id -> ids must be unique and defined. The per-app dict is a one-off; the reusable part is the geometry engine + style constants.
- **Regeneration confidence:** High - pure string templating; only per-app labels differ.

---

### wireframe_builder.py - generates a Balsamiq `.bmpr` (SQLite) wireflow with vertical flows, sticky notes, grids, and curved loop-arrows
- **Language / runtime:** Python 3.x. No shelling out.
- **Third-party deps:** Pillow/PIL (`ImageFont`, for text-width metrics). Stdlib: `sqlite3, json, sys, uuid, os, shutil`.
- **OS constraints:** Windows-only as written - hardcoded `C:/Windows/Fonts/arial.ttf` / `arialbd.ttf` (repoint on other OSes).
- **Inputs:** `argv[1]` = OUT `.bmpr`; `argv[2]` = REF (an existing exported `.bmpr` used as the schema/skin donor).
- **Outputs:** One `.bmpr` (SQLite) with one mockup holding all screens on a single canvas. Stdout: path + control count.
- **Method:**
  1. Global `ctrls` + id counter; `add(typeID,x,y,w,props,h,mW,mH)` appends a control dict (`ID`, `typeID`, `zOrder`, `measuredW/H`, `x/y/w`, optional `h`, `properties`).
  2. `J(s,bold)` builds the Balsamiq `jsonText` DOM (one entry per `\n`-split line; bold runs wrapped `{"type":"bold","children":[...]}`).
  3. Widget helpers: `text, hrule, combo, tinput, check, field, red` (red callout), `button` (returns bottom-center anchor), `note` (yellow sticky sized to wrapped text), `grid` (manual: Canvas container + header shade + column-separator Canvases + header/data Text + HRule separators), `arrow` (curved loop arrow).
  4. `wraplines(s,wpx)` counts wrapped lines via PIL metrics to size notes.
  5. `screen(title,x,y,sw)` adds a BrowserWindow, returns content origin; `finish()` resizes window height to content.
  6. Emit screens in 4 flows (worker submit; worker change; manager review; admin config), stacking top-to-bottom with bold flow labels.
  7. Record button anchors + target-tops; after each flow draw `arrow()` from button to next screen's top-left.
  8. Compute `mockupW/H` from max extents; wrap as `{"mockup":{...,"version":"6.0"}}`.
  9. Copy REF->OUT, open SQLite, DELETE RESOURCES/THUMBNAILS/COMMENTS, update INFO name, INSERT one RESOURCES row (uppercase-UUID id, BRANCHID `Master`, ATTRIBUTES `{"kind":"mockup",...,"order":1000000.0}`, DATA = mockup JSON), commit.
- **Key constants:** `LX=40, PAD=30, TOP=88, NGAP=30, NW=400`. Note fill `16643026`/border `14268749`; grid white `16777215` border `11184810`, header shade `15921906`, separators `12303291`. Red `RED=13369344`. Fonts 12/13. Arrow `p1` fixed fraction `{0.564..., 0.1538...}`, `mW=150, mH=100`. Mockup `version:"6.0"`. Grid header h26, row h22, PADC 12.
- **Gotchas:** `.bmpr` IS SQLite - copy a real exported REF first to match exact schema/skin (differs per Balsamiq release). Arrow `p0`/`p2` are bbox pixels but `p1` is a 0-1 curve-bend FRACTION - absolute values shoot arrows off-canvas. Use manual grids, not the Table control. Over-estimate wrapped lines or notes overflow. RESOURCES id must be uppercase UUID. Carries a one-off content block; reusable part is the widget/grid/note/arrow engine.
- **Regeneration confidence:** Medium - engine is reproducible, but the exact Balsamiq JSON envelope (jsonText DOM, mockup version, ArchiveAttributes) needs an authentic REF `.bmpr`, and arrow curve values are taste-tuned.

---

### bmpr_render.py - generic `.bmpr` -> PNG renderer (rough local preview approximating Balsamiq)
- **Language / runtime:** Python 3.x. No shelling out.
- **Third-party deps:** Pillow/PIL (`Image, ImageDraw, ImageFont`). Stdlib: `sqlite3, json, sys, math`.
- **OS constraints:** Windows-only as written - hardcoded `C:/Windows/Fonts/` (arial/arialbd); repoint on other OSes.
- **Inputs:** `argv[1]` input `.bmpr`, `argv[2]` output PNG, `argv[3]` optional float scale (default 1.0). Reads the first RESOURCES.DATA row as the mockup JSON.
- **Outputs:** One PNG. Stdout: "rendered <path> <size>".
- **Method:**
  1. `font(sz,b)` loads Arial/Arial-Bold, min size 8.
  2. `txt_of(props)` rebuilds plain text from the `jsonText` DOM (concatenate string runs + bold children), falling back to `props["text"]`.
  3. `col(props,default)` converts a Balsamiq int color to RGB via `((v>>16)&255,(v>>8)&255,v&255)`.
  4. Open SQLite, load mockup, canvas = mockupW/H + 40, white RGB image.
  5. Sort controls by `zOrder`; scale with `S(v)=int(float(v)*scale)`.
  6. Per `typeID` draw: Canvas (rect), BrowserWindow (window + ~44px chrome + 3 traffic-lights + URL pill + title), Text (word-wrapped via `textlength`), TextInput, ComboBox (box + arrow polygon), CheckBox (box + green check if selected), Button (rounded rect + centered bold), HRule (line), Arrow.
  7. Arrow: read `p0/p1/p2`; if `loopRendering`, treat `p1` as 0-1 control point and sample a 21-step quadratic Bezier, else straight line; arrowhead polygon from `atan2` of the final segment (head L=11, +/-0.4 rad).
  8. Save PNG.
- **Key constants:** chrome ~44px; traffic-lights `(230,90,90)/(230,200,80)/(90,200,110)`; default text `(40,40,40)`; Bezier 21 samples; arrowhead L=11 +/-0.4; button radius 6; URL pill radius 4. 3-byte RGB (no alpha).
- **Gotchas:** intentional approximation to catch overlaps/off-canvas before the client PDF export - not a faithful render. Arrow `p1` MUST be a fraction of the bbox (matches wireframe_builder; code guards `if p1.x<=1`). Colors are ints -> bit-shift. Only branched typeIDs draw; unknown controls skipped silently.
- **Regeneration confidence:** High - self-contained PIL drawing off a known schema; per-widget fidelity is approximate by design.
