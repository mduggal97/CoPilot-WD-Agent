# Financials: FDM, accounting, P2P, Accounting Center - solution playbook

Foundation Data Model, financial accounting/journals, procure-to-pay, and Accounting
Center (Prism-based external accounting). Config facts: (doc-sourced - Workday Education
manuals, 2026-08-25; verify in-tenant). Web-service names: (from the in-tenant WWS
master inventory).

## 1. Configuration spine

### FDM core (companies, ledgers, worktags)

- The 13-step accounting setup sequence (documented in full in payroll.md - same FDM
  tasks): Ledger Account Types -> Account Sets -> Default Ledger Accounts -> Posting
  Rules -> Fiscal Schedule -> Posting Intervals -> Initial/Next Fiscal Year -> **Edit
  Company Accounting Details (LOCKED after the first posting)** -> Ledger Types ->
  Ledger -> Ledger Year and Periods -> Mass Update Ledger Period Status.
- Posting rule evaluation: top-to-bottom, first match wins, else default ledger account;
  missing match AND missing default = error journal.
- **Worktag usage is TENANT-WIDE per transaction type** (Maintain Worktag Usages):
  Primary worktags max 10 per transaction, orderable; required worktag missing = cannot
  save AT ALL. To require a worktag for only one company, use a Custom Validation
  (Critical = hard stop, Warning = bypassable; fires at SUBMIT; conditions evaluate in
  order, first match stops).
- **Hard worktag limits**: 15 custom worktag types PER TENANT; unlimited custom org
  types but only 10 usable as financial worktags (Financial Usage on Maintain
  Organization Types); 73+ delivered worktag types. Every organization can be a worktag;
  no worktag can be an organization. Inactivated worktags stay usable on transactions -
  enforce with custom validations or BP condition rules.
- Related worktags (Maintain Related Worktag Usage) auto-populate from the object used;
  Default Required vs Required on Transaction.

### Journal sequencing + conversion order (irreversibility cluster)

- **Journal sequencing (gapless statutory numbering) is IRREVERSIBLE once a single
  number is assigned, and cannot back-number existing posted journals -> ENABLE BEFORE
  DATA CONVERSION.** Configure only for periods in Created/Closed/Not Available status.
  Undersized sequence padding breaks sorting when volume exceeds the digits.
- Conversion split: **Put Beginning Balance Journal** - NOT affected by ledger period
  status, NO business process, subsequent loads REPLACE prior balances; vs **Import
  Accounting Journal** (historical monthly activity) - ledger period must accept
  activity, routes through the Accounting Journal Event BP (set auto-complete to
  bypass), subsequent loads create NEW journals. Custom validations do NOT apply to
  beginning-balance loads and may need temporary removal for historical journal loads.
- Suspense rules (apply to the Import Accounting Journal path): ONE suspense account
  rule per account set; the journal source must have Enable Suspense Processing plus a
  Suspense Threshold Percent - exceeding the error-line share FAILS the whole load.
- Intercompany prerequisites: Edit Company Intercompany Profile defines who can initiate
  vs settle; related companies MUST share the same account set; posting rules must cover
  Intercompany Receivables and Payables. Two flavors: On Behalf Of (auto Intercompany
  Affiliate worktag) vs Direct (real mapped customer/supplier invoices). No partial
  payments on intercompany receipts.
- Close: Roll Forward Year-End Balance replaces next-year beginning balances
  (rerunnable before close); Maintain Year-End Closing Rules redirect balances.
  Book codes: operational journals post with a BLANK book code (the Common Book).

### P2P spine

Supplier Contract -> Requisition -> Source/Create PO -> Issue PO -> Receive -> Invoice
(match) -> Settle.

- Sequence IDs REQUIRED before transacting (Edit Tenant Setup - Financials) for
  requisitions, POs, receipts, supplier contracts, supplier invoices, and more;
  company-level generators take precedence.
- Spend categories are required on all reqs/POs/contracts/invoices and drive accounting
  via posting rules; one category cannot do BOTH business-asset and inventory tracking,
  and CANNOT change from inventory to procurement usage.
- **Requisition sourcing rules match by RANKED ATTRIBUTE IMPORTANCE, not list order**:
  Purchase item > Spend category > Street address > Company. Four rule sets: Buyer,
  Supplier, Order-From Connection, Inventory Site.
- **Matching is REAL-TIME, not batch**: Supplier Invoice Match Event fires on invoice
  submission and re-runs from receipt, change order, contract amendment, and invoice
  adjustment events; always matches against the most current PO version. Config chain:
  Match Condition Rules -> Match Exception Reasons -> Match Rules -> Match Rule Sets.
  **A company ties to only ONE match rule set; a company with NO match rule set = its
  invoices skip matching entirely.** 2-way (services, bill-only), 3-way (default),
  4-way (+inspection). Delivered matching CRFs are prefixed "MR".
