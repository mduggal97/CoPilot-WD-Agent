# The 16-tab Extend design doc - structure, styles, build method

## Tab order (exact)

`Instructions | Overview | Discovery | Requirements | Field Specifications | Data & Webservice Mapping | Object Model | Business Process Design | Security | Technical Specification | UI & Wireframes | Process Flow | Unit Testing | QA Review | Open Items | Migration Checklist`

Keep **Instructions** and **QA Review** verbatim from the template; the other 14 tabs carry app content.

## Getting a blank template

**Default: regenerate a working structural template from text** - `python scripts/build_extend_design_doc.py [out.xlsx]` (bundled, cross-platform openpyxl). It emits the full 17-tab set (this spec + KPI & Reporting), every section band / instruction row / table header, the standing Instructions + QA Review content, the Unit Testing status-summary formulas, and the yellow open-items convention, in **neutral / unbranded** grayscale. Style it afterwards with `scripts/xlsx_brand_style.py` - neutral by default, or a client profile. See [scripts.md](scripts.md) and [template-builder.md](template-builder.md). This skill no longer ships a proprietary binary master.

**Or obtain the branded master per engagement** - a branded Extend template obtained per engagement (engagement store - see the environment memory) or a client program's mandated template. Then use these as **style donors / verification refs**:

- **Blank base** - the client program's 16-tab template workbook (when the engagement mandates its own).
- **Filled reference (the style donor)** - a delivered, fully-styled design doc from the program, used to clone style objects when you want to match an existing look.
- **Style-clone generator (optional)** - `design_doc_builder.py` clones a reference workbook's style objects by role, keeps Instructions + QA Review, rewrites the other 14 tabs, embeds process-flow + wireframe PNGs. It is **NOT bundled**; (re)generate it from the build-spec in [scripts.md](scripts.md) only when you specifically need to match a donor's styling rather than the neutral/firm build above.

## The style-cloning method (do NOT hand-guess styles)

When generating or extending a doc programmatically, open a real reference workbook and **copy its actual style objects by role**: `copy.copy(cell.font)`, `.fill`, `.alignment`, `.border` from a known cell of each role (title, section band, instruction, table header, data). A first attempt that re-created the palette by eye produced a broken-looking doc; cloning is both easier and exact.

## Style spec (for verification / small manual edits)

**(!) This palette is a CLIENT-PROGRAM style** (blue `FF0070C0` title / teal `FF78DED4` bands - the format one client program mandates; template-builder.md identifies it as such). The DEFAULT is the neutral palette (band `FF1F2A37` / header fill `FFE5E7EB` - see `brands/neutral.json` and template-builder.md). Match the palette to whose template you are in - do not hand-edit a neutral doc in these client colors.

- Column A: width 3 spacer; content starts in B
- Title: merged B2:{end}, 18pt bold white on `FF0070C0`
- Section bands: 14pt bold `FF242724` on `FF78DED4`, row height 21.75
- Instruction rows: 9pt italic `FF0070C0`
- Table headers: 10pt bold `FF7F7F7F` on `FFF2F2F2`
- Data cells: 11pt with thin `BFBFBF` borders
- Always 8-hex ARGB - 6-hex fills render transparent
- One blank unformatted row between sections (see SKILL.md formatting rules)

## Tab content expectations

- **Overview**: purpose, in/out of scope, stakeholders, app identity (name, reference ID, tenants)
- **Discovery**: Q&A rows with source attribution (who answered, when); unanswered rows yellow on both question and response
- **Requirements**: numbered requirements with priority + source; these are what wd-testing traces scenarios to
- **Field Specifications**: per page/BO - field, type, required, validation, source/derivation, notes
- **Data & Webservice Mapping**: every API/WQL/RaaS/SOAP touchpoint - direction, endpoint/op, fields mapped, auth
- **Object Model**: BOs, fields, types, relationships (matches `model/` exactly - drift here breaks defect triage)
- **Business Process Design**: BP types, steps, approvers, routing, send-back behavior, notifications
- **Security**: domains, groups, who-sees-what matrix, ISU needs (feeds the security request package in wd-extend-dev's security-setup)
- **Technical Specification**: orchestrations, integrations, limits considerations (25s page-sync cap etc.), App Attributes
- **UI & Wireframes**: embedded wireframe export (wd-design-visuals; final embed must be the clean Balsamiq export)
- **Process Flow**: embedded swimlane PNG (wd-design-visuals)
- **Unit Testing**: scenario table (ID, requirement ref, steps, expected, result, tester, date) - wd-testing derives and executes
- **Open Items**: ID, raised date, owner, description, status, resolution - the row-yellow rule applies
- **Migration Checklist**: tenant promotion steps (feeds wd-deployment)

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Blank base** - the engagement's 16-tab design-doc template workbook. Obtain the branded template master per engagement, or regenerate it and keep the neutral default.
- **Filled reference (style donor)** - a delivered, fully-styled design doc from the engagement, used to clone style objects.
- **`_Design Tools\` path** - where the durable generator (`design_doc_builder.py`) lives on your machine; if absent, regenerate from the build-spec in [scripts.md](scripts.md).

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).
