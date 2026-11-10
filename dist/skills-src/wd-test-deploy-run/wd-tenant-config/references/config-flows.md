# Config flows - named, browser-executable tenant configuration procedures

A **config flow** is a named, ordered, browser-executable procedure that orchestrates the
R# recipes plus native admin tasks into a whole configuration objective - "stand up an app's
security", "set up an integration system", "make a report a web service". You do not figure
config out on the fly; you pick the flow that matches the objective and walk its steps.

Each step carries one of the THREE TIERS this skill runs on (full rulebook:
(references/safety-and-scope.md)):

- **[FREE]** - navigate, search, open a task, read_page, screenshot, fill-for-review. No ask.
- **[CONFIRM-EACH-WRITE]** - a non-security config write or a test record: present the exact
  task + field values, wait for one clear yes in chat, then the single committing click.
- **[HAND-TO-USER]** - security/system settings, credentials, deletion, OAuth: you navigate
  and lay out the exact click sequence and values; the USER commits; the read-back is yours.

The recipe CONTENT (every click, field, "you're done when") is owned by wd-deployment
tenant-task-recipes.md (R1-R12); these flows CITE R# and never restate it. The per-recipe
browser-execution notes + the confirm-each-write block template live in
(references/config-execution.md). Browser-driving technique is wd-test-execution
browser-mechanics.md.

**Exemplar bar (wd-extend-dev standards.md):** each flow is a north-star reference - reusable,
cited to its source manual, leaving a read-back evidence trail someone else can reconstruct
the tenant setup from. A flow that runs but leaves no read-back is not done.

**Nav caveats (browser-mechanics.md) that bite the marked steps below:** a **hung prompt** -
Escape, re-read_page, retype a shorter exact term, clear via the field X (not Ctrl+A); a
**"No Items" picker** is often a timing artifact - type -> Enter -> wait 2-3s before concluding
empty (financial pickers are also security-gated by the signed-in worker); **grids with row
action buttons / in-cell config** - act by row-scoped ref one row at a time, re-read_page
between rows, never batch a committing click.

---

## Flow 1 - Stand up an Extend app's security end-to-end (S22 -> data flowing)

**Purpose:** take a freshly deployed Extend app from S22 "permission denied" on every BO data
call to data rendering, with the persona-split domain model in place.

**When to use:** after the first deploy to a tenant, and after every `wdcli app copy` (a copy
is a new app with new domains - wd-extend-dev model.md, the S22 rule).

**Prerequisites:** app deployed (Tier 1 read); target security groups exist (Flow 2 if not);
tenant identity confirmed dev/sandbox (URL host + `wdcli whoami` + a tiny read).

**Steps:** follow the dependency order + task labels in wd-deployment tenant-task-recipes.md
(R1 -> R2 -> R8); this flow adds only the tier and the read-back per step:
1. **[FREE]** Enumerate the app's domains (one per `.securitydomain`). Verified norm: a DATA
   domain (all groups View+Modify, ISU Get+Put) and PAGE domains split by persona (manager ->
   manage-pages, specialist -> specialist-pages, admin -> admin-pages).
2. **[HAND-TO-USER]** Grant each domain to its group (**R1**). You fill group + access for
   review; user clicks OK. Read-back: re-open the policy, confirm the group at the right access.
3. **[HAND-TO-USER]** Activate (**R2**). You show the pending list + a Comment; the user clicks
   OK then Confirm. Read-back: pending list empty.
4. **[FREE]** Prove S22 gone: GET the app's BO collection (or open a BO-backed page); data
   returns instead of S22. This read-back IS the flow's gate.
5. **[CONFIRM-EACH-WRITE]** Set per-tenant App Attributes (**R8**), WID from a Tier 1 WQL read
   first. Read-back: a picker filtered by that attribute returns this tenant's instances.

**Pitfalls:** the Activate (step 3) is the most-forgotten step - a granted-but-unactivated
domain looks identical to no grant (still S22). Inline-seed pages render pre-grant (no BO
call) and fool you into thinking security is fine. Union rule: a target user also in an
unconstrained group on the same domain silently loses the constraint. App Attributes left at
build-tenant defaults make pickers come back EMPTY with no error - verify the WID is THIS
tenant's.

