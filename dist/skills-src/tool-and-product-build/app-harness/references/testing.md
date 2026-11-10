# Testing - the test pyramid for a hosted tool's own code

Reference for `app-harness`. This is the "does the CODE work" story for Track 2
(build/host a tool) - unit, integration, contract, and E2E/UI testing of the
hosted app itself, plus lightweight UAT. It sits next to `complexity-routing.md`
(the build-discipline loop that makes tests trustworthy) and hands off cleanly to
`app-agentic/references/evals.md` (does the AGENT answer well) where a tool is
agentic.

**Why this file exists.** Track 1 (Workday delivery) has two whole skills for
this - `wd-testing` derives scenarios and runs the lifecycle, `wd-test-execution`
drives the browser through them. Track 2 had nothing: `evals.md` is strong but
scoped to agent OUTPUT quality (golden sets, LLM-as-judge, trace assertions) -
it never asks whether a route 500s or a migration rolls back cleanly.
`app-harness` already owns build discipline (mutation-proof testing lives in
`complexity-routing.md`), so the app-level testing strategy belongs here too.

---

## Contents

- [The boundary: this file vs evals.md](#the-boundary)
- [The pyramid, in one picture](#the-pyramid)
- [Unit - the functional core](#unit)
- [Integration - the imperative shell against real Postgres](#integration)
- [Contract - schema-per-module and API shapes](#contract)
- [E2E / UI - the SPA and backend end to end](#e2e)
- [UAT - internal accelerator today, not a customer product](#uat)
- [Customer-grade testing (for a SOLD hosted product)](#customer-grade)
- [Where it runs](#where-it-runs)
- [Coverage bar](#coverage-bar)
- [What to remember](#what-to-remember)

---

<a name="the-boundary"></a>
## The boundary: this file vs evals.md

Two different questions, two different files:

| | This file (`testing.md`) | `app-agentic/references/evals.md` |
|---|---|---|
| Question | Does the CODE work - routes, DB, migrations, UI? | Does the AGENT answer well? |
| Input under test | Real Postgres, real HTTP, a real browser | The real model behind the provider seam |
| Determinism | Deterministic - same in, same out | Stochastic - same in, different out across runs |
| Pass condition | Exact assertion | A threshold over samples, or a judge's grade |

**If the tool is agentic, both apply.** A hosted tool with an agent loop needs
this pyramid to prove the routes and DB work, AND the eval harness in
`evals.md` to prove the agent's answers are good. A green test suite here says
nothing about answer quality - `core/reconcile.py` passing its unit tests does
not mean the agent that calls it gives a sound recommendation. Do not let a
green pyramid stand in for an eval run, and do not let evals stand in for a
migration test.

---

<a name="the-pyramid"></a>
## The pyramid, in one picture

```
        /  E2E/UI  \        few, slow, real browser - the critical path only
       /------------\
      / Contract     \      schema + API shape - module and service boundaries
     /----------------\
    /  Integration     \    api/ shell against real Postgres - the DB layer
   /--------------------\
  /       Unit           \  core/ pure functions - fast, hermetic, the bulk
 /------------------------\
```

Bulk at the bottom, on purpose: unit tests are free and fast, so they carry the
majority of assertions; each layer up costs more (a container, a browser, a
running service) and should therefore assert fewer, higher-value things. A
suite shaped like an hourglass (heavy E2E, thin unit) is a smell - it means the
functional core (`module-contract.md`) is not actually pure, or the team is
testing behavior that belonged in `core/` by clicking through the UI instead.

---

<a name="unit"></a>
## Unit - the functional core

**What it tests.** Everything in a module's `core/` folder - the pure functions,
dataclasses, and set/string/number logic that `module-contract.md` requires to
have NO I/O, no DB session, no network call, and no import of `api/` or
`models`. Per that file's FCIS split: `api/` may import `core/`; `core/` may
never import `api/`. That one-way arrow is what makes this tier possible at
all - a pure function over values needs nothing running to test it.

```python
# tests/unit/test_reconcile.py
# KT: pure function in, pure value out - no fixture, no DB, no mock. This is
# the whole point of the FCIS split: the hard-to-get-right branching logic
# (set math here; limit/cursor validation in pagination.py) lives where it
# costs microseconds to test.
from widgets_app.core.reconcile import plan


def test_plan_adds_and_removes_the_right_ids():
    result = plan(incoming_ids={"a", "b"}, existing_ids={"b", "c"})
    assert result.to_add == ("a",)
    assert result.to_remove == ("c",)
```

**Property-based where it fits.** Reach for a property-based tool (Hypothesis
for Python, https://hypothesis.readthedocs.io/) when the function has an
algebraic invariant that is easier to state than to enumerate examples for -
`plan()` above always satisfies `to_add & existing_ids == set()`, for any input
sets. Do not force it on every function; a handful of well-chosen example
cases is often clearer than a property nobody can state cleanly. Use it where
the input space is large and the invariant is real (parsers, reconciliation,
pagination math), skip it for simple pass-through logic.

**Fast, the bulk.** No network, no container, no sleep - a unit suite in the
hundreds of tests should run in seconds. If it does not, something impure
leaked into `core/`; that is a design smell to fix, not a suite to accept.

**Location.** `packages/modules/<name>/tests/unit/` per `module-contract.md`'s
layout. No `__init__.py` in the tests tree (two modules' identically-named
test files would collide on collection) - run pytest with `importlib` import
mode from the repo root so tests are keyed by path, not by package identity
(https://docs.pytest.org/en/stable/explanation/goodpractices.html#test-discovery).

---

<a name="integration"></a>
## Integration - the api/ shell against real Postgres

**What it tests.** The imperative shell - `api/router.py`, `repository.py`,
`deps.py` - against a REAL database, not a mock. Mocking the DB layer only
proves your mock behaves like you assumed it would; a repository test that
never touches Postgres cannot catch a query that is syntactically valid but
semantically wrong (a bad join, a missing index, a schema-qualification bug).

**Use testcontainers, not a shared dev DB.** Spin up a throwaway Postgres per
test run (or per session) with the `testcontainers` library
(https://testcontainers-python.readthedocs.io/) rather than pointing tests at
a long-lived dev database. A shared DB accumulates state between runs and
makes a failure non-reproducible; a container is disposable, matches the real
Postgres version, and starts clean every time.

```python
# tests/integration/conftest.py
# KT: session-scoped container, function-scoped schema reset. Booting Postgres
# once per test file would be wasteful; leaving rows between tests would make
# test order matter, which is its own bug magnet.
import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def pg_container():
    with PostgresContainer("postgres:16") as pg:   # pin the major version you deploy on
        yield pg


@pytest.fixture()
def db_session(pg_container):
    # Run this module's Alembic chain to head against the container, then
    # hand back a schema-scoped session - the SAME seam api/deps.py uses in
    # production (get_session_for_schema), not a hand-rolled test session.
    ...
```

**What belongs at this tier:**

- **The DB layer.** CRUD through `repository.py`, pagination against real rows,
  constraint violations (unique, FK) surfacing as the right error - none of
  which a mock can reproduce faithfully.
- **Migrations apply AND rollback.** Run the module's Alembic chain
  `upgrade head`, then `downgrade -1` (or to base) and confirm it does not
  error and does not leave orphaned objects. A migration that only runs
  `upgrade` and is never proven to roll back has never actually been tested for
  the failure case it exists to handle. Per `module-contract.md`, each module's
  chain is independent (private `alembic_version_<module>` table) - test each
  module's chain in isolation so a broken migration in one module cannot be
  masked by another module's passing chain.
- **Module boundaries.** `module-contract.md`'s independence rule ("a module
  never imports a sibling module and never reads another module's rows") is a
  code-level contract in `pyproject.toml`/import-linter, but the DATA half of it
  - no cross-schema row reads - is what integration tests catch: seed rows in
    module A's schema, assert module B's repository genuinely cannot see them
    (queries against B's schema-scoped session return nothing, not an error
    that happens to hide the leak).

**Location.** `packages/modules/<name>/tests/integration/`, run against the
container - never against shared infrastructure, and never skipped because
"the container is slow to start" (a session-scoped fixture amortizes that cost
across the whole file).

---

<a name="contract"></a>
## Contract - schema-per-module and API shapes

**What it tests.** The SHAPE of a boundary, independent of the logic behind it
- request/response bodies, status codes, and error formats stay stable for
whoever is on the other side (another module calling over HTTP, a frontend, an
external consumer).

**Two kinds of contract in this family:**

1. **Schema-per-module, enforced structurally.** `module-contract.md` makes
   cross-module data isolation a hard rule (no sibling schema reads; call the
   other module's HTTP API instead of reaching into its tables). Test this as a
   contract, not just an integration detail: assert the OpenAPI/Pydantic
   response models for a module's public routes are exactly what a consumer
   expects, and that a schema migration cannot silently change a response shape
   without the contract test noticing.
2. **API contracts - request/response shapes and errors.** Every route's
   request and response models are frozen Pydantic contracts
   (`api/contracts.py` per `module-contract.md`); assert against those models
   directly rather than against ad hoc dict shapes, so a field rename anywhere
   in the chain fails a test instead of shipping silently. Error responses
   should conform to RFC 9457 "Problem Details for HTTP APIs"
   (https://www.rfc-editor.org/rfc/rfc9457) - `type`, `title`, `status`,
   `detail` (and `instance` where useful) - and a contract test should assert
   an error path returns THAT shape, not an ad hoc `{"error": "..."}` that
   varies by route.

**Consumer/provider, when modules or services actually talk.** Once a module is
extracted into its own service (the whole point of `module-contract.md`'s
"liftable unit" design), an HTTP call from one service to another needs a
contract test that survives independent deploys - the consumer's expectations
and the provider's actual response are verified against each other WITHOUT
both services running together in CI. Pact
(https://docs.pact.io/) is the standard tool for this pattern
(consumer-driven contract testing). Do not reach for it prematurely: while
everything still runs in one composition root (the common case for an internal
accelerator today), the schema/response-model assertions above are enough: add
consumer/provider contract tests at the point a module is actually extracted,
not before.

---

<a name="e2e"></a>
## E2E / UI - the SPA and backend end to end

**What it tests.** The whole stack together - browser, frontend, backend,
database - through the same paths a real user takes. This is the top of the
pyramid on purpose: fewest tests, slowest to run, but the only tier that
catches "the pieces are each individually correct and the integration between
them is broken."

**Standard tool: Playwright.** Use Playwright
(https://playwright.dev/docs/intro) for browser E2E - cross-browser
(Chromium/Firefox/WebKit) from one API, built-in auto-waiting (no manual
sleeps flaking the suite), and a trace viewer for debugging a CI failure you
cannot reproduce locally. Cypress (https://docs.cypress.io/) is an acceptable
alternative if a team already standardizes on it, but pick ONE per repo -
running both means duplicated fixtures and two flake sources instead of one.
Version-sensitive note: pin the Playwright package version and the browser
binaries it installs together (`playwright install`) - a CI image with a
stale browser binary against a newer test API is a recurring source of
"works locally, fails in CI."

```python
# tests/e2e/test_critical_path.py  (Playwright, sync API)
# KT: this is a SMOKE test, not a feature test - it proves the stack is wired
# together end to end. Feature-level branching belongs at the unit/integration
# tiers, which are far cheaper to run and to debug when they fail.
from playwright.sync_api import Page, expect


def test_health_auth_and_critical_path(page: Page, base_url: str):
    # 1. Health: the unauthenticated liveness route answers before anything else.
    resp = page.request.get(f"{base_url}/api/v1/widgets/health")
    assert resp.ok

    # 2. Auth flow: the default-deny edge (module-contract.md s3) actually
    # denies, then a real sign-in reaches an authenticated page.
    page.goto(f"{base_url}/widgets")
    expect(page).to_have_url(lambda url: "login" in url or "signin" in url)
    # ... perform the configured auth flow for this environment ...

    # 3. The critical path: the one user journey that must never break -
    # create a widget, see it listed. Named explicitly so "critical path"
    # means one specific thing per app, not "everything."
    page.get_by_role("button", name="New widget").click()
    page.get_by_label("Name").fill("smoke-test-widget")
    page.get_by_role("button", name="Save").click()
    expect(page.get_by_text("smoke-test-widget")).to_be_visible()
```

**What to smoke-test, and no more, at this tier:**

- **Health** - the composition root's root-level `/health` AND at least one
  module's own `/health` (`module-contract.md` s3), proving both the container
  liveness probe and the per-module route the platform will hit post-extraction.
- **Auth flow** - the default-deny edge actually denies an unauthenticated
  request and a real sign-in reaches past it. This is the one thing a unit or
  integration test structurally cannot prove, because it depends on the whole
  stack being wired correctly.
- **The critical path** - ONE (or a small named few) end-to-end user journey
  per app that must never break. Resist the urge to E2E-test every screen;
  that is what makes this tier slow and flaky. Push branching/edge-case
  coverage down to unit and integration.

**Run headless, in CI.** Playwright runs headless by default in CI
(https://playwright.dev/docs/ci) - no display server needed. Run this tier
against a real deployed environment (or a docker-compose stack that mirrors
one), not against mocked network calls; mocking the network here defeats the
purpose of an END-to-end test.

---

<a name="agent-boundary"></a>
## The agent boundary

If the tool is agentic (built on `app-agentic`), TWO test surfaces both apply,
and neither substitutes for the other:

- **This file** - does the tool's code/routes/DB work? The agent loop itself
  has plumbing (budget enforcement, provider seam, tool dispatch) that is
  ordinary deterministic code, and it gets ordinary unit + integration tests
  like any other shell code. `evals.md` even says as much: "the provider seam
  exists partly so unit tests can pass a hand-built fake `ModelProvider` and
  run with no network - those tests prove your loop plumbing."
- **`app-agentic/references/evals.md`** - does the agent's ANSWER meet the bar?
  Golden-set cases, behavioral assertions on the trace, LLM-as-judge for
  open-ended prose. A green pyramid here proves the loop dispatches tools
  correctly and stays within budget; it says nothing about whether the answer
  it produced was actually good. Run both before an agentic tool ships.

---

<a name="uat"></a>
## UAT - internal accelerator today, not a customer product

Track 2 as currently scoped is INTERNAL tooling - accelerators the delivery
team builds and uses itself. That changes what UAT means and how heavy it
needs to be:

- **UAT = the delivery team using it against real scenarios.** There is no
  separate customer sign-off step today. The people who will actually use the
  tool run it against the real work it is meant to accelerate, before calling
  it done. Keep this lightweight and scenario-based - a short list of "does
  this handle the actual cases we hit last week," not a formal test-script
  exercise.
- **This is intentionally thin compared to Track 1.** `wd-testing` derives
  numbered UAT scenarios and `wd-test-execution` drives a browser through a
  formal script with defect/CR triage, because that lifecycle ends with a
  CLIENT sign-off. An internal accelerator has no equivalent external
  stakeholder to sign off to, so borrowing that full ceremony here would be
  ceremony without a customer on the other end of it.
- **Customer-sold product -> the heavier bar below.** An internal accelerator's
  lightweight UAT is NOT sufficient once a tool has an external paying customer.
  The practice is building that path (see "Customer-grade testing" next).

<a name="customer-grade"></a>
## Customer-grade testing (for a SOLD hosted product)

When the disposition (product-strategy) is CUSTOMER-SOLD, the pyramid above still
applies, but four heavier layers are added on top. Do NOT ship a paying-customer
product without them:

- **Multi-tenant ISOLATION testing (non-negotiable).** The worst bug a SaaS can
  ship is a cross-tenant data leak. Write an automated test that PROVES tenant A
  cannot read/write tenant B - through the API, not just the DB layer - and run
  it in CI on every change. This is the acceptance gate for the tenancy model in
  `app-architecture/references/multi-tenancy.md` (Row-Level Security / schema/DB
  isolation); a passing functional suite means nothing if isolation is unproven.
- **Security testing.** SAST + dependency/SCA scanning in CI (supply chain, OWASP
  LLM03); DAST against a running instance; and a third-party **penetration test**
  before launch and on a cadence (buyers ask for the report - see
  product-operations `references/compliance-ops.md` and the security-questionnaire
  answer bank). Cite the pen-test cadence in the security exhibit (wd-contracts).
- **Load / performance / scale testing.** Prove the app holds its SLA under
  realistic multi-tenant load (k6, Locust, or Gatling) - concurrency, the noisy-
  neighbor case, and the SLA's latency/throughput targets (product-operations
  `references/sla-and-support.md`). An SLA you have not load-tested is a guess.
- **Formal UAT + acceptance.** A real acceptance process closer to Track 1's:
  numbered scenarios, a customer/stakeholder sign-off, defect/CR triage. Borrow
  the discipline from `wd-testing` (scenario derivation) and `wd-test-execution`
  (browser-driven execution) - the ceremony is justified once there is a customer
  on the other end of the sign-off.

---

<a name="where-it-runs"></a>
## Where it runs

The pipeline's **Test** stage (`app-hosting/references/cloudformation-pipeline.md`
section 3) runs unit + integration before Build, on purpose: **Test precedes
Build** so a failing suite never produces or publishes an image at all. E2E
typically runs later - after `DeployDev`, against the live dev App Runner
service - since it needs a real running stack, not a locally-built image. Wire
E2E as its own stage (or a post-deploy hook on DeployDev) rather than folding
it into the pre-Build Test stage; the two have different dependencies (Test
needs nothing running; E2E needs a deployed service) and different costs
(Test is seconds, E2E is a full browser run).

**Mutation-proof discipline applies here too.** `complexity-routing.md`
invariant 8 is not scoped to any one tier - "a test that cannot fail proves
nothing" applies exactly as much to an integration test against Postgres or a
Playwright smoke test as to a unit test. Before trusting ANY test in this
pyramid as real coverage: break the thing it covers, run the test, quote the
failure, then restore and confirm green again. A green E2E suite that has
never been proven to catch a broken critical path is exactly the "green
rubber stamp" that file warns about - do not skip the mutation check just
because the tier is expensive to run twice.

---

<a name="coverage-bar"></a>
## Coverage bar

- **Target, not a mandate to chase 100%.** A reasonable bar for `core/` (pure,
  cheap to test) is high - most of it should be covered, because there is no
  excuse not to. A reasonable bar for `api/` (integration-tested, more
  expensive) is lower - cover the real paths and the real error cases, not
  every permutation. E2E covers a deliberately small, named set of journeys.
  Chasing a single global coverage percentage across all three tiers rewards
  padding cheap unit tests over writing the integration/E2E tests that
  actually catch the bugs that matter.
- **Test behavior, not implementation.** Assert on what a function/route
  RETURNS and what state change it causes, not on which private helper it
  called internally or how many times. A test coupled to implementation
  details breaks on every refactor even when behavior is unchanged - that is
  the same failure mode `evals.md` calls out for exact-match assertions on a
  stochastic system, just for a different reason: the code under test changed
  shape without changing behavior, and the test should not have cared.
- **A coverage number is a smell detector, not a gate by itself.** Use a drop
  in coverage to ask "what stopped being tested," not as the sole ship/no-ship
  signal - a 100%-covered suite full of tautological assertions is worse than
  an 80%-covered suite of tests that were each proven to fail-then-pass
  (mutation-proof, above).

---

<a name="what-to-remember"></a>
## What to remember

- **Bulk at the bottom.** Unit tests on the pure `core/` are fast and free -
  put most of your assertions there. Each tier up (integration, contract,
  E2E) costs more and should assert fewer, higher-value things.
- **Real Postgres for integration, not a mock.** A mocked DB layer proves your
  mock behaves as assumed, not that your query is right. Use testcontainers;
  prove migrations both apply AND roll back.
- **Contract tests protect the boundary**, not the logic behind it - schema
  isolation, frozen request/response models, RFC 9457 errors. Add
  consumer/provider tests (Pact) only once a module is actually extracted into
  its own service.
- **Playwright, headless, in CI**, for a small named set of E2E journeys:
  health, auth flow, the critical path. Resist turning E2E into a feature-test
  tier - that belongs lower down.
- **This file is does-the-code-work; `evals.md` is does-the-agent-answer-well.**
  An agentic tool needs both, run separately, neither a substitute for the
  other.
- **UAT here is lightweight because Track 2 is internal today.** A future
  customer-sold Track 2 product needs a heavier acceptance process this family
  has not designed yet - say so, don't quietly reuse the internal bar.
- **The Test stage runs before Build**, and mutation-proof discipline
  (`complexity-routing.md`) applies at every tier - a suite that has never
  been shown to fail is not coverage, it is decoration.
