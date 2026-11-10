---
name: app-architecture
description: >-
  Structure a hosted web app or agentic tool so it can grow from a single service into many
  without moving code. Owns the module contract (how one liftable unit is shaped), the
  functional-core/imperative-shell (FCIS) split, schema-per-module data isolation, per-module
  migrations, and topology independence (a module runs in a monolith or as its own service by
  changing a composition root, not by moving files). START HERE when scaffolding a new hosted
  tool, adding a feature module to an existing one, or deciding where code and data boundaries go.
  TRIGGERS: "new app", "new tool", "add a module", "how should I structure this", "module
  contract", "monorepo", "extract a service", "composition root", scaffolding, FCIS,
  import-linter, schema isolation. Hands off to app-hosting for the AWS deploy pipeline,
  app-agentic for the Bedrock/Anthropic agent layer, and app-harness for the build-discipline
  loop. Modeled on a private reference architecture - patterns only, no client code copied.
---

# Hosted App & Agentic Tool Architecture

This skill is a thin index. Read the reference for the boundary you're drawing - each is
self-contained and distilled from a working private reference architecture. It answers
one question above all others: **how do I shape a new tool so it can start simple and scale
without a rewrite.**

## The one principle that drives everything

**Repo organization and runtime topology are independent axes.** How the code is arranged in
the repo has nothing to do with how many services it deploys as. A feature is a self-contained
**module** (a "liftable unit"); a thin **composition root** decides at deploy time whether that
module runs inside a shared monolith or as its own extracted service. Splitting a service later
is a config change in a composition root - **zero code movement**. Design for this from day one
and you never pay for a premature microservice split or a painful monolith breakup.

## Before you scaffold - the module contract

Every module obeys the same contract so the composition root can mount it uniformly and the
hosting pipeline can deploy it with no new infrastructure. Read
[references/module-contract.md](references/module-contract.md) first. The non-negotiables:

- **FCIS split** - `core/` is pure functions (no I/O, unit-testable in isolation); `api/` is the
  imperative shell (routers, DB sessions, side effects). Business logic never lives in a router.
- **Unauthenticated `GET /health`** - every module exposes its own for liveness and for when it is
  extracted into its own service. Note: App Runner's platform health check probes the composition
  root's ROOT-level `GET /health` (see app-hosting), not each module's path; the per-module
  endpoint is the module's own liveness signal, and the pipeline smoke test can hit either.
- **Schema-per-module** - each module owns a Postgres schema; no module reads another's tables
  directly. Cross-module reads go through the other module's API/core, never its rows.
- **Per-module Alembic migration tree** with a private `version_table` - migrations never collide
  across modules, so modules deploy and roll back independently.
- **Scaffold, don't copy** - generate a new module from the scaffold so the contract is correct by
  construction; never clone a sibling module and rename.

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **The module contract** - the exact shape of one liftable unit (FCIS, health, schema token, migrations, per-module CLAUDE.md) | [references/module-contract.md](references/module-contract.md) |
| **Topology independence** - liftable units, composition roots, monolith-vs-extracted, same-origin reverse proxy, how to split a service later | [references/topology-independence.md](references/topology-independence.md) |
| **Repo layout** - where apps/web, services/api, packages/modules, packages/shared, infra, and tools live and why | [references/repo-layout.md](references/repo-layout.md) |
| **Local dev / getting started** - the "0 to running on a laptop" quickstart (Docker Postgres, per-module Alembic, seed data, anthropic-provider off-proxy, the dev auth-config stub, the scaffold generator) | [references/local-dev.md](references/local-dev.md) |
| **Discovery + design brief (BEFORE you scaffold)** - the non-Workday tool design front-end: problem/users/JTBD/scope/data/integrations/NFRs/success metrics -> a one-page brief whose last line is your first-cut module list | [references/discovery-and-design-brief.md](references/discovery-and-design-brief.md) |
| **Estimating a build (LOE)** - complexity tiers + drivers + a starting-point effort model + one-time setup + ongoing run-cost (calibrate before quoting) | [references/estimating.md](references/estimating.md) |
| **Starter kit + scaffold** - the one-time starter-repo checklist AND the runnable `scripts/scaffold_module.py` (generates a contract-correct module skeleton: FCIS api/core, /health, schema token, per-module migrations, tests, import-linter lines) | [references/starter-kit.md](references/starter-kit.md) |
| **Frontend React/Vite UI craft** - scaffold, TS config, data layer (TanStack Query), forms (react-hook-form + zod), routing inside a module, testing (Vitest/Testing Library/Playwright/MSW), production-build gotchas, a11y baseline | [references/frontend-react-vite.md](references/frontend-react-vite.md) |
| **Multi-tenancy (CUSTOMER-SOLD product)** - per-customer data isolation: Pool (tenant_id + Postgres RLS) vs Bridge (schema-per-tenant) vs Silo (DB-per-tenant), the cross-tenant-leak invariant + its test. Orthogonal to schema-per-MODULE (features) | [references/multi-tenancy.md](references/multi-tenancy.md) |
| **Data store decisions** - when NOT Postgres: NoSQL/cache/object/search as deliberate escalations, Postgres-first as the standing rule (DynamoDB, ElastiCache/Redis-Valkey, S3, OpenSearch) | [references/data-store-decisions.md](references/data-store-decisions.md) |
| **TypeScript/Node parity spec** - when a module must be built in TS/Node instead of Python (client standard, existing Node estate, JS-only dependency): the decision gate, the Fastify/Drizzle/zod/eslint-plugin-boundaries parity picks, and the honest deltas from the Python contract | [references/module-contract-ts.md](references/module-contract-ts.md) |

## Boundaries

- **AWS deploy pipeline, App Runner, RDS, CloudFormation:** app-hosting
- **Bedrock/Anthropic agent layer, tool-loop, spend metering, MCP hosting:** app-agentic
- **Build-discipline loop, complexity routing, security hooks:** app-harness
- **Workday-side Extend/O4I builds (not general web apps):** wd-extend-dev

## Lifecycle neighbors

First skill you touch when standing up a **hosted tool** (as opposed to a Workday Extend app). It
sets the boundaries that app-hosting deploys and app-agentic fills with agent logic. Get the
module contract right here and the other two skills have nothing to fight.

**Ship gate for this track (not the Workday `quality-gates.md` registry):** before a hosted tool ships, run the conformance checklist in **app-harness** (AWS Well-Architected Agentic AI Lens + OWASP Top 10 for LLM Apps). The app-* family deliberately does not use the Workday delivery quality-gate footer.

> Modeled on a private reference architecture. Patterns are reusable; no reference-project or
> client source was copied. Internal identifiers (AWS account IDs, VPC endpoints, App Runner URLs,
> the reference project's GitHub org) never appear in this suite - see app-hosting
> references/deploy-runbook.md for the genericize-before-adopt rule.
