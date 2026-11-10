# Deployment Guide - The Client-Facing Deliverable Pattern

The **Deployment Guide** is the named, client-facing document that walks a tenant
admin / developer through getting the app **live in a tenant** and **promoting it
across tenants** (DEV -> IMPL -> SBX -> PROD). It is the "hand this to the client and
they can stand the app up themselves" artifact.

## What it is, and how it relates to the tenant-setup guide

The Deployment Guide and the **tenant-setup guide** (`tenant-setup-guide.md`) are the
same body of content viewed at two altitudes - do not write them twice:

- **For a UI Extend app**, the tenant-setup guide (security domains + BP config +
  App Attributes, step-ordered) **usually IS the deployment guide** - you just wrap it
  with an overview, a promote-across-tenants section, and support/escalation, and give
  it a client-facing title.
- **For an O4I / no-UI integration**, the delivered pattern is a **separate, named
  Deployment Guide** covering config, ISU/ISSG, reference attributes, and schedule -
  because there is **no end-user experience**, so no end-user guide carries the
  operational load. **Precedent:** a delivered O4I no-UI integration shipped a
  **User Guide *and* a Deployment Guide** as two distinct deliverables in the install
  package (the Deployment Guide's own "Installation Package" section lists the User
  Guide `.docx` and a Configuration Extract `.dat` beside it).

**Rule of thumb:** tenant-setup steps *feed* the Deployment Guide. The Deployment Guide
adds the wrapper (overview, prerequisites, install/deploy, promote-across-tenants,
validation, support) around the step-ordered tenant setup. Author the click-level steps
once (per the recipes) and reuse them in whichever deliverable ships.

## Grounded in two real delivered guides

This pattern is reconstructed from two delivered O4I documents (both no-UI integrations,
so both are the "separate Deployment Guide" case). They are referred to below as
**Example A** and **Example B**:

- **Example A - O4I Deployment Guide** (Marketplace / Built-on-Workday style; a delivered
  no-UI integration's guide under `<your workspace>`). BoW-product voice: App Manager
  install, Configuration Extract migration, packaged support process.
- **Example B - Tenant Setup Guide** (project / consulting-delivery style; a delivered
  bespoke O4I integration's guide under `<your workspace>`). Numbered Step 1-8 walkthrough
  for a developer new to Extend/Orchestrate, with a values-to-collect table, a final
  checklist, and a RAID/open-items list.

They use different registers (a Marketplace product install vs. a bespoke project
handoff), but they carry the **same content shape**. The recommended outline below
converges the two.

## The two real section skeletons (what each doc actually used)

### Example A - O4I Deployment Guide (Marketplace/BoW register)

1. **About this Application** - plain-English purpose + the scenarios it handles.
2. **About this Guide** - audience (technical resource installing/configuring),
   and the pointer to complete it *before* the User Guide.
3. **Installation Package** - what ships: User Guide `.docx`, Configuration Extract
   `.dat`, validation files.
4. **Application Prerequisites** - *Workday Tenant* (platform components enabled: Built
   on Workday, O4I, Core HCM); *Application Security* (security groups / ISSG to create,
   with a permissions file); *Integration System Users (ISU)* (ISUs to create + the ISSG
   to add each to).
5. **Application Installation** - App Manager worklet: Ready to Install -> Install ->
   confirm under Installed (once per tenant).
6. **Tenant Configuration** - *Object Migration* (Migrate Configuration Extract `.dat`,
   **or** App Manager -> Configure -> Install); *Object Validation* (confirm every
   packaged object exists, compare configs; validation file per implementation type -
   Integration System + Custom Report); *Create Integration System* (template =
   Orchestrate Integration Template, name, Maintain/Configure Integration Attributes,
   Maintain Launch Parameters, Workday Account -> Edit -> assign ISU); *Integration
   Scheduling* (Launch/Schedule, daily recurrence, launch criteria explained, schedule
   tab - start time, catch-up, start/end dates).
7. **Application Support** - *Technical Support* (managed-services process,
   authorized support coordinators); *Support Portal Instructions* (login, create
   incident request, severity vs. urgency).

### Example B - Tenant Setup Guide (project register)

- **Title block** - app name, "Workday Tenant Setup Guide", program, prepared date /
  build package, audience ("developers new to Workday Extend / Orchestrate").
- **Contents** (TOC).
- **How to Use This Guide** - work in order; quoted text = exact Workday task name;
  effort estimate; do it in a test tenant first, never PROD; "Stuck? contact ...".
- **What This Integration Does** - plain-English overview + the nightly flow, and a
  **Key Facts** table (Integration ID, app name / reference ID, main orchestration,
  type/direction, source system, Workday web service used, run frequency, currently
  deployed-to tenant, upstream dependency).
- **Before You Start** - *Access You Need*; *Values You Need to Collect* (a
  parameterized table: value -> who provides it -> status/open issue, with BLOCKED
  markers tied to RAID IDs).
- **Step 1 - Verify the App Is Deployed** (find it in-tenant; confirm the orchestration
  + suborchestrations).
- **Step 2 - Create the Integration System** (+ a TIP box: if the template doesn't
  appear, the deploy didn't finish or you lack Extend security).
- **Step 3 - Security Setup** - *3a* Create the ISU; *3b* Create the ISSG + add ISU;
  *3c* Grant Domain Security Policies (domain -> access -> why table; **verify the securing
  domain via `View Security for Securable Item`**; then Activate Pending Security Policy
  Changes; TIP that the launcher's own token needs the access when testing).
- **Step 4 - Integration Attributes** (exact-name-match IMPORTANT box; attribute table;
  create-with-TBD-then-fill for BLOCKED values).
- **Step 5 - Launch Parameters** (Validation Mode, Debug; defaults false).
- **Step 6 - Notifications** (one for Failed/Aborted, one for Completed with Errors;
  recipients; subject/body pointing at the ERROR messages).
- **Step 7 - Schedule the Nightly Run** (IMPORTANT: do not schedule until E2E passes;
  Run As User = the ISU; schedule launch params false/false).
- **Step 8 - Smoke Test** (validation-mode first -> live run in test tenant -> verify
  both systems -> re-run retrieves zero).
- **Final Checklist** (numbered, initial-and-date, hand back to the lead).
- **Open Items You Cannot Close Yet** (RAID items that block go-live but not setup).
- **Contacts** (name / role / email).

## Recommended converged outline (use this)

Merge the two. Sections marked **(O4I)** vs **(UI)** flag where the variants diverge -
see the variant section below.

1. **Overview / About this Application** - plain-English purpose, who runs it, where it
   lives in Workday. *(from both - Example A "About this Application", Example B "What This
   Integration Does".)*
2. **About this Guide + Installation Package** - audience, how to read it (quoted text =
   exact Workday task name, work top-to-bottom), and what ships with it (User Guide,
   config extract, validation files). *(Example A "About this Guide" + "Installation Package";
   Example B "How to Use This Guide".)*
3. **Prerequisites** - tenant platform components enabled (BoW / O4I / Core HCM / Extend
   SKU); access the executor needs (security admin, App Manager, Extend view); upstream
   dependencies (other INTs live, refresh timing). *(Example A "Application Prerequisites";
   Example B "Before You Start -> Access You Need" + Key Facts "Dependency".)*
4. **Per-tenant parameter table ("Values you need for THIS tenant")** - one table up
   front: every WID, alias, group name, endpoint, and attribute value the run needs,
   with owner and status; BLOCKED rows tied to RAID IDs. *(Example B "Values You Need to
   Collect" - the model for this; make it the first thing after prerequisites.)*
5. **Environment / version to deploy** - which built version goes to which tenant, the
   promotion level path, and the reference ID / tenant aliases. *(cross-ref
   `promotion-and-environments.md`.)*
6. **Install / deploy the app** - *DEV*: `wdcli app deploy`; *higher tenants*: this is a
   promotion, not a deploy - see section 7. For a Marketplace/BoW app the install is the **App
   Manager worklet** (Ready to Install -> Install) plus **Object Migration** of the
   Configuration Extract. *(Example A "Application Installation" + "Tenant Configuration ->
   Object Migration/Validation".)*
7. **Promote across tenants (DEV -> IMPL -> SBX -> PROD)** - first-class section; see its
   own heading below. *(cross-ref `promotion-and-environments.md`; the Example A doc's
   per-tenant "install once per tenant" note is the seed of this.)*
8. **Security setup (ISU / ISSG / domains)** - build this section from
   **`security-setup-section.md`** (the reusable novice spec): its **Part 1** names the exact
   tasks in order (embed the recipes - **R3**->**R4**->**R2** for O4I; **R1**->**R2** for UI -
   don't restate clicks), its **Part 2** is the naming block (ISU/ISSG/domain/group/API-client
   names, filled with this app's values), and its **Part 3** is the **enumerated domains &
   permissions table** - every domain, its plain-English purpose, the exact Report/Task
   (View / View & Modify) and Integration (Get / Put) access, and which group gets it,
   populated from the design doc's Security tab / IDD `WD Solution` tab. A blank domain table
   is a defect. *(Example B "Step 3 - Security Setup"; Example A "Application Prerequisites ->
   Security / ISU"; recipes in `tenant-task-recipes.md`; the section template in
   `security-setup-section.md`.)*
9. **Reference data / App or Integration Attributes (per environment)** - **R8** (App
   Attributes, UI apps) / **R8b** (Integration Attributes, O4I). This is the per-tenant
   values step - each attribute, its meaning, and how to find this tenant's value.
   *(Example B "Step 4 - Integration Attributes" + Example A "Configure Integration Attributes".)*
10. **Schedule / launch config** - **R11**; launch parameters (**R10**-adjacent);
    validation-mode-first; leave PROD schedule suspended until go-live. *(Example B "Step 5
    Launch Parameters" + "Step 7 Schedule"; Example A "Integration Scheduling".)*
11. **Notifications** - **R10**; failure + completed-with-errors alerts to the support
    list. *(Example B "Step 6 - Notifications".)*
12. **Validation / smoke test** - a concrete numbered end-to-end script (not "test the
    app"); validation-mode first, then a real run, then a safe re-run; verify both
    systems. *(Example B "Step 8 - Smoke Test"; Example A "Object Validation" for the
    config-object side.)*
13. **Final checklist** - numbered, initial-and-date, handed back to the lead. *(Example B
    "Final Checklist".)*
14. **Rollback** - what "abort" means, who calls it and by when; remember **promotion is
    one-way** - rollback = turn users back to legacy + disable app access, not
    un-promote. *(cross-ref `cutover-planning.md` section 2 rollback plan.)*
15. **Open items / known gaps** - RAID items that block go-live but not setup, with
    owners, so the executor doesn't chase them as setup failures. *(Example B "Open Items
    You Cannot Close Yet".)*
16. **Support / escalation + Contacts** - the managed-services / support-portal process
    for a Marketplace app, or the escalation contact list for a project. *(Example A
    "Application Support"; Example B "Contacts".)*

## Promote across tenants (DEV -> IMPL -> SBX -> PROD) - a first-class section

Every Deployment Guide gets an explicit promotion section. **Do not restate promotion
mechanics - pull them from `promotion-and-environments.md`** and localize with this
app's reference ID and tenant aliases. Cover, at minimum:

- **The path and that it is one-way.** `wdcli app deploy` reaches **DEV only**; every
  higher tenant (IMPL -> SBX -> PROD) is reached with **`wdcli app promote`**, never
  `deploy`. There is **no demote** - fix forward with a new version. SBX is refreshed
  weekly from PROD, so anything in SBX not also in PROD is wiped.
- **(!) The app is not the whole deployment.** The **Integration System and any RaaS
  custom reports promote SEPARATELY** from the app version - promoting the app alone
  leaves the integration unrunnable in the target tenant. Treat every promotion as a
  bundle (app version + Integration System config + every RaaS report, same name +
  Integration Maps / CredStore / schedules). *(See `promotion-and-environments.md`
  "The app is not the whole deployment".)*
- **The per-tenant re-setup matrix reminder.** Promotion **does not carry** security
  domain grants, ISU/ISSG, API clients, App Attributes, or BP config - every one of
  those is re-done in each tenant. Point the reader at the re-setup matrix in
  `promotion-and-environments.md` and at the numbered recipes for each item, rather than
  duplicating the matrix. State the lead-time reality: client security-admin requests
  often take **1-2 weeks each** - front-load them per tenant.
- **A promote-and-verify sequence per hop.** For each hop (e.g. IMPL -> SBX): promote the
  version -> promote/rebuild the Integration System + RaaS reports -> re-run the security /
  attributes / schedule setup for that tenant -> smoke test -> sign off before the next
  hop. Non-migratable items (API clients, PGP private keys) must be created in the
  **master tenant** so a refresh carries them down - flag which tenant that is.

## O4I (no-UI) variant vs. Extend-UI variant

The outline is shared; these are the deltas.

| Aspect | **O4I / no-UI integration** | **Extend UI app** |
|---|---|---|
| End-user guide? | **No** - no end users. The Deployment Guide is a standalone deliverable and carries the whole operational load (paired only with an *operations*-flavored guide for the Integration Admin, per Example A). | Yes - a separate **User Guide** carries end-user tasks; the Deployment Guide focuses on standing the app up. |
| Dominant setup content | **ISU/ISSG + domain Integration Permissions (Get/Put)**, **Integration Attributes** (per environment), **schedule/launch** config, **notifications**. Recipes **R3->R4->R2, R8b, R11, R10** (+ **R9** for file/SFTP keys, **R5** for the Integration System). | **Security-domain grants to user role groups (View+Modify)** and **BP definition / approver-chain config** dominate. Recipes **R1->R2, R7, R8**; **R6** only if external REST/WQL. |
| Attributes | **Integration Attributes** on the Integration System - **developer-owned** (R8b), read by exact name at runtime. | **App Attributes** via App Manager -> Configure (R8) - instance WIDs that differ per tenant. |
| BP config | Usually none (no interactive BP). | **Central** - the Extend file declares one step; the real approver chain is configured on the BP definition in-tenant (R7). |
| Launch | Scheduled run as the ISU (R11); validation-mode-first smoke test. | User-initiated task; smoke test is create -> route -> approve -> write-back -> verify. |
| Support wrapper | Marketplace/BoW: managed-services support process + portal (Example A). Project: escalation contact list (Example B). | Same choice by delivery type. |

## Authoring standard

The Deployment Guide is **novice-executable** - assume the reader has never done this and
is following along live in the tenant.

- **Embed the click-level recipes, don't re-invent them.** The section skeleton is the
  *skeleton*; for each setup step, drop in the matching numbered recipe from
  **`tenant-task-recipes.md`** (R1-R12), filled with this app's real names. Point at the
  recipe library so the guide stays the single source of the click steps.
- **The security section is not just tasks - give tasks + naming + domains/permissions.**
  Build it from **`security-setup-section.md`**: exact tasks (Part 1), the naming block for
  every object the reader creates (Part 2), and an **enumerated domains-and-permissions table**
  with a plain-English "what this lets the app do" column and the exact View/Modify + Get/Put
  access per domain (Part 3), populated from the design doc. Never ship "set up security" with
  no domain table.
- **Exact task names, one action per step.** Name the searchable Workday task in quotes
  ("Create Integration System User") before the steps; one field/button per numbered
  step; define each term (ISU, ISSG, domain, WID, attribute) in one plain sentence on
  first use.
- **One per-tenant parameter table up front.** Every value that changes per tenant (WIDs,
  aliases, group names, endpoints, attribute values) goes in a single "values you need for
  THIS tenant" table near the top, with owner and status - the model is Example B's "Values
  You Need to Collect". Everything downstream references that table.
- **Mark blocking steps + failure symptoms.** Flag the blocking step loudly ((X)) and state
  the symptom if skipped so a mis-ordered run self-diagnoses - the canonical one:
  **domain grant not activated -> S22 "permission denied"** (pages load, data doesn't).
  Mark unknowns TBD-with-owner (wd-design-doc yellow-highlight spirit), never silently
  omit.
- **State what success looks like.** Every step gets a "you're done when..." check and, for
  the whole guide, a final numbered checklist to initial-and-date.
- **File mechanics via the `docx` skill.** Markdown for a working/dev audience; a Word
  document (neutral formatting, auto TOC) for a formal client deliverable - the `docx`
  skill owns the file itself.
- **Client-neutral instruction voice.** Write the steps so any client can execute them.
  Keep real client literals (tenant aliases, WIDs, contact emails, dates) out of the
  reusable body - put them in the per-tenant parameter table, under a `## Program
  defaults` block, or clearly framed as delivered-example provenance.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live:

- **Delivered precedents** - the two model docs (Example A, a Marketplace/BoW
  O4I Deployment Guide with a paired User Guide; Example B, a bespoke O4I
  Tenant Setup Guide as the standalone integration deliverable). Use both as
  the model, not as content to copy verbatim.
- **Tenants the guide is executed against** - the DEV tenant alias
  (`wdcli app deploy` target) -> IMPL tenant alias(es) (E2E) -> SBX -> PROD, and
  the target PROD window. Same path for every app in the program.
- **Org short ID + developer account** - the org short ID / reference-ID
  suffix, and the developer account the deploys run under
  (`wdcli account switch` / `wdcli whoami`).

**Lead times:** each client security-admin request (domains, ISU/ISSG, API
client) often takes **1-2 weeks** - front-load and batch per tenant stand-up.

**Delivered-example provenance, not reusable literals:** real contact lists,
RAID IDs, and vendor values from the delivered guides are provenance only - do
NOT carry them into a new client's guide.

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).
