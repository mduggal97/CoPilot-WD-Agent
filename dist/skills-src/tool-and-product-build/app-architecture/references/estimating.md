# Estimating - sizing a hosted-tool build (LOE + run cost)

Modeled on the reference architecture. Patterns only - every number below is an
INVENTED starting point, not a quoted rate. No client data, no real quotes.

This is a generic hosted-**tool** effort model. It is NOT the Workday UET
(`wd-estimate` owns that, and the Workday-templated LOE). Use this to size a
non-Workday hosted tool built on the app-* stack: how big is the build, what
one-time setup it carries, and - the part people forget - what it costs to RUN,
every month, alongside the build hours.

**Standing rule for this whole file: every LOE number is a STARTING POINT to
calibrate against your real builds. Mark it "calibrate before quoting."** These
ranges exist to give a first cut a shape, not to hand a client a number. The first
two or three real builds replace these with measured anchors.

## Table of contents

- [The two numbers, kept separate](#two-numbers)
- [Complexity tiers - Simple / Standard / Complex](#tiers)
- [The drivers that move the estimate](#drivers)
- [A rough build-effort model](#effort-model)
- [One-time hosting / CI setup cost](#setup)
- [Ongoing run cost - quoted alongside the build](#run-cost)
- [Where this feeds](#feeds)
- [What to remember](#remember)

---

<a name="two-numbers"></a>
## The two numbers, kept separate

A hosted-tool estimate is always TWO numbers, and conflating them is the classic
mistake:

- **Build LOE** - one-time hours to design, build, test, and ship it. A project
  cost.
- **Run cost** - the recurring monthly infrastructure + model spend to keep it
  alive. An operating cost, forever, whether or not anyone touches it.

Quote both, always. A tool that takes 200 hours to build and 900 dollars a month
to run is a very different proposition from one that runs at 90 dollars a month -
and the client (or the practice, for an internal tool) needs both to decide.
`wd-estimate` makes the same "present LOE + assumptions as a package, never a bare
number" point; this file adds "and the run cost travels with it."

---

<a name="tiers"></a>
## Complexity tiers - Simple / Standard / Complex

Size the tool into one of three tiers first. These deliberately **mirror
app-harness's complexity routing** (Simple goes straight to implement; Standard
plans first; Complex stops for a human design) - the build-discipline tier and the
estimate tier are the same judgment, so use one word for both.

- **Simple** - one module, no agent, at most one straightforward integration,
  internal auth, CRUD over a small data model. The kind of tool app-harness routes
  straight to implement.
- **Standard** - a few modules OR one agentic module, one or two integrations, a
  real auth story, a data model with some depth. app-harness plans this before
  building.
- **Complex** - multiple modules AND agentic, several integrations, long-running
  background agent work or RAG, a customer-grade availability / compliance bar.
  app-harness stops and requires a human design before code.

KT note: the tier is a starting anchor, not the estimate. Two Standard tools can
differ 3x on hours depending on the drivers below. Pick the tier to get in the
right range, then adjust by drivers.

---

<a name="drivers"></a>
## The drivers that move the estimate

Within a tier, these are what actually move the hours. They come straight off the
design brief (`discovery-and-design-brief.md`) - which is why the brief exists
before the estimate.

- **Number of modules** (per the module contract) - each liftable unit is its own
  scaffold, schema, migration tree, tests, and UI surface. Modules are the primary
  multiplier. Two modules is not twice one module (shared foundation is built
  once), but it is not free either.
- **Static vs agentic** - the single biggest fork. An agentic module adds the
  provider seam, the metered tool-loop, a spend cap, and evals (`app-agentic`).
  Roughly it can DOUBLE a module's build over the same module done as plain CRUD.
- **Number of integrations** - each external system is auth + sync style +
  idempotency + retry + rate-limit + mapping + mock-in-dev (saas-integration).
  Plus vendor access lead time, which is schedule risk even when it is not hours.
- **Auth / security bar** - internal single-audience auth is cheap; multi-audience
  (staff + external customers + service-to-service), PII/regulated data, or a
  compliance standard (SOC 2, HIPAA-adjacent) adds real hardening and review time.
- **Data / RAG needs** - plain relational CRUD is baseline; retrieval (pgvector,
  chunking, retrieve-then-ground, citations) is a meaningful add on top of the
  agentic cost, not instead of it.
- **UI surface** - a backend-only module (no registry entry) is less than one with
  a full SPA surface; count worker/approver/admin-style variants separately, the
  way `wd-estimate` counts page variants.

Rule of thumb: **agentic and integrations are the two drivers that most often blow
a Simple estimate into a Standard one.** Watch those two hardest.

---

<a name="effort-model"></a>
## A rough build-effort model

Below is a STARTING shape - ranges by tier, then driver add-ons. These are
invented anchors to calibrate against your real builds, NOT quotable rates. The
whole point is to replace them with measured hours after the first few tools.

**Do not present these numbers to a client. Calibrate before quoting.**

Base build, by tier (design + build + test + ship, one module's worth of core):

- **Simple** - a small starting range (order of a few developer-days). One
  scaffold, one schema, a thin UI, ship.
- **Standard** - a mid starting range (order of one to a few developer-weeks).
- **Complex** - a large starting range (order of several developer-weeks and up),
  and this is the tier where the range is widest and least trustworthy until
  calibrated - treat a Complex first cut as a rough order of magnitude only.

Driver add-ons (added on top of the base, per unit):

- **+ per additional module** - roughly a fraction of a base module (shared
  foundation already built), scaling with that module's own drivers.
- **+ make a module agentic** - roughly the same again as that module's static
  build (provider seam is shared once; the loop, spend cap, and evals recur).
- **+ per integration** - a starting chunk per external system, more if the auth
  is auth-code/OAuth dance rather than a client-credentials/API-key seam.
- **+ RAG on a module** - a starting chunk on top of that module's agentic cost.
- **+ raised security / compliance bar** - a percentage uplift across the whole
  build, not a line item - it touches auth, data handling, logging, and review
  everywhere.

How to actually use this:

1. **Pick the tier** to land in the right range.
2. **Start from the base** for the primary module.
3. **Add the driver add-ons** for extra modules, agentic, integrations, RAG.
4. **Apply the security/compliance uplift** as a percentage if the bar is raised.
5. **Add the one-time setup cost** (next section) if this is the FIRST tool on a
   fresh stack.
6. **Label the whole thing "starting estimate - calibrate before quoting"** and
   list the assumptions, exactly as `wd-estimate` does. The assumptions are the
   protective wall.

KT note: the honest move when you have no calibration yet is to give a RANGE and
name the drivers that would push it to either end, not a false-precise single
number. "Standard tool, one integration, agentic - starting range X to Y, lands
high if the integration auth is OAuth-code and the data is PII" beats a bare
figure every time.

---

<a name="setup"></a>
## One-time hosting / CI setup cost

The FIRST tool on a fresh stack pays a one-time tax the later tools do not. Count
it once, separately, so it does not distort the per-tool number:

- **Stand up the two-account pipeline** - dev/prod accounts, the immutable-dev /
  mutable-prod deploy pipeline, ECR, CloudFormation stacks (app-hosting).
- **Provision shared RDS** and the schema-per-module bootstrap.
- **Wire the identity provider** - the real Entra (or equivalent) app registration,
  the runtime auth-config route, the default-deny seam.
- **Set up the build harness** - the guard hooks, complexity routing, and the
  supervisor/worker loop (app-harness).
- **First-module scaffold generator** and the import-linter contracts.

For the SECOND tool onward that reuses the same stack, most of this is already
paid - the setup line drops to near zero and you are back to just build LOE +
run cost. Make that reuse explicit in the estimate: a shared platform is exactly
what makes tool number two cheap.

---

<a name="run-cost"></a>
## Ongoing run cost - quoted alongside the build

**Every build LOE ships with a monthly run cost, or the estimate is half-done.**
This is the operating side, and app-hosting already owns the detailed worksheet.

**Cross-link: `app-hosting/references/operations.md` s4-s6** - the App Runner +
RDS + Bedrock TCO worksheet. Do not re-derive it here; pull the current rates and
fill that worksheet. In brief, the three cost centers are:

- **App Runner (compute)** - provisioned memory 24x7 + active CPU while serving.
  The min-size lever is the big one: raising min-size >= 1 (for cold-start OR for
  background agent work) costs steady money every hour. An availability bar of
  "customers notice an outage" pushes this up.
- **RDS (shared database)** - one instance per environment, 24x7 (a database does
  not scale to zero), plus storage and backups. Multi-AZ roughly doubles it - a
  prod cost, often skippable for dev. Because it is shared schema-per-module,
  allocate a SHARE to each tool rather than charging it all to the first.
- **Bedrock (model spend)** - the only usage-scaled cost: per input+output token,
  per model. Bounded by the SpendGuard hard cap, so the worst case is a KNOWN
  number - which is what lets you quote a ceiling instead of an open-ended risk.

Two run-cost rules that matter for the estimate:

- **A non-agentic tool has NO Bedrock line** - do not pad it with model spend it
  will never incur. This is another reason the agentic-or-not question is
  load-bearing.
- **Size dev AND prod** - they are separate accounts. Dev runs lean (no Multi-AZ,
  min-size 1); prod carries the availability cost. Quote both or the monthly
  number is optimistic.

The App Runner CPU-throttle trap (operations.md s5) is a design cost, not just a
run cost: genuinely long-running background agent work may need Fargate / Batch /
Step Functions rather than plain App Runner - which is extra BUILD hours as well
as extra run cost. If the brief says "long-running agent," flag both.

---

<a name="feeds"></a>
## Where this feeds

- **product-gtm pricing** - the build LOE + setup + run cost are the cost floor
  under any price. You cannot price a product below what it costs to build and run;
  this estimate is that floor's foundation.
- **product-strategy's TCO bar** - the internal-vs-external disposition call weighs
  total cost of ownership. The run-cost number here IS the "what does it cost to
  keep running" input that bar needs.
- **The design brief closes the loop** - the drivers (module count, agentic,
  integrations, security) come from `discovery-and-design-brief.md`, so a change to
  the brief mechanically re-sizes the estimate instead of forcing a re-guess -
  the same explicit-layers discipline `wd-estimate` uses.

---

<a name="remember"></a>
## What to remember

- **Two numbers, always: build LOE and monthly run cost.** Quote both as a
  package; a bare build number hides the operating cost.
- **Tier first (Simple / Standard / Complex), mirroring app-harness routing** -
  then adjust by drivers; the tier alone is not the estimate.
- **Agentic and integrations are the biggest drivers** - either can push a Simple
  tool into Standard. The agentic-or-not answer is the single largest fork.
- **First tool pays a one-time setup tax; later tools on the same stack do not** -
  count it once, and make the reuse saving explicit.
- **Run cost = App Runner + shared RDS + capped Bedrock** - detailed worksheet in
  `app-hosting/references/operations.md`; a non-agentic tool has no Bedrock line;
  size dev and prod separately.
- **Every number here is a STARTING POINT - calibrate before quoting.** Replace
  these invented ranges with measured anchors after the first real builds, and
  always ship the assumptions list alongside.
