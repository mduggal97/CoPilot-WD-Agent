# Config execution - driving the setup recipes in the browser

How this skill executes wd-deployment tenant-task-recipes.md (R1-R12) through the Browser
pane. The recipe CONTENT - every step, field, and "you're done when" - is owned by
wd-deployment; this file is only the browser-level EXECUTION and the tier each recipe runs
at. Read (references/safety-and-scope.md) first; it defines the tiers used below. Browser
tool map, selectors, waits, and evidence conventions are shared - see wd-test-execution
browser-mechanics.md; do not re-learn them here.

## The execution loop

Run this loop per recipe. Steps 1-2 are one-time per session; 3-8 repeat per recipe.

1. **Confirm tenant identity** (environment gate, safety-and-scope.md): read the Browser
   pane URL host and cross-check with `wdcli whoami` + a tiny tenant read. Dev/sandbox
   only. Do not proceed to any write until this passes.
2. **Login handoff.** The Browser pane has no SSO session. Emit the USER-ACTION login block
   (wd-auth mfa-and-browser-auth.md) and wait for "done". Never type a credential or MFA
   code. Re-handoff if the session drops mid-loop (you will see a login screen on `read_page`).
3. **Pick the recipe.** Cite the R# in wd-deployment tenant-task-recipes.md - do not restate
   its steps. Follow that recipe's dependency order (R3 before R4; R2 after every grant; R5
   after R3/R4).
4. **Navigate via global Search to the exact task name.** Click the Search control, type the
   task name the recipe gives (e.g. `Create Integration System`), open the result. Some
   recipes are reached through App Manager or a related-action menu, not Search (R8, R12,
   R10) - noted per recipe below.
5. **Fill non-committal fields FOR REVIEW** (Tier 1). Use `form_input` / `computer` type to
   populate the form to the recipe's values, then STOP before the committing click.
6. **Present the confirm-each-write block** (Tier 2 recipes) OR the prepare-and-hand-to-user
   steps (Tier 3 recipes). See safety-and-scope.md confirm-each-write protocol. For Tier 3,
   you lay out the exact click sequence and values on the now-filled screen; the user commits.
7. **Commit.** Tier 2: on the user's yes, make the single committing click. Tier 3: the user
   clicks; you do not.
8. **Read-back evidence.** Re-read the object / run the recipe's "you're done when" check /
   screenshot the after-state. Record it (see Evidence trail). Then next recipe.

Worked confirm-each-write block (what step 6 looks like in chat for a Tier 2 write):

```
Ready to commit this write - confirm before I click:
  Task:    Create Integration System (Workday Search)
  Fields:  System Name = INT_ExpenseSync_Inbound
           System ID   = INT_ExpenseSync_Inbound
           Template    = Orchestrate Integration Template
           Orchestration = ExpenseSync_Inbound_Orch
  Target:  <dev-tenant alias> (confirmed dev, identity checked this session)
  On yes:  I click OK, then run the read-back (re-open the system, confirm it
           points at the orchestration).
Reply "yes" to commit this one write, or tell me what to change.
```

Wait for the yes. One yes = this one write only; the ISU-map that follows gets its own block.

## Per-recipe execution notes (browser level + tier)

One line each: how it is driven, its tier, the exact task to search, and the read-back that
proves it. Steps live in wd-deployment tenant-task-recipes.md - cited, not repeated. Any
field names or values below are ORIENTING HINTS (so you know you are on the right screen);
the authoritative field-by-field values are in the cited R# and WIN on any conflict - read
the recipe before committing, do not treat these one-liners as the spec.

- **R1 - Grant a security domain to a security group.** Tier 3 (HAND TO USER - security).
  Search `Maintain Permissions for Security Group` (or open the domain via `View Security
  for Securable Item` -> Domain -> Edit Security Policy Permissions). You navigate + fill
  the group and access levels for review; the user clicks OK. Read-back: re-open the domain
  policy and confirm the group appears with View+Modify and Get+Put (then R2).
- **R2 - Activate Pending Security Policy Changes.** Tier 3 (HAND TO USER - security). Search
  `Activate Pending Security Policy Changes`. You show the pending list and a suggested
  Comment; the user clicks OK then Confirm. Read-back: the pending list is empty AND the
  gated data call now returns data (S22 gone).
