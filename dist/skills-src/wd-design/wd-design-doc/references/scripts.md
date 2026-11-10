# Scripts this skill uses - bundled vs. regenerate-on-demand

See `wd-extend-lifecycle/references/prerequisites.md` for runtimes/packages. Bundled scripts:

- **`scripts/build_extend_design_doc.py`** - **bundled**, cross-platform (openpyxl, no COM).
  **Regenerates the blank Extend design-doc template from text** so the skill no longer ships a
  proprietary binary master. Emits the full **17-tab** set (16-tab structure + KPI & Reporting) in
  exact order, every section band / instruction row / table header, the standing Instructions + QA
  Review content, the Unit Testing COUNTIF/IFERROR status summary, and the yellow open-items
  convention - in **NEUTRAL grayscale, unbranded**. Style it afterwards with
  `scripts/xlsx_brand_style.py` (which recolours the neutral title/section/header placeholder
  fills into the palette), or obtain a branded master per engagement. Verified to
  re-open with the correct 17-tab set. `python scripts/build_extend_design_doc.py [out.xlsx]`.
- **`scripts/build_idd_structure.py`** - **bundled**, cross-platform (openpyxl, no COM). Regenerates
  the IDD's **SHEET STRUCTURE + headings** as a **structural `.xlsx` equivalent** - all 22 sheets in
  order with the correct visibility (O4I default), each tab title, section bands, primary
  column-header rows, the Overview Key Details block, the Unit Testing status summary, and the READ
  ME **as cells** (imports the canonical `BLOCKS` from `write_idd_readme.py`, so the two never drift).
  **HARD LIMIT - this is NOT the macro workbook:** the VBA Integration-Type visibility macro, the
  ISU/ISSG auto-naming formulas, and the READ ME text box **cannot be regenerated from text** and are
  therefore absent (documented in the script banner and in `idd-template.md`). For a true macro
  `.xlsm`, obtain the branded master per engagement (engagement store - see the environment
  memory). Verified to re-open with the correct 22-sheet set + visibility.
  `python scripts/build_idd_structure.py [out.xlsx]`.
- **`scripts/rebrand_template.py`** - **bundled** (ships in this skill). Produces a
  customer-recoloured *copy* of an already-styled design doc or template (never overwrites the
  source); role keys are the brand profile's palette names, resolved to the neutral default's
  colours, or give explicit hex keys. `.xlsx` via openpyxl recolor (no Excel needed), `.xlsm` via
  Excel COM (preserves VBA/formulas; early-bound through `xlsx_com`, because its format
  find/replace does nothing late-bound). Deps: `openpyxl`, and `pywin32` for the `.xlsm` path
  (**Windows + Excel only**). Usage in `template-builder.md`.
- **`scripts/write_idd_readme.py`** - **bundled.** Writes the IDD **READ ME sheet as formatted
  cells** (deletes any legacy text-box shape first) from the canonical content in
  `assets/idd-readme-content.md`. This is the durable fix for the recurring "READ ME missing"
  defect - cells survive every build path, text boxes don't. Excel COM (preserves VBA), Windows
  + Excel; retries once on a transient COM error. `python scripts/write_idd_readme.py <idd.xlsm>`.
  A current firm-store master already carries the cell-based READ ME. See `idd-template.md`.
- **`scripts/reset_views.py`** - **bundled.** Resets the **saved scroll position of every
  visible sheet to A1** and makes the workbook open on its first visible tab. Fixes the
  "sheet opens near column AA and looks blank" trap (Excel remembers per-sheet scroll). Excel
  COM (preserves VBA/formatting), Windows + Excel; retries once on a transient COM error (never
  after an Excel refusal). Ends its own Excel reliably (it used to leave one running - see
  `xlsx_com.py`).
  `python scripts/reset_views.py <file.xlsm> [<file2> ...]`. Works on any `.xlsx`/`.xlsm`.
