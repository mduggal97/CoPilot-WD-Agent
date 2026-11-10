# EIB (Enterprise Interface Builder) - inbound and outbound walkthrough

EIB is the wizard-driven, no-code integration type: one data source, one (optional)
transform, one endpoint per direction. Naming lives in [integration-naming.md](integration-naming.md),
builder gates in [integration-build.md](integration-build.md), the reviewer's scorecard in
[integration-review.md](integration-review.md). This file owns the EIB-specific anatomy.

## When EIB (vs Core Connector vs Studio vs O4I)

Workday's tool-selection priority (doc-sourced, per "Creating and Securing Integrations"
course manual, Jul 2026): 1) end-to-end vendor connector -> 2) Core/generic connector ->
3) Orchestrate -> 4) Connector + Document Transformation -> 5) Studio. EIB sits beside
that ladder as the answer when the need is a single document, a single transform, and a
single endpoint - a spreadsheet load, a scheduled report extract to SFTP. The moment you
need multiple sources, per-row branching, retries, external HTTP, or streaming over huge
files, move up the ladder - the full chooser is in [studio.md](studio.md) "When to choose
Studio". Cost note: EIB API metering (what counts toward Flex Credits) is owned by
`wd-estimate/references/flex-credits.md`.

## INBOUND EIB - end to end

### 1. Create and pick the web-service operation

Create EIB task -> Inbound -> select the web-service operation the load will call.
Operation-name convention (house rule, owner-confirmed): `Import_*` operations are the
BULK/file convention - asynchronous, high-volume, results land in an Import Process;
`Submit_*` and `Put_*` are interchangeable names for the SINGULAR-transaction convention -
one request per business transaction, synchronous errors. Prefer `Import_*` when it exists
for your object and volumes are real; the singular ops are fine for low-volume maintenance
loads. Inventory what an ISU can call via [wws-catalog.md](wws-catalog.md).
(official-docs - developer.workday.com / public WWS docs, 2026-08-25): the Import_* semantics
are officially stated PER-OPERATION in the public WWS service docs - e.g. Payroll v46.2
Import_Payroll_Input = "bulk add/update... from external systems", Import_Payroll_Off-Cycle_Payment
= "asynchronous request mode", Import_Maintain_Payroll_Reporting_Codes = "High Volume Web Service
task"; some Import_ ops load with automatic approval (bypassing BP routing). No global
naming-convention page exists, so the rule stays a house convention - but with official
per-operation backing.

### 2. Generate the spreadsheet template

Generate Spreadsheet Template produces the workbook keyed to the operation and WWS version.
Verified template shape (local-verified, firm training set - accounting-journal and
maintain-contact-info demo workbooks):

- An **Overview sheet**: operation description plus Business Process columns - Business
  Process, Processing Instruction (e.g. Automatic Processing), Processing Comment.
- **One data sheet per top-level data area.** Header block is 5 rows: row 1 = operation
  title; row 2 = "Area" (the element path each column belongs to); row 3 = "Restrictions"
  (Required/Optional); row 4 = "Format" - either a primitive (Text, Y/N, YYYY-MM-DD,
  Number (26,6)) or a **Reference-ID type name** (Employee_ID, Company_Reference_ID,
  Currency_ID, Ledger_Account_ID) telling you exactly which ID type to paste; row 5 =
  "Fields" (column labels, `*` marks keys). Data starts row 6.
- **Row linkage:** a "Spreadsheet Key" identifies each transaction; parent/child sheets
  join Header Key -> Line Key (journal header sheet -> journal-lines sheet); repeating
  nested elements on one sheet use Row ID columns (`21120-1` style suffixes).

The tenant object behind the template is the **EIB Template Model** - Ref ID
`<INT ID>_EIB_TEMPLATE_MODEL`, display `<INT ID> {Web Service}` (house rule,
integration-naming.md). Versioning discipline: the template is generated against a specific
operation + WWS version; when either changes, REGENERATE and re-issue - do not let business
users keep filling a stale copy (see troubleshooting).

### 3. Or: custom transformation instead of the spreadsheet

