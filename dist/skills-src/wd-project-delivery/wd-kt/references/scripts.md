# Scripts this skill uses - bundled template builders + regenerate-on-demand

See `wd-extend-lifecycle/references/prerequisites.md` for runtimes/packages.

This skill ships **two cross-platform template builders** (no Office/COM, no firm
branding baked in) that regenerate clean, vendor-neutral, structurally-correct BLANK
versions of the two KT templates. Branding (fonts, colours, logo, cover) is applied
SEPARATELY, per engagement, via the **docx** / **xlsx**
skills - the builders deliberately produce a neutral skeleton so branding is a later,
swappable layer. To obtain the firm's already-branded master instead of regenerating,
pull it per environment memory (see the engagement's project memory).

There is also a THIRD, non-shipped build-spec - `runbook_validator` - which lives
**inline in [triage-runbook-pattern.md](triage-runbook-pattern.md)** (section  Build-spec:
`runbook_validator`). It is cross-referenced here, not moved: regenerate it from that
section on demand; it does not ship as a file.

---

### `scripts/build_int_kt_template.py` - regenerate the Integration KT document template (.docx)
- **Status:** **bundled** (ships in this skill).
- **Language / runtime:** Python 3, `python-docx` only (no COM -> cross-platform: Windows/macOS/Linux).
- **Third-party deps:** `python-docx` (`pip install python-docx`). Stdlib: `sys`; `docx.oxml`
  (`OxmlElement`, `qn`) for the TOC field.
- **OS constraints:** none - pure `python-docx`, `.docx` only (no macros).
- **Inputs (CLI args):** `1` OUT (optional) = output `.docx` path. Default `./INT_KT_Template.docx`
  in the current directory. Content-agnostic - takes no per-app content; it emits the blank skeleton.
- **Outputs:** one blank `.docx` with the full 14-section KT skeleton + a live Word TOC field;
  stdout confirmation. It never overwrites the bundled asset unless OUT points at it explicitly.
- **Method:**
  1. `Document()` (python-docx default template - no firm styles), then a Title paragraph
     (`Title` style) + two italic `[INSERT ...]` cue lines for the cover.
  2. `add_toc()` injects a REAL Word `TOC \o "1-2" \h \z \u` field via raw OXML
     (`w:fldChar` begin / `w:instrText` / separate / placeholder `w:t` / end) so page numbers
     build on open (Update Field / F9) - this replaces the bundled template's hardcoded TOC page numbers.
  3. Helper `body(text, italic)` = a `Normal` paragraph (italic for `[INSERT ...]` editorial cues);
     `bullets(items)` = `List Bullet` paragraphs; `table(headers, blank_rows, seed)` = a `Table Grid`
     table with a bold header row, optional `seed` rows (e.g. the "Initial document" revision row,
     the ISU/ISSG description hints), then N blank rows.
  4. Emit the sections in order (skeleton table in `int-kt-template.md`): Revision History ->
     Introduction (+ session-scope bullets, High-Level Overview) -> Interface & Configuration Summary ->
     Custom Services (+ RaaS) -> Attributes -> Maps -> Web Services -> Business Process -> Security
     (ISU + ISSG) -> Launch Instructions (+ Launch Parameters) -> Scheduling (+ the 7-row Run-Frequency
     reference table) -> Periodic Maintenance -> Error Handling -> Event Review.
- **Vendor-neutral style mapping (the whole point):** the bundled master used proprietary named
  styles (`* 5 Heading 1`, `* 6 Heading Level 2`, `* 2 Body Copy`, `* 3 Bulleted List`). The builder
  maps them to python-docx **built-ins** - `Heading 1` / `Heading 2` / `Normal` / `List Bullet` /
  table style `Table Grid` - so the file carries NO firm branding and opens cleanly anywhere.
- **Key constants to preserve:** section order + table column headers exactly as in
  `int-kt-template.md`; the 7-row Run-Frequency schedule table (Run Once in the Future, Minute /
  Hourly / Daily / Weekly / Monthly Recurrence, Dependent) with its per-row schedule-criteria text
  (incl. the "End Date cannot exceed December 31 of the next calendar year" note); the "every
  integration has an ISU and an ISSG" framing; the supplement-to-session bullet list.
- **Gotchas / correctness notes:** the TOC is a FIELD, not literal text - it shows a placeholder line
  until Word updates it (expected). Newlines inside a schedule-criteria cell are real `\n` line breaks
  in one cell (do not split into rows). Curly punctuation from the original binary was normalised to
  straight quotes/apostrophes so the file is encoding-clean.
- **Verify (re-open check):** `Document(out)`; assert 15 `Heading 1` paras (TOC + 14 sections),
  9 `Heading 2`, 15 tables, and a TOC `instrText`. Confirmed: H1/H2/table counts + shapes match the
  bundled skeleton; schedule table = 8x2.
- **Regeneration confidence:** **High** - content-agnostic, fully specified by the section skeleton
  in `int-kt-template.md`.

---

### `scripts/build_kt_plan.py` - regenerate the Knowledge-Transfer Plan workbook template (.xlsx)
- **Status:** **bundled** (ships in this skill).
- **Language / runtime:** Python 3, `openpyxl` only (no COM -> cross-platform).
- **Third-party deps:** `openpyxl` (`pip install openpyxl`) - `styles`, `utils`,
  `worksheet.datavalidation`. Stdlib: `sys`.
- **OS constraints:** none - pure `openpyxl`, `.xlsx` only (no macros).
- **Inputs (CLI args):** `1` OUT (optional) = output `.xlsx` path. Default
  `./Knowledge_Transfer_Plan_Template.xlsx`. Content-agnostic - emits the blank one-sheet skeleton.
- **Outputs:** one blank `.xlsx`; stdout confirmation.
- **Method:**
  1. One worksheet renamed `<Name>` (rename / duplicate per functional area, as `kt-sessions.md` describes).
  2. Title block: `A6=[Client]`, `A7=Workday Implementation`, `A8=Knowledge Transfer Plan` (merge `A8:C8`).
  3. Status-summary block `E2:G7`: headers Status / Count / Percent; four ladder rows
     `NS: Not Started`, `U: Understood`, `D: Demonstrated`, `R: Responsible`, then Total.
     `F3:F6 = COUNTIF(H:H, E<row>)`, `F7 = SUM(F3:F6)`; `G` column = `=IFERROR(F/$F$7,0)` as `0%`.
  4. Column-header row at **row 10**, 11 columns: Knowledge Area | Related Tasks & Reports in Workday |
     Topic Description | Primary Transferor | Primary Transferee | Transfer Method | Target Completion
     Date | Status | Notes | Final Sign-Off (Transferee) | Sign-Off Date - with the measured widths.
  5. Knowledge-area section rows + blank topic rows beneath each: Core Configuration (6), Processes (2),
     Tasks (3), Reporting/Integrations (6), Documents (3) - landing the section rows at the same
     row numbers as the master (11 / 18 / 21 / 25 / 32).
  6. Status **dropdown** (`DataValidation` type `list`, `formula1="=$E$3:$E$6"`) over the topic rows
     in column H. `freeze_panes="A11"`.
- **Vendor-neutral styling (the whole point):** the bundled master used a firm blue
  (`FF136CB8`) + theme-indexed fills. The builder swaps these for a **neutral gray system** -
  `D9D9D9` band (title/summary), `BFBFBF` column-header row, `F2F2F2` section rows - plus bold + thin
  `A6A6A6` borders. No firm colour is baked in; brand recolour is a later xlsx pass.
- **Key constants to preserve:** the four-step ladder text EXACTLY (the dropdown + COUNTIF depend on
  `E3:E6` matching what's typed in column H); the 11 column headers + order; section labels + their
  landing rows; `freeze_panes A11`; row-10 height 42.
- **Gotchas / correctness notes:** the dropdown `formula1` must stay `=$E$3:$E$6` (absolute) or it
  drifts per row. COUNTIF matches on the literal status STRING, so the ladder cells and the dropdown
  list must be the same four strings - never reword one without the other. `.xlsx` (no VBA) so openpyxl
  is safe; if a future variant needs macros, switch to the COM-copy pattern (see wd-design-doc `scripts.md`).
- **Verify (re-open check):** `load_workbook(out)`; assert sheet `<Name>`, merged `A8:C8`,
  summary formulas present, 11 headers at row 10, section rows at 11/18/21/25/32, `freeze_panes=A11`,
  one `list` data-validation `=$E$3:$E$6`. Confirmed against the bundled skeleton.
- **Regeneration confidence:** **High** - content-agnostic; fully specified by `kt-sessions.md`.

---

### `runbook_validator` - cross-reference only (NOT here, NOT shipped)
Defined inline in [triage-runbook-pattern.md](triage-runbook-pattern.md) section  *Build-spec:
`runbook_validator`*. Stdlib-only Python that scores a triage runbook on the six mandatory
step attributes and blocks on any ownerless step (pass >= 80 AND zero ownerless steps).
Regenerate from that section on demand - it stays documented next to the pattern it checks.
