# Banking and Settlement: bank accounts, statements, the settlement run, payment formats - solution playbook

The treasury/cash slice of Financials: bank accounts and bank-account setup, bank
statements and reconciliation (auto and manual matching), the SETTLEMENT run that turns
approved payables and payroll results into bank payments, payment types and delivered
payment formats (ISO 20022 / NACHA / positive pay), payment elections, cash management,
and the delivered bank integration surface (payment-file generation, statement/ack
inbound). This playbook is the design bridge for treasury/cash/payments work; it
COMPLEMENTS financials.md (which owns FDM, accounting, and P2P) - it does not restate FDM
content, so cross-link financials.md for anything ledger-side. Payment-file generation is
usually a Studio/DT/EIB integration, so the BUILD overlaps heavily with wd-integration-dev
- this playbook names the surface and points there. Config facts: doc-sourced (Workday
product / course-manual level; NOT re-crawled this pass - confirm in-tenant). Web-service
names + operation counts: from the in-tenant WWS master inventory as already cited in
financials.md and payroll.md (build-verified list). Trust-but-verify the tenant actually
holds treasury data before designing (wd-extend-lifecycle/references/verify-in-tenant.md).

## 1. Configuration spine

### Bank accounts and financial institutions

- Object chain (doc-sourced; confirm task names in-tenant): Financial Institution (the
  bank) -> Bank Account (routing/transit number, account number, currency, account type).
  A Bank Account is owned by a Company; one company can hold many.
- **Settlement Bank Account** marks which account disburses for a given Company + currency
  + payment type, and sets the default disbursement account. Settlement cannot produce a
  payment for a Company/currency/payment-type combination that has no settlement bank
  account (confirm in-tenant).
