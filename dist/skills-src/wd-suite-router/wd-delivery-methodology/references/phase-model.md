# The phase model - a full Workday deployment, end to end

> Vendor-neutral. Phase names follow the vocabulary Workday itself uses publicly for
> deployments (Plan / Architect / Configure & Prototype / Test / Deploy), with generic
> pre-project and post-production phases added. Rename freely to match a firm's or
> client's own methodology - the WORK in each phase is what matters.

**One gloss up front - "tenant":** a tenant is a full, separate instance of the client's
Workday environment. An implementation runs SEVERAL in parallel (build, test, parallel,
production), they get wiped and refreshed on schedules, and configuration does NOT move
between them automatically - it must be deliberately migrated (wd-deployment).

## Two delivery models (know which you are on)

- **Packaged / fixed-scope** - the midmarket pattern (Workday's own "Launch"-style
  offerings and partner equivalents): time-boxed (roughly 6-9 months), fixed fee,
  pre-built workbooks and milestone plans, scope controlled by the package definition.
  Speed comes from ADOPTING the package's decisions, not re-litigating them. In this
  model: Ready compresses to a light readiness pulse, the Plan artifacts (plan, tenant
  schedule, workbooks) arrive largely pre-built, and the guiding principles are mostly
  inherited from the package - the client's job is to accept them knowingly.
- **Tailored enterprise program** - larger, phased, multi-module programs (common in
  higher-ed, healthcare, and complex enterprises): scope, sequencing, and governance are
  designed per client; readiness and operating-model work carry real weight; timeline is
  driven by data conversion, integrations count, and decision velocity. Here Ready is a
  real phase, governance is designed (not defaulted), and the plan is built bottom-up.

State which model the engagement is on at kickoff - artifacts, cadence, and the client's
decision burden differ substantially between them.

## The phases

