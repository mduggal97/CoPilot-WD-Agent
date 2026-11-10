# Customer technical roles, access & enablement - set the client's team up for success

A delivery isn't done when the app ships - it's done when the **client's own technical people can run, extend, and support it**. That starts on day one, not at handoff: the customer's integration / Extend / Prism / reporting / security owners need access **early** so they can start *learning and using* the Workday tools while we build alongside them. This reference is the model for who those counterparts are, what access each needs, **when** to provision it, and how we get them productive. It is a lifecycle artifact (**staged in the plan**) and a KT artifact (**enablement is continuous**) - see the ownership note at the bottom.

**Guiding principles (state these to the client's security team at kickoff):**
- **Least-privilege + just-in-time.** Grant each role what it needs *when it makes sense to provide it* - not everything on day one. Access is a planned, phased set of milestones, not a single request.
- **Early enough to learn, not so early it rots.** A builder who gets a sandbox + tool access during design can do Workday's training and practice before they must produce - so they're productive when their workstream starts. That head start is the whole point.
- **The Security Partner's SLA gates everyone.** Every other role's access is a request that role fulfills; identify that person first and get their turnaround time in writing (this is why the kickoff checklist names them).
- **It's in the plan.** Access-provisioning milestones live on the project plan (wd-pm) with owners and dates; the client onboarding packet (wd-pm `references/client-onboarding-packet.md`) names each role's owner and access-need date.

## The role archetypes

Six technical counterparts (a client may combine several into one person, or split one across a team - map to real names in the onboarding packet). **Domains listed are Workday-standard; the security GROUPS they attach to are per-tenant/client-defined** - grant the domain to the client's role-aligned group. Grant mechanics (the click-level how) live in wd-deployment `references/tenant-task-recipes.md` (R1-R12) and wd-extend-dev `references/security-setup.md`; which domains a *specific* build needs come from each REST op's `x-workday-secured-by-domains` (wd-extend-dev `references/rest-api-catalog.md`) and the op->domain query (`references/tenant-ops.md`).

| Role | Owns on the client side | Core Workday domains (grant to their group) | Access needed by |
|---|---|---|---|
| **Security Partner / Administrator** | Domain & BP security-policy grants, ISU/ISSG creation, activation, auth policy. The gatekeeper. | Security Administration, Security Configuration; Set Up: (functional areas being enabled); the *Activate Pending Security Policy Changes* task | **Kickoff (day one)** - everyone else waits on them |
| **Integrations Developer / Lead** | EIB / Studio / Core Connector / DT / O4I build + ownership, ISU/ISSG, schedules, monitoring | Integration Build, Integration Configure, Integration Event, Integration Debug, Integration Security | Discovery->Design (read + sandbox to learn); full at Build |
| **Extend Developer** | Extend apps (PMD/model/orchestration), App Manager config | Developer-site (dev company) account, App Manager access, Development, + each app's functional-area security domains | Discovery->Design (dev tenant + training); full at Build |
| **Prism Analyst / Data Engineer** | Prism tables, datasets, pipelines (DCTs), connections | Prism: Tables Create/Manage, Prism Datasets Create/Manage/Publish, Prism: Manage Data Source, Manage Connection, Manage File Containers | When the data/reporting workstream starts (often Design) |
| **Reporting / RaaS Author** | Custom reports, RaaS endpoints, WQL | Report Definition Sharing (All/Groups/Users as scoped), Custom Report Administration, Custom Report Creation, Manage: All Custom Reports, Workday Query Language / WQL for Workday Extend | Design (to define report/RaaS sources) onward |
| **Functional / BP Config Owner** *(adjacent, not always "technical")* | BP definitions the Extend/Model-BP apps trigger; worktag/related-worktag config | The functional-area BP admin domains (per module) | Design->Build (when Model BPs / FDM writes are wired) |

O4I/Extend platform enablement itself (MSA Innovation Services opt-in / Maintain Workday Build Company; UMSA automatic) is a separate day-one prerequisite - SKILL.md kickoff checklist + wd-deployment `references/promotion-and-environments.md`.

## Staged provisioning plan (the "as they need it" timeline)

Map these to real dates on the project plan. The **left column is the trigger**, not a hard date - provision when the phase opens so the team has runway to learn.

| Phase | Provision / enable | Why then |
|---|---|---|
| **Kickoff** | Security Partner identified + SLA agreed; Community accounts for all technical counterparts; dev-tenant + developer-site (dev company) accounts requested; O4I/Extend platform opt-in started | Long-lead items; the gatekeeper and the tenants gate everything downstream |
| **Discovery** | Builders (Integrations, Extend) get **read + sandbox** access + their Workday training tracks kicked off; Prism/Reporting get read access to explore existing data sources | They learn the tools and the tenant's data landscape while requirements firm up |
| **Design** | Extend devs get dev-tenant + App Manager + Development; Prism/Reporting get their create/manage domains as the data & reporting design lands; Security Partner sees the design's domain list early (so grants aren't a go-live surprise) | Access matches what each role must now *produce or validate* |
| **Build** | Full build domains per role; ISU/ISSG for integrations; the app's functional-area domains granted as apps deploy to the dev tenant (S22 until then) | Real build work; co-build with the client dev where one is active (wd-extend-dev workflow) |
| **Test / UAT** | Client testers get end-user security; the client team runs alongside E2E/UAT | They exercise the app in their own hands (wd-testing) |
| **Deploy** | Per-tenant re-grant in impl/sbx/prod (access does NOT promote with the app); the tenant-readiness read-set confirms it (wd-deployment) | Every new tenant is a fresh grant; verify, don't assume |
| **Run / hypercare** | Support/admin domains for the ongoing owners; refresh KT for any new admin | Steady-state ownership sits with the client team |

