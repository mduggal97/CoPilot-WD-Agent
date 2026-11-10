# Test data - creating synthetic records in-tenant via the browser

How this skill creates the test data a scenario needs, through the Browser pane, in a
dev/sandbox tenant, one confirmed write at a time. Read (references/safety-and-scope.md)
for the tiers and the synthetic-data rule; browser mechanics are shared - see
wd-test-execution browser-mechanics.md. Every create here is Tier 2 (drive-and-confirm):
you fill the form for review, present the confirm-each-write block, and click only on the
user's yes.

## What to create through the UI vs not

The browser is for interactive, low-volume seeding - not a bulk loader.

- **Drive-and-confirm in the UI:** single or low-volume synthetic records - a few test
  workers via `Hire`, an org, a cost center, a position, and app BO instances via the app's
  own create pages. Each one gets a confirm-each-write and a read-back.
- **Hand off to a loader:** bulk (dozens+ of records). Point at EIB (wd-integration-dev
  eib.md) or an API seed loader (wd-extend-dev tenant-ops.md write-side catalog: BO REST
  `?bulk=true`, customObject bulk upsert; wd-testing automation-harness.md). Clicking the
  same form thirty times is the signal you are past the browser's job - stop and hand off.
- **Rule of thumb:** if you will re-run it, script it (seed pack). If it is a one-off to
  unblock a single scenario, drive it.

## Synthetic-data rules

Standing suite rule (safety-and-scope.md; wd-extend-dev tenant-ops.md WRITE GATE; the
no-customer-data-in-dev-tenants feedback):

- **Realistic-shaped but fake.** No real names, SSNs, government IDs, real addresses, real
  bank/card numbers. Invent plausible values (a made-up worker name, a synthetic address, a
  test cost-center code).
- **Reuse the delivered demo population where possible.** Prefer an existing sample worker
  as the target of a transaction over creating a new person record - fewer PII surfaces and
  less cleanup. Only create new person records when the scenario genuinely needs one that
  does not exist.
- **Genericize any value derived from a real client artifact.** A design doc's example
  values are structural templates, not data to load verbatim.
- **Never enter real customer PII into a shared dev tenant.** If the only realistic data you
  have is real, stop and synthesize instead.

## Creation patterns

Three ways to create a record; all Tier 2, all with a read-back.

- **Create-via-app-page** - use the app's OWN create flow (its PMD create page or its Model
  BP). This is the preferred pattern for app BO instances because it exercises the app under
  test the way a user will, and it goes through the app's own validation and defaulting.
  Drive: open the app -> its create page -> fill fields for review -> confirm-each-write ->
  Submit. If the create launches a BP, the submit is the write (confirm it).
- **Create-via-native-task** - a delivered Workday task for foundation/reference data:
  `Hire` (a test worker), `Create Cost Center`, `Create Position`, `Create Supervisory
  Organization`, etc. These are security-neutral DATA entry (Tier 2), not security config -
  distinct from the Tier 3 security recipes in (references/config-execution.md). Drive:
  search the task -> fill synthetic values for review -> confirm-each-write -> OK/Submit.
  A `Hire` runs the Hire BP; expect an inbox step and confirm each committing click.
- **Verification read-back** - after every create, prove the record exists AND is usable:
  search for it, GET it via BO REST / app page, or run a WQL SELECT. Tie to the boolean-
  Active gotcha (wd-extend-dev model.md): an unset boolean on POST/PUT stores `false`, not
  null, so a record created without its `active`/status flag set true SILENTLY VANISHES from
  every filtered list and downstream reads come back empty. The read-back must confirm the
  record is present AND Active (or whatever the app's visibility gate is) - not merely that
  the create returned success. When a filtered read is empty, check the gate boolean on the
  source rows before assuming the create failed.

## Seeding order

Create data in dependency order, the same discipline as the recipe order in
(references/config-execution.md). A record that references another must have its target
already present, or the create fails validation (or worse, stores a broken reference).

1. **Foundation / reference data first** - orgs, cost centers, positions, worktags: the
   things app records and transactions point at. Native tasks (`Create Cost Center`,
   `Create Position`, `Create Supervisory Organization`).
2. **People next** - test workers via `Hire`, only if the delivered demo population does
   not already give you a usable target. A Hire needs a supervisory org and often a
   position to exist first (step 1).
3. **App BO instances last** - create through the app's own page so SINGLE_INSTANCE fields
   can resolve to the foundation/person records now present. A SINGLE_INSTANCE field whose
   target does not exist yet has nothing to pick.

Read back each layer before building the next on top of it - a missing or inactive
foundation record surfaces as a confusing empty picker three steps later.

### Worked shape (illustrative, not a script)

To seed one app record that references a worker and a cost center: (1) confirm a demo
worker and a test cost center exist via WQL read - if not, `Hire` / `Create Cost Center`
each as its own confirm-each-write; (2) open the app's create page, fill fields for review
picking those two as the SINGLE_INSTANCE targets, set the `active` gate explicitly true;
(3) confirm-each-write, Submit; (4) read back via BO REST GET and confirm the record is
present, Active, and its references resolved to descriptors (not null). One yes per write -
the Hire, the cost center, and the app record are three separate confirmations.

## Coordinating with wd-test-execution

Test data must EXIST before a scenario runs. This skill seeds; wd-test-execution executes
the scenario against what is seeded. The handshake: a scenario's precondition block (wd-
testing) is its data spec - this skill creates exactly those records, reads them back, and
reports them present-and-Active; then wd-test-execution runs.

