# UAT Support - Client-Executed, Consultant-Supported

Companion to `wd-testing/SKILL.md`. UAT is distinct from E2E:

| | E2E (end-to-end cycles) | UAT |
|---|---|---|
| Who executes | Consulting team (with client SMEs observing/assisting) | **Client business users** |
| Consultant role | Driver | **Support**: scripts, triage, fixes, daily rhythm |
| Purpose | Prove the integrated build works across systems/BPs | Prove business users can run their process and accept the app |
| Scripts | Unit/integration scenarios, tester-speak | Business-language scripts derived from unit scenarios |
| Exit | Cycle objectives met, defects triaged | Formal sign-off artifact |

A large multi-app program runs numbered E2E cycles (cycle 1, cycle 2) before UAT;
scope can shift between cycles (e.g. one app moved from cycle 1 to
cycle 2 after team realignment) - the UAT plan inherits whatever landed by
the final cycle, so re-baseline scripts against the then-current design
version, not the one the scripts were first written from.

## Generating UAT scripts from unit scenarios

Do not write UAT scripts from scratch - **translate** the unit scenarios:

1. **Select:** business-facing scenarios only. Keep page flows, BP
   approvals, notifications, end-to-end request lifecycles. Drop
   internals-only scenarios (orchestration timeout paths, API-error
   injection, null-field boundary checks) - those stay in unit/regression.
2. **Translate tester-speak -> business-user-speak:**
   - "POST creates Request BO instance with status Submitted" ->
     "Submit the request; you should see a confirmation and the request
     appears in your list with status Submitted."
   - "Approve via approvalStep /approveCostCenter/{eventId}" ->
     "Open your Workday inbox task for the request and click Approve."