- **`scripts/idd_audit.py`** - **bundled**, cross-platform (openpyxl). The **mandatory
  pre-delivery completeness gate**: flags the odd-one-out interior blank (a table row missing a
  column its peers fill), confirms the READ ME sheet has content, and reports yellow open cells.
  ALSO runs the cross-tab reconciliation pass (gap-analysis.md): security-domain set diff between
  the Security and Technical Specification tabs, referenced-vs-defined requirement-ID diff across
  every tab, and a warn for Must-priority requirements with no Unit Testing reference (all three
  skip silently when the workbook lacks the needed tabs/columns).
  Conservative by design (skips form/prose tabs + dashboard blocks; needs >=3 sibling rows) so it
  has near-zero false positives - a noisy gate gets ignored. Exit 1 on defects.
  `python scripts/idd_audit.py <idd.xlsm> [--skip "Tab A,Tab B"]`.
- **`scripts/xlsx_format_audit.py`** - **bundled**, cross-platform for the report (openpyxl);
  `--fix` needs Excel COM. The **mandatory formatting gate** (added 2026-08-06). Flags five
  defects: **CLIPPED** (row too short for wrapped text), **NOWRAP**, **VALIGN** (wrapped cells must
  be top-aligned), **IMG-OVERLAP** (2D check; header-band brand furniture excluded by geometry, and
  a header-band title free to overflow is not flagged as NOWRAP), and **CONTRAST** (added
  2026-10-17: any valued cell whose text is under 4.5:1 against its own solid fill - gate G16 made
  mechanical; unset font = black; theme / tint / indexed colours resolved, unresolvable ones
  counted; checked on EVERY tab including READ ME and hidden tabs, which the layout checks skip).
  IMG-OVERLAP and CONTRAST are report-only under `--fix`. `idd_audit.py` checks CONTENT
  completeness and says nothing about readability - run both. Exit 0 clean, 1 findings, 3/4 from
  `xlsx_com` (Excel refused a `--fix` edit / Excel already running).
  `python scripts/xlsx_format_audit.py <workbook> [--fix] [--skip "Tab A,Tab B"]`
- **`scripts/xlsx_merge_narrow_notes.py`** - **bundled**, Excel COM. Sweeps the recurring defect of
  a long note sitting in a narrow UNMERGED label cell (renders as vertical text, one character per
  line) and merges it across its table's column span, wrapped, top-aligned, height-fitted.
  Threshold is RELATIVE to column width - an absolute char floor missed a 92-char note in a
  7-wide column. Idempotent: a second run reports 0. **A merge stops at its block's gutter**
  (blocks from `xlsx_layout_rules.py`): spreading into the gutter of a two-column tab is what once
  welded Overview and WD Solution - O4I into one block for the layout pass. Ends its own Excel
  reliably (a failed Close used to skip Quit and leave Excel running - see `xlsx_com.py`).
  `python scripts/xlsx_merge_narrow_notes.py <workbook> [--brand-profile SLUG]`
- **`scripts/xlsx_repair_wrap.py`** - **bundled**, Excel COM (its own private Excel instance).
  Repairs wrap / top-alignment / row heights **including merged ranges** (Excel AutoFit silently
  ignores merges), and REPORTS a long note in a narrow unmerged cell instead of masking it with a
  giant row. Brand-free; logic unchanged from the retired firm rebrand script's formatting job.
  `python scripts/xlsx_repair_wrap.py <workbook>`
- **`scripts/xlsx_place_wordmark.py`** - **bundled**, Excel COM (its own private Excel instance).
  Places a CLIENT brand's wordmark (from its profile's `logo`: asset, locked ratio, width) on every
  sheet, hidden ones included, replacing an earlier header logo; names it `BRAND_WORDMARK` so a
  re-run replaces rather than stacks. A no-op for a brand with no wordmark (the neutral default).
  `python scripts/xlsx_place_wordmark.py <workbook> --brand-profile <client>` - then
  `xlsx_brand_style.py --wordmark-only` to anchor it.

