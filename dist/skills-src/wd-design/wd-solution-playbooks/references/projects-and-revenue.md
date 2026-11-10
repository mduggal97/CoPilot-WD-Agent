# Projects/PSA + Revenue Management: project-to-bill, contracts, revenue - solution playbook

Workday Projects (the PSA/project-management surface) plus the billing side financials.md
deliberately PUNTS: Customer Contracts, Project Billing, and Revenue Management / revenue
recognition - the whole opportunity-to-cash (project-to-bill) chain. Projects also lives
inside the Resource Management 394-op service alongside P2P in financials.md; this playbook
picks up projects AND the "Revenue Management 308 ops (separate playbook scope)" line
financials.md defers (~line 132). Config facts below are doc-sourced (Workday Education
manuals, 2026-08-25); verify in-tenant. Web-service names/counts are from the in-tenant WWS
master inventory (financials.md); the REST surface is build-verified from the suite's
rest-api-catalog.

## 1. Configuration spine

### Setup order

1. FDM + accounting FIRST - companies, ledgers, worktags, posting rules must exist
   (financials.md). Revenue and project accounting both post through the same posting-rule
   engine.
2. Project foundation - Project Hierarchies, then Projects (each carrying a Project worktag,
   ref-id format `PJ1nnnnn` auto-sequence per integration-naming.md), project templates,
   phases/tasks catalog. A project can be billable, capital, or internal - that flag drives
   which downstream config applies.
3. Project plan - plan phases -> plan tasks -> task dependencies; the plan is the work
   breakdown that time and expense post against.
4. Resource plan - assign workers/roles to the project (resource plan lines, forecast
   lines). Resources are HCM workers, so the staffing foundation gates who can be planned
   (hcm-core.md).
5. Project assets (capital projects only) - project cost accumulates, then converts to a
   business asset via the asset framework (asset ops live in Resource Management -
   financials.md).
6. Customer + contract side (billable projects) - Customer Category (drives receivables
   ledger account), Revenue Categories (hierarchical, worktag-capable, a posting-rule
   condition), Sales Items (exactly one revenue category each), then the Customer Contract
   with its Contract Line Types.
7. Billing + revenue config - Billing Schedules / Methods / Milestones and Revenue
   Recognition Methods, wired per contract line. Billing and revenue are configured
   SEPARATELY but must reconcile at contract level.
8. Settlement - Customer Invoice -> revenue recognition -> cash application / collections.

### Key BPs

Create Project, Create/Edit Project Plan, Assign Project Resources (resource plan),
Customer Contract Event (create/amend), Customer Invoice Event, Revenue Recognition, Cancel
Customer Invoice, Project Asset conversion events, Register/Adjust/Transfer/Dispose Asset
(shared with financials.md). The project-to-bill chain: Customer -> Customer Contract ->
Billing Schedule -> Customer Invoice -> Revenue Recognition -> Cash Application (flow per
wd-discovery functional-financials.md).

### Hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

- **Contract Line Type is destiny**: one of 11 Workday Contract Line Types is chosen per
  line and CANNOT change after the contract is approved - it fixes whether the line bills,
  recognizes revenue, or both. A design that "flips a line to billable later" is a new
  line, not an edit.
- **Billing and revenue are decoupled but must reconcile**: separate schedules, methods,
  and installments, yet an "Out of Balance" condition (lines != installment amounts) BLOCKS
  processing at the contract level. An integration writing one side must keep the other in
  balance.
- **Milestones are hard gates**: a pending milestone stops both billing and revenue on its
  lines until released - automation keyed on "invoice the contract" silently produces
  nothing while a milestone is open.
- ASC 606 / IFRS 15 multiple-element allocation runs off fair-value price lists; Alternate
  Contracts are draft replicas for what-if modeling - do not integrate against an Alternate
  as if it were live.
- Project worktag behaves like any financial worktag: subject to the tenant worktag ceiling
  (15 custom worktag types + 10 custom-org financial worktags per tenant - financials.md),
  and required-worktag usage is TENANT-WIDE per transaction type.
- Resource plan lines reference HCM workers - a planned resource who is not an active worker
  (or is future-dated/terminated) breaks the plan; the staffing model landmines in
  hcm-core.md apply to the resource side unchanged.
- "Enforce Required in Web Services" (tenant validation setting) governs whether
  red-asterisk required fields apply to web-service submissions - a contract/invoice load
  that works in one tenant can reject in another on this checkbox alone (same trap as
  financials.md / hcm-core.md).

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory - financials.md):

- **Resource Management - 394 operations** - the P2P + expenses + assets + PROJECTS service.
  Projects, project plans, resource plans, and business-asset (fixed-asset) ops are served
  here (asset ops are SOAP-only - rest-api-catalog.md). Confirm the exact project/resource-
  plan operation names in-tenant (doc-sourced; not build-verified in the suite).
- **Revenue Management - 308 operations** - the billing/customer-contract/revenue service
  financials.md defers to this playbook. Expected surface: customer-contract create/amend,
  customer-invoice submit/import/adjust, billing-schedule, and revenue-recognition ops, plus
  reads for contracts/invoices/schedules. The 308 count is from the WWS inventory; confirm
  exact operation names and count in-tenant (doc-sourced; not build-verified in the suite).
- **Financial Management - 431 operations** carries the downstream accounting - revenue
  recognition and billing post journals through the same engine financials.md documents
  (Import/Submit Accounting Journal, posting rules).

