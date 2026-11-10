# Design-document quality gates - brand- and template-agnostic

These gates apply to **every** design document we produce: firm template, client template, firm
branding, client branding. Branding decides colours, fonts and which wordmark; it never decides
whether the document is *well made*. Keep the two separate and a client-branded doc goes out as
clean as a firm-branded one.

Written after a full formatting pass on `INTXXXX_Payroll_Input_Inbound_O4I_Template_Design_Document`
(2026-08-06). Every trap below is one that actually shipped or nearly shipped.

## Branding policy

1. **No branding specified -> the neutral default.** `brands/neutral.json` is the default in
   `scripts/xlsx_brand_style.py` (slate and grey, the system font pair, no wordmark).
   Nobody has to ask for it; it is what happens.
2. **Client asks for their branding -> honour it, for that project only.** Copy
   `brands/_example-customer.json` to `brands/<client>.json`, fill in palette/fonts/logo, and pass
   `--brand-profile <client>`. Ask for: brand guide hex values, an approved wordmark PNG/SVG on a
   transparent background, its locked aspect ratio, and whether their fonts are licensed for our
   machines. If they are not, use the system pair and say so in Version Control - a doc that
   silently font-substitutes on the client's machine is worse than one that chose system fonts.
3. **Check contrast when swapping a palette.** Band text on band, header text on header fill. A
   dark-on-dark table header is the most common failure when a client palette drops in.
4. **Never restyle meaning.** Yellow `FFFF00` is the open-item convention, and semantic status
   colours (RAG colour scales, test-status rules) are usually **conditional formatting** that
   carries meaning. Both survive every rebrand. Verify CF before "fixing" a bright cell:
   `ws.conditional_formatting` will tell you.
5. **Unknown source template -> discover, don't guess.**
   `python scripts/xlsx_brand_style.py <wb> --discover-roles` censuses every fill with counts and a
   sample cell. Assign each to band / sub-section / header once, record it in
   `templates/<slug>.json`. Never infer hierarchy from shape - an early version decided "a row with
   1-2 populated cells is a band" and turned a label/value form into a wall of colour.

## The gates

Structural gates first (content completeness is [gap-analysis.md](gap-analysis.md)); these are the
*presentation* gates.

