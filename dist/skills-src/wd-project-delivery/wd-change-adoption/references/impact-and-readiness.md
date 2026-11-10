# Impact, readiness, stakeholders & the change network

The "who is affected, how ready are they, and who helps drive it" half of the OCM workstream. All artifacts
here are vendor-neutral and reusable on any Workday program.

## Stakeholder analysis

Map every impacted group before planning anything else. For each stakeholder group capture:
- **Group / role** and an approximate headcount.
- **Impact** (how much their day-to-day changes: High/Med/Low) and **influence** (how much sway they hold).
- **Current sentiment** (supportive / neutral / resistant) and the **shift you need**.
- **What they need from us** (information, involvement, training, reassurance) and **who owns the relationship**.

Plot impact x influence to prioritize: high-impact/high-influence groups get sponsor-level engagement;
high-impact/low-influence groups get the most training and support; low-impact groups get information only.
This feeds the communications plan (who is an audience) and the training plan (who needs curriculum).

## Change-impact assessment

The core "what actually changes" artifact. For each impacted process/role, record:
- **What changes** (process, system, policy, who-does-what), **from -> to**, and **why**.
- **Severity** rated **High / Med / Low** against a fixed rubric (define it once - e.g. High = new system of
  record or a role's core task changes; Med = same task, new steps/screens; Low = cosmetic/awareness only).
- **Population affected** and **when the change lands** (which phase / go-live wave).
- **Mitigation** (comms, training, job aid, staffing, policy update) and **owner**.

Disciplines:
- **One tracker.** Change impacts live in the program's existing RAID/tracker (wd-pm / wd-smartsheet), not a
  parallel spreadsheet - a second tracker drifts and no one trusts either.
- **Validate against the real design**, not assumptions: cross-check impacts against the business-process
  inventory, the design doc, and session notes (wd-design-doc), so the assessment matches what will actually ship.
- Severity should **drive** the comms/training intensity for that population - a High impact with a Low-touch
  plan is a gap to flag.

## Readiness assessment (repeated rounds)

Measure whether the organization is getting ready - do not wait until go-live to find out it is not. Run the
same short survey/checklist at 2-3 points (e.g. after strategy, mid-build, before go-live) so you can see the
trend, not a single snapshot. Cover: awareness of the change and its timing, understanding of "what's in it
for me", confidence to perform Day-1 tasks, and perceived support. Pair the survey with a **readiness
checklist** of concrete conditions (training delivered, access provisioned, data staged, support channel live).
Falling or flat readiness on a High-impact group is an escalation, not a footnote.

## Role mapping (the hinge)

Map each **job role -> the Workday security role/profile it will use -> the tasks it performs -> the training
it needs**. This single matrix keeps three workstreams aligned:
- **Security** - it tells wd-deployment / wd-discovery (dimension 5) which security groups each role needs.
- **Training** - it tells the training plan which curriculum each role gets (role-based, not one-size-fits-all).
- **Change impact** - a role whose mapping changes a lot is a High-impact population.
Keep it current as config and security design evolve; a stale role map trains the wrong people on the wrong tasks.

## Sponsorship & the change network

Two tiers of people carry adoption; plan both:
- **Executive sponsors / steering** - visible, active, and vocal support (the single biggest predictor of
  adoption). Equip them with talking points and decision asks (steering mechanics live in wd-pm
  references/steering-committee.md; this skill supplies the change narrative they carry).
- **Change network** - department-nominated champions / ambassadors / super-users (a light, ~2-4 hrs/month
  commitment) who are the local face of the change, a two-way feedback channel, and early training pilots.
  Plan the network kit: nomination + welcome + reminder notes (drafted by wd-comms from your plan), a simple
  feedback log (in the RAID tracker), and a short "how to talk about this change" guide for ambassadors.

## Where these go

Impacts and readiness actions -> the RAID log (wd-pm). Role mapping -> shared with wd-deployment (security) and
the training plan (comms-and-training-plan.md). Sponsor/network engagement dates -> the project plan (wd-pm).
The message drafts these artifacts imply -> wd-comms, sequenced by the communications plan.
