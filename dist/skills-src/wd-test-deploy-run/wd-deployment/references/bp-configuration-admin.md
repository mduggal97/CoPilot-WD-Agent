# Business process configuration - native tenant BPs

doc-sourced - Workday Education course manuals (public), crawled 2026-08-25; cite: "HCM Core for
Administrators" (Business Process Framework chapter), cross-checked against "Security for Administrators".
These are doc-tier facts: verify in-tenant before load-bearing use (labels and options can shift by release).

**Scope:** how NATIVE Workday business processes (Hire, Terminate, Change Job, custom definitions of
delivered types) are configured. Custom Model BPs on Extend business objects live in wd-extend-dev
`model-bp.md`. The click-level "configure an app's BP definition per tenant" procedure is recipe **R7**
in `tenant-task-recipes.md` - this file is the rules that recipe assumes.

## Anatomy of a BP definition

- A business process = configurable steps completing a larger task. Each **BP type** is
  vendor-delivered - you cannot create new types - and each type has exactly **one BP security policy**.
- Edit via Related Actions > **Business Process > Edit Definition**; create a new definition via
  **Create, Copy, or Link Definition**. Search prefix `bp:` finds definitions.
- **Initiation step:** always step "a", always first, cannot be removed; its section of the security
  policy defines who can start the process.
- **Completion step:** the step where data COMMITS to the system. Exactly ONE per definition
  ("Set as Completion" on a step). **All Approval and Review steps must come BEFORE the completion step.**
- **Letter-based step ordering:** steps are ordered a, b, c... deliberately letters, not numbers, so
  you can insert between them without renumbering: a, b, ba, bb, c. Steps run sequentially or in
  parallel per configuration.

## Default vs custom definitions - and how Workday picks one

Every BP type has a **default definition**; orgs can carry their own **custom definitions**.
Resolution order for an event in an organization:

1. A definition specific to THAT organization.
2. The nearest superior organization's definition (walk UP the hierarchy).
3. The default definition.

**A definition containing ERRORS is skipped entirely** - Workday silently falls through to the next
candidate. If an org "isn't using its custom definition", check the definition for errors before
anything else.

One inheritance quirk: copied definitions inherit initiation-step worklets (embedded analytics) from
the DEFAULT definition - initiation-step worklets can only be configured on the default.

## Step types - three buckets

| Bucket | Steps | Notes |
|---|---|---|
| Action | review/edit data, initiate subprocesses | validation conditions allowed here |
| Approval | Approval, Approval Chain, Consolidated Approval, Consolidated Approval Chain, Mass Approval | **a single denial denies the ENTIRE business process** |
| Utility | To Do, Service, Batch/Job, Integration, Report, Complete Questionnaire, Edit Additional Data, Review Documents, Checklist, Shared Participation | plus connector-specific: Service - Fire Integration, Service - Document Delivery, Service - Document Retrieval |

Utility-step rules worth knowing:
- **To Do steps can be assigned to ANY active security group in the tenant** - the group does NOT need
  to be on the BP security policy. Maintain via **Maintain To Dos**; find usage via the **To Dos** report.
- **An Integration step failure terminates the whole BP.**
- Edit Additional Data steps skip BP validation rules.

## Condition rules - the four kinds and where each is legal

This taxonomy is the thing people misremember; keep the table handy:

| Condition kind | What it decides | Legal on |
|---|---|---|
| Entry | whether a step executes | ALL step types EXCEPT Initiation |
| Validation | data checks; if any validation condition applies, the process STOPS | Initiation and Action steps ONLY |
| While Running | evaluates the next user in the management chain | Approval Chain / Consolidated Approval Chain ONLY |
| Exit | when the step is considered complete | Approval Chain, Consolidated Approval Chain, and Integration steps ONLY |

- Construction: And/Or logic + Source External Field or Condition Rule + Relational Operator +
  Comparison Type (compare to a value or to another field) + Comparison Value.
- Troubleshoot a rule with **Rule Tester** (Related Actions).
- Step-level config menu (per step): Create Condition Rule, Maintain Step Conditions, Maintain Step
  Delay, Maintain Advanced Routing, Maintain Step Label Override, Maintain Step Help-Text,
  Set as Completion.

## Approval rules (the commit gate)

- One completion step maximum; every Approval/Review step sits before it.
- A denial at ANY approval step denies the whole BP - there is no partial-deny.
- **Advanced Routing** (Maintain Advanced Routing on the step) can prevent self-approval: exclude the
  initiator, a prior approver, or the subject of the event.
- Stuck steps: reassign via **Mass Operation Management** (includes Reassign Business Process Steps).

## Notifications and delegation

- **Notifications** trigger on BP status change or step entry/exit; delivered by email or the in-tenant
  Inbox; body = static text + dynamic fields.
- Delegation is granted through the BP security policy ("delegate" permission per group); delegated
  tasks route to the delegate's inbox for the configured scope/period. (Deep delegation design is a
  client-security-model topic - security-role-design.md.)

## BP security policies

Each BP TYPE has one security policy controlling, per security group: **initiate** (including via
specific web services - "Initiating Action (Web Service)"), **approve**, **deny**, **delegate**,
**cancel**, **rescind**, **view all**, **manually advance**.

**BP policy edits are STAGED - they require Activate Pending Security Policy Changes** (recipe R2),
exactly like domain policy edits. The full activation-asymmetry rule (policy edits pending vs group
changes immediate) lives in `configurable-security-admin.md` - it applies verbatim here.

## Diagnostics and reference reports

| Task/report | What it answers |
|---|---|
| **Business Process Configuration Options** | per BP type: available step types, org types, allowed actions, restrictions, prerequisites, allowed subprocesses, mass-action support - read this BEFORE designing a definition |
| Business Process Security Policies for Functional Area | which groups hold which BP permissions |
| View Definition (per effective date) | what the definition looked like when an event ran |
| Business Process Exception Audit | definitions with errors (the silent-skip cause above) |
| Unassigned Tasks | BP steps stuck on empty security groups |

## Worked staffing examples (from the manual - patterns, not prescriptions)

- Hire requires: hire date, position, employee type, job profile, time type, location; Propose
  Compensation for Hire runs as a subprocess.
- Auto-populate service dates: add a "Service Dates Change" subprocess, tick Autocomplete, configure
  **Maintain Staffing Field Defaults**.
- Supervisory-org corrections on Hire require both orgs on the same staffing model; enabled via the
  Hire BP security policy.
- Role handoffs on job change: subprocess **Assign Roles - Change Assignments for Worker** inside
  Change Job, with transfer/copy/remove options (see configurable-security-admin.md, role-based section).

## Checklist when a BP "doesn't work"

1. Is the definition erroring? (**Business Process Exception Audit** - an erroring custom definition is
   silently SKIPPED and the default runs instead.)
2. Did a BP security policy edit go unactivated? (R2.)
3. Is a step assigned to an empty security group? (**Unassigned Tasks**.)
4. Did a denial or an Integration-step failure kill the process? (Denial denies ALL; integration
   failure terminates the BP.)
5. Is the condition rule on a step type where that condition kind is even legal? (Table above.)
