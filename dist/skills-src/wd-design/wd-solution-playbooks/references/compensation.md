# Compensation + Advanced Compensation - solution playbook

Core Compensation (packages, grades, plans, defaulting, one-time payments) plus Advanced
Compensation (merit/bonus/stock review cycles, matrices, scorecards, pools). Config facts
below are doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant.
Web-service names are from the in-tenant WWS master inventory.

## 1. Configuration spine

### Setup order (core)

1. Compensation elements - the bridge to payroll earnings; best practice 1:1
   element-to-earning. Earnings field blank = tracked in comp, never sent to payroll.
2. Compensation eligibility rules - ~50 criteria fields (org, job profile, site,
   position, pay rate type, management level, ...), AND/OR logic. Two rules on the same
   component are automatically OR'd.
3. Compensation grades (required) + optional grade profiles (localization) + steps.
   Grade range violations WARN, they do not error.
4. Compensation plans - salary, hourly, period salary, unit salary, allowance
   (amount/percent/unit), commission, calculated (dynamic vs event-driven), merit,
   bonus, stock, one-time payment.
5. Compensation packages - grouping of grades + plans; the unit of defaulting. Minimum
   viable tenant: one package, one grade, one salary plan.
6. Compensation basis - aggregation layer (Total Base Pay delivered; configurable bases
   ranked per employee; Manage Basis Total for top-down entry).
7. Advanced comp, in order: eligibility rules -> merit/bonus/stock plans -> compensation
   matrices / scorecards -> participation rule sets -> Initiate Compensation Review
   Process. Stock components (grant types, vesting schedules, date rules) must exist
   BEFORE the stock plan.

### Key BPs

Propose Compensation Hire/Change (subprocesses of Hire and Change Job), Request
Compensation Change, Request Grade Change, One-Time Payment, Request Compensation
Change for Leave of Absence, Initiate Compensation Review Process (the advanced-comp
cycle), Change Default Compensation, Requisition Compensation.

### Hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

- Default-comp precedence ladder (highest wins): Offer Compensation > Requisition
  Compensation > Position Compensation > Job Profile Grade (overrides eligibility
  rules) > Compensation Eligibility Rules. Position + requisition compensation together
  is NOT recommended.
- Dual-eligibility kills defaulting: eligible for MORE THAN ONE package or grade =
  nothing defaults. Eligible for a plan NOT in the package = no default (but selectable).
  Design to a single package + single grade per employee.
- Eligibility OR-logic: two rules on one component OR together - a "restrict" rule added
  alongside an existing rule widens eligibility instead of narrowing it.
- Request Compensation Change does NOT evaluate eligibility - it warns on mismatch only.
  Eligibility-rule changes do nothing to current assignments until a comp transaction.
- Calculated plans: DYNAMIC recalculates whenever read (reports/integrations) but
  generates no comp events and no retro/proration; EVENT-DRIVEN updates only during comp
  events (or the Mass Operations Management task) and IS retro-capable. Effective-dated
  requirements force event-driven.
- MBT allocation order is fixed: (1) fixed-amount plans, (2) percent-of-primary-basis,
  (3) percent-of-fixed-number, (4) salary plan, (5) percent-of-prior-boxes,
  (6) remainder plans. Salary Plans Maximum caps at 100 (100 = no limit).
- Element mapping: two plans on one compensation element = duplicate payments.
- One-time payments: no eligibility rule = EVERYONE eligible; one worktag per org type;
  eligibility rules cannot restrict which security group picks a plan (that is
  segmented security).
- Advanced comp cycle: Process Period End Date is THE eligibility date; participation
  rule sets are mandatory or parallel events lock down entirely; cannot rescind a whole
  completed review (per-worker award rescind only); autofill overwrites manager edits;
  grid caps at 500 rows (default 100, indirect reports only); stock frequency is Annual
  only; performance review period end date must fall inside the comp review period or
  ratings do not populate the grid.
- Scorecard funding: without the Manage Bonus Process Funding step on the BP, Workday
  assumes 100% funding and post-approval scorecard updates do nothing. Matrix + scorecard
  weights must total 100%. Company Funding Scorecards cannot have profile goals.
- Irreversible tenant setting: Eligibility Rule Performance Enhancement cannot be undone.
- Expected End Date on a plan needs a scheduled process to actually remove it; Actual
  End Date ends it automatically.

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory):

- **Compensation** - 74 operations. Transactions: Request Compensation Change (+ Import
  Request Compensation Change for bulk), Request One-Time Payment (+ Import), Request
  Bonus Payment, Request Employee Merit Adjustment, Request Default Compensation,
  Correct Compensation Change, Add/Update Stock Grant (+ Bulk Import Update Stock Grant).
  Setup: Put Compensation Plans / Grade / Grade Hierarchy / Eligibility Rule /
  Matrix (+ Bulk Import Put Compensation Matrix) / Scorecard + Scorecard Result /
  Configurable Compensation Basis / One-Time Payment Plan / Stock Participation Rate
  Table. Reads: Get Compensation Plans / Grades / Matrices / Scorecard Results /
  Eligible Earnings (+ Import Eligible Earnings Override). Also benchmark/survey-job
  ops and Put Previous System Compensation History (conversion).
