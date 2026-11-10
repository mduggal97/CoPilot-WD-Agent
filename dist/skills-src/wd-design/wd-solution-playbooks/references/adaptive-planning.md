# Adaptive Planning (EPM): versions, levels, accounts, sheets - integration + scoping playbook

Workday Adaptive Planning is a SEPARATE Workday product (the EPM / financial-planning
layer), NOT a domain of the core HCM/Financials tenant. It has its OWN object model
(versions, levels, dimensions, accounts, modeled + cube sheets) and its OWN API - it does
not live in the WWS/RaaS/WQL surface the other playbooks describe. So this playbook is an
INTEGRATION-SURFACE + SCOPING guide, not a tenant-config spine: the suite's role is the
Workday <-> Adaptive integration and the scoping around it. Extend and O4I do NOT build
INSIDE Adaptive - there are no Adaptive "pages" or "business objects" for the suite to
author; the build is the data bridge.

Provenance is honest and thin here. Adaptive specifics below are [DS] (doc-sourced,
Workday Adaptive product knowledge; verify in-tenant / in the Adaptive instance) unless
tagged [BV]. This is a distinct product with far less build-verified suite coverage than
the core-tenant domains, so treat every Adaptive object/API detail as "confirm in the
actual Adaptive instance" - the suite has not build-verified an Adaptive integration on
disk. Where the suite DOES have build-verified ground (the WD-side load mechanics, Prism,
variance reporting) it is tagged [BV] and cross-linked. Before designing on Adaptive data,
verify the instance actually holds the model you assume (a bare instance will not) -
trust-but-verify (wd-extend-lifecycle/references/verify-in-tenant.md). [BV]

## 1. Configuration spine

This is Adaptive's OWN model, and it is configured INSIDE the Adaptive instance, not the
WD tenant. Know it to scope the integration - do not expect to build or edit it from
Extend.

### Adaptive object model (high level) [DS] confirm in-instance

- **Versions** - the top-level container for a set of plan/forecast/actuals data (e.g.
  "Working Budget", "FY Forecast", "Actuals"). Versions are how Adaptive separates
  scenarios; almost every reconciliation and load question routes back to "which version".
  There is typically a locked/published actuals version and one or more working plan
  versions.
- **Levels** - Adaptive's organizational hierarchy (the rough analog of WD cost
  centers / supervisory orgs / companies). Levels are where WD org structure MAPS IN, and
  the mapping is the #1 drift risk (see gotchas). Levels can be owned/assigned for
  workflow.
- **Dimensions** - the analytical attributes on data (product, region, department,
  worktag-like slicers). WD dimension values (cost center, region, custom worktags) sync
  into Adaptive dimensions; names/IDs rarely match 1:1 out of the box.
- **Accounts** - the chart of accounts inside Adaptive (GL accounts, plus calculated /
  assumption / metric accounts). WD ledger/GL accounts map to Adaptive accounts; Adaptive
  also holds accounts that have no WD equivalent (drivers, ratios).
- **Sheets** - where data lives and is edited:
  - **Modeled sheets** - row-based, structured planning sheets (e.g. personnel/headcount,
    capital, revenue detail) with per-row logic. Used for driver-based planning.
  - **Cube sheets** - multi-dimensional grids (accounts x levels x dimensions x time) for
    the general financial model. This is usually where actuals land and where variance is
    computed.
  - Cube vs modeled is a real design fork: actuals + GL-style data -> cube; detailed
    driver plans (headcount, assets) -> modeled. Getting the target sheet type wrong
    breaks the load mapping.
- **Time** - Adaptive has its own time/period model (fiscal calendar, months, quarters);
  it must be reconciled to the WD fiscal schedule for actuals to land in the right period.

### How a WD tenant connects to Adaptive [DS] confirm in-tenant + in-instance

- The delivered path is the **Workday-Adaptive integration** (the Adaptive Integration
  framework), commonly surfaced as the **Workday Data Connector / integration** between
  the WD tenant and the Adaptive instance. This is Workday-delivered plumbing whose whole
  job is to move WD structure + actuals INTO Adaptive on a schedule - prefer it over any
  hand-built bridge (see Solution patterns).
- Adaptive also has its own native connectors/loaders (data import from files/API, and
  standard connectors) for non-WD sources. For a WD <-> Adaptive engagement, the delivered
  Workday connector is the default; custom EIB/API is the exception, not the rule.
- **Licensing/enablement gate:** Adaptive is a separately licensed product with its own
  instance and admin. Confirm the client actually has Adaptive provisioned AND the
  Workday-Adaptive connector enabled before scoping integration work - this is a common
  discovery miss ("they said planning, they meant a WD budget", or vice versa). [DS]

