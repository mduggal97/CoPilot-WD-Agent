# Tenant Setup Guide - The Deliverable Pattern

Every Extend app needs a **step-ordered tenant setup document** that a client
tenant admin can follow top-to-bottom to make the app functional in a new
tenant. Write it once per app; it gets executed once per tenant (DEV -> IMPL ->
SBX -> PROD), so keep tenant-specific values (WIDs, aliases, group names)
clearly parameterized.

> **Relationship to the Deployment Guide** (`deployment-guide.md`): these tenant-setup
> steps *feed* the client-facing **Deployment Guide**. For a **UI Extend app** this
> step-ordered content usually *is* the Deployment Guide (wrapped with an overview,
> a promote-across-tenants section, and support). For an **O4I / no-UI integration**
> the Deployment Guide is a **standalone named deliverable** built on these steps.
> Author the click-level steps once here (via `tenant-task-recipes.md`) and reuse them.

## Real examples to model

- **Markdown cheatsheet style:** a delivered Extend app's `TENANT_SETUP.md`
  cheatsheet under `<your workspace>`. Numbered sections, "work top to
  bottom," a blunt callout of the blocking step ("(X) nothing works until this
  is done"), tables for BP approver chains and WQL sources, and a closing
  smoke test + backlog list.
- **Client-deliverable docx style:** a delivered O4I integration's **Tenant
  Setup Guide** (`.docx`) under `<your workspace>` - same content shape,
  formatted as a Word document for client handoff.

Pick the format by audience: markdown for a working/dev audience, docx for a
formal client deliverable (use the docx skill for the file itself).

## Embed the click-level recipes - and write for a novice

The step order below is the *skeleton*. For each step that the CLIENT executes
in the tenant, embed the matching **numbered recipe** from
`tenant-task-recipes.md`, filled with THIS app's real names - so the client
gets crystal-clear "here's exactly what YOU do in the tenant" instructions, not
a vague pointer. Recipe map:

| Setup step | Recipe(s) to embed from `tenant-task-recipes.md` |
|---|---|
| 1. Grant the security domains (the S22 fix) | **R1** (grant) -> **R2** (activate) |
| 2. Configure the business processes | **R7** |
| 3. Provision / confirm security groups | (feeds R1/R7 - list the groups) |
| 4. ISU / ISSG / Integration System / API client | **R3** (ISU) -> **R4** (ISSG) -> **R2** (activate) -> **R5** (integration system); **R6** if external REST/WQL; **R9** for SSH/PGP keys |
| 5. App Attributes (tenant WIDs) | **R8** (App Attributes) / **R8b** (Integration Attributes) |
| 6. Notifications / schedule / other config | **R10** (notifications), **R11** (schedule/launch) |

**The security steps (1, 3, 4) follow the Security Setup Section spec.** For anything
security - domains, ISU/ISSG, groups - build the content from
**`security-setup-section.md`**: name the exact tasks in order (Part 1), give the naming
pattern *and* a filled example for every object the reader creates (Part 2), and include the
**enumerated domains-and-permissions table** - every domain, plain-English purpose, the exact
Report/Task (View / View & Modify) and Integration (Get / Put) access, and the group it's
granted to (Part 3), populated from the design doc's Security tab / IDD `WD Solution` tab. A
blank domain table is a defect.

**Novice-audience writing standard - apply to every embedded step** (this extends the plain-language writing standard owned by wd-extend-lifecycle; the tenant-step specializations below are the local delta, not a redefinition). Assume the
reader has **never done this before** and is following along live in the tenant:

- **Name the exact Workday task** (the searchable string typed into the search
  bar), in quotes, before the steps - never "go configure security".
- **One action per numbered step.** Each step names the field/button and what to
  enter. Don't bundle three clicks into one sentence.
- **No unexplained jargon.** The first time you use a term (ISU, ISSG, domain,
  WID, App Attribute), say in one plain sentence what it is and why it matters.
- **State what success looks like** after the step ("You're done when...") and the
  **failure symptom if skipped** (e.g. S22) so a mis-ordered run self-diagnoses.
