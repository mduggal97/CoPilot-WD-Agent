# Unit Testing - Derivation Method and Execution Detail

Companion to `wd-testing/SKILL.md`. This file holds the full derivation
walkthrough, per-element scenario patterns with real examples, and the
execution/recording procedure.

## 1. Derivation happens during design authoring

The scenario list is a design deliverable. Sequence inside the design phase:

1. Author (or receive) the Requirements tab / Discovery content.
2. **Requirement walk:** for each REQ row, write the happy-path scenario in
   the user's language ("Submitter creates a Cost Center request with all
   required worktags and submits"), then ask "how does this fail?" - each
   distinct failure mode is its own scenario (missing required field,
   invalid combination, unauthorized user, downstream write rejected).
3. **Checklist sweep:** apply Section 2 below against the Object Model,
   Business Process Design, Security, Technical Specification, and UI tabs.
   This catches scenarios that no single requirement names (null-field
   landmines, timeout paths, negative security).
4. Land the rows on the Unit Testing tab (format owned by wd-design-doc)
   before the design sign-off gate. Unknowns in a scenario (e.g., "expected
   BP routing - TBD, Q: who approves at step 3?") follow the yellow-cell
   convention: yellow fill + the question in the cell text, cleared when
   answered.

**Change-driven testing pointer:** when the trigger is a change or enhancement rather than
net-new design, the acceptance criteria pinned at the change-workflow entry gate
(wd-extend-dev `references/workflow.md` Rule 0) are the seed for the requirement walk above
- each criterion becomes at least one scenario. That gate only supplies the intent; the
derivation method stays here.

Traceability check before sign-off: every REQ has at least one UT-###;
every UT-### cites a REQ-### or a checklist line. Orphans on either side
mean the design or the test plan is incomplete.

## 1a. Scenario quality gate - earn your place on the tab

Before any scenario row lands on the Unit Testing tab, it must clear these four gates.
Fast to answer when authoring; never revisited once recorded.

1. **What behavior or invariant does this protect?** Name the requirement or
   checklist line. "It tests the submit button" is not an answer; "it confirms
   the POST fires and the BO record is created" is.
2. **What credible regression causes it to fail?** Spell out the break: a change
   to the endpoint path, a null field on the BO, a missing security grant. If you
   cannot name a plausible regression, the scenario is likely testing implementation
   noise rather than behavior.
3. **Does any existing scenario already catch that regression?** If yes, merge
   or drop - redundant coverage adds maintenance cost with no safety gain.
4. **Is the expected outcome from an independent source of truth?** The
   acceptance criterion, the wireframe end-state, the requirement text - not
   re-derived the same way the code derives it (tautological scenario: "submit
   returns the BO id it just created" - the id came from the code under test).

**Three anti-patterns to name and reject at authoring time:**

- **Implementation-coupled:** the scenario asserts HOW the code does something
  (a specific endpoint URL, an internal state variable, the order of two
  non-ordered operations). Tell: the scenario breaks on a behavior-preserving
  refactor even though the feature works correctly. Fix: reframe against the
  observable result at the public interface (the BO record state, the page that
  renders, the notification the user receives).
- **Tautological:** the expected value is computed the same way the code computes
  it - a wrong answer still passes. Fix: anchor the expected value to a literal
  from the design (a named worktag ID, a status written in the requirement,
  a field count from the BO model).
- **Horizontal-slice:** ALL scenarios are drafted first, THEN all execution
  begins. Risk: scenarios describe imagined behavior not yet built or signed off.
  Fix: work vertically - derive and execute one vertical's scenarios (one feature
  slice or requirement group) before authoring the next. The derivation sequence in Section 1 already enforces this;
  the anti-pattern surfaces when a sprint reserves a separate "test authoring
  sprint" disconnected from the build.

## 2. Extend derivation checklist - worked detail

### Pages (every PMD, no exceptions)

Per page:
- **Render:** loads with valid context (correct role, valid record/eventId),
  all sections and pickers populate, computed/locked fields show correctly.
- **Submit:** the outbound endpoint fires, the BO/event is created or
  updated, the user lands on the designed confirmation/next page (wireflow
  arrow target from the design's UI tab).
- **No-context open:** navigate to the page URL **without** the expected
  query params. Real defect (a costing app):
  approve/create/details/revise pages threw 500s / JexlArithmetic
  NullOperand when opened without eventId - read endpoints needed null-safe
  URLs and `exclude` guards. Every param-dependent page gets this scenario.
- **Every request-type variant** counts as its own page set (e.g. a
  multi-type request app with Cost Center, Program, Project, Gift, and several
  accounting types, each with create/approve/details/revise pages - that is 4 scenarios x each, not 4
  total). This mirrors the design-thoroughness standard: every screen, not
  a representative subset.

### Custom BPs (Model BPs)

Per BP definition:
- **Approve** through every configured step (a 4-step approver chain is
  4 approval scenarios or one scenario with 4 verified steps - but each
  step's approver/notification is asserted).
- **Deny** - status write-back, submitter notification, record end-state.
- **Send-back / revise** - ONLY if configured. `SEND_BACK` requires
  `revisePageRoute` (build error P400 without it); one request app shipped
  APPROVE/DENY-first with revise deferred, so its early test plan had no
  send-back scenario - when revise was added (REQ-009), the scenario set
  grew: send back -> submitter edits on revise page -> PUT full-replace ->
  resubmit -> routing restarts correctly.
- **Cancel/rescind** mid-flight: what happens to the BO record and any
  pending orchestration trigger.

### Security domains

Per domain (data domains AND page domains):
- **Positive:** a user in the granted group performs the protected action.
- **Negative:** a user NOT in the group (or with only the other domain)
  gets nothing - page blocked, WQL returns no rows, API endpoint 403s.
  "Wrong role sees nothing" is asserted, not assumed. Include the
  pre-grant state: one app's domains reported S22 until granted in-tenant -
  a scenario should confirm the app fails closed, not open, before grants.

### Orchestrations

Per orchestration, four paths minimum:
- **Success** - end-to-end with write-back verified on the BO (e.g.,
  BP-completion -> Put Cost Center -> result written to the Request record).
- **API error** - the downstream SOAP/REST call rejects (bad reference ID,
  validation failure). Assert the error is captured somewhere a human sees
  it (write-failure UX was Open Item material on one app - don't let failures
  vanish silently).
- **Empty data** - the WQL/read step returns nothing; orchestration must
  not NPE or write garbage.
- **Timeout** - page-synchronous flows have a 25-second cap (owned by
  wd-extend-dev orchestration.md). Any flow that can exceed it (large payloads,
  slow tenant) needs a scenario at/near the cap proving the designed behavior
  (async hand-off, user messaging).

### Integrations / web-service calls

Per call (SOAP or REST):
- **Happy payload** - including verification in the target module (the Cost
  Center actually exists after Put_Cost_Center, with the right worktags).
- **Malformed/rejected payload** - wrong reference-ID type is the classic
  Extend miss: on one app the worktag `Worktag_Type_Reference` ID-types differ per
  operation (Accounting_Worktag_Type_ID vs Worktag_Type_ID enums) and were
  flagged UNVALIDATED until a real-tenant run. A scenario per known-risky
  mapping.
- **Retry/replay** - is the op idempotent? Put_* generally is; Submit_*
  (Gift, Project) may create duplicates on replay. Assert designed behavior.

### Boundary data - the null-fields landmine

Whenever a BO gains fields after records already exist, **old records carry
nulls in the new fields and pages that assume values crash**. Mandatory
scenario on every BO field addition: open/edit/approve a **pre-existing
record** created before the field existed. Grounding: on one request app the Request BO was
extended repeatedly (classification, bypassWebService, worktag WIDs 32-37),
and a staging-model deletion once silently shipped a BO with only fields
1-19 - both failure shapes are caught by the "old record renders clean"
scenario plus a field-count check against the model.

### Volumes

Grids/lists over ~100 rows hit the BO REST collection limit (owned by
wd-extend-dev pmd-gotchas.md). If the design expects more (e.g. a request app
forecasting ~300 requests/month - a status grid passes 100 rows within weeks),
the scenario seeds >100 records and proves paging/filtering/WQL-side limits,
not just a 5-row demo.

### Tenant-specific configuration

Anything read from App Attributes (`site.<attr>`) or otherwise
tenant-variable (instance WIDs, subtype IDs, credential names like
`_DEFAULT_WORKDAY_CREDENTIAL`) gets:
- a scenario with the attribute correctly overridden for the tenant, and
- a scenario with it missing/wrong, asserting a diagnosable failure
  (empty picker with a known cause beats a silent wrong-data write).

## 3. Execution procedure

1. **Tenant:** dev/implementation tenant named in the scenario's
   tenant/data column. Data-dependent scenarios that need client reference
   data (custom orgs, real worktags) may only be executable in the client's
   tenant - mark those rows explicitly rather than faking a pass in the
   delivery-org tenant (e.g., a master-data app whose Balancing Unit /
   Function pickers are empty in the delivery-org dev tenant by design; that is
   "not executable here", not "Fail").
2. **Seed data:** use the seed/wipe script pattern (see wd-extend-dev) so
   every run starts from a known state. Record the seed set version with
   the result. (Scenario preconditions double as the seed-pack spec -
   tenant-ops write verbs pending; WRITE GATE applies.)
3. **Record per run** on the Unit Testing tab: Status (Pass / Fail /
   Retest / Blocked / Not Executable in tenant), Evidence (screenshot path,
   event ID, or record WID), Date, Tester. Fail -> log a defect (see
   defect-triage.md) and link its ID in the row. The BO/event end-state and
   evidence WID are capturable live via tenant-ops (BO REST get / WQL) -
   paste the read result as the row's evidence.
4. **Retest discipline:** after a fix deploys, the row moves Retest ->
   Successful only on re-execution with fresh evidence - never on "the fix
   was deployed" alone (one delivered app: a fix deployed but the row held at
   Retest pending visual confirmation of the approve page).
5. **Gates:** tab fully current (no stale Fail/Retest rows unexplained)
   before design sign-off, and again before hand-off to wd-deployment.
