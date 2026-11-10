# Core Connector - configuration, change detection, and the DIS security exception

Core Connectors are Workday-built TEMPLATED integration systems: you create an integration
system from a delivered template and configure it entirely tenant-side - no code. Sourcing
below is doc-sourced from the "Creating and Securing Integrations" and "Security for
Administrators" course manuals (Jul 2026) unless labeled otherwise. Naming:
[integration-naming.md](integration-naming.md); builder gates:
[integration-build.md](integration-build.md); reviewer scorecard:
[integration-review.md](integration-review.md).

## When a Core Connector wins

Workday's selection priority puts connectors FIRST: 1) end-to-end vendor connector ->
2) Core/generic connector -> 3) Orchestrate -> 4) Connector + DT -> 5) Studio (doc-sourced).
If a delivered template covers the object and the field gap is small, take the connector -
it is simpler AND often cheaper at the API layer (the Flex Credits counting rule for
connectors vs Studio augmentation is owned by `wd-estimate/references/flex-credits.md`).
Walk away from the connector when field overrides pile up (limit below) or when the flow
needs orchestration the template cannot express.

## Configuration surface

- **Create Integration System** task -> pick the template. End-to-end (vendor-specific)
  vs Core/generic templates: Worker, Positions, Organization, Candidate Outbound, Job
  Profile, Organization Inbound, Accounting Journal Inbound. Search prefix `intsys:` finds
  existing systems. Research current templates via the **Integration Template Catalog**
  report and Workday Community.
- **All config hangs off Related Actions on the integration system:** Configure Integration
  Services / Attributes / Field Attributes / Field Overrides / Maps / Notifications /
  Sequence Generators / Transaction Log / Population Eligibility (DIS) / Test Transport.
- **Integration Services** = groups of attributes, maps, and transformations the template
  offers. Enable ONLY the services the design needs - enabling a service can ADD
  web-service calls (e.g. Job Profile Data on the Positions connector adds Get Positions +
  Get Job Profiles), which is runtime and, on a metered system, cost. Custom Integration
  Services supplement when delivered ones lack data.
- **Attributes** = tenanted values/behavior (address types, prior-value inclusion).
  **Field Attributes** = include/exclude fields, required, max length. **Maps** = value
  translation Workday -> external; ALWAYS set the Default Value for unmapped input so one
  stray code does not fail the run. Restrict attributes and maps by environment
  (integration-build.md).
- **Field Overrides** = point a template output slot at a report/calculated/custom field.
  Two steps: create a custom field-override service (Configure Integration Services), then
  map fields (Configure Integration Field Overrides). HARD GUIDANCE: **more than ~30 field
  overrides means the connector is the wrong tool** - and calc fields in overrides are a
  known performance risk (doc-sourced).
- **Output**: Workday XML (WIDs + Reference IDs) or Simple XML. Sequence generators build
  unique output filenames and OVERRIDE any static Output Filename attribute.
- **Launch parameters**: value types Determine Value at Runtime / Specify Value / Use
  System Default. The standard incremental window pattern: Current Moment (DateTime) plus
  "As of Entry DateTime of Last Completed Integration Event".

## Change detection - decide and DOCUMENT per integration

Three extract modes (doc-sourced): **Full-File** (everything as of the As Of moment),
**Full-Diff** (only new/changed since the last successful run), and **transaction-log**
change detection (only instances with subscribed log events; configure via Configure
Integration Transaction Log - subscribe by BP/transaction type, or all-except).

- KEY CONSTRAINT: the transaction log catches **DIRECT changes only**. Indirect changes -
  a job-classification edit that changes what workers report, a manager change reflected on
  subordinates - never hit the subscribed log and are silently missed. Those integrations
  need **Full-Diff** instead. Record the chosen mode and WHY in the IDD (house rule).
- Stack processing: Top of Stack (net start->end values) vs Effective Stack (every value,
  incl. same-day intermediate ones).
- Gotchas (doc-sourced): earliest usable date is 1970-01-01; MANUAL runs share the
  timestamp state with scheduled runs (an ad-hoc run can shrink the next scheduled window);
  some transactions are effective immediately (Personal Info) while others post next-day
  (Termination) - test window edges.
- Per-event audit outputs: Data Changes Audit (field-level; ABSENT on Full-File extract),
  Diagnostic Audit, XSD, Messages Audit.

## DIS and the security exception

DIS (Data Initialization Service) is the high-performance data-gathering alternative on
some templates (notably Core Connector: Worker): it reads **report fields** through the job
framework instead of making web-service calls. Population scoping moves to **Configure
Integration Population Eligibility** (a boolean Worker field; "Is True" = everyone) - and
the Define Eligibility FIELD OVERRIDE is IGNORED once DIS is on (doc-sourced).