**Non-browser alternative (dev/sandbox, bulk):** `wd-extend-dev/scripts/security_domain_discovery.py`
auto-enumerates the domains + BP permissions an app or integration needs (step 1), and
`security_domain_apply.py` applies the grants (steps 2-3) via a guarded SOAP path (dry-run default,
per-item backup, never activates). Use it for a bulk grant instead of clicking each; see the security
ownership map in wd-deployment `references/security-role-design.md` and the safety model in wd-extend-dev
`references/domain-apply-safety.md`.

**Source:** tenant-task-recipes.md R1/R2/R8; wd-deployment configurable-security-admin.md (activation
asymmetry + union rule); wd-extend-dev model.md (the S22 rule). This flow is the interaction-tier cut
of the security core; the CANONICAL full new-app sequence (adds R7 group creation, R6 API-client
registration, and the tenant-readiness read-set as the gate) is OWNED by config-execution.md "The S22
setup sequence in practice" - keep the two in step via that file.

---

## Flow 2 - Create and configure a security group

**Purpose:** create the right TYPE of group, place it on the domain / BP policy it needs, and
activate - the building block Flows 1, 3, 5, 6 assume exists.

**When to use:** when an app, BP, or integration needs a group the client has not provisioned.

**Prerequisites:** you know the group's PURPOSE (who becomes a member; what TARGET constraint
it must enforce); tenant identity confirmed.

**Steps:**
1. **[FREE]** Choose the type from the group-type table (wd-deployment configurable-security-admin.md):
   Role-Based (default for scalable end-user access), User-Based (always UNCONSTRAINED; small
   admin populations), Integration System (ISUs only; Flow 5), Aggregation/Intersection to
   combine. Decide **constrained vs unconstrained** (a subset of instances vs all).
2. **[HAND-TO-USER]** Create it - `Create Security Group`, set Type + Name for review; user
   clicks OK. Read-back: search the group, confirm its type.
3. **[HAND-TO-USER]** Place it on the domain policy (**R1**) or BP policy (Flow 3) at the
   needed access; user commits.
4. **[HAND-TO-USER]** Activate (**R2**) the POLICY placement. Asymmetry: adding a MEMBER is
   immediate (no activation); placing the group ON a policy is staged until Activate.
5. **[FREE]** Read-back: `Start Proxy` as a real member (non-production only), test POSITIVE
   and NEGATIVE access.

**Pitfalls:** union rule - one unconstrained membership on a domain bypasses every constrained
restriction on it; adding a segment-based group means REMOVING the base groups from that
policy or segmentation is bypassed. Groups can never be deleted once used - inactivate. The
permission grid is a row-action grid: act by row-scoped ref, one row at a time. Forgetting
Activate (step 4) leaves the placement inert.

**Source:** wd-deployment configurable-security-admin.md (group-type table, activation asymmetry, union rule);
tenant-task-recipes.md R1/R2.

---

## Flow 3 - Configure a business process end-to-end

**Purpose:** turn a BP type into a working definition - ordered steps, legal condition rules,
notifications, and the BP security policy - so a submitted event routes and commits correctly.

**When to use:** once per custom BP, per tenant, after deploy (**R7**); or adjusting a native
BP (Hire, Change Job) definition.

**Prerequisites:** app deployed; approver/initiator groups exist (Flow 2); tenant identity
confirmed. Read `Business Process Configuration Options` FIRST for the type's allowed step
types (wd-deployment bp-configuration-admin.md).

**Boundary:** this configures NATIVE tenant BPs and the tenant-side definition of an Extend
app's custom BP. A Model BP defined on an Extend business object in SOURCE is wd-extend-dev
model-bp.md - do not reconfigure model-owned routing here.

**Steps:**
1. **[FREE]** Open the definition - `Edit Business Process` (prefix `bp:` finds definitions),
   or Related Actions -> Business Process -> Edit Definition.
