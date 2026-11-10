# Layout engine: content / layout / brand, calibrated from a reference

## Why this exists

The original formatting passes (`xlsx_brand_style`, `xlsx_balance_columns`, `xlsx_normalize_layout`,
`xlsx_normalize_borders`) are **structure-preserving**: they read the template's existing cells and
adjust width, height, fill, and border. They can *restyle* a tab but they cannot *re-lay-out* it -
they inherit the template's cell topology.

A human cleaning a tab does more than restyle. They:

- choose column widths by judgment (a "High Level" column wants room a one-word label does not),
- group related fields into aligned **panels**,
- **merge** cells into callouts,
- sometimes **author** structure that isn't in the template (File's third property panel - five
  labels that did not exist in the source).

Those are **layout** decisions, not styling decisions. Trying to infer them mechanically turned into
whack-a-mole: band-labelled columns, bled merges, lone-prose width, the File restructure - each a new
special case, and the output still landed at "better but short."

## The reframe: three separable concerns

| Layer | Owns | Lives in |
|---|---|---|
| **Content** | *What* information must appear (every field, table, prose block, callout) | the workbook cells (+ a coverage contract) |
| **Layout** | *How* it is arranged - column widths, panels, callouts, order, merges | a per-tab **layout spec** - a calibration, `templates/layouts/<slug>.json`, bound to ONE document |
| **Brand** | palette, type, logo, rules, spacing | the brand profile (`brands/<slug>.json`) |

Layout was previously welded to the template's incidental cell positions. Unwelding it - into an
explicit spec - is what gives freedom to arrange a page for a professional, readable result while
still covering all the information.

## How it works (hybrid: model-authored spec + deterministic engine)

1. **Calibrate from the reference.** `xlsx_extract_layout.py <hand-cleaned-copy> --tabs "..."
   --baseline <pre-style-backup> --write --calibration <doc-slug>` reads the author's cleaned copy
   and records, per tab, into `templates/layouts/<doc-slug>.json` -> `tab_layouts`:
   - `widths` - the author's chosen column widths (the single biggest miss);
   - `panel_merges` - the merges in the header band (a *record* of the panel/callout structure);
   - `structure` - the directives below (with `--baseline`).
   It also records `match` - the baseline's identity cells - so the calibration applies to this
   document and no other (see "A calibration belongs to one document" below).
2. **Apply deterministically.** `xlsx_apply_layout.py` is AUTHORITATIVE on column widths for spec'd
   tabs. It runs after `xlsx_balance_columns.py` (which SKIPS the tabs of the calibration matched
   to this workbook, so the generic balancer never fights the spec) and BEFORE
   `xlsx_normalize_layout.py`, so the uniform-to-worst-row height pass fits the authored widths.
3. **Brand renders.** The existing style / normalize / border passes paint fills, headers, rhythm and
   borders from the brand profile - unchanged, brand-agnostic.
4. **Render and look, then revise.** `render_tabs.py` is a per-engagement scratchpad harness (it is
   NOT bundled - it lives beside the doc it renders); when it isn't present, the canonical G18
   render path is the PyMuPDF one-liner in document-quality-gates.md (render each tab to PNG and
   look). Compare to the reference. The numbers only rank candidates - the render is the arbiter
   (gate G18).

For a NEW template with no hand-cleaned reference, the model authors the `widths` (and, later, richer
directives) from the design principles below instead of extracting them.

## A calibration belongs to one document (2026-10-17)

**What went wrong.** The Payroll Input reference's calibration lived in `templates/idd.json`, the
profile every script loads by default. So every workbook got it. On a freshly built IDD skeleton,
`xlsx_apply_structure.py` injected the reference's own prose into Question (D62:E63) and
WD Solution - O4I (H40:J55), plus seventy Report labels. Extend docs share three tab names with the
IDD (Overview, Requirements, Unit Testing), so they got its widths and a boxed `J7:J35` merge. Their
Unit Testing "Tested By" column went wide while "Expected Behavior" clipped. The coverage guard
passed throughout: injecting into an empty cell deletes nothing.

**Two kinds of fact had been welded together.**

- **Template-family facts** are true of every doc built from the template: which fill means band,
  sub-section or header (`roles`). They stay in `templates/<slug>.json`.
- **Calibration facts** are true of ONE document: its column widths, its merges, the text it moved or
  added at exact cells. They live in `templates/layouts/<doc-slug>.json`.

**The binding.**

