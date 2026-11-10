# Process flows - the 3-lane swimlane template + integration variant

## The standard template (apps with a UI)

Template file: the engagement's process-flow template (see **Engagement inputs** below). Builder: `process_flow_builder.py` (one geometry, two label sets: blank template + per-app instance) - **if it's not on your machine, regenerate it from the build-spec in [scripts.md](scripts.md)** rather than relying on a hardcoded `_Design Tools\` path.

Structure:
- **Header container "Extend Business Objects"** - the app's custom BOs as cylinders (`shape=cylinder3`), so reviewers see the data model at a glance before reading the flow.
- **Horizontal pool, 3 lanes:**
  1. **User** - actors (`shape=umlActor`) -> Action page -> Confirm page -> View All/My Data pages + admin Config page (amber page boxes `#FFE6A0` fill / `#D6B656` border)
  2. **Integration-API** - Workday API calls, RaaS reads, Integration Admin touchpoints, third-party note (orange note text)
  3. **BP-Approval** - legend, approval diamond (rhombus) -> Approved/Denied/Send-Back branches -> Status container of event BOs (`shape=process` boxes)
- Shaded rotated lane labels (`#EFEFEF`); bold title top-left: `<App> - Future-State Process Flow`; content-sized rounded legend.

Per-app instantiation: copy the template, rename actors/pages/BOs/BP branches to the app's real ones, add/remove page boxes to match the actual page list, keep the lane geometry. Every exchange the app makes appears as an arrow crossing a lane boundary - if the design doc's Data & Webservice Mapping has a row with no corresponding arrow, one of them is wrong.

**Lane count is per-app, not fixed at 3.** The 3-lane User / Integration-API / BP-Approval split is the default, but instantiate lanes to the app's actual role model. An app-owned-project model with distinct member/lead/admin actors (e.g. a task app) warranted a **4-lane** flow - Member / Lead / Admin / Integration. Add or split lanes to match who actually acts; keep the lane geometry and the Extend Business Objects header.

## Integration-only variant (O4I / no UI)

The 3-lane UI swimlane doesn't fit an integration with no screens. Build a tailored left-to-right flowchart instead: trigger (schedule/BP event/file arrival) -> retrieve -> transform/validate (with error-branch to the event log + notification) -> deliver/write -> summary/logging. Keep the Extend Business Objects header if the integration owns BOs; annotate each node with the concrete mechanism (RaaS report name, SOAP op, SFTP endpoint) in layperson terms. Precedent: a delivered integration-only (no-UI) flowchart.

## Rendering

Headless PNG export for design-doc embedding:

```bash
"/c/Program Files/draw.io/draw.io.exe" --force-device-scale-factor=1 --export --format png --scale 2 --border 20 --output out.png in.drawio
```

**`--force-device-scale-factor=1` is REQUIRED and must come BEFORE `--export`.** On a HiDPI / display-scaled Windows machine (device pixel ratio 2) the headless render doubles the content scale but sizes the canvas for the requested scale, so the PNG ends up cropped to the TOP-LEFT QUARTER of the diagram. The flag pins the device scale to 1 so content and canvas match. Do not drop it. (cache-dir "Access is denied" stderr noise is harmless; export still succeeds.)

