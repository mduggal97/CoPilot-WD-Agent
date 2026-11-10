---
name: wd-kt
description: Knowledge transfer and client enablement for Workday Extend apps - user guides, admin guides, training, documentation for the client, handoff to client developers, runbooks, KT sessions, teach-the-client-team enablement. Also owns RELEASE NOTES authoring, the per-integration KT document, and the training/facilitator DECK. Use when producing any end-of-project documentation (user guide, admin/config guide, support runbook), release notes for an enhancement, the integration KT document, a training/facilitator deck, planning or running KT/training sessions, or transitioning code ownership to client developers.
---

# wd-kt - Knowledge Transfer & Client Enablement

Part of the Workday Extend delivery-lifecycle suite. This skill covers the KT phase:
turning a delivered Extend app into something the client can run without the delivery team.

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **A user guide / admin guide** (the end-user + admin document) | [references/user-guide-pattern.md](references/user-guide-pattern.md) |
| **The dual-audience spec** (end-user vs admin content split) | [references/dual-audience-spec.md](references/dual-audience-spec.md) |
| **A training / facilitator deck** | [references/training-deck.md](references/training-deck.md) |
| **Planning + running KT sessions** | [references/kt-sessions.md](references/kt-sessions.md) |
| **A per-integration KT document** | [references/int-kt-template.md](references/int-kt-template.md) |
| **A support triage runbook** (owner/duration/success/failure/rollback/escalation) | [references/triage-runbook-pattern.md](references/triage-runbook-pattern.md) |
| **Handing code ownership to client developers** | [references/client-dev-enablement.md](references/client-dev-enablement.md) |
| **Rebrand + screenshot masking** for client-facing docs | [references/rebrand-and-screenshot-mask.md](references/rebrand-and-screenshot-mask.md) |
| **Regenerating the KT scripts** (build-spec) | [references/scripts.md](references/scripts.md) |

## KT philosophy

KT succeeds when the client can **operate**, **support**, and **extend** the app
without the delivery team on the phone. Plan every KT effort backwards from those three verbs:

- **Operate** - end users complete their tasks; admins run schedules, manage security,
  maintain config attributes.
- **Support** - the support desk can triage an error to a fix or a clean escalation.
- **Extend** - a client developer can safely make and deploy a change.

If a deliverable or session doesn't move one of those verbs, cut it.

## Audience mapping (do this first)

**Upstream scoping.** If a change/OCM workstream is running, **wd-change-adoption** already
scopes this KT build: its training-needs analysis and role-based training plan define which roles
need what training and to what depth. Inherit those audiences and depth targets rather than
re-deriving them - `wd-change-adoption` owns the needs analysis and training plan; this skill
builds the CONTENT and runs the sessions they call for.

Before writing anything, map audiences to deliverables. Every KT plan names four audiences:

| Audience | Deliverable | Session |
|---|---|---|
| End users | User guide + training | Per-role walkthrough, demo-then-do |
| Client admins | Admin/config guide: security (ISSG/ISU), tenant tasks, config attributes, schedules | Admin working session |
| Client developers | Code walkthrough, change-list workflow, dev environment setup | Joint working sessions on their first real changes |
| Support desk | Triage runbook: symptom -> likely cause -> fix or escalate | Runbook walkthrough with live log review |

Integration-only apps (no UI) have no end-user audience - the "user guide" becomes an
operations guide for the Integration Administrator (see `references/user-guide-pattern.md`),
and the admin deliverable is the per-integration KT document
(`references/int-kt-template.md`).

## Completeness checklist

KT is done when EVERY audience above has all three:

1. **A deliverable** - written, delivered, and stored in the app's document folder.
2. **A session** - held, recorded, transcript captured.
3. **A named recipient who has DEMONSTRATED the skill back.** Teach-back beats
   attendance: "Maria ran the schedule and cleared a failed run herself" counts;
   "Maria attended the session" does not.

Track this as a table (audience x deliverable / session / named recipient / teach-back
date) - it becomes the KT sign-off artifact. See `references/kt-sessions.md`.

## Deliverable patterns