- Procurement conditional rules (Prevent Cancel/Close/Receipts...) hide UI actions but
  do NOT stop web services (except Prevent ASN) - guard inbound integrations with
  custom validations instead.
- External Warehouse PO type: ONLY the Submit Purchase Order web service can create
  them; stock-item lines only; no price variances.

### Accounting Center (Prism-based external accounting)

Ingest high-volume external transactions into a Prism TABLE -> enrich (worktags,
validations) -> detailed accounting -> summarize -> post summarized journals with
drill-back.

- AC requires a TABLE as ingestion source (not a base dataset); one table serves only
  ONE accounting source; Enrichment Steps count CANNOT change after creation;
  inactivating an accounting source is IRREVERSIBLE.
- Cardinal enrichment rule: TRANSACTION COUNT MUST NOT CHANGE through enrichment
  (filters and non-left-outer joins are the classic batch-killers).
- **HARD LIMITS**: no resulting worktags on ANY account posting rule type in AC; once
  Summarization runs there is NO rollback/rerun of the batch (keep detailed accounting
  manual during test); **summarized journals BYPASS budget check** (post even over
  budget); intercompany journal-line companies must share ledger currency; amounts must
  match the currency's decimal precision or journals will not balance.
- Value-mapping ranges evaluate as STRINGS ("5" is outside 1-19, "05" is inside 01-19);
  mapping tables evaluate TOP-DOWN first-match; a definition locks once a table uses it.
- Effective-dated config snapshots: initial effective date must PREDATE all incoming
  transactions (01/01/1900 pattern).

## 2. Technical surface

(from the in-tenant WWS master inventory)

- **Financial Management - 431 operations** (largest service in the tenant). Journals:
  Import Accounting Journal, Submit Accounting Journal, Bulk Import Submit/Cancel
  Accounting Journal, Put Beginning Balance Journal, Put Beginning Balance Translation
  Amounts, Import Accounting Center Detailed Journal, Get Journals, Cancel Accounting
  Journal. FDM setup: Put Account Set, Put Account Posting Rule Set, Put Ledger, Put
  Ledger Year and Ledger Periods, Put Fiscal Year, Put Company Accounting Details, Put
  Journal Source, Put Suspense Account Rule, Put Custom Worktag, Put Intercompany
  Profile, Put Custom Account Posting Rule Type/Dimension (AC), Submit Mass Update
  Ledger Period Status. Planning/stats: Import Budget (4 import modes incl. Replace All
  and zero-amount-deletes; Plan Event BP unless auto-complete), Import Budget Amendment,
  Import Statistic, Put Statistic Definition.
- **Resource Management - 394 operations** (P2P + expenses + assets + projects). Key
  writes: Submit Supplier Invoice, Import Supplier Invoice, Bulk Import Submit Supplier
  Invoice, Submit Supplier Invoice Adjustment/Request, Put OCR Supplier Invoice, Submit
  Purchase Order, Submit Purchase Order Change Order, Submit Requisition, Submit
  Receipt, Submit Return, Submit Supplier, Submit Supplier Contract (+Amendment), Put
  Purchase Item (+Bulk Import), Import Supplier Items, Import Catalog Load, Put Location
  Customer Account Number Detail, Submit Expense Report, Import Credit Card
  Transactions, asset ops (Register/Adjust/Transfer/Dispose Asset).
- **Cash Management - 113 operations**: Import Bank Statement, Import Intraday Bank
  Statement, Import Bank Fee Statement, Import Ad hoc Bank Transaction, Put Bank
  Account, Put Financial Institution, Import Payment Acknowledgement Message.
- **Settlement Services - 48 operations**: Submit Settlement Run, Get Payments, Submit
  Payment Return, Submit Stop Items, Put Bank Routing Rule, Put Payment Type.
- Adjacent (billing side, separate playbook scope): Revenue Management 308 ops.
- Graph/REST: **submitAccountingJournal GraphQL mutation** (journal create without SOAP);
  Prism REST v3 (fileContainers, tables, dataChanges) for AC/Prism loads; supplier
  invoice external sources delivered as Web services, EDI 810, and REST API.
- EIB facts: outbound formats never include native Excel; Integration IDs report lists
  reference IDs for templates; Journal Connector = scheduled SFTP journal-file import
  with worktag mapping. Delivered EDI: 855 (POA), 810 (invoices). Import-vs-Submit house
  rule and the import framework (poll Get_Import_Processes -> harvest
  Get_Import_Process_Messages) per wd-integration-dev eib.md.

## 3. Solution patterns + donors

- **Accounting journal inbound (Studio -> O4I conversion base)**: INT126 Burdening
  Journals Boomerang (prefer _v2) - no Java and a real config surface, the chosen base
  over the fully hardcoded FIN_INT_Import_Journals (zero launch params - the
  anti-example). GL-inbound shape also in IS_INT7003/IS_INT7004 (hospital/physician
  billing GL inbound) and FIN_INT_Gift_Journals.
