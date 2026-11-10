# Scripts this skill uses - regenerate-on-demand build-spec

`convert_md_to_docx.ps1` does not ship as a file (it lived in the author's `Pilot Project
Management\` folder). It's a content-agnostic converter, so Claude can regenerate it cleanly
from the build-spec below. Setup is in `wd-extend-lifecycle/references/prerequisites.md`.
**Windows-only** - it drives Word via COM; on Mac/Linux ask Claude for a `pandoc` or
`python-docx` variant. For styled output, formatting still comes from
the `docx` skill - this converter just does the Markdown->Word structural conversion.

---

### convert_md_to_docx.ps1 - batch-convert Markdown files to formatted Word `.docx` via Word COM
- **Language / runtime:** PowerShell 5.1 driving Word via COM.
- **Third-party deps:** Microsoft Word installed (COM `Word.Application`). No modules.
- **OS constraints:** Windows-only (desktop Word + COM).
- **Inputs:** No args. Recursively globs `*.md` under a hardcoded `$baseDir`, excluding `README.md`; each read as UTF-8. (When regenerating, parameterize the input path/glob.)
- **Outputs:** One `.docx` per `.md` (same path, extension swapped). Stdout: per-file progress + final count.
- **Method:**
  1. Create hidden Word (`Visible=$false`, `DisplayAlerts=0`).
  2. `Write-InlineText`: split on `**` to toggle bold; strip backtick code spans to plain; type runs via `Selection.TypeText`.
  3. `Add-WordTable`: drop separator rows (`|---|`), split pipe rows into trimmed cells, `Tables.Add` with style `Table Grid`, header row `HeadingFormat=-1`, cells via `Cell.Range.Text`; bold header with shading `0x2F5597` + white font; move past the table.
  4. `Convert-MdToDocx`: new doc, Normal style Calibri 11, iterate lines through a small state machine.
  5. State machine: YAML front matter (first two `---` skipped; 3rd+ = HR); fenced code blocks (```) -> Courier New 9; pipe tables (buffered, then flushed); ATX headings `#`-`####` -> Heading 1-4; bullets `-`/`*` (indent >=2 -> List Bullet 2); numbered -> List Number/List Number 2; blanks; normal paragraphs.
  6. Flush any trailing table; delete a trailing empty paragraph; `SaveAs([ref]$docxPath,[ref]16)` (wdFormatDocx).
  7. After all files, `Quit()` + release the COM object.
- **Key constants:** table/header shading `0x2F5597`, white font `0xFFFFFF`; body Calibri 11, code Courier New 9; SaveAs format `16` (wdFormatDocx); `HeadingFormat=-1`/`Font.Bold=-1` = true (Word COM boolean); `MoveDown(5,1)` (wdByRow) to exit tables; front-matter counter: occurrences <=2 are fences, 3rd+ is an HR.
- **Gotchas:** Word COM booleans are `-1`/`0`, not `$true`/`$false`. `SaveAs` needs `[ref]` args in PS 5.1. Read files as UTF-8 for special chars. Release COM + `Quit()`. Write table cells via `Cell.Range.Text` (direct `.Text` on cells is flaky). Content-agnostic - driven by whatever `.md` files exist (no hardcoded content).
- **Regeneration confidence:** High - self-contained, content-agnostic; only the Markdown-subset coverage and COM constants must be reproduced.
