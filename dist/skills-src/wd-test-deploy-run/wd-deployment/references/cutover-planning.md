# Cutover Planning - Data Conversion, Legacy Coordination, Go-Live

Cutover = the coordinated switch from the legacy process to the Extend app in
production. Three workstreams: data conversion, legacy-system coordination,
and go-live-day execution.

## 1. Data conversion (legacy data -> Extend BOs)

### Decide WHAT converts

Not everything should. For each Extend business object, classify:

- **Reference/config data** (config BOs, threshold tables, select-list
  items, room/location masters) - almost always loads; small volume; often
  the app is unusable without it.
- **Open in-flight transactions** (requests mid-approval in the legacy tool)
  - usually the hardest call. Options: (a) drain the legacy queue before
  freeze (preferred - no mid-BP state to fake), (b) re-enter open items in
  Extend after go-live, (c) load them as new records and relaunch BPs. You
  generally CANNOT recreate a legacy approval mid-chain in an Extend BP -
  plan to drain or relaunch.
- **Historical/closed records** - load only if reporting or audit needs them
  in the app; otherwise leave them in the legacy archive / data lake. (Common
  pattern: the client's data lake is the long-term system of record - history
  often belongs there, not in Extend BOs.)

### Decide HOW it loads

- **Extend BO REST batch scripts** - the default. Generated endpoints at
  `https://api.workday.com/apps/<refId>/v1/<collection>`; **reads page at
  max 100 per page** and writes are per-instance, so conversion is a script
  that loops (see the seed/wipe script precedent in
  a per-tenant seed/wipe script (author example `seed-<tenant>.ps1` / `wipe-<tenant>.ps1`; if not present, regenerate from the pattern - parent->child load, child->parent delete) - token via
  `wdcli tenant token <alias> --ci`). Load **parent -> child** order; delete
  (for re-runs) **child -> parent** to avoid referential-integrity 500s.
- **An orchestration load** - when volume is large or the load must
  transform/validate per record (bulk endpoints where the app has them,
  e.g. `bulk=true` at 100/request; Submit Extend Data-style orchestrations
  batching <=500 records). Also the right shape if the client team will rerun
  loads themselves.
- **EIB** - for delivered/select-list data that has an EIB path (e.g.,
  Select List Items), or mass migration of tenant config the app reads.
- Remember PUT is **full-replace** - a "fix-up" pass must send the complete
  payload, not a delta.

### Dry-run in IMPL - non-negotiable

Run the full conversion in IMPL (`<impl-tenant>`) exactly as
you will in PROD: same scripts, same source extract format, same sequence.
The dry run is what surfaces field-mapping surprises (null SINGLE_INSTANCE
corruption, WQL objects vs. strings, date formats) before go-live day.

### Reconciliation counts

For every loaded collection, record and compare:

- Source-extract row count -> loaded-record count (per BO)
- Rejected/errored rows, with reasons, and the disposition of each
- Spot-check totals where meaningful (sums of currency fields, distinct key
  counts)
- Sign-off: the data owner confirms the counts, not the loader

Keep the reconciliation sheet - it's day-of evidence and the rollback
baseline.

## 2. Legacy-system coordination

- **Freeze window:** define when the legacy system stops accepting new
  entries (or goes read-only). Everything entered after extract and before
  freeze is a delta you must re-extract or hand-key - keep the window short.
- **Turn-off / turn-on sequencing:** the safe order is
  1. Legacy freeze (read-only)
  2. Final extract + delta load into PROD Extend
  3. Reconciliation sign-off
  4. Extend app opened to users (security groups populated / links
     published)
  5. Legacy decommission or read-only-archive (typically weeks later, after
     hypercare)
  Never turn off legacy before reconciliation signs off - it's your
  comparison source and your rollback landing zone.
- **Comms to end users:** who is affected, what changes, the freeze dates,
  where the new app lives (Workday search/task names), training/job-aid
  links, and the support channel. Send twice: T-1 week and day-of.
- **Rollback plan:** written before go-live, with (a) the abort criteria
  (what failure severity triggers it), (b) the decision maker and the
  decision deadline ("go/no-go by noon"), (c) the mechanics - reopen legacy
  for entry, park or export any records created in Extend during the window,
  and note that **promotion is one-way**: rollback means turning users back
  to legacy and disabling access to the app (security groups), NOT
  un-promoting the app.

> **Phased conversion - use the wave scorecard.** When the conversion runs in waves, gate each wave through `references/migration-readiness-gates.md` (Pass / Conditional Pass / Fail per gate). Its cutover gate - all prior gates formally passed + an agreed rollback decision point (time + trigger) + a named decision-maker - is the entry condition for the go/no-go below; the freeze/rollback rules in section 2 still govern the calendar around it.

## 3. Go-live day checklist

- [ ] Freeze confirmed in effect; final delta extract taken
- [ ] Delta load run; reconciliation counts match; data owner sign-off
- [ ] Per-tenant setup verified in PROD (security domains active, ISU works,
      App Attributes hold PROD WIDs, BP approver chains configured - see
      `promotion-and-environments.md` matrix)
- [ ] Integration System + RaaS reports confirmed present and runnable in
      PROD (they promoted separately)
- [ ] Scheduled orchestrations enabled with the correct PROD schedule
- [ ] **Smoke test executed end-to-end by a real user account:** create a
      record -> BP routes to the right approver inbox -> approve -> write-back
      orchestration fires and the SOAP/REST result verifies -> record visible
      in reporting. Include a send-back/revise path if the app has one.
