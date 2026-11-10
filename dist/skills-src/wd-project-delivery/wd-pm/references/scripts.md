# Scripts this skill uses - regenerate-on-demand build-spec

`generate_project_plan.ps1` does not ship as a file (it lived in the author's `Pilot Project
Management\` folder and carries a hardcoded task set). If it isn't on your machine, Claude
regenerates an equivalent from the build-spec below, re-supplied with your project's tasks.
Setup is in `wd-extend-lifecycle/references/prerequisites.md`. **Windows-only** - it drives
Excel via COM; on Mac/Linux ask Claude for the `openpyxl` variant (same tab structure/styling,
no COM). Cross-reference: `project-plan-format.md` (the 5-tab format + Smartsheet import).

---

### generate_project_plan.ps1 - build a multi-tab Master Project Plan workbook via Excel COM
- **Language / runtime:** PowerShell 5.1 driving Excel via COM.
- **Third-party deps:** Microsoft Excel installed (COM `Excel.Application`). No modules.
- **OS constraints:** Windows-only (desktop Excel + COM).
- **Inputs:** No args. Task data is hardcoded as arrays of `[PSCustomObject]` (one per use case) plus a master-timeline milestone array; output folder is a hardcoded `$outputBase`. (When regenerating, pass the real tasks/milestones in.)
- **Outputs:** `Master_Project_Plan.xlsx` (SaveAs format `51` = .xlsx) in `$outputBase`. Stdout: "Saved: <path>".
- **Method:**
  1. Create hidden Excel (`Visible=$false`, `DisplayAlerts=$false`); add workbook; delete extra sheets to 1.
  2. `Build-Sheet($ws,$name,$tasks)`: name the sheet; write an 11-column header (`ID, Task Name, Phase, Level, Assigned To, Duration (Days), Start Date, End Date, Predecessors, Status, Notes`) bold, fill `0x2F5597`, white font.
  3. Loop task objects into rows (Status default "Not Started"); hierarchy formatting: Level 1 = bold + fill `0xBDD7EE`; Level 3 = indent 2; else indent 1. AutoFit columns.
  4. Four task datasets (first on sheet 1, rest appended via `Sheets.Add` after the last), each via Build-Sheet.
  5. Add a MASTER TIMELINE sheet: 7-col header (`Use Case, Phase, Milestone, Target Date, Owner, Status, Notes`), header fill `0x1F3864`.
  6. Write milestone rows; bold + green fill `0xE2EFDA` any row whose Milestone matches `*GO-LIVE*` or `*PILOT*`. AutoFit.
  7. Move MASTER TIMELINE to first tab.
  8. `SaveAs($path, 51)`, `Close($false)`, `Quit()`, release the COM object.
- **Key constants:** header fills `0x2F5597` (task sheets) / `0x1F3864` (master); Level-1 fill `0xBDD7EE`; go-live/pilot fill `0xE2EFDA`; white font `0xFFFFFF`; SaveAs code `51` (xlOpenXMLWorkbook). Note: COM `Interior.Color` is **BGR**-ordered - these literals are read BGR by Excel.
- **Gotchas:** release the COM object and `Quit()` or Excel lingers. Use `Value2` for data, `Value` for headers. Sheets added positionally with `[System.Reflection.Missing]::Value`. The four datasets are a one-off; the reusable engine is `Build-Sheet` + the styling conventions.
- **Regeneration confidence:** High for the engine/formatting; the hardcoded task lists (dates, predecessors, owners) are project-specific and must be re-supplied.
