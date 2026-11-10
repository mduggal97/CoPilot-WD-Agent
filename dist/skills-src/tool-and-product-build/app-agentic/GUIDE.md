---
name: app-agentic
description: >-
  Add an AI agent runtime to a hosted tool - the layer that calls the model, runs tool-use loops,
  meters spend, and survives long-running jobs. A swappable provider seam picks Amazon Bedrock via
  boto3 (the default behind a corporate TLS proxy) or the Anthropic API by config, never by code
  change. Owns the model registry, the budgeted tool-use loop (run_tool_loop), spend governance to
  a ledger (SpendGuard), declarative agent specs (model cards), durable async runs that resume
  after a restart, and hosting an MCP server with a prompt-injection trust boundary. START HERE to
  make a hosted tool agentic. TRIGGERS: "make it an agent", "call Bedrock", "call Claude", "tool
  use", "agent loop", "spend cap", "budget", "long-running agent", "background job", "async run",
  "MCP server", "model routing", boto3, Converse. Hands off to app-hosting for where it deploys
  and app-architecture for how the module is shaped. Modeled on a private reference architecture -
  patterns only.
---

# Hosted App Agentic Runtime

This skill is a thin index over the agent layer of a hosted tool - proven by a private reference architecture and extended here to run against **either Bedrock or the Anthropic API**
behind one seam. Read the reference for the piece you're building. The goal: **make a tool
agentic without locking it to one model provider and without an unmetered spend surprise.**

## The design decision that defines this layer

**A swappable provider seam.** All model calls go through one narrow interface; two backends
implement it:

- **Bedrock via boto3** - the default behind a corporate TLS proxy. The reason is concrete and hard-won: the Anthropic
  Python SDK (httpx/certifi) fails TLS certificate verification behind a corporate inspection
  proxy, while the **AWS client works in practice** (empirically observed - the actual mechanism is
  the AWS client trusting the corporate root via `AWS_CA_BUNDLE`/`ca_bundle`, NOT "boto3 reading the
  OS trust store," which is a common misconception; see references/provider-seam.md). Uses
  `us.`-prefixed cross-region inference profiles in us-east-2.
- **Anthropic API direct** - the alternative backend for tools that run outside the corporate-proxy
  path or want the Anthropic SDK's features.

A tool selects its provider by **config, not code**. This is the same swappable-seam shape the reference architecture
uses for its authenticator (shared-token to Entra) - a pattern worth reusing wherever a dependency
might change. Read [references/provider-seam.md](references/provider-seam.md) first.

## Two things every agentic tool must have from day one

- **A spend cap it cannot exceed.** Every model call is metered to a ledger (SpendGuard) with a
  budget; the tool-use loop is *budgeted* - it stops when the budget is spent, it does not run free.
  This is the FinOps discipline the practice needs before any tool touches a customer.
- **Durability if it runs longer than a request.** A multi-minute agent job returns `202` + a run
  id immediately, works in a background task, heartbeats to Postgres, and a restart resumes orphaned
  runs. A closed browser tab never loses the work.

## Reference map - read what you need

| You're building | Read |
|---|---|
| **The provider seam** - the interface, the Bedrock-via-boto3 backend (and *why*), the Anthropic-direct backend, the model-id enum registry, config-driven selection | [references/provider-seam.md](references/provider-seam.md) |
| **The agent loop** - the budgeted+metered tool-use loop (run_tool_loop), SpendGuard ledger metering, declarative agent specs / model cards, supervisor fan-out | [references/agent-loop.md](references/agent-loop.md) |
| **Durable async runs** - 202 + run id, FastAPI background task, Postgres heartbeat, resume-orphaned-on-restart | [references/durable-runs.md](references/durable-runs.md) |
| **Hosting an MCP server** - fastmcp streamable HTTP transport, swappable Authenticator seam (shared-token to Entra), trust-boundary framing against prompt injection | [references/mcp-hosting.md](references/mcp-hosting.md) |
| **Evals for the agent** - output-quality testing (golden sets, behavioral assertions, LLM-as-judge), regression-on-prompt-change, cross-tier testing, and a build-spec for the you-build-it harness | [references/evals.md](references/evals.md) |
| **Retrieval / RAG** - pgvector on the schema-per-module Postgres, chunking, retrieve-then-ground, required citations, and the trust-boundary tie-in (retrieved text is untrusted data) | [references/retrieval.md](references/retrieval.md) |

## Boundaries

- **Where the agent runtime deploys (App Runner, Bedrock region, RDS):** app-hosting
- **How the module holding the agent is shaped (FCIS, schema):** app-architecture
- **Workday custom agents (.agent/.agentskill on the Workday platform):** wd-extend-dev (different runtime entirely)

## Lifecycle neighbors

Fills the module that app-architecture shaped with agent logic, deployed by the pipeline
app-hosting owns. This is the "make it think" skill.

**Ship gate for this track (not the Workday `quality-gates.md` registry):** before a hosted agentic tool ships, run the conformance checklist in **app-harness** (`references/conformance-checklist.md` - AWS Well-Architected Agentic AI Lens + OWASP Top 10 for LLM Apps). The app-* family deliberately does not use the Workday delivery quality-gate footer.

> Modeled on a private reference architecture. Patterns only - no reference-project or client
> source copied. The boto3-for-Bedrock decision is the single most reusable insight here for a
> corporate-proxy environment.