1. **Initiate (pre-plan)** - the sales-to-delivery handoff. Read the signed SOW (statement
   of work - the contract's scope document) in detail with client and delivery leadership
   in the first two weeks: scope and timeline are tightly coupled, so scope control starts
   here, not at the first change request. Stand up team access (tracker workspace,
   tenants, distribution lists), onboard the team, and publish a first-30-days task list.
2. **Ready** - is the ORGANIZATION ready, not just the software? Build the case for change
   (why now, what changes, cost of not changing); run a readiness assessment (survey +
   stakeholder interviews, repeated in rounds so you get a trend, not a snapshot); start
   the change-impact inventory and the champion/change network; capture the program's
   OUTCOME BASELINES here (the current-state metrics that value realization will be
   measured against - the technical sub-track calls this work "discovery"). For
   assessment-only engagements, this phase is the engagement. (The OCM instruments live
   in wd-change-adoption - this phase is where they start.)
3. **Plan** - authorize, resource, schedule. Produce: project charter; governance model
   (executive sponsor -> steering committee -> program management -> workstream teams);
   4-6 written **guiding principles** (decision guardrails - see delivery-norms.md); the
   RAID log and tracker stood up (wd-pm / wd-smartsheet); the project plan with the
   mandatory gates as dated tasks; the **tenant management plan** (which tenants exist,
   what each is for, refresh schedule); configuration workbooks issued to the client
   (at this stage they are foundation-data questionnaires - legal entities, org
   structures, calendars, current-state facts; they grow into the design-decision record
   later, see delivery-norms.md); and the initial foundation tenant built from those
   client-completed workbooks and smoke-tested. Engage the data-conversion team from day
   one - the first tenant build is usually the critical path.
4. **Architect & Configure** - the build heart. Cross-area design kickoff workshops open
   the phase (they fix the shared skeleton - foundation data, org structures, calendars,
   cross-module design decisions - before per-area design starts); then per-area design
   sessions produce documented design decisions tracked in the configuration workbook;
   configuration follows the per-area configuration guides (config-guide-pattern.md),
   reusing catalogued solutions before building net-new (wd-practice-ops reuse catalog);
   **customer confirmation sessions** play configured functionality back to the client
   for structured sign-off; unit testing runs against the build tenant; reports,
   integrations, and Extend apps build in parallel on their own sub-track
   (wd-extend-lifecycle); the phase closes by assembling the end-to-end tenant.
5. **Test** - prove the WHOLE tenant works and the organization is ready to run it.
   Stage test events from most granular to most production-like, each tied to a tenant
   and a build-validation gate (see the build sequence below): unit -> end-to-end
   business process ("relay-style" across areas) -> payroll parallel (compare legacy vs.
   Workday gross-to-net over one or more full cycles, in a dedicated tenant) ->
   regression (after feature releases) -> performance -> user acceptance (real client
   users, real scenarios; in higher-ed, a mock-term simulation). Set NUMERIC exit
   criteria per event (percent executed, percent passed, blocker disposition,
   workarounds documented) and agree them with the client before the event starts.
   Cutover and readiness PLANNING begin in this phase - checklist, rollback/contingency,
   first go/no-go checkpoints (wd-deployment). Defect-vs-change-request discipline
   tightens as go-live nears (wd-testing).
6. **Deploy** - cutover -> go-live. Final production build and data conversion, final
   go/no-go with a named decider, execute the cutover checklist daily, legacy freeze and
   rollback plan per wd-deployment. Nothing new enters scope in this phase without
   executive-level change control.
7. **Support (stabilize -> steady state)** - hypercare (typically 4-8 weeks; longer for
   Student, where stabilization spans a full academic cycle), production-support
   operating model stood up (service tiers, escalation, operational governance), adoption
   measured against the baselines captured in Ready, stabilization tracked against
   quantified criteria agreed before go-live, lessons-learned session, then closeout:
   actuals written back to estimation calibration, reusable assets harvested
   (genericized) into the practice catalog, KT sign-off. Mechanics: wd-post-go-live,
   wd-kt, wd-practice-ops.

**Timeline shape (typical, never committed):** Architect & Configure and Test are the two
long poles - together they usually consume well over half the calendar, roughly evenly
split; Plan and Deploy are short and sharp; Ready and Initiate overlap other work. Data
conversion and client decision velocity are what stretch a timeline, more than
configuration effort (sizing by role and phase: wd-estimate).

## The build-and-conversion sequence (what "sign off each build" means)

Tenant builds run as a named sequence, each fed by a conversion pass and consumed by test
events:

1. **Foundation build** (Plan) - from the client's foundation workbooks; smoke-tested;
   sign-off = foundation data verified.
2. **Configuration/end-to-end build(s)** (Architect & Configure -> Test) - configuration
   plus a fuller conversion pass; consumed by unit and end-to-end testing; sign-off per
   build.
3. **Parallel build** (Test, where payroll is in scope) - production-grade conversion for
   payroll-parallel cycles.
4. **Final ("gold") build** (late Test -> Deploy) - the production-candidate: final
   configuration, near-final conversion, consumed by regression/UAT; its sign-off gates
   go-live authorization.
5. **Production build** (Deploy) - the cutover conversion into the production tenant.

**Conversion cadence rule:** one reconciled conversion pass per major build - reconcile
counts and balances source-vs-loaded BEFORE the test event that consumes the build, never
during it. The data-conversion lead owns the pass schedule; it belongs on the project
plan as dated tasks.

## Cross-map to the wd-extend-lifecycle sub-track

| Sub-track phase (wd-extend-lifecycle) | Program phase (this model) |
|---|---|
| Estimate, Contract | Initiate (or pre-program pursuit) |
| Discovery | Ready / Plan |
| Design (+ visuals) | Architect & Configure |
| Build (Extend/integrations) | Architect & Configure |
| Test | Test |
| Deploy / cutover | Deploy |
| Post-go-live | Support |

An Extend app or integration delivered INSIDE a full deployment follows the program's
gates; one delivered standalone (to a live client) runs the sub-track on its own.

## Cross-cutting threads (run the whole lifecycle)

- **Governance** - the committee bodies with a stated cadence and decision rights;
  governance fails when leaders bypass it, so decisions must stick or be formally
  superseded (wd-pm steering/decision conventions).
- **Change management** - the people side, parallel to the build from Ready onward
  (wd-change-adoption).
- **Knowledge transfer** - continuous, not an end-phase event; client counterparts should
  OWN their area's design by Test (wd-kt).
- **Quality assurance** - independent checkpoint reviews at phase exits, where
  "independent" means the reviewer sits outside the workstream being reviewed (the
  engagement manager commissions them - see roles-and-raci.md); the suite's quality-gate
  registry (wd-extend-lifecycle references/quality-gates.md) is the every-artifact
  enforcement layer.
- **Value/outcomes** - baseline metrics in Ready, targets at design sign-off, actuals
  post-go-live (wd-post-go-live value capture).

## Exit conditions (the phase-gate pattern)

Every phase exits on NAMED conditions, reviewed with the client, with exceptions logged as
RAID items with owners - never silently. Typical gates per phase:

- **Initiate**: SOW walkthrough held with both leaderships; team access stood up.
- **Ready**: case for change accepted by the sponsor; readiness baseline + outcome
  baselines captured.
- **Plan**: charter + governance + guiding principles + plan signed; foundation tenant
  smoke-tested.
- **Architect & Configure**: design decisions documented and confirmed (confirmation
  sessions held); unit scenarios captured; end-to-end tenant assembled.
- **Test**: each event passed against its agreed criteria; gold-build sign-off; go-live
  authorization signed.
- **Deploy**: cutover checklist complete; production handover accepted.
- **Support**: hypercare exit criteria met; support model operating; closeout artifacts
  filed.

Put the gates on the project plan as dated tasks the day the plan is drafted.
