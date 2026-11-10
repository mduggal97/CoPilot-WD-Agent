# Expenses & Procurement (Spend Management): expense, P2P, suppliers - solution playbook

The SPEND slice of Workday Financials: employee expense (expense reports, expense
items, spend authorizations, corporate-card transactions) and procure-to-pay
(requisitions, purchase orders, receipts, supplier invoices) plus the supplier
accounts / supplier contracts and procurement config those ride on. This is the design
bridge for spend / P2P work.

**Boundary.** `financials.md` owns general financials + accounting and the whole FDM /
worktag layer (companies, ledgers, spend-driven posting rules, journal sequencing,
Accounting Center). It also already carries the P2P MATCHING and SOURCING config detail.
THIS playbook owns the SPEND / P2P transactional slice and the expense side `financials.md`
only touches. Where the two meet (matching, sourcing, spend-category accounting), cross-link
`financials.md` - do NOT restate FDM / worktag / posting-rule content it owns.

Config facts below are doc-sourced ([DS] - Workday Education manuals + Procure-to-Pay
product knowledge, 2026-08-25); confirm load-bearing numbers in-tenant. Web-service names
are from the in-tenant WWS master inventory. REST surfaces tagged [BV] are build-verified
from the suite's rest-api-catalog.

## 1. Configuration spine

### Expense management (expense reports, items, spend authorizations, corporate card) [DS]

- **Object chain**: Spend Authorization (optional pre-approval / commitment) -> Expense
  Report -> Expense Report Lines, each line an **Expense Item** (the config object;
  Expense Item Groups classify them and drive accounting via posting rules -> see
  `financials.md`, do not restate). Corporate-card charges arrive as **Credit Card
  Transactions** that a worker (or auto-match) pulls ONTO expense-report lines.
- **Spend authorization is a commitment, not a payment**: it can be required by expense
  item, and reconciles against the later expense report; automation that treats it as the
  spend event double-counts. Cash advances tie to spend authorizations.
- Expense config spine: Expense Item + Item Groups -> Expense Policies (per-diems, limits,
  itemization, receipt-required thresholds) -> Worktag defaulting -> Expense Report and
  Spend Authorization BPs. Ship-to / expense-location and currency drive per-diem and rate
  lookup.
- **Corporate-card load is a two-step**: transactions import first (Import Credit Card
  Transactions), THEN reconcile to expense lines. A card feed that only imports leaves
  charges unreconciled; the design owns the match-and-attach step, not just the load.

### Procurement / P2P chain [DS]

Full spine (Supplier Contract -> Requisition -> Source/Create PO -> Issue -> Receive ->
Supplier Invoice -> Match -> Settle) and the MATCHING + SOURCING config (match rule sets,
match condition/exception rules, ranked requisition sourcing) are documented in
`financials.md` P2P spine - cross-link, do not restate. What this playbook adds on the
procurement-config side:

- **Sequence IDs REQUIRED before transacting** (Edit Tenant Setup - Financials; company
  generators take precedence): requisitions, POs, receipts, supplier contracts, supplier
  invoices. Naming prefixes are delivered patterns, not free text - see
  `wd-integration-dev/references/integration-naming.md` (`SUP-` supplier, `PO-`, `INV-`
  supplier invoice, `EXP-` expense; master data = 3-char prefix + digits).
- **Spend Categories** (hierarchical commodity classification) are required on
  reqs/POs/contracts/invoices and drive accounting; one category cannot do BOTH
  business-asset and inventory tracking and cannot flip inventory -> procurement usage
  (the accounting side is `financials.md`).
- **Requisition / PO types carry accounting specials**: **Bill Only** = no accounting,
  **Consignment** = at no cost. Misclassifying a type breaks journals - it is a config
  decision, not a data attribute.
- **Item machinery**: Purchase Items, Supplier Items, Catalog Items (a catalog item can
  auto-route a PO, BYPASSING the requisition), Web items / punchout. Item mass-maintain
  via worksheet is capped (confirm the row ceiling in-tenant; product docs cite a low-
  thousands limit).
- **Procurement Conditional Rules** (Prevent Cancel / Close / Receipts ...) hide UI actions
  but do NOT stop web services (except Prevent ASN) - guard inbound P2P integrations with
  custom validations instead (same trap called out in `financials.md`).

### Supplier accounts + supplier contracts [DS]

- **Supplier** is a distinct account object with its own onboarding BP: Supplier Category
  (exactly ONE required), tax/1099 status, remit-to and payment settings, and
  duplicate-detection + sanction / denied-party screening at create. A supplier is NOT a
  worker and NOT a customer - do not model it as either.
- **Supplier Contract** governs pricing and terms (many delivered types incl. leases);
  pricing hierarchy is Supplier Contract line > Advance Pricing > Supplier Info > Purchase
  Item default. Contract amendments re-fire matching (`financials.md`).