3. **Strip tenant jargon:** no WIDs, endpoint paths, `wdcli`, WQL, App
   Attributes, tenant names. Refer to tenants as "the test environment."
   Replace seed-record IDs with recognizable business data ("the Oncology
   cost center request").
4. **Keep traceability:** each UAT script carries the UT-### / REQ-### it
   came from, so a UAT failure maps straight back to a requirement and its
   unit evidence ("did we test this?" is answerable in one lookup).
5. **Add role/actor headers:** who runs each script (Submitter, Cost Center
   Manager, Central Approver) and which **real test user** (not consultant
   accounts) plays that role.
6. Script format mirrors the scenario format: ID (UAT-###), source UT/REQ,
   actor, preconditions in business terms, numbered steps, expected result
   in business terms, a Pass/Fail + comments column for the client tester.

## Coverage matrix (requirements <-> test cases, maintained both ways)

A standing UAT-toolkit artifact (pattern from a community skill-craft survey,
2026-08-06 - rebuilt for this suite): a requirements <-> test-cases matrix
maintained in BOTH directions - every requirement lists the cases that cover
it, and every case lists the requirement(s) it exercises. Step 4's per-script
traceability makes this cheap: the matrix is just those UT-###/REQ-### links
pivoted both ways.

- **Source of truth is the design doc's Unit Testing tab** - the matrix is
  DERIVED from it (plus the UAT script set), never a second hand-maintained
  copy. Regenerate it; don't edit it.
- **Compute coverage %** (requirements with >=1 covering case / total
  requirements) and emit the **gap list**, which reads in both directions:
  - Requirements with ZERO cases = **untested scope** - write the case or get
    the gap explicitly accepted in writing.
  - Cases with NO requirement = **scope creep or a missing requirement** -
    either the requirement exists and needs writing back into the design doc
    (wd-design-doc), or the case tests something nobody asked for.
- **Quality-gate tie-in:** the UAT exit gate includes "coverage matrix gap
  list is empty, or every remaining gap is explicitly accepted with a named
  accepter" - see exit criteria below.

## Entry criteria (do not start UAT without these)

- **Unit tests pass:** Unit Testing tab current, no open Fail rows in UAT
  scope, no open Sev1/Sev2 defects.
- **Data converted/seeded:** the client tenant holds realistic reference
  data (the custom orgs, worktags, hierarchies the app reads) and any
  converted transactional data. Confirm tenant-specific config (App
  Attribute overrides, sequence generators, ISU credentials, BP approver
  chain assignments) is done - these are exactly the items that pass in the
  dev tenant and break in the client tenant. Most of these confirms are
  runnable as the tenant-readiness read-set (wd-extend-dev
  `references/tenant-ops.md`) rather than asked of the client admin.
  Seeding and between-cycle resets can be API-scripted (scenario
  preconditions double as seed-pack specs) - wd-extend-dev
  `references/tenant-ops.md`, WRITE GATE mandatory.
- **Sensitive data masked or synthetic:** decide explicitly whether UAT needs
  converted production data (usually only when the test IS the conversion -
  reconciliation, volume realism) or synthetic data suffices (almost always,
  for functional scripts). Any field classified PHI or FERPA in the design
  doc's data-classification pass (wd-design-doc
  `references/nfr-accessibility.md` section 5) must be **masked or synthetic in the
  non-prod tenant** unless the client's security office approves real values
  in writing - file that approval with the UAT plan. Default is masked.
- **Security assigned to real test users:** each UAT role mapped to a named
  client test user with the correct security groups/domains granted, and a
  negative check that non-testers can't reach the app. Consultants
  executing scripts is not UAT.
- Scripts distributed, testers briefed on intake process, triage calendar
  booked.

## Exit criteria

- All in-scope UAT scripts executed with a recorded result.
- **Coverage matrix gap list empty or accepted:** no requirement with zero
  covering cases unless a named client owner has explicitly accepted the gap
  in writing (the acceptance travels with the sign-off artifact).
- **No open Sev1 or Sev2 defects** (severity guide in defect-triage.md).
  Open Sev3/Sev4 items are listed with an agreed disposition (fix before
  go-live / fix after / accepted as-is) - each dispositioned item is either
  a defect with an owner or an Open Item in the design doc.
- Deferred change requests explicitly logged in wd-design-doc change
  control, not left as verbal understandings.
- **Sign-off artifact:** a dated acceptance record naming the client
  signatories, the design-doc version tested against, and the
  open-item/deferred-CR list attached. This artifact travels with the
  deployment package (wd-deployment expects it).

## Defect intake and daily triage rhythm

During the UAT window:

- **Single intake channel.** One tracker (program standard - e.g., a
  Smartsheet tracker like a program-level Extend Task Tracker, or the client's
  defect tool). No hallway/email/Teams-only defects - anything raised
  verbally gets logged by whoever heard it, same day. Required fields at
  intake: reporter, date, script/step ref (UAT-###), actual vs expected,
  screenshot/record ID, tester's severity guess.
  - **Intake fields that make triage deterministic** (adapted from an internal
    firm skill, 2026-08-28): the exact failing record/instance (valid by
    construction where the form constrains the values), the inputs / runtime
    values used, expected value vs actual value, and a screenshot - with an
    explicit "no PHI/PII in screenshots" reminder ON the intake form (synthetic
    or scrubbed data only, per wd-extend-lifecycle `ai-data-governance.md`
    section 6). The more precise the failing intersection, the faster the
    regression check in `defect-triage.md` Step 0 resolves.
- **Daily triage, 30 min, same time each day.** Attendees: consultant lead
  (runs it), client UAT coordinator, developer or architect on call.
  Agenda: new items -> classify per the decision tree in defect-triage.md
  (bug vs design gap vs change request vs data/config) -> assign severity
  and owner -> review yesterday's fixes ready for retest.
- **Turnaround targets:** Sev1 same-day response, Sev2 within 1 business
  day, Sev3/4 batched. Retests happen in the UAT tenant by the original
  reporter where possible.
- **Daily status note** to the program channel: executed/passed/failed
  counts, new defects by severity, blockers. Keeps the exit-criteria math
  visible so sign-off day has no surprises.
- Code fixes during UAT follow wd-extend-dev's workflow - pull latest +
  diff first; if a client developer owns the code, deliver a change-list
  rather than editing directly, and account for that hand-off delay in
  retest promises.

## Tester experience (recruit -> orient -> thank)

Testers are business users doing UAT on top of their day jobs - how they're
treated determines script throughput AND whether anyone volunteers next time.

**T-2 weeks - the tester ask.** Two weeks before the UAT window, send the
formal ask: **named testers** (not "someone from AP"), **estimated hours over
the window** per tester (derive from script count x realistic minutes +
retest allowance), and **manager cc** so the time is actually released.
This ask is a standing row in the client onboarding packet's UAT-gate
refresh (**wd-pm** `references/client-onboarding-packet.md`) - feed it
there rather than inventing a new channel.

**Orientation (30 min, day 1 of the window).** Before the first script:
- The test environment: how to get in, which test user they are, that it's
  safe to break things.
- How to log a defect **in their words** - actual vs expected + screenshot;
  severity is a guess, triage assigns the real one (defect-triage.md).
- The daily rhythm: triage happens at [time], fixes come back for retest,
  the daily status note shows progress.
- What happens to their findings - the triage classes in one plain-language
  minute, so "works as designed" answers don't read as dismissals.

**Tester quick-start (one page, business language).** Login, their role +
test user, where the scripts live, how to record Pass/Fail, how to log a
defect, who to ask, the daily schedule. No tenant jargon (same translation
rules as the scripts above). Hand it out at orientation.

**Wrap-up / thank-you note (at exit).** Send within days of sign-off, cc
managers: results in one line (scripts run, pass rate, defects fixed),
what ships when (go-live date, which of their findings land at go-live vs
after), and a genuine thank-you naming the testers. Voice per **wd-comms**.

**Recruit champions from testers.** The wrap-up note is also the recruiting
moment: the strongest testers are the natural champions/super-users for
go-live (role and ask defined in **wd-post-go-live**
`references/adoption-and-feedback.md` - this note just makes the invitation).
