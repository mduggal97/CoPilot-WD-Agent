# Scripts this skill references - regenerate-on-demand build-specs

Cross-platform Python template builders that regenerate clean, **vendor-neutral** blank
versions of this skill's deployment worksheets. Run one to get a working blank; keep its neutral
formatting, or obtain the firm's branded master per engagement
(environment memory). They live in `scripts/` in this skill; if one is missing, Claude
regenerates it from the build-spec below.

- **`scripts/build_migration_checklist.py`** - Integration Migration Checklist (per-integration tenant-migration tracker).
- **`scripts/build_cutover_spreadsheet.py`** - Integration Production Run Cutover workbook (per-INT portfolio cutover).

**Runtime for both:** Python 3, third-party dep `openpyxl` (`pip install openpyxl`). Cross-platform. Setup in `wd-extend-lifecycle/references/prerequisites.md`.

---

### build_migration_checklist.py - Integration Migration Checklist workbook
- **Language / runtime:** Python 3 (`#!/usr/bin/env python3`).
- **Third-party deps:** `openpyxl` only. Stdlib: `sys`.
- **OS constraints:** Cross-platform.
- **Inputs:** CLI `argv[1]` = optional output path. Default `Integration_Migration_Checklist.xlsx` in the CWD. No other inputs - the template content is embedded.
- **Outputs:** one `.xlsx` with three sheets: **Migration Checklist** (title + 52-column header + 40 blank entry rows + freeze + status/type dropdowns), **Type Applicability** (11 integration types x the check-question columns, `x` where the check applies), **Workflow Notes** (migrator->reviewer workflow, status set, design-change-note convention, Master SFTP Tracker definition). Stdout confirmation.
- **Method:**
  1. `COLUMNS` = the adopted house ("proposed revision") column set, 52 labels A..AZ; tracking columns A..R + AY/AZ, check columns S..AX.
  2. `build_checklist_sheet`: title row 1, header row 2 (grey fill, bold, wrapped, 60px high), freeze `C3`, widths (24 for tracking, 18 for checks), 40 entry rows with thin borders.
  3. Data validations: **Is Current?**=Yes/No (A), **Integration Type**=the 11 `INTEGRATION_TYPES` (D), **Migration Status** & **INT Lead Review Status**=the 5-value status set (H, M), **Yes/No/N/A** on every check column S..AX **except** the NOTES columns.
  4. `build_matrix_sheet`: check-question labels as rotated (90deg) column headers; one row per integration type; `MATRIX` (keyed by 0-based COLUMNS index via the S/T/U... letter shorthands) marks `x`.
  5. `build_workflow_sheet`: `WORKFLOW_NOTES` list of `(text, is_heading)` written down column A at 120 width.
- **Key constants:** `MIGRATION_STATUSES`/`REVIEW_STATUSES` = "Not Started, In Progress, Migration Issue, Ready for Review, Complete"; `INTEGRATION_TYPES` (SOAP/REST/RaaS API, Packaged, Core Connector, DT, BIRT, Studio, Inbound EIB, Outbound EIB, O4I); `FIRST_CHECK_COL=19` (column S); `FULL_CONFIG`/`RAAS_BLOCK` reused across type rows in `MATRIX`; neutral header fill `D9D9D9` (NOT a brand color).
- **Gotchas:** the matrix is authored with column-letter shorthands (`S..AX`) that are **0-based COLUMNS indices** (S=18 = `COLUMNS[18]`) - if you insert/remove a column, re-derive the shorthands or the `x` marks shift. `AW` (index 48) is the free-text NOTES column and is deliberately excluded from both the Yes/No/N/A validation and the matrix check-column set. The workbook default "Document Retention set to 180 days" was generalized to "...required length" per the adopted revision. This is the tracker's column set; the source is designed as a Smartsheet with Dynamic Views (transport: `wd-smartsheet`), but the layout works in Excel unchanged.
- **Regeneration confidence:** High - column set, status values, type matrix, and validations are fully specified and embedded; only the matrix-shorthand<->index coupling needs care.

---

### build_cutover_spreadsheet.py - Integration Production Run Cutover workbook
- **Language / runtime:** Python 3.
- **Third-party deps:** `openpyxl` only. Stdlib: `sys`.
- **OS constraints:** Cross-platform.
- **Inputs:** CLI `argv[1]` = optional output path. Default `Integration_Production_Run_Cutover.xlsx`. Template content embedded.
- **Outputs:** one `.xlsx` with four sheets: **CutoverDetails** (one row/integration; 25-column A..Y layout, `Details for Vendor Communications` merged banner over K2:R2, Yes/No/n-a dropdowns on the gate/temp-file columns, 40 blank rows), **Cutover Tasks** (Integration Name / Consultant / Production Cutover Tasks / Done? / Notes; Done? = Yes/No), and an **EXAMPLE** twin of each (same headers + a yellow "delete example data" banner row + a couple of GENERIC synthetic rows). Stdout confirmation.
- **Method:**
  1. `DETAILS_HEADERS` (A..Y) and `DETAILS_WIDTHS` reproduce the source column layout: readiness gates (UAT / Moved to Gold / docs attached / GoldCopy validation), vendor-communications endpoint block (K..R), people, keys, run-sequence (last legacy run -> prerequisites -> first run in Workday).
  2. `build_details`: title (18pt), merged `K2:R2` section banner, header row 3 (grey fill, wrapped), freeze `A4`. Non-example -> Yes/No/n-a validation on `DETAILS_YN_COLS`; example -> yellow merged banner on row 4 + `DETAILS_EXAMPLE_ROWS` written from row 5, `_col_idx` maps a column letter to its 1-based index.
  3. `build_tasks`: 5-column layout, title, headers, freeze `A4`; non-example -> Yes/No on `Done?` (D); example -> yellow `A4:D4` banner + `TASKS_EXAMPLE_ROWS`.
- **Key constants:** `EXAMPLE_BANNER` text; `DETAILS_YN_COLS = B,C,G,H,I,J,Q,R`; example rows use only synthetic vendor-neutral values (`Vendor A`, `sftp://vendor-a.example.com`, generic INT001/INT002 names) - NO real vendors, clients, or endpoints; neutral header fill `D9D9D9`; yellow banner `FFFF00`.
- **Gotchas:** the four sheets must keep the two working sheets **blank** (headers only) and confine sample data to the EXAMPLE twins behind the yellow "delete" banner - never seed the working sheets. Example data is intentionally generic per the no-customer-data-in-dev-tenants rule; do not paste real cutover data into the template. `_col_idx` is a small A->1 helper because example rows are keyed by column letter.
- **Regeneration confidence:** High - the 25-column details layout, the merged banner, the 5-column tasks layout, and the example/blank split are fully specified.
