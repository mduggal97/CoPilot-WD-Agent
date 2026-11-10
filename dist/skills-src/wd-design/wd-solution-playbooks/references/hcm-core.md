# HCM core: orgs, staffing models, jobs/positions, hire - solution playbook

The foundation domain every other playbook stands on: supervisory organizations,
staffing models, the job catalog, positions, and the hire-to-terminate staffing
event chain (plus the BP and security frameworks those events ride on). Config facts
below are doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant.
Web-service names are from the in-tenant WWS master inventory.

## 1. Configuration spine

### Setup order

1. Organization types/subtypes (Maintain Organization Types/Subtypes), then LOCATIONS -
   locations must exist before supervisory orgs (Primary Location is required).
2. Supervisory organizations + hierarchies; other org types (Company, Cost Center,
   Region, Pay Group, Custom) + organization assignments (Allowed = multi, Default =
   single; subordinates inherit unless overridden).
3. Staffing model per supervisory org (Position Management or Job Management) - assigned
   before any staffing activity.
4. Job catalog: Job Family Groups > Job Families > Job Profiles (required on every
   worker) > Job Classifications > Management Levels. Only required job-profile fields:
   name, job code, effective date.
5. Compensation framework (elements -> eligibility rules -> grades -> plans ->
   packages) - see the compensation playbook; Hire carries Propose Compensation Hire.
6. Security: functional areas -> domains/BP types (Workday-delivered, immutable) ->
   security groups -> policies -> Activate Pending Security Policy Changes.
7. BP definitions per staffing event; org-specific definitions inherit up the
   supervisory hierarchy (org-specific -> superior -> default).
8. Prepare for hire: Create Position (Position Management) or hiring restrictions on
   the org (Job Management); job requisitions required if Workday Recruiting is live.

### Key BPs

Hire, Contract Contingent Worker, Change Job (template-driven; promotions, transfers,
location changes), Terminate Employee / Submit Resignation, Create Position, Edit
Position Restrictions, Change Organization Assignments for Worker, Assign Roles (runs
as subprocess of Change Job / Divide Organization / Request Leave of Absence),
Add Additional Job, Start International Assignment, End Additional Job.

### Hard limits and landmines (doc-sourced - Workday Education manuals, 2026-08-25; verify in-tenant)

- **Staffing model is one-way locked**: once a position exists (Position Management) or
  hiring restrictions are set (Job Management), Edit Staffing Model is unavailable for
  that org. Hybrid models across the hierarchy are fine; changing one later is not.
  Move Workers also requires both orgs to share the same staffing model.
- **BP subprocesses do NOT inherit security**: every subprocess BP security policy is
  configured individually - a Hire definition working end-to-end still fails if Propose
  Compensation Hire's own policy lacks the group. One BP type = ONE security policy
  shared by all its definitions.
- BP events run against the definition effective AT INITIATION; later definition changes
  never retro-apply. Step order is an alphanumeric STRING sort (lowercase before same
  letter uppercase; "10" sorts before "2").
- Hiring restrictions are enforced during Hire / Contract Contingent Worker / Change Job
  but NOT during Edit Position; single-value location restriction cannot be overridden
  at hire.
- Corrections (Correct) skip approval, do not re-validate hiring restrictions, and
  cannot move outside the previous/next event dates; correcting the supervisory org on a
  Hire can orphan role-based-group My Tasks items (Mass Operation Management cleanup).
- Base currency locks after a company's first transaction; org inactivation requires
  removing all positions/workers first.
- Termination status flips at 12:00:01 AM the day AFTER the termination date in the
  worker's OWN time zone - downstream deprovisioning that keys on "terminated today"
  fires a day late and staggers across time zones.
- Job overlap: org assignments do NOT sync across overlap positions; Manager-role
  routing goes to BOTH principal and overlap workers; headcount reports count one.
- Rescinding a Change Job does NOT rescind its Assign Roles subprocess - role
  assignments persist.
- "Enforce Required in Web Services" (tenant validation setting) controls whether
  red-asterisk required fields apply to web-service submissions - a load that works in
  one tenant can reject in another on this checkbox alone.

## 2. Technical surface

WWS SOAP services (from the in-tenant WWS master inventory):

- **Staffing** - 154 operations, the event surface. Transactions: Hire Employee,
  Contract Contingent Worker, Change Job, Terminate Employee, End Contingent Worker
  Contract, Create Position, Edit Position, Edit Position Restrictions, Set/Edit Hiring
  Restrictions, Add Additional Job, End Additional Job, Switch Primary Job, Move Workers
  By Organization, Change Organization Assignments, Assign Roles, Change Personal
  Information, Edit Service Dates. High-volume background twins exist for most (Import
  Hire Employee, Import Change Job, Import Terminate Employee, Import Create Position,
  ...) - these are the EIB/import-framework path. Reads: Get Workers, Get Positions,
  Get Organizations, Get Job Families/Job Family Groups. Deprecated in the inventory:
  Transfer Employee, Promote Employee (use Change Job), Assign Organization Roles (use
  Assign Roles).
- **Human Resources** - 336 operations, the master-data surface. Get Workers (the
  god-read: response groups gate payload size - see wd-integration-dev wws-catalog.md),
  Get/Add Update/Inactivate/Reactivate Organization, Get Locations / Put Location,
  Get Job Profiles / Submit Job Profile (Put Job Profile is DEPRECATED), Put Job
  Family (+ Group), Maintain Contact Information, Change Home/Work Contact Information,
  Change Person Photo / Put Worker Photo, Add Workday Account, Put Assign User-Based
  Security Group, Get/Put Work Schedule Calendar (+ Groups), Put Holiday Calendar.
