---
name: wd-discovery
description: Run Workday Extend and integration discovery - plan requirements gathering, generate intake/kickoff questions, document current state, and structure greenfield scoping. Use whenever the user mentions discovery, discovery call prep, a scoping session, requirements gathering, current state, intake questions, kickoff questions, or asks "what should we ask the client" for an Extend app or integration build. Also use when preparing for a first client session on a new use case, reviewing a discovery doc, or turning DISCOVERY-session notes into structured discovery/requirements output. (A meeting transcript, recording, or notes meant to UPDATE a design or tracker belongs to wd-pm meeting intake; this skill owns discovery-session capture.)
---

# Workday Extend Discovery

Discovery is where Extend projects are won or lost. Every expensive late-stage surprise on a real project traces back to a question nobody asked in month one - e.g., in a master-data app, discovering mid-build that FDM object creation is SOAP-only reshaped the whole write architecture; in a grant-forms app, discovering the form was ~400 data points forced a split into two apps. The goal of this skill is to make those questions land in the first two sessions, not in E2E testing.

## Step 0: Pick the playbook

Ask one question first: **"Does a process or tool exist today that this replaces?"**

- Yes (legacy tool, spreadsheet, SAP bolt-on, manual email process) -> **Playbook A**. The current state IS the requirements document; your job is extraction and delta-mapping.
- No (net-new capability, nothing to observe) -> **Playbook B**. There is nothing to extract, so you must make the unknowns enumerable with the eight-dimension framework.
- The "process that exists today" is a **live Extend app we're enhancing** -> **Playbook C**. Current state is an artifact set, not interviews.
- The build is primarily an integration (no or minimal UI) -> run the matching playbook for the business process, then work through [references/integration-discovery.md](references/integration-discovery.md) - read it before any session that involves an external system, because vendor lead times are the usual critical path and must be surfaced on day one.

Most real projects are a mix: an existing process with greenfield extensions. Run A for what exists, B for the new parts.

