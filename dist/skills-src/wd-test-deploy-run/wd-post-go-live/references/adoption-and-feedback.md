# Adoption & Feedback - Getting the App Used, Not Just Live

Companion to `wd-post-go-live/SKILL.md`. Go-live proves the app works; adoption
proves people use it. A technically clean go-live with silent users is a failure
that surfaces at renewal, not in the defect queue. This reference covers the
light-touch adoption path (no change-management megaproject - a handful of named
moves) and the feedback loops that keep users engaged after week one.

## The light-touch adoption path

**1. Champion / super-user role (per user population)**
- **Continue the pre-go-live change network - do not stand up a new one.**
  wd-change-adoption already built and ran a change network (champions/ambassadors)
  during the build (`wd-change-adoption/references/impact-and-readiness.md` owns the
  network operating model). At go-live, that network **hands off into hypercare**: the
  same named champions become the hypercare champions/super-users below. Only fill gaps
  (a population with no existing champion) by recruiting fresh.
- One named champion per distinct user population (per role, per department where
  populations differ). For a gap, recruit from UAT testers - they already know the app,
  and the UAT wrap-up note makes the ask (**wd-testing** `references/uat-support.md`,
  Tester experience).
- The role, sized honestly (2-4 hrs/wk during go-live weeks, then ~1): first stop
  for "how do I" questions, feeds real user reactions to the hypercare stand-up,
  co-hosts office hours.
- Named champions go in the support-ownership matrix
  (`references/handoff-and-closeout.md`) under first-line user questions.

**2. People-readiness inputs to go/no-go**
The go/no-go checklist (**wd-deployment** SKILL.md) carries people-readiness gates;
this reference defines how to measure them:
- **% of target users trained** - against a threshold agreed with the client at UAT
  exit (not invented on go/no-go day); "trained" = attended a session or completed
  the job aid, per the KT tracking table (**wd-kt** `references/kt-sessions.md`).
- **Job aid distributed** - to the full user population, via a channel with receipts
  (not "it's on SharePoint somewhere").
- **Help path verified end-to-end by a real user** - one actual end user (not a
  consultant, not the champion) raises a test question through the published help
  path and gets an answer within the stated SLA. This one check catches dead
  mailboxes, wrong queue routing, and untrained help desks.

**3. Go-live-week floor support**
- Office hours (standing call or drop-in) for at least the first week, staffed by a
  champion + the on-point hypercare consultant - put it ON the hypercare roster,
  not as a side offer.
- Announced in the go-live comms (**wd-comms** owns the announcement).

**4. Adoption metric in daily hypercare monitoring**
Use wd-change-adoption's adoption-metric DEFINITIONS, don't reinvent them:
`wd-change-adoption/references/adoption-measurement.md` owns the leading/lagging
metric definitions and their baseline/target; this reference consumes those
definitions and reports the go-live actuals against them. Add one line to the daily
hypercare checks (SKILL.md "What to monitor daily"): submissions/logins by user
population vs expected (expected = the change-adoption target, cross-checked against
the Volumes Questionnaire forecast and the trained-user count).
- **Low usage is a Sev2-equivalent finding.** Treat "population X has submitted
  nothing in 3 days" with the same urgency as a blocked workflow: find out same
  week whether it's awareness, access (security!), fear, or a shadow process still
  running. Silence is a defect in adoption even when the app is defect-free.
- Adoption actuals feed the 30/60/90-day value check-ins
  (`references/value-capture.md`).

## Feedback loops (after week one)

**CSAT pulse** - defined in `references/value-capture.md` (two moments: hypercare
exit and closeout). Consume it from there; do NOT redefine questions or timing here.
Champions are the distribution channel for the user-population pulse.

**Enhancement intake - a named path, not folklore**
- "How to request an enhancement" is a **named row in the support-ownership matrix**
  (`references/handoff-and-closeout.md`) with exactly one Own, parallel to defect
  intake - users who can't find the enhancement path either log defects or go quiet.
- The post-production guide's Part 1 gets a matching section ("have an idea?"),
  parallel to its how-to-report-an-issue section.
- Enhancement requests are not defects (SKILL.md hypercare rule) - they land in the
  backlog, sized via **wd-estimate** when material.

**Backlog disposition review**
- At the (monthly) service review - `references/managed-services.md` - walk the
  enhancement backlog and disposition each item: accepted (target release), deferred
  (revisit date), or declined (reason stated). Undispositioned backlogs read as
  ignored suggestions, and users stop submitting.

**Close the loop: "you asked, here's what's coming"**
- Release notes (**wd-kt** owns authoring) cover what SHIPPED; this note covers
  everything else. Short template, sent to users after each disposition review:

  > Since go-live you've raised N ideas. Shipping next: [1-2 items + rough when].
  > On the list: [1-2 items]. Not planned: [item + one honest line why].
  > Keep them coming: [the named intake path].

- One note per cycle, voice per **wd-comms**. This is the cheapest retention
  artifact the engagement produces: it proves the intake path is alive.

## Boundaries

- CSAT pulse definition, KPI baselines, value snapshots -> `references/value-capture.md`.
- Change network operating model + adoption-metric DEFINITIONS -> **wd-change-adoption**
  (`references/impact-and-readiness.md` for the network, `references/adoption-measurement.md`
  for the metric definitions). This reference continues that network into hypercare and reports
  actuals against those definitions; it does not redefine either.
- Training content, job aids, KT sessions -> **wd-kt**.
- Go/no-go checklist itself -> **wd-deployment** SKILL.md (this reference defines the
  people-readiness measures it points at).
- Enhancement roadmap / QBR / renewal motion -> `references/account-growth.md`.