REST / WQL / RaaS (build-verified from the suite's rest-api-catalog - wd-extend-dev
rest-api-catalog.md):

- **projects v3 (64 ops)** - adHocProjectTimeTransactions, planPhases, planTasks, projects,
  resourceForecastLines, resourcePlanLines, taskResources. The build-verified read/write
  surface for project plans and resource plans without dropping to SOAP.
- **revenue v1 (5 ops)** - billableTransactions: the billable-transaction surface feeding
  project billing.
- **customerAccounts v1 (11 ops)** - customers, invoicePDFs, invoices, payments: customer
  invoice reads/writes, invoice PDFs, and cash-application/payment data.
- **common v1 (40 ops)** exposes `customers` for customer master reads; **coreAccounting v1**
  resolves posting rules (`/evaluateAccountPostingRules`) for revenue/billing lines; the
  **worktag v1 `/validateWorktags`** pre-check applies to project-tagged transactions.
- WQL / RaaS: project, project-plan, resource-plan, customer-contract, billing, and
  revenue-recognition data sources back reporting and outbound extracts; RaaS custom reports
  remain the outbound workhorse (~2083-char URL guard - wd-extend-dev orchestration.md).
  Confirm exact data-source names in-tenant.

Delivered connectors and hooks:

- **No project- or billing-specific delivered Core Connector is named in the suite's
  integration-naming.md** (its CC list is CCB/CCW/CCP/CCJP/CCJPJF/CCJR/CCL/CCO/PICOF/PECI/
  WECI - none for projects, contracts, or revenue). Do NOT assume a delivered CC exists here;
  confirm the delivered-integration catalog in-tenant before scoping a custom feed. Naming
  formats that DO exist: Project worktag `PJ1nnnnn` (auto sequence), Revenue Category
  `RC1nnnn`, and the Customer sequence generator `CST-` (integration-naming.md).
- BP hooks: Customer Contract, Customer Invoice, Revenue Recognition, and Project events can
  carry integration/service steps and Extend BP-triggered orchestrations (useForOrchestrate -
  wd-extend-dev orchestration.md); Model BPs give custom project/contract companion objects
  their own routable events (wd-extend-dev model-bp.md).

## 3. Solution patterns + donors

- **Project / resource-plan companion Extend app** - an Extend BO intake (project-request or
  resource-request form with its own BP) that then creates the Project / resource plan via
  projects v3 REST or SOAP. No project-specific build-verified donor is on disk; reuse the
  hcm-core.md "custom work-event app with its own BP" shape - build-verified donor
  `createAWorkEvent` (custom .businessprocess + wizard + hub), production-shaped sibling
  `workFromAlmostAnywhere`. The pattern transfers directly; the write target differs.
- **Billable-transaction / time-and-expense feed into billing** - push billable lines via
  **revenue v1 billableTransactions** or **projects v3 adHocProjectTimeTransactions** (REST,
  build-verified shape from the snapshot). No billing-specific build-verified donor exists in
  the suite - say so in an estimate rather than implying a liftable converter.
- **Customer-invoice inbound / outbound** - for an inbound customer-invoice or contract load,
  reuse the generic O4I import-framework shape (submit -> poll Get_Import_Processes -> harvest
  Get_Import_Process_Messages) whose build-verified donor is `supplierInvoicesInbound` (same
  framework, DIFFERENT payload - financials.md); there is no customer-side build-verified
  donor on disk. For outbound extracts mirror the hcm-core.md O4I donor
  `employeeDemographicOutbound` (RaaS -> CsvFormat, sequenced filename).
- **Revenue / billing journal from Extend** - revenue recognition posts delivered journals;
  where a page or flow must originate a related journal, the build-verified donor is
  `createAccountingJournal` (submitAccountingJournal Graph mutation, zero orchestrations -
  financials.md). Do not hand-post revenue journals the delivered recognition already writes.
- **Boomerang project-data sweep** (read Workday -> compute -> write back) - build-verified
  O4I donor `updateServiceDateBoomerang` shape (RaaS/WQL read -> loop -> SOAP/REST update);
  INT126-style Studio donors on the financials.md registry.
- Grant-funded projects overlap Grants Management - if the project is sponsored, read
  [grants.md](grants.md) for the award/F&A layer rather than duplicating it here.

## 4. Design gotchas

- Contract Line Type is chosen once and frozen at approval - design the contract structure
  (which lines bill vs recognize) UP FRONT; you cannot re-type a line later, only add a new one.
- Billing and revenue are two decoupled schedules that must reconcile - an integration that
  writes billing without matching revenue (or vice versa) trips "Out of Balance" and blocks
  the whole contract, not just the offending line.
- Milestones are hard gates - a flow that "invoices the contract" produces nothing while a
  milestone is pending; check milestone status before assuming an empty result is a bug.
- Project worktag is a financial worktag under the tenant ceiling - inventory existing custom
  worktag usage (financials.md) before a design claims Project as a new required tag.
- Resource plans ride HCM workers - the staffing foundation governs who can be a resource;
  ask the staffing model FIRST (hcm-core.md) when the app plans people onto projects.
- Verify the tenant actually HOLDS project/contract/revenue data before designing on it (a
  bare dev tenant will not) - trust-but-verify
  (wd-extend-lifecycle/references/verify-in-tenant.md).
- Functional literacy (what a project / customer contract / revenue category / contract line
  type IS, the opportunity-to-cash vocabulary) lives in wd-discovery functional-financials.md
  (Customer Accounts and Contracts / Revenue Management section) - this playbook assumes it.