**The deploy-wipes-dev-data trap:** a `wdcli app deploy` to a dev tenant can wipe the app's BO
data (wd-extend-dev wdcli-workflow.md / tenant-ops.md; suspected trigger: a new app version).
Assume app BO test data you seeded may be gone after the next deploy: check it, and re-seed
AFTER the deploy, before re-running scenarios. This is
the strongest argument for a repeatable seed pack over hand-clicking - if you find yourself
re-creating the same records post-deploy, hand off to a seed script (wd-extend-dev
tenant-ops.md seed/wipe; wd-testing automation-harness.md). Foundation data created via
native tasks (workers, cost centers) is tenant data, not app BO data, and is NOT wiped by an
app deploy.

## Cleanup

Every seed ships with its cleanup plan (WRITE GATE, wd-extend-dev tenant-ops.md). Prefer
soft over hard:

- **Soft-delete / status over hard delete.** Set the record's `active`/status flag to
  false/inactive rather than deleting. Hard delete is prohibited-tier (safety-and-scope.md)
  AND blocked by the SINGLE_INSTANCE dependency 500 (wd-extend-dev model.md: a parent delete
  500s while any child still references it - delete children first, or design status flags).
- **Wipe-by-marker.** Give seed records a recognizable marker in a text field so a later
  `WQL WHERE field CONTAINS marker` finds them all for cleanup (wd-extend-dev tenant-ops.md).
- **A fresh collection name beats purging zombies.** If old test records are tangled in
  dependencies, seed the next cycle into a clean set rather than fighting to purge the old
  ones. For app BO data, a deploy wipes it anyway - let the deploy be the reset and re-seed.
- **Never hard-delete to clean up.** If a stakeholder wants records permanently removed,
  that is a user-committed action (Tier 3) - hand them the exact steps; you do not click it.

Cleanup steps are themselves writes - each is a Tier 2 confirm-each-write (a status flip) or
a Tier 3 handoff (any hard delete). No seed load without a cleanup plan (WRITE GATE).

## Native recruiting records - Job Requisitions (learned 2026-10-03, Global Modern Services-based dev tenant)

**Check what the creation task will even allow before promising a test record.**

- **Create Job Requisition can make fields REQUIRED that legacy data leaves blank.** In this tenant
  both **Job Posting Title** and **Primary Job Posting Location** carry the required asterisk on
  the Job step. So a "requisition with no posting title" or "no posting location" test case
  cannot be created through the UI - it exists only as legacy rows. Search existing data for it
  first (WQL `... IS EMPTY`); if none, record the case as not reproducible and ask the client
  whether real tenants hold such records (integration loads, pre-requirement data).
- **Posting fields auto-copy from the plain fields.** Choosing a Primary Location fills the
  Primary Job Posting Location; Additional Locations fill Additional Job Posting Locations. To
  make the two lists DIFFER, remove the copied entries (the x on each chip) and add new ones.
- **An in-progress requisition is invisible to WQL `allJobRequisitions`.** Until the Create Job
  Requisition event completes (approvals done), the row is absent - so an app reading it sees
  nothing. Plan the approval steps (or a proxy approver) into the test-data job; do not test
  against a requisition that is still awaiting approval.
- **Template values from real rows.** Pick sup org, job profile, locations and reason from an
  existing requisition via WQL (`supervisoryOrganization`, `jobProfileHiringRequirement`,
  `createJobRequisitionReason`, the location fields) rather than guessing valid combinations.
- **Mark it as synthetic in the record itself.** Prefix the posting title (e.g. "SYN Test R-B ...")
  and say "synthetic test requisition, do not post" in Justification - doubles as the
  wipe-by-marker key.

### Browser mechanics for this wizard (Browser pane)

- **Viewport rule (one rule, shared with wd-deployment R8).** Keep the pane's own responsive
  size (preset `desktop`) and act by element ref from a fresh `read_page` / `find`, not by
  pixel coordinates. Re-`find` after any resize, full-screen switch or re-layout - a ref taken
  before it points at old geometry. If a layout genuinely needs more width, emulate a MODERATE
  width the pane can show unscaled: a larger emulation is scaled down to fit (1100x1400 in a
  narrow pane rendered at ~25% and clicks missed). Take a screenshot and confirm its scale
  before any coordinate click, check each value landed with `find`, and reset to `desktop`
  when done. Detail: wd-test-execution `browser-mechanics.md`.
- **Each section is read-only until its pencil is clicked; save it with the tick** before Next.
- **Date fields ignore `type` and `form_input`.** Click the MM segment, then send the digits as
  key presses (`key` "1 2 0 1 2 0 2 6").
- **Prompt fields:** click, type the search text, press Return; a mobile picker sheet may open -
  press Return again inside its search box.
- **The final Submit may be refused by the agent's own permission layer** (Claude Code auto
  mode blocked the BP Submit click on 2026-10-03 despite the user's approval in chat). Do not
  work around it: leave the completed form on its review page and hand the Submit click to the
  user as a USER-ACTION step, then verify the result by WQL.