- The template profile names its `identity_cells` - where a doc keeps its own ID and name. For the
  IDD that is `Overview!J8` (Integration ID) and `Overview!J9` (Integration Name), the cells the
  master's ISU/ISSG formulas build from.
- A calibration records their values as `match`. `scripts/xlsx_layout_match.py` gives each workbook
  the one calibration whose `match` equals its identity cells (whitespace-collapsed), or none.
- `xlsx_apply_layout.py`, `xlsx_apply_structure.py`, `xlsx_balance_columns.py` (which defers only
  the matched tabs) and `xlsx_normalize_layout.py` (which protects only the matched merges) all ask
  it, and each prints its verdict, so every step's log says whether a calibration ran.
- **Fail closed.** No match means no calibration. Blank identity cells match nothing. An unbound
  calibration (`match` null) never applies. Two calibrations claiming one doc is a hard error.

**Why identity cells, not a header fingerprint.** The builders reproduce the master's headings, so a
regenerated skeleton and the real document share their header text. The ID and name are what make a
document that document. They hold across its revisions and differ from every other doc.

**Using the Payroll Input calibration again.** It is UNBOUND: the reference is not on this machine,
so its ID and name are unknown. On that document's pre-style backup, run once:

```bash
python scripts/xlsx_layout_match.py <pre-style-backup> --bind payroll-input-inbound-o4i
```

**The guard.** `check_profiles.py` check 7 fails if any template profile carries `tab_layouts`, and
validates every calibration file (template exists, `match` names exactly the identity cells with
non-blank values, no two calibrations claim one document).

## `xlsx_apply_layout.py` stays WIDTHS ONLY - structure is a separate, guarded pass

`xlsx_apply_layout.py` sets column widths and nothing else, on purpose. An earlier version also
replayed the reference's `panel_merges`, and reproducing `Requirements!J7:J35` (a tall Notes callout)
via COM `Merge()` **cascaded** into `B7:R35`, swallowing the entire 27-row table. Widths are safe by
construction; merging is not, so it does not belong in the widths pass.

**Root cause of the cascade (proven, isolated COM experiment).** The template backup already holds a
stack of overlapping merges in that column - `J7:R7 ... J49:R49`. A naive `Merge(J7:J35)` *on top of*
that stack makes Excel **absorb the horizontal extent** -> `J7:R35`; a downstream normalize reshape
then extended it further. It was never "merging is unsafe" in the abstract - it was merging over
pre-existing overlapping merges.

**The fix - `xlsx_apply_structure.py`, safe by three constructions:**

1. **Unmerge-intersecting-first.** Before every `merge`, unmerge every existing merge that intersects
   the target (`UnMerge` never deletes values), so Excel cannot absorb a neighbour. Proven: naive
   merge over the J:R stack -> `J7:R35`; unmerge-first -> exact `J7:J35`, all values intact.
2. **Tail-empty assert.** A `merge` runs only if every non-anchor cell in the target is empty (else it
   is SKIPPED and reported - a populated tail would be a silent delete, because `Merge()` keeps only
   the top-left value).
3. **Coverage assert.** Per affected sheet, census the value-multiset before, apply in memory, census
   after via one `UsedRange.Value` read; if any value went missing, close WITHOUT saving. Nothing bad
   is persisted.

**The structural directive model** lives in `tab_layouts[tab].structure` - an ordered list:

```json
"structure": [
  {"op": "unmerge", "range": "J7:R49"},
  {"op": "merge",   "range": "B6:I6", "row_pt": 15.75},
  {"op": "merge",   "range": "J7:J35"},
  {"op": "border",  "range": "J7:J35", "edges": "box"},
  {"op": "move",    "from": "E3", "to": "B3"},
  {"op": "inject",  "cell": "G8", "value": "Direction:", "like": "F8"}
]
```

`move` uses Cut/Paste (re-points relative formulas; copy-then-clear does not). `inject` fills an empty
cell, optionally cloning another cell's format. `border` draws a thin box (`edges:"box"`) or full grid
(`edges:"all"`) in the brand rule colour - used to outline a callout card the way a human would. Any op
may carry `row_pt` to set its top row's height: a band whose title only needs one line once merged wide
would otherwise keep the tall height normalize gave the pre-merge narrow cell (structure runs after
normalize), so `row_pt` restores the thin band. All ops are idempotent. `xlsx_extract_layout.py
--baseline <pre-style-backup>` DERIVES this list by diffing the reference against the backup (removed
merges -> unmerge rectangles, added merges -> merges, moved/new values -> move/inject), so calibration
is reproducible, not hand-authored. `panel_merges` remains only as a human-readable record.