For any **net-new app** (or a build above the program's size threshold), discovery closes with an options assessment - is an Extend app even the right answer, vs config/report/Prism/Marketplace/wait? - per [references/solution-options.md](references/solution-options.md), with a named client approver, before wd-design-doc starts.

## Speak the client's functional language

Discovery for a functional area (HCM, Financials, Payroll, Student, Analytics) goes better when you know
what the SKU does and the vocabulary the client uses. Before a session in a functional area, skim the
matching functional-literacy reference so you can ASK better questions and RECOGNIZE what they mean:
[references/workday-functional-skus.md](references/workday-functional-skus.md) (hub: one-platform model,
FDM/security/BP primitives, deployment sequencing, Healthcare/Higher-Ed lens) and its domain files
(HCM / Talent & Rewards / Payroll / Financials / Student / Analytics). Each SKU entry ends with an
"Integration & reporting touchpoints" note tying the functional area to our delivery surfaces (EIB /
Core Connector / Studio / O4I / RaaS / WQL / Prism / Extend). Doc-sourced from official Workday manuals.

These files own LITERACY (what the thing is, the vocabulary). Once discovery turns toward HOW to build,
hand off to the **wd-solution-playbooks** skill: its per-domain playbooks carry the configuration objects,
the exact web services / RaaS / WQL sources, delivered connectors, named donor apps, and design gotchas
for the same functional areas - the bridge from "I understand the client's need" to a concrete technical design.

## Playbook A: An existing process or tool exists

### Request before the first call

Ask for these artifacts up front so the first session is spent confirming, not describing. People explain their process badly from memory but correct artifacts quickly.

- Current-state process documentation (SOPs, training decks, job aids) - even stale ones reveal the intended process, and the gap between intended and actual is itself a finding.
- Screenshots or a recorded walkthrough of the legacy tool, plus any exports of its configuration (form fields, dropdown values, routing rules). Legacy field lists become your first-draft data model.
- Sample data files - real (anonymized) transactions, not templates. Real data exposes the messy cases templates hide (e.g., in a reconciliation app, sample vendor statements revealed formats were so non-standardized that OCR/file-upload was dropped for manual paste in MVP - a decision only real samples could force).
- Volumes reports: transactions per year, by month if possible. You will need these numbers again for Workday's Volumes Questionnaire, so capture them now with a source you can cite.
- An org chart or role list of everyone who touches the process - initiators, approvers, admins, downstream consumers. Missing actors found late become missing screens and missing security groups.
- Existing SLAs, deadlines, or compliance requirements attached to the process (month-end close, audit windows, regulatory retention).

### Interview guide for process owners

Interview around specific instances, not generalities - "walk me through the last time you..." gets ground truth; "how does the process work" gets the org chart's fiction.

- "Walk me through the last time you processed one of these, click by click."
- "Now walk me through one that went wrong. What broke? Who fixed it and how?"
- "What are the exceptions - the 10% that don't fit the happy path? How often does each occur?" (Exceptions drive most of the build cost; count them.)
- "Are there seasonal peaks - fiscal year-end, enrollment, close week? How bad?" (Feeds volumes AND performance testing later.)
- "Who approves, and does the approver ever change based on amount, type, or org?" (Conditional routing is a design decision, not a detail.)
- "What do you do outside the tool - side spreadsheets, emails, sticky notes?" (Shadow workarounds are unstated requirements.)
- "If you could change one thing, what?" (Separates 'replicate' from 'improve' scope.)

### Map current state -> future Extend state

Build a two-column table: current step -> future step, marking each future step as *replicated*, *improved*, *automated*, or *eliminated*. Do this in the session with the client watching, because clients validate deltas far better than blank slates. Every "improved/automated" row needs an explicit client decision on record - silent improvements are how scope creeps. Legacy behaviors the client wants dropped go on record too; someone will ask for them back in UAT and you want the decision dated.

## Playbook B: Greenfield (no current state)

With nothing to observe, unknowns are unbounded unless you impose structure. Walk all eight dimensions in order - each unasked dimension is a category of surprise you've chosen to accept. Cover every dimension at least shallowly before going deep on any one; a shallow pass over all eight beats a deep dive on three.

### 1. ACTORS - who touches this?

- Who initiates? Who approves (how many levels, does the chain vary)? Who administers configuration? Who only views?
- Are all users workers in Workday? Non-worker users (external vendors, affiliates, students) change the security and licensing picture fundamentally - ask early.
- For each actor: roughly how many people, and are they mapped to an existing Workday security group or is a new one needed? (e.g., in a grant-change app, routing to "the primary grant's manager only" required a brand-new security group auto-populated by a daily integration - a whole workstream discovered only by asking who exactly approves.)

### 2. TRIGGERS - what starts the process?

- User action (someone opens a form)? A schedule (nightly, month-end)? A Workday business-process event (hire, termination, close)? An external system pushing data?
- Can multiple triggers start the same process? What prevents duplicates?
- Is there a deadline pressure on the trigger (must complete before payroll, before close)?

### 3. DATA - what's captured and where does truth live?

- List every field the user enters vs. every field derived from Workday. Derived data needs a source (WQL, RaaS, web service) - name it per field. Then verify the tenant actually HOLDS the native data before designing on it (a bare dev tenant will not) - trust-but-verify (wd-extend-lifecycle/references/verify-in-tenant.md).
- Where does master data live? **FDM objects (cost centers, funds, programs, worktags) are SOAP-only for creation** - if the app creates master data, that constraint shapes the whole write architecture. Ask now.
- Attachments: required, optional, size/type limits, who can see them?
- Reference data / dropdowns: sourced live from Workday, or maintained as app config? Who maintains it?
- **Regulated-data classification (ask in session one):** does any field, attachment, or free-text/comment area carry **PII, PHI (healthcare), FERPA education records (higher-ed), or other regulated data**? Tag candidates now - this seeds the per-field classification pass at design (wd-design-doc `nfr-accessibility.md` section 5) and its downstream gates (BAA/data-protection terms, masking, retention, FERPA disclosure-basis). Free-text/notes fields default to "none" but are exactly where regulated data leaks - flag them.

### 4. VOLUMES - how much, how often?

- Transactions per year? Per peak month/week/day? (e.g., ~1,752 requests/yr vs ~1.3M invoice transactions/yr are different apps.)
- How many users total, and how many active in the peak hour?
- Multi-step approvals multiply volume: a 4-step chain means approval actions run ~4x request volume - often the highest-frequency action in the app.
- Capture these with a source now: Workday's Volumes Questionnaire and Performance Testing Template both demand them later (wd-deployment owns those documents), and re-asking the client months later is painful.

### 5. SECURITY - who may see and do what?

- For each actor x each screen/action: view, create, edit, approve? This maps directly to Extend security domains - sketch the domain list in discovery.
- Any data confidentiality within the app (e.g., comments visible to some roles only)?
- Who at the client provisions security groups, and what is their **lead time**? Client security-admin queues of weeks are common and gate every testing milestone.

### 6. INTEGRATIONS - what flows in and out?

- Upstream sources and downstream consumers, per system: direction, auth method, format, frequency. Then go run [references/integration-discovery.md](references/integration-discovery.md) for the full questionnaire.
- Don't forget Workday-internal "integrations": RaaS reports, Boomerangs, orchestrations that must be built and scheduled.

### 7. REPORTING - who needs what, rolled up how?

- Who consumes reports, at what grain? Pin the grain early - e.g., in a variance app, choosing cost-center *hierarchy node* vs. individual cost center as the reporting grain drove the entire data design.
- In-app views vs. delivered Workday reporting on the Extend data source vs. Prism? Each has different cost and refresh characteristics.
- Reporting requirements are legitimately deferrable - but log the deferral as an open item, don't drop it.

### 8. LIFECYCLE - what happens after submit?

- Corrections and cancellations: can a submitted request be recalled, revised, sent back? By whom, at which steps? (Send-back from a non-inbox surface is a real design constraint in Extend - flag it if the answer is yes.)
- Retention: how long is data kept, and is there a purge/archive requirement? Who owns that policy (often a data-governance group, not the process owner)?
- Audit: who asks "who changed what, when," and what would they need to see?

### Techniques that make greenfield sessions work

- **Scenario walkthroughs.** "Pretend it's live. A request just came in - narrate exactly what happens next, person by person." Concrete narration surfaces actors, triggers, and exceptions that abstract questioning never finds. Run at least three scenarios: the happy path, a rejection/send-back, and a correction after the fact.
- **Straw-man first, correct second.** Draft a rough process flow in or immediately after the first session and put it in front of the client - people correct a wrong diagram far better than they specify a right one from nothing. Expect to be wrong; being correctably wrong is the fastest path to right.
- **Timebox unknowns.** When an answer needs someone not in the room, spend two minutes capturing it as an open item with an owner and move on. A stalled session waiting for an answer costs more than a logged open item. (Recording and formatting of open items follows the **wd-design-doc** skill's conventions - don't invent your own.)

## Playbook C: Enhancing a live Extend app

Don't interview people about an app whose truth is fully inspectable. Assemble the artifact set first:

- The **latest signed design doc + IDD** - the baseline the change amends (versioning per **wd-design-doc**).
- The **deployed source**: `wdcli app download` + the audit sweep in **wd-extend-dev** references/app-review-audit.md - the as-built state, which may have drifted from the doc.
- **Production volume actuals** vs what the Volumes Questionnaire claimed (wd-deployment owns that doc) - growth beyond the approved envelope is itself a finding - count actuals directly via tenant-ops WQL (aggregate counts only; wd-extend-dev references/tenant-ops.md).
- The **hypercare/support backlog** - known defects and workarounds the enhancement should absorb or explicitly exclude.

Then delta-map **only the changed behavior**, reusing Playbook A's replicated/improved/automated/eliminated table at feature grain - unchanged features get one "replicated" row, not a re-discovery.

## Answering client asks in-session (all playbooks)

When the client asks "can it do X?" mid-session, use the four answer shapes from **wd-demo** references/demo-playbook.md - yes-live / yes-not-built / roadmap-candidate / no-and-why - never an improvised yes. This matters MOST in discovery because sessions often run pre-contract or pre-design: a casual "yes" here becomes a commitment the client remembers at UAT and a dispute exhibit if the relationship sours. "Roadmap / candidate" plus an open-item row is the honest default for anything not yet designed; anything you do affirm goes on record as a decision or requirement, not just in the air.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Client legal entities** - the entity or entities in scope (a client often has several with separate procurement/finance orgs). Always ask whether scope, thresholds, and routing differ **by entity** - they usually do; a multi-entity client is a routing/threshold design decision, not a detail.
- **Legacy source systems** - the current-state tools/ERPs being replaced or integrated (planning/EPM tools, ERP bolt-ons, home-grown or nicknamed legacy systems). Get their names and ask about each by name - legacy field lists and formats seed the data model.
- **Dev -> go-live window** - the delivery arc (discovery -> design sessions -> dev -> E2E test -> go-live) and this program's actual dev-start and go-live dates. Confirm the live dates from memory or the client; do not carry a date forward from another engagement or an older design doc.
- **Purchased / pre-built apps to reuse** - any platform, Marketplace, or previously-purchased apps the client already has (e.g. a user-access-request app). Check before designing overlapping functionality - role/view-access requests, for instance, often route to an existing app rather than being built per-app.
- **Use-case / app ID conventions** - how this program numbers use cases, apps, and integrations (e.g. a use-case ID scheme, an app-ID scheme, INT IDs), and the standard shape of discovery inputs (e.g. a numbered discovery doc plus a partially-filled IDD workbook - treat the IDD as a starting checklist, not the finished product).

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).