- **R3 - Create an Integration System User.** Tier 3 (HAND TO USER - an ISU is a security
  principal; also involves a password = prohibited to type). Search `Create Integration
  System User`. You fill User Name, Do Not Allow UI Sessions, Session Timeout 0; the USER
  sets the generated password and clicks OK, then adds the ISU to `Maintain Password Rules`
  exempt list. Read-back: search the user, confirm no-UI + on the exempt list.
- **R4 - Create an ISSG, add the ISU, grant its domains.** Tier 3 (HAND TO USER - security).
  Search `Create Security Group`, then `Maintain Permissions for Security Group`. You fill
  type/name/members/domains for review; the user commits and runs R2. Read-back: the ISU
  shows as a member and the integration's first call clears 403.
- **R5 - Create the Integration System + map the ISU credential.** Tier 2 (DRIVE-AND-
  CONFIRM - non-security config; the ISU it maps was already created via R3). Search `Create
  Integration System`. Fill System Name/ID, template `Orchestrate Integration Template`,
  point at the orchestration; confirm-each-write before OK. Then related action `Workday
  Account -> Edit` to add the ISU - a second confirm-each-write. Read-back: the system
  points at the orchestration and shows the ISU as run-as.
- **R6 - Register API Client + Refresh Token.** Tier 3 (HAND TO USER - issues credentials).
  Search `Register API Client for Integrations`. You fill Client Name, ISU, scope, timeout
  for review; the USER clicks OK and copies the Client ID / Secret / Refresh Token (shown
  once - never paste into chat). Read-back: the client appears in `View API Clients`; the
  user confirms a token mint succeeds out-of-band.
- **R7 - Business Process definition / approver chain.** Tier 3 (HAND TO USER - BP
  security). Search `Edit Business Process` for the app's custom BP. You lay out the ordered
  steps/groups and initiation security per the design doc; the user saves. Read-back: submit
  a test instance and confirm it routes to the configured first approver's inbox.
- **R8 - Set an App Attribute.** Tier 2 (DRIVE-AND-CONFIRM - non-security config). Reached
  through `App Manager` -> open the app -> Configure -> App Attributes (NOT tenant Search).
  Find this tenant's WID via a WQL read (Tier 1) first, then fill the attribute; confirm-
  each-write before Save. Read-back: re-read the attribute value and exercise a dependent
  feature (a filtered picker returns correct data).
- **R8b - Integration Attributes (developer task).** Tier 2 (DRIVE-AND-CONFIRM). On the
  integration system, related action `Configure / Maintain Integration Attributes`. Names
  must match `intsys.stringAttributeValue("<exact name>")` exactly. Treat token values as
  credentials - do NOT type secret values; leave `TBD` and hand secret entry to the user.
  Read-back: re-read each attribute; confirm exact-name match.
- **R9 - SSH & PGP keys.** Tier 3 (HAND TO USER - key material is credential-grade, and the
  not-migratable private pairs must be created in the master/prod tenant, out of this
  skill's dev/sandbox scope). You point the user at `Create x509 Private Key Pair` /
  `Create PGP Private Key Pair` etc. and the migratable-vs-not table; the user creates them.
  Read-back: the key appears in the matching `View ... Key` report.
- **R10 - Integration Notifications.** Tier 2 (DRIVE-AND-CONFIRM). On the integration
  system, related action `Configure Integration Notifications`. Fill trigger statuses,
  recipients, subject/body; confirm-each-write before Save. Read-back: the notification
  config lists the correct trigger statuses and distribution list.
- **R11 - Schedule / Launch the integration.** Tier 2 (DRIVE-AND-CONFIRM), with care. Search
  `Launch / Schedule Integration`. A validation-mode Launch is still a write - confirm it.
  Do NOT drive a PROD schedule (production is never a target); dev/sandbox test runs and a
  disabled schedule definition only. Read-back: open the event via `Process Monitor`,
  confirm INFO/summary and NO ERROR messages.
- **R12 - Create Custom Task.** Tier 2 (DRIVE-AND-CONFIRM). Search the tenant for `Create
  Custom Task` first (Sep 2026); if absent, `App Manager` -> Configure -> Configurations tab ->
  Create Custom Tasks tile (2026-08-05) - both routes in R12. Fill Title, Route Path and the
  security Domains, and turn Testing Mode Only OFF (it defaults on - R12 trap);
  confirm-each-write before Save. Read-
  back: as a non-admin test user, search the app name and confirm the task lands on Home.
  (House first: a shipped `.task` file often removes the need for this - see wd-extend-dev
  model.md; if you are hunting for a Business Object value just to make a plain launcher,
  that is the tell to ship a `.task` file and redeploy instead.)
- **Sequence generators (FDM ID pre-assignment).** Some apps expect a tenant sequence
  generator to exist for human-readable IDs. There is no R# recipe for it yet - treat it as a
  Tier 2 config object (`Create Sequence Generator` / `Edit Tenant Setup`) but confirm the exact
  naming with wd-integration-dev integration-naming.md, and flag it as a recipe gap to
  wd-deployment tenant-task-recipes.md if you hit it.

**Domain shape a new app usually needs (verified norm):** two domains - a DATA domain (all
groups View+Modify, ISU Get+Put) and PAGE domains split by persona (a manager group holds the
manage-pages domain, a specialist group the specialist-pages, admin the admin-pages). Simple
apps can be single-domain. This is what the R1 grants (below) target. Inline-seed-data pages
render BEFORE any grant (no BO call), so a demo page can show something even pre-S22 - but any
BO-backed page stays S22 until the grant + Activate Pending.

## The S22 setup sequence in practice

After the first deploy (or any `app copy`), BO data calls return S22 permission-denied
until the app's domains are granted and Activated Pending (wd-extend-dev model.md, the S22
rule). The canonical new-app setup this skill drives end to end, with the security commits
handed to the user:

