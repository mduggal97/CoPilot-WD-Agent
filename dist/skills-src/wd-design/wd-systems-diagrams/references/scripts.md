# Scripts this skill uses - regenerate-on-demand build-spec

**The engine ships in `scripts/`.** Unlike the other wd-* skills, this skill *bundles* its
generators as code (`scripts/sfd_engine/` = the `backend/core`, `backend/output`, `backend/config`
of the SFD Agent v3.3 desktop app, plus two headless glue files). The engine is
plain Python and - now that all client references have been neutralized - shareable, so it stays in
the folder rather than being regenerated on every run.

**Local changes vs SFD Agent v3.3 - re-apply them after any re-copy.** The engine was copied
unchanged except for these; a fresh copy from an SFD Agent checkout silently undoes them:

1. **Neutral brand constants** - `config/brand.py` names its colours `BRAND_PRIMARY`,
   `BRAND_ACCENT`, `BRAND_PRIMARY_LIGHT` and carries a neutral palette (the original used another
   firm's names and colours); its 4 importers use the new names, and the PPTX footer names no firm.
2. **Diagram pictures and slide headers in the PPTX** (2026-11-03) - new `output/svg_raster.py`
   renders each SVG to a PNG with a headless Edge/Chrome; `output/pptx_generator.py` embeds that
   picture (python-pptx cannot embed SVG, so every diagram slide used to show an
   "SVG export available in ZIP" text box) and draws every slide header with one `_add_header()`,
   subtitle right-aligned inside the bar (it used to straddle the bar's lower edge and get cut off).

**If the `scripts/` folder is missing or partial, regenerate it from this spec.** The two small
glue files (`generate_diagrams.py`, `smartsheet_adapter.py`) are embedded **verbatim** below and can
be pasted back exactly. The larger generator modules are given as detailed specs (algorithm + key
data structures + constants) - enough to rebuild behavior-for-behavior. Prefer re-copying the three
`sfd_engine/` folders from a known-good SFD Agent checkout when one is available; use the specs only
when it is not.

Setup / Python prerequisites: `wd-extend-lifecycle/references/prerequisites.md` (and SKILL.md).
Cross-references: `diagrams-and-brand.md` (palette tiers, layout constants, formats),
`input-schema.md` (tracker columns + Smartsheet aliases).

**For branded output, use neutral formatting (no firm brand skill is installed).** The bundled `config/brand.py` and
`config/diagram_config.yaml` carry a built-in neutral default palette; pass `--client`/`--palette`
to override per run. Never hardcode a firm's brand hexes or name into the engine - a client look is
a per-run palette.

---

## Module tree

```
scripts/
+-- generate_diagrams.py          # ENTRYPOINT - headless CLI; wires the pipeline (glue, verbatim below)
+-- smartsheet_adapter.py         # live Smartsheet -> SFD-schema CSV (glue, verbatim below)
+-- sfd_engine/                   # bundled engine package (put THIS dir on sys.path, not its parent)
    +-- config/
    |   +-- brand.py              # palette, workstream colors, node sizing, edge dash styles
    |   +-- color_suggestions.py  # brand-name -> hex lookup + vendor-palette generator
    |   +-- diagram_config.yaml   # default run config (scope suggestions, logo tiers, ws order)
    +-- core/
    |   +-- models.py             # pydantic data objects (System, Integration, LayoutResult, ...)
    |   +-- ingest.py             # Stage 1: parse xlsx/csv -> Integration/System objects
    |   +-- scope_discovery.py    # Stage 1b: discover/normalize scope values
    |   +-- validation.py         # Stage: pre-render validation checks -> ValidationReport
    |   +-- graph.py              # Stage 2: filter to visible integrations; networkx graph
    |   +-- layout.py             # Stage 4: compute node positions (executive + workstream)
    |   +-- logo_lookup.py        # Stage 3: 3-tier logo resolver (SKIPPED in headless mode)
    +-- output/
        +-- svg_generator.py      # SVG renderer (executive + per-workstream)
        +-- drawio_generator.py   # multi-page Draw.io XML renderer
        +-- pptx_generator.py     # 9-slide branded PPTX (python-pptx)
        +-- svg_raster.py         # SVG -> PNG via headless Edge/Chrome, for the PPTX diagram pictures
        +-- lucidchart_generator.py # LucidChart-import CSV (nodes+edges)
        +-- packager.py           # Stage 6: assemble timestamped ZIP + manifests
```

**Import convention (critical):** the engine's internal imports are `from core. ...`,
`from config. ...`, `from output. ...`. So `sfd_engine/` **itself** must be on `sys.path` (NOT its
parent). `generate_diagrams.py` does this: `sys.path.insert(0, <this dir>/sfd_engine)`.

## External dependencies (verified from actual imports)

- **pandas** - `core/ingest.py` (`import pandas as pd`; `read_csv`/`read_excel`).
- **openpyxl** - Excel read engine (`pd.read_excel(..., engine="openpyxl")`). Required for `.xlsx`.
- **pydantic** - `core/models.py` (`BaseModel`, `Field`). All data objects.
- **networkx** - `core/graph.py` (`import networkx as nx`) and imported by `layout` path.
- **python-pptx** - `output/pptx_generator.py` (`from pptx import ...`). **Only** needed when
  `--formats` includes `pptx`; the entrypoint imports it lazily and skips gracefully if absent.
- **Microsoft Edge or Google Chrome** (any Chromium browser) - `output/svg_raster.py`, only for the
  pictures on the PPTX diagram slides. Found at its standard install path or on PATH; set
  `SFD_BROWSER` to a browser executable to override. Without one the deck still builds: each
  diagram slide carries a note and the run prints one warning.
- **requests** + **urllib3** (+ optional **certifi**) - `core/logo_lookup.py` only. NOT exercised
  headless (logo lookup is skipped; nodes render as clean colored boxes). Pillow is referenced in
  SKILL prereqs for the same logo path but is likewise not exercised.
- **PyYAML** (`yaml`) - only if a caller loads `diagram_config.yaml`; the headless entrypoint uses
  hardcoded defaults (`DEFAULT_WS_ORDER`, `DEFAULT_SCOPE_SUGGESTIONS`) instead of reading the YAML,
  so PyYAML is optional for the headless path.
- **svgwrite** - NOT used; the SVG generator emits XML via stdlib `xml.etree.ElementTree`. (Listed in
  the task's candidate-dep list for completeness; the actual renderer is `ElementTree`.)
- Stdlib: `argparse, sys, io, csv, re, math, logging, zipfile, json, datetime, colorsys, pathlib,
  collections.Counter, concurrent.futures, threading, enum, typing`.

The headless pipeline call sequence (what the entrypoint replicates from the desktop app's
`api/*.py`): **ingest -> validate -> scope/direction filter -> layout -> render -> package.**

---

## core/models.py - pydantic data objects (single source of truth for shapes)
- **Responsibility:** define every data object passed between stages. No logic beyond a couple of
  convenience properties.
- **Enums:** `Severity(HARD/SOFT/INFO)`, `Confidence(HIGH/MEDIUM/LOW/NA)`,
  `Direction(Inbound/Outbound/Bidirectional/Boomerang)`,
  `SystemCategory(Internal/External/Third-Party/Cloud/On-Premise)`,
  `SystemStatus(Active/Planned/Deprecated/TBD)`, `IntegrationPriority(P1/P2/P3)`,
  `DataSensitivity(PHI/PII/Financial/General)`.
- **Core objects:**
  - `System{system_id, system_name, system_category, business_domain, vendor_owner="",
    data_sensitivity="General", system_status="Active", notes=""}`
  - `Integration{integration_id, integration_name, source_system_id, target_system_id, direction,
    workstream, integration_type="", frequency="", data_classification="General", scope_status,
    priority="P3", go_live_wave="", notes="", vendor_system_category="External",
    ingest_errors=[]}`
  - `ValidationEvent{severity, row, message, check_name=""}`;
    `ValidationReport{errors[], warnings[], notices[]}` + `.has_hard_errors`, `.all_events()`.
  - `ScopeDiscovery{discovered_scopes[], value_counts{}, pre_selected[], single_value_notice,
    normalization_events[]}`.
  - Logo: `LogoEntry{system_id, system_name, resolved_domain, tier_used(1-4), confidence,
    source_url_or_path, cached_path, user_action, logo_data_url}`;
    `LogoManifest{entries: dict[system_id, LogoEntry]}` + `.get()`.
  - Layout: `NodePosition{x, y, width=120, height=60}`; `DiagramNode`, `DiagramEdge`;
    **`LayoutResult{nodes[], edges[], positions: dict[system_id, NodePosition], workstream|None}`**
    - the generators read **only** `.positions` (and `.workstream`).
  - Output config: `OutputFormats{pptx, lucidchart_csv, svg, drawio}`,
    `OutputOverlays{wave_badges, deprecated_highlighting, phi_pii_lanes(no-op)}`,
    `RunConfig{scope_filter[], selected_workstreams[], formats, overlays, title_prefix,
    client_name="Client", description, hub_system="Workday", vendor_palette[]}`.
  - Result envelopes (`IngestResult`, `LogoLookupResult`, `RenderResult`, `PackageResult`) - used by
    the desktop API, mostly unused headless.
- **Regeneration confidence:** High - pure schema. Keep field names/defaults exact; downstream code
  reads attributes by name.

## core/ingest.py - Stage 1: file -> objects
- **Responsibility:** read xlsx/csv bytes into a DataFrame; map real headers to logical fields via
  case-insensitive alias maps; build `Integration`/`System` objects; auto-derive systems when no
  systems file is given.
- **Key structures:** `SYSTEM_ALIASES` and `INTEGRATION_ALIASES` (logical field -> list of accepted
  lowercase header names). Constants `WORKDAY_HUB_ID="workday"`, `WORKDAY_INTERNAL_ID="workday_internal"`.
  `_DIRECTION_NORM` normalizes direction spellings; `_CATEGORY_CANONICAL` collapses vendor-category
  values (e.g. `Internal (Client Owned)` -> `Internal`); `_INTEGRATION_METHOD_VALUES` /
  `_SYSTEM_CATEGORY_VALUES` drive column disambiguation.
- **Key functions:**
  - `parse_integrations(content, filename) -> (list[Integration], col_map)` - the main entrypoint
    the CLI calls. Detects columns, runs `_disambiguate_vendor_type_col`, then **direction-inference
    mode**: when there is no explicit source/target column but there IS a single external-system
    column, it derives endpoints from `direction` + that column (Inbound -> ext->WD hub; Outbound ->
    WD hub->ext; Boomerang -> WD hub->internal pseudo-node; else ext->WD hub). Boomerang endpoints are
    forced to hub/internal and validated in explicit-column mode.
  - `parse_systems(...)` - parses an optional systems inventory; falls back to slugified name as ID.
  - `derive_systems_from_integrations(integrations) -> list[System]` - always includes the Workday
    hub; every unique external endpoint becomes a `System` with category by **majority vote** across
    the rows that reference it (`_best_category` prefers a non-"External" category on ties).
  - Helpers: `_read_file` (dtype=str, keep blanks, strip whitespace), `_detect_columns`,
    `_normalize_header`, `_slugify`, `_normalize_direction`, `_normalize_vendor_category`.
- **Inputs/outputs:** bytes + filename in; lists of pydantic objects + column-mapping dict out.
  Logging via `logging.getLogger("ingest")`.
- **Regeneration confidence:** High for logic; the alias lists are broad and tuned - preserve them
  (they are the client-neutrality mechanism). See `input-schema.md`.

## core/scope_discovery.py - Stage 1b: scope values
- **Responsibility:** find the distinct scope values in the data and decide which to pre-select.
- **Functions:** `discover_scopes(integrations, suggestions, case_sensitive=False) ->
  (ScopeDiscovery, warnings)` - collects non-blank scope values (title-cased unless case-sensitive),
  counts frequency, sorts by count desc then A-Z, cross-references the suggestion list for
  `pre_selected`, auto-selects when only one value exists, emits INFO warning at >=8 distinct values
  (likely wrong column), SOFT warnings for blank rows. `apply_scope_normalization(integrations)` -
  returns copies with `scope_status` title-cased.
- **Regeneration confidence:** High.

## core/validation.py - pre-render checks -> ValidationReport
- **Responsibility:** warn (never block, in headless) on data-quality issues.
- **Checks:** system_id uniqueness (HARD); ingest-time errors surfaced (HARD); integration_id
  uniqueness **within the same scope value** (HARD in-scope / SOFT out-of-scope); placeholder IDs
  matching `^int[-_]?x+$` (HARD if in-scope); self-reference (skip Boomerang); blank/placeholder
  vendor names (`^(n/?a|tbd?|tbc|blank|unknown|none|-)$`); direction enum; workstream enum (SOFT ->
  Technical); deprecated systems (SOFT, render at 50% opacity); system_name >28 chars (SOFT,
  truncated); PHI/PII-vs-General sensitivity mismatch (INFO). Deferred rows are skipped everywhere.
- **Regeneration confidence:** High - keep the two regexes and the valid-value sets exact.

## core/graph.py - Stage 2: filtering + networkx graph
- **Responsibility:** produce the visible integration set and (for API parity) a networkx graph.
- **Functions:** `get_visible_integrations(integrations, scope_filter, workstream_filter,
  direction_filter=None)` - **the function the CLI actually uses**; filters by scope  in  filter and
  workstream  in  filter, optionally by direction. `build_graph(...)` -> `nx.DiGraph` (nodes=systems,
  edges=integrations, self-edges dropped). `get_workstream_graph`, `count_by_workstream`,
  `zero_result_breakdown` (explains a 0-visible result by scope/workstream). Requires **networkx**.
- **Regeneration confidence:** High.

## core/layout.py - Stage 4: node positions
- **Responsibility:** compute `NodePosition`s for both diagram modes. Returns `LayoutResult`
  (generators read only `.positions`).
- **Key constants:** executive - `EXEC_COLS=5`, gaps `EXEC_GAP_X=22`, `EXEC_GAP_Y=18`, paddings
  `EXEC_PAD_X=50`, `EXEC_PAD_TOP=62`, `EXEC_PAD_BOT=35`, `EXEC_H_GAP=210` (center gap holding hub),
  `EXEC_V_GAP=90`, `EXEC_TITLE_H=110`, `HUB_R=90`, canvas `EXEC_W=1600`/`EXEC_H=900`. Workstream -
  `WS_HUB_W=210`, `WS_HUB_H=90`, `WS_GRID_COLS=3`, `WS_GAP_X=180`, `WS_GAP_Y=80`, `WS_TITLE_PAD=134`,
  `WS_HUB_MARGIN=60`, `WS_HUB_GAP=150`, `WS_OUTER_PAD=60`, `WS_W=1300`, `_LINE_SPACING=34` (**must
  match** `svg_generator._WS_LINE_SPACING`). Node size from `config.brand`: `NODE_W=170`, `NODE_H=75`.
- **`compute_executive_layout(systems, visible, ws_order)`:** assign each non-hub node to a
  workstream by majority vote; arrange workstreams in a **2-column grid** of sections (each section a
  `_region_dims`-sized box, <=5 node columns), place the Workday hub in the center gap between the
  two columns vertically centered on the total content height. Boomerang pseudo-node excluded from
  the hub slot.
- **`compute_workstream_layout(systems, integrations, workstream)`:** hub on the LEFT (height
  stretches to match the vendor grid), vendor nodes in a `WS_GRID_COLS`-column grid on the RIGHT.
  Per-row gaps are sized by the busiest node's integration count so parallel connector lines
  (spaced `_LINE_SPACING` apart) don't overlap - `_row_gap(row)` = `max(WS_GAP_Y, (max_n-1)*34+20)`.
  `_find_hub_id` picks the hub by: exact name "Workday" -> exact id "workday" -> category/name
  startswith Workday -> id substring "workday".
- **Regeneration confidence:** High but geometry-sensitive - preserve the constants and the
  `_LINE_SPACING`<->`_WS_LINE_SPACING` coupling, or lines and pills misalign.

## core/logo_lookup.py - Stage 3: 3-tier logo resolver (headless SKIPS this)
- **Responsibility:** resolve a logo per system (Tier 1 Clearbit `logo.clearbit.com`, Tier 2 Google
  faviconV2 via `t0.gstatic.com`, Tier 3 fuzzy filename match against a user ZIP, Tier 4 category
  fallback). Runs `_MAX_WORKERS=8` threads; Clearbit fast-fails after 5 consecutive failures.
- **Headless note:** the CLI passes an **empty `LogoManifest`** and never calls `run_logo_lookup`, so
  this module (and `requests`/`urllib3`/`Pillow`/`certifi`) is imported-but-not-exercised. Nodes
  render as clean colored boxes. Keep the module present so imports resolve, but regeneration of its
  network internals is not required for the headless skill to work.
- **(!) Third-party-mark provenance (if logo lookup IS enabled):** Tiers 1-2 fetch vendor **logos/trademarks**
  from Clearbit / Google favicons and embed them into the generated diagram. Those third-party marks then ride
  in any diagram distributed externally, under those providers' terms. For a client-facing/shared deliverable,
  confirm logo-usage rights, OR run headless (logos disabled - the default) / Tier 3 with a cleared logo set.
  This is the runtime-embedded case of the third-party-asset clearance gate (wd-extend-lifecycle quality-gates.md).
- **Regeneration confidence:** Medium and unnecessary for headless - a stub returning an empty
  manifest keyed by system_id is sufficient if rebuilding minimally.

## config/brand.py - palette, colors, sizing, edge styles
- **Responsibility:** built-in default (neutral) visual constants. `BRAND_PRIMARY=#1F3A5F`, `BRAND_ACCENT=#8EB8E5` (it sits on the primary colour, so it is light: 5.5:1 contrast),
  `BRAND_PRIMARY_LIGHT=#C9D6E3`, `BRAND_WHITE=#FFFFFF`,
  plus per-workstream `WS_COLORS` (fill/stroke/text for HCM, Financials, SCM, Sponsored Projects,
  Technical) with `ws_color(ws)` fallback to Technical. `TYPE_DASH` maps integration type -> SVG
  `stroke-dasharray` (EIB solid, Core Connector `3,3`, Studio `8,4`, API `2,5`, RaaS `6,3,1,3`,
  Orchestrate `9,3,2,3`, BIRT `12,3`, ...) resolved through `_INT_TYPE_ALIASES` via `edge_dash(type)`.
  `NODE_W=170`, `NODE_H=75`; `FONT_FAMILY="Arial"`; `P1_GOLD=#F4A700`; `WAVE_COLORS`; `CONF_COLORS`.
- **Note:** these are the engine's *default* look; for per-run brand palettes pass
  `--client`/`--palette` (see `color_suggestions.py`).
- **Regeneration confidence:** High - a constants table.

## config/color_suggestions.py - brand lookup + vendor-palette generator
- **Responsibility:** map an org name to seed brand hexes, and expand any seed list into exactly `n`
  (default 10) legible connector-line colors.
- **`BRAND_COLORS`:** lowercase org-name -> ordered hex list (universities, health systems,
  government, common corporates). Includes a **generic `example org` / `example organization`** entry
  (`#1F4E79, #2E75B6, #548235, #9E3B3B`) demonstrating the multi-color shape - swap in real colors as
  needed. `suggest_colors(name)` normalizes then tries exact then substring match.
- **`generate_vendor_palette(seeds, secondary_hex=None, n=10)`:** three-phase fill - (1) clamp seed
  colors to a readable-on-white HLS range (`_clamp`: lightness 0.18-0.42, sat >=0.40, near-gray kept
  dark); (2) tints/shades of seeds via `SHADE_STEPS=[+/-0.07,+/-0.14,+/-0.20]`; (3) hue-wheel rotation from
  the primary seed hue; (4) pad. Keeps colors >=`DISTINCT=0.12` RGB-Euclidean apart. Helpers:
  `_hex_to_hls`, `_hls_to_hex`, `_rgb_dist`, `_normalize_name`.
- **Regeneration confidence:** High - self-contained; the `BRAND_COLORS` table is illustrative and
  extensible.

## config/diagram_config.yaml - default run config
- Keys: `brand.{primary_color,accent_color,logo_path}`; `scope.{scope_include_suggestions:[In Scope,
  In-Scope], scope_blank_action:warn, scope_case_sensitive:false}`; `logo.*` (Clearbit/favicon tiers,
  cache paths); `layout.{workstream_order:[HCM,Financials,SCM,Sponsored Projects],
  node_label_max_chars:28, edge_label_max_chars:38}`; `output.{formats, diagram_title_prefix,
  output_directory}`; `overlays.{wave_badges, deprecated_highlighting, phi_pii_lanes:false}`. The
  headless CLI hardcodes equivalents (`DEFAULT_WS_ORDER`, `DEFAULT_SCOPE_SUGGESTIONS`) rather than
  reading this file, so it is documentation/override surface, not a hard dependency.

## output/svg_generator.py - SVG renderer (largest module, ~1440 lines)
- **Responsibility:** render both diagrams to SVG using stdlib `xml.etree.ElementTree` (no svgwrite).
- **Entrypoints:**
  - `generate_executive_svg(systems, visible_integrations, layout, logo_manifest, workstream_order,
    title_prefix="", description="", hub_system="Workday", vendor_palette=None) -> bytes`
  - `generate_workstream_svg(ws, systems, integrations, layout, logo_manifest,
    overlays_wave_badges=True, overlays_deprecated=True, title_prefix="", description="",
    hub_system="Workday", vendor_palette=None) -> bytes`
- **Algorithm (executive):** size the canvas from actual position extents (+`CANVAS_PAD=60`); draw a
  tinted section background + label per workstream; draw the hub box centered; draw each vendor node
  via `_node_rect` (logo-as-fill with a colored name-footer when a HIGH/MEDIUM logo exists, else a
  clean colored box; `_palette_tint` lightens the workstream/palette color for the fill); draw
  aggregated edges hub<->node with an **obstacle-avoiding orthogonal router** (`_route_avoiding_obstacles`
  on an `_ROUTE_GRID=18` px grid) and arrow markers (`_arrow_marker`), clipping endpoints to node
  rects (`_clip_to_rect`).
- **Algorithm (workstream):** hub on the left, vendors on the right; one **colored line per
  integration** with a two-line label pill (`_route_ws_line`/`_route_ws_connector`); parallel lines to
  the same vendor are stacked `_WS_LINE_SPACING=34` px apart (must match layout). Deprecated systems
  at reduced opacity; optional wave badges.
- **Key structures/constants:** `_VENDOR_COLORS` (10 deep, distinct hexes: `#1565C0 #C62828 #2E7D32
  #E65100 #6A1B9A #00695C #AD1457 #4527A0 #827717 #00838F`), `_ROUTE_GRID=18`, `_WS_LINE_SPACING=34`,
  font sizes `FS_NODE_LABEL=13`/`FS_EDGE_LABEL=11`. Helpers: `_svg_root`, `_truncate`, `_split_label`,
  `_hub_node`, `_node_rect`, `_logo_data_url`. `vendor_palette` (from `--client`/`--palette`) overrides
  `_VENDOR_COLORS`/workstream colors when supplied.
- **Regeneration confidence:** Medium - behavior is fully specified but this is the most geometry- and
  routing-heavy module. Prefer re-copying from a good checkout; if rebuilding, get `_clip_to_rect`,
  the orthogonal router, and the `34` px line-spacing coupling right first.

## output/drawio_generator.py - multi-page Draw.io XML (~870 lines)
- **Responsibility:** emit a single `.drawio` (mxGraph XML) with an **Executive** page + one page per
  active workstream, editable in diagrams.net / draw.io desktop (and exportable to VSDX for Visio).
- **Entrypoint:** `generate_drawio_xml(systems, visible_integrations, exec_layout,
  workstream_layouts, logo_manifest, workstream_order, title_prefix="", description="",
  hub_system="Workday", vendor_palette=None) -> bytes`.
- **Algorithm:** build `<mxfile>` with one `<diagram>`/`<mxGraphModel>` per page (`_add_page` with an
  id generator). Majority-vote each non-hub node to a workstream for exec-page coloring; when a
  `vendor_palette` (>=2 colors) is given, assign one palette color per workstream (`_dxo_exec_ws_color`)
  and tint node fills with `_dxo_tint` (alpha-blend over white at 0.12). Emit vendor nodes
  (`_add_vendor_node`) and hub nodes (`_add_hub_node`) as mxCells with geometry from the
  `LayoutResult.positions`; emit edges (`_add_edge`/`_add_exec_line`) with `_edge_style` derived from
  workstream stroke + `edge_dash(type)` + direction (bidirectional arrows), plus label pills
  (`_add_label_pill`) and text cells (`_add_text_cell`). Workstream pages route edges via
  `_ws_route_edges`/`_channel_y`. Shares `_VENDOR_COLORS` and `_WS_LINE_SPACING=34` with the SVG
  generator.
- **Helpers:** `_hex`, `_esc`, `_trunc`, `_geom`, `_is_workday`, `_vendor_node_value`,
  `_hub_node_value`.
- **Regeneration confidence:** Medium - the mxGraph cell/geometry/style grammar must be exact for the
  file to open. Re-copy when possible.

## output/pptx_generator.py - 9-slide branded PPTX (~360 lines)
- **Responsibility:** assemble a stakeholder deck embedding the SVGs. **Requires python-pptx** (lazy
  import; skipped if absent).
- **Entrypoint:** `generate_pptx(systems, visible_integrations, exec_svg, workstream_svgs,
  validation_report, run_config, workstream_order) -> bytes`. Slides: (1) title (brand background,
  accent bar, stats row: #systems/#integrations/#workstreams/scope filter, confidential footer); (2)
  Executive Landscape; (3-7) one per workstream in `workstream_order` present in `workstream_svgs`;
  (8) Validation Summary (counts + top-20 events table); (9) Appendix (first 40 integrations table).
- **Key details:** `SLIDE_W=13.33"`, `SLIDE_H=7.5"` (16:9). `_parse_svg_dimensions` reads viewBox to
  size embedded pictures aspect-preserving (fallback `1800x1200`). `_add_diagram_slide` gets a PNG
  of the SVG from `svg_raster.render_svg_png` and embeds it in the content area (0.25"/0.75",
  max 12.83" x 6.5", centred); with no PNG it adds a centred note giving the reason, and returns
  that reason so `generate_pptx` prints one warning for the run. `_add_header(slide, title,
  subtitle="")` draws every content slide's header: a 0.65" bar, the title left (16pt bold, wraps,
  two lines fit) and the optional subtitle right-aligned in a 4.2" block (9pt), both boxes the full
  bar height and centred vertically. Brand colors from `config.brand` (`BRAND_PRIMARY`,
  `BRAND_ACCENT`, `BRAND_PRIMARY_LIGHT`, `WS_COLORS`); `_hex_to_rgb`, `_set_cell_text` helpers.
  The title-slide footer reads `CONFIDENTIAL - For Internal Use Only` and names no firm.
- **Regeneration confidence:** High - linear python-pptx construction; keep slide order, the
  SVG-dimension parse, and the header geometry.

## output/svg_raster.py - SVG to PNG for the PPTX (~130 lines)
- **Responsibility:** turn one SVG into a PNG picture for a slide, faithfully. python-pptx takes
  raster images only. A light rasterizer is not enough: PyMuPDF (tried 2026-11-03) drew the
  connectors solid (the dash pattern encodes the integration type), dropped the arrowheads (the
  direction), drew the `#RRGGBBAA` drop shadows solid black and fell back to a serif font.
- **Entrypoint:** `render_svg_png(svg, width, height, scale=2, timeout=60) -> (png_bytes | None,
  reason)`. `find_browser()` (cached) checks `SFD_BROWSER`, then the standard Edge/Chrome install
  paths on Windows and macOS, then PATH (`msedge`, `google-chrome`, `chromium`, ...).
- **Algorithm:** write the SVG to a fresh temp folder; run the browser with `--headless=new`, a
  throwaway `--user-data-dir` in that folder, `--window-size` = the SVG's size,
  `--force-device-scale-factor=scale` and `--screenshot`. On Windows `msedge.exe` is a launcher that
  returns at once while a child writes the file 1-2 s later, so wait (up to `timeout`) for a
  COMPLETE PNG - one ending in the IEND chunk - then check its pixel size is exactly
  `width*scale x height*scale` (read from the PNG header; no Pillow). Any other size returns None:
  no picture beats a cropped one. Remove the temp folder, retrying for up to 5 s while the
  browser's children let go of the profile.
- **Regeneration confidence:** High - one subprocess call plus a wait loop; keep the
  complete-file wait and the exact-size check.

## output/lucidchart_generator.py - LucidChart-import CSV
- **Responsibility:** emit a LucidChart "Import Data" CSV (`LUCIDCHART_COLUMNS`: Id, Name, Shape
  Library, Shape, Width, Height, Fill/Stroke/Text Color, Font Size, Label, Source, Destination, Line
  Style). One node row per active endpoint (Workday = brand fill; deprecated = gray), one edge row
  per integration (stroke/text from `ws_color`, `dashed/solid` + `;bidirectional` from
  `edge_dash`/direction). `generate_lucidchart_csv(systems, integrations, exec_layout,
  workstream_layouts) -> bytes`. **Note:** the headless CLI does not currently emit this format
  (`lucidchart_csv=None` in the packager), but the module is retained.
- **Regeneration confidence:** High.

## output/packager.py - Stage 6: ZIP + manifests
- **Responsibility:** bundle everything into `SFD_<client>_<UTCstamp>.zip`.
- **`assemble_zip(client_name, pptx_bytes, lucidchart_csv, exec_svg, workstream_svgs, drawio_bytes,
  validation_report, logo_manifest, visible_integrations, run_config) -> (bytes, filename)`** - writes
  (when present) the PPTX, LucidChart CSV, `.drawio`, `svg/executive_landscape.svg` +
  `svg/workstream_<ws>.svg`, `validation_report.json`, `logo_manifest.json`, and a run `manifest.json`
  (generated_at, client, scope filter, workstreams, counts, formats, overlays). Filename is sanitized
  to alnum/`-`/`_`.
- **Regeneration confidence:** High.

---

## Verbatim glue file 1 - `scripts/generate_diagrams.py`

```python
#!/usr/bin/env python
"""
generate_diagrams.py - HEADLESS system-landscape diagram generator.

WHAT THIS IS (plain English)
----------------------------
The Systems Flow Diagram (SFD) Agent is normally a Windows desktop app: a
FastAPI backend + React UI that walks you through 6 gates and spits out
stakeholder-ready diagrams (executive integration landscape + per-workstream
deep-dives) as SVG, Draw.io and PPTX. This script runs that SAME proven
engine with NO GUI and NO web server - you point it at an Integration Tracker
(Excel/CSV, or a live Smartsheet) and it writes the diagrams straight to a
folder + a zip.

The layout and rendering code under `sfd_engine/` is bundled, unmodified,
from the SFD Agent v3.3 desktop app (backend/core, backend/output,
backend/config). This file only replicates the small amount of "glue" that
the app's api/*.py endpoints did - the exact call sequence:

    ingest -> validate -> scope/direction filter -> layout -> render -> package

HOW THE PIPELINE IS WIRED HEADLESS
----------------------------------
  1. core.ingest.parse_integrations(bytes, filename)   -> integrations
  2. core.ingest.derive_systems_from_integrations(...)  -> systems (no separate
     systems file needed; categories inferred by majority vote)
  3. core.scope_discovery.apply_scope_normalization / discover_scopes
  4. core.validation.run_validation                     -> report (warn, don't die)
  5. hub auto-detect (most-frequent endpoint) unless --hub given
  6. core.graph.get_visible_integrations(scope, ws, direction)  -> visible
  7. core.layout.compute_executive_layout / compute_workstream_layout
     (these return LayoutResult.positions, the ONLY field the generators read)
  8. output.svg_generator / drawio_generator / pptx_generator
  9. output.packager.assemble_zip  -> timestamped .zip

Logo lookup (the desktop app's Stage 3, which hits the network) is SKIPPED -
we pass an empty LogoManifest so this runs fully offline. Nodes render as
clean colored boxes instead of logo-filled boxes.

USAGE
-----
  python generate_diagrams.py --input tracker.xlsx --formats svg,drawio,pptx --out ./out
  python generate_diagrams.py --input tracker.csv  --hub "Oracle Fusion" --scope "In Scope"
  python generate_diagrams.py --smartsheet <sheet-id> --client "Example Health System" --out ./out

Requires (see SKILL.md prerequisites): pandas, openpyxl, networkx, pydantic,
python-pptx (only if pptx requested), Pillow + requests (imported by the
bundled logo module but not exercised here).
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

# --- Make the bundled engine importable as top-level packages -----------------
# The engine's internal imports are `from core.  / from config.  / from output.`
# so the `sfd_engine` directory itself must be on sys.path (NOT its parent).
_ENGINE_DIR = Path(__file__).resolve().parent / "sfd_engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from core.ingest import parse_integrations, derive_systems_from_integrations  # noqa: E402
from core.scope_discovery import discover_scopes, apply_scope_normalization    # noqa: E402
from core.validation import run_validation                                     # noqa: E402
from core.graph import get_visible_integrations                                # noqa: E402
from core.layout import compute_executive_layout, compute_workstream_layout    # noqa: E402
from core.models import LogoManifest                                           # noqa: E402
from output.svg_generator import generate_executive_svg, generate_workstream_svg  # noqa: E402
from output.drawio_generator import generate_drawio_xml                        # noqa: E402
from output.packager import assemble_zip                                       # noqa: E402
from config.color_suggestions import suggest_colors, generate_vendor_palette   # noqa: E402

# Default workstream ordering (mirrors the desktop app's DEFAULT_WS_ORDER).
DEFAULT_WS_ORDER = ["HCM", "Financials", "SCM", "Sponsored Projects"]
DEFAULT_SCOPE_SUGGESTIONS = ["In Scope", "In-Scope", "In Scope - Data Lake"]


# ---------------------------------------------------------------------------
# Input loaders
# ---------------------------------------------------------------------------
def _load_file(path: Path) -> tuple[bytes, str]:
    """Read an xlsx/csv Integration Tracker from disk -> (bytes, filename)."""
    if not path.exists():
        raise SystemExit(f"ERROR: input file not found: {path}")
    return path.read_bytes(), path.name


def _load_smartsheet(sheet_id: str) -> tuple[bytes, str]:
    """Pull a live Integration Tracker from Smartsheet -> (csv bytes, filename).

    Delegates to smartsheet_adapter, which reads the sheet via the wd-smartsheet
    helper and maps its columns onto the SFD input schema.
    """
    from smartsheet_adapter import fetch_tracker_csv  # local import - optional dep
    csv_text = fetch_tracker_csv(int(sheet_id))
    return csv_text.encode("utf-8"), f"smartsheet_{sheet_id}.csv"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------
def _detect_hub(systems, integrations) -> str:
    """Replicate api/ingest.py hub auto-detection: most-frequent endpoint's name."""
    counts: Counter = Counter()
    for i in integrations:
        if i.source_system_id:
            counts[i.source_system_id] += 1
        if i.target_system_id:
            counts[i.target_system_id] += 1
    if not counts:
        return "Workday"
    hub_sid = counts.most_common(1)[0][0]
    hub_sys = next((s for s in systems if s.system_id == hub_sid), None)
    return hub_sys.system_name if hub_sys else hub_sid


def _resolve_palette(client: str | None, palette_arg: str | None) -> list[str]:
    """Build the 10-color vendor palette from --palette hexes or a --client brand match."""
    if palette_arg:
        seeds = [h.strip() for h in palette_arg.split(",") if h.strip()]
        if seeds:
            return generate_vendor_palette(seeds)
    if client:
        seeds = suggest_colors(client)
        if seeds:
            return generate_vendor_palette(seeds)
    return []  # empty = engine uses its default (neutral) palette


def _ordered_workstreams(visible, order: list[str]) -> list[str]:
    """Workstreams present in the data, sorted by the preferred order then A-Z."""
    present = {i.workstream for i in visible if i.workstream}
    ranked = [w for w in order if w in present]
    ranked += sorted(w for w in present if w not in order)
    return ranked


def run(args) -> int:
    # 1. INGEST -------------------------------------------------------------
    if args.smartsheet:
        content, filename = _load_smartsheet(args.smartsheet)
    else:
        content, filename = _load_file(Path(args.input))

    integrations, col_map = parse_integrations(content, filename)
    if not integrations:
        raise SystemExit("ERROR: no integration rows parsed - check the file's columns "
                         "(need at least an ID column and an external-system column).")
    systems = derive_systems_from_integrations(integrations)
    integrations = apply_scope_normalization(integrations)

    # 2. VALIDATE (report only - headless never blocks on soft/hard warnings) --
    report = run_validation(systems, integrations)
    scope_disc, scope_warn = discover_scopes(integrations, DEFAULT_SCOPE_SUGGESTIONS)
    for ev in report.errors:
        print(f"  [validation:ERROR] {ev.row}: {ev.message}")
    for ev in (report.warnings + scope_warn)[:8]:
        print(f"  [validation:warn]  {ev.row}: {ev.message}")

    # 3. SCOPE + DIRECTION FILTER ------------------------------------------
    if args.scope:
        scope_filter = [s.strip().title() for s in args.scope.split(",") if s.strip()]
    elif scope_disc.pre_selected:
        scope_filter = scope_disc.pre_selected
    else:
        scope_filter = scope_disc.discovered_scopes  # nothing matched "In Scope" -> take all
    direction_filter = [d.strip().title() for d in args.direction.split(",")] if args.direction else []

    ws_order = list(DEFAULT_WS_ORDER)
    # Pre-filter visible set once to know which workstreams actually survive.
    pre_visible = get_visible_integrations(integrations, scope_filter,
                                           list({i.workstream for i in integrations}),
                                           direction_filter or None)
    selected_ws = _ordered_workstreams(pre_visible, ws_order)
    visible = get_visible_integrations(integrations, scope_filter, selected_ws,
                                       direction_filter or None)

    print(f"\n  Parsed {len(integrations)} integrations, {len(systems)} systems.")
    print(f"  Scope filter: {scope_filter or '(all)'}   Direction: {direction_filter or '(all)'}")
    print(f"  Workstreams: {selected_ws}")
    print(f"  Visible integrations after filters: {len(visible)}")
    if not visible:
        raise SystemExit("ERROR: 0 integrations left after filters - loosen --scope/--direction.")

    # 4. HUB ----------------------------------------------------------------
    hub_system = args.hub if args.hub else _detect_hub(systems, integrations)
    print(f"  Hub / ERP: {hub_system}")

    # 5. PALETTE ------------------------------------------------------------
    palette = _resolve_palette(args.client, args.palette)
    if palette:
        print(f"  Brand palette: {len(palette)} colors "
              f"({'--palette' if args.palette else 'brand match for ' + repr(args.client)})")

    # 6. LAYOUT -------------------------------------------------------------
    exec_layout = compute_executive_layout(systems, visible, ws_order)
    ws_layouts = {}
    for ws in selected_ws:
        ws_intgs = [i for i in visible if i.workstream == ws]
        if ws_intgs:
            ws_layouts[ws] = compute_workstream_layout(systems, ws_intgs, ws)

    # 7. RENDER -------------------------------------------------------------
    formats = {f.strip().lower() for f in args.formats.split(",") if f.strip()}
    manifest = LogoManifest()  # empty - no network logo lookup in headless mode
    title_prefix = (args.title_prefix.strip() + " ") if args.title_prefix.strip() else ""
    client_name = args.client or "Client"

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    svg_dir = outdir / "svg"
    written: list[Path] = []

    exec_svg = generate_executive_svg(
        systems=systems, visible_integrations=visible, layout=exec_layout,
        logo_manifest=manifest, workstream_order=ws_order,
        title_prefix=title_prefix, description=args.description,
        hub_system=hub_system, vendor_palette=palette,
    )
    ws_svgs: dict[str, bytes] = {}
    for ws in selected_ws:
        if ws in ws_layouts:
            ws_svgs[ws] = generate_workstream_svg(
                ws=ws, systems=systems, integrations=visible, layout=ws_layouts[ws],
                logo_manifest=manifest, overlays_wave_badges=False, overlays_deprecated=True,
                title_prefix=title_prefix, description=args.description,
                hub_system=hub_system, vendor_palette=palette,
            )

    if "svg" in formats:
        svg_dir.mkdir(exist_ok=True)
        p = svg_dir / "executive_landscape.svg"
        p.write_bytes(exec_svg); written.append(p)
        for ws, data in ws_svgs.items():
            p = svg_dir / f"workstream_{ws.replace(' ', '_')}.svg"
            p.write_bytes(data); written.append(p)

    drawio_bytes = None
    if "drawio" in formats:
        drawio_bytes = generate_drawio_xml(
            systems=systems, visible_integrations=visible, exec_layout=exec_layout,
            workstream_layouts=ws_layouts, logo_manifest=manifest,
            workstream_order=ws_order, title_prefix=title_prefix,
            description=args.description, hub_system=hub_system, vendor_palette=palette,
        )
        p = outdir / f"{_safe(client_name)}_Diagrams.drawio"
        p.write_bytes(drawio_bytes); written.append(p)

    pptx_bytes = None
    if "pptx" in formats:
        try:
            from core.models import RunConfig, OutputFormats
            from output.pptx_generator import generate_pptx
            run_config = RunConfig(
                scope_filter=scope_filter, selected_workstreams=selected_ws,
                formats=OutputFormats(pptx=True, svg=True, drawio="drawio" in formats),
                title_prefix=title_prefix, client_name=client_name,
                description=args.description, hub_system=hub_system, vendor_palette=palette,
            )
            pptx_bytes = generate_pptx(
                systems=systems, visible_integrations=visible, exec_svg=exec_svg,
                workstream_svgs=ws_svgs, validation_report=report,
                run_config=run_config, workstream_order=ws_order,
            )
            p = outdir / f"{_safe(client_name)}_Integration_Landscape.pptx"
            p.write_bytes(pptx_bytes); written.append(p)
        except ImportError as exc:
            print(f"  [pptx] SKIPPED - python-pptx not installed ({exc}). "
                  f"Install with: pip install python-pptx")

    # 8. PACKAGE ------------------------------------------------------------
    from core.models import RunConfig, OutputFormats
    zip_bytes, zip_name = assemble_zip(
        client_name=client_name,
        pptx_bytes=pptx_bytes, lucidchart_csv=None, exec_svg=exec_svg if "svg" in formats else None,
        workstream_svgs=ws_svgs if "svg" in formats else {},
        drawio_bytes=drawio_bytes, validation_report=report, logo_manifest=manifest,
        visible_integrations=visible,
        run_config=RunConfig(
            scope_filter=scope_filter, selected_workstreams=selected_ws,
            formats=OutputFormats(pptx=pptx_bytes is not None, svg="svg" in formats,
                                  drawio="drawio" in formats),
            title_prefix=title_prefix, client_name=client_name,
            description=args.description, hub_system=hub_system, vendor_palette=palette,
        ),
    )
    zip_path = outdir / zip_name
    zip_path.write_bytes(zip_bytes); written.append(zip_path)

    print("\n  WROTE:")
    for p in written:
        print(f"    {p}  ({p.stat().st_size:,} bytes)")
    print(f"\n  Done. {len(written)} files in {outdir}")
    return 0


def _safe(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Headless system-landscape diagram generator (SFD Agent engine, no GUI).")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="Path to an Integration Tracker .xlsx or .csv")
    src.add_argument("--smartsheet", help="Smartsheet sheet ID to pull the tracker live")
    p.add_argument("--hub", default="", help="Hub/ERP display name (default: auto-detect, e.g. Workday)")
    p.add_argument("--scope", default="", help="Comma list of Scope values to include (default: In Scope*)")
    p.add_argument("--direction", default="", help="Comma list: Inbound,Outbound,Bidirectional,Boomerang (default: all)")
    p.add_argument("--formats", default="svg,drawio", help="Comma list: svg,drawio,pptx (default: svg,drawio)")
    p.add_argument("--client", default="", help="Client/project name (also triggers brand palette lookup)")
    p.add_argument("--palette", default="", help="Comma list of brand hex seeds, e.g. '#002D72,#68ACE5'")
    p.add_argument("--title-prefix", dest="title_prefix", default="", help="Prefix for every diagram title")
    p.add_argument("--description", default="", help="Executive-overview description (blank = auto-generated)")
    p.add_argument("--out", default="./sfd_output", help="Output directory (default: ./sfd_output)")
    return p


if __name__ == "__main__":
    sys.exit(run(build_parser().parse_args()))
```

## Verbatim glue file 2 - `scripts/smartsheet_adapter.py`

```python
#!/usr/bin/env python
"""
smartsheet_adapter.py - pull an Integration Tracker LIVE from Smartsheet and
map its columns onto the SFD input schema the diagram engine understands.

WHAT THIS DOES (plain English)
------------------------------
A program's Smartsheet Integration Tracker has dozens of columns with
program-specific names (e.g. "Workday ID #", "Vendor / External Systems",
"Assigned To - Design"). The SFD engine needs a small, well-defined set of
fields (Scope, integration ID, name, direction, external system, workstream,
+ a few optional ones). This adapter:

  1. Reads the whole sheet via the wd-smartsheet REST helper (column-title dicts).
  2. Maps each real column onto an SFD field using a CASE-INSENSITIVE alias map
     (the same aliases the engine's own ingest uses, plus program-specific ones).
  3. Filters to in-scope rows (Scope contains "in scope").
  4. Emits a CSV string whose headers are the canonical SFD names, which
     `core.ingest.parse_integrations` then ingests unchanged.

It is import-safe with NO network: importing this module does nothing. Only
`fetch_tracker_csv(sheet_id)` touches Smartsheet, and `map_rows_to_sfd(rows)`
is pure and unit-testable offline.

REFERENCE SHEET (example, not hardcoded default)
------------------------------------------------
A typical program's integration tracker (e.g. a "Program Integration Tracker"
Smartsheet with several hundred rows) exposes columns like `Workday ID #`,
`Integration Name`, `Workstream`, `Scope`, `Assigned To - Design`. No sheet id
is hardcoded here - the caller passes the sheet id via `--smartsheet <sheet-id>`.
Real trackers vary; the alias map below is how we stay client-neutral.
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# SFD field -> accepted source column names (lower-cased, punctuation-normalized).
# The engine's ingest matches columns case-insensitively too; this map is a
# superset tuned for real Smartsheet integration trackers.
# ---------------------------------------------------------------------------
SFD_COLUMN_ALIASES: dict[str, list[str]] = {
    # --- required by the engine ---
    "Scope":                    ["scope", "scope status", "integration scope", "in scope", "include"],
    "Workday ID #":             ["workday id #", "workday id", "wd id", "integration id",
                                 "integration_id", "int id", "int #", "id"],
    "Integration Name":         ["integration name", "integration_name", "name",
                                 "legacy integration description", "description"],
    "Direction":                ["direction", "inbound/outbound", "flow direction", "flow",
                                 "integration direction"],
    "Vendor/External Systems":  ["vendor/external systems", "vendor / external systems",
                                 "vendor/external system", "external systems", "external system",
                                 "3rd party system", "vendor system", "non-workday system",
                                 "vendor application", "vendor name", "vendor", "external application",
                                 "sending/receiving system"],
    "Workstream":               ["workstream", "work stream", "module", "workday module", "domain"],
    # --- optional (enrich the diagram if present) ---
    "Integration Type":         ["integration type", "integration_type", "integration template name",
                                 "integration method", "connector type", "integration technology",
                                 "template"],
    "Vendor Type":              ["vendor type", "system type", "system category", "internal/external",
                                 "int/ext", "classification", "system classification"],
    "From System":              ["from system", "source system", "source", "from"],
    "To System":                ["to system", "target system", "target", "to"],
    "priority":                 ["priority", "integration priority", "p1/p2/p3"],
    "Workday Domain Area":      ["workday domain area", "domain area", "wd domain area", "go live wave",
                                 "wave", "go-live wave"],
    "Has PII Data?":            ["has pii data?", "has pii", "pii", "data classification",
                                 "data sensitivity", "sensitivity"],
    "frequency":                ["frequency", "freq", "schedule", "run frequency"],
    "notes":                    ["notes", "note", "comments", "comment"],
}

# Canonical output order (engine reads by header name, but stable order helps debugging).
SFD_OUTPUT_COLUMNS = list(SFD_COLUMN_ALIASES.keys())


def _norm(header: str) -> str:
    """Lower-case + collapse punctuation/whitespace so 'Workday ID #' == 'workday id  #'."""
    h = header.strip().lower()
    for ch in ("_", "-", "/", "\\", ".", ",", "(", ")"):
        h = h.replace(ch, " ")
    return " ".join(h.split())


def build_header_map(source_headers: list[str]) -> dict[str, str]:
    """Return {sfd_field: source_header} for every SFD field we can find.

    Case/punctuation-insensitive. First matching source header wins.
    """
    norm_to_original = {}
    for h in source_headers:
        norm_to_original.setdefault(_norm(h), h)

    mapping: dict[str, str] = {}
    for sfd_field, aliases in SFD_COLUMN_ALIASES.items():
        for alias in aliases:
            key = _norm(alias)
            if key in norm_to_original:
                mapping[sfd_field] = norm_to_original[key]
                break
    return mapping


def _is_in_scope(scope_val: str) -> bool:
    """True if the Scope cell reads as in-scope (covers 'In Scope', 'In-Scope', 'In Scope - Data Lake')."""
    s = (scope_val or "").strip().lower()
    return "in scope" in s or "in-scope" in s


def map_rows_to_sfd(rows: list[dict], *, in_scope_only: bool = True) -> list[dict]:
    """Pure transform: Smartsheet row-dicts (keyed by column title) -> SFD row-dicts.

    - Applies the alias map (via the first row's keys as the header set).
    - Optionally filters to in-scope rows.
    - Skips rows with no integration ID.
    """
    if not rows:
        return []
    header_map = build_header_map(list(rows[0].keys()))
    scope_src = header_map.get("Scope")
    id_src = header_map.get("Workday ID #")

    out: list[dict] = []
    for row in rows:
        if in_scope_only and scope_src is not None:
            if not _is_in_scope(str(row.get(scope_src, ""))):
                continue
        if id_src is not None and not str(row.get(id_src, "")).strip():
            continue  # no integration id -> not a real integration row
        sfd_row = {}
        for sfd_field in SFD_OUTPUT_COLUMNS:
            src = header_map.get(sfd_field)
            sfd_row[sfd_field] = "" if src is None else str(row.get(src, "")).strip()
        out.append(sfd_row)
    return out


def rows_to_csv(sfd_rows: list[dict]) -> str:
    """Serialize mapped SFD rows to a CSV string with canonical headers."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=SFD_OUTPUT_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for r in sfd_rows:
        writer.writerow(r)
    return buf.getvalue()


def fetch_tracker_csv(sheet_id: int, *, in_scope_only: bool = True) -> str:
    """LIVE: read the Smartsheet tracker and return SFD-schema CSV text.

    Imports the wd-smartsheet helper on demand so this module is import-safe
    without a token. The helper handles auth (env var / Credential Manager /
    .env) and pagination.
    """
    _add_smartsheet_to_path()
    from smartsheet_api import get_sheet  # noqa: E402  (optional dep, resolved at call time)
    _columns, rows = get_sheet(sheet_id)
    sfd_rows = map_rows_to_sfd(rows, in_scope_only=in_scope_only)
    if not sfd_rows:
        raise SystemExit(f"No in-scope integration rows mapped from sheet {sheet_id}. "
                         f"Check the sheet's Scope/ID columns against SFD_COLUMN_ALIASES.")
    return rows_to_csv(sfd_rows)


def _add_smartsheet_to_path() -> None:
    """Put the wd-smartsheet scripts dir on sys.path so `import smartsheet_api` works."""
    candidate = Path.home() / ".claude" / "skills" / "wd-smartsheet" / "scripts"
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))


if __name__ == "__main__":
    # Tiny self-test of the (offline) mapping logic - no network.
    sample = [
        {"Workday ID #": "INT001", "Integration Name": "Payroll Export",
         "Scope": "In Scope", "Direction": "Outbound",
         "Vendor / External Systems": "ADP", "Workstream": "HCM",
         "Assigned To - Design": "Jane Doe"},
        {"Workday ID #": "INT002", "Integration Name": "Legacy GL",
         "Scope": "Out of Scope", "Direction": "Inbound",
         "Vendor / External Systems": "Oracle GL", "Workstream": "Financials"},
    ]
    mapped = map_rows_to_sfd(sample)
    print("header map:", build_header_map(list(sample[0].keys())))
    print(f"in-scope rows: {len(mapped)} (expected 1)")
    print(rows_to_csv(mapped))
```

---

**Regeneration order if rebuilding from scratch:** `models.py` -> `config/brand.py` +
`color_suggestions.py` -> `ingest.py` -> `scope_discovery.py` -> `validation.py` -> `graph.py` ->
`layout.py` -> (`logo_lookup.py` stub) -> `svg_generator.py` -> `drawio_generator.py` ->
`svg_raster.py` -> `pptx_generator.py` -> `lucidchart_generator.py` -> `packager.py` -> the two glue
files above. Then
smoke-test: `python scripts/generate_diagrams.py --input references/sample-integration-tracker.csv
--formats svg,drawio --out ./_smoketest`.