- **`scripts/xlsx_brand_style.py`** - **bundled**; openpyxl PLANS, Excel COM APPLIES. The design-system
  pass: collapses the workbook onto **2 font families, 2 sizes, 3 structural fills** and one border
  neutral, sets the masthead / logo row / gutter identically on every tab, standardises the wordmark
  when the brand has one (one size, locked ratio, anchored `B3`, on **all** sheets incl. hidden),
  places every tab title clear of the wordmark, and clears stray formatting beyond the last real
  content. A brand with no wordmark (the neutral default) leaves existing pictures untouched.
  **Brand- and template-agnostic via two profiles** - `brands/<slug>.json` (palette, fonts, wordmark)
  and `templates/<slug>.json` (which of the source template's fills mean band / sub-section / header,
  plus layout metrics). Defaults: `neutral` + `idd`, so **no branding specified -> the neutral default**.
  `--discover-roles` censuses an unknown template's fills so a role map can be authored on evidence.
  **RECOLOUR, DON'T INVENT** - it never creates a band where the template has none; an earlier
  shape-heuristic version turned a label/value form into a wall of colour. Because sub-section labels
  end up with *no* fill by design, the pass is **not idempotent** for them: always re-run from a
  pre-style copy, never over a styled output.
  `python scripts/xlsx_brand_style.py <workbook> [--brand] [--brand-profile S] [--template-profile S] [--discover-roles] [--wordmark-only] [--dry-run]`
- **`scripts/xlsx_normalize_borders.py`** - **bundled**, pure stdlib (no COM, no openpyxl). Rewrites
  every border colour in `xl/styles.xml` to one neutral, keeping the sub-section rule. One filled IDD
  had **fifteen** border colours across 604 style definitions covering ~51,000 edges. It patches the
  **shared styles table inside the closed package**, so all other parts stay byte-identical (VBA,
  drawings, media, OLE). Two alternatives were tried and rejected: per-cell COM is far too many
  round-trips, and setting `.Color` on a whole range **creates borders on cells that had none**
  (measured 2,842 -> 3,737 edges on one tab). **Run it LAST and never open-and-save the workbook in
  Excel afterwards** - an Excel save rewrites the styles table and discards the patch.
  Colours come from the brand profile: the one neutral is the palette's `rule`, and the kept colour
  is its `band` (the sub-section rule) plus the former firm band `FF5D013A`, for older documents.
  `python scripts/xlsx_normalize_borders.py <workbook> [--brand-profile neutral] [--neutral RRGGBB] [--keep AARRGGBB] [--dry-run]`