- [ ] Security groups opened to the real user population (this is the "go
      live" switch)
- [ ] Go-live announcement sent
- [ ] Monitoring in place for day 1: orchestration run logs (filter
      `wd_log_type = remote`, read `wd_response_code`/`wd_message`), BP
      event queue, and an error-report triage channel

## 4. Hypercare handoff -> wd-post-go-live

At end of day 1, hand wd-post-go-live:

- The reconciliation sheet + any open data-fix items
- The smoke-test evidence and any deferred defects (with severity)
- The hypercare roster (who staffs the support channel, for how long -
  typically 2-4 weeks), and the escalation path (client admin -> the delivery
  firm -> Workday case)
- The list of first scheduled-orchestration run dates to babysit (the first
  monthly run is a go-live event of its own)
- Legacy decommission date and who owns it

## Integration production-run cutover - the per-INT tracker

When the cutover is an **integration portfolio** (many INTs going live against
vendors, not one Extend app), track it per integration in the Production Run
Cutover workbook - **regenerate via `scripts/build_cutover_spreadsheet.py`**
(spec in `scripts.md`), or obtain the firm's branded master per engagement
(environment memory). Two working sheets (each has an
EXAMPLE twin whose sample rows are explicitly marked "delete"):

**Sheet 1 - CutoverDetails**, one row per integration, four column groups:

- **Readiness gates**, in order: *Signed off UAT? -> Moved to Gold (config
  migrated to the master/gold tenant)? -> Supporting documentation attached to the
  integration? -> GoldCopy validation run?* An integration doesn't get a first-run
  date until all four are Yes.
- **Vendor communications:** go-live email sent / vendor confirmation received,
  vendor contact, and the endpoint block the vendor conversation needs - sFTP
  description, endpoint address **per environment**, directory, user, filename
  pattern (test vs. PROD names differ by convention), temp-file use, delete-after-
  retrieval, and which keys were exchanged **and their kind (auth vs.
  encrypt/decrypt)**.
- **People:** Integration Consultant, Customer Technical SME, Customer Functional
  SME, and an explicit *"IC available for prod runs?"* column - day-of coverage is
  planned per INT, not assumed.
- **Run sequence:** *Last legacy run date/time -> go-live first-run
  prerequisites -> First run date/time in Workday -> Second run date/time in
  Workday.* Conventions: prerequisites name concrete preconditions ("payroll must
  be run", "INT062 must finish before INT001" - cross-check the dependency order);
  babysit the **second** production run too, not just the first (the second run
  proves the schedule and steady state - same instinct as the first-scheduled-run
  item in section 4); event-driven/on-demand INTs record `n/a` for legacy-run columns
  rather than blank.

**Sheet 2 - Cutover Tasks**, one row per integration: *Integration Name / IC /
Production Cutover Tasks / Done? / Notes.* This is the prod-flip punch list the
promotion matrix implies, made explicit per INT - recurring task types from the
example data: flip sequence-generator filenames from test to PROD pattern, hand
the vendor the PROD URL/WID/endpoint, exchange new PROD SSH/PGP keys, remove
test-mode attributes, verify External IDs per company, and grant any
security-group domain access the PROD run needs. **"none" is a valid entry** -
an empty cell is an unanswered question, "none" is a verified answer.

The tracker complements this file's app-centric sections: section 2's freeze/rollback
still governs the calendar; the tracker governs the per-INT mechanics. Endpoint
and re-setup mechanics stay in `promotion-and-environments.md` /
`tenant-task-recipes.md` - the tracker rows just record status and dates.

## Version-swap cutover - promoting a new version over a live app

An enhancement to an app already live in PROD is a mini-cutover of its own
(the enhancement lifecycle itself lives in `marketplace-recert.md`). The two
runtime questions that shape the plan are **not practitioner-confirmed**:

- **(!) confirm:** is Extend version promotion zero-downtime for users mid-task,
  or is there a window where pages/orchestrations serve inconsistently?
- **(!) confirm:** what happens to **in-flight BP events** created on the prior
  version when the new version lands (especially if the enhancement changes a
  Model BP, a BO the BP writes, or an orchestration a BP step calls)? **Do not
  guess - CHECK it per cutover:** query `businessProcess /events` (+ eventSteps)
  for open events on the affected BOs/BPs before the swap and use the count as
  go/no-go evidence (the live-check is in wd-extend-dev tenant-ops.md).

**Conservative default until confirmed:** treat the swap like a freeze-window
cutover in miniature -

1. Schedule the promotion in a **quiet window** (outside business hours for the
   user population; not while a scheduled orchestration is due to fire).
2. **Drain in-flight events first** - have approvers complete (or send back)
   open BP events created on the prior version before the swap; use the BP
   event queue to verify zero open events on the app's BPs (assertable live
   via tenant-ops: businessProcess events read - file the zero-count as the
   swap's go/no-go evidence).
3. Smoke-test the changed paths immediately after (same pattern as the go-live
   day checklist above), including one record created BEFORE the swap being
   read/processed correctly AFTER it.

Record the confirmed answers here once observed on a real promotion.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live:

- **IMPL tenant(s) for dry-runs** - the tenant alias(es) the conversion
  dry-run runs against, and the target PROD (go-live) window.
- **Historical data disposition** - where aged history lives long-term (e.g.,
  a client data lake with a rolling export as the standing archive answer);
  bias against loading history into Extend BOs.
- **Data Lead** - the named person who signs off conversion reconciliation
  counts (the data owner confirms counts, not the loader).

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).
