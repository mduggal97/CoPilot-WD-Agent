# Time Tracking + Absence - solution playbook

Two coupled domains: Time Tracking (time entry, clocks, calculations) and Absence
Management (time off plans, accruals, leaves of absence). Config facts below are
doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant. Web-service
names are from the in-tenant WWS master inventory.

## 1. Configuration spine

### Setup order - Time Tracking

1. Work Schedule Calendars (day breaker default midnight; week starts Sunday; shifts
   under 24h; max two unpaid meal periods).
2. Period Schedules (open/lock/unlock/close dates gate entry; bulk-loadable).
3. Time Entry Codes (hours-only vs in/out; unit must be Workday-delivered "Hours").
4. Time Calculation Tags -> Time Calculations (12 types) -> Time Calculation Groups
   with priorities.
5. Time Code Groups (codes + eligibility) and Time Entry Templates (the orchestrating
   object: calendar UI, default code, totals, worktags, attestations, validations).
6. Eligibility rules on templates, code groups, calc groups, period schedules.

### Setup order - Absence

1. Calculations -> balance periods -> accruals -> Time Off Plans (attaching accruals)
   -> Time Offs -> eligibility/validations -> absence tables (optional cascades).
2. Leave side: Leave Families -> Leave Types (with/without balance) -> entitlements ->
   eligibility (Worker/Position objects only) -> validations (hard vs soft) ->
   coordinated/cascading leaves -> intermittent time offs linked to leave types.

### Key BPs

Enter Time (iterative - NO cancel, rescind, or correct; Enter -> Submit -> Approve),
Request Time Off / Correct Time Off, Request Absence, Request Leave of Absence /
Request Return from Leave of Absence (auto worker inactivation/reactivation), Assign
Work Schedule Calendar, Reported Time Batch Event (launched by importing reported time
blocks - needs a BP condition for external load to auto-process).

### Hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

- **Time code group eligibility evaluates in a fixed order**: Country/Country Region,
  then Pay Rate Type, then the Worker Eligibility rule - a rule that "should" match
  fails if an earlier gate does not.
- **One template per worker is a SOFT constraint**: Workday allows multiple template
  eligibility and silently keeps the ORIGINAL. Police with the delivered audits (Audit -
  Workers with Multiple Time Entry Templates / Time Period Schedules / Work Schedule
  Calendars).
- **Calculation priority is an alphanumeric STRING sort** (10-char max): "1, 13, 2, 20"
  without zero-padding; equal priorities fire in RANDOM order. Pad or use 100-step
  increments.
- Period schedules open/lock/unlock/close in PACIFIC TIME regardless of tenant or
  worker time zone; time itself saves in the worker's own time zone.
- In/out entry codes are MANDATORY for the Workday web clock and any third-party clock
  feed; max time block 24h; Increment for Hours Entry is strictly enforced (off-increment
  entries are rejected).
- Costing worktags entered in Time Tracking OVERRIDE whatever Payroll would assign.
- **Absence unit-of-time rigidity**: all time offs, accruals, limits, and calc values in
  one plan share one unit (hours OR days) and Workday NEVER converts between them. Same
  rule for leave entitlements.
- **Plan structure locks**: Track Balance, Period Schedule, and Unit of Time are
  immutable after creation; worker-based vs position-based cannot flip once data
  exists; time offs/accruals cannot be removed once requested against.
- **Override before adjustment**: overrides apply first, then adjustments; only ONE
  override per accrual per processing period; once a balance is overridden, Workday
  never recalculates that date or earlier - even for retroactive entries (pair with
  the Time Off Date Before Maximum Override Balance Date validation).
- Absence tables: no intermittent time offs, no position-based plans, no effective
  dates, no adjustments/overrides, no start/end times, no unit-of-time changes.
- 12-month effective-date limit on absence setup snapshots unless the removal checkbox
  is set; scheduled balance-store process: 91+ day intervals, one plan per schedule,
  never current/future periods.

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory):

- **Time Tracking** - 10 operations. Inbound: Import Time Clock Events (load, modify,
  delete raw clock punches; batch <= 150 per the manual) and Put Time Clock Events;
  Import Reported Time Blocks (launches Reported Time Batch Event BP) and Put Reported
  Time Blocks for Worker; Import Ad Hoc Schedules (third-party scheduling; needs the
  Process: Ad Hoc Schedule Processing domain). Outbound: Get Calculated Time Blocks
  (post-calculation time - the payroll-grade read). Also Assign Work Schedule, Get/Put
  Time Requests, Put Time Attendance Points.
- **Absence Management** - 17 operations. Entry: Enter Time Off, Adjust Time Off,
  Request Leave of Absence, Request Return from Leave of Absence, Request Edit Leave of
  Absence, plus high-volume Import Time Off Request Event Batch / Import Request Leave
  of Absence Events / Import Request Return from Leave of Absence Events (attachments
  supported). Balances/config: Get Time Off Plan Balances, Put/Get Absence Inputs
  (mass accrual overrides, auto Batch IDs), Put Override Balance, Put Carryover
  Override, Get/Put Accrual Expiration Override.
- **Scheduling** - 48 operations (Workday Scheduling module): Get/Import Schedule
  Shifts, Import Labor Demand, Import Worker Availability / Scheduling Preferences,
  Put Operating Hours, Put Scheduling Organizations.
- Neighbor services hold key config objects: Human Resources carries Get/Put Work
  Schedule Calendar (+ Groups) and Put Holiday Calendar; Payroll and Payroll Interface
  carry Get Period Schedules / Put Period Schedule.

REST / WQL / RaaS:

- REST: absenceManagement v5 (balances, workers - the self-service-shaped read/request
  surface). There is NO dedicated Time Tracking REST service in the tenant REST catalog
  (wd-extend-dev rest-api-catalog.md) - time writes go SOAP/background import.