- **`scripts/xlsx_balance_columns.py`** - **bundled**; openpyxl plans, COM applies one `ColumnWidth`
  per column. Rebalances column widths so cells wrap readably. Colour consistency does nothing for a
  table where one column is starved: the row grows tall to serve it while its neighbour sits half
  empty (`WD Solution - O4I` col D needed 10.7 lines at 31.1 next to col E at 32.9 needing 0.9).
  **Default `--mode relieve`: width moves only where content needs it.** The widths a document
  arrives with are treated as intent (builder `TAB_WIDTHS`, a client template, an author's
  adjustment). Two passes:
  - **Pass 1 (the hard need):** a column whose text needs more than ~6 lines, or whose longest word
    does not fit, is raised to that need. Its neighbours pay from their spare width, flag columns
    first and prose last (role weights in the brand's `col_roles`). No donor is cut below its own
    one-line text, or below what a wrapped title note (rows 1-3) needs to fit its row.
  - **Pass 2 (idle width only):** width a column does not use moves to text that is cut off, or
    wrapping past 3 lines (offered enough for 2). Prose columns and empty table columns never give.
  - Nothing starved, cut off or stacked deep -> nothing moves. Block total width is preserved, so
    print scale does not move.
  - **Roles are read per TABLE:** the header row directly above each body. Label/value panels are
    caption | prose. A band title is a column label only over a one-column block.
  - **Content is measured as it renders:** wrapping text in lines; short unwrapped text needs
    nothing if it can overflow, and is "cut off" if a filled neighbour stops it. Formula text and
    merged cells are not content. Grouped `<col>` widths are read correctly.
  - **`--mode reallocate`** is the previous method: share the whole block by role weight. Use it only
    for a template whose widths carry no intent. Header keywords misfire on tuned templates (Custom
    Object's L/M swap).
  - **Calibrations:** it skips only the tabs of the calibration matched to this workbook
    (`xlsx_layout_match.py`), whose widths `xlsx_apply_layout.py` sets. With no match it balances
    every tab.
  - **`--self-test`** runs the offline regression cases (no Excel). Run it after changing this file
    or `xlsx_col_roles.py`.
  `python scripts/xlsx_balance_columns.py <workbook> [--brand-profile S] [--template-profile S] [--mode relieve|reallocate] [--skip "Tab,Tab"] [--dry-run]`
- **`scripts/xlsx_normalize_layout.py`** - **bundled**; openpyxl plans, COM applies. The GEOMETRY
  pass: section bands, sub-section rules and table headers span their column BLOCK (one right edge
  per block), one uniform grid per table, one spacer height, table row heights fitted **both ways**
  (the format gate only ever grows them, so legacy heights survive - `Contacts: List` had three rows
  of identical text at 13, 26 and 40pt), and the PRINT AREA set to the content extent. Reads its
  colours from the same brand profile, so it is brand-agnostic. A table's body is the run of filled
  rows directly under its header; an empty table frames its header row only, and the Extend
  builder's "Need more rows?" footer hint is never body. `--dry-run` prints each tab's blocks,
  bands, headers and table frames.
  `python scripts/xlsx_normalize_layout.py <workbook> [--brand-profile SLUG] [--dry-run]`
  Pass `--template-profile <slug>` and it PROTECTS the merges declared in `tab_layouts[*].structure`
  of the calibration matched to this workbook from its reshaping passes (overwide clamp / dead-merge
  unmerge / single-title band merge), so a spec'd callout is never re-absorbed.
- **`scripts/xlsx_layout_match.py`** - **bundled**, shared by the layout scripts below. Answers "which
  calibration belongs to THIS workbook?": the one in `templates/layouts/` whose `match` equals the
  workbook's identity cells (the template profile's `identity_cells`; IDD `Overview!J8` / `J9`), or
  none. Fails closed: blank identity, an unbound calibration and no match all mean no calibration;
  two matches is a hard error. `--bind <slug>` records a document's identity into a calibration -
  run it only on the document the calibration was taken from (its pre-style backup).
  `python scripts/xlsx_layout_match.py <workbook> [--template-profile idd] [--bind <slug>]`
- **`scripts/xlsx_apply_layout.py`** - **bundled**; applies the per-tab calibrated column WIDTHS from
  the calibration matched to this workbook (widths only, by hard rule; no match -> nothing). Runs
  after balance (which skips the matched tabs) and before normalize.
  `python scripts/xlsx_apply_layout.py <workbook> [--template-profile idd]`
- **`scripts/xlsx_apply_structure.py`** - **bundled**; applies the per-tab `structure` directives
  (`merge` / `unmerge` / `move` / `inject` / `border`, plus an optional `row_pt` row-height on any op)
  of the calibration matched to this workbook - never another document's, because `inject` carries
  that document's text - and reproduces a reference's bespoke layout SAFELY:
  every merge unmerges intersecting merges first (no cascade - proven fix for the `J7:J35`->`B7:R35`
  disaster), asserts the tail is empty, asserts per-sheet value coverage before saving (closes without
  saving if any value would be lost), and white-fills the vacated tails. Runs AFTER normalize (not
  before - normalize has many Merge() sites that would otherwise reshape a spec'd merge into a
  cascade), before the format gate.
  `python scripts/xlsx_apply_structure.py <workbook> [--template-profile idd] [--dry-run]`
- **`scripts/xlsx_coverage_guard.py`** - **bundled**; the MANDATORY content-coverage guard. `snapshot`
  censuses the non-empty value multiset per sheet; `check` fails loudly if any snapshot value is now
  missing (multiset-subset invariant: merge/move/inject pass, delete/cascade fail). The pipeline
  driver snapshots at the start and checks after EVERY step.
  `python scripts/xlsx_coverage_guard.py snapshot|check <workbook> <snapshot.json> [--label STEP]`
- **`scripts/xlsx_com.py`** - **bundled**; the ONE owner of how every script drives Excel. Every
  COM script starts, retries, counts refusals and ends Excel through it:
  `start_excel()` (refuses with **exit 4** if ANY Excel is running; always a NEW private process
  via late-bound `DispatchEx`; holds a process handle from the start; `early_bound=True` only for
  format find/replace, which does nothing late-bound - generated into a private throwaway folder,
  never the shared `gen_py`), `rt()` (retries "Call was
  rejected by callee"), `warn()` / `note()` (report-and-carry-on / silent - both COUNT Excel's
  licence refusals), and `run(main)` (quits, releases, waits for the script's own Excel and ends
  that one process if it lingers; any refusal makes the result **exit 3**). Added 2026-10-17 after
  refused edits exited 0 and two scripts left Excel running. `python scripts/xlsx_com.py check`
  is its static guard: it fails any script that imports `win32com`, dispatches Excel, defines its
  own retry helper, skips `run()`, or has an except-handler that carries on without counting
  (pure openpyxl/file handlers carry a `# not COM` comment). Run it after editing any COM script.
- **`scripts/selftest_checks.py`** - **bundled**; proves the CONTRAST check and the refusal /
  teardown handling still FAIL on planted defects. Offline (any OS): planted low-contrast cells of
  every colour kind, fabricated refusals through `note`/`warn`/`rt`/`run`, and a planted script
  that bypasses `xlsx_com`. With `--com` (Windows + Excel, about two minutes): a REAL private Excel
  that refuses Merge (swallowed and raised cases must both exit 3), `reset_views.py` and
  `xlsx_merge_narrow_notes.py` leaving no Excel behind, a leaked Excel ended by `run()`, and the
  running-Excel guard leaving another Excel alone. Run it after changing either check.
  `python scripts/selftest_checks.py [--com]`
- **`scripts/check_profiles.py`** - **bundled**, pure stdlib, read-only. Proves every default
  profile slug the scripts fall back to (`DEFAULT_BRAND`, `DEFAULT_TEMPLATE`, every
  `--brand-profile` / `--template-profile` default) has its file; exactly one brand is
  `is_default`; every brand carries the palette roles and font pairs the scripts read; and a logo
  block is complete. It also fails if any template profile carries `tab_layouts`, or if a calibration
  in `templates/layouts/` is malformed or claims the same document as another (check 7); an unbound
  calibration is reported as a note. Run it after editing any profile or any script default - a default that points
  at a renamed or archived profile otherwise fails mid-pipeline, after earlier steps have already
  rewritten the workbook. Exit 0 clean, 1 on any error.
  `python scripts/check_profiles.py [--root <skill folder>]`
- **`scripts/xlsx_layout_rules.py`** - **bundled**, pure stdlib; a shared module plus its own
  self-test. ONE owner for the layout judgements several passes must make the same way:
  `column_blocks` (a gutter is an empty column between two regions that each carry their own
  section band - merges never decide it), `is_prose` (band text is prose by sentence punctuation,
  not length alone; over 120 chars always), `may_overflow` (text up to the format gate's own
  `LONG_TEXT` stays unwrapped, longer wraps), and `is_footer_hint` (the Extend builder's "Need more
  rows?" row). Imported by `xlsx_brand_style.py`, `xlsx_merge_narrow_notes.py` and
  `xlsx_normalize_layout.py`. Run the self-test after changing a rule or a builder's sheet layout:
  it reads both builders' sheet tables from source (never runs them) and fails if a builder band
  heading would be demoted to a note, if the builder's footer hint stops matching, if the
  pinned two-column / sparse-tab block layouts change, or if its overflow limit drifts from the
  format gate's `LONG_TEXT`. Exit 0 clean, 1 on any failure.
  `python scripts/xlsx_layout_rules.py [<scripts folder>]`
- **`scripts/xlsx_extract_layout.py`** - **bundled**; calibrates `tab_layouts` FROM a hand-cleaned
  reference: per-tab `widths`, `panel_merges` (record), and - with `--baseline <pre-style-backup>` -
  the `structure` directive list derived by diffing reference vs backup. `--write` saves it to
  `templates/layouts/<calibration>.json`, bound to the baseline's identity cells; it refuses blank
  identity cells and a calibration already bound to another document.
  `python scripts/xlsx_extract_layout.py <ref> --tabs "..." [--baseline <backup>] [--write --calibration <slug>]`
- **`scripts/xlsx_transplant_sheet.py`** - **bundled**; the ESCAPE HATCH. COM-copies a fully-authored
  reference sheet wholesale into the output (gridlines off, view to A1) with a coverage check (result
  >= reference non-empty count, else nothing saved) and a branding check (wordmark present). Use when
  a tab is too bespoke to model with directives.
  `python scripts/xlsx_transplant_sheet.py <workbook> --from <ref> --tabs "..." [--dry-run]`

**The gate list, run ORDER, and the full trap list live in
[document-quality-gates.md](document-quality-gates.md).** Order matters - several of these steps undo
each other if reordered, and **widths must settle before heights**.

**COM reliability for all of these (learned the hard way; `xlsx_com.py` now enforces it):** never
`gencache.EnsureDispatch` against the shared cache - it regenerates `%TEMP%/gen_py`, and a corrupted
cache silently returns broken dispatch objects (`AttributeError: Item.PageSetup`, `.Columns`) for
every later COM call in the session; delete that folder if it was ever generated.
`xlsx_com.start_excel()` is late-bound; `start_excel(early_bound=True)` (format find/replace only)
generates into a private throwaway folder instead.
Wrap calls in `xlsx_com.rt` (Excel answers "Call was rejected by callee" while busy) and iterate
sheets **by index**, not via the collection iterator. Killing Excel mid-operation leaves the file
locked by an orphaned process - stop it by PID before retrying (`xlsx_com.run()` ends a script's
own lingering Excel this way, and only that one).

Under a heavy styling pass Excel also drops the connection outright - `-2147417848 "disconnected
from its clients"` or `0x800A01A8 "Object required"` - at a *different* point each run. What
measurably helped: set `Calculation = xlCalculationManual` for the run (a workbook with CONCAT
formulas recalculates on every save), checkpoint every ~5 sheets instead of every sheet, keep
per-cell reads in openpyxl and send only the *applying* through COM, and **wait ~4 s after
force-killing Excel before the next `Dispatch`** - without the wait the next step fails at
`Dispatch` and one blip cascades through a whole pipeline. Never let a bare
`finally: wb.Close(...)` swallow the real exception: its own "disconnected" error masks the actual
failure and sends you chasing a symptom.

- **`design_doc_builder.py`** - **NOT shipped as a file** (it lived in a hardcoded
  `_Design Tools\` folder and carries a one-off content block). Regenerate from the build-spec
  below when needed. The reusable value is the **style-clone engine + template-clear mode**,
  not the per-app content.

---

### design_doc_builder.py - clone house styles from a reference workbook, then either data-clear it into a blank template or author a design doc
- **Language / runtime:** Python 3, `openpyxl` only (no COM -> cross-platform).
- **Third-party deps:** `openpyxl` (incl. `openpyxl.styles` and `openpyxl.drawing.image.Image` for PNG embeds). Stdlib: `shutil`, `sys`, `copy`.
- **OS constraints:** cross-platform (pure openpyxl; `.xlsx` only, no macros).
- **Inputs (CLI args):** `1` REF = reference `.xlsx` to clone styles from; `2` OUT = output path; `3` MODE = `template` | `<content>`; `4` FLOW = process-flow PNG path (content mode); `5` WIRE = wireframe PNG path (content mode).
- **Outputs:** OUT `.xlsx` - either a scaffold-preserving blank template or a fully authored doc; embedded PNGs on the Process Flow / UI & Wireframes tabs; stdout confirmation.
- **Method:**
  1. `shutil.copyfile(REF, OUT)`; `openpyxl.load_workbook(OUT)`.
  2. **Capture the real style objects BEFORE editing** - `copy.copy` of `font/fill/alignment/border/number_format` from known Overview anchor cells into role dict `CAP`: title=`B2`, section=`A4`, instr=`A5`, header=`B17`, data=`B18`. This is the "clone real styles, never hand-guess" rule.
  3. Define `sty(cell, role, wrap, yellow, bold)` applying a captured role; and builders `T()` (title row merged across the tab's column span), `SEC()` (section band), `INS()` (blue-italic instruction), `BODY()` (merged multi-row prose), `TBL(headers, rows, yellowrows)` (header + data rows, optional yellow fill per row).
  4. `TITLE_END` = per-tab dict of the merge column span (how wide each title/section band runs); `KEEP = {"Instructions","QA Review"}` are never touched.
  5. **template mode:** for every sheet except KEEP, null out any cell whose value is *not scaffold*. Scaffold = column A, row 2 (title), a section-band or header fill, or a blue-italic instruction font. Special-case **Unit Testing**: keep the legend + the `Status/Scenario` header row. Drop images. Set a generic Overview title. Save + exit.
  6. **content mode:** `blank()` the content tabs (unmerge all, clear values/styles/row heights, drop images), then author each tab with `SEC/INS/BODY/TBL`; embed the wireframe and flow PNGs scaled to fixed widths (aspect-ratio preserved); build the Unit Testing COUNTIF status legend with `%` formulas over the scenario range. Save.
- **Key constants to preserve:** `YELLOW = "FFFFFF00"` (**8-hex ARGB**); scaffold fills `FF78DED4` (teal section band) and `FFF2F2F2` (gray table header); role anchor cells `B2/A4/A5/B17/B18`; embed widths **1300px** (wireframe) and **1550px** (flow); image height = `width * (h/w)`.
- **Gotchas / correctness notes:** 8-hex ARGB is mandatory - a 6-hex fill renders **transparent** (`FFFF00` fails, `FFFFFF00` works). Capture styles with `copy.copy` *before* mutating cells or you copy already-cleared formatting. template mode preserves structure by **fill-color/italic detection**, not row numbers, so it survives layout drift. `.xlsx` has no VBA, so openpyxl is safe here - for the macro-driven **IDD `.xlsm`**, do NOT use this pattern; copy the master (see `idd-template.md`).
- **Regeneration confidence:** **High** for the engine (style-clone + template-clear). The original also carried a hardcoded per-app content block (for one delivered app) - that's a one-off, not needed for regeneration; author fresh content per the tab specs in `16-tab-spec.md`.

---

### fill_bow.py - fill the 10-tab BoW/Marketplace template via Excel COM, preserving conditional formatting / formulas / shapes
- **Status:** **NOT shipped as a file.** `bow-template.md` calls it a "pattern" (precedent: a delivered BoW doc) - there is no bundled script. Regenerate from this build-spec per engagement; the reusable value is the **COM fill + preserve + tab-by-tab diff** discipline, not any one app's content.
- **Language / runtime:** Python 3 driving Excel via COM (`pywin32` / `win32com.client`). **Windows + desktop Excel only.**
- **Third-party deps:** `pywin32`. Openpyxl may be used READ-ONLY for the post-fill diff, but the FILL must go through COM.
- **Why COM, not openpyxl (the whole reason this script exists):** the BoW template carries **conditional formatting, formulas (Unit Testing's status-summary), and shapes** that openpyxl silently drops on save. COM edits cells in place through Excel itself, so that furniture survives. A delivered draft once lost both the CF and the summary formulas via an openpyxl path - that class of regression is unacceptable in a delivered doc.
- **Inputs:** the blank BoW 10-tab template path (canonical blank per engagement - pull from project memory, never hardcode; see `bow-template.md` section  Engagement inputs); a per-tab content payload (Discovery Q&A, Specification endpoint inventory, Object Model grid, Process Flow steps, etc.); output path.
- **Outputs:** a filled `.xlsx`/`.xlsm` copy of the template (never overwrites the master); stdout confirmation + the tab-by-tab diff report.
- **Method:**
  1. **Copy the blank template to the scratchpad FIRST** - cloud-synced (OneDrive) files hold sync locks that can block even a read. Open the scratch copy, never the synced original.
  2. Launch hidden Excel (`Visible=False`, `DisplayAlerts=False`) via **late-bound** `win32com.client.Dispatch("Excel.Application")` (see COM reliability below); open the scratch workbook.
  3. **Set `Calculation = xlCalculationManual` for the run** - the template's CONCAT/COUNTIF summary formulas otherwise recalc on every touch and slow/destabilise the session.
  4. Fill each tab's cells in place. Tab order is fixed: `Overview | Discovery | Specification | Process Flow | Object Model | UI Wireframes | Unit Testing | QA Review | Open Items | Migration Checklist`. Requirements live INSIDE Discovery; endpoint/API inventories inside Specification.
  5. **Preserve, don't rebuild:** write VALUES into existing cells; do not delete/recreate ranges that carry conditional formatting, shapes, or formulas. Leave Unit Testing's status-summary formula cells untouched. When ADDING a section into an appended region, explicitly **clear the fill first** (used-range often oversizes the template blue band -> white-on-blue illegible text) and copy the live template's own style objects for the bordered-table treatment (`bow-template.md` section  Phantom band-fill).
  6. Restore `Calculation = xlCalculationAutomatic`; `Calculate()`; `SaveAs` the output; `Close(SaveChanges=True)`; `Quit()`; **release the COM object**.
  7. **Diff against the blank template tab-by-tab afterward** (mandatory): confirm every tab's formatting AND Unit Testing's summary formulas survived. Report any tab where CF / formulas / shapes changed - a lost formula or dropped CF is a delivery-blocking regression.
- **Key constants:** fixed 10-tab order (above); SaveAs format `51` (`xlOpenXMLWorkbook`) for `.xlsx`; scratchpad-copy-before-open rule; `xlCalculationManual` during the run. Yellow open-items fill `FFFFFF00` (8-hex ARGB) per the house convention.
- **Gotchas (COM, learned across the suite):** delete `%TEMP%/gen_py` and use late-bound `win32.Dispatch` - `gencache.EnsureDispatch` regenerates that cache and a corrupted one silently returns broken dispatch objects for the rest of the session. Wrap COM calls in a retry (Excel answers "Call was rejected by callee" while busy) and iterate sheets **by index**, not via the collection iterator. **Release the COM object and `Quit()`** or Excel lingers and locks the file. If you must force-kill Excel, kill it by PID and **wait ~4 s before the next `Dispatch`** - without the wait the next step fails at `Dispatch`. Never let a bare `finally: wb.Close(...)` swallow the real exception (its own "disconnected" error masks the actual failure). The band fill is a THEME color, so `fgColor.rgb` returns a theme index not a hex - copy the whole style object rather than reading/rebuilding it (`Values must be of type str` otherwise).
- **Regeneration confidence:** **High** for the COM fill + preserve + diff engine (fully specified here and cross-referenced in `bow-template.md`). Per-app content is supplied fresh each engagement; the canonical blank template path is an engagement input, never hardcoded.
- **Cross-ref:** [bow-template.md](bow-template.md) (10-tab format, fill method, phantom band-fill, engagement inputs).
