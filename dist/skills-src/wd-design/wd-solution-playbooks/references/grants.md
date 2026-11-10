# Grants Management: sponsored programs, awards, F&A, award billing - solution playbook

Workday Grants Management is the sponsored-research layer for higher-ed and nonprofit - a
NAMED target vertical: sponsored programs, award/grant worktags, award setup and budgets,
the Facilities & Administration (F&A / indirect-cost) engine, award billing / letter of
credit, and effort. It sits on the FDM (financials.md) and, when awards fund projects,
overlaps [projects-and-revenue.md](projects-and-revenue.md) - cross-linked, not duplicated.
Config facts below are doc-sourced (Workday Education manuals, 2026-08-25); the F&A /
indirect-cost parameters are from the suite's discovery cues (wd-discovery
integration-discovery.md ~line 71); verify all in-tenant. Web-service names/counts are from
the in-tenant WWS master inventory (financials.md); the REST surface is build-verified from
the suite's rest-api-catalog.

## 1. Configuration spine

### Setup order

1. FDM + accounting FIRST - companies, ledgers, worktags, posting rules (financials.md).
   Grant accounting posts through the same posting-rule engine; Fund/Grant/Program are the
   standard higher-ed fund-accounting sector org types (functional-financials.md).
2. Sponsor setup - Sponsors (the awarding agency; ref-id via the `SPN` sequence generator -
   integration-naming.md), sponsor types (federal / state / foundation / industry), and the
   letter-of-credit sponsors that draw federally.
3. Grant / award worktags - the **Grant worktag** (ref-id format `GR-yyyy-nnnn`
   auto-sequence per integration-naming.md), plus supporting **Program** (`PG1nnnn`) and
   **Fund** (`FD1nn`) worktags. These are financial worktags under the tenant worktag ceiling
   (financials.md).
4. Award setup - the Award (the funded agreement) and its Award Lines / sponsored program
   structure; award effective dates, periods of performance, and the sponsor's terms.
5. Award budget - grant budgets loaded/maintained via the budget framework (Import Budget -
   financials.md); budget check enforces against award budget lines.
6. F&A / indirect-cost engine - F&A (indirect) rate agreements with their rate TIERS,
   the MTDC (Modified Total Direct Cost) base and its exclusions, fringe rates, subaward
   caps, cost-share rules, and tuition-remission handling (parameters from
   integration-discovery.md; confirm exact values against the client's negotiated rate
   agreement in-tenant).
7. Award billing - billing schedules/methods for the award and the letter-of-credit draw
   mechanism (billing side; shares the Revenue Management surface - see projects-and-revenue.md).
8. Effort - effort certification config (payroll costing to awards -> effort statements ->
   certification routing), where the client certifies effort against sponsored funding.

### Key BPs

Award Event (create/amend award), Award Budget events, Grant/Sponsor setup, Award Billing /
Sponsor Invoice events, Effort Certification, and the costing-allocation events that charge
salary to awards (payroll costing allocations - payroll.md). Award-funded project work also
runs the project BPs in projects-and-revenue.md.

### Hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; F&A parameters from wd-discovery integration-discovery.md; verify in-tenant)

- **F&A is rule-driven, not a flat percent**: the indirect-cost calculation depends on the
  rate TIER, the MTDC base (which cost categories are EXCLUDED from the base - equipment,
  subaward amounts above the cap, tuition, participant support), and the effective rate for
  the period of performance. A design that applies one flat F&A rate to total cost is wrong;
  model the base exclusions.
- **Subaward cap**: F&A typically applies only to the first tranche of each subaward (the
  cap), not the whole subaward - a common base-exclusion the client's rate agreement fixes.
  Federal default (2 CFR 200.1 "Modified Total Direct Cost", 2024 revision): the first $50,000
  of each subaward for federal awards made on or after 2024-10-01; the first $25,000 for
  earlier awards unless the awarding agency applied the 2024 rule to them. A tenant can hold
  both, so the cap is per award, not one tenant constant. Confirm the cap amount in-tenant.
- **Cost-share and tuition remission** are separate rule sets that alter the base and the
  effective charge - carry them as explicit config, not afterthoughts.
- **Grant worktag is a financial worktag** under the tenant ceiling (15 custom worktag types
  + 10 custom-org financial worktags per tenant - financials.md); required-worktag usage is
  TENANT-WIDE per transaction type. Inventory existing usage before claiming Grant as a new
  required tag.
- **Award periods of performance gate charges**: costs dated outside the award period, or an
  inactive/closed award, fail or route to error - integrations posting to awards must respect
  the period and status.
- **Grants sponsors are NOT student financial-aid sponsors**: Workday Student sponsor
  contracts (student.md) are a DIFFERENT object with their own precedence rules; do not
  conflate the two when a university runs both SIS and Grants.
- "Enforce Required in Web Services" (tenant validation setting) governs whether
  red-asterisk required fields apply to web-service submissions - an award/budget load that
  works in one tenant can reject in another on this checkbox alone (same trap as
  financials.md / hcm-core.md).

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory - financials.md):

- **Financial Management - 431 operations** - grant/award worktag setup (Put Custom Worktag),
  award budgets via **Import Budget** (4 import modes incl. Replace All and zero-amount
  deletes; Plan Event BP unless auto-complete - financials.md), and the journals grant
  accounting posts. Confirm the exact Award / sponsored-program operation names in-tenant
  (doc-sourced; not build-verified in the suite).
- **Revenue Management - 308 operations** - the award-billing / sponsor-invoice / letter-of-
  credit surface (billing side, shared with projects-and-revenue.md). Confirm exact
  operation names and count in-tenant (doc-sourced; not build-verified in the suite).
