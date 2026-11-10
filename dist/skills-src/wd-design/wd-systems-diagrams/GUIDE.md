---
name: wd-systems-diagrams
description: >-
  Turn an integration inventory into system-LEVEL landscape diagrams - an executive
  integration landscape and per-workstream deep-dives - rendered as SVG, Draw.io, and PPTX.
  Use when the user says "systems diagram", "integration landscape", "architecture diagram",
  "draw.io of integrations", "exec integration overview", "broader landscape", "map our
  integrations", or wants a stakeholder-ready picture of how Workday (or any hub ERP) connects
  to external systems across a program. Runs a proven headless diagram-generation engine (no
  GUI/server needed) from an Excel/CSV tracker or a live Smartsheet. NOT for app-level Extend
  page flows or wireframes - that is wd-design-visuals.
---

# wd-systems-diagrams - program integration landscape diagrams (headless engine)

This skill generates **system-landscape** diagrams from an integration inventory. It bundles a
**proven headless diagram-generation engine (no GUI/server needed)** - `sfd_engine/` is the
`backend/core`, `backend/output`, `backend/config` of the SFD Agent desktop app (v3.3), copied
unchanged - and drives it with a small headless CLI. Do not rewrite the layout/render logic;
call the scripts.

## When to use / when NOT to
- **Use** for the *broader landscape*: how the hub ERP connects to many external systems across
  workstreams (an executive one-pager + one deep-dive per workstream).
- **Don't use** for a single Extend app's screen flow, wireframes, or swimlane process flow - those
  are **app-level** and belong to **wd-design-visuals**. This skill is **program/system-level**.

## Lifecycle neighbors

- **wd-smartsheet** - tracker transport (used by the live adapter).
- **wd-extend-dev** / **wd-integration-dev** - integration-naming / INT IDs that populate the tracker.
- **wd-design-doc** - the Broader Landscape section of the IDD (this skill produces the picture that goes there).
- **wd-design-visuals** - app-LEVEL screen flows / wireframes / swimlanes (this skill is program/system-level only; the reverse routing is on that skill).

## Two diagram modes (both produced every run)
- **Mode A - Executive Landscape:** 2-column workstream grid, hub centered, one node per system,
  per-workstream color coding.
- **Mode B - Workstream Deep-Dive:** hub on the left, vendor nodes on the right, orthogonal
  connectors, per-vendor color coding, labeled connector pills. One page per in-scope workstream.

**Connector labels carry the transmission method.** Each integration/connector can be tagged with how
it moves data - **SFTP / API / RaaS REST** (or TBD) - alongside its direction pill; show the method on
the connector so the picture answers "how", not just "what connects to what".

**Two-system interface variant (when the landscape is one hub + one external system):** instead of the
workstream grid, use two system boxes (each listing its in-scope **objects** as pills) with the
direction/method-labelled integration cards between them. A card can drill into an expandable
**source-steps -> INT -> target-steps** swimlane for that one integration - but that per-integration
swimlane is an **app/process-level** artifact owned by **wd-design-visuals** `process-flow.md`; this skill
draws the system-level picture and hands the step-level swimlane to that skill.

Details, palette tiers, formats, and layout constants: **[references/diagrams-and-brand.md](references/diagrams-and-brand.md)**.

## Two input paths
1. **File** - an Integration Tracker `.xlsx` or `.csv`.
2. **Live Smartsheet** - `scripts/smartsheet_adapter.py` reads a sheet via the wd-smartsheet helper
   and maps its columns onto the SFD schema (case-insensitive aliases, in-scope filter).

Input columns, aliases, and the Smartsheet mapping: **[references/input-schema.md](references/input-schema.md)**.

## How to run (headless - no GUI, no server)
```bash
# From a file (executive + per-workstream SVG + Draw.io + PPTX):
python scripts/generate_diagrams.py --input tracker.xlsx --formats svg,drawio,pptx --out ./out

# From a live Smartsheet, with a client brand palette:
python scripts/generate_diagrams.py --smartsheet <sheet-id> --client "<Client>" --out ./out
```
Key args: `--input <xlsx|csv>` **or** `--smartsheet <id>`; `--hub "<ERP>"` (default: auto-detect,
usually Workday); `--scope "In Scope"`; `--direction Inbound,Outbound,Bidirectional,Boomerang`;
`--formats svg,drawio,pptx`; `--client "<name>"` and/or `--palette "#hex,#hex"` for brand colors;
`--title-prefix`, `--description`, `--out <dir>`. The script prints every file it writes and also
bundles a timestamped `.zip`.

## Brand / palette
Pass `--client "<name>"` to auto-match a known brand palette, or `--palette "#1F4E79,#2E75B6"` to
seed one explicitly; the engine expands seeds into a legible 10-color palette. No palette -> the
engine's built-in default palette. See the brand reference for the three tiers.

## Prerequisites (Python deps)
`pandas`, `openpyxl` (Excel read), `networkx`, `pydantic` (engine models) - required.
`python-pptx` - only if `--formats` includes `pptx` (skips gracefully if absent).
Microsoft Edge or Google Chrome - only for the pictures on the PPTX diagram slides (python-pptx
cannot embed SVG, so each diagram is rendered to a PNG headless). Edge ships with Windows; set
`SFD_BROWSER` to point at another. Without one the deck still builds, with a note on those slides.
`requests`, `Pillow` - imported by the bundled logo module but **not exercised** headless (logo
lookup is intentionally skipped so this runs fully offline; nodes render as clean colored boxes).
Live Smartsheet path also needs the **wd-smartsheet** helper + a Smartsheet API token.

## Notes
- The engine under `scripts/sfd_engine/` is **bundled proven code from the SFD Agent v3.3** desktop
  app. This skill only adds headless glue (`generate_diagrams.py`) + the Smartsheet adapter. The
  engine ships as code and stays bundled; if the `scripts/` folder is ever missing or partial,
  regenerate it from the build-spec in **[references/scripts.md](references/scripts.md)** (it embeds
  the two glue files verbatim and specs every module). If the SFD Agent engine is updated, re-copy
  those three folders, then re-apply the local changes listed at the top of scripts.md (neutral
  brand constants; PPTX diagram pictures and headers) - a plain re-copy undoes them.
- Client-neutral: any real tracker id and its columns appear only as clearly-labeled examples in
  the references.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
