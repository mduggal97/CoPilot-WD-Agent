---
name: practice-lifecycle
description: >-
  The TOP-LEVEL front door for the Workday Practice Delivery and Innovation suite: forks the two
  tracks and points to the right router. Use when starting something new and unsure of the track,
  when the request is "build a tool / build an app / build a product / an internal accelerator"
  and is NOT obviously a Workday Extend app, or for "which track / where do I start / what can
  this suite do". TRIGGERS: "build a tool", "build an app", "build a product", "internal tool",
  "accelerator", "not a Workday app", "which skill / which track", "where do I start", "what do
  you want to build", "productize this". Track 1, WORKDAY DELIVERY (a client Extend/Integration
  project): wd-extend-lifecycle. Track 2, BUILD A TOOL/PRODUCT (a web app or agentic tool on AWS,
  not an Extend app): app-architecture, plus market-research for whether to build. A clearly
  Workday delivery phase (estimate, discover, design, Extend build, tenant, deploy) goes straight
  to wd-extend-lifecycle.
---

# Practice front door - which track are you on?

This is the top-level router for the suite. It has ONE job: fork cleanly between the
two things the practice does, so you land in the right place. Ask the first question:

**Are you DELIVERING a Workday project, or BUILDING a tool/product?**

## Track 1 - Workday delivery (client Extend / Integration project)

Delivering a Workday Extend app or integration for a client - the estimate -> discover ->
design -> build -> test -> deploy -> run lifecycle. This is the mature, deep track.

**Go to: wd-extend-lifecycle** (the Workday delivery map, phase-by-phase, with the mandatory
gates and preflights). Everything wd-* lives under it.

Signals you're on this track: an RFP or SOW, a client tenant, Extend/O4I, EIB/Studio/Core
Connector, a Workday go-live, UAT in a tenant, "promote to prod."

## Track 2 - Build & host a tool/product (any platform, not Workday Extend)

Building a web app or agentic tool - for the practice or for a customer - hosted on
AWS (React SPA + FastAPI + Postgres + App Runner + Bedrock/Anthropic + Entra). This is the
Innovation-Lead track: tools and applications that are NOT Workday Extend apps.

The Track-2 lifecycle, in order:

- **Whether to build** -> market-research (platform-neutral demand/whitespace/go-no-go)
- **Internal tool or customer product?** -> product-strategy (the disposition gate + productize-an-accelerator lifecycle; sets the support/GTM/security/TCO bar)
- **Discovery + design + estimate** -> app-architecture references/discovery-and-design-brief.md + estimating.md (the non-Workday design front-end)
- **Shape it to scale** -> app-architecture (module contract, topology) - then app-hosting (ship it on AWS), app-agentic (make it agentic), app-harness (the build loop + conformance ship gate)
- **Integrate other SaaS** (Salesforce / ServiceNow / data platforms) -> saas-integration
- **Take it to market** -> product-gtm (non-Workday channels: standalone SaaS, AppExchange, ServiceNow Store, AppSource) or bow-sales-enablement (the Workday Marketplace channel)
- **Run a SOLD product as a business** (customer product only) -> product-operations (SLA/incident, versioning, billing, customer success, compliance-ops)

Signals you're on this track: "build a tool / an app / a portal / an agent," a hosted web
app, "not in Workday," an internal accelerator, a productized SaaS idea.

## Shared upstream - whether to build at all

**market-research** (platform-neutral) runs the *whether/what to build* decision for ANY
platform - Workday Marketplace, Salesforce AppExchange, ServiceNow, or a standalone SaaS. A GO
decision then routes into Track 1 (a Workday build) or Track 2 (a hosted tool). Start there
when the question is "is this worth building" rather than "how do I build it."

## Cross-cutting (spans both tracks)

- **session-orchestration** - when a task is big enough to split, fork work out to other agents / sessions / models and route each piece to the right model (up for hard reasoning, down for mechanical/bulk). Applies to either track.
- **Standing operating gates** (both tracks): measure-twice requirements-first (a blank SECURITY section is a hard stop before you build), automate-first (do it via API/wdcli/browser; prompt only for the strictly-disallowed set), and self-QA before handoff (correctness + presentation). Owned in wd-extend-lifecycle `references/quality-gates.md`.

**Track-2 scope note (2026-09-10):** Track 2 is proven for INTERNAL practice tools today. The CUSTOMER-SOLD product path (a next-year roadmap item) is now built out as METHODOLOGY - public/multi-tenant hosting (app-hosting customer-hosting.md + app-architecture multi-tenancy.md), run-as-a-business (product-operations), and the DPA/legal paper (wd-contracts saas-data-processing.md). Route a CUSTOMER-SOLD disposition through those. The real AWS-security architecture and the DPA/SOC 2 still need IT/security + counsel sign-off before an actual customer launch - the suite carries the how, not those approvals.

## The rule that spans both tracks

Whichever track: **market-research decides whether to build; the track routers decide how.**
Do not skip a track's own gates - Track 1's quality-gates registry (wd-extend-lifecycle) and
Track 2's conformance checklist (app-harness) are the two ship gates, and they are different by
design.

## When NOT to use this skill

If the task is already clearly inside one track (a Workday phase, or a specific app-* build
step), skip the fork and go straight to that track's router - this skill is only for the
"which track / where do I start" moment.
