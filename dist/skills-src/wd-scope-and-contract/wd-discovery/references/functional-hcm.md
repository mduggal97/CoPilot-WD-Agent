# Functional literacy - HCM Core, Security, Time & Absence

Assumes the shared platform primitives in [workday-functional-skus.md](workday-functional-skus.md)
(FDM, security, BP framework, eligibility rules, calc engine). Source: Workday Education manuals
(HCM Core, HCM Core Supplemental, Security, Time Tracking, Absence for Administrators).

---

## HCM Core - the people-and-organization system of record
Foundation that structures the workforce into management hierarchies, defines how jobs are filled, and runs
staffing transactions. Everything else in HCM sits on it.

**Process areas:** organization design & reorganizations; staffing (hire, position/job management); job catalog
administration; the compensation framework (shared with Compensation); staffing BP execution (Hire, Change Job,
Terminate); reporting; search/navigation.

**Key configuration objects**
- **Staffing models** - **Position Management** (control: hire only into an open, approved position) vs.
  **Job Management** (flexibility: hire freely against org-level restrictions, no position object). Can be blended
  per branch (tight for exec roles, flexible for high-volume). **Model locks once positions/restrictions exist** -
  an effectively irreversible early design decision.
- **Hiring restrictions** (job family/profile, location, worker type, time type) enforced at staffing.
- **Job Profile** (min 3 fields: name, job code, effective date) - every worker must have one; **Job Family /
  Family Group**; **Management Level** (routing/eligibility tier).
- **Compensation framework**: packages -> grades (+ grade profiles for localization) -> plans -> eligibility (see
  [functional-hcm-talent-rewards.md](functional-hcm-talent-rewards.md)).
- **Organization types & hierarchies**, **Reorganization Events** (grouped structural change, one effective date).

**Core terminology**
- Supervisory Organization - management hierarchy holding jobs/positions; the HCM backbone.
- Position Management / Job Management - the two staffing models (control vs. flexibility).
- Hiring Restriction - allowed staffing parameters enforced at hire.
- Job Profile / Job Family / Management Level - generic job definition / grouping / hierarchical tier.
- Reorganization Event - grouped org change with a common effective date.
- Organization Assignments - default/allowed orgs inherited at hire/transfer.
- Matrix Organization - dotted-line manager relationship across supervisory orgs (maps to clinical service lines / academic dotted-lines).
- Correct / Rescind / Cancel - modify in-flight / undo completed / stop in-progress.

**FDM & cross-module ties:** organizations ARE the FDM backbone (Company/Cost Center/Location/Pay Group tie HCM
into Financials & Payroll). Job profiles link to comp grades; supervisory orgs drive security and BP routing everywhere.

**Integration & reporting touchpoints:** Report Writer is the reportable format (needs "Custom Report Creation"
domain). Staffing BPs (Hire/Termination) are the classic integration triggers (provisioning, background check).
EIB/Core Connector/Studio attach to worker/org/job/comp objects. Search prefixes `org:` `bp:` `event:` speed admin nav.

**Consultant gotchas:** (1) staffing model is effectively irreversible once used - decide early. (2) Hierarchies
can't hold transactions - rollup/security only. (3) A worker must have a job profile; maintain job-family
membership or comp packages won't default at hire. (4) Proxy access (non-prod only) supports only UNCONSTRAINED
security groups, never integrations/scheduled jobs.

**HC/Higher-Ed:** Matrix orgs -> clinical service-line / academic dotted-line reporting. AMU/GOV demo tenants.

---

## HCM Core Supplemental - the advanced-configuration layer
Deep BP design, custom validations, template-driven staffing events (Hire/Termination/Change Job), advanced/
custom security groups, custom reporting.

**Key constructs & must-knows**
- **BP definition approaches** (Default / Org-specific / Rule-based) and **~23 step types** - see hub.
- **Validations**: Default Warning (orange, bypassable) vs. Default Critical (red, blocking) vs. Configurable
  (custom text + severity), via Maintain Custom Validation / Configure Optional Fields; attach to Initiation/Review
  steps only. "Enforce Required in Web Services" separately controls API-side field enforcement.
- **BP Templates** (Onboarding, Change Job, Termination) - section groups + task-level security; require BOTH the
  BP security policy AND the domain security policy (a common access-troubleshooting gap).
- **Advanced security group types**: Intersection (member of ALL - AND), Aggregation (ANY - OR), Segment-Based
  (restricts which VALUES are visible, e.g. pay components), Rule-Based (baseline + condition rules, no activation
  needed to change membership), Conditional Role-Based, Service Center-Based.
- **Change Job** via Guided Editor (single screen); **Event Categories & Reasons** (tenanted reasons mapped to
  delivered change types; feed turnover/mobility analytics). **Notice Period** auto-calculates proposed termination
  date by country. **Job Overlap** - two workers in one position temporarily (position mgmt only).

**Gotchas:** (1) denial of any approval step denies the whole BP. (2) Rule-based defs allow one condition rule
(but unlimited nested conditions). (3) Intersection (AND) vs. Aggregation (OR) is a frequent design mistake -
rule-based groups often replace intersection with better performance. (4) Proposed data isn't committed until the
Completion step - matters for integration timing.

**HC/Higher-Ed:** Job Overlap suits clinical training/handoff and hard-to-backfill academic/research roles;
country notice periods matter for multi-entity systems.

---

## Security for Administrators - the authorization framework
The tenant-wide model controlling what every user AND integration can view/do. Core primitives (domains, policies,
group types, ISU/ISSG, union-of-permissions, Activate Pending) are in the hub - this manual is the deep dive.