**Order: structure runs AFTER normalize (learned the hard way).** The first build ran apply-structure
BEFORE normalize and taught normalize to PROTECT the spec'd merges. But normalize has many internal
`Merge()` sites (not just the three that were guarded); one merged row 7 across the block and, meeting
the protected `J7:J35`, Excel absorbed it into `B7:J35` - deleting 197 Requirements cells. The
coverage guard caught it and aborted (its whole purpose; the backup was untouched). The robust fix is
architectural: normalize is proven-safe on the backup's own topology (every prior session ran it
cleanly), so run it FIRST, and apply the callout/panel merges LAST, when no later pass can reshape
them. apply-structure additionally cleans the vacated tail (white fill + no borders) so unmerging the
template's old horizontal stack leaves clean white space. normalize still accepts `--template-profile`
and protects spec'd merges as a belt-and-suspenders guard (a no-op in this order, but correct if a
future pipeline reorders).

**Mandatory coverage guard across the WHOLE pipeline.** `xlsx_coverage_guard.py snapshot` censuses
non-empty cell values per sheet at the start; the driver runs `xlsx_coverage_guard.py check` after
EVERY step and ABORTS if any snapshot value disappeared. The invariant is multiset-subset (every value
still present somewhere on its sheet): a merge keeps the anchor, a move relocates, an inject adds - all
pass; only a delete/cascade fails. This is the guard that would have caught the `B7:R35` disaster at
the step that caused it. The legacy hand-authored restructure (`_restructure_file_panel3.py`) is now
just the pre-baked content in the backup; new structure is expressed as directives, not one-off scripts.

## Design principles the layout serves ("professional and pleasing")

These are the objective, whether widths come from a reference or are authored for a new template:

- a consistent grid and gutters; align panels to it;
- group related key-values into panels; don't strand a field alone;
- prose columns get real width; short labels go narrow (set by the builder's widths or a reference;
  `xlsx_balance_columns.py` then only relieves a column whose content does not fit);
- one body height per table (worst normal row); structural rows as ratios of it;
- clear section hierarchy (band > sub-section > header) by size, not new colours;
- balanced whitespace; a table closes with a border, then clean white space (right-edge discipline);
- gridlines OFF - the design paints its own canvas and borders, so the default grid is noise.

## Brand plug-in

Everything visual comes from the brand profile: palette, type scale, logo ratio/size, rule colour,
row rhythm ratios, column role weights. Swap the profile -> different brand, same layout logic. A
client brand override is a different `brands/<slug>.json`; the layout spec is brand-agnostic.

## Files

- `scripts/xlsx_extract_layout.py` - reference -> calibration `templates/layouts/<slug>.json`
  (widths + `--baseline` structure), bound to the baseline's identity cells.
- `scripts/xlsx_layout_match.py` - which calibration (if any) belongs to a workbook; `--bind`.
- `scripts/xlsx_apply_layout.py` - spec -> column widths (deterministic apply; widths only).
- `scripts/xlsx_apply_structure.py` - spec `structure` -> safe merge/unmerge/move/inject directives.
- `scripts/xlsx_coverage_guard.py` - snapshot/check the non-empty value multiset (mandatory guard).
- `scripts/xlsx_layout_rules.py` - the shared judgements (blocks/gutters, heading vs prose, table
  footer hint) the styler, the notes pass and normalize must make identically; self-test included.
- `scripts/xlsx_transplant_sheet.py` - escape hatch: copy a fully-authored reference sheet wholesale.
- `templates/layouts/<slug>.json` -> `tab_layouts` - the per-tab specs (`widths` + `structure`), one
  file per document; `templates/<template>.json` -> `identity_cells` - where a doc keeps its identity.
- `xlsx_balance_columns.py` - defers to the matched spec (skips only its tabs).
- `xlsx_normalize_layout.py` - `--template-profile` -> PROTECTS the matched spec's merges from reshaping.
- pipeline order: style -> ... -> balance -> **apply-layout** -> normalize(protect) ->
  **apply-structure** -> format-gate -> views -> restore-hidden -> borders,
  with `coverage_guard check` after **every** step.
- [layout-engine-findings.md](layout-engine-findings.md) - the calibration/incident notes behind the
  engine (what was tuned and why); read it when a layout pass behaves unexpectedly.