**The security exception:** because DIS reads report fields, grants for field overrides are
**Report/Task View permissions on the owning domains - NOT Integration Get**. Get/Put may
still work at runtime, but **Test Security for Document Field Overrides gives WRONG answers
until the View grants are in place** (doc-sourced). Iterative build loop: baseline full
extract as an admin -> ISU/ISSG + Integration Event Modify -> View Security for Securable
Item on every override/eligibility field -> grant View -> activate -> run as the ISU ->
diff against the baseline -> if gaps, run Test Security for Document Field Overrides and
read the Diagnostic Audit File -> repeat. "Completed with Warnings" + DIS Exception:
Related Actions > Integration Event > Retrieve Technical Files and read the exception log.

## The connector family (orientation only)

Type abbreviations and naming: integration-naming.md. CCW (Worker), CCB (Benefits - carrier
feeds; depth in the "Core Connector: Benefits (CCB)" section below - a delivered
benefits-enrollment Studio inbound donor is registered in studio.md; PECI/payroll notes are
in integration-build.md), CCP/CCJP/CCJR/CCL/CCO per the naming
table. Payroll connectors: **PICOF** is the older certified Payroll Interface output format;
**PECI** its effective-change successor - outbound demographic/effective-change export, at
least one instance per country, paired with inbound EXPR (results) and pay-slip imports.
That one paragraph is the boundary - the full payroll-connector pattern (list-value mapping
checklist, pay groups, period schedules) stays in integration-build.md. Efficiency (house
rule, integration-build.md): run PECI at most once daily; avoid CCW full-file runs;
schedule CCW end-of-day.

## Core Connector: Benefits (CCB) - carrier feeds

CCB (Cloud Connect for Benefits) is the delivered outbound connector family for **benefits
carrier eligibility feeds** - the recurring extract Workday sends each provider (medical,
dental, vision, life, disability, FSA/HSA administrators, retirement/COBRA vendors) so the
carrier can maintain enrollment on its side. Pattern-level guidance below; **confirm the exact
template, services, and fields per carrier/tenant** - carrier layouts are not uniform. Owner
split: `wd-solution-playbooks/references/benefits.md` owns the benefits solution surface (BPs,
plan/event config, WWS ops); this section owns the CCB build mechanics only.

- **Use case (outbound, per provider):** one CCB integration system per carrier/provider (or
  per feed the carrier requires), scoped to that carrier's participating plans. Selection
  priority still holds (connector-family orientation above): **default to CCB before proposing
  custom Studio/O4I**; drop to custom only for vendors that cannot consume/emit connector-shaped
  output (benefits.md, doc-sourced). A delivered benefits-vendor **enrollment inbound Studio
  donor** for the reverse direction is registered in studio.md.
- **Template + services:** create the integration system from the delivered benefits/carrier
  template, then enable only the Integration Services the feed needs (same discipline as any
  connector - extra services add web-service calls, cost, and runtime). Scope which carrier +
  plans are in-feed via attributes and population/eligibility config; restrict attributes and
  maps by environment (integration-build.md).
- **Typical field groups (confirm per carrier):** worker/subscriber demographics + coverage
  begin/end; **enrollment lines** (plan, option, coverage tier); **coverage amounts / elected
  vs. approved** (life/disability); **dependents and beneficiaries** with relationship and
  their own coverage/effective dates; and **EOI status** (elected vs. carrier-approved amount -
  benefits.md: administrators can only reflect the carrier-accepted amount, never an arbitrary
  approved figure). Group-number/plan-code cross-references are the highest-value **Integration
  Maps** - always set a Default Value so one unmapped plan code does not fail the run
  (core-connector Maps rule above).
- **Delivered vs. custom mapping:** take delivered template output slots and Integration Maps
  first; add **Field Overrides** (report/calc/custom field into a template slot) only for the
  gap - and hold the line at the connector's override budget (**>~30 overrides = wrong tool**,
  and calc fields in overrides are a documented performance risk; both doc-sourced above).
  Carrier group numbers, division/location splits, and derived eligibility flags are the
  common override/custom-field candidates.
- **Carrier-specific formats (DT/XSLT augmentation):** when the carrier needs a layout CCB
  cannot emit (fixed-width, delimited, a mandated header/trailer, a proprietary record order),
  chain a **Connector with Document Transformation** and run XSLT against the CCB output rather
  than forcing the connector - the DT integration rides the parent for metering
  ([document-transformation.md](document-transformation.md); XTT/ETV annotations for
  fixed-width/delimited output live in xslt3.md). Flag any augmentation with its Flex-Credits
  impact in the IDD (design-review checklist below).