2. **[HAND-TO-USER]** Build the step order (**R7**). Steps are LETTER-ordered (a, b, ba, bb, c)
   so you insert without renumbering; Initiation is always "a"; exactly ONE Completion step
   (data commits there) and every Approval/Review step comes BEFORE it. You lay out each step +
   group; the user saves.
3. **[HAND-TO-USER]** Add condition rules only where legal: Entry (all except Initiation),
   Validation (Initiation + Action ONLY), While Running / Exit (Approval Chain family; Exit
   also on Integration steps). User commits.
4. **[CONFIRM-EACH-WRITE]** Configure notifications (status change or step entry/exit). If the
   BP has BP-level notifications, prefer those over integration notifications (avoid duplicates).
5. **[HAND-TO-USER]** Set the BP security policy (initiate / approve / deny / delegate / view
   all / cancel / rescind / manually advance, per group). BP policy edits are STAGED.
6. **[HAND-TO-USER]** Activate (**R2**) the staged BP policy edits; user commits.
7. **[FREE]** Read-back: submit a test instance (Flow 6 persona); confirm it routes to the
   configured first approver's inbox.

**Pitfalls:** a definition with ERRORS is silently SKIPPED and the default runs instead - check
`Business Process Exception Audit` when a custom definition "isn't used". One denial denies the
ENTIRE process; an Integration-step failure terminates the BP; a step on an empty group stalls
(`Unassigned Tasks`). The policy's Security Groups multi-select is a native category prompt
that RESISTS the driver - use the suspected recipe in browser-mechanics.md and verify live, or
hand the field entry to the user. Forgetting Activate (step 6) leaves the policy inert.

**Source:** wd-deployment bp-configuration-admin.md (step letters, completion-step rule, condition legality,
exception-audit); tenant-task-recipes.md R7/R10/R2.

---

## Flow 4 - Create a custom report + calculated field + enable as RaaS

**Purpose:** author an Advanced report with a calculated field and expose it as a web service
(RaaS) an integration or external caller can consume.

**When to use:** an app/integration needs a report-driven feed, an alert condition, or a RaaS
endpoint; or a design doc calls for a custom report deliverable.

**Prerequisites:** the author holds `Analytics Data: Report Fields and Values` plus the data
source + every report field's domain (the three-part report access test,
wd-deployment configurable-security-admin.md); tenant identity confirmed.

**Steps:**
1. **[FREE]** Confirm the PBO first - the PRIMARY BUSINESS OBJECT LOCKS once chosen; you swap
   data sources only WITHIN the same PBO. Wrong PBO = rebuild. Use `Business Object Details`.
2. **[CONFIRM-EACH-WRITE]** `Create Custom Report`, Type = **Advanced** (shareable + RaaS-
   capable; Simple is neither). Pick the smallest data source with the data (indexed at
   volume). Read-back: the report opens on the chosen PBO.
3. **[CONFIRM-EACH-WRITE]** Add a calc field at the right SCOPE: report-level
   (`Create Calculated Field for Report`, domain `Private Calculated Fields Management`) for
   one report; system-wide (`Create Calculated Field`, domain `Custom Field Management`) only
   if reused. A calc field NEVER widens data access. Read-back: it returns values in preview.
4. **[CONFIRM-EACH-WRITE]** Add prompts, columns, sort, filter - push conditions into
   data-source filters/subfilters before calc-field conditions (performance).
5. **[CONFIRM-EACH-WRITE]** Enable as a web service: Advanced tab -> **Enable as Web Service**
   (Matrix reports CANNOT be web-service-enabled - Advanced only). Read-back: a RaaS endpoint
   appears; note the 2 GB integration-payload cap.
6. **[CONFIRM-EACH-WRITE]** Share deliberately (don't share / all authorized / specific groups
   + users). You can only share with users who can access the data source + filter; an ISU
   consumer needs the data source + field domains like any user (Flow 5).