- **Compensation Review** - 22 operations, the advanced-comp cycle surface: Get/Put
  Compensation Review Template, Participation Rule Sets, Validation Rules, Eligibility
  Waiting Period, Deferred Bonus Calculation; Get Employee Awards + Import Employee
  Awards (load proposed awards into a live cycle); Import Compensation Review Budget
  Pools; Get/Import Employee Proration Segment Details. (Get Budget Pools is flagged
  DO NOT USE in the inventory.)

Other read/write paths:

- The manuals' named integration surfaces: EIB loads eligible earnings overrides,
  commission actuals, net-attainment values, and one-time payments (Request One-Time
  Payment web service); Request Compensation Change web service for mass comp changes;
  Update Stock Grant web service / MOM Update Stock Grant Events for post-review grant
  finalization; scorecard results load via Put Compensation Scorecard Result at each
  funding checkpoint.
- Review ratings arrive from Talent via EIB (Bulk Import Update Employee Review Rating,
  Performance Management service - see the talent-and-learning playbook); Pay for
  Performance consumes only the manager's overall rating.
- Reporting: Compensation Review Process Employee Adjustments - Indexed (custom report
  data source); "Enable for Web Services" on an advanced report feeds Docs for Layouts
  compensation statements; HCM Reporting Data Source drives MOM calculated-plan refresh.
- BP hooks: comp events ride Hire / Change Job / Request Compensation Change; a
  BP-triggered orchestration on approval is the standard Extend write-back moment.

## 3. Solution patterns + donors

- **Spot bonus / recognition-to-payment app** - Extend form + approval BP, then write a
  one-time payment on approval. Donors: createSpotBonus (one GraphQL mutation runs
  requestOneTimePayment + initiateWorkerFeedback) and tuitionReimbursement
  (CreateOneTimePayment orchestration; its BP-status subselect - businessProcesses
  {status, businessProcessStepAwaitingAction} in page WQL - is the one-query approval
  grid, per wd-extend-dev wql.md).
- **Off-cycle merit / adjustment intake** - Extend request app feeding Request
  Compensation Change or Request Employee Merit Adjustment on approval; bulk variants
  via Import Request Compensation Change (EIB/Studio - route wd-integration-dev).
- **Commission / variable-pay calculators** - external or Prism-computed amounts landing
  as payroll input or comp transactions. Donor: salesCommission (Prism -> Extend
  pipeline, DCT execution, POST /payroll/v2/payrollInputs).
- **Scorecard funding feed** - integration pushing company/division metrics into
  Put Compensation Scorecard Result before initiation and again before the Manage Bonus
  Process Funding step; small O4I is usually enough (boomerang shape: donor
  updateServiceDateBoomerang in the wd-extend-dev app-catalog registry).
- **Award load into a live cycle** - Import Employee Awards / Import Compensation Review
  Budget Pools when a client models awards outside Workday and loads results back.
- **Comp statement generation** - Docs for Layouts over a web-service-enabled advanced
  report; only build custom rendering when layout demands exceed it.

## 4. Design gotchas

- Never write comp plans directly onto workers when a transaction exists for it - use
  Request Compensation Change so eligibility warnings, routing, and effective dating
  hold; naked Puts of plan assignments bypass the audit trail clients expect.
- An Extend app proposing comp changes mid-cycle collides with participation rules:
  events between Compensation Snapshot Date and Effective Date get coordinated or held.
  Check Compensation Review Options windows before scheduling automated comp writes.
- Rollout Compensation Plans to Employees silently skips anyone with an in-progress comp
  event - a plan-rollout automation needs a sweep-and-retry loop.
- Dynamic calculated plans recalc on every read - an integration extracting them gets
  values as of RUN time, not event time; use event-driven plans when downstream systems
  need point-in-time amounts.
- Grade-range and statutory checks are warnings, not blocks - if a client wants hard
  floors/ceilings enforced from an app, validate in the app before submitting.
- One-time payment loads: Gross Up only works on amount-based plans; Send to Payroll
  unchecked = record-only (use for externally paid awards to avoid double pay).
- Editing a pulled-in performance rating on the review grid does NOT write back to the
  performance review - do not treat the comp grid as a rating correction surface.
- Deprecated ops in the inventory: Request Stock Grant, Put Eligible Earnings, Get/Put
  Compensation Survey Jobs - use the successors (Update Stock Grant, Import Eligible
  Earnings Override, Survey Job Detail/Result ops).