- Ship-To locations + Location Customer Account Number detail (Put Location Customer Account
  Number Detail) tie a supplier's account number to a ship-to for ordering.

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory):

- **Resource Management - 394 operations** is THE spend surface (P2P + expenses + assets +
  projects share it). The full write list lives in `financials.md` Technical surface -
  cross-link rather than re-inventory. Spend-relevant ops: Submit / Import / Bulk Import
  Submit Supplier Invoice, Submit Supplier Invoice Adjustment/Request, Put OCR Supplier
  Invoice, Submit Purchase Order (+ Change Order), Submit Requisition, Submit Receipt,
  Submit Return, Submit Supplier, Submit Supplier Contract (+ Amendment), Put Purchase Item
  (+ Bulk Import), Import Supplier Items, Import Catalog Load, Put Location Customer Account
  Number Detail, **Submit Expense Report**, **Import Credit Card Transactions**. External
  Warehouse POs can ONLY be created by Submit Purchase Order (stock-item lines, no price
  variance) - `financials.md`.
- **Financial Management - 431 operations** owns the ACCOUNTING that spend posts to
  (posting rules, journals, worktags) - do not reach into it for spend transactions; it is
  `financials.md`'s surface.
- **Integrations - 37 operations** (meta): Launch Integration / Launch EIB, Approve /
  Cancel / Rescind Business Process, Get Import Processes, Get Import Process Messages - the
  import-framework poll/harvest ops every high-volume spend load leans on.

REST / WQL / RaaS (REST rows [BV] from `wd-extend-dev/references/rest-api-catalog.md`):

- **expense v1 [BV]** (`/expense/v1`, 17 ops - `entries`, `expenseItems`, `reports`): the
  no-SOAP path to build an expense report from a page - create entries, roll into a report,
  add lines. This is the surface `mileageExpense` uses.
- **procurement v5 [BV]** (`/procurement/v5`, 44 ops - `purchaseOrders`,
  `requisitions`, `requisitionTemplates`): read-heavy P2P + requisition micro-writes
  without SOAP.
- **accountsPayable v1 [BV]** (`/accountsPayable/v1`, 12 ops - `supplierInvoiceRequests`,
  `sendSupplierInvoiceAttachmentsForScanning`): the supplier-invoice-REQUEST and
  scan-attach lane.
- **contractCompliance v1 [BV]** (`/contractCompliance/v1`, 4 ops - `supplierContracts`):
  read supplier-contract data.
- **worktag v1 [BV]** `POST /validateWorktags` - read-only pre-validation of a worktag combo
  (e.g. `Taggable_Type_ID=EXPENSE_REPORT`) BEFORE submitting; and **budgets v1 [BV]**
  `POST /runBudgetCheck` - pre-flight a multi-line spend transaction against budget plans.
  Both let a spend app fail fast instead of on submit. Full map in
  `wd-extend-dev/references/rest-api-catalog.md`.
- WQL / RaaS: supplier, supplier-invoice, purchase-order, requisition, receipt, expense-
  report, and credit-card-transaction data sources back reporting and outbound extracts;
  RaaS custom reports remain the outbound workhorse (~2083-char URL guard -
  `wd-extend-dev/references/orchestration.md`). Confirm exact data-source names in-tenant -
  spend source names are NOT build-verified in the suite (source-name mismatch is a real
  runtime failure mode; verify before quoting).

Delivered connectors and hooks:

- Delivered EDI: **855** (PO acknowledgement) and **810** (supplier invoice) - `financials.md`.
  Supplier inbound also via Supplier Collaboration hosted sites / portals; item feeds via
  punchout / UNSPSC. **Check these BEFORE hand-building a supplier or invoice integration.**
- The suite's `integration-naming.md` lists delivered Core Connectors for Worker / Location /
  Organization / recruiting objects but does NOT name a build-verified procurement or
  supplier Core Connector abbreviation - do not invent a "CCPO"/"CCSA"; confirm the
  delivered connector name in-tenant before citing one.
- BP hooks: Expense Report, Spend Authorization, Supplier, Supplier Invoice, Requisition,
  and PO BPs all accept Extend BP-triggered orchestrations (`useForOrchestrate` -
  `wd-extend-dev/references/orchestration.md`); Model BPs give custom spend objects their own
  routable events (`wd-extend-dev/references/model-bp.md`).

## 3. Solution patterns + donors

Donor tiers per the SKILL.md donor-citation bar. Build-verified (`[BV]`) donors are on disk;
where none exists, this section SAYS SO rather than inventing one.

- **Expense report from an Extend page** [BV]: `mileageExpense` (catalog) - chains the
  Workday Expense REST surface `/expense/v1` (entries -> reports -> lines) after an external
  Google Maps call, key held in `appProperties`. THE donor for a page that originates an
  expense report; the external-API leg shows the egress + credential pattern
  (`wd-extend-dev/references/orchestration.md`).