**Pitfalls:** a missing FIELD domain does not error - the field returns SILENTLY BLANK or a
constrained subset (three-part access test). The PBO lock (step 1) is the costliest mistake. A
calc field or report in use cannot be deleted - deprecate a calc field with the `Do Not Use`
label. Shared SCHEDULED output BYPASSES standard security - a data-disclosure decision. Field
pickers are async - type -> Enter -> wait before concluding "No Items".

**Source:** wd-extend-dev report-writer-admin.md (PBO lock, hard-limits, calc-field scopes,
RaaS 2 GB); model.md (calc-field type selector for Extend BOs); report-administration manual
(if scheduled).

---

## Flow 5 - Set up an integration system for an O4I / integration

**Purpose:** stand up everything a scheduled O4I integration needs to run as a service
identity with the right access - in strict dependency order, credentials handed to the user.

**When to use:** deploying an O4I orchestration to a tenant that must run/schedule as an ISU.

**Prerequisites:** orchestration deployed (Step 0); tenant confirmed dev/sandbox; you hold
security-administration access. Order is load-bearing and owned elsewhere - follow the
dependency order + task labels in wd-deployment tenant-task-recipes.md (the R9/R3/R4/R2/R5/
R8b/R10/R11 chain); the tier tags + read-backs per step below are this flow's.

**Steps:**
1. **[HAND-TO-USER]** (file integrations only) Create SSH/PGP keys (**R9**). Not-migratable
   private pairs must be created in Production/master - out of dev/sandbox scope; point the
   user at the create tasks + the migratable-vs-not table.
2. **[HAND-TO-USER]** Create the ISU (**R3**) - `Create Integration System User`. You fill User
   Name, `Do Not Allow UI Sessions`, Session Timeout 0; the USER sets the password, clicks OK,
   and adds the ISU to the `Maintain Password Rules` exempt list. Read-back: no-UI + on the
   exempt list.
3. **[HAND-TO-USER]** Create the ISSG, add the ISU, grant its domains (**R4**). Find the
   securing domain via `View Security for Securable Item` on the web-service operation - never
   guess; Get implies View, Put implies Get; do NOT blanket-grant Integration Build/Debug. User
   commits.
4. **[HAND-TO-USER]** Activate (**R2**) the domain grants (adding the ISU as a MEMBER was
   immediate; grants are staged). Read-back: the first call clears 403.
5. **[CONFIRM-EACH-WRITE]** Create the Integration System (**R5**) - `Create Integration
   System`, template `Orchestrate Integration Template`, point at the orchestration; then
   Related Actions -> Workday Account -> Edit to add the ISU as run-as (a SECOND confirm).
   Read-back: system points at the orchestration and shows the ISU.
6. **[CONFIRM-EACH-WRITE]** Fill Integration Attributes (**R8b**, developer task) by EXACT name
   (`intsys.stringAttributeValue("...")` must match). Leave secret/token values `TBD` and HAND
   secret entry to the user - do not type secrets.
7. **[HAND-TO-USER]** (external REST/WQL) Register API Client + refresh token (**R6**) -
   `Register API Client for Integrations`. The USER clicks OK and copies Client ID / Secret /
   Refresh Token (shown once - never paste into chat). Not migratable - create in master.
8. **[CONFIRM-EACH-WRITE]** Notifications (**R10**) - Failed/Aborted and Completed with Errors
   to the support distribution list.
9. **[CONFIRM-EACH-WRITE]** Schedule / launch (**R11**) - dev/sandbox only, validation-mode
   first (a validation Launch is still a write); never a PROD schedule. Read-back:
   `Process Monitor` shows INFO/summary, NO ERROR.

**Pitfalls:** wrong order is the #1 false alarm - R3 before R4, R2 after every grant. An ISU
password that expires silently kills nightly runs (the exempt list, step 2). API clients +
not-migratable keys are ABSENT in a promoted tenant unless created in master. A schedule is
OWNED by its user - Run As User = the ISU, or a departed owner breaks it. WSU window: in-flight
runs auto-restart (double-load risk).