- **Resource Management - 394 operations** carries award-funded project + expense + asset
  transactions that charge to the Grant worktag (financials.md).

REST / WQL / RaaS:

- **No grants-specific REST service exists in the suite's rest-api-catalog snapshot** - there
  is no `grants`/`awards` service among the 51 (rest-api-catalog.md). Do NOT invent one.
  Adjacent build-verified surfaces: **budgets v1 `/runBudgetCheck`** (pre-flight a
  transaction against budget plans, incl. award budgets), **worktag v1 `/validateWorktags`**
  (validate Grant/Fund/Program worktag combos before submit), **coreAccounting v1
  `/evaluateAccountPostingRules`**, and - for award-funded projects/billing -
  **projects v3 (64 ops)** and **revenue v1 (5 ops, billableTransactions)**
  (projects-and-revenue.md). All build-verified from the snapshot (rest-api-catalog.md).
- WQL / RaaS: grant/award, award-budget, sponsor, and award-billing data sources back
  reporting and the sponsor/agency extracts grants reporting lives on; RaaS custom reports
  remain the outbound workhorse (~2083-char URL guard - wd-extend-dev orchestration.md).
  Confirm exact data-source names in-tenant.

Delivered connectors and hooks:

- **No grants/award-specific delivered Core Connector is named in the suite's
  integration-naming.md** (its CC list carries nothing for grants, awards, or sponsors). Do
  NOT assume one exists; confirm the delivered-integration catalog in-tenant before scoping a
  custom feed. Naming formats that DO exist: Grant worktag `GR-yyyy-nnnn` (auto sequence),
  Program `PG1nnnn`, Fund `FD1nn`, Sponsor sequence generator `SPN` (integration-naming.md).
- BP hooks: Award, Award Budget, Award Billing, and Effort Certification events can carry
  integration/service steps and Extend BP-triggered orchestrations (useForOrchestrate -
  wd-extend-dev orchestration.md); Model BPs give custom award-companion objects their own
  routable events (wd-extend-dev model-bp.md).

## 3. Solution patterns + donors

- **Award-intake / proposal companion Extend app** - an Extend BO intake (award-setup or
  proposal-routing form with its own BP) that then creates the Award / sponsor / budget via
  SOAP or the budget import. No grants-specific build-verified donor is on disk; reuse the
  hcm-core.md "custom work-event app with its own BP" shape - build-verified donor
  `createAWorkEvent` (custom .businessprocess + wizard + hub), production-shaped sibling
  `workFromAlmostAnywhere`. The pattern transfers; the write target differs.
- **Award budget load** - drive **Import Budget** (Financial Management, build-verified in
  financials.md's WWS list) through the generic O4I import framework (submit -> poll
  Get_Import_Processes -> harvest Get_Import_Process_Messages) whose build-verified donor is
  `supplierInvoicesInbound` (same framework, DIFFERENT payload - financials.md). No
  grant-budget-specific donor exists on disk - say so in an estimate.
- **Award billing / sponsor invoice + letter-of-credit draw** - billing side; reuse the
  projects-and-revenue.md billing patterns (revenue v1 / customerAccounts v1, Revenue
  Management SOAP). No award-billing build-verified donor exists in the suite; a
  letter-of-credit federal-draw feed is almost always NET-NEW O4I work, not a conversion -
  estimate accordingly (mirrors the financials.md GL-outbound finding).
- **F&A / cost-share reconciliation sweep** (read award costing -> compute indirect ->
  compare) - Boomerang shape: build-verified O4I donor `updateServiceDateBoomerang`
  (RaaS/WQL read -> loop -> SOAP/REST write); INT126-style Studio donors on the financials.md
  registry. The F&A math itself is delivered engine config - do not re-implement it in a flow
  unless reconciling, not replacing, the delivered calculation.
- **Effort-certification companion / reminder** - a Model-BP fan-out to a population mirrors
  the hcm-core.md `crisisCheckin` donor (AsyncProcessListOfWorkersToLaunchModelBP) for effort
  campaigns; the certification itself stays on the delivered effort BP.
- Award-funded PROJECTS overlap projects-and-revenue.md - for the project plan / resource
  plan / project-billing layer read that file rather than duplicating it here.

## 4. Design gotchas

- F&A is a base-and-tier calculation, never a flat percent - model MTDC exclusions
  (equipment, over-cap subaward, tuition, participant support), the rate tier, and cost-share
  before an integration touches indirect cost; the delivered engine owns the math.
- Subaward F&A caps and tuition remission are separate rule sets that change the base -
  confirm both against the client's negotiated rate agreement, not a generic assumption.
- Grant worktag is a financial worktag under the tenant ceiling - inventory existing custom
  worktag usage (financials.md) before a design claims Grant as a new required tag.
- Award period of performance and status gate every charge - costs outside the period or on a
  closed award fail; inbound integrations must check period + status, not just the worktag.
- Grants sponsors vs Student sponsor contracts are different objects (student.md) - at a
  university running both, keep them distinct in security and in any reconciliation.
- Verify the tenant actually HOLDS grant/award/sponsor data before designing on it (a bare
  dev tenant will not) - trust-but-verify
  (wd-extend-lifecycle/references/verify-in-tenant.md).
- Functional literacy (what a sponsor / award / F&A rate / MTDC base / effort statement IS,
  the sponsored-research vocabulary) lives in wd-discovery functional-financials.md - this
  playbook assumes it; the F&A discovery cues are in wd-discovery integration-discovery.md.