1. Confirm the app deployed (Tier 1 read) and the target security group exists.
2. **R1** grant each app domain to the group - Tier 3, user commits.
3. **R2** Activate Pending - Tier 3, user commits.
4. **R7** configure each custom BP definition - Tier 3, user commits.
5. **R8** set each per-tenant App Attribute (WID via WQL) - Tier 2, drive-and-confirm.
6. **R6** register the API Client if external REST/WQL is needed - Tier 3, user commits.
7. Run THE TENANT-READINESS READ-SET (wd-extend-dev tenant-ops.md): BO data returns data
   not S22; every design-doc RefID resolves; App-Attribute WIDs are this tenant's; RaaS
   under the ISU works. The pass/fail set IS the gate evidence.

Confirm tenant identity before step 2. The security steps (R1/R2/R7/R6) are all Tier 3 - you
prepare and read back; the user commits.

## Evidence trail

Every committed change gets a confirming read-back recorded in the session. That record
doubles as the wd-deployment tenant-setup deliverable evidence and populates the
wd-deployment security-setup-section.md domain table (which group holds which domain at
which access). Capture, per change: the task, the values committed, the target instance,
and the read-back result (a screenshot or a read query output). A change with no read-back
is not done - it is unverified.

## Read-back techniques (proving a change took)

The read-back is Tier 1 (free) and mandatory after every commit. Pick the cheapest one that
actually proves the recipe's "you're done when":

- **Re-open the object in the UI** - re-search the task/object and screenshot the after-
  state (the domain policy shows the group; the integration system shows the ISU as run-as).
- **Run a tenant read** - a WQL SELECT or a BO REST GET via wd-extend-dev tenant-ops.md
  (e.g. after R1+R2, GET the app's BO collection and confirm data returns instead of S22).
- **Exercise the dependent feature** - after R8, open the page whose picker depends on that
  attribute and confirm it returns the right instances.
- **Check the pending/empty state** - after R2, confirm the pending-changes list is empty.

A screenshot alone that shows a "success" toast is not a read-back - it proves the click,
not the effect. Read the resulting state.

## When to STOP driving and use a script/EIB instead

The browser is for interactive setup and one-off config, not a loader. Stop and hand off
when the work is repeatable or bulk:

- Anything you will re-run (re-seed after a deploy - a deploy can wipe dev data) -> a
  repeatable seed script (wd-extend-dev tenant-ops.md seed/wipe, wd-testing automation-
  harness.md).
- Bulk config or data (dozens+ of records/attributes) -> EIB (wd-integration-dev eib.md)
  or an API seed loader (wd-extend-dev tenant-ops.md write-side catalog).
- Standing/unattended loads the CLIENT will own -> EIB, per wd-extend-dev tenant-ops.md.

Test-data specifics (what to create in-tenant vs hand off) are in (references/test-data.md).
