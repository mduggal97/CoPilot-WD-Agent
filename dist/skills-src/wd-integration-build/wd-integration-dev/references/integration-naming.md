# Integration naming standards - INT IDs, ISUs, ISSGs, calc fields, and friends

Naming is what makes an integration searchable and migratable: every object carrying the integration's ID means one search finds the whole footprint, and the INT prefix gates tenant migration. The firm naming-standards document - **regenerate a vendor-neutral master via `scripts/build_naming_standards_doc.py`** (spec in `scripts.md`; reproduces the full section outline + all reference tables), then keep it neutral, or obtain the firm's branded master per engagement. The upstream Workday guidance lives on **Workday Community** (search "Integration Naming Standards") - it is **access-gated content; do not bundle or redistribute Workday's document** (especially in anything shared with a client). Reference it by link and regenerate the vendor-neutral master here instead. Per client, the client's own standard wins if one exists - capture it during discovery.

## Integration IDs

- `INT` + 3-digit number (Community allows 4), NO space: `INT123`. When HR and FIN are both implemented: HR `INT0001-INT1000`, FIN `INT1001-INT2000`.
- Integration-specific objects carry the full ID; objects shared ACROSS integrations use the bare `INT` prefix.
- Connected integrations share the base ID with type distinguishing them; multiples of the same type get an alpha suffix; the initiating one may carry "START HERE": `INT001 CCW Vendor X Outbound START HERE`, `INT001a DT Vendor X Outbound`.

## Core name patterns

| Object | Pattern | Example |
|---|---|---|
| Integration System | `<INT ID> <Vendor/Target> <Description> <Type> <Direction>` | `INT050 ICIMS Employee Hire Studio Inbound` |
| ISU | `ISU <INT ID> <Description> <Type> <Direction>` (matches the integration system name) | `ISU INT005 TIBCO Studio Outbound` |
| ISSG | `ISSG <INT ID> <Description> <Type> <Direction>` (Community variant ends in Get/Put) | `ISSG INT005 TIBCO Studio Outbound` |
| Calculated field | `CF <INT ID or INT> <Type abbrev> <Description>`; `RCF` if report-specific | `CF INT123 LRV Manager ID` |
| Custom report | `CR <INT ID> <Description>` | `CR INT123 Workers Not Paid in Prior Pay Period` |
| Encryption key | `EK <INT ID> <Key Type> <Audience>` (SSO/SLO/DelAuth in place of INT ID for non-integration keys) | `EK INT005 PGP Public` |
| XSLT file | `<INT ID> <Description> <Type> <Direction> <Version>.xsl` | `INT005 TIBCO Studio Outbound v1.xsl` |
| File utility | `<INT ID> Filename <Description> <Direction>` (File Name must match the sequence generator name if one exists) | `INT005 Filename TIBCO Outbound` |
| Sequence generator | `<INT ID> <Integration System> <Purpose>` | `INT001 Cigna Medical Output File` |
| Integration services | `INTXXX-Reports`, `INTXXX-Delivery`, `INTXXX-Retrieval`, `INTXXX-Attributes-Generic`, `INTXXX-Maps-Generic`, `INTXXX-LaunchParameters-Generic`, `INTXXX-Sequences`, `INTXXX-Transactions` (no spaces; consolidate all reports on ONE report service); custom-object service `INTXXX-Custom` / `INTXXX-<Description>-Custom`; service reference `INTXXX-Field-Override-Reference` | - |
| Security segment | `<INT ID> Security Segment <Identifier>` | `INT005 Security Segment Payroll Integrations` |

## Per-environment, template-model, and schedule names

Some objects exist once **per environment** or carry extra slots the core table doesn't show:

| Object | Pattern | Note |
|---|---|---|
| File name (per env) | display `<INT ID> FileName <Vendor> <Desc> <Type> <Dir> <ENV>`; Ref ID `<INT ID>_FileName_<Vendor>_<Desc>_<Type>_<Dir>_<ENV>` | `<ENV>` = IMPL / SBX / PRD - one object per environment |
| Sequence generator (per env) | display `<INT ID> SeqGen <Vendor> <Desc> <Type> <Dir> <ENV>`; Ref ID `<INT ID>_SeqGen_..._<ENV>` | `<ENV>` = IMPL / SBX / PRD |
| EIB Template Model | display `<INT ID> {Web Service}`; Ref ID `<INT ID>_EIB_TEMPLATE_MODEL` | the template-model object behind a spreadsheet EIB |
| Schedule | display `<INT ID> <Vendor> <Desc> <Type> <Dir> (<Schedule>)`; Ref ID `<INT ID>_<Vendor>_<Desc>_<Type>_<Dir>_<Schedule>` | schedule label in parentheses on the display name |
| Encryption key (with expiry) | display `EK <INT ID> <KeyType> [ExpiryDate]`; env-specific `EK <INT ID> <ENV> <KeyType> YYYYMMDD` (ENV = QA or PR) | ExpiryDate = create date + 3 years (see the x509 3-year rule below) |

