# Defect & Change-Request Triage - E2E/UAT Decision Tree

Companion to `wd-testing/SKILL.md`. Run this tree on every logged defect or
change request during E2E cycles and UAT windows. The goal is to route each
item to the right workflow (and only one), with the right people notified.

## Step 0 - Validate latest code against latest design FIRST

Before classifying anything, pull the **latest deployed code** (via
wd-extend-dev: `wdcli app download ... --latest-version`, then diff against
the local copy) and open the **latest signed design-doc version** - not the
version the tester remembers.

Why first: the disagreement is often **doc-vs-build drift, not a bug**.
Both drift constantly during active delivery - e.g., one app's design doc
carried an outdated go-live date in three tabs after the real window moved,
and another's early design-doc version predated most of the built
functionality. A tester comparing behavior to a stale doc logs phantom
defects; a consultant comparing a stale local copy to the doc misses fixes
already shipped. Establish the true current state of BOTH sides, then
classify.

Record what you compared: app version/build ID and design-doc version go on
the defect record.

- **REGRESSION CHECK.** When the defect reads like "this used to work," pull the
  recent deploy/change history for the artifact(s) the defect touches (app build
  IDs + design-doc change-log + wd-extend-dev app-build logs) BEFORE classifying.
  A defect whose artifact was redeployed in the last cycle is a probable
  regression - reproduce at the reported intersection against the prior build
  first. Record the build IDs compared on the defect (you already record app
  version + design-doc version here - add "last change to this artifact").
  (adapted from an internal firm skill, 2026-08-28)

## Step 1 - Classify

### (a) Code does not match the signed design -> CODE FIX

The design is clear, signed, and the build deviates.

- **Route:** fix via **wd-extend-dev**'s workflow - pull latest + diff
  before editing; if a client developer owns the code, deliver a
  **change-list** (file, location, exact change, why) instead of editing
  and deploying directly.
- **Close-out:** deploy -> flip the linked Unit Testing row to Retest ->
  re-execute with evidence -> Successful.
- **Example (a costing app):** approve-page Additional
  Worktags descriptors didn't render - the display POD's column had the
  instanceList pool but no `selectedValues` while every sibling column had
  it. Design clearly expected descriptors on the approve page; build
  deviated; classification (a); one-line code fix, deployed, held at
  Retest pending visual confirmation.

### (b) Design is ambiguous or silent -> DESIGN DECISION

The build does *something*, the tester expected *something else*, and the
signed design doesn't settle it (or two design tabs conflict).

- **Route:** convene the named decision-makers (product owner/architect +
  client functional owner - small, empowered, fast). Present the ambiguity
  and 2-3 options with implications. **Outcome recorded via wd-design-doc**:
  requirement updated or an Open Item row added (which yellow-highlights
  per convention until resolved). Only after the doc records the decision
  does any resulting code work start (as class (a) against the new text).
