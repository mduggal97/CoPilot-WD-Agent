# Triage Runbook Pattern - The Support-Desk Deliverable

The fourth deliverable in the audience mapping (SKILL.md): the document that lets a
client help desk take a ticket from "it's broken" to a fix or a clean escalation
without a delivery-team consultant on the phone. It is taught in KT session #3
(`kt-sessions.md`) and its teach-back is a walked mock ticket.

Audience calibration: written for a help-desk analyst who has never opened Extend -
observable symptoms and click-level checks, not architecture. It is the help-desk
translation of **wd-testing**'s triage classes (`references/defect-triage.md`);
mirror those classes, don't fork them.

## Part 1 - The five-way triage decision tree

Every ticket gets classified into exactly one branch. One page, tree or table form,
with **observable symptoms** per branch - things the analyst can see, not infer:

| Branch | Observable symptoms | First checks | Then |
|---|---|---|---|
| **1. The app itself** (code/defect) | Error message from the app on a normal action; a screen 500s for EVERY user with the right role; wrong value written/displayed and data + security check out | Reproduce with a second user of the same role; capture screenshot + record ID | Escalate to the delivery team (packet below) - maps to wd-testing class (a) |
| **2. BP configuration** | Request submitted but stuck - no inbox task for the expected approver; task routed to the wrong person; event sits "In Progress"/"Awaiting Action" past normal age | View the event's Process history: which step is it on, who is it assigned to? Is that assignee populated/active? | Client BP admin fixes routing/assignment; no code change |
| **3. Security** | ONE user (or one role) can't see a page/button/data that peers with the same job can; brand-new user affected; "S22"/permission-style errors | Compare the affected user's security-group membership to a working peer; was the user added recently (grants may not be activated)? | Client security admin: group membership / domain grant / Activate Pending Security Policy Changes |
| **4. Data / config** | Empty dropdown or picker; a lookup returns nothing for a value that "should exist"; behavior differs between tenants; wrong default value | Does the referenced record actually exist in THIS tenant? App Attributes / reference data current? | Client config admin per the deployment guide (**wd-deployment** `references/deployment-guide.md`) - class (d) |
| **5. Workday platform** | Whole tenant slow/unreachable; delivered (non-app) screens failing too; behavior changed right after an R1/R2 release with no app change | Is it happening outside the app as well? Check Workday status/trust page; note the release calendar | Workday Customer Care case (packet below); notify the delivery team if the app is implicated |

Rules for the tree:
- **Sequence matters**: check the cheap/likely branches (2-4) before assuming branch 1.
  Most hypercare tickets are config, security, or data - not code (the wd-testing
  class-(d) pattern).
- Enhancement asks ("can it also...") are NONE of the five - route to the enhancement
  intake path (**wd-post-go-live** `references/adoption-and-feedback.md`), not the
  defect flow.
- If a ticket fits two branches, it's two tickets (the split rule, mirrored from
  defect-triage class (e)).

## Part 2 - Escalation packets

What to collect BEFORE escalating - an escalation without the packet round-trips for
days. Two destinations, two packets:

**Delivery-team ticket (branch 1, or unresolved 2-4):**
- Who + when: affected user(s), security role, date/time of failure
- What: exact steps taken (numbered), expected vs actual, full error text verbatim
- Evidence: screenshot, the record/event ID, and - for orchestration issues - the
  failed run's log entry (the monitoring runbook in **wd-post-go-live** SKILL.md
  shows where; `wd_response_code` + `wd_message` are the two fields the delivery team asks
  for first)
- Scope: one user / one role / everyone; workaround known or not; severity guess
  per the agreed SLA definitions

**Workday Customer Care case (branch 5):**
- Tenant name + environment; time window; whether delivered functionality is
  affected outside the app
- Screenshots + any Workday-issued error/reference codes
- Raised by the client's authorized case-raiser (named in the support-ownership
  matrix - **wd-post-go-live** `references/handoff-and-closeout.md`); the delivery team cc'd
  when the app is implicated

## Part 3 - Top-10 what-if scenarios (per app)

Ten concrete "what do I do when..." walkthroughs, each: symptom -> branch -> exact
resolution steps -> escalation packet if steps fail. **Seed them from real hypercare
tickets** - `kt-sessions.md` already mandates that tickets feed the runbook; this
list is their home format. Draft placeholders from the unit-test failure modes
(**wd-testing** scenario checklist) before go-live, then replace with real tickets
during hypercare - by KT session #3 the majority should be real.

Typical shape: stuck approval, empty picker, new-hire can't see the app, scheduled
run didn't fire, user submitted in error and wants it back, attachment won't upload,
approver on leave, wrong default value, R1/R2 morning-after check, "is it down?"

## Part 4 - Error-table superset

ONE lookup table for every error the app can surface - the user-guide error table
(pattern per `user-guide-pattern.md`: *what the user sees -> what it means -> what to
do*) PLUS the admin-only errors users never see (orchestration log entries, failed
scheduled runs, integration event WARNINGs/ERRORs), each with the same three columns
plus **which triage branch it indicates**. The user guide keeps its user-facing
subset; the runbook holds the superset - one place a help desk can search any error
text. When an enhancement adds a failure mode, the refresh-checklist row in SKILL.md
updates BOTH tables.

## Mandatory step attributes (six per step) - a pre-generation gate

Every actionable runbook step - the what-if resolution steps (Part 3), the
first-checks in the tree (Part 1), the escalation actions (Part 2) - carries
SIX attributes (pattern from a community skill-craft survey, 2026-08-06 -
rebuilt for this suite):

1. **Named owner** - a ROLE with a name slot ("BP admin - [name]"), never
   "the team" or "IT."
2. **Expected duration** - how long before you should worry.
3. **Observable success signal** - what the analyst SEES when it worked.
4. **Observable failure signal** - what they see when it didn't.
5. **Rollback / undo path** - how to get back to the pre-step state (or an
   explicit "no undo - escalate instead").
6. **Escalation contact** - where the step goes when it fails (usually one of
   the Part-2 packets).

A step missing its owner **BLOCKS the runbook** - refuse to finalize until the
role is named; don't generate-and-flag. This gate runs BEFORE authoring, not
after: an ownerless document decays fastest, and a runbook is the document a
client keeps longest.

### Build-spec: `runbook_validator` (regenerate on demand, don't ship)

Per the suite's build-spec convention (wd-extend-dev `references/scripts.md`),
regenerate this stdlib-only Python script when needed rather than storing it:

- **Input:** the runbook file (markdown tables or headed sections).
- **Checks:** each detected step row/section has all six attributes present
  and non-placeholder; the owner is a named role (reject "team"/"IT"/"TBD"
  owners - TBD is allowed on other attributes only if flagged).
- **Output:** per-step findings (step ref -> missing/weak attributes) plus a
  0-100 score (attribute completeness across all steps); **pass >= 80 AND
  zero ownerless steps**.

The quality-gate check for guides/runbooks in wd-extend-lifecycle
`references/quality-gates.md` invokes this validator - run it before the
runbook is presented as final and report the score with the deliverable.

## Maintenance

- Owned by the support desk after KT sign-off; the delivery team seeds v1.0.
- Every escalated-and-resolved ticket that taught something new adds a row (what-if
  or error-table) - the runbook is a living document, versioned like the other KT
  docs (SKILL.md refresh checklist).