- **Corporate-card / spend request companion app** [BV]: `requestCreditCard` - the canonical
  `useForOrchestrate` write-on-approval loop with an external REST call and PATCH-back plus a
  `.report` model file. The shape for a card-request or spend-request intake app whose own BP
  approves before it writes.
- **Purchase-item order form** [BV]: `businessCards` - a tiny 2-page order form against
  `purchaseItem` via the attribute store. The minimal reuse pattern for a catalog-style
  self-service buy.
- **Supplier-invoice inbound** [BV]: `supplierInvoicesInbound` (catalog) - the WWS Import
  framework natively in O4I: `Import_Supplier_Invoice` POST `/soap/.../Resource_Management`
  -> `X-Validate` dry-run -> poll `Get_Import_Processes` -> harvest
  `Get_Import_Process_Messages` -> `ImportResults.csv`. Plus the local template donors
  `supplier-invoice-template` / `nonpo-supplier-invoice` (the 6-subflow O4I scaffold -
  `financials.md`). **This submit -> X-Validate -> poll -> harvest shape is THE house pattern
  for ANY `Import_*` spend load** (credit-card transactions, catalog, supplier items).
- **Requisition / PO / receipt from O4I or a page**: SOAP `Submit_Requisition` /
  `Submit_Purchase_Order` / `Submit_Receipt` on Resource Management, or `procurement v5`
  REST for lighter writes. **No build-verified requisition/PO/receipt-specific donor is on
  disk** - reuse the `supplierInvoicesInbound` import-framework shape for high-volume loads,
  or the generic staffing-style SOAP-chain sequencing from `hcm-core.md` (donor
  `addAdditionalJob`); do not present a P2P-transaction donor that is not on the machine.
- **Supplier onboarding companion app**: an Extend BO intake (supplier request / vendor
  onboarding form) with its own BP that then initiates `Submit_Supplier` (+ contract). **No
  supplier-specific build-verified donor exists** - reuse the `hcm-core.md` "custom
  work-event app with its own BP" shape (`createAWorkEvent` [BV]; production-shaped sibling
  `workFromAlmostAnywhere`). The pattern transfers directly.
- **Outbound spend extract** (supplier / invoice / PO / expense out): RaaS custom report ->
  format is the workhorse; custom O4I shape mirrors `employeeDemographicOutbound` [BV]
  (RaaS -> `CsvFormat`/`FormattedCsvFoldValue`, sequenced filename) - `hcm-core.md`,
  `wd-extend-dev/references/app-catalog-registry.md`.

## 4. Design gotchas

- Stay on the boundary: matching (one match rule set per company; no rule set = invoices
  skip matching), requisition sourcing (ranked by attribute importance, not rule order), and
  all FDM / worktag / posting-rule accounting are `financials.md` - cross-link, don't rebuild
  them here.
- **Expense report != supplier invoice**: different objects, different BPs, but the SAME
  Resource Management service. An app that "captures spend" must pick the right lane -
  employee-reimbursable spend is Expense Report; third-party payable spend is Supplier
  Invoice.
- Spend authorization is pre-approval / commitment, not the spend event - reconcile against
  the later expense report; treating it as the payment double-counts commitment.
- Corporate-card design is import-THEN-reconcile: Import Credit Card Transactions loads
  charges, but they sit unattached until matched onto expense lines. Own the reconcile step.
- Procurement conditional rules hide UI actions but do NOT stop web services (except Prevent
  ASN) - inbound P2P integrations need custom validations for the guardrails users see.
- Requisition/PO type is an accounting decision: Bill Only = no accounting, Consignment = no
  cost. A wrong type does not error - it silently mis-posts (or does not post).
- Supplier Category is exactly one, required, and duplicate + sanction screening fires at
  create - a supplier-load integration that skips category or bypasses screening fails
  submit or creates a compliance gap.
- Pre-flight before submit: `POST /validateWorktags` (worktag combos, e.g. EXPENSE_REPORT)
  and `POST /runBudgetCheck` (budget plans) let a spend app catch errors client-side instead
  of on a failed submit - use them in intake apps.
- Verify the tenant actually HOLDS supplier / procurement / expense data before designing on
  it (a bare dev tenant will not), and verify spend data-source / worktag-usage names
  in-tenant before quoting - trust-but-verify
  (`wd-extend-lifecycle/references/verify-in-tenant.md`).
- Functional literacy (what a requisition / PO / receipt / supplier invoice / spend category
  IS, the P2P funnel and expense vocabulary) lives in `wd-discovery` functional-financials.md
  ("Procure to Pay (Procurement + Supplier Accounts) - spend management" section) - this
  playbook assumes it.

Cross-refs: `financials.md` in this skill (FDM, accounting, P2P matching/sourcing, Resource
Management full op list, Accounting Center), `wd-integration-dev` (eib.md, studio.md,
integration-naming.md), `wd-extend-dev` (rest-api-catalog.md, app-catalog-registry.md,
orchestration.md, model-bp.md), `wd-deployment` (data conversion + security model).