- **Journal create from Extend**: `createAccountingJournal` catalog app - journal submit
  via the Workday Graph API (submitAccountingJournal mutation) with ZERO orchestrations,
  plus 6 WQL FDM lookups. The lightweight path when a page, not a file, originates the
  journal.
- **Supplier invoice inbound**: local donors `nonpo-supplier-invoice` +
  `supplier-invoice-template` (the 6-subflow O4I template: ValidateFile /
  ConvertCSVtoJSON / ValidateValues / SendSOAPRequest / EventSummary /
  InitializeEventData - the scaffold donor the payroll-input template was built from)
  and the official catalog app `supplierInvoicesInbound` - the WWS import framework
  natively in O4I: Import_Supplier_Invoice submit -> X-Validate dry-run -> poll
  Get_Import_Processes -> harvest Get_Import_Process_Messages -> ImportResults.csv.
  This submit-poll-harvest pattern is THE house shape for any Import_* load.
- **Payroll-results-to-GL outbound**: INT0021 (delivered CLAR corpus; ERP variants
  INT0012/INT0030/INT0050). Note from the 80-project estate audit: no journal/payroll
  OUTBOUND existed locally (only journals-to-Prism) - a true GL export is usually
  NET-NEW O4I work, not a conversion; estimate accordingly.
- **Bank/treasury**: INT553/INT554/INT555 bank REST API outbound family (real-time
  request/response - wd-integration-dev studio.md donor registry); statement INBOUND is
  plain Import Bank Statement / Import Intraday Bank Statement; INT060-style prenote
  and INT003-style settlement-date flows; acks via Import Payment Acknowledgement Message.
- **Accounting Center / Prism**: AC itself is configuration, not custom build - the
  custom surface is the FEED (Prism REST fileContainers -> files -> dataChanges
  choreography, sample-verified) and the dismissal/BP hooks. Donors:
  `prismAndExtendDesignPatterns` (cds_ table reads, single-threaded DCT status lock,
  install.orchestration self-provisioning) and `salesCommission` (DCT execution via the
  typed SendPrismRequest node). Published AC/Prism data reads back into Extend via WQL
  as `cds_<apiName>` with WPA_RowID as the stable id - see wd-extend-dev
  prism-and-reporting.md for the full build workstream and Prism limits.
- **Boomerang** (read Workday -> compare/compute -> write Workday): INT126-style Studio
  donors; O4I equivalent `updateServiceDateBoomerang` (catalog).

## 4. Design gotchas

- Edit Company Accounting Details locks after the first posting; journal sequencing is
  irreversible and must be enabled BEFORE conversion - both are day-one decisions that
  cannot be walked back.
- Put Beginning Balance Journal REPLACES on reload and skips custom validations;
  Import Accounting Journal APPENDS and needs an open-for-activity period - loading the
  same data through the wrong one double-posts or silently overwrites.
- Suspense threshold: a 50 percent threshold on a 5-line journal with 3 bad lines fails
  the LOAD, not just the lines - size thresholds for real file quality.
- Adjust Accounting reclasses worktags on paid transactions but CANNOT change amounts -
  amount fixes are operational-transaction edits, not journal adjustments.
- EIB error signature: "does not meet the restrictions defined for this field
  (Company_Reference)" WITHOUT "ID" in the message = the launching user lacks security
  (e.g. Accountant role not assigned for that company), not a data error.
- One match rule set per company, and no rule set = no matching at all - a new company
  silently pays unmatched invoices until someone notices. Avoid overriding no-receipt /
  quantity match exceptions on inventory replenishment POs (corrupts average cost).
- Requisition sourcing is ranked by attribute importance, not rule order; and
  procurement conditional rules do not stop web services - inbound P2P integrations
  need custom validations for the guardrails users see in the UI.
- Accounting Center: no resulting worktags on posting rules, no rollback after
  summarization, budget check bypassed on summarized journals, transaction count must
  not change through enrichment, string-compare ranges in mapping tables - each of
  these has broken a naive AC design.
- Report Writer reports return ALL book codes unless filtered (standard reports honor
  the Book prompt) - the classic custom-report-vs-Trial-Balance mismatch.
- Custom worktag budget: 15 custom types + 10 custom-org financial worktags per tenant
  is a REAL ceiling - inventory existing usage before a design claims a new worktag.

Cross-refs: payroll.md in this skill (13-step sequence detail, costing allocations),
wd-integration-dev (eib.md, studio.md, document-transformation.md), wd-extend-dev
(prism-and-reporting.md, app-catalog-registry.md, rest-api-catalog.md), wd-deployment
(data conversion + security model).