## 2. Technical surface

Unlike the core-tenant playbooks, the primary surface here is NOT WWS/RaaS/WQL - it is the
delivered connector plus the Adaptive API. WD's own SOAP/REST surface participates only as
the SOURCE of actuals/structure that the connector reads.

### Delivered Workday-Adaptive connector (the default) [DS] confirm exact behavior in-tenant

- **WD -> Adaptive, actuals load:** the connector extracts posted GL actuals from the WD
  Financials ledger and loads them into the target Adaptive version (usually a cube sheet,
  Actuals version), mapped by account / level / dimension / period. This is the core,
  recurring flow.
- **WD -> Adaptive, structure/dimension sync:** the connector also syncs WD structure into
  Adaptive - organizations / cost centers -> levels, and WD dimension values (cost center,
  region, custom worktags, worker/position data for headcount planning) -> Adaptive
  dimensions/accounts. Structure sync should run BEFORE the actuals load so the actuals
  have somewhere to land.
- **What flows each way (typical):**
  - Into Adaptive: GL actuals; org/cost-center/company structure; dimension values; often
    worker/position/headcount + compensation data for personnel planning.
  - Back into WD: plan/budget data, so WD can run **budget-vs-actual variance** against a
    published Adaptive plan (this is the adjacency where the suite genuinely helps - see
    section 3 and the financials cross-link).
- Confirm the connector's exact object coverage, mapping tables, and scheduling in the
  specific tenant + Adaptive instance - delivered behavior varies by release and by how
  the client configured the integration. [DS]

### Adaptive API / loader (for custom data) [DS] confirm in-instance

- Adaptive exposes its own API (historically a SOAP-style Adaptive API; confirm the
  current REST/API surface and auth for the client's instance) plus file-based import for
  loading data the delivered connector does not cover (e.g. non-WD source data, statistical
  drivers, external actuals).
- Auth, endpoints, and object names for the Adaptive API are INSTANCE-specific and are NOT
  in the WD WWS master inventory - do not assume the WD OAuth/ISU pattern applies. Treat
  Adaptive API access as a separate credential/governance item. [DS]

### WD-side source surface (build-verified) [BV]

- The WD side of "get actuals / structure out of Workday" IS build-verified suite ground:
  GL actuals come from Financial Management journals/ledger reads and RaaS custom reports;
  org/cost-center/worker structure comes from the HCM/FDM surfaces the other playbooks
  document (see financials.md section 2 for Financial Management ops and Import Budget;
  hcm-core.md for org/worker). If a custom extract-to-Adaptive is needed, THAT extract is
  ordinary suite work (RaaS -> file/API) even though the Adaptive landing side is not.
- **Import Budget** (WD Financial Management, 4 import modes incl. Replace All) is how
  plan/budget data comes BACK INTO WD for variance - build-verified in financials.md. This
  is the concrete WD endpoint for the Adaptive-plan-to-WD direction. [BV]

## 3. Solution patterns + donors

**Honest donor status: the suite has little-to-no build-verified Adaptive donor on disk.**
No Extend or O4I app that integrates with Adaptive has been build-verified in the local
corpus this session. Do not cite an Adaptive donor as build-verified. The build - when a
custom bridge is actually needed - is owned by **wd-integration-dev** (EIB/Studio/API) and,
for any WD-side orchestration, **wd-extend-dev** (O4I / RaaS extract). Point there for the
actual construction; this playbook scopes it.

- **Delivered connector first (the default pattern).** For WD -> Adaptive actuals +
  structure, configure the delivered Workday-Adaptive integration / Data Connector. This
  is almost always the correct answer; it is delivered plumbing, not a build. Scope =
  configuration + mapping + schedule, not code. [DS]
- **Custom EIB / API only when the connector cannot cover it.** Reach for a custom bridge
  only for data the delivered connector does not carry (non-WD source data, unusual driver
  feeds, a bespoke cadence). Then:
  - WD -> Adaptive custom load: extract from WD via RaaS custom report (the outbound
    workhorse; ~2083-char URL guard - wd-extend-dev orchestration.md [BV]) or EIB, then
    load to Adaptive via its API/import. The WD-extract half reuses the generic outbound
    shape (donor `employeeDemographicOutbound`: RaaS -> CsvFormat, sequenced filename -
    hcm-core.md [BV]); the Adaptive-landing half is NET-NEW, instance-specific work with
    no build-verified suite donor. Estimate the Adaptive side as new build, not a
    conversion. [DS]
  - Adaptive plan -> WD: land Adaptive plan/budget output into WD via **Import Budget**
    (financials.md [BV]) for variance. The file/API extract out of Adaptive is
    instance-specific; the WD import side is build-verified.
- **Variance / budget-reporting angle (where the suite adds real value).** Once plan data
  is in WD (via connector or Import Budget), budget-vs-actual variance, attestation, and
  projection reporting are ordinary WD work - Prism + Extend + Report Writer. This is the
  ADJACENT surface the suite is strong at: see **financials.md** (Import Budget, planning/
  stats ops, Accounting Center/Prism feed pattern) [BV] and **analytics-prism.md** for the
  reporting-surface choice. If the client's real ask is "see the variance in Workday", the
  heavy lift may be WD-side reporting, not the Adaptive integration at all. [BV]
- **WD Data Cloud / analytics angle.** Where the client is heading toward WD Data Cloud /
  LDQ for cross-domain analytics, Adaptive plan data landed in Prism/Data Cloud can join WD
  actuals for variance analytics without a round-trip back into the transactional ledger -
  note it as an option, confirm the client's Data Cloud posture (analytics-prism.md;
  wd-extend-dev prism-and-reporting.md for the build). [DS] confirm-in-tenant

