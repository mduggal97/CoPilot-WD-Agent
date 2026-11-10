# Demo Playbook - Staging, Track Variants, Live-Question Triage

Companion to `wd-demo/SKILL.md`.

## Demo-tenant staging checklist

Run this before the FIRST demo of an app and re-verify (abbreviated) before every
subsequent one.

Staging state is verifiable live via tenant-ops reads (picker-source counts, cast
group membership, stray in-flight events) - run the read-set before the dry run,
not instead of it (wd-extend-dev references/tenant-ops.md).

The org's existing demo setups are the precedent to reuse: a demo/dev tenant with a
standing test cast (e.g. the Workday sample personas Logan McNeil / Steve Morgan /
Betty Liu) plus security-group and proxy rules, and a delivered app's demo-script
Word doc. The SPECIFIC tenant name, cast membership, proxy rules, and demo-script
file locations live in the owner's ENVIRONMENT/PROJECT MEMORY, not in this skill
(the suite ships client-clean) - pull them from memory or ask the owner at demo
setup time; the sections below are the reusable shape.

**1. Test cast (personas -> security)**
- One named test user per actor in the app's flow (submitter, each approver step,
  admin, view-only), mapped to the REAL security groups the design specifies - a
  demo run entirely as an admin proves nothing about security and hides broken
  role views.
- Proxy rules configured so one presenter can switch personas live without
  re-logging in; verify proxy works for EVERY cast member in the dry run.
- Keep the cast standing across apps in the program - reusable cast + reusable
  proxy setup is what makes demo prep cheap the second time.

**2. Story-shaped seed data**
- Seed records at EVERY workflow stage: one draft, one in-flight at each approval
  step, one approved, one denied/sent-back, one completed end-to-end. The audience
  should see the lifecycle without waiting for it.
- Business-plausible names and values - no "Test 1", no lorem ipsum, no obviously
  fake amounts. Use the client's own org names/worktags where the tenant has them
  (recognizable data is half the demo's credibility).
- **Seed-data policy (house rule):** the demo cast and all seed TRANSACTIONS are
  always **synthetic personas** - invented people, invented requests, invented
  amounts. Real REFERENCE data (org names, cost centers, worktags) is acceptable
  in **client-internal** demos, where recognizability helps. Real person records
  or PHI are **never** seeded into a demo tenant, for any audience. (External
  showings additionally need the anonymization + permission gates in the
  prospect-demo row below.)
- **No empty pickers.** Every dropdown/picker on the click path has real options -
  empty pickers are almost always tenant config (App Attribute WIDs, missing
  reference data - the class-(d) pattern in **wd-testing**
  `references/defect-triage.md`), and they read as "the app is broken."
- Seed via the seed/wipe script pattern (**wd-extend-dev** owns it) so staging is
  repeatable, not artisanal.

**3. Pre-demo smoke run (same day)**
- Walk the exact click path with the exact cast, in the exact tenant, same day.
- Check the fresh-transaction path too: create one new record live in the smoke
  run so you know submit/route/approve works TODAY (schedules, ISU credentials,
  and security grants rot between demos).

**4. Reset procedure (between demos)**
- Script the reset: wipe/re-seed demo transactions back to the story-shaped state;
  cancel/rescind any in-flight BP events the last demo created (a stuck "Awaiting
  Action" event from last week's demo will greet this week's audience) - this
  scripted wipe/reseed is the per-app seed-pack recipe in wd-extend-dev
  references/tenant-ops.md (write verbs pending; WRITE GATE applies).
- Reset BEFORE the smoke run, not after the demo - post-demo you'll forget.

## Track variants - match the demo to its moment

| Track | Job of the demo | Framing | Notes |
|---|---|---|---|
| **PoC demo** | Get a decision on the riskiest slice | Design-decision framing: "here is the risky pattern working; here are the 2-3 design choices it opens" - show the seam, not a polished app | Acceptance gates the PoC phase (wd-pm plan skeleton); capture decisions to the Decisions log same day |
| **Build demo** (bi-weekly) | Keep the client bought-in and catch drift early | Working software in the tenant mapped to design-doc requirement refs - "REQ-12 is this screen" | Cadence, 30-min structure, and named-plan-task rule: **wd-pm** `references/project-plan-format.md` section Build-demo cadence. Feedback routes through **wd-testing**'s triage classes - never absorb "while you're in there" asks live |
| **SteerCo demo** | Sustain sponsor confidence | Outcome framing: the business result on screen in <=5 minutes, not feature tours - "a requester did X, the approval landed in Y's inbox, the record wrote back" | Slot inside the SteerCo agenda (**wd-pm** `references/steering-committee.md`); rehearse to half the allotted time |
| **Prospect demo of a delivered client app** | Sell the capability without exposing the client | **Two gates first: anonymization + client permission.** Scrub client names, org values, logos, and real data from the tenant view (or demo in a firm-owned tenant with neutral seed data); confirm the client's reference/demo rights are on record before ANY external showing | Reference-rights logging: **wd-post-go-live** `references/value-capture.md`. For a productized Marketplace demo, switch to **bow-sales-enablement** `references/demo-script.md` |

## Live "can it do X?" triage

Every demo gets these questions. Answer in one of four honest shapes - never vamp:

1. **Yes - live**: show it now if it's on or near the click path (only if
   smoke-tested; an unrehearsed detour is how demos die).
2. **Yes - not built yet**: it's in the signed design, not yet in the build. Name
   the requirement ref and the phase it lands.
3. **Roadmap / candidate**: not in scope; worth logging. -> parking lot.
4. **No - and why**: platform limit or explicit design decision. State the reason
   plainly (the rejected-options record in the design doc is your source);
   a confident "no because" builds more trust than a soft "we'll look into it."

**Parking-lot capture is not optional.** Every 2/3/4 answer gets a parking-lot line
(who asked, what, which answer shape). Route after the demo: in-scope gaps ->
**wd-testing** triage; new-scope asks -> CR log (**wd-pm** `references/raid-log.md`);
"next app" sightings -> the opportunity log (**wd-post-go-live**
`references/account-growth.md`).

## Demo-day mechanics (quick list)

- Rehearse to 2/3 of the slot - questions fill the rest.
- Have a fallback: screenshots or a recording of the smoke run, in case the tenant
  misbehaves live (pattern per bow-sales-enablement's recorded-demo fallback).
- Narrate personas as people, not accounts ("Betty, the cost center manager, opens
  her inbox...").
- Close every demo with what happens to the feedback ("these three go to triage,
  this one's a CR, here's when you'll hear back") - the close-the-loop habit is
  what keeps demo audiences engaged next time.