- **User guide** - per-role sections, screenshot-per-step, plain language, FAQ,
  error-message table. Full pattern: `references/user-guide-pattern.md`.
  Screenshots and examples use **synthetic / scrubbed** data - no real PHI/PII or secrets in a guide
  (owner rule: wd-extend-lifecycle `references/ai-data-governance.md` section 6).
- **Reuse / transfer a deliverable** - to another client, the reuse catalog, or a demo: rebrand it AND
  **OCR-mask sensitive data out of embedded SCREENSHOTS** (not just the text) - a text-only pass leaves
  client data sitting in the images. Full pipeline: `references/rebrand-and-screenshot-mask.md`
  (operationalizes the no-client-data rule above for image content; ties to wd-practice-ops reuse catalog
  + wd-demo).
- **Dual-audience document** - Part 1 business / Part 2 technical, for specs and
  post-production guides. Full pattern: `references/dual-audience-spec.md`.
- **Client-developer handoff** - change-list workflow, comment verification, wdcli
  onboarding, co-ownership etiquette. Full pattern: `references/client-dev-enablement.md`.
- **Triage runbook** (support desk) - five-way triage decision tree, escalation
  packets (delivery-team ticket vs Workday case), top-10 what-if scenarios seeded from
  hypercare tickets, error-table superset. Full pattern:
  `references/triage-runbook-pattern.md`.
- **Integration KT document** - the per-integration operations reference for
  Studio/EIB/CC/DT/O4I handoffs (services, attributes, maps, ISU/ISSG,
  launch + scheduling, periodic maintenance, error handling, event review).
  Full pattern: `references/int-kt-template.md`; regenerate the blank template via
  `scripts/build_int_kt_template.py`, or obtain the firm's branded master per
  engagement (environment memory) - see `references/scripts.md`.
- **Training / facilitator deck** - the standard facilitator-deck skeleton (Cover ->
  Agenda -> Roles -> per-module divider/content/exercise -> summary -> Q&A) plus the
  presenter-notes discipline (talk-track + timing + SME-validation flag per content slide;
  draft callouts in notes only). Full pattern: `references/training-deck.md`; rendering via
  **pptx** (neutral formatting).
- **KT session series** - per-audience sessions, demo-then-do, teach-back tracking,
  sign-off; plus the topic-level **KT Plan workbook** (NS->U->D->R status ladder,
  per-topic transferor/transferee/sign-off rows; regenerate the blank workbook via
  `scripts/build_kt_plan.py`, or obtain the firm's branded master per engagement
  (environment memory) - see `references/scripts.md`). Full
  pattern: `references/kt-sessions.md`.

## Keeping KT docs current after a change

Every enhancement to a live app invalidates part of the KT set. Run this per-audience
refresh checklist, keyed to what changed - same audiences as the mapping table above:

| Change type | Refresh |
|---|---|
| UI change (page/pod/field visible to users) | User guide - affected screenshots + walkthrough steps; a training delta (what's different, not a full re-run) for end users |
| New App Attribute, security domain, ISU/ISSG, or schedule | Admin/config guide section + the Deployment Guide (wd-deployment owns the deployment guide - `references/deployment-guide.md`; update via that skill, don't fork a copy here) |
| New failure mode / error message / validation | Runbook: one new error-table row (*what the user sees -> what it means -> what to do*); mirror it in the user guide's error table if user-facing |
| New/changed code a client developer maintains | Comment sweep on the changed files (KT-level comments section below); change-list delivered per wd-extend-dev's workflow |

Bump the affected doc's version (v1.0 -> v1.1) and note the app product version it
matches. An unrefreshed guide is worse than none - it teaches the prior behavior
with confidence.

## Day one for a new administrator

When a NEW client admin inherits a live app (turnover, backfill, or a fresh hire
after KT closed), hand them this starter path rather than re-running full KT:

- **Reading order across the doc set:** admin/config guide -> Deployment Guide
  (wd-deployment `references/deployment-guide.md`) -> triage runbook
  (`references/triage-runbook-pattern.md`) -> session recordings for anything
  still unclear. In that order - the guides answer most questions the recordings
  ramble through.
- **First-week self-checklist** (mirrors the teach-back tasks in
  `references/kt-sessions.md`):
  - Run the monitoring runbook once end-to-end (wd-post-go-live owns its content)
  - Locate the app's schedules, ISU credentials, and App Attributes in the tenant
    (don't change anything - just prove you can find them)
  - Walk one mock ticket through the triage runbook's decision tree
- **Named-recipient rule applies:** the KT tracking table row for admins reopens on
  turnover (kt-sessions.md) - the new admin becomes the named recipient and owes a
  teach-back, even self-administered via this checklist.
- **When to engage the delivery team for refresh KT:** if the self-checklist stalls, or the app
  has changed materially since the guides' versions. Under a support agreement,
  refresh KT for a new admin is a named included-or-charged item - the
  managed-services path (**wd-post-go-live** `references/managed-services.md`).

## Release notes (this skill owns authoring)

Every enhancement shipped to a live app gets release notes for its subscribers/users.
The mini-pattern is three fields per change - nothing more:

1. **What changed** - one plain-language line per change.
2. **Opt-in vs. automatic** - does the subscriber see it without doing anything, or
   must they enable it (e.g. a new config attribute defaulting to prior behavior)?
3. **Action required** - what an admin must do (new security grant, attribute value,
   schedule), or explicitly "none."

wd-kt owns authoring these; **wd-deployment's marketplace re-cert checklist
(`references/marketplace-recert.md`) consumes them** as a required item, and wd-comms
renders any end-user-facing version (its templates section 7 note).

## Writing standards

- Plain-language standard owned by **wd-extend-lifecycle** (SKILL.md "Writing standard").
  Application here: end-user material is written at the end-user reading level - no Workday
  jargon without a one-line definition on first use.
- Every screen the user touches gets a screenshot (or a clearly-marked placeholder if
  screenshots come later - grey placeholder boxes per house style).
- Error content is always a table: *what the user sees -> what it means -> what to do*.
- FAQ sections are harvested, not invented: mine UAT questions and KT-session
  transcripts (wd-pm meeting-intake captures these).

## KT-level code comments

KT-level comments (explain intent per block, descriptive names) are written DURING
development - wd-extend-dev owns that standard. This skill's job is to **verify they
exist before handoff**: sweep every script and orchestration; any file a client
developer would open cold must be readable without the original author present. Comments
are the durable KT artifact - they outlive every session recording. If a file fails
the sweep, route the fix through wd-extend-dev's workflow, don't restyle ad hoc here.

## Boundaries

- **Word document mechanics** (.docx generation, TOC, styles) -> use the `docx` skill.
- **Deployment Guide / tenant-setup guide** deliverable -> owned by **wd-deployment**
  (see its `references/deployment-guide.md`); cross-reference it from the admin guide,
  don't duplicate it. For an O4I / no-UI app the Deployment Guide is the standalone
  deliverable that carries all the ISU/ISSG/attribute/schedule setup.
- **Security in the admin/config guide** -> build it from wd-deployment
  `references/security-setup-section.md` (the novice spec: exact tasks, naming conventions,
  and the enumerated domains-and-permissions table). Don't hand admins "manage security" -
  give them the tasks, the object names to use, and every domain + its View/Modify + Get/Put.
- **Code commenting standards** -> owned by **wd-extend-dev**; this skill only audits
  that they were followed.
- **Change-list mechanics** (wdcli pull-latest + diff, list format) -> defined in
  **wd-extend-dev**; this skill covers teaching the client dev to live inside that
  workflow.

## Lifecycle neighbors

- **Upstream (scopes this build):** wd-change-adoption - its training-needs analysis and
  role-based training plan define the audiences and depth this KT effort serves; inherit them.
- **Previous:** wd-deployment (the app is live) and wd-post-go-live (hypercare).
- **KT runs in parallel with hypercare** - every hypercare ticket is KT material
  (runbook entries, FAQ items), and the KT sign-off artifact gates project closeout
  in wd-post-go-live.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
