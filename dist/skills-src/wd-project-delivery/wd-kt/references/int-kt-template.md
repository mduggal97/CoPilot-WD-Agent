# Integration KT Document - the per-integration handoff reference

The standard KT deliverable for **integrations** (Studio, EIB, Core Connector,
DT, O4I-as-INT). Where the Extend-app KT set splits by audience (user guide, admin
guide, runbook), an integration's KT lands in ONE Word reference document per
integration (or one document covering a related set) that the client's Integration
Administrator keeps open while operating it. Get the blank template one of two
ways - don't rebuild the skeleton by hand: **regenerate the clean, vendor-neutral
blank via `scripts/build_int_kt_template.py`** (cross-platform, python-docx - see
`references/scripts.md`), **or obtain the firm's branded master per engagement**
(environment/project memory). Either way the section skeleton
below is the content model - render it via the `docx` skill, not
by editing the builder.

**Relationship to neighbors:** this document is the *operations reference* - it
overlaps the O4I Deployment Guide / tenant-setup guide (wd-deployment
`references/deployment-guide.md`) on ISU/ISSG/attributes/scheduling, but its job is
different: the Deployment Guide stands the integration up once; the KT document is
what the admin re-reads every launch, error, and maintenance event. Populate both
from the same design doc; don't fork content - where a Deployment Guide exists,
the KT doc's security/attribute tables cite the same values.

The template's own framing: the document **supplements the KT session, never replaces
it** - its Introduction enumerates what the live session walks through (integration
system, services and configuration, business process, launch parameters,
notifications, logical flow, inputs/outputs, security, remaining documentation).
Keep that list in the Introduction so the session scope is contracted in writing.

## Section skeleton (from the template, in order)

| # | Section | Content shape |
|---|---|---|
| 1 | Revision History | table: Revision # / Date / Revised by / Description |
| 2 | Introduction + High-Level Integration Overview | the supplement-to-session framing + the session-scope bullet list; plain-English overview |
| 3 | Interface and Configuration Summary | one row per integration covered: Integration Name / Integration System Type / link to Design Document. One doc can cover several related integrations - repeat the per-integration sections under "Current Integration: <name>" headers |
| 4 | Integration Custom Services (+ RaaS Reports subsection) | tables: Service Type / Name / Description; RaaS rows add report name + link |
| 5 | Integration Attributes | Provider / Attribute Name / Value / Description - "configurable parameters retrieved at run time, more constant in nature" |
| 6 | Integration Maps | Map / Description (Workday value -> external value translations) |
| 7 | Web Services | Web Service / Description |
| 8 | Business Process | the BP(s) needed to execute the integration |
| 9 | Integration Security | ISU table (User / Description) + ISSG table (Group / Description / Link); template rule: **every integration has an ISU and an ISSG** |
| 10 | Integration Launch Instructions | generic `Launch / Schedule Integration` walkthrough + a Launch Parameters table (Parameter / Type) with per-integration specifics |
| 11 | Scheduling Integrations | run-frequency reference (below) + integration-specific schedule |
| 12 | Periodic Maintenance | Item to Maintain / Description - recurring human interventions (new map items for future data, resetting schedules) |
| 13 | Integration Error Handling | Error Type / Error-Warning / Description / Resolution Task - the template scopes this to **Studio and transformation integrations**; for packaged connectors Workday owns the error surface and rows are added as testing finds them |
| 14 | Integration Event Review | Task / Notes / Resolution Task - what to check after each launch |

Sections 12-14 are the ones no other deliverable carries - do not skip them. The
error-handling table is the same three-way shape as the user-guide error table
(`user-guide-pattern.md`): message -> meaning -> action; harvest rows from testing
and hypercare, same as the runbook.

## Scheduling reference the template embeds (keep it)

- Run frequencies: Run Once in the Future, Minute/Hourly/Daily/Weekly/Monthly
  Recurrence, and **Dependent** (trigger on another integration's completion
  status) - each with its schedule-criteria fields.
- **Transfer schedule ownership to the integration's ISU** - a schedule owned by a
  departing consultant's account dies with the account.
- A schedule's End Date cannot be set beyond **December 31 of the next calendar
  year** - so schedules expire and re-creation is a Periodic Maintenance row.
- Concurrent-event handling lives on the "Integration Criteria" tab when offered;
  mind Workday's weekly maintenance windows when picking run times.

## Usage notes

- Audience-mapping fit: this is the **client-admin deliverable** for an
  integration (the "admin/config guide" row of SKILL.md's audience table), and its
  sections 12-14 seed the support-desk runbook. It does not replace developer KT
  (code walkthrough, `client-dev-enablement.md`) for custom-built Studio/O4I work.
- Track the KT session and teach-back for it per `kt-sessions.md`; plan the topic
  rows in the KT Plan workbook (same file, "KT Plan workbook" section).
- Fill every table from the design doc / IDD - an empty ISU/ISSG or attributes
  table is a defect, same standard as the security section rule in wd-deployment
  `references/security-setup-section.md` - table contents are verifiable live via
  tenant-ops before KT sign-off, so the doc teaches the as-built tenant
  (wd-extend-dev references/tenant-ops.md).
