# Diagram modes, brand palette, formats & layout constants

Distilled from the SFD Agent v3.3 design (the engine this skill bundles). These describe how the
bundled generators behave - you drive them via `scripts/generate_diagrams.py`, you don't edit them.

## The two modes (both generated every run)

### Mode A - Executive Landscape (`svg/executive_landscape.svg`, page 1 of Draw.io/PPTX)
- 2-column **workstream quadrant** grid; each workstream gets its own tinted section.
- Hub ERP node centered in the gap between columns; one node per external system.
- **Per-workstream color coding** - every node + connector in a workstream shares one palette color,
  so the diagram reads as distinct colored sections (HCM = color 1, Financials = color 2, ...).
- Node fills use a 12% tint of the workstream color over white for a subtle on-brand wash.

### Mode B - Workstream Deep-Dive (`svg/workstream_<WS>.svg`, one page each)
- Hub on the **left**, vendor nodes in a grid on the **right**, orthogonal connector routing.
- **Per-vendor color coding** - each vendor's lines/pills/accents share one palette color.
- Single-line label pills (`ID  Name`) sit in the routing channels.

## Conditional legend
Legend entries appear **only when the data warrants**: the "^ gold ring = P1" entry shows only if a
visible integration is P1; the "dim = Deprecated" entry shows only if a system is Deprecated. The
Boomerang legend line uses the hub name (e.g. "(cycle) Boomerang (Workday->Workday)").

## Connector dash styles (Integration Type)
Each integration type gets a **unique** `stroke-dasharray` (EIB, Core Connector, Studio, API,
Orchestrate, RaaS, BIRT, SFTP, Custom, Real-time, ...). Spelling variants
("Orchestration"/"Orchestrations", etc.) are normalized. Types with no dash render solid.

## Brand palette - three tiers of control
1. **Auto-match** - `--client "<name>"` looks the name up in `config/color_suggestions.py`
   (`BRAND_COLORS`, ~70 universities / health systems / gov / F500). Match -> brand seeds.
2. **Explicit seeds** - `--palette "#1F4E79,#2E75B6"` supplies your own brand hexes.
3. **Auto-expand** - either way, `generate_vendor_palette(seeds, n=10)` expands seeds into 10 dark,
   legible-on-white connector colors via a 3-phase fill: (1) seeds clamped to a readable
   lightness/saturation range, (2) on-brand tints/shades of each seed, (3) hue-wheel rotation only
   if slots remain. No palette provided -> the engine's built-in default 10-color palette.

## Output formats
- **SVG** - `svg/executive_landscape.svg` + `svg/workstream_<WS>.svg` (one per workstream).
- **Draw.io** - one multi-page `<client>_Diagrams.drawio` (exec page + a page per workstream);
  imports directly into diagrams.net / Lucid; export to VSDX for Visio.
- **PPTX** - `<client>_Integration_Landscape.pptx`, a branded deck: title + validation-summary slides, one slide per diagram, appendix (~9 slides typical - see scripts.md; needs `python-pptx`). Tell the client "a branded deck," not "just the diagrams."
  - Each diagram slide shows a 2x PNG picture of that diagram's SVG, rendered by headless Edge or Chrome. It is a picture: edit diagrams in the draw.io file, not in the deck.
  - With no Edge or Chrome on the machine, those slides carry a note instead and the run prints a warning. Check for it before the deck goes to a client.
- Everything is also bundled into a timestamped `SFD_<client>_<ts>.zip` alongside a
  `validation_report.json` and `manifest.json`.

## Layout constants (from the engine, for reference)
| Constant | Value | Meaning |
|---|---|---|
| `EXEC_TITLE_H` | 110px | Executive canvas top margin (title + description + legend strip) |
| `WS_TITLE_PAD` | 134px | Workstream canvas top margin (title + description + 2-line legend box) |
| `WS_GAP_X` | 180px | Horizontal gap between vendor nodes |
| `WS_GAP_Y` | 80px | Minimum vertical gap between rows |
| `WS_HUB_GAP` | 150px | Gap between hub right edge and first vendor column |
| `_LINE_SPACING` | 34px | Spread between parallel lines to the same vendor |

## Headless differences vs the desktop app
- **Logo lookup (Stage 3) is skipped** - runs fully offline; nodes are clean colored boxes instead
  of logo-filled boxes. (The desktop app fetches vendor logos over the network.)
- **All in-scope workstreams** are rendered by default (no interactive gate); narrow with `--scope`
  and `--direction`. Everything else - layout, coloring, dash styles, legend logic - is identical
  proven code.
