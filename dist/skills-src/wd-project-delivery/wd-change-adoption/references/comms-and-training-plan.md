# Communications plan & training plan

The two "make people ready" plans. This skill owns the PLANS; the executional skills own the build:
wd-comms drafts each message from the comms plan; wd-kt builds and delivers the training the training plan scopes.

## Communications plan (the matrix)

The communications plan is a matrix - one row per planned communication across the whole program. It is the
single source of truth that tells wd-comms what to draft, for whom, and when. Standard columns:

| Column | What it holds |
|---|---|
| Phase / wave | Which lifecycle phase or go-live wave this belongs to |
| Target date | When it must reach the audience (drives the draft/review lead time) |
| Audience | The stakeholder group (from the stakeholder analysis) - and their security role if relevant |
| Topic / theme | The subject, tied to the period's single theme |
| Purpose / key message | What the audience should know/feel/do afterward |
| Channel / vehicle | Email, town hall, intranet/site, newsletter, Teams, manager cascade, job aid |
| Sender | Whose name it goes out under (sponsor, PM, manager) - credibility matters |
| Owner + draft/review/send dates | Who writes it and the internal lead-time milestones |
| Status + link | Draft/approved/sent, and a link to the final artifact |

Disciplines:
- **Cadence over volume.** Sequence comms on a **countdown-to-go-live** rhythm (e.g. milestones at
  ~6 months / 3 months / 1 month / go-live / +30 days) and give each period a **single theme** - every message
  that period reinforces it. Steady drumbeat beats a pre-go-live flood.
- **Match intensity to impact.** High-impact populations (from the change-impact assessment) get more touches,
  more senior senders, and two-way channels; low-impact groups get awareness only.
- **Use existing channels and the informal network.** Reuse the client's real channels and let managers +
  the change network cascade - a message from a manager lands harder than one from the project.
- **Two-way, not just broadcast.** Build in feedback capture (survey, ambassador log, Q&A) so comms respond
  to actual confusion (readiness results feed the next theme).
- **Hand-off:** each row's actual wording is drafted by **wd-comms** (tone, per-client branding), inheriting
  the audience/channel/sender/timing/theme from this matrix. This skill plans; wd-comms writes.

## Training plan

### Training-needs analysis
Before building anything, determine **who needs to learn what, to what depth, by when**. Drive it from the
**role mapping** (impact-and-readiness.md): for each role, list the tasks it must perform Day-1, the current
skill gap, the depth needed (awareness / can-do-with-a-job-aid / proficient), and the go-live date that sets
the deadline. The output is a role x curriculum matrix - the scope contract for the content build.

### Role-based curriculum plan
- **By role, not by feature.** Each role gets only the tasks it actually performs - avoid one giant course.
- **Right format for the need:** instructor-led / virtual for complex or high-impact tasks; short recorded
  or self-paced modules for simpler ones; **job aids / quick reference** for point-of-need "how do I do X".
- **Delivery timing:** just-in-time - deliver close to go-live so it is fresh (training too early is forgotten).
- **Materials owner:** the actual guides, job aids, module content, and KT sessions are built and delivered by
  **wd-kt** (which owns authoring conventions and the user/admin-guide patterns). This plan scopes and
  schedules them; it does not write them.

### Pilot inside UAT (a testing activity, not an afterthought)
Pilot the training with real users **during UAT/UXT**, before go-live:
- It validates the materials against the actual built system (screens/steps match).
- UAT confusion is a **readiness signal** - it surfaces comms gaps and new FAQ/job-aid needs, not just defects.
- It gives the change network hands-on time so they can support their peers at go-live.

### Evaluate & sustain
Plan post-go-live sustainment: knowledge checks, a refresh/repository for new joiners, and an owner for
keeping materials current through the next Workday release. Adoption metrics (adoption-measurement.md) tell you
where training did not stick and needs a follow-up.

## Where these go

Comms plan -> drives wd-comms drafting; dates on the project plan (wd-pm). Training plan -> scopes wd-kt's
content build and KT sessions; training milestones on the project plan; role x curriculum derived from the
role map. Both plans reference the change-impact severity to size effort per population.
