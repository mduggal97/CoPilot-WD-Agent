# Benefits - solution playbook

Benefit plans, groups, enrollment events (life event / passive / open enrollment),
dependents/beneficiaries, EOI, and the carrier-feed surface. Config facts below are
doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant. Web-service names
are from the in-tenant WWS master inventory.

## 1. Configuration spine

### Setup order

1. Foundation - benefit providers (effective date must be on/before the plan's), coverage
   types, coverage targets (health care / insurance / additional; HSA targets are
   federally fixed at Employee + Family unless the "Other" target is enabled in tenant
   setup), healthcare classifications (PPO/HMO/EPO), related person relationships,
   electronic signatures, benefit eligibility rules (6 types incl. the ACA trio).
2. Benefit groups - membership by eligibility rule; carry frequency, currency, country,
   waiting/grace period calculation ORDER, EOI takes-effect option, flex-credit
   structure (38 credit types).
3. Benefit plans (6 delivered types: health care, HSA, insurance, spending account,
   retirement savings, additional benefit) - providers, participating groups, worker +
   dependent eligibility rules, coverage targets, rates (flat / calculated / individual),
   deductions/earnings.
4. Event setup - benefit plan year definition, enrollment event types, enrollment event
   rules (six-tab config: coverage begin, waiting periods, days to enroll, deduction
   begin, coverage end/grace, levels of change), benefit defaults, cross-plan
   dependencies (4 types), passive event rules, open enrollment event type.

### Key BPs

Change Benefits, Change Benefits for Life Event (subprocess on Hire, Change Job,
Terminate, leave BPs, and more), Change Benefits for Open Enrollment, Reopen Open
Enrollment, Passive Event, Dependent Event, Change Beneficiary, Review COBRA Eligibility,
Change Retirement Savings, Benefits Billing Event. Comp events (Propose/Request
Compensation Change, comp review) also trigger benefit recalcs for salary-based coverage.

### Hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

- Benefit-group single-membership policy trap: a worker matching MORE THAN ONE group's
  eligibility means Workday cannot determine plans/rates/event rules. Groups are not
  system-enforced exclusive - run the Benefit Group Audit report. Group->worker must be
  1:1; group->plan is many-to-many.
- Rate-type lock-in: once a plan's rate type is flat or calculated it can never change
  (in use or not). Individual rates cannot be disabled once in use, and mid-year
  individual-rate changes only hit NEW enrollment events. Additional Benefit plans allow
  flat/individual rates only, and no dependents or beneficiaries.
- Coverage-type-overlap reprocessing: two events reprocess each other only if their
  coverage types OVERLAP (and no Do Not Reprocess flag is set); same-date events with
  overlapping types consolidate into a hybrid event. Simultaneous events: earliest
  first, later ones held - and a held event is CANCELLED AND RECREATED, wiping any
  elections the employee already entered.
- OE structural differences vs life events: no Worker Selectable or Route to Benefits
  Partner checkboxes, no Days to Enroll section (days entered at initiation), routing by
  condition rules only, does NOT auto-close (manual/scheduled close; finalize only as
  "Finalize Events After Closing", never scheduled separately), and post-finalize changes
  go through Correct, not Change Elections. Termination auto-cancels an OE event only if
  the term date precedes the OE date.
- Multi-event conflict resolution is highest-wins: max level of change, guaranteed-issue
  amount, and the documented priority ladders for plan-change and dependent-change
  options.
- Finalize Open Benefit Events schedule cannot extend more than 5 runs past the end of
  the next calendar year - the End Date needs periodic extension (standing admin task).
- Deductions have NO proration - taken in full or not at all.
- Passive events fire ONCE per worker unless Is Re-Runnable is set (needed for multiple
  children aging out); "No Changes Allowed" coverage rules make the event open and
  instantly close, applying defaults.
- Dependents/beneficiaries with active enrollments cannot be inactivated or deleted;
  court-ordered coverage blocks employee-side removal; the tobacco question never
  re-asks after first answer; Quebec spousal beneficiaries are automatically irrevocable.
- EOI: administrators can only accept/deny the elected amount per the carrier - no
  arbitrary approved amounts. Default-coverage-pending-EOI and takes-effect-date are
  config, not free choices at runtime.
- Discontinued plans retire via a NEW plan year definition, never deletion (retro
  enrollments). Enrollment instruction text is NOT effective-dated - edits go live
  immediately. FSA is prefunded use-it-or-lose-it; HSA+FSA generally exclusive except
  limited-purpose FSA; cross-plan maximum rounding goes UP to the next $1,000 and
  violations are hard errors.

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory):