(Embed on the design doc's Process Flow tab (wd-design-doc). Keep the .drawio next to the design doc as the editable source.)

**Re-embedding an updated PNG into an existing design-doc .xlsx** (without re-inserting the picture through Excel): the workbook stores diagram exports at `xl/media/imageN.png`. Find the right `N` via `xl/drawings/_rels/drawingX.xml.rels`, then zip-swap that entry with the new PNG. Do this BEFORE any Excel COM save, or the save rewrites the media and overwrites your swap.

**draw.io CLI is flaky from a cloud-synced (e.g. OneDrive) path.** The Electron single-instance lock renders once then refuses (silent no-op / stale output) on subsequent exports. Workaround: copy the `.drawio` source to a scratch dir, clear the draw.io lock / app-state, and run the export with absolute input and `--output` paths.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Process-flow template `.drawio`** - the engagement's 3-lane swimlane template. Obtain the branded template master per engagement, or use neutral formatting.
- **`_Design Tools\` path** - where the builder (`process_flow_builder.py`) lives on your machine; if absent, regenerate from the build-spec in [scripts.md](scripts.md).

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).

---

## Integration-only variant, refined: BAND BY OWNERSHIP (verified on a delivered design, 2026-08-06)

The "tailored left-to-right flowchart" above works, but when an integration has a **client-owned
step** (a pre-formatter, a partner transformation, an upstream ETL) the most valuable thing the
diagram can do is make that boundary unmissable. Organise the flow into horizontal **ownership
bands**, flow still reading left-to-right:

1. **SOURCE SYSTEM (client)** - any layout, any format
2. **PRE-FORMATTER (CLIENT-OWNED)** - the boundary. Show the mechanism OPTIONS side by side behind
   a "choose one" gateway bar, mark the recommended one, and add a callout listing what ANY option
   must produce. This is where reviewers otherwise assume the integration does the work.
3. **THE INTEGRATION (owned by us)** - numbered steps, each annotated with its concrete mechanism
4. **WORKDAY** - what lands, plus the platform's own event/message machinery
5. **ERROR HANDLING & NOTIFICATION** - which failures halt the run vs. reject a single row

Why it beats a plain flowchart: a reviewer's first question is "who does what", and bands answer it
before they read a single node. It also gave a natural home for the "the template never reads a
client's raw file" point that a linear flow kept burying.

Include a **"How to read this diagram"** note keyed to the band colours, and label failure paths
with dashed arrows. Keep the legend outside every frame.

## draw.io generation gotchas (each of these cost a rework cycle)

- **`whiteSpace=wrap` is REQUIRED on every `text;html=1` cell.** Without it a long note renders as
  one enormous single line and the exported canvas inflates to fit it - a 2,400px-wide diagram
  exported at 8,272px because of three unwrapped notes. Symptom: export dimensions far wider than
  your content bbox.
- **`\n` does NOT break a line when `html=1`.** Store `&lt;br&gt;` in the `value` attribute (a raw
  `<` is illegal in an XML attribute; it XML-decodes to `<br>`, which drawio renders). Escape the
  text first, THEN substitute newlines.
- **Container/band labels need `verticalAlign=top`.** A rounded-rect container centres its label by
  default, so member shapes sit on top of it and the band caption vanishes.
- **Route edges through dedicated CHANNELS, never box-to-box across a table of nodes.** A straight
  connector between non-adjacent boxes draws straight through the boxes between them and strikes
  out their text. Give each such edge explicit waypoints in a clear horizontal corridor below the
  row, and set `exitX/exitY` + `entryX/entryY` so it leaves and arrives where you intend.
- **Converging arrows strike through their own source labels.** Four source boxes arrowing into one
  document shape drew lines across three of the four labels. Collapsing them into a single box that
  lists the sources was both cleaner and more honest.
- **A constraint is not a flow step.** If a callout applies to ALL branches, give it no edges at all
  and title it "ALL OPTIONS MUST...". Wiring it produced three dashed edges across the option boxes.

### Export reliability

- **The draw.io CLI single-instance lock silently returns STALE output** on a second export in the
  same run - the second file was byte-identical to the first, same md5, same dimensions. Detect it
  by comparing hashes. Workaround: **split a multi-page `.drawio` into one file per page**, export
  each with absolute in/out paths, and kill `draw.io.exe` between runs.
- **Verify geometry programmatically before handing off**: parse the XML and check (a) nothing sits
  off-page, (b) no two content boxes overlap, (c) every node falls inside its intended band. That
  check caught real title/label collisions and a stray note. Then **still render and LOOK at it** -
  the geometry check passed on a diagram whose notes were unwrapped and running off-canvas.
