---
name: product-strategy
description: >-
  Owns the DISPOSITION DECISION for anything the practice builds - an INTERNAL practice
  accelerator (a tool the team runs for itself) or a CUSTOMER-SOLD product? - and the
  productize-an-internal-accelerator lifecycle. The call sets very different bars (support / SLA,
  GTM, security / compliance / data residency, IP / licensing, TCO, polish), so it is made once,
  before the build hardens: the "you build it, you run it" question for the practice's own tools.
  Use when deciding "internal tool or customer product?", "should we productize this", "productize
  this accelerator", "internal accelerator vs product", "what support / SLA does this need", "is
  this sellable", "build-it-run-it ownership", or setting the posture for a tool worth building.
  Comes after market-research. NOT demand validation (market-research); NOT the build or hosting
  (app-* family); NOT go-to-market for a chosen product (product-gtm, or bow-sales-enablement for
  the Workday Marketplace).
---

# product-strategy - internal accelerator or customer product? (the disposition call)

This skill is a thin index. It owns ONE decision and ONE lifecycle:

- **The disposition gate** - for anything the practice is about to build (or already built for
  itself), is it an INTERNAL practice accelerator or a CUSTOMER-SOLD product? That single answer
  sets the downstream bars - support model / SLA, GTM, security / compliance / data-residency,
  IP / licensing, TCO tolerance, polish - which are very different for the two answers.
- **The productization lifecycle** - the staged path for taking an INTERNAL accelerator (from the
  wd-practice-ops reuse catalog) and turning it into a sellable / hosted product, with a gate
  between each stage.

## Why this is its own decision

It is tempting to build first and ask "can we sell this?" later. That is backwards and expensive.
An internal accelerator and a customer product diverge on almost every non-functional axis, and
those axes are cheap to design in and costly to retrofit. Deciding the disposition FIRST - before
the build hardens - means you build to the right bar the first time. This is the
**"you build it, you run it"** ownership question (platform-as-a-product / Team Topologies framing)
applied to the practice's own tools: whoever owns a thing long-term owns its run cost, its support
load, and its blast radius, so name that owner before you build, not after.

## What this skill owns

- **The disposition decision** - internal accelerator vs customer product, on named criteria.
- **The downstream POSTURE** each answer sets - the bar the build, host, and support work is held to.
- **The productize-an-internal-accelerator lifecycle** - stages + gates from a proven internal tool
  to a launched product.
- **The build-it-run-it ownership + operating-model implications** of each disposition.

## Reference map - read what you need

| You're deciding | Read |
|---|---|
| **Internal tool or customer product?** - run the decision gate on the criteria (who is the user, sold or free, support / SLA, security / compliance / data-residency, IP / licensing, who runs it long-term, TCO tolerance) and read off the downstream posture for each answer | [references/disposition-gate.md](references/disposition-gate.md) |
| **Productize an internal accelerator** - the staged path (harden -> generalize / de-client -> security + compliance uplift -> support model -> pricing + packaging -> hosting -> launch), the ownership implications, and the gate between each stage | [references/productization-lifecycle.md](references/productization-lifecycle.md) |

## Core principles

1. **Decide disposition BEFORE the build hardens.** The internal-vs-external call is cheap up front
   and expensive to retrofit; make it once, deliberately, and hold the build to that bar.
2. **You build it, you run it.** Name the long-term owner of the run cost, support load, and blast
   radius before the build - an unowned tool is a liability, not an asset.
3. **Internal is a real, honorable answer.** Most accelerators SHOULD stay internal; "not sellable"
   is a success, not a failure - it just skips GTM + conformance + TCO and takes a lighter posture.
4. **Demand is a precondition, not this skill's job.** Do not productize on a hunch - market-research
   validates demand FIRST; this skill assumes a build-worthy idea is already on the table.
5. **A product is an internal accelerator that graduated - and graduation has a bar.** The bar is
   the app-harness conformance checklist plus a real support model and TCO; passing it is what makes
   an internal tool defensible as a product.

## Boundaries

- **market-research** owns demand - WHETHER and WHAT to build (opportunity, whitespace, sizing,
  go / no-go). THIS skill is DOWNSTREAM: given a build-worthy idea or an existing internal tool,
  what is its disposition and, if a product, how does it get there. Do not re-run demand here.
- **wd-practice-ops reuse-and-asset-catalog.md** owns the register of internal accelerators (what
  the practice has built). THIS skill reads the catalog as the SOURCE of productization candidates;
  a productized asset graduates its catalog maturity from proven to productized.
- **app-architecture / app-hosting / app-agentic** own the BUILD and HOST once a disposition is set;
  a GO-to-productize routes there for the actual work. THIS skill sets the bar; those skills meet it.
- **product-gtm** (non-Workday channels + the shared GTM core) and **bow-sales-enablement** (the
  Workday Marketplace / BoW channel) own GTM once it IS a product - positioning, messaging, pricing
  execution, playbook, battlecards. THIS skill decides it should BE a product and hands off by
  channel; it does not do the selling.
- **app-harness references/conformance-checklist.md** is the SHIP gate for the built product; THIS
  skill's productization lifecycle cross-links it, it does not duplicate it.

## Lifecycle neighbors

- **Draws from:** market-research (a validated, build-worthy concept), and wd-practice-ops reuse
  catalog (the existing internal accelerator to productize).
- **Feeds:** app-architecture (+ app-hosting / app-agentic) for the build / host at the disposition's
  bar; GTM once it is a product - product-gtm (non-Workday channels) or bow-sales-enablement (Workday
  Marketplace / BoW); wd-practice-ops (updates the catalog maturity); wd-estimate (the productization
  LOE, if a customer product).
- **Runs at:** the moment a build-worthy idea or an existing internal tool needs its disposition set
  - after market-research says GO, before app-architecture scaffolds to a bar.

**CUSTOMER-SOLD disposition - route to the customer-product path (2026-09-10):** if the disposition comes
out **CUSTOMER-SOLD product**, the extra bar a sold hosted product needs now HAS a home (the practice built
it out; the actual AWS-security and legal decisions are still real firm calls, not suite-only):
- **Public + multi-tenant hosting** -> app-hosting `references/customer-hosting.md` (public ingress + WAF,
  external identity, per-customer provisioning) + app-architecture `references/multi-tenancy.md` (Pool/Bridge/
  Silo isolation + the cross-tenant-leak invariant). The INTERNAL architecture does NOT reach a paying customer.
- **Run it as a business** -> **product-operations** (SLA/incident/on-call, versioning, billing/metering,
  customer success, compliance-ops).
- **Legal paper** -> wd-contracts `references/saas-data-processing.md` (DPA, data-residency, security exhibit).
- **Customer-grade testing** -> app-harness `references/testing.md` (multi-tenant isolation test, security/
  pen-test, load, formal UAT).
Set the disposition's posture (support/SLA/security/TCO bar) knowing these exist, and route the build through
them. (Note: hosted products for CUSTOMERS are a next-year roadmap item being built ahead - the methodology is
here; the public-hosting security architecture + the DPA/SOC 2 still need IT/security + counsel sign-off.)

**Quality-gate rule (suite-wide):** the disposition memo + productization plan this skill produces have a
named check in wd-extend-lifecycle `references/quality-gates.md` (the writing-quality gate) - run it and
report the result with the deliverable.

> Framing inspired by Team Topologies (platform-as-a-product, "you build it, you run it") -
> INSPIRATION, cite, do not copy. No client names, PII, or firm-internal identifiers in this skill.