**Must-knows beyond the hub**
- **Get/Put** (integration) is parallel to **View/Modify** (interactive); Put implies Get, Modify implies View.
- To LAUNCH an integration a business user needs **Modify on the Integration: Integration Event domain**.
- **Inbound EIBs assess the launching user's security, not an ISU** - plan access accordingly.
- **RaaS/report security**: shared custom reports run under each viewer's constraints; a user needs access to BOTH
  the data source AND its data-source filters. Notifications can carry report fields but enforce recipient security
  ("[not available]" if they lack access).
- **Segment-based ISSGs** restrict integrations to specific systems; use unconstrained/user-based (not role-based)
  groups inside segments to avoid context gaps.
- Troubleshooting report: **View Security for Securable Item** ("secura").

**Gotchas:** union-of-permissions means one stray unconstrained group over-provisions; audit for it. Role-based
membership auto-updates on job change (access follows the role); user-based does not (follows the person) - choose
deliberately. Right access needs the right group TYPE, not just membership.

**HC/Higher-Ed:** constrained role-based + org-membership groups map to department/campus/facility/service-line
scoping; segment-based supports need-to-know on research grants and clinical pay components.

---

## Time Tracking - capture, calculate, and route payable time
Captures reported time (elapsed "Hours Only" or clock-based "In/Out"), applies calculations (OT/premiums/shift
differentials), validates, and routes payable time to Payroll and Absence.

**Key constructs**
- **Time Entry Code** (reportable time type) + **Calculation Tags** (Regular/OT/Comp categories -> payroll mapping).
- **Time Entry Template** (one per worker - calendar behavior, rounding, geofence, edit thresholds).
- **Time Code Groups / Time Calculation Groups** (eligibility-bundled - a worker MAY be in several).
- **Period Schedules**, **Work Schedule Calendars** (day breaker, patterns, flextime bands), **Holiday Calendars**
  (Workday maintains for 86 countries).
- **12 Calculation Templates** (Standard OT, Consecutive Day, Shift Differential, Min Daily, Min Weekly, Min Rest,
  Schedule Deviation, Override Rate, Flextime, Time Block Conditional, Time Block Create, Holiday Time Block Create).
- **Meal Break Rule Sets / Attestations**, **Time Accumulators** (threshold tracking: static/rolling/period).

**Core terminology:** Time Block (calendar unit of reported/calculated time) - Time Clock Event (TCE) (raw check-in/out
matched into blocks) - Calculation Tag (labels time for payroll) - Day Breaker (work-day boundary, default midnight)
- Time Shift (consecutive blocks separated by meal/break) - Rounding Breakpoint - Geofence (lat/long + radius,
>=100m) - Attestation (worker confirms meal/break compliance at checkout) - Time Accumulator (hours vs. a regulatory threshold).

**FDM/ties:** Worktags (Cost Center/Region/Program) flow to Payroll and OVERRIDE default costing allocations;
Calculation Tags map payable time into Payroll earnings; feeds Absence. Reported Time Batch Events import
third-party time (TCEs load <=150 every 2-5 min).

**Gotchas:** (1) a worker should qualify for exactly ONE template/period-schedule/work-calendar but MAY be in
multiple code/calc groups. (2) Payroll only picks up SUBMITTED blocks after the Enter Time BP completes - clocking
alone doesn't pay. (3) Calculation **priority ordering** ("A" before "C") is load-bearing - calcs cascade;
mis-ordering silently produces wrong OT/premiums. (4) Time Block Conditional TAGS existing time; Time Block Create
GENERATES new time (e.g. holiday hours). (5) a validation rule must reference only one primary business object.

**HC/Higher-Ed:** shift differentials, min-rest, consecutive-day, meal/break attestation, geofenced clock-in are
core to hospital/24-7 and shift-based higher-ed (facilities, dining, student workers).

---

## Absence Management - time away from work
Two distinct functions: **Time Off** (short, balance-accruing) and **Leave of Absence** (extended, workflow-gated,
worker retains employee status/benefits). Choosing between them is the foundational design fork - different objects,
tracking, and whether a return workflow exists.

**Key constructs**
- **Time Off Plan** (master container: eligibility, accrual, balance period, upper/lower limits, carryover);
  **Time Off Type / Time Off**; **Accrual** (frequency/amount/timing).
- **Leave Family / Leave Type / Leave of Absence Rules / Balance Calendar**.
- **Absence Table** (multi-plan tiered prioritization -> cascading balance usage, e.g. STD -> LTD).
- **Advanced Lookup Tables** (effective-dated calc parameters); **Leave Effects** flags (Payroll, Benefit, Stock
  Vesting, Continuous Service, Scheduling) that gate downstream behavior.

**Core terminology:** Accrual - Balance Period (calendar/anniversary) - Upper/Lower Limit - Carryover -
Coordinated/Cascading Leaves - Hard vs. Soft Error (block vs. warn) - Leave Effects - Absence Case (statutory
reintegration tracking) - Termination Adjustment / Balance Transfer.

**FDM/ties:** calc fields evaluate Worker/Position/Leave-Request/Leave-Type; Leave Effects gate Payroll/Benefits/
Vesting/Scheduling; Job Change BP auto-adjusts accruals. Mass load via EIB; approved time off syncs to Google/
Outlook calendars.

**Gotchas:** (1) Time Off vs. Leave is the design fork. (2) Balance stored monthly with a 13-month lookback;
dynamic calcs build forward - matters for retro accrual accuracy. (3) Overrides apply BEFORE adjustments during
accrual (sequence gotcha). (4) Intermittent time off must pass validation for BOTH the time off and the related LOA.

**HC/Higher-Ed:** FMLA/STD/LTD cascade, intermittent leave, and statutory absence cases are heavy in 24/7 healthcare
workforces.