**Provisioning is a quality gate, not a favor:** each phase's access should be confirmed before that phase's work depends on it - the tenant-readiness read-set (`tenant-ops.md`) turns "did the grant activate?" into an assertion, and a missing grant becomes a RAID item, not a silent blocker.

## Enablement - getting each role productive (KT owns this half; continuous)

Access without enablement is a login nobody uses. wd-kt owns the *make-them-productive* path; this model owns *who + what access + when*. For each role, wd-kt (`references/client-dev-enablement.md`, `references/kt-sessions.md`) runs the NS->U->D->R ladder (Not Started -> Understands -> Does-with-help -> Runs-independently) against a named recipient with a teach-back. Role-specific tracks:
- **Extend / Integrations devs:** Workday's own Extend Pro / Integrations Pro learning + certs (the firm may maintain its own recert prep tooling); shadow-then-solo on a real change; the co-build + change-list model in wd-extend-dev `references/workflow.md`.
- **Prism / Reporting:** hands-on in a Prism-enabled sandbox; the read/write patterns in wd-extend-dev `references/prism-and-reporting.md`.
- **Security Partner:** the grant recipes (tenant-task-recipes) as a runbook they own; the per-tenant re-setup matrix.
- All roles: a triage runbook for their surface (wd-kt `references/triage-runbook-pattern.md`) and day-one-for-a-new-admin onboarding.

## Ownership (anti-drift)

- **This file (wd-extend-lifecycle)** owns the role model + staged-access plan - it's part of the methodology and the plan.
- **wd-kt** owns enablement (how we make each role productive) - cross-referenced above, not restated.
- **wd-deployment** (`tenant-task-recipes.md`, `security-setup.md` in wd-extend-dev) owns the grant *mechanics*; this file names *who/what/when*, never the click steps.
- **wd-pm** puts the access milestones on the plan and names owners in the onboarding packet.
- The guided walkthrough surfaces the right slice each phase - see the "technical inputs & client access by phase" thread in [guided-delivery.md](guided-delivery.md).