- **Run cadence (decide + document per feed):** most carriers take a **change-only** feed
  (Full-Diff or transaction-log per the change-detection section above) on a fixed schedule
  (often weekly), with a periodic or onboarding **full-file** to re-baseline the carrier.
  Confirm the carrier's expectation - some accept only full-file replacements, some only
  net changes - and record the mode and WHY in the IDD (house rule). Remember the
  transaction-log **indirect-change trap**: an eligibility-rule or dependent-relationship
  change that alters who is in-feed may never hit the subscribed log - use Full-Diff when
  indirect changes drive enrollment (doc-sourced, change-detection section).
- **Common gotchas (confirm per carrier/tenant):**
  - **Effective-dating:** coverage begin/end and EOI takes-effect are event/config-driven, not
    free runtime values (benefits.md); carrier feeds are sensitive to the As Of window and to
    events that post next-day (e.g. termination) vs. immediately (personal info) - test window
    edges (change-detection gotchas above).
  - **Eligibility snapshots:** a change-only feed sends what changed since the last run; the
    carrier's picture is only as good as the baseline. Re-baseline with a full-file after plan
    year changes, discontinued plans (retired via a NEW plan year definition, never deletion),
    or scope changes to participating groups.
  - **Negative / termination records:** confirm how the carrier wants drops - a terminate/
    coverage-end record vs. absence from the file. A change-only feed that simply omits a
    dropped worker will NOT terminate them at a carrier that expects an explicit term record.
  - **Test-file validation with the carrier:** always run a **Test Transport** and exchange a
    carrier-validated test file before go-live - carriers commonly reject on group-number,
    plan-code, or record-format mismatches that only their system surfaces. Treat carrier
    sign-off on the test file as a prerequisite gate.
  - **Sensitive data:** carrier feeds carry dependent SSNs, Medicare, court-ordered coverage -
    keep files off general-purpose buckets and segment tightly (benefits.md; wd-deployment owns
    the security model).

## Downstream formatting

When the vendor needs a layout the connector cannot emit, chain a **Connector with
Document Transformation** - the DT integration runs your XSLT against the connector output
([document-transformation.md](document-transformation.md); DT rides the parent integration
for metering). XSLT starter templates exist for Core Connector Worker and PICOF output
reshaping - [xslt3.md](xslt3.md) starter-templates bullet. XTT/ETV annotations for
fixed-width/delimited output live there too.

## Security, scheduling, ISU/ISSG

Standard chain (one ISU + one ISSG per integration system, domain grants, activation):
wd-deployment tenant-task-recipes **R3** (ISU) -> **R4** (ISSG + grants) -> **R11**
(schedule/launch). Find the right domains with **View Security for Securable Item** on the
operation name - e.g. Core Connector: Positions needs "Worker Data: All Positions"
(doc-sourced). Most outbound connectors need Get only; least privilege - Delivery Assurance
flags integrations granted more access than necessary. Transfer schedule ownership to the
ISU (Scheduled Future Processes -> Transfer Ownership) so schedules survive departures.

## Design-review checklist (sourced entries only)

| Check | Why |
|---|---|
| Template researched on Community / Integration Template Catalog before committing | Right template = fewer overrides (doc-sourced) |
| Only needed Integration Services enabled | Extra services add web-service calls (doc-sourced) |
| Field-override count << 30; calc-field overrides justified | >30 = wrong tool; calc fields = performance risk (doc-sourced) |
| Every Integration Map has a Default Value | Unmapped input otherwise errors the run (doc-sourced house practice) |
| Change-detection mode chosen AND documented; indirect-change fields identified | Transaction log misses indirect changes (doc-sourced) |
| DIS on? -> Population Eligibility configured; View (not Get) grants on override fields | Define Eligibility override ignored; Test Security misleads (doc-sourced) |
| Attributes/maps/transports Environment-Restricted; retention set | integration-build.md gates |
| ISU owns reports and schedules; ISSG grants least-privilege | integration-naming.md + tenant-task-recipes R3/R4 |
| Studio augmentation flagged with its Flex-Credits impact in the IDD | Augmentation meters the connector's calls (SKILL.md) |

Troubleshooting quick hits: empty diff output when the change was indirect -> switch to
Full-Diff; unexpected window gaps -> a manual run consumed the timestamp; "Completed with
Warnings" on a DIS connector -> Retrieve Technical Files first.
