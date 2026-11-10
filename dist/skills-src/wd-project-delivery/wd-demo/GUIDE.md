---
name: wd-demo
description: >-
  Stage and deliver demos of Workday Extend apps - demo prep, demo scripts for
  delivery-track demos, demo-tenant staging and seed data, demo dry runs, and
  handling live questions. Trigger on: demo, demo prep, demo script, demo
  tenant, demo data, PoC demo, build demo, steering/SteerCo demo, prospect
  demo, "show the app", "walk the client through it", dry run before a
  demo, or resetting a tenant between demos. Owns tenant staging and
  delivery-track demo craft; the productized Marketplace demo-script/deck
  artifacts belong to bow-sales-enablement (this skill points there).
---

# wd-demo - Demo Staging & Delivery Craft for Extend Apps

Demos are where Extend apps are judged - a working app shown badly reads as a broken
app. This skill owns two things: **making the tenant demo-ready** (personas, seed
data, smoke run, reset) and **matching the demo to its moment** (PoC vs build vs
SteerCo vs prospect - each has a different job).

## When to use

- Preparing ANY live showing of an Extend app: PoC acceptance, bi-weekly build demo,
  steering-committee demo, KT demo-then-do session, prospect demo of a delivered app
- Staging or resetting a demo tenant: test cast, security, story-shaped seed data
- Writing the talk track / click path for a delivery-track demo
- The demo went sideways and you're diagnosing why (usually staging, not code)

## The one rule

**Never demo un-smoke-tested.** Every demo is preceded by a same-day dry run of the
exact click path with the exact demo users. The most common demo failure is not a
bug - it's staging: an empty picker, a security group the demo user fell out of, a
seed record someone consumed in the last demo.

Seed data and resets can be scripted instead of hand-entered: per-app **seed packs**
loaded/reset via the tenant API - mechanics and the mandatory WRITE GATE in
wd-extend-dev `references/tenant-ops.md`.

Driving staging + the dry run LIVE in the browser: **wd-tenant-config** creates the
synthetic seed data and runs the setup (grants, Activate Pending, App Attributes) in a
dev/sandbox tenant confirm-each-write, and **wd-test-execution** runs the smoke dry run -
proxy to the demo worker, walk the exact click path, confirm the tiles/data render, catch
the empty-picker / dropped-group / consumed-seed faults BEFORE the client is watching. The
"blank under the wrong worker or wrong org is staging, not a bug" rule is theirs too.

## Full playbook

Staging checklist, per-track script variants, live-question triage, reset procedure:
-> **`references/demo-playbook.md`**

## Boundaries

- **Productized Marketplace / BoW demo assets** - the sellable demo script + demo
  deck for a many-customer product (three-persona-view structure, claims-gated talk
  tracks, `<CLICK>` markers) -> **bow-sales-enablement** `references/demo-script.md`
  and `references/demo-deck.md`. This skill stages the tenant those demos run in and
  covers delivery-track demos of one client's app.
- **Build-demo cadence in the plan** (bi-weekly rhythm, named plan tasks) ->
  **wd-pm** `references/project-plan-format.md`; this skill owns how to run the demo
  itself.
- **Demo-then-do KT sessions** (teach-back, per-audience series) -> **wd-kt**
  `references/kt-sessions.md`; the staging checklist here feeds those sessions.
- **Tenant security/config mechanics** (ISU/ISSG, domains, App Attributes) ->
  **wd-extend-dev** and **wd-deployment**; this skill consumes them as staging
  prerequisites.
- **Wireframes / mockups** for showing an app that isn't built yet ->
  **wd-design-visuals**.

## Lifecycle neighbors

Cross-cutting - demos recur through the whole delivery: **wd-extend-dev** (PoC and
build demos show its output), **wd-pm** (build-demo cadence as plan tasks; SteerCo
slot), **wd-testing** (demo feedback routes through its triage classes so demos
don't become scope creep), **wd-kt** (demo-then-do sessions), **wd-post-go-live**
(parking-lot items feed the opportunity log), and **bow-sales-enablement** (the
productized demo kit).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