## 4. Design gotchas

- **Extend does not build inside Adaptive.** There are no Adaptive PMD pages / business
  objects / Model BPs. Extend can SURFACE Adaptive data in a WD app only by first
  integrating it INTO the WD tenant (connector or custom load -> WQL/Prism-readable) - it
  cannot query the Adaptive model natively. Design any "show planning data in our app"
  request as an integration + WD-side store, not a live Adaptive read. [DS]
- **Version management is the reconciliation spine.** Every load and every variance is
  version-scoped. Loading actuals into the wrong version, or comparing a working plan to
  actuals from a mismatched version, produces silently wrong numbers. Nail down the version
  map (which WD data lands in which Adaptive version, which version is "the plan" for
  variance) at design time. [DS]
- **Actuals-vs-plan reconciliation.** WD actuals and Adaptive plan live in two systems with
  two calendars, two account structures, and two level/dimension trees. Reconciliation
  breaks on: period/fiscal-calendar mismatch, account-mapping gaps (a WD account with no
  Adaptive target, or vice versa), and currency/precision differences. Agree the
  reconciliation rules (rounding, unmapped-account handling, period cutover) before build. [DS]
- **Dimension / level mapping drift.** WD org/cost-center/dimension IDs rarely equal
  Adaptive level/dimension IDs 1:1, and the two structures DRIFT over time (a new WD cost
  center with no Adaptive level, a renamed dimension). Structure sync must run before
  actuals, and unmapped-value handling must be explicit - unmapped actuals either fail or
  dump into a catch-all level and quietly distort the plan. [DS]
- **Licensing / provisioning gate.** Adaptive is separately licensed with its own instance
  and admin. Confirm it exists and the Workday-Adaptive connector is enabled before
  committing to integration scope; do not assume "they have Financials so they have
  planning". [DS]
- **Adaptive API is not the WD API.** Different auth, endpoints, and object names; not in
  the WWS master inventory; separate credential + data-governance item. Do not lift the WD
  OAuth/ISU pattern onto Adaptive. [DS]
- **The real ask may be WD-side.** "Budget variance" often means WD reporting on
  already-loaded plan data (financials.md variance angle [BV]), not new Adaptive
  integration. Scope what actually needs to move before assuming an Adaptive build.

Cross-refs: financials.md in this skill (Import Budget, planning/stats ops, variance /
Accounting Center + Prism feed - the adjacent surface the suite is strong at) [BV];
analytics-prism.md (reporting-surface + Data Cloud/LDQ choice); hcm-core.md (org/worker
structure that syncs into Adaptive levels/dimensions). Build owners: wd-integration-dev
(EIB/Studio/API bridge) and wd-extend-dev (O4I / RaaS extract, Prism, prism-and-reporting.md).
Verify-in-instance pointer: wd-extend-lifecycle/references/verify-in-tenant.md (and confirm
the Adaptive instance holds the model you assume).

Functional-literacy footer: there is NO wd-discovery functional file for Adaptive Planning /
EPM (functional-financials.md and workday-functional-skus.md do not cover it) - a known
LITERACY GAP. Until one exists, ground planning/EPM concepts (what a version / level /
dimension / cube-vs-modeled sheet IS) directly from Workday Adaptive product docs, and flag
the gap to the suite maintainer.