- **Integrations** - 37 operations, the meta surface apps lean on: Launch Integration /
  Launch EIB, Approve/Cancel/Rescind/Deny Business Process, Get Event Detail, Get
  Integration Events, Put Integration System User, Get References.

REST / WQL / RaaS:

- REST: staffing v7 (144 ops - jobChanges, jobFamilies, jobProfiles, jobs,
  organizationAssignmentChanges, supervisoryOrganizations, workers), common v1 (40 ops -
  workers, organizations, supervisoryOrganizations, businessTitleChanges),
  businessProcess v1 (events, eventSteps, types). Full map: wd-extend-dev
  rest-api-catalog.md.
- WQL: allWorkers, allActiveWorkers, and workersForHCMReporting (dataSourceFilter =
  allActiveWorkers) are build-verified in the suite - shapes and nested-projection
  examples in wd-extend-dev wql.md. workersForHCMReporting is the indexed choice for
  volume reads.
- RaaS custom reports remain the outbound workhorse for worker extracts (~2083-char URL
  guard - wd-extend-dev orchestration.md).

Delivered connectors and hooks:

- **Core Connector: Worker (CCW)** full-file/changes worker demographic outbound and
  **PECI** (effective-change successor: captures ALL effective-dated events in sequence,
  one instance per country for country-specific sections). Operating rule from
  wd-integration-dev integration-build.md: run PECI at most once daily; avoid CCW
  full-file runs; schedule CCW end-of-day. Check these BEFORE designing a custom
  worker outbound.
- BP hooks: Integration step (separate thread), Service steps (Create Workday Account,
  Document Delivery), and Extend BP-triggered orchestrations on any staffing event
  (useForOrchestrate - wd-extend-dev orchestration.md); Model BPs give custom objects
  their own routable events (wd-extend-dev model-bp.md).

## 3. Solution patterns + donors

- **Custom work-event app with its own BP** - Extend BO + custom business process +
  approval routing. Donor: createAWorkEvent (custom .businessprocess, GraphQL mutations,
  wizard + hub); production-shaped sibling: workFromAlmostAnywhere (App-Attribute-driven
  validation, home cards, calendar).
- **Staffing-event chain from an app/orchestration** - sequence the SOAP events in O4I.
  Donor: addAdditionalJob catalog app (Create_Position -> Add_Additional_Job SOAP
  chain). Order matters in Position Management: the position must exist and be open
  before the hire/add event.
- **Boomerang worker-data sweep** - RaaS/WQL read -> loop -> SOAP update. Donors:
  updateServiceDateBoomerang (Update_* via /soap/Staffing, dual success/error logs),
  updateWorkdayAccounts (account usernames). All in wd-extend-dev
  app-catalog-registry.md.
- **Mass launch to a population** - Model BP fan-out. Donor: crisisCheckin
  (AsyncProcessListOfWorkersToLaunchModelBP self-launch loop) - the shape for
  attestations, surveys, compliance campaigns.
- **REST micro-writes** - single-field changes need no SOAP: changeBusinessTitle donor
  (POST common/v1 businessTitleChanges). Check rest-api-catalog.md before reaching for
  a SOAP op.
- **Account lifecycle on staffing events** - BP-triggered flow on Hire/Termination.
  Donor: disableWorkdayAccount (SOAP Get/Update_Workday_Account on BP trigger).
- **Outbound demographics** - delivered CCW/PECI first; custom shapes: O4I donor
  employeeDemographicOutbound (RaaS -> CsvFormat, sequenced filename) or the
  INT155-pattern person-hub Studio outbound (wd-integration-dev studio.md registry).
- **High-volume inbound loads** - background Import * ops via EIB (wd-integration-dev
  eib.md) or the O4I import framework (submit -> poll -> Get Import Process Messages;
  donor supplierInvoicesInbound - same framework, different payload).

## 4. Design gotchas

- Design hire/rehire automation around the BP, not around a naked Put - Hire Employee
  launches the full definition (subprocess security, onboarding, comp defaulting).
  An app that "creates workers" is really an app that initiates Hire events.
- Ask the staffing model FIRST in discovery. Position Management forces a
  create-position step into every hire/transfer flow and enables unfilled-position
  reporting; Job Management cannot report open positions at all. The model is
  effectively permanent (see landmines).
- Effective date != entry date: staffing events are effective-dated and can be
  retroactive or future-dated. Integrations keying on "what changed today" need PECI
  semantics (effective-change capture), not a nightly snapshot diff.
- Cancel works only In Progress; Rescind only after completion; Correct is
  administrative with no approvals. An app replaying or fixing events must pick the
  right verb - the Integrations-service ops (Cancel/Rescind Business Process) mirror
  these constraints.
- Get Workers without response-group discipline is the classic timeout: request only
  the groups you need, page the call, or use workersForHCMReporting via WQL instead.
- Security design for any HCM app rides the delivered framework: domains are immutable,
  constrained role-based groups derive from org role assignments, and policy changes
  need activation. Route the end-user security model to wd-deployment
  configurable-security-admin.md and security-role-design.md.
- Functional literacy (what a sup org IS, worker vs position vs job) lives in
  wd-discovery functional-hcm.md - this playbook assumes it.