- **Mark unknowns**, don't omit them: `(!) confirm exact label in-tenant` for a
  task name the source couldn't pin down; TBD-with-owner for a missing value
  (the wd-design-doc yellow-highlight convention's spirit).

## The canonical step order

The ordering matters - each step unblocks the next. Deviating produces
confusing symptoms (e.g., testing before domain grants and concluding the
app is broken).

### 0. Deploy the build
The exact deploy/promote command(s) for this tenant, including the reference
ID and tenant alias. For non-DEV tenants this is `wdcli app promote`, not
`deploy` (see `promotion-and-environments.md`). Note who runs it and any
login prerequisite the admin must do interactively (`wdcli tenant login`).

### 1. Grant the security domains - the blocking step
Call this out loudly: **until granted, every BO call returns S22 "permission
denied"** - pages may load, data won't. Include the **domains-and-permissions
table** from `security-setup-section.md` Part 3 - one row per domain the app
declares, with:
- The exact domain names the app declares (list each `.securitydomain` - usually
  a **Data** domain + a **Pages** domain) and a plain-English note on what each
  lets the app do
- The exact access per domain: **Report/Task** = View or View & Modify;
  **Integration** = Get and/or Put
- The tenant task: Domain Security Policies (or Maintain Permissions for
  Security Group) -> add the security group with that access ->
  **Activate Pending Security Policy Changes** (R1 -> R2)
- Which group to grant for testing vs. the production groups (cross-ref
  step 3)

### 2. Configure the business processes
The Extend file declares only a single approval step; the real routing lives
on the BP **definition** in-tenant. Provide a table: BP name -> the full
approver chain from the design doc (step by step, including conditional
steps), plus the **initiation security** per BP (who can submit). One row
per custom BP.

### 3. Provision / confirm security groups
List every role-based group the app's design references, note any verified
in-tenant names, and flag that the client finalizes names/membership. These
feed both step 1 (grants) and step 2 (routing/initiation).

### 4. ISU / API client
Name the objects per the naming block (`security-setup-section.md` Part 2 -
`ISU <INT ID> <Description> <Type> <Direction>`, matching ISSG), then:
- ISU + ISSG with Integration Permissions (Get/Put) on the exact functional
  areas the orchestrations call (e.g., Financial_Management,
  Resource_Management, Staffing), mapped to the app's
  `_DEFAULT_WORKDAY_CREDENTIAL` - list each in the domains-and-permissions
  table (Part 3, O4I variant), confirming each domain via `View Security for
  Securable Item` against the real web-service operation
- If external/BO REST is used: register the API Client, create the refresh
  token, record the token endpoint - per tenant
- Confirm/enable BP->orchestration subscriptions where applicable

### 5. App Attributes (tenant-specific WIDs)
List each App Attribute, what it holds, its default (which tenant that
default belongs to), and **how the admin finds this tenant's value** (e.g.,
the WQL query to read an org-subtype WID: `SELECT subtype FROM
customOrganizations` and read `subtype.id`). This is the step most often
missed because the app *appears* to work with the wrong tenant's defaults.
With a tenant-ops profile, Claude runs this WQL and hands the admin the
actual WID (wd-extend-dev references/tenant-ops.md).

### 6. Sequence generators / reference data / other config
Any delivered sequence generators to confirm, config-BO seed data to load,
Integration Maps, CredStore entries, scheduled launch configurations.

### 7. Smoke test
A concrete numbered script, not "test the app": open the specific task ->
create a record with named sample values -> confirm the BP lands in the
configured approver's inbox -> approve/deny/send-back -> confirm the
write-back result -> check the reporting page. Include the send-back/revise
round-trip if the app has one.

### Appendix: backlog / known gaps
Anything intentionally not in scope for this tenant setup (unbuilt items,
open items by number) so the admin doesn't chase them as setup failures.

## Style rules

- **Number the steps and state the dependency** ("Items 1-3 are required
  before anything works; 4-7 make the automation real").
- **Name exact tenant tasks** (the searchable Workday task name), exact
  domain/group names, exact endpoints - the admin should never have to
  guess.
- **Mark blocking steps** with a visible symbol and the failure symptom
  (S22) so a mis-ordered execution self-diagnoses.
- **Parameterize per-tenant values** in one place (a table of "values you
  need for this tenant" up front works well for PROD runs).
- Apply the wd-design-doc yellow-highlight convention's spirit: unknowns are
  explicitly marked TBD with an owner, never silently omitted.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live:

- **Tenants the guide is executed against** - the DEV -> IMPL -> SBX -> PROD tenant
  aliases and the target PROD (go-live) window.
- **Org suffix + developer account** - the org suffix appended to reference
  IDs, and the developer account the deploys run under (`wdcli account switch`
  / `wdcli whoami` to confirm the active account).

Client security-admin requests (steps 1, 3, 4) often take **1-2 weeks each** -
front-load them and batch the requests when scheduling a tenant stand-up.

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).
