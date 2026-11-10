# Standing delivery norms - the rhythms every program keeps

> Vendor-neutral. These are the always-on artifacts and disciplines that make a Workday
> program predictable, independent of firm or delivery model. Each norm names the suite
> skill that owns its mechanics.

## One system of record (RAID + decisions)

- **One tracker for the whole program** (wd-pm content rules; wd-smartsheet transport):
  **RAID** (risks, actions, issues, decisions - this suite's expansion; some
  methodologies read the A as assumptions) plus change impacts all live there. Parallel
  spreadsheets are where accountability goes to die.
- **All team members write to it** - entering and resolving items is everyone's job; the
  PM monitors and escalates, they do not transcribe.
- **Decisions stick**: every decision gets date + decider + rationale the day it is made;
  a reversal is a NEW superseding entry, never an edit. High-impact decisions that cross
  governance bodies get a short standalone decision document.
- **Change control formalizes by the Test phase**: during Plan and design, scope
  questions are logged as decision items; from Test onward a formal change-request log
  with impact and approval fields is mandatory, and it tightens as go-live nears
  (wd-pm CR log; wd-design-doc change control).

## The configuration workbook

The client-facing record of what was decided and what was configured, per area: decision,
options considered, rationale, owner, date, and the configuration that implements it.
**Its lifecycle has two stages**: issued at Plan as a foundation-data QUESTIONNAIRE the
client completes (legal entities, org structures, calendars, current-state facts - what
the first tenant build needs), then it grows into the running DESIGN-DECISION record
through Architect & Configure - one artifact, two jobs in sequence. It is the input to
confirmation sessions and unit-test scenario derivation (wd-testing). A configuration
nobody wrote down is a defect waiting for triage.

## Customer confirmation sessions

Structured playback of configured functionality to the client for sign-off: agenda tied
to the workbook's decisions, demo in the tenant (never slides alone), confirmations and
exceptions recorded in the tracker the same day. These sessions are the design sign-off
mechanism for configuration, the counterpart of wd-design-doc sign-off on the
Extend/integration sub-track.

## Guiding principles

4-6 written decision guardrails, agreed with the executive sponsor at Plan, cited in
design sessions to kill circular debates. Classic examples (write the client's own):

- Adopt Workday-delivered functionality first; configure before you customize; extend
  only with a documented business case.
- Design for the majority, not the exception - exceptions get a workaround, not a
  redesign.
- Standardize processes across units unless a regulation says otherwise.
- Decisions are made at the lowest governance level that can make them, and are final
  unless formally superseded.

Over-modification and analysis paralysis are the two classic deployment failure modes;
the principles exist to refuse both in the moment.

## Governance bodies

Executive steering (quarterly-ish: direction, escalations, go/no-go), working/program
steering (monthly-ish: cross-workstream decisions, RAG - red/amber/green - status
review), change control board
(from Test: CR approval), and the PM cadence (weekly status per wd-pm). Publish each
body's decision rights and turnaround expectations in the charter (wd-pm
steering-committee conventions). Governance fails when leaders bypass it - if a decision
was made in a hallway, it gets recorded and ratified or it did not happen.

## Tenant strategy

Write a tenant management plan at Plan and keep it current:

- **Name each tenant's job**: a foundation/build tenant (configuration and unit test), an
  end-to-end/test tenant (integrated test events on converted data), a payroll-parallel
  tenant where payroll is in scope, a final/gold build that becomes production, and
  production itself. Post-production, the sandbox/preview tenants carry release testing.
- **Know the refresh schedule** - what gets wiped and when; unmigrated configuration in a
  refreshed tenant is gone (wd-deployment owns promotion and per-tenant re-setup - and
  security/config does NOT promote automatically).
- **Each test event ties to a tenant and a build sign-off**: unit runs in the
  foundation/build tenant; end-to-end, regression, and user acceptance run in the test
  tenant (regression and UAT against the final/gold build); payroll parallel gets its
  dedicated tenant; performance testing follows wd-deployment's guidance and gating
  documents. The build sequence itself is in phase-model.md.

## The testing ladder

Unit -> end-to-end business process -> payroll parallel -> regression -> performance ->
user acceptance (mock-term simulation for Student). Each event has an entrance gate (build
signed off, data loaded, scenarios ready), NUMERIC exit criteria agreed with the client in
advance, and a sign-off. wd-testing owns scenario derivation and defect/CR triage;
wd-deployment owns performance testing and the production-approval gating documents.

## Meeting norms

State the objective and the intended DECISIONS at the top of every working session; take
notes that feed the tracker (decisions, actions with named owners and dates, new risks);
design sessions get transcripts captured for wd-pm meeting intake. A meeting that
produced no tracker entries either decided nothing or lost what it decided.

## Knowledge transfer as a thread

KT is continuous: counterparts co-facilitate design sessions by mid-build, own their
area's confirmation session content by Test, and demonstrate teach-back before closeout
(wd-kt owns the ladder and sign-off artifact).
