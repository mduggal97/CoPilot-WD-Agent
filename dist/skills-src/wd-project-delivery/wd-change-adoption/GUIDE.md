---
name: wd-change-adoption
description: Plan and run the organizational change management (OCM) and user-adoption workstream for a Workday program - the people side that runs parallel to the build so users actually adopt what ships. Use for change management, OCM, a change plan / strategy, stakeholder analysis, change-impact assessment, change readiness (assessment/survey), a change network / champions / super-users, a communications PLAN or matrix (program-level who/what/when/channel), training-needs analysis or a role-based training PLAN, adoption metrics, resistance management, or "build the change plan / how do we drive adoption". Use THIS for the OCM program structure and its planning artifacts; an individual client-facing MESSAGE is wd-comms (THIS owns the comms PLAN that tells it what to write); training CONTENT, guides, job aids, and KT sessions are wd-kt (THIS owns the training PLAN that scopes them); post-go-live adoption feedback is wd-post-go-live; project plan / RAID / status is wd-pm.
---

# wd-change-adoption - Organizational Change Management & Adoption

The build can be perfect and still fail if people do not adopt it. This skill owns the **people side** of a
Workday program: identify who is impacted and how, get them ready, communicate on a disciplined cadence,
train by role, and measure adoption - so the delivered app/integration actually gets used. It plans the
program; the executional skills do the doing (wd-comms drafts the messages, wd-kt builds the training,
wd-post-go-live runs the live feedback loop).

## When to use this skill

- Standing up the **change/adoption workstream** on a new program, or writing the **change strategy/plan**
- **Stakeholder analysis** (who is impacted, influence vs. impact) and building a **change network** (champions/ambassadors)
- **Change-impact assessment** - what changes for whom, rated, with mitigations
- **Change-readiness** assessment/survey rounds and readiness workshops
- Building the **communications plan / matrix** (audience x message x channel x cadence) that drives wd-comms
- **Training-needs analysis** and the **role-based training plan** that scopes wd-kt's content build
- Defining and tracking **adoption metrics** (are people actually using it, and well)
- **Resistance management** and go-live people-readiness inputs

## The workstream at a glance

OCM runs as one continuous workstream across the whole lifecycle, not a go-live-week scramble. Five moving
parts, each with an owning reference:

| Part | What it produces | Reference |
|---|---|---|
| Impact & readiness | stakeholder analysis, change-impact assessment, readiness assessments, role mapping | [references/impact-and-readiness.md](references/impact-and-readiness.md) |
| Communications plan | the comms matrix + cadence that feed wd-comms | [references/comms-and-training-plan.md](references/comms-and-training-plan.md) |
| Training plan | training-needs analysis + role-based curriculum plan that scope wd-kt | [references/comms-and-training-plan.md](references/comms-and-training-plan.md) |
| Adoption measurement | leading/lagging adoption metrics + the measurement program | [references/adoption-measurement.md](references/adoption-measurement.md) |
| Sponsorship & network | sponsor/steering engagement + the change network operating model | [references/impact-and-readiness.md](references/impact-and-readiness.md) |

## How it threads across the lifecycle

- **Discovery/Plan:** change strategy; stakeholder analysis; stand up the change network; first readiness
  assessment; draft the communications plan (baseline adoption metrics captured with wd-discovery's outcome metrics).
- **Design/Build:** change-impact assessment (rated, mitigations); role mapping (the hinge to security + training);
  ongoing comms on cadence; training-needs analysis; second readiness assessment.
- **Test:** build training content (wd-kt) and **pilot it inside UAT** - training validation is a testing
  activity, and UAT feedback surfaces comms/readiness gaps; third readiness assessment.
- **Deploy/Go-live/Post:** cutover + go-live comms; just-in-time training delivery; people-readiness go/no-go
  input; then the live adoption feedback loop hands to **wd-post-go-live** (adoption-and-feedback.md).

## Core disciplines (the non-negotiables)

1. **One impact tracker, not two.** Change impacts are rated High/Med/Low and tracked in the program's
   existing RAID/tracker (wd-pm / wd-smartsheet) - never a parallel spreadsheet that drifts.
2. **Cadence beats volume.** Communications run on a countdown-to-go-live cadence with a single theme per
   period; every message ties to the plan. The plan lives here; wd-comms drafts each message from it.
3. **Role mapping is the hinge** between functional config, security profiles (wd-deployment / wd-discovery
   dimension 5), and training curriculum - keep the three aligned or training teaches the wrong people.
4. **Pilot training in UAT**, not after go-live - and treat UAT confusion as a readiness signal, not just a defect.
5. **Adoption is a measured outcome**, not a hope - baseline at discovery, target at design sign-off, and
   during hypercare **low usage is a Sev2-equivalent finding** (wd-post-go-live).
6. **Name the CM owner early (RACI).** On many engagements the client owns the CM lead role and the delivery
   team advises - set that in wd-pm's RACI at kickoff so nobody assumes the other side has it.

## Boundaries

- **wd-comms** owns drafting an individual client-facing message to tone/branding. THIS skill owns the
  communications PLAN/matrix (audience, channel, sender, cadence, theme) that tells wd-comms what to write and when.
- **wd-kt** owns building training content, user/admin guides, job aids, and running KT sessions. THIS skill
  owns the training-needs analysis and the role-based training PLAN that scope that build.
- **wd-post-go-live** owns the live adoption feedback loop, champions-in-hypercare, and low-usage findings
  after go-live. THIS skill owns the adoption-metric DEFINITIONS and the pre-go-live measurement program.
- **wd-pm** owns the project plan, RAID log, and status. THIS skill's impacts/actions live in that RAID log,
  and its milestones go on that plan.
- **wd-discovery** owns requirements discovery; the change-readiness/CM discovery questions here complement it.
- **wd-delivery-methodology** owns the full-program delivery phase model this OCM workstream runs parallel
  to; align change milestones to its phases. A firm-private methodology skill (not installed here) layers on
  top of both (one-way coupling): it may draw on this skill, but do NOT import any proprietary methodology
  content into this skill - keep this base brand-agnostic.

## Lifecycle neighbors

- **Runs parallel to** the whole delivery lifecycle (not a single phase).
- **Feeds:** wd-comms (message plan), wd-kt (training plan), wd-deployment (people-readiness go/no-go, role
  mapping -> security), wd-post-go-live (adoption metrics + the feedback loop it continues).
- **Draws from:** wd-discovery (impacted-population + outcome-metric baselines), wd-pm (RAID + RACI + plan).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle
`references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