- **Example (a request app's scope):** a discovery session flagged several
  data domains as out-of-scope while the design-doc MVP still
  included them - a doc-vs-decision conflict no one could adjudicate from
  the workbook alone. Correct handling: decision meeting, outcome into the
  doc; the built vertical waits on that record, and downstream
  artifacts carry the "scope pending confirmation" caveat meanwhile.
- **Example (an architect review):** an entire batch of ambiguities became
  Open Items (validation placement, write-failure UX, ID
  generation...) rather than defects - silence in the design is a design
  gap, not a bug.

### (c) Works as designed, client wants different -> CHANGE REQUEST

The build matches the signed design; the client's expectation changed or
was never in scope.

- **Route:** into **wd-design-doc's change control** - never "just tweak
  it." If the change is material, assess LOE via **wd-estimate**
  calibration before the client decides. **Do not build ahead of
  approval**, even when approval is "expected."
- **Example (a costing app CR):** app built the designed
  funding-unknown checkbox; client direction shifted to representing
  unknown/control-salary funding via a dedicated Program worktag and
  dropping the checkbox + free-text field. Works-as-designed -> CR through
  the program's change-control board, Extend LOE estimated ~40 hrs,
  build explicitly held until approval despite approval being expected.
  That is the template.

### (d) Data / config / tenant issue -> TENANT FIX, NO CODE

The code and design agree; the environment doesn't cooperate.

- **Typical causes:** missing security-domain grants (app fails closed /
  S22 pre-grant), BP approver chains not configured on the definition,
  App Attributes still holding another tenant's instance WIDs, sequence
  generators not set up, ISU credential missing permissions, reference
  data absent, stale/unseeded test data.
- **Route:** tenant configuration fix (consultant or client security/config
  admin per the tenant-setup checklist), then retest. No code change, no
  design change; note the resolution on the defect so it doesn't get
  re-logged. Most (d) causes are checkable live via tenant-ops (S22 probe on
  the app's data source, RefID liveness, App-Attribute WQL - wd-extend-dev
  references/tenant-ops.md) - run the read-set before assigning an owner.
- **Example (empty pickers):** Balancing Unit / Function / Department pickers
  empty in the dev tenant - those client custom-org subtypes simply don't
  exist there, and the subtype WIDs are tenant-specific instance WIDs.
  Environment fact, not defect (the durable mitigation - App Attributes per
  tenant - was a design improvement, handled separately).

### (e) Combination -> SPLIT

One report, multiple items. Split into separate tracked items, one per
class, cross-referenced. Common shape: a genuine code defect (a) whose
investigation exposes a design silence (b) - e.g., a write-failure that is
both "the error wasn't surfaced" (code/design gap) and "who should be
notified on failure was never specified" (Open Item). Never let a CR ride
inside a bug ticket - the CR needs its own LOE and approval trail.

## Step 2 - Fix protocol (for class (a) code fixes)

Classification names WHAT kind of item you have. This step governs HOW you investigate
and fix class (a) code defects - the discipline that prevents the guess-and-check spiral
that burns consultant hours and logs phantom defects as new bugs.

**Investigate before proposing.** No fix proposal until the root cause is named.
"The page renders incorrectly" is an observation, not a cause. Pull the actual error
(console, EndSync body, Integration Messages grid) and form a specific claim about what
is wrong and why, grounded in the code or tenant config. Record it on the defect row
before touching any code.

**One hypothesis at a time.** Form the most specific theory you can, make the smallest
change that would confirm or deny it, then observe. Two simultaneous changes mean you
cannot tell which one fixed (or introduced) anything.

**Investigation checklist - run before attempt 1, not attempt 3:**
1. Read the actual error - not the UI message, the EndSync body, app build log, or
   Integration Messages grid. The specific text narrows the cause to 1-2 locations.
2. Confirm which code version is live in the tenant - not "the latest I uploaded" but
   the live version from `wdcli app builds list` or the About-This-App page in tenant.
3. Reproduce in the simplest possible case: fewest fields, smallest data set, single user.
4. Check the class (d) read-set first (tenant-ops: security grant, App Attribute, RefID
   liveness) - environment issues outnumber code bugs in early tenants and are cheaper
   to eliminate than to rule out by changing code.
5. Run the pmd-gotchas sweep on the affected page/script/BO before writing new code.
   Many Sev1 root causes are known gotchas (#40 = unguarded endpoint read, #45 = soft-delete
   boolean default, #47 = grid cellTemplate editable). Finding the gotcha number short-circuits
   the investigation loop.

**The 3-attempt escalation rule.** After 3 consecutive failed fix attempts on the same
defect with no convergence, STOP. Three failures signal an architectural assumption that
is wrong - the root cause is not where you have been looking. Escalate to design-level
review (the Step 1 class (b) route): pull in the architect, state clearly what has been
tried and what was observed each time, and treat it as a design gap until the architecture
is understood. Continuing past 3 attempts without escalation is the leading source of
Sev1 spirals in Extend builds and is never acceptable on a client engagement.

## Severity guide

| Sev | Definition | Examples | Response |
|---|---|---|---|
| **Sev1** | Blocker - core flow broken, no workaround; testing halted for a group | Submit fails for all users; approve page 500s (the unguarded-read-endpoint class); data written incorrectly to the tenant | Same-day; all-hands until workaround or fix; can pause the UAT window |
| **Sev2** | Major - core flow broken with clumsy workaround, or an entire secondary flow down | Send-back/revise loop broken; one request type of several unusable; security leak (wrong role sees data) - always >=Sev2 | Fix within the cycle/window; blocks exit criteria |
| **Sev3** | Minor - cosmetic-plus: wrong label, confusing message, non-blocking validation gap | Descriptor shows WID instead of name; missing helpful error text | Batch; disposition at exit (fix pre/post go-live) |
| **Sev4** | Trivial/cosmetic | Spacing, casing, nice-to-have text | Backlog; never blocks anything |

Severity is about **impact**, independent of classification - a Sev1 can be
a tenant-config issue (d) and a Sev4 can be a code bug (a). Change requests
(c) carry priority, not severity.

## Who to notify, per class

| Class | Always notify | Also when Sev1/2 |
|---|---|---|
| (a) Code fix | Developer/owner of the code (change-list if client dev), architect | PM + client UAT coordinator (retest impact) |
| (b) Design decision | Architect + client functional owner (decision-makers), doc owner | PM (schedule risk while undecided) |
| (c) Change request | PM / change-control owner (e.g., program-level board), client sponsor, estimator | - (CRs go through the board regardless) |
| (d) Tenant/config | Whoever owns the tenant checklist item (consultant config, client security admin) | Client UAT coordinator (testers blocked) |
| (e) Combination | Union of the split items' lists | PM to track the linkage |

Team rosters change mid-delivery (one program lost its architect and developer
within a week) - keep the notify list role-based in the
tracker, resolve to names at triage time.

## Record-keeping

Every triaged item ends up in exactly one home:

- (a) -> defect row in the tracker + linked Unit Testing row (Retest cycle)
- (b) -> Open Item / requirement update in the design doc (wd-design-doc)
- (c) -> change-control entry (wd-design-doc) with LOE (wd-estimate)
- (d) -> defect row closed "environment", tenant-setup checklist updated so
  the next tenant migration doesn't repeat it
- (e) -> one item per class, cross-referenced

If an item can't be placed in one home, it isn't classified yet - take it
back to Step 0.

## Defect-register column model (owner)

This skill OWNS the human/tool column-ownership taxonomy for a defect register -
who is accountable for each column, so a run driven by tooling never overwrites a
human judgment column and vice versa. The transport skill (**wd-smartsheet**) only
moves values into whatever sheet holds the register; it points HERE for what each
column means and who owns it.

| Column | Owner | Filled by |
|---|---|---|
| **Description** | Human | The tester/consultant logging the defect - the plain-English "what's wrong" |
| **Steps** (to reproduce) | Human | The tester - the exact repro path + evidence ref |
| **Tester Severity** | Human | The tester's proposed Sev1-Sev4 (impact call - confirmed at triage per the severity guide above) |
| **Business Sign-off** | Human | The client/business owner accepting the fix or disposition (a judgment, never auto-set) |
| **Root Cause** | Tool | The automation/agent run or the code-diff analysis (class (a)-(e) + the located page/script/BO) |
| **Fix Description** | Tool | The change-list / commit summary from wd-extend-dev (what actually changed) |
| **Status** | Tool | The workflow state (Open / Retest / Successful / Closed-environment) advanced by the run + close-out |
| **Approval ID** | Tool | The change-control / case reference the fix or CR is tied to |

**Rule:** a tool-driven update writes only tool-owned columns; the human-owned
columns are set by a person and are never machine-overwritten (a run may READ them,
never clobber them). When wd-smartsheet writes results to a register, it respects
this split.