- WQL/report data sources: All Time Blocks and All Time Clock Events are indexed;
  All Time Review Events drives the MOM mass-advance framework. Absence side: Time
  Off - All Statuses for Active and Terminated Employees (indexed), Calculated Balances
  for Organization (by Worker), Absence Occurrences for Workers (Indexed). Worker
  population reads allWorkers / allActiveWorkers / workersForHCMReporting are
  build-verified in the suite (wd-extend-dev wql.md). RaaS over these sources is the
  standard outbound for time/absence extracts.

Delivered connectors, EIB shapes, hooks:

- Third-party clock systems integrate via Import Time Clock Events (raw punches ->
  Workday matches to in/out blocks; unmatched/invalid event reports delivered).
  Third-party calendar integration (Google/Outlook) is ONE-WAY Workday-to-external,
  minimum every 2 hours.
- Absence-to-payroll: time off flows to Workday Payroll via calc tags; to Payroll
  Interface per the "Picked Up by Payroll Interface one Period in Arrears" checkbox.
- EIB shapes (wd-integration-dev eib.md): Enter Time Off / Adjust Time Off mass loads;
  Request Leave of Absence / Return spreadsheet imports; Put Period Schedule; Put
  Advanced Lookup Table. Importing reported time launches the Reported Time Batch
  Event BP - update its security policy and add the external-load condition or every
  batch sits awaiting action.
- Automated service steps: Automated/Bulk Automated Accrual Adjustment (fires after
  Change Job / collective agreement changes), Automated Leave Processing, Adjust Time
  Off Balances, Automated Absence Case Creation.

## 3. Solution patterns + donors

- **Time clock / attendance inbound** - raw punches in, calculated blocks out. Studio
  donor: the INT045 time-entry inbound (third-party clock vendor) - present in the local
  Studio-to-O4I candidate inventory (inventory-cited, NOT build-verified; open the actual
  project in the raw Studio export before quoting it); modern build = O4I on the WWS import framework
  (submit background import -> poll -> harvest Get Import Process Messages; donor
  supplierInvoicesInbound in wd-extend-dev app-catalog-registry.md - same framework,
  swap in Import Time Clock Events). Respect the 150-event batch cap.
- **Badge-scan / kiosk attendance app** - Extend page or external device feeding clock
  events. Donors: the badge-scanning reference app in the Extend workspace _reference
  folder (external-API sync flow, the canonical async/egress donor per wd-extend-dev
  external-apis-and-genai.md) and jlv-worker-badges / workerBadges (badge + attachment
  CRUD choreography).
- **Manager time/absence dashboard** - WQL over the indexed time-block/time-off sources
  + absenceManagement v5 balances; delivered Review Time and the Time and Scheduling
  Hub first - build only when requirements exceed them.
- **Mass time-off / leave load** - Enter Time Off EIB for time off; Import Request
  Leave of Absence Events for high-volume leave with attachments. Both follow the
  native BPs, so approvals/validations still apply.
- **Accrual/override automation** - boomerang shape (read balances -> compute -> Put
  Absence Input / Put Override Balance / Put Carryover Override); donor
  updateServiceDateBoomerang (wd-extend-dev app-catalog-registry.md) for the
  RaaS -> loop -> SOAP-write skeleton. Mind override-before-adjustment precedence.
- **Attestation campaigns** - per-entry attestation is NATIVE (Time Attestation Rules,
  meal break rule sets) - configure before building. A standalone mass-attestation app
  is the crisisCheckin Model-BP fan-out donor shape.
- **Leave case management** - Extend app wrapping Request Leave of Absence + Return
  events with Absence Cases reads; cascade logic (Next Leave Type) is native - do not
  rebuild it in app code.

## 4. Design gotchas

- Enter Time has no rescind/correct - "fixing" time means re-entering and resubmitting
  the week (or Adjust Calculated Time, which STOPS all future calculated time for that
  week and cannot be done by the worker). Apps promising time correction must model
  this, not a rescind verb.
- Time saves in the worker's own time zone even when a manager elsewhere enters it -
  cross-timezone reporting and clock reconciliation must normalize accordingly.
- Load raw punches (Import Time Clock Events), not pre-built blocks, when a clock
  vendor is the source - Workday owns matching, calculations, and overtime. Import
  Reported Time Blocks is for already-blocked time and drags the Reported Time Batch
  Event BP with it.
- Extract CALCULATED time (Get Calculated Time Blocks / All Time Blocks source) for
  payroll-grade outbounds - reported time lacks OT splits, tags, and rounding.
- Schedule integrations around the period lifecycle: locked periods block non-exempt
  entry, closed periods block everyone, all gates trip in Pacific Time. A nightly load
  landing after a lock fails silently for affected workers.
- Never write a balance when an input will do (Put Absence Input over Put Override
  Balance) - an override freezes recalculation for that date and earlier, permanently.
- Time off vs leave balances evaluate INDEPENDENTLY - one check never covers both;
  coordinated leave entitlements reduce concurrently, never combine.
- Mass-operation ceilings: Mass Enter Time 100 workers; Mass Advance 5,000 events
  (degrades past 500); MOM framework 50,000; Run Time Calculations for a Date Range
  3-month max and it recalculates whole weeks even in locked/closed periods.
- Balance history: Workday stores a monthly 13-months-back snapshot; post-termination
  absence purge windows are country-specific (USA 3y, France 5y, UK 6y, Canada 7y) -
  retention answers route to wd-post-go-live.
- Functional literacy lives in wd-discovery functional-hcm.md; the end-user security
  model in wd-deployment configurable-security-admin.md.