## Acceptance criteria - every captured requirement gets testable ones

A requirement isn't captured until its acceptance criteria are **observable and testable** (pattern from a community skill-craft survey, 2026-08-06 - rebuilt for this suite). Each criterion has three parts: a **trigger** (when/given), an **outcome** (then), and a **verification method** (how we'll know - a demo step, a unit-test scenario, a report to check). Vague adverbs are BANNED in criteria - "correctly," "properly," "securely," "quickly" name a feeling, not a behavior; replace each with the observable behavior it stands for ("quickly" -> "the grid loads in under N seconds at peak volume," with the client supplying N).

Two tiers, sized to the stakes:

- **Quick capture (3-7 criteria)** for routine requirements - jot them in the session as the requirement lands.
- **Full acceptance brief** for risky or contested scope (anything already argued about, anything with a compliance or dollar edge): criteria plus explicit out-of-scope statements, agreed line by line with the client.

The skill's epistemics rule still governs (it's why Playbook C inspects instead of interviews): facts discoverable from artifacts, code, or the live tenant (tenant-ops reads: data-source inventory, custom-object definitions, RefID liveness - wd-extend-dev references/tenant-ops.md) are gathered, not asked; business constraints and thresholds MUST come from the client and get attributed (who, when). Criteria feed **wd-testing**'s scenario derivation 1:1 - a requirement whose criteria can't be turned into a test scenario isn't testable yet, which means it isn't done.