An inbound EIB can instead retrieve an external file and run a custom XSLT that emits the
WWS requests itself. Verified shape (local-verified, firm training set - wellness-data
demo): the stylesheet matches the external root, loops the source records, and emits one
`<bsvc:Put_Worker_Wellness_Data_Request bsvc:version="vNN.0">` element per record, all
wrapped in a dummy `<root>` element; each emitted request is one transaction. Pin
`bsvc:version` explicitly. XSLT version caveat: EIB historically supports XSLT 2.0 only -
avoid 3.0-only features in EIB transforms (house rule, [xslt3.md](xslt3.md) "Where XSLT
3.0 runs"). Retrieval config (endpoint, SSH keys, retention, compression, decryption key)
per integration-build.md; keys via wd-deployment tenant-task-recipes R9.

### 4. Validate, then load

Launch EIB offers a validate-only mode (the same Field_Override_Data toggle the
`Launch_EIB_Request` web service exposes as Validate-Only; Studio hits the equivalent WWS
switch with the `X-Validate-Only` header - local-verified via WriteLaunchEIBRequest.xsl).
House discipline: EVERY first run of a new file is validate-only; only load after a clean
validate. Validate-only exercises schema and reference resolution; business-process and
condition-rule outcomes still only surface on a real load (!) verify in-tenant.

### 5. The LAUNCHING-USER security trap (expanded)

EIBs have **no independent permissions** - no ISU runs them by default. An EIB assesses the
security of whoever launches or scheduled it, including contextual filtering (doc-sourced,
"Security for Administrators" course manual; house rule in integration-build.md). What that
means in practice:

- An inbound EIB run by a human loads with THAT person's access: they need Put on the
  relevant domain and possibly "Initiating Action (Web Service)" on the BP security policy.
  Users who CONFIGURE EIBs also need Modify on the Integrations: EIBs domain (doc-sourced).
- Two people can run the identical file and get different results - contextual security
  filters rows silently.
- To make runs deterministic, run the EIB AS the ISU: schedule it (or transfer an existing
  schedule) so the ISU is the owner - Scheduled Future Processes report -> related action ->
  Transfer Ownership (doc-sourced); the ISU needs Modify on Integration Event. Test the
  ISU's access before go-live by launching a validate-only run under an ISU-owned schedule
  and diffing against an admin-run baseline (!) verify in-tenant.

### 6. Error surfacing - where messages land

- **Singular ops (Submit_*/Put_*):** per-transaction errors land as messages on the
  integration event - View Background Process, Messages tab (doc-sourced).
- **Bulk ops (Import_*):** the EIB event completing only means the file was SUBMITTED; the
  actual load is an asynchronous Import Process. Harvest results via `Get_Import_Processes`
  (status) and `Get_Import_Process_Messages` (row-level errors). When requests were batched,
  reconcile a returned `Line_Number` back to the true source row with the
  `Row_Number mod batch-size` idiom - [xslt3.md](xslt3.md) error/audit framework
  (BuildSingleError) and [studio-patterns.md](studio-patterns.md) WWS import framework.
- Event statuses: Completed / Completed With Errors / Completed With Warnings / Failed /
  Aborted (doc-sourced, "Creating and Securing Integrations").

## OUTBOUND EIB - end to end

1. **Data source = a web-service-enabled custom report (RaaS).** Report gates (house rule,
   integration-build.md): share with the security group AND the ISU, transfer ownership to
   the ISU; population logic in calculated fields, not raw report filters. The report's
   RaaS namespace is `urn:com.workday.report/<ReportName>`; rows arrive as
   `wd:Report_Data/wd:Report_Entry` (local-verified in the training XSLs).
2. **Transformation.** Delivered alternate output formats (CSV, XML variants) cover simple
   cases; **Custom Report Transformations** are the tenant-config way to format COLUMNS on
   an outbound EIB - not XSLT, not DT (house rule, wd-deployment migration-checklist.md).
   For real reshaping attach a custom XSLT via Create XSLT Attachment Transformation
   (Ref ID per integration-naming.md). Verified transform idioms (local-verified, training
   XSLs): `method="text"`, explicit CRLF variable, per-row `for-each` over
   `wd:Report_Entry`, Reference-ID pick via `wd:ID[@wd:type='Employee_ID']`, display name
   via `@wd:Descriptor`, `substring(wd:Day1,1,10)` to strip time/offset from dates, and
   mask-then-substring for sensitive IDs. XTT/ETV annotation-driven flat files:
   [xslt3.md](xslt3.md).
3. **Delivery.** Create SSH/PGP keys BEFORE the delivery config (house rule,
   integration-build.md; key recipes: wd-deployment tenant-task-recipes R9). Email and FTP
   transports REQUIRE PGP encryption (doc-sourced) - an unencrypted email EIB needs a
   security-admin override on every edit. Delivery BPs get Environment Restrictions with at
   least PROD + non-PROD endpoints (integration-build.md).
4. **Scheduling.** Frequencies from every-5-minutes to monthly, plus Dependent (on another
   integration reaching Completed / Completed with Warnings) and Custom Recurrence; max 5
   scheduled instances beyond calendar year-end; Catch Up Behavior None or Run Once
   (doc-sourced). Transfer schedule ownership to the ISU (see the trap above) so a
   departing employee does not break the run. Schedule naming: integration-naming.md.

## Launching an EIB from another integration

`Launch_EIB_Request` (WWS Integrations service) launches an EIB programmatically, passing
the file as base64 `Attachment_Data` and toggles (Validate-Only, spreadsheet mode) as
`Field_Override_Data`. The reusable request-builder XSLT is WriteLaunchEIBRequest.xsl
([xslt3.md](xslt3.md) worked-example library); the full submit-many-EIBs Studio design
(unzip -> per-file launch -> harvest each event WID) is [studio-patterns.md](studio-patterns.md)
section 1. O4I can drive the same WWS import loop natively - see studio.md item 4.

## Troubleshooting (sourced entries only)

| Symptom | Likely cause | Fix |
|---|---|---|
| Outbound file is empty or missing rows | Report not shared with / owned by the ISU, or the launching user's contextual security filters rows | Share + transfer report ownership to the ISU; run under the ISU-owned schedule (house rule, integration-build.md) |
| Same file, different results per person | Launching-user security (EIBs have no own permissions) | Run as the ISU; stop ad-hoc human launches for production loads |
| Load errors on columns that used to work | Template drift - spreadsheet filled against an old template model or WWS version | Regenerate the spreadsheet template; re-key data; version the Template Model per integration-naming.md |
| Import_* event Completed but no data visible | The load is an async Import Process, not the EIB event | Check Import Process status/messages (Get_Import_Processes / Get_Import_Process_Messages) |
| Validate-only passed, real load fails | Validation does not exercise BP/condition outcomes (!) verify in-tenant | Test a small real load in a non-PROD tenant before full volume |
| Scheduled EIB stopped after a departure | Schedule owned by the departed user | Scheduled Future Processes -> Transfer Ownership to the ISU (doc-sourced) |
| Edit blocked on an email-delivery EIB | Unencrypted email transport requires a security-admin override | Add PGP encryption (doc-sourced; integration-build.md) |

Build gates + retention defaults: integration-build.md. Reviewer checklist:
integration-review.md. Functional testing ownership: wd-testing.