| # | Gate | Pass condition | Tool |
|---|---|---|---|
| G1 | Clipped text | no wrapped cell taller than its row | `xlsx_format_audit.py` |
| G2 | Wrap | long text wrapped, except headings free to overflow | `xlsx_format_audit.py` |
| G3 | Vertical alignment | every wrapped cell top-aligned | `xlsx_format_audit.py` |
| G4 | Image overlap | no image covering live cells | `xlsx_format_audit.py` |
| G5 | Narrow-cell notes | no long string stacked in a narrow column | `xlsx_merge_narrow_notes.py` |
| G6 | Type scale | exactly **2 families** (head + body) and **2 sizes** (title + body) | `xlsx_brand_style.py` |
| G7 | Fill roles | at most **3** structural fills + conventions | `xlsx_brand_style.py` |
| G8 | Borders | **one** neutral + the sub-section rule, measured PER CELL | `xlsx_normalize_borders.py` |
| G9 | Wordmark | one size, locked ratio, same anchor, on **all** sheets incl. hidden | `xlsx_brand_style.py` |
| G10 | Tab title | single line, clear of the wordmark, same offset every tab | `xlsx_brand_style.py` |
| G11 | Trailing junk | no fills/borders past the last real content | `xlsx_brand_style.py` |
| G12 | Column balance | no column needs more than ~6 lines while a neighbour sits idle | `xlsx_balance_columns.py` |
| G13 | Section framing | bands / rules / headers span their BLOCK, one right edge per block | `xlsx_normalize_layout.py` |
| G14 | White space | one spacer height; table rows sized to content, both directions | `xlsx_normalize_layout.py` |
| G15 | Print area | set to the CONTENT extent, not the used range | `xlsx_normalize_layout.py` |
| G16 | Legibility / contrast | **WCAG AA for a client-facing deliverable: body text >= 4.5:1, large text / UI >= 3:1**; ~2.5:1 is only an absolute never-below floor for incidental non-text fills | `xlsx_brand_style.py` (fills vs body text, BEFORE styling) + `xlsx_format_audit.py` **CONTRAST** (every valued cell's text vs its own fill, AFTER styling; every tab incl. READ ME + hidden) |
| G17 | Opening view | every sheet's saved scroll position is A1; workbook opens on tab 1 | `reset_views.py` |
| G18 | **Verify by render** | export tabs to PDF and *look* | see below |

**Colour consistency is not layout consistency.** G6-G8 can all pass on a workbook that still reads
as ragged, because they say nothing about geometry. On the reference IDD, after the palette was
unified: `WD Solution - O4I` had 3 band spans, 5 sub-section rule spans and 5 table-header spans on
ONE tab; stacked tables in the same column block ended at columns D, E and F; `Requirements` col C
was 65.4 wide needing 0.6 lines beside col D at 61.3 needing 4.2; and `Contacts: List` rendered three
rows of identical text at 13, 26 and 40pt. G12-G15 exist for exactly that.

**G18 is not optional and not replaceable by G1-G17.** Property checks passed on a version whose
Overview tab was a wall of band colour, and again on one whose title sat on top of the logo. Render
and look:

```bash
python -c "import fitz; d=fitz.open('t.pdf'); d[0].get_pixmap(dpi=120).save('t.png')"
```

Excel -> `ws.ExportAsFixedFormat(0, path)` per tab, then PyMuPDF (`fitz`) to rasterise. `poppler`
is not installed, so `pdftoppm` is unavailable. Crop and raise the DPI to inspect a band closely.
Beware: each tab is fit-to-one-page-wide, so a 96-column tab renders much smaller than an
18-column one - apparent font differences between tabs are usually page scale, not a defect.

**Second concrete proof (build-verified on a delivered app, v1.7).** A doc whose used range ran to row 303
with no print area set, under fit-to-1-page-wide, produced multiple **solid-blue empty pages** after
the content ended; separately, its appended sections had white-on-blue text (see bow-template.md).
Both passed every property gate; only the render caught them. Two fixes that mattered: set
`ws.print_area` to the true content extent, and clear fills/borders **strictly below the last content
row** - but skip any reserved conditional-format rows (e.g. the Unit Testing tab's pre-formatted CF
rows), which are intentional, not stray.

## Order matters

Run in this order; several steps undo each other if reordered.

0. `xlsx_coverage_guard.py snapshot` - census the non-empty value multiset (the baseline for the
   MANDATORY guard); the driver re-runs `check` after EVERY step below and ABORTS on any dropped value.
1. `xlsx_brand_style.py` - type, fills, roles, geometry, wordmark, title, trailing cleanup
2. `xlsx_place_wordmark.py` - ONLY when the brand has a wordmark: place it on every sheet (incl. hidden)
3. `xlsx_brand_style.py --wordmark-only` - re-anchor; step 2 keeps each earlier logo's position
4. `xlsx_merge_narrow_notes.py`
5. `xlsx_balance_columns.py` - column widths BEFORE any row fitting (SKIPS the tabs of the
   calibration matched to this workbook, and only those)
6. `xlsx_apply_layout.py` - the calibrated per-tab column WIDTHS for spec'd tabs (widths only).
   Steps 5-8 use a calibration only when `xlsx_layout_match.py` matches it to the workbook's identity
   cells; on a regenerated skeleton or an Extend doc, none matches and the generic passes do the work
7. `xlsx_normalize_layout.py --template-profile <slug>` - framing, grids, spacers, row heights, print
   area; also PROTECTS spec'd merges (belt-and-suspenders - a no-op given step 8 runs after it)
8. `xlsx_apply_structure.py` - the per-tab `structure` directives (safe merge/unmerge/move/inject),
   applied AFTER normalize so no later reshape can cascade them
9. `xlsx_format_audit.py` (no `--fix`) - should already be CLEAN; if it wants to grow rows, step 7's
   estimator has drifted from the gate's. Fix the estimator rather than letting the gate re-grow
   rows, because re-growing is what makes heights uneven again. Its **CONTRAST** check is the only
   gate that sees text a step 4-8 pass left on a fill it painted - a CONTRAST hit means a pass set a
   fill without its text colour (fix that pass, not the cell)
10. `reset_views.py` - the last COM step (resets every sheet's scroll position to A1)
11. `xlsx_sheet_visibility.py restore` - re-hide the macro-hidden tabs (COM+save, so BEFORE borders)
12. `xlsx_normalize_borders.py` - **LAST** (patches the closed package)

Widths must settle before heights: rebalancing changes how many lines every cell needs. Steps 6-8
run after step 5 for the same reason. **Structure (step 8) runs AFTER normalize (step 7), not before**:
normalize has many internal `Merge()` sites and is proven-safe on the backup topology, so applying the
spec'd callout/panel merges last is the only way they cannot be reshaped into a cascade. Protecting
them inside normalize was tried and was insufficient - one unguarded merge site deleted 197 cells.

**The coverage guard is not optional.** It is the one check that catches content DELETION - a bad
merge or a reshape that swallows a table (the `Requirements!J7:J35` -> `B7:R35` disaster deleted 27
rows and every property gate still passed). Multiset-subset per sheet: merges/moves/injects preserve
it, a delete breaks it, and the run aborts at the offending step.

- **Start each full run from a pre-style copy of the document.** The pass is *not* idempotent for
  sub-section labels: they end up with no fill by design, so a second run cannot re-detect them.
  Keep `_prestyle_backup_<version>.xlsm` beside the doc and re-run the whole pipeline from it.
- **Nothing may open-and-SAVE the workbook in Excel after step 6.** Border normalisation patches
  `xl/styles.xml` inside the closed package; an Excel save rewrites the styles table and discards
  it. Renderers must close with `SaveChanges=False`.
- Put content fixes in the pre-style backup, not the styled output, so the pipeline stays the one
  reproducible path.

A driver that retries a failed step and restores the backup before retrying step 1 is worth the
40 lines - see the traps below for why. Every COM step ends its own Excel and settles its exit code
through `scripts/xlsx_com.py`: **exit 3 = Excel refused edits** (stop; re-run from the input copy
once Excel accepts edits), **exit 4 = another Excel is running** (never retry into it - wait for
its owner). Treat both as failures; neither is a pass.

## Traps

**Excel COM is genuinely flaky under this load.** The same script succeeds, then fails at a
different point next run with `-2147417848 "disconnected from its clients"` or
`0x800A01A8 "Object required"`. Mitigations that measurably helped:

- Set `Application.Calculation = xlCalculationManual` for the run. A workbook with CONCAT formulas
  recalculates on every save; combined with a save per sheet that alone caused drops. **Set it only
  AFTER `Workbooks.Open` - setting it before any workbook is open raises `-2147352567 "Unable to set
  the Calculation property"`.** Move the assignment after Open, or wrap it in a try.
- Checkpoint every ~5 sheets, not every sheet.
- Do the *thinking* in openpyxl and only the *applying* in COM. Moving per-cell reads (values,
  column widths, merge state) out of COM and into the openpyxl planning pass fixed a reproducible
  mid-run disconnect.
- Force-kill Excel and **wait ~4 s** before the next `Dispatch`. Without the wait, the next step
  fails at `Dispatch` and one blip cascades through the whole pipeline. (`xlsx_com.end_excel()`
  pays this wait itself whenever it has to end a process.)
- **Never let a bare `finally` swallow the real error.** `finally: wb.Close(...)` raised
  "disconnected" and masked the actual exception, which cost a full debugging cycle chasing a
  close error that was only a symptom. Catch, print the traceback, then tear down defensively.
- **Start Excel only through `xlsx_com.start_excel()`** - late-bound and always a NEW private
  process. Never `gencache.EnsureDispatch` against the SHARED `%TEMP%/gen_py` (it corrupts and
  produces phantom `AttributeError: <obj>.PageSetup` / `.Columns` failures), and never plain
  `win32.Dispatch`, which attaches to an Excel the user already has open - `Quit()` then closes
  THEIR Excel with DisplayAlerts off. `PageSetup` properties can also fail transiently; retry them
  and carry on.
- **Excel's format find/replace silently does NOTHING late-bound.** `FindFormat` / `ReplaceFormat`
  + `Range.Replace(SearchFormat=True, ReplaceFormat=True)` recoloured 0 of 34 bands late-bound and
  every band early-bound (2026-10-18) - with no error either way. Ordinary named arguments
  (`Copy(Destination=...)`) do work late-bound. For format find/replace only, use
  `xlsx_com.start_excel(early_bound=True)`: it generates the early-bound classes in a private
  throwaway folder, so the shared cache is never touched. `xlsx_com.py check` fails a script that
  uses `FindFormat`/`ReplaceFormat` without it.
- **Excel can REFUSE edits and the run still look green.** When Office's licence check lapses,
  Excel drops into reduced-functionality mode intermittently and answers edits with "This command
  is unavailable because the license to use this application has expired" (a font change says
  "Unable to set the Name property of the Font class"). Every script caught these, printed
  `! merge ...` and exited 0: one `xlsx_apply_structure.py` run logged 42 refusals - its final Save
  among them - and passed (2026-10-16). Now every COM except-handler counts refusals through
  `xlsx_com.warn()` / `note()` and the script exits 3. A handler that swallows an error without
  counting it fails `python scripts/xlsx_com.py check`.
- **A failed `Close()` must never skip `Quit()` - and even a clean `Quit()` is not enough.**
  `reset_views.py`, `xlsx_merge_narrow_notes.py` and `xlsx_apply_structure.py` left their Excel
  running after they finished (2026-10-16, 30 times across three batches): one ran
  `Close(); Quit()` as a single step, another hid a failed Quit behind `except: pass`. Worse, on
  this machine Excel intermittently ignores `Quit()` outright - measured 2026-10-18 with ZERO
  references held, still alive 40 s after its client process had exited, and on most pipeline
  steps in a bad hour. So every teardown is one guarded step at a time, and `xlsx_com.run()` waits
  up to 15 s for the process the script started, then ends that one process - identified by a
  handle held since start, so it can never end anyone else's Excel. Expect its
  `[teardown] ... ended it` line on a bad day; it is the fix working, not a failure.

**Formatting-specific:**

- **AutoFit silently ignores merged cells.** A merged block never grows, so `--fix` has to compute
  and set the height explicitly. A 2,236-char narrative sat at 15 pt, cut off mid-sentence.
- **When COM `--fix` (AutoFit) hangs on a heavy doc, replicate it in pure openpyxl** using the
  audit's OWN constants - `CHAR_W=1.05`, `LINE_PT=12.75`, `LONG_TEXT=60`. Clipped-fix: row height =
  `need_lines * LINE_PT + 2`, set valign `top` on wrapped multi-line cells, and wrap-on for text
  longer than 60 chars unless it is free to overflow (row <= 5 with empty neighbours). Deterministic,
  needs no Excel, and re-audits clean - the fallback path when COM is being flaky (build-verified on
  a delivered app, v1.7).
- **Setting `Borders(edge).Color` on a multi-cell range CREATES borders** on cells that had none -
  measured: 2,842 -> 3,737 styled edges on one tab. That is why border colour is normalised in the
  shared styles table instead. Test before trusting either approach.
- **A `--fix` must never be more aggressive than the check that drives it.** The audit exempted
  header text that is free to overflow; the fix did not, so it wrapped a tab title into three
  stacked lines under the wordmark.
- **Row heights: a 13.5 pt row clips the descenders of 10 pt text.** Give table headers a floor
  (16.5 pt for 10 pt Tahoma - what Excel's own autofit picks).
- **Width-relative thresholds, never absolute character counts.** "Merge notes over 60 chars"
  missed a 43-char *title* in a 5.0-wide column that stacked nine lines deep. Test *lines needed
  in its own column* instead.
- **Never size a title with leading spaces inherited from another font.** The template's 27 spaces
  were calibrated for Arial 24; in a narrower font the title landed on the logo. Measure the space
  width from the font actually in use (Excel can do it: a temporary textbox with `AutoSize`,
  comparing `"M"*10` against the same string with spaces between) and re-derive the padding.
- **Guard the header band from generic row rules.** A generic "merge narrow notes" pass grabbed the
  space-indented tab title, merged it, and shrank the logo row from 42 pt to 18.75 pt, clipping the
  wordmark. Rows 1-3 belong to the masthead/logo/title; exclude them.
- **The logo row must exceed the wordmark height** (`width_pt / ratio`), or the logo overflows into
  the rows below.
- **Hidden is not gone.** Sheets hidden by an Integration-Type macro still ship, and un-hide on
  demand. Four tabs kept the legacy lockup because the rebrand skipped non-visible sheets. Un-hide,
  swap, restore the exact prior state (`xlSheetHidden` 0 and `xlSheetVeryHidden` 2 differ).
- **Excel's used range extends past the data** and drags stray formatting with it - a solid blue
  block printed on page 2 of a tab, on empty cells that were unfilled in the source. Clear fills
  and borders beyond the last valued row/column. Stay conservative: blank rows *inside* a table are
  scaffolding for the reader and their borders belong there.
- **G8 is judged per CELL, not by the styles table.** `xlsx_normalize_borders.py --dry-run` counts
  every `<color>` inside `<borders>`, including definitions on edges no cell styles. After an Excel
  save the definition table re-expands even though every *applied* border stayed neutral - the
  document reads correctly. Confirm with a per-cell census (`cell.border.<edge>.color`) before
  concluding the gate failed.
**Layout-specific:**

- **`Range.Merge()` DESTROYS every value except the top-left one, silently, with DisplayAlerts off.**
  A clamp that re-merged over-wide header merges wiped **20 real cells** - the entire Examples header
  row (`Artifact` / `File (click to open)` / `Status` / `What it is / why it matters`),
  `Requirements!C8:H8`, and three WD Solution header rows. Never merge unless every cell after the
  first is verified empty, and diff cell VALUES against the pre-style backup after any pass that
  merges. That diff is the only reason this was caught.
- **Detect tables PER BLOCK, never per row.** A header row in the left block and a DATA row in the
  right block share a row number. Treating the row as one table painted real data
  (`_DEFAULT_WORKDAY_RETRY_CONFIG | 3 | Exponential`) with the table-header fill and ran one table's
  body down through the other block's rows. This is what "tables inside tables" looks like from the
  outside, and it is the single biggest source of confusion on a two-column tab.
- **Draw the grid on LOGICAL columns, not physical ones.** Take each table's columns from where its
  header row actually has labels (merge-aware), then switch `xlInsideVertical` OFF inside a logical
  column that spans several physical ones. Bordering the block's physical columns instead draws a
  divider for every physical column, so a 3-column table in a 5-column block shows two phantom
  column lines - that is the "grid where there shouldn't be one" effect.
- **A header cell must span the same columns as the body beneath it.** Examples' notes are merged
  `F:T`; its header sat unmerged in `F` (9 wide), so the label stacked vertically above body text
  with 127 points to spread across.
- **Column/row extent must be MERGE-AWARE and computed BEFORE anything uses it.** Deriving the
  extent from valued cells alone stopped Examples at column F, so the print area became `A1:F22` and
  both the notes column and the intro prose were cut off at the page edge.
- **The white canvas must clear BORDERS, and must start at the last REAL content column.** Setting
  the fill white is not enough - leftover template borders past the content still draw a grid. And
  the canvas start must not come from the merge-aware extent: one wide populated merge pushes `lc`
  far to the right, so the canvas begins past it and never touches the columns immediately after the
  table. Measured on the reference IDD: Overview's content ends at J with 46 bordered cells each in
  K/L/M; Unit Testing ends at I with 53 each in J/K/L; Examples ends at F with 13 each in G:J. Users
  report this precisely as "looks good until column <X> on". Clear borders from
  `last_valued_column + 1`, skipping only cells inside a populated merge.
- **The tab-title size is only for sheets WITH a wordmark.** 24pt is calibrated to sit beside the
  logo. On a sheet without one (READ ME) the first string is a prose heading, and 24pt inside its
  existing 21.95pt merged row was clipped by the row below. Use the section size there.
- **Wrap decisions are WIDTH-RELATIVE everywhere** (same rule as "Width-relative thresholds" under
  Formatting-specific above): `Mappings!B8` held 19 chars in a 14-wide column with wrap OFF - under
  the 60-char floor, so never wrapped and the text ran off its cell. Compare against the column's (or
  merge span's) capacity, not a fixed count.
- **THE RIGHT-EDGE RULE: a table closes with a border, then clean white space.** Getting this right
  needs THREE passes in a specific order, and any two of them alone fails:
    1. grid draws the table (on logical columns),
    2. the white canvas clears fill AND borders beyond the last valued column,
    3. the closing right edge is RE-DRAWN on each table's last logical column.
  Canvas-first alone lets the grid overdraw into empty space (measured 1,198 stray bordered cells).
  Canvas-last alone wipes the table's own right border, because Excel may store the J/K boundary as
  K's LEFT edge - tables come out open-ended. Both plus the re-draw: 337 stray, all of it the one
  structural case below.
- **Excel REMEMBERS each sheet's scroll position, and it is saved in the file.** A tab last edited
  at row 60 / column AA opens there for the reader and looks blank or half-empty - which reads as a
  broken document even though nothing is wrong with it. Reset every sheet to A1 and set the workbook
  to open on its first visible tab, as the last COM step before the package patch.
- **A sub-section label inserted by hand must carry the TEMPLATE's sub-section fill, not the brand
  colour.** The styler recognises roles by fill and maps them to the brand itself; giving a new label
  the brand's header fill makes it read as a table HEADER instead of a sub-section.
- **Shift a block with CUT, never copy-then-clear.** Excel re-points relative formulas on a cut. On
  Unit Testing the summary moved C:G -> B:F and its COUNTIF criteria followed to B6:B10 while the
  ranges it counts (`C15:C1121`, not moving) correctly stayed put.
- **CONTRAST is a gate, not an eyeball job.** READ ME row 4 carried a near-black template fill
  (`FF2A2A38`) under dark body text and was simply unreadable - reported three times before it was
  found, because it survives everything: that colour is in no role map, and the canvas only touches
  cells OUTSIDE the content. Test luminance contrast between every solid fill and the body text
  colour; below ~2.5:1, neutralise the fill to paper. This catches the whole class for ANY brand
  instead of special-casing one hex, and it is the check that matters most when a client palette
  drops in. I dismissed this exact fill as harmless on first inspection - do not repeat that.
- **The styler's contrast gate runs BEFORE styling, so it cannot see what later passes paint.**
  `xlsx_normalize_layout.py` once set band FILL without band TEXT colour: five cells came out
  dark-on-dark (File!D6, File!I6, Overview!I19, WD Solution - O4I!B18, Custom Object!D6) while
  every gate passed (2026-10-16). `xlsx_format_audit.py` CONTRAST now checks every valued cell's
  own text against its own fill AFTER the passes (unset font = black; theme, tint and indexed
  colours resolved; any colour it cannot resolve is counted, never passed silently).
- **Unmerge EMPTY merged tails; they are what breaks the right-edge rule.** Requirements' Notes
  cells were merged `J:R` with no value, drawing a bordered block eight columns past the table. The
  canvas cannot reach inside a merge and clearing part of one is a no-op. Unmerging loses nothing
  (they are empty) and lets the canvas clear the tail: stray bordered cells fell 337 -> 102, and
  Unit Testing went from 46 stray / 7 closing borders to 0 stray / 52 closing. But if a merge anchor
  actually HOLDS content, narrowing it is a TEMPLATE STRUCTURE decision - surface it to the author
  rather than silently changing the doc.
- **Two tables stacked with no separation read as one.** File's property rows sat directly under the
  section band, which ALSO carried their Test/Production/Inbound column labels - so the properties
  table had no header of its own. Give each table its own header row, and put a blank spacer row
  between tables so they read as separate objects.
- **The closing border goes on the table's last CONTENT column, not the block's edge.** One wide
  populated merge stretches a block far past the last valued column, so drawing the closing edge at
  the block boundary put a lone vertical rule ten columns out - Overview at T, Requirements at R,
  Open Issues at Q, 45/27/30 cells each. Compute the edge from the values actually present in the
  table's own rows (including populated merge ends), clamped to the block.
- **Un-merging leaves the merged AREA's outer border behind.** After dropping an empty tail, the old
  right-hand border survives on a now-lone empty cell far right. Clear the range's borders in the
  same breath as the un-merge, or you trade a bordered block for a phantom rule.
- **Together these two took stray bordered cells from 337 to 6** across fourteen tabs, with closing
  borders present on every table tab. That is the right-edge rule satisfied: table closes with a
  border, clean white space after.
- **Report body columns with no header label** rather than inventing one. A partially-labelled header
  row is a content defect for the author to fix.

- **Measure spans MERGE-AWARE or you will chase phantoms.** openpyxl exposes a fill only on a
  merge's ANCHOR cell, so a band merged across B:F reads as a one-cell chip. A first audit reported
  6 of 7 Question bands as single-cell defects; they were already correct. Expand merged ranges
  before comparing spans.
- **Normalise per BLOCK, not per tab.** Two-column tabs (Overview: content in B:G beside I:J) are
  separated by an empty gutter column. Stretching a band to the tab's width welds the columns
  together. A span that already crosses a gutter is a tab-level header - leave it.
- **A gutter is decided by VALUES and BANDS, never by merges - and every pass must agree on it
  (2026-10-17).** The notes pass merged notes and headers rightwards up to the next populated cell,
  straight across the gutter (Overview `B7:H7`; O4I `E8:H8`, `B16:H16`, `B24:H24` - the last three
  reaching the right column's own cells). The layout pass counted merged columns as "in use", found
  no gutter, and logged `blocks=1` on every IDD tab: the "Contacts: List" band and header ran over
  the Key Details labels, and O4I's "Security" band was moved H18 -> B18 and merged across the tab.
  A plain "empty column = gutter" rule is wrong too: the File tab leaves its value columns blank
  beside the labels and would shatter. The rule now lives in ONE place,
  `xlsx_layout_rules.column_blocks`: an empty column is a gutter only between two regions that
  each carry their own section band, and of several empty columns only the LAST is the gutter -
  the others are the left region's spare columns (O4I's F, 60 wide, beside the 3-wide gutter G;
  calling F gutter too left the "Transformation or related Notes/Configuration" header clipped
  in 12-wide column E). Any pass that spreads content rightwards stops at its block.
  The same fix exposed a second weld: grouping band cells per ROW joined the two bands that share
  a row on a two-column tab (Overview row 6) into one span - group them per block.
- **A table's body is the run of filled rows DIRECTLY under its header.** Skipping blank rows to
  find a first body row boxed whatever came next: the Extend builder's "Need more rows?" hint under
  every empty table (Overview Contacts, Security), O4I's "Supporting Objects / Internal Files"
  sub-heading eight rows down, and Report's next section band. An empty table frames its header row
  only; the footer hint is never body even when a full table runs into it; a band, sub-section rule
  or another header ends a table.
- **A heading takes its height from the table DIRECTLY under it, or none.** Looking past an empty
  table to the next populated one sized Extend bands at 53.6pt from a table 60 rows away. And set
  the band's minimum height in the PLAN, not only in the band pass: the row-height pass after it
  had been resetting every band over an empty table to the title's 15.8pt text height.
- **Heading or prose is a SENTENCE test, not a length test.** A 70-character cut-off demoted real
  section headings to italic notes: O4I's 88-char "Orchestrate for Integration Configuration
  Details (HTTP Retries, Namespaces, CSV Format)" and CC's 76-char "Connector Configuration Details
  (...)". The builders carry the IDD master's wording (the master's own version runs to 93 chars),
  so the rule changed, not the text: over 70 chars, band text is prose only with sentence
  punctuation; over 120 it always is (`xlsx_layout_rules.is_prose`, shared by the styler and the
  layout pass). `python scripts/xlsx_layout_rules.py` fails if any builder band heading would be
  demoted.
- **Wrap-or-overflow belongs to the FORMAT GATE's number, not the layout pass's.** Once promoted,
  those two headings stayed unwrapped under normalize's private 70-char limit, and the gate (60,
  `LONG_TEXT`) flagged both NOWRAP. Wrapping "because the band is merged" failed differently:
  a tab_layouts calibration unmerged Custom Object's band afterwards, leaving a wrapped title stacked four lines
  deep in a 6-wide column. Now band text up to the gate's limit overflows and longer text wraps
  (`xlsx_layout_rules.may_overflow`); the self-test fails if the two numbers drift apart.
- **Apply sub-section rules AFTER the table grid.** A sub-section heading usually sits inside the
  row range of the table beneath it, so a grid pass applied later erases the rule - 10 rules became
  2 on the first attempt.
- **Column width is a MINIMAX problem, not "give the starved column more".** Scaling every column's
  "need" proportionally made already-fine columns worse. Lines are equal across columns exactly when
  width is proportional to CONTENT LENGTH; allocate on that, express the line ceiling as a FLOOR on
  width, cap per column at no less than its current width, and water-fill. Do not mutate the
  remaining budget mid-pass - that compounds clamps and collapsed one column from 63.6 to 16.2.
  (2026-10-18: the default `--mode relieve` DOES give the starved column more, but only up to its
  own need, and a donor never drops below its own need - so no fine column is made starved, and
  columns nobody needs to touch keep their width.)
- **Row height requirements follow the CELL, not the row.** A cell merged down N rows may spread its
  height across them; a plain cell in the same row may not. Deriving it from the row let a
  neighbouring vertical merge dilute a 2-line cell down to a 15pt row.
- **Rows inside a multi-row merge are not spacers.** They are blank but the merge's text is laid out
  across them; collapsing them to a 6pt gap left a 2,236-char narrative six lines short.
- **Long blank runs are reserved capacity, not white space.** Unit Testing keeps ~1,060 empty
  scenario rows under a conditional-format range. Only normalise runs of one or two blank rows.
- **A band row whose only content is its title must be MERGED across the band.** Otherwise the
  title wraps at its OWN column's width: after the rebalance narrowed column B to 22, "Orchestrate
  for Integration Configuration Details (HTTP Retries, Namespaces and CSV Formats)" stacked four
  lines deep inside that column and the band clipped the last one, while 160pt of band sat empty
  beside it. Merging is how the bands that already looked right were built.
- **Short headings overflow; long prose wraps - and set wrap BOTH ways.** Unwrapping everything on a
  band row pushed a 767-char tab description off the side of the sheet. Refraining from touching
  prose is not enough either: once an earlier run turned its wrap off, an idempotent pass has to
  turn it back ON, not merely leave it alone.
- **Cap the longest-WORD width floor.** The floor exists so a header does not stack one word per
  line, but identifiers like `Import_Payroll_Input` and long XPath strings inflated it until a
  block's floors exceeded its total width - so the block was silently skipped and its worst column
  stayed at 10.7 lines. Excel will break a pathological token; cap the floor around 22 width units.
- **Set the PRINT AREA to the content.** `WD Solution - O4I`'s used range runs to column 96 while its
  content ends at J, so fit-to-one-page-wide scaled the sheet down to fit ~86 empty columns - it
  rendered unreadably small in the left quarter of the page, and any PDF sent to a client had it.
- **Never delete embedded objects before their replacements are proven.** Deleting nine embeds
  first, then discovering `OLEObjects.Add(Filename=...)` failed for every path, left no way back.
- **Historical text is not stale text.** A Version Control log describing what v0.1 did must keep
  saying "20 columns" even after the layout reaches 27. Fix live content; leave the log alone.

## Reporting

Report the gate result with the deliverable: which gates ran, what they found, what was fixed, and
anything knowingly left. Silent truncation ("top 10 fixed") reads as "all clean" - say what was
dropped.

## Calibrated against a human-cleaned reference (2026-08-06; WIRED IN + render-verified 2026-08-10)

The author cleaned the same IDD by hand and the diff exposed four rules the automated pass had
WRONG. These are the difference between "every cell fits" and "looks finished". Rules 1-3 are now
implemented and confirmed by rendering six tabs against the reference; rule 4 is an open aesthetic
decision. The tunable numbers live in the brand profile (`rhythm`, `col_roles`), not in code.

**1. A table body gets ONE uniform row height - do not fit each row to its own content.**
Per-row fitting produced 41.2 / 54.0 / 55.0 / 66.8 / 79.5 down a single File table; the reference
sets every body row to 41.2. Ragged heights read as sloppy even when no cell is clipped, and this is
the single biggest reason output still "looks rough" after all the other gates pass. Fit the height
to the WORST row in the table, then apply it to every body row in that table.
STATUS: wired in `xlsx_normalize_layout.py` (per-table worst-row level, `ESCAPE_PT` excludes
multi-line narratives). Only ever GROWS a row, so the grow-only format gate leaves it alone.

**2. Structural rows are TALLER than the automated pass made them.** Measured from the reference:
    section band     47-54 pt   (pass produced 15.8-28.5)
    sub-section      28.5 pt    (pass produced 16.5)
    column header    41.2 pt    (pass produced 28.5)
    body row         41.2 pt uniform
Headings need vertical presence; a 15.8pt band is a coloured line, not a heading.
STATUS: wired as RATIOS of the table's worst body row (`rhythm` in the profile: band 1.3 / header
1.0 / sub 0.7), so they self-scale with the type scale. A band/rule takes the body of the first
table beneath it in its block (`body_below()`).