## Capturing output

Every session produces three artifacts: answered questions (with who answered and when - answers get relitigated), open items (owner + due date), and decisions (what was decided, alternatives rejected, date). Also capture **3-5 outcome-metric baselines** (cycle time, hours saved, error rate - with measurement source) during discovery, alongside the volumes questions - see wd-post-go-live `references/value-capture.md`. How these land in the design document - Discovery-tab Q&A format, open-items handling, volume answers flowing forward - is covered in [references/discovery-to-design.md](references/discovery-to-design.md); read it when you're ready to write discovery results up. Yellow-highlight and open-items formatting conventions are owned by the **wd-design-doc** skill.

## Reference map - read what you need

- [references/integration-discovery.md](references/integration-discovery.md) - the integration questionnaire; read before any session involving an external system or vendor.
- [references/discovery-to-design.md](references/discovery-to-design.md) - how discovery output lands in the design doc; read when writing up results.
- [references/solution-options.md](references/solution-options.md) - the options-assessment matrix (Extend vs config vs Prism vs Marketplace vs wait) at the pursuit->design boundary; required for any net-new app.
- Functional-literacy domain files (HCM / payroll / financials / student / analytics / talent-rewards): via [references/workday-functional-skus.md](references/workday-functional-skus.md) (hub) - the six domain cribs hang off this sub-hub, not the SKILL.md list.

---

## Lifecycle neighbors

previous = **wd-estimate** (RFP/LOE - discovery validates or corrects the estimate's assumptions), next = **wd-design-doc** (design authoring - discovery answers feed the design doc's Discovery tab).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