- **Log / output file names must include a date or datetime stamp** in any reasonable format; a time
  component is only required when the integration runs multiple times per day.
- **Ref IDs use underscores only** (no spaces, no special characters); display names use spaces between
  tokens. A truncated Ref ID in a PDF export - assess pattern correctness, not character length.

## Direction values

`Inbound`, `Outbound`, and `Bidirectional` are all valid direction components - do **not** flag a name
for using `Bidirectional`. (Boomerang is a design pattern, not a direction token - see studio-patterns.md.)

## Integration type abbreviations (the `<Type>` slot)

EIB, Studio, DT, O4I, CCB (CC: Benefits), CCW (Worker), CCP (see discrepancies), CCJP (Job Postings), CCJPJF (Job Profile and Job Family), CCJR (Job Requisitions), CCL (Location), CCO (Organization), PICOF (Payroll Interface), PECI, WECI.

## Naming rules (both sources agree)

- Title case, descriptive not vague, spaces in Integration System names (Studio PROJECT names use dashes, no spaces), spell out "and", no hyphens/underscores as word separators, avoid abbreviations, no customer identifiers in object names.
- Reference IDs: letters/numbers/underscores only, other chars -> underscores, no leading zeros; Workday compares them case-insensitively.
- Temporary/do-not-use objects: **`DNU` prefix FIRST** (`DNU INT001 ...`) - never buried mid-name. Deactivate/rename ISSGs with DNU; never delete.
- One ISU per integration system; report owner = the ISU; share reports with Implementers + Integrations Administrator + the ISU. Share with security groups, never individual named users (position changes break named-user sharing).
- Notification configured on EVERY integration system (and each system in a chain), using the standard calc fields `CF CT Integration Notification Message Content - Subject` / `- Body`.
- Update reference IDs on ALL of: PGP keys, integration service components, custom report data sources, integration BPs, sequence generators, file utilities, transport protocol. Configure Environment Restrictions wherever possible (build details: integration-build.md).
- No sensitive values in reference IDs - RaaS appends them as URL parameters, so they travel in the clear.
- x509 private keys: set 'Valid To' three years from creation.
- Integration report prompts: set default values wherever possible; multi-select prompt labels end `(s)`; optional prompts end `or leave blank for All`.
- Research-only reports: tick Temporary Report (expires in 7 days - the default, changeable on the Advanced tab for all report types except simple). Expired definitions are **never deleted automatically** - actual deletion requires someone running **Delete My Temporary Report Definitions** or an admin scheduling **Delete All Temporary Report Definitions** - confirm the client schedules it. Per Workday Admin Guide (Reporting & Analytics), Jul 2026.

## Report lifecycle facts (per Workday Admin Guide (Reporting & Analytics), Jul 2026)

- Ownership transfer: **Transfer Ownership of Custom Reports** task (new owner must have access to the report data source and its data-source filter; previously-shared users keep access); **Transfer Ownership of Report Group** requires the Custom Report Administration + Manage: All Custom Reports domains.
- Sharing is governed by three domains (Report Definition Sharing - All Authorized Users / Specific Groups / Specific Users); **simple reports can't be shared at all**.
- Deletion guardrails: reports used in business-form layouts, BP steps, other reports, report groups, or scheduled future processes can't be deleted; prod deletions are unrecoverable (the sandbox copy survives only until the weekly refresh).
- RaaS namespace (`urn:com.workday.report/...`) stays stable across report rename/owner change, but is **editable with no uniqueness check** - treat a namespace edit as a breaking change to every consumer. The REST RaaS URL embeds the **owner's username** (and breaks if it contains a backslash) - one more reason the ISU owns the report.

## Studio object naming

Components meaningful camelCase (`aggregateRecords`); Local-Out `call-[Local-In name]`; integration attributes `ia.` prefix lowercase dotted (`ia.sftp.endpoint`); launch parameters `lp.` prefix (`lp.start.date`); MVEL vars lowercase dotted; maps/lists include the type in the name (`props['union.names.map']`); XSL/XSD files lowercase with underscores (`format_final_rows.xsl`); XSLT functions in a `this:` namespace; enums `Enum_<Description>`.