**3. Prose columns want far MORE width than an even minimax split gives them.** On File the
reference widened "Purpose to Integration" 27.9 -> 65.9 and "Special Error Handling" 19.9 -> 46.4,
while narrowing short-label columns (B 18.7 -> 11.3, D 18.7 -> 11.3). Minimising the worst column
across the block spreads width too evenly: short-label columns do not need parity with prose
columns. Weight the allocation toward the long-text columns and let label columns go narrow.
STATUS: wired in `xlsx_balance_columns.py` as ROLE-weighted allocation (prose 3.41 / name 1.03 /
label 1.0 / flag 0.55 in the profile's `col_roles`), role read from the header text via the shared
`xlsx_col_roles.py`. Content length is a bounded within-role tiebreaker only. Replaced minimax.
BAND-LABEL + LONE-PROSE (added 2026-08-10): a column whose only label sits on the section BAND
row (e.g. `Requirements!J` "Notes") is now classified too - short single-column band labels are read
as headers, and a directly-placed band label OVERRIDES a header-fill label that merely BLED onto the column
from a wide merge anchored elsewhere (Requirements' "Added to Test" header was merged H:R and covered
J). A lone prose column (a side callout that forms a one-column block) gets panel width (`NOTES_MIN`)
instead of being skipped as a <2-column block, so the "Notes" callout is a usable panel, not a sliver.
SUPERSEDED AS THE DEFAULT (2026-10-18): those proportions now live in the builders' widths (IDD
`TAB_WIDTHS` are the hand-cleaned master's numbers). Re-allocating a tuned template by header keyword
undid them: 108 changes on a fresh IDD, 76 on an Extend doc, Custom Object's L/M swapped. Balance now
defaults to `--mode relieve`: widths are intent, and width moves only into a column whose content
needs it (G12), paid by flag columns first. A second pass moves only IDLE width (width a column does
not use) to cut-off text or text wrapping past 3 lines, never from a prose or empty column. Roles are
read per TABLE, and the band label rule applies only to a one-column block. Role-weighted
re-allocation stays available as `--mode reallocate`.

**4. A prose-only tab can be a shaded PANEL, not white paper.** The reference fills the whole READ ME
instruction block (rows 3-19) with the header fill, turning it into one callout card. The automated
pass had neutralised it to white. On a tab with no tables, a single panel fill reads better than bare
white - but note this competes with the contrast gate, so panel fill + body text must still pass it.
STATUS: DECLINED 2026-08-10 (author's call). The contrast gate already yields a clean, readable
READ ME on white that matches the reference geometry within rounding, and a fill behind body prose
risks the very contrast problem the gate fixes. Prose-only tabs stay on white; `tab_treatment` in the
profile carries no panel entry. Re-open only if a future brand explicitly wants the panel look.
FOLLOW-UP: "all white" also means NO GRID. Excel's default gridlines still showed on-screen (they do
not print, so PDFs looked fine), so `reset_views.py` now sets `DisplayGridlines = False` on every
sheet - the design system paints its own white canvas and intentional borders, so the default grid is
just noise everywhere, most obviously on a prose-only tab.

**Method note:** ask for a hand-cleaned copy of the same document and diff row heights, column widths
and per-row fills against it. Eleven rounds of prose feedback produced less than one structural diff.
Two reusable harnesses came out of this: a per-tab col-delta/row-delta/distinct-height comparator and a
named-tab PDF renderer (RENDER AND LOOK is the final arbiter - the numbers only rank candidates).
