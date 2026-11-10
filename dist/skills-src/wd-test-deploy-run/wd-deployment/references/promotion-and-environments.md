# Tenant Promotion & Environments

## The tenant path

```
DEV  ->  IMPL  ->  SBX  ->  PROD
```

- **DEV** (DEVELOPMENT promotion level) - the only level `wdcli app deploy`
  can target. Build, unit test, iterate here.
- **IMPL** (IMPLEMENTATION level) - E2E testing, client validation, data-load
  dry runs. Reached only via `wdcli app promote`, never `app deploy`.
- **SBX** (sandbox) - **refreshed weekly from production.** Anything deployed
  or configured in SBX that hasn't also been migrated to PROD is **wiped on
  the next refresh.** Never treat SBX as a durable staging area; use it for
  prod-like validation immediately before go-live.
- **PROD** - production. Requires Workday's production approval (Volumes
  Questionnaire + Performance Testing, see the SKILL.md main body).

## Promotion is ONE-WAY

There is no demote. Once a version is promoted to a higher level, you cannot
pull it back down - you fix forward with a new version. Plan promotion timing
accordingly: promote only versions that passed the gate below them.

Two doc-confirmed points (per Workday Admin Guide (Integrations), Jul 2026):
- The Dev -> Impl -> Sandbox -> Prod sequence is **enforced sequential** - no
  skipping levels; this is official platform behavior, not house convention.
- Non-Development tenants need the **NSC to enable Extend** on them plus the
  security-domain configuration **before** apps can migrate there - official
  backing for the per-tenant re-setup matrix below.

## Pre-promotion "evaluate" gate - a go/no-go review before EACH hop

Promotion is one-way (above), so the review happens while the version can still be fixed in
place - *before* it leaves the tenant it's in, not after. Before every hop (DEV->IMPL,
IMPL->SBX, SBX->PROD), run a short correctness/security/reliability review of the version and
produce a written **go/no-go**:

- **Security domains & ISU scope** - the app's domains and the ISU/ISSG permissions are the
  *minimum* the flow needs, not broad-grant convenience; no orphan Get/Put the app never
  calls. (Cross-check the re-setup matrix below.)
- **Error handling** - every downstream SOAP/REST node has a guard and surfaces failures
  where a human sees them; silent write-failures are the classic miss (wd-extend-dev
  `references/orchestration.md`).
- **Retry / idempotency** - is replay safe? `Put_*` generally is; `Submit_*` can duplicate.
  State the designed behavior per write op.
- **Reliability paths** - the 25-second page-sync cap and the >100-row BO REST collection
  limit (both owned by wd-extend-dev - orchestration.md and pmd-gotchas.md), plus empty-data
  reads, each have a designed answer, not a hope.

Record the outcome as go/no-go with a named decider, filed with the promotion package. This
**complements, does not replace**, the Volumes Questionnaire + Performance Testing gating
(owned by wd-deployment - see the SKILL.md main body) and the UAT sign-off precondition
below: those gate *capacity and production-readiness*; this is a *code/config correctness
sweep* run per hop. (!) Verify-before-promote - this is a house review discipline
(inspiration: fivetran `evaluate-connector`), NOT a Workday-enforced step; the platform
enforces only the sequential path and the PROD approval docs. Treat the go/no-go as our
standard and confirm the depth each program wants per engagement.

## Who may promote to PROD - and the evidence trail

Promotion to PROD is a controlled change, not a developer convenience:

- **Preconditions in hand before anyone types `promote`:** the UAT sign-off
  artifact (wd-testing `references/uat-support.md` exit criteria) and a client
  change-record ID (whatever the client's change-management process issues).
  No artifact + no change record = no promotion, regardless of schedule
  pressure.
- **The promoter is named per program** and is distinct from the developer who
  built the version - or, where the team is too small to separate them, the
  developer promotes with a named second person countersigning the go/no-go.
  Separation of duties is the point; pick whichever form the program can staff.
- **Emergency path:** an urgent production fix follows the roll-forward
  criteria and named decision-maker in `marketplace-recert.md` section Enhancement
  rollback - with the change record filed **after the fact**, not skipped.
- **Evidence statement:** `wdcli app versions` output + the App Manager
  version history + the initialed cutover checklist together form the
  deployment audit trail. That trio answers "who put what in production,
  when, on whose authority" - keep all three with the deployment package.
- **Studio-deploy SoD cross-link:** deploying a Studio CLAR requires Modify in
  Integration Build (+ Integration Configure); CLARs containing delivery/
  retrieval services additionally need Put in BP Administration / Manage:
  Business Process Definitions / iLoad Web Services - full permission set in
  wd-integration-dev `references/studio.md`. (Per Workday Admin Guide (Workday
  Studio), Jul 2026.)

**SBX access note:** SBX is refreshed weekly **from production**, so it holds
prod data days after refresh - non-prod access to SBX should match prod-grade
controls, not dev-tenant looseness. (!) Confirm the client's actual non-prod
data/access posture per engagement; some clients mask on refresh, many don't.

## Promote by defect, not by raw artifact

Tie the promotion bundle to the **closed UAT defects** it carries, not to a loose list of
files. Tick the defects you worked; resolve each to its artifacts; the union of those
artifacts is what promotes. Two rules make it trustworthy:

- **A logged fix must RECORD its artifacts to be promotable.** A fix with no recorded
  artifact list is not promotable - "what's in this promotion" must trace back to a
  signed-off defect, not to someone's memory of what they touched.
- **Run the target-tenant login in a DEDICATED work dir** so it never clobbers the source
  session's auth state (the same instinct as the machine-global `wdcli whoami` warning in
  wd-extend-dev - a target-tenant token minted in the source session's working directory
  can silently repoint later source commands).

This makes the deployment audit trail (below) answer not just "who put what in production"
but "which sign-off authorized each piece." (adapted from an internal firm skill, 2026-08-28)

## The promotion commands (wdcli specifics live in wd-extend-dev)

The two-or-three commands specific to promotion:

```powershell
# Deploy a built version into a DEVELOPMENT tenant (the only level deploy reaches)
wdcli app deploy <referenceId> -t <dev-tenant-alias> --latest-version

# Promote a deployed version to a higher level (DEVELOPMENT -> IMPLEMENTATION -> ... -> PRODUCTION)
wdcli app promote <referenceId> ...

# Confirm what's where
wdcli app versions <referenceId>
```

Key behaviors (verified):
- `app deploy` **only targets DEVELOPMENT tenants.** To get an app into an
  IMPL tenant (`<impl-tenant>`), deploy to the DEV tenant first
  (`<dev-tenant>`), then `wdcli app promote` the version up.
- `app deploy` always prompts for a tenant interactively even with `--ci` -
  pass `-t <tenant-alias>` explicitly or it hangs.
- For everything else (auth, upload/build loop, `-f json --ci` scripting
  flags), defer to **wd-extend-dev**.

## (!) The app is not the whole deployment

**The Integration System and any RaaS custom reports promote SEPARATELY from
the app.** Promoting the app alone leaves an integration unrunnable in the
target tenant - the flow exists but its Integration System registration and
the custom reports it calls do not. Treat every promotion as a bundle:

1. The app version (`wdcli app promote`)
2. The Integration System configuration (tenant-side)
3. Every RaaS custom report the app or its orchestrations call (migrated /
   rebuilt in the target tenant, web-service-enabled, same name)
4. Any Integration Maps, CredStore entries, or scheduled launch configs

Verify each item exists in the target tenant before declaring the promotion
done. Items beyond the app itself are checkable live via tenant-ops (RaaS
responds under the ISU, RefIDs resolve, config reads) - run the read-set per
hop instead of eyeballing (wd-extend-dev references/tenant-ops.md).

## Per-tenant re-setup matrix

Deploying/promoting the app binary is the *smallest* part of standing it up
in a new tenant. After the FIRST deploy to **any** new tenant, expect all of
the following, every time:

| Item | Symptom if skipped | Who does it |
|---|---|---|
| **Security domain grants** | Every BO data call returns **S22 "permission denied"** (pages may load; data won't) until a tenant admin grants the app's security domains: Domain Security Policies -> find the app's domains -> add security group with **View + Modify** and integration **Get + Put** -> **Activate Pending Security Policy Changes** | Tenant security admin |
| **ISU / ISSG** | Orchestration SOAP/REST calls fail auth. Provision an ISU + ISSG with the required domain Integration Permissions (Get/Put), map to the app's `_DEFAULT_WORKDAY_CREDENTIAL` | Tenant security admin |
| **API client + refresh token** | External/BO REST callers can't mint tokens. Register a Workday API Client, create a refresh token, note the REST endpoint - per tenant | Tenant security admin |
| **App Attributes** | Pickers/queries silently return nothing or wrong data - attribute defaults hold the *previous* tenant's WIDs. Instance WIDs (org subtypes, config references) differ per tenant; override in App Manager -> App Attributes | App admin / you |
| **BP definitions & approver chains** | BPs route to no one, or to the default single step. The Extend file declares only a single approval step; the real multi-step approver chain + initiation security is configured on each BP definition in-tenant | Tenant BP admin |
| **Security group assignments** | Users can't see pages / initiate. Role-based groups must exist and have real members in this tenant | Tenant security admin |
| **Scheduled orchestrations / launch configs** | Batch flows never run | App admin |
| **Searchable custom task** (apps with a home page - house standard) | Users can't FIND the app by name in Workday search; adoption drags on App-Manager directions and bookmarks. Source-side `.task` files deploy with the app (only the domain grant is needed); tenant-created custom tasks must be RE-CREATED per tenant - recipe R12 in tenant-task-recipes.md | App admin / tenant admin |

Rule of thumb: **the tenant setup guide** (see
`references/tenant-setup-guide.md`) is the deliverable that walks a client
admin through this matrix in order. Write one per app; reuse it per tenant.

## Kickoff-stage environment prerequisites

(Cross-linked from wd-extend-lifecycle - confirm these at project kickoff,
because the lead times bite at deployment time.)

- **Extend SKU / Innovation Services** confirmed on the customer's Workday
  contract - no Extend deployment without it. The concrete O4I opt-in path
  (per Workday Admin Guide (Integrations), Jul 2026): **MSA** customers opt in
  via the **Innovation Services and Data Selection Opt-In** report (Available
  Services -> WCP -> "Workday Orchestrate for Integration"), then run **Maintain
  Workday Build Company for Orchestrate for Integration** to name the Developer
  Site company admin. **UMSA** customers have it automatically - no Innovation
  Services tasks exist in UMSA tenants (their absence is not a problem).
- **Entitlements dashboard** = the contract thresholds (production app count,
  data transfer, users, dev tenants) - check it against the program plan at
  kickoff. Analytics-dashboard log files are **permanently deleted after a
  retention period** (length unspecified) - pull any usage evidence you need
  before it ages out. (Per Workday Admin Guide (Integrations), Jul 2026.)
- **Developer tenant access + App Manager access** for the build team, in the
  customer's org (example: apps created with `-a <org-short-id>` under the
  customer's developer account, deployed to their DEV tenant).
- **Workday Community accounts** for everyone who needs API docs / support
  cases.
- **Client security-admin lead times** - every row of the re-setup matrix
  above that says "tenant security admin" is a request into the client's
  queue, and those requests **often take 1-2 weeks each**. Batch them, submit
  them early, and sequence the tenant-setup guide so the long-lead items go
  in first.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live:

- **Tenants** - the DEV tenant alias (deploy target: `-t <dev-tenant-alias>`)
  and the IMPL tenant alias(es) (E2E). Same pair for every app in the program.
- **Developer org short ID** - the org the apps are created/deployed under;
  switch orgs with `wdcli account switch`, confirm with `wdcli whoami`.
- **Account authorization quirks** - e.g. whether `wdcli app validate` is
  authorized on the program's developer account; if it isn't, use
  `wdcli app upload` (the build) as the validator.

Precedent (generic): an app deployed to the DEV tenant, then promoted toward an
IMPL tenant; after the first deploy the security domains needed granting in each
tenant before any BO data call worked.

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).
