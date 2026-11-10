---
name: wd-practice-ops
description: Run the OPERATIONS of a Workday consulting practice - the meta layer that grows and runs the team, distinct from delivering any one engagement. Vendor-neutral practice management. Use for onboarding/ramping a new consultant, a competency / skills matrix, certification tracking (Workday Extend Pro, Integrations Pro, functional Pro certs, recerts), staffing / resourcing / bench / who-to-put-on-what, utilization or capacity planning across engagements, building the practice's enablement path, a reuse-asset catalog, or managing the Workday partner/alliance relationship (partner tier/status, Built-on-Workday / Innovation partner program, roadmap-intelligence intake). Use THIS for the practice layer; running a SINGLE engagement (plan/RAID/status/staffing-hours) is wd-pm; sizing/pricing a deal is wd-estimate; go-to-market for a productized app is bow-sales-enablement; the delivery craft is the wd-* delivery skills.
---

# wd-practice-ops - Workday Consulting Practice Operations

The delivery skills build the work; this skill runs the **practice** that does the building: getting
consultants productive, tracking their skills and certifications, staffing them to the right work, and owning
the firm's relationship with Workday. It is the "grow and run the team" layer, deliberately separate from any
single engagement's PM.

## When to use this skill

- **Onboard/ramp a new consultant** - get them productive on the suite, the delivery method, and their first engagement
- **Competency / skills matrix** - what each role should know, and where each person is against it
- **Certification tracking** - Workday Extend Pro, Integrations Pro, and functional Pro certifications + recert cadence
- **Staffing / resourcing** - match people (skill + availability) to pursuits and engagements; manage the bench
- **Utilization / capacity** - target utilization, capacity planning across a portfolio of engagements
- **Workday partner/alliance relationship** - partner tier/status, Built-on-Workday / Innovation partner
  program, Community + Customer Care as an ongoing relationship, and roadmap-intelligence intake

## The two halves

| Half | What it covers | Reference |
|---|---|---|
| People enablement | onboarding path, competency model, certification tracking, knowledge-sharing loop | [references/practitioner-enablement.md](references/practitioner-enablement.md) |
| Staffing & alliance | resourcing/bench/utilization/capacity, and the Workday partner/alliance relationship + roadmap intake | [references/staffing-and-alliance.md](references/staffing-and-alliance.md) |
| Reusable-asset / IP catalog | the cross-engagement register of reusable delivery assets (apps/components/patterns/templates): "prioritize by reuse", when-to-reuse decisioning, shared-component versioning, contribute-back at closeout | [references/reuse-and-asset-catalog.md](references/reuse-and-asset-catalog.md) |

## Core principles

1. **The suite is the fastest onboarding asset.** A new consultant productive on the wd-* skills + the
   methodology is productive on engagements faster; the enablement path is built around them (start at
   wd-extend-lifecycle, then the phase skills for their role).
2. **Certifications are a capability inventory, not a trophy shelf** - track them because they gate who can be
   staffed/pursued on what, and because they expire (recert cadence).
3. **Staff by capability + availability, transparently** - the skills matrix + the bench view drive staffing;
   guessing who's free is how engagements get the wrong team.
4. **The Workday relationship is an asset to tend, not a case queue** - partner status, roadmap intelligence,
   and Community presence compound over time and feed both delivery (GA risk) and sales (partner credibility).
5. **Feed the loops** - lessons learned roll into project memory + the reuse catalog
   (references/reuse-and-asset-catalog.md) + estimation calibration (wd-estimate); roadmap intelligence rolls into the GA
   tracker (wd-extend-dev release-impact.md).

## Boundaries

- **wd-pm** owns running a single engagement (plan, RAID, status, and the staffing HOURS on that project).
  THIS skill owns cross-engagement resourcing and who-goes-where.
- **wd-estimate** owns sizing/pricing a deal and calibration data. THIS skill supplies the people/skills
  availability that staffing a sized deal depends on.
- **bow-sales-enablement** owns go-to-market for a productized app. THIS skill owns the internal practice/team
  and the partner relationship, not the product's GTM.
- **wd-extend-dev release-impact.md** owns the platform GA-feature/roadmap TRACKER. THIS skill's roadmap
  intelligence intake feeds that tracker; it does not duplicate it.
- The delivery CRAFT (how to build/test/deploy) stays in the wd-* delivery skills; this skill grows the people
  who apply it.

## Lifecycle neighbors

- **Runs alongside** the whole practice (not a project phase). **Feeds:** wd-estimate (available capacity for
  staffing a quote), wd-extend-lifecycle (the onboarding entry point / router), wd-extend-dev
  (roadmap intelligence -> GA tracker). **Draws from:** every engagement's closeout (actuals, lessons, new assets).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle
`references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