## Tenant-wide naming (same firm standard, beyond integration objects)

The bundled docx covers whole-implementation naming; the distillation (all formats below are the template's sample defaults - confirm per client):

- **Reference IDs (all config):** Title Case words joined by underscores; letters/numbers/underscores only; collapse consecutive underscores; no leading zeros. Assign ref IDs to ALL configuration before any tenant-to-tenant move - auto-assigned IDs from different tenants can collide and corrupt shared config (condition rules especially). Review via the View/Maintain Reference IDs tasks and the Integration IDs report.
- **Codes:** number sequentially - no smart numbering, no descriptive text as the code (reorgs break both). An alpha prefix (`CC1000`) makes search unambiguous. Organization Codes are indexed/searchable; plain reference IDs are not. Never change a code/ref ID that external systems already use.
- **Org/Worktag ID formats:** Company `CO1n`, Cost Center `CC1nnn`, Program `PG1nnnn`, Fund `FD1nn`, Project `PJ1nnnnn` (auto sequence), Grant `GR-yyyy-nnnn` (auto sequence), Revenue Category `RC1nnnn`, Spend Category `SCnnnnn`, Location `Lnnnn` (or embed an existing scheme as `Building_Floor_Room`). Where an object has both, keep Organization Code = Reference ID. **Custom-org prefixes follow the same 2-letter+digits shape, named for whatever the client segments by** - e.g. higher-ed: school/college `SC1nn`, department `DP1nnn`; healthcare: service line `SL1nn`, facility/entity `FA1nn`; commercial: business unit `BU1nn`, region `RG1nn`. Pick prefixes that can't collide with the delivered set above; the docx's full table shows one industry's worked example - treat it as a shape to copy, not values to reuse.
- **Sequence generators:** master data = 3-char prefix + dash + digits (`CST-00001` Customer, `SUP-1000000` Supplier, `SPN` Sponsor, `AST` Asset); transactions = shorter prefix (`JE-` Journals 10 digits, `INV-` Supplier Invoices, `PO-`, `EXP-`); bank-file EFT payments get NO prefix. Full FIN + HCM tables in the docx. Set up sequence generators FIRST in a tenant build; reset counters when migrating them.
- **Condition rules:** name = what the rule is used for, led by the object/functional area (`Customer Invoice Validation`, `Grant is Tagged`); define on the broadest object possible (Taggable); reference ID mandatory; assign at least one condition rule category (add missing ones via Maintain Condition Rule Categories).
- **Calculated fields (non-integration):** `CF - <Team> - <Object> - <Type> - <Description>` (`CF - HCM - Worker - ESI - Most Current Certification`). Never modify a calc field you didn't create or that's in use - copy it instead; copy-and-rename WDSETUP calc fields before changing (reloading factory defaults overwrites edits). Set the ref ID manually equal to the field name (Workday doesn't update auto ref IDs on rename); assign Category values on the Additional Info tab. Integration calc fields stay integration-specific (INT ID in the name), never shared with functional reporting; report-specific `RCF` is preferred unless the field is reused across reports.
- **Custom reports (non-integration):** `CR <Functional Area> <Description>` (`CR PAY Workers Not Paid in Prior Pay Period`); stand-alone end-user reports may use `<Data Source> - <Description> - <Intended Audience>`. A custom report's ref ID = name + owner - no manual ref ID needed.

## Known discrepancies (resolve per client, note the choice in the IDD)

- `CCP` = Core Connector: Positions (firm standard) vs Cloud Connect for Payroll (Community).
- ISSG direction suffix: Get/Put (Community) vs Inbound/Outbound-style (firm examples).
- Calc-field abbrev #25: `LVA` Lookup Value As Of Date (firm standard) vs `LVD` (Community). The 32-type list is otherwise identical.

## Calc-field type abbreviations (the 32)

ARI, AC, BD, CT, CC, CTN, CRI, DC, DD, EE, EMI, ESI, FD, FN, FT, IDD, LDR, LH, LHR, LO, LOR, LRB, LRV, LTV, LVA/LVD, NC, PV, ST, SRI, TC, TL, TF (+ FIN-side extras seen in the firm doc). Full expansion table lives in the bundled docx.

## Extend/O4I apps delivered as INTs

O4I integrations tracked under an INT number follow these patterns for their tenant-side objects (Integration System, ISU/ISSG, notifications) even though the app itself follows Extend naming (standards.md in the wd-extend-dev skill). The IDD records both.