- Bank Account Signers and bank branch details feed check/wire output. Prenotes (a
  zero-dollar ACH validation of a payee's bank account before the first live payment) gate
  when an account becomes payable.

### Payment types and payment formats

- **Payment Type** = the method: Check, EFT/ACH (Direct Deposit), Wire, Manual, and
  similar. Payment types are configured and mapped to bank accounts + formats (Put Payment
  Type / Put Bank Routing Rule on the technical surface below).
- **Payment Format** = the file layout the bank consumes. Delivered families (doc-sourced;
  confirm the exact delivered format list + version in-tenant): **ISO 20022** (pain.001
  credit-transfer initiation outbound; pain.002 status inbound; CAMT.05x statements),
  **NACHA** (US ACH), **positive pay** (outbound check-issue file for bank-side fraud
  matching), plus country-/bank-specific delivered formats.
- Settlement Bank Account + Payment Type + Payment Format together determine which file is
  generated and where it goes. Treat "the tenant supports ISO 20022 / NACHA" as the
  STARTING point - each bank tweaks fields/headers, so confirm the bank's exact spec.

### Payment elections

- **Payment Election** = how a PAYEE chooses to be paid: which payment type, which bank
  account, and any split/allocation across accounts. Workers set elections via
  self-service; integrations rarely write them directly.
- **Payment Election Rules** gate which payment types/accounts are allowed per country and
  per run category / pay component. This is a REQUIRED payroll gate (one per run category;
  a missing rule = payroll cannot complete) - that slice is owned by payroll.md; cross-link
  it rather than restating.

### The settlement run

- **Settlement** is how Workday turns approved payables (supplier invoices, expense
  reports, payroll results, ad hoc payments) into actual bank payments. It is a SHARED
  engine across AP, Expenses, and Payroll - a design touching payments must know which
  source populated the run.
- Create Settlement Run / Scheduled Settlement Run selects payment-eligible transactions by
  Company, bank account, payment type, and payment date; produces Payment records; and
  generates payment files via the delivered bank integration. Manual vs scheduled both
  exist (Submit Settlement Run / Put Scheduled Settlement Run - technical surface below).
- Downstream statuses update inbound via Payment Acknowledgement Message (bank/ISO
  pain.002 ack). Payment Return, Stop Items, and Escheatment Items handle the exception
  lifecycle.

### Bank statements and reconciliation

- Statement inbound (doc-sourced; confirm exact delivered format codes in-tenant): Import
  Bank Statement (end-of-day, e.g. BAI2 / ISO CAMT.053), Import Intraday Bank Statement
  (e.g. CAMT.052), Import Bank Fee Statement (e.g. CAMT.086). These are DELIVERED
  file-based loads, not custom builds.
- **Auto-reconciliation** matches statement lines to Workday payments/deposits/ad hoc bank
  transactions by reconciliation rules (amount, date window, reference/check number);
  unmatched lines route to **manual reconciliation**. An **Ad Hoc Bank Transaction** books
  a bank movement with no originating Workday transaction (fees, interest) so it can
  reconcile. Reconciliation-rule config is not build-verified in the suite - confirm
  in-tenant.

### Cash management

- Cash Management ties bank accounts, statements, settlement, and ad hoc transactions
  together and feeds cash position / forecasting. The custom surface here is almost always
  the FEED (statement inbound, payment-file outbound, ack inbound), not the config.

## 2. Technical surface

(Web-service ops below are cited from the in-tenant WWS master inventory as recorded in
financials.md and payroll.md - cite, do not re-document; open those files for the full
operation lists.)

- **Settlement Services - 48 operations** (per financials.md / payroll.md): Submit
  Settlement Run, Put Scheduled Settlement Run, Get Payments, Submit Payment Return, Submit
  Stop Items, Submit Escheatment Items, Put Bank Routing Rule, Put Payment Type,
  Import/Put Payment Acknowledgement Message. This service is SHARED with payroll
  settlement (payroll.md).
- **Cash Management - 113 operations** (per financials.md): Put Bank Account, Put Financial
  Institution, Import Bank Statement, Import Intraday Bank Statement, Import Bank Fee
  Statement, Import Ad hoc Bank Transaction, Import Payment Acknowledgement Message.
- **REST / WQL / RaaS.** Per the REST snapshot (wd-extend-dev rest-api-catalog.md, snapshot
  2026-07-27) there is NO delivered bank-account or settlement-run REST service - the
  receivables-side customerAccounts v1 (customers, invoices, payments) and accountsPayable
  v1 (supplierInvoiceRequests) exist, but treasury WRITES are SOAP (Settlement Services /
  Cash Management) or file-based. Re-check at each release refresh (rest-api-catalog.md
  release routine). RaaS/WQL are the read path for payment/bank data, but the suite has NO
  build-verified WQL data source for banking objects - do not guess source or field names;
  confirm in-tenant (wd-extend-dev wql.md discipline).
- **Delivered payment-file generation.** Workday emits payment files from the settlement
  run using the delivered payment formats above. When a bank needs a layout the delivered
  format cannot emit, chain a **Connector with Document Transformation** to reshape the
  settlement output (wd-integration-dev document-transformation.md; XTT/ETV for
  fixed-width/delimited layouts in xslt3.md), or a Studio/O4I outbound for anything needing
  orchestration. Naming (INT IDs, ISU/ISSG) per wd-integration-dev integration-naming.md;
  connector mechanics per core-connector.md. The BUILD is owned by wd-integration-dev.
- **Event/BP hooks.** Post-settlement integrations (ACH/positive-pay/check-print/hosted tax
  filing) fire off settlement/payment events - see payroll.md's post-settlement integration
  list for the payroll side.

## 3. Solution patterns + donors

Donor-citation bar (SKILL.md): the bank donors below are **inventory-cited** Studio
projects named in the illustrative library table in wd-integration-dev studio.md - NOT
build-verified. Always caveat and open the raw Studio export before quoting one. The suite
has NO build-verified O4I/Extend donor for a banking payment-file or bank-API flow - SAY SO
in an estimate; invent none.

- **Real-time bank REST API outbound** (request/response to a bank API - account update,
  card limits/application): inventory-cited Studio family INT553/INT554/INT555 (studio.md
  donor table; inventory-cited, not build-verified - open the project before quoting it).
  Shape = cc:workday-out-rest / http-out to a bank endpoint with request/response handling.
  An O4I equivalent would use SendHttpRequest egress (wd-extend-dev orchestration egress
  constraints), but there is NO build-verified banking O4I donor on disk - treat as
  net-new.
- **Prenote / settlement-date flows**: inventory-cited INT060-style prenote status update
  and INT003-style settlement-date update (studio.md donor table; inventory-cited, not
  build-verified).
- **Remittance advice outbound** (email + generated XML for ACH/wires): inventory-cited
  INT540-style remittance emails (studio.md; inventory-cited, not build-verified).
- **Payment-file generation** (NACHA / ISO 20022 pain.001 / positive pay to the bank): no
  build-verified firm donor is on disk in the suite. This is usually a Connector with
  Document Transformation over the settlement output, or a Studio/O4I outbound - treat as
  NET-NEW work and estimate accordingly (parallel to financials.md's note that GL OUTBOUND
  is usually net-new). Mechanics: document-transformation.md + xslt3.md (fixed-width/
  delimited output).
- **Statement + acknowledgement inbound**: delivered Import Bank Statement / Import
  Intraday Bank Statement and Import Payment Acknowledgement Message (file-based, not custom
  logic). If a bank sends a non-delivered statement layout, pre-format with DT first
  (document-transformation.md O4I pre-formatter pattern) before the delivered import.
- **Reusable house shapes** (not banking-specific): the submit -> poll -> harvest import
  framework (donor supplierInvoicesInbound) and the boomerang read/compare/write shape are
  cited in financials.md and hcm-core.md - reuse those for any Import_* load or compare
  sweep rather than a banking-specific donor.

## 4. Design gotchas

- **Settlement is a SHARED engine** across AP, Expenses, and Payroll - do not design a
  standalone "payments app" per source. Know which source populated the run; financials.md
  owns AP settlement config, payroll.md owns payroll settlement.
- **No delivered REST for bank accounts / settlement runs** in the current snapshot -
  treasury automation is SOAP (Settlement Services / Cash Management) or file-based. A
  design that assumes a REST bank/settlement service will stall; confirm at each release
  refresh (rest-api-catalog.md).
- **Payment file layouts are bank-specific even from a delivered format.** ISO 20022 /
  NACHA / positive pay is the starting point, not done - each bank tweaks fields, headers,
  delimiters, and control totals. Confirm the bank's exact spec and budget a DT/Studio
  reshape (document-transformation.md).
- **Positive pay can be BOTH directions** - outbound check-issue AND an inbound
  exception/decision file. Clarify direction(s) with the bank; a one-way design misses the
  exception handling.
- **Prenotes gate live ACH.** A worker/supplier bank account may be in a prenote waiting
  period and not yet payable - reconciliation and payment timing must account for prenote
  status (the INT060-style flow).
- **Config gates that silently block payment**: Payment Election Rules are REQUIRED per
  payroll run category (missing = payroll cannot complete - payroll.md); on the AP/supplier
  side, a missing settlement bank account for a Company + currency + payment type blocks
  settlement. Both are pre-go-live config gates - surface them in scoping.
- **Auto-reconciliation depends on reference alignment.** The check/reference number
  Workday emits on the payment file must match what the bank returns on the statement - if
  the outbound integration rewrites the reference, the auto-recon match rate drops. Design
  the outbound payment file and the reconciliation rules together.
- **Real bank details are sensitive** (routing/account numbers, signers) - never load into
  shared dev tenants (no-customer-data-in-dev-tenants house rule); genericize any donor
  before reuse.
- **Format/reconciliation facts here are not build-verified.** Confirm every format code
  (BAI2 vs CAMT.053, pain.001 vs pain.002, the delivered NACHA/positive-pay variants) and
  the reconciliation-rule config against the tenant and the bank before committing a design.

Functional literacy (what a settlement run, payment election, bank account, or bank
statement IS, and the AP and payroll payment cycles) lives in wd-discovery
functional-financials.md (Financial Management banking + Procure to Pay + the Customer
Accounts settlement engine) and functional-payroll.md (the pay-settlement slice) - this
playbook assumes it.

Cross-refs: financials.md (FDM, accounting, P2P, AP settlement config, the bank/treasury
donor list), payroll.md (payroll settlement run, payment election rules, post-settlement
tax/ACH integrations) in this skill; wd-integration-dev (integration-naming.md,
core-connector.md, document-transformation.md, xslt3.md, studio.md donor registry) for the
BUILD; wd-extend-dev (rest-api-catalog.md, orchestration.md for O4I egress, wql.md);
wd-deployment (security model for bank/payment data). Verify in-tenant:
wd-extend-lifecycle/references/verify-in-tenant.md.