- **Benefits Administration** - 47 operations. Transactions: Change Benefits (+ Bulk
  Import Change Benefits), Change Benefit Jobs, Change Beneficiary, Add/Edit Dependent,
  Enroll in Retirement Savings Plans, Grant COBRA Eligibility, Manage Medicare
  Information, Put Evidence of Insurability. Setup: Put Benefit Plan (+ Expanded
  Details), Put Benefit Plan Year Definition, Put Benefit Provider, Put Health Care
  Rate / Insurance Rate / Benefit Individual Rate / Benefit Annual Rate + Credit,
  Put Custom Validation Rule. Reads: Get Benefit Plans (+ Expanded Details), Get Benefit
  Plan Year Definitions, Get Health Care / Insurance / Individual / Annual Rates, Get
  Benefits Billing Events. ACA: Get ACA 1095-C Forms Data, Import 1095-C Form Recipients
  Data, Put Affordable Care Act Worker Hours And Wages. Deprecated: Put Dependent
  (use Add/Edit Dependent), Get/Put Employee Defined Contribution Elections.
- **Benefits Partner Program Integrations** - 4 operations (wallet cards, benefit
  programs); NOT name-probe discoverable - confirm in-tenant before designing on it.

Other read/write paths:

- Delivered connectors: CCB - Cloud Connect for Benefits, the carrier-feed family
  (named per wd-integration-dev core-connector.md / integration-naming.md); a delivered
  benefits-vendor enrollment inbound Studio donor also exists in the wd-integration-dev
  studio.md donor table. Default to CCB for carrier eligibility files before proposing
  custom; custom Studio/O4I only for non-standard vendor formats.
- EIB shapes named in the manuals: healthcare calculated-rate loads and BAR (benefit
  annualized rate) population; plus Bulk Import Change Benefits for enrollment
  conversion.
- Payroll handoff: employer contributions pass to Workday Payroll or Payroll Interface;
  the employer-match-from-employee-deduction calc is NOT available for Payroll
  Interface. Healthcare classification feeds "most integration files" - treat as
  required for US plans even though the tenant does not enforce it.
- BP hooks: Change Benefits for Life Event rides nearly every staffing BP; the
  "If there is an effect on employee benefits?" condition is Workday-owned and mandatory
  on HR BPs. The Step Delay on Change Benefit Elections for Compensation Change hides
  comp changes from Benefits History until announced.
- Reporting: Benefit Events Status Report, Benefits Eligibility by Benefit Group,
  Enrollment Count, Benefits Census, Workers with Enrollment Events On Hold, Benefit
  Group Audit - the audit/report layer most benefits dashboards should read from.

## 3. Solution patterns + donors

- **Benefits attestation / decision-support app** - Extend config-BO-driven form suite
  collecting attestations or plan-selection inputs outside the enrollment UI, writing
  elections via Change Benefits on approval. Donor: vaccineManagement (config-BO-driven
  form suite, 3 BPs, on-behalf-of, attachments).
- **Mass benefit-event sweep** - Model BP / async fan-out to open events or to-dos for a
  population (e.g. dependent verification drives). Donor: crisisCheckin (Model BP mass
  launch via async fan-out).
- **Dependent-document / EOI evidence intake** - upload + document scan + typed results
  feeding a verification queue. Donor: documentIntelligenceWithTheAIGateway (upload ->
  orchestration scans doc -> typed results).
- **Carrier eligibility feed** - CCB first; Studio inbound for enrollment files from
  vendors that cannot consume/emit the connector formats (donor: the benefits-vendor
  enrollments Studio inbound in wd-integration-dev studio.md). Route via
  wd-integration-dev.
- **Rate refresh at plan year** - EIB loads of Put Health Care Rate / Put Benefit
  Annual Rate during OE prep; pair with a diff report so brokers' rate sheets are
  validated before load.
- **Benefits status dashboard** - read-only Extend page over the delivered status
  reports/RaaS (events on hold, not-started OE, EOI pending) rather than re-deriving
  event state from raw objects.

## 4. Design gotchas

- Never write elections outside an enrollment event context - Change Benefits IS the
  event; direct Puts of rates/plans do not touch worker elections. Enrollment state
  lives in events, and reprocessing rules decide whose write wins.
- Any app that opens benefit events must plan for the hold-and-recreate behavior: an
  employee mid-election on an event your automation supersedes loses their work. Check
  Workers with Enrollment Events On Hold before mass-initiating.
- Timing: OE and Finalize Open Benefit Events are batch/overnight processes - do not
  design real-time flows that assume an event finalizes on submit.
- The Do Not Reprocess flags are per-event-type config, not per-transaction - an
  integration relying on "my event will not be disturbed" must verify the event type's
  flags AND coverage-type overlap with everything else in flight.
- Benefits data is HIPAA-adjacent: dependent SSNs, Medicare, court orders. Segment
  Extend app domains tightly and keep carrier files out of general-purpose buckets
  (wd-deployment owns the security model design).
- ACA surfaces (1095-C, 4980H) have dedicated ops and eligibility-rule types - do not
  improvise ACA logic in an app; feed the delivered framework.
- The Benefits Partner Program Integrations service is not publicly probe-discoverable -
  anything designed on wallet cards needs an in-tenant WWS report check first (see
  wd-integration-dev wws-catalog.md).
- No proration on deductions means mid-period coverage math belongs in payroll design,
  not in a benefits app - set expectations in discovery.