**Source:** tenant-task-recipes.md R3/R4/R5/R6/R8b/R9/R10/R11/R2; wd-deployment configurable-security-admin.md
(ISU/ISSG mechanics, find-the-domain, over-privilege warning).

---

## Flow 6 - Create test-data personas + proxy for testing

**Purpose:** create the synthetic worker(s) a persona-scoped test needs with the right
security, then hand off to Proxy / Sign In As so the test runs AS the correct worker.

**When to use:** a wd-test-execution scenario's precondition names a persona (a manager,
specialist, financial worker) the delivered demo population does not already provide.

**Prerequisites:** synthetic-data-only (safety-and-scope.md; test-data.md) - realistic-shaped
but fake, no real PII; PREFER the delivered demo population as targets over creating people;
tenant confirmed dev/sandbox.

**Steps:**
1. **[FREE]** Check whether a delivered demo worker already fits (WQL read / search). Reuse if
   so - fewer PII surfaces, no cleanup. Create only when the scenario needs a worker that does
   not exist.
2. **[CONFIRM-EACH-WRITE]** Seed foundation first if the Hire needs it (dependency order,
   test-data.md): `Create Supervisory Organization`, `Create Position`, `Create Cost Center` -
   each its own confirm + read-back. Security-neutral DATA (Tier 2), not the Tier 3 security
   recipes.
3. **[CONFIRM-EACH-WRITE]** Create the worker via `Hire` (runs the Hire BP - confirm EACH inbox
   step's committing click). Fill synthetic values for review first. Read-back: search the
   worker, confirm active.
4. **[HAND-TO-USER]** Give the worker the test's security - place them in the role/group (Flow
   2 / R1 / R2); activate group-on-policy edits. Read-back: `View Security Groups for User`
   shows the group.
5. **[FREE]** Proxy handoff - `Start Proxy` -> type the worker name -> **press Enter to CHIP
   the name** (required) -> OK; the proxied worker's security governs what the app sees;
   `Stop Proxy` to end. Read-back: the persona-gated pages/pickers now populate.

**Pitfalls:** `workers/me` returns S21 for implementer/admin accounts (no Worker record) -
Start Proxy as a real worker. Financial pickers (Fund, Balancing Unit) are security-gated - an
HR-only worker sees "No Items" though data exists; use a financially-secured worker. Boolean-
Active gotcha (model.md): an unset `active` stores `false` not null, so a record vanishes from
filtered lists - read-back must confirm present AND Active. A deploy can wipe app BO test data -
check and re-seed after every `wdcli app deploy` (native-task foundation data is NOT wiped); if
re-creating the same records post-deploy, STOP and hand off to a seed script.

**Source:** (references/test-data.md) (patterns, seeding order, synthetic rules, cleanup);
browser-mechanics.md (proxy pattern, chip-the-name, gated pickers); wd-extend-dev model.md
(boolean-Active gotcha).

---

## How to use a flow in a session

1. **Pick the flow** matching the objective ("set up the tenant" -> Flow 1 or 5; "grant the
   security" -> Flow 1/2; "configure the BP" -> Flow 3; "make a report a web service" -> Flow
   4; "seed a test worker" -> Flow 6).
2. **Confirm tenant identity BEFORE the first write** - dev/sandbox only, via URL host AND
   `wdcli whoami` (org matters, not just tenant) AND a tiny tenant read. Re-run both on any
   host change (environment gate, safety-and-scope.md).
3. **Login handoff** - invoke wd-auth, emit the USER-ACTION login block, wait for "done". Never
   type a credential or MFA code; re-handoff if the session drops.
4. **Walk the steps honoring each tier** - [FREE] freely; [CONFIRM-EACH-WRITE] one yes per
   write via the confirm-each-write block (config-execution.md); [HAND-TO-USER] you prepare and
   read back, the user commits. Record the read-back after every commit - the evidence trail IS
   the tenant-setup deliverable.
5. **When the work turns repeatable or bulk, STOP** and hand off to a seed script / EIB / API
   loader (config-execution.md, "When to STOP driving"). The browser is for interactive,
   one-off config, not a loader.
