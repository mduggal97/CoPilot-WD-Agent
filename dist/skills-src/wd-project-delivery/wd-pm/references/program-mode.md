# Program Mode - Coordinating Multiple Extend Apps

Switch to program mode when 2+ Extend apps run in parallel for one client.
A large program can run 8+ concurrently (e.g., a mix of request/config, costing-allocation, reconciliation, form-routing,
variance-reporting, access-provisioning, and O4I-integration apps - each with its
own use-case/app ID per the engagement's ID convention). Per-app routines (SKILL.md) still
apply inside each app; program mode adds the coordination layer.

## Shared tracker with per-app workstreams

One program tracker, one row per app (Extend Tracker pattern - sheet IDs live in the
ENGAGEMENT'S PROJECT MEMORY, not in any skill; the registry SHAPE to record them in is
wd-smartsheet `references/smartsheet-registry-template.md`):

- Inventory ID + name (per the engagement's use-case/app ID convention), Type, Client/firm-owned
- Phase statuses: Design / Prototype / Build / Test / Deploy / Overall
- Design due date, Build due date, current RAG

The program plan workbook follows project-plan-format.md with **one tab per app**
plus a MASTER TIMELINE tab of all apps' gates and go-lives - that timeline is the
single view for spotting collisions (two UATs same week with the same client SMEs;
two go-lives in one tenant window).

## Program-level RAID with app tags

**One** program RAID, not eight app RAIDs (columns per raid-log.md):

- Every row carries an **App / Workstream tag**; program-wide rows tagged `PROGRAM`.
- One weekly program review covers the whole log, filtered views per app.
- Cross-app risks are the ones an app-level log structurally misses - a shared
  SME bottleneck, a tenant refresh that hits three test cycles, one Workday
  gating-review queue. Tag them `PROGRAM` and score them against the worst-hit
  milestone.
- One Decisions log for the program: decisions on one app often bind the others
  (naming standards, shared-component ownership) - decide once, tag `PROGRAM`.

## Cross-app collision checks

Run at design sign-off for every new app (add as a Design-phase task row):

- **App reference IDs**: Extend app reference IDs are tenant-unique - check the
  new app's ID against every deployed/in-flight app before creation (rename is
  painful after objects exist).
- **Security domain names**: custom domain and security-group names collide in
  the tenant; keep one program-wide naming register (app-prefixed names, e.g.
  `<AppPrefix> - Administrator`) and check new domains against it.
- **Business-object and orchestration names**: same register, same rule - a
  consistent app prefix prevents both collisions and month-6 confusion.

All three checks are runnable live via tenant-ops reads - the tenant is the
authoritative register; keep the naming register as the intent list and diff it
against the tenant at each design sign-off (wd-extend-dev references/tenant-ops.md).

## Cross-app dependency register

Apps that share nothing at design time grow couplings by go-live. Keep one
register so a change in one app can't silently break another:

- Columns: **consumer app -> provider** (app / BO / integration / security
  group / report) -> **coupling type** (reads BO, calls orchestration, shares
  security group, consumes RaaS report, Boomerang) -> **break-impact** (what
  fails downstream, and how loudly).
- Review at **every design sign-off** (a new app declares what it consumes
  and what it exposes) and **before any go-live reordering** - resequencing
  go-lives is where a consumer ships before its provider.
- A provider-side change (BO schema, report definition, security group) raises
  an action per consumer app - same discipline as shared-component fixes below.

## Program tech-debt register

Debt outlives the app project that created it; the program owns the ledger:

- Columns: item, **source** (PoC shortcut / CR deferral / preview-feature
  fallback), affected app(s), **cost-to-fix** (S/M/L), **trigger-to-revisit**
  (a date, a release, a volume threshold - never "someday").
- Harvest points: **build complete** (sweep the OI-tagged assumptions
  wd-extend-dev's PoC guidance requires developers to leave in code) and
  **hypercare exit** (workarounds that shipped).
- Closeout rule: an app project's open tech debt **transfers here, never dies
  with the project** - wd-post-go-live's closeout checklist points at this
  register.

## Shared components - reuse, don't rebuild

Patterns proven in one app (sequence generators, SOAP subflows, error-handling
orchestration wrappers) get reused via **wd-extend-dev**'s `wdcli app copy`
patterns rather than rebuilt per app. Program-mode duties:

- Keep a shared-components register: component, source app, version/date copied,
  consuming apps.
- When a shared pattern gets fixed in one app, raise an action per consuming app
  to port the fix - copies don't auto-update.
- Assign each shared component one owning app/developer ("who owns what" for code).

## Shared program data

Maintain once at program level; reuse for every app's paperwork:

- **Contacts**: client program contacts, delivery-team leads, Workday CSM - the same
  block feeds every Volumes Questionnaire and Perf Testing Template
  (see the reference_extend_volumes_questionnaire / perf-testing standards).
- **Tenants**: sandbox / implementation / prod tenant names, refresh schedule -
  refresh dates are program-level plan rows because they hit every app's testing.
- **Environments/credentials process**: ISU/ISSG setup conventions per app,
  tracked in the naming register.

## Program capacity ledger

Workday sizes each Volumes Questionnaire app-by-app; nobody but the program
sees the SUM. Keep one ledger, one row per app:

- Per app: declared **annual + peak volumes**, worker count, and
  **orchestration schedules** (actual run windows, not just cadence).
- A **total row** compared against the client's Extend capacity tier - eight
  individually-modest apps can be a collectively-loud tenant.
- **Schedule-collision check:** map the nightly windows. Two heavy
  orchestrations landing in the same window is a capacity event even when
  every annual volume is fine - stagger them here, at the program level,
  because no single app's design review can see the overlap.
- Update triggers: any Volumes Questionnaire submission (wd-deployment's
  volumes-questionnaire.md writes back here), any order-of-magnitude delta
  between actuals and declared volumes, and any new app entering design.

## Batching Workday gating docs

Every Extend app needs the Volumes Questionnaire approved by Workday before go-live
(hard gate); the Performance Testing Template is required per Workday's volume
threshold (~50K annual transactions - wd-deployment owns the rule and templates;
under threshold it's optional good practice). In program mode, **batch them**:

- Group apps with adjacent go-lives into one submission wave; reuse the shared
  program-data block; submit together so Workday reviews them as a set.
- Track each app's gating-doc status on the shared tracker (Not Started /
  Drafted / Submitted / Workday-Approved) - an unapproved doc two weeks before
  go-live is an automatic Amber for that app.
- One owner for the whole wave, not one per app.

## Program status rollup

Weekly: RAG table (one line per app: RAG, phase, next milestone + date, one-line
note), then full status blocks (per status-reporting.md) for Amber/Red apps only.
Program-level metrics: apps by phase, gating-doc pipeline, PROGRAM-tagged RAID
items open, cross-app actions past due.
