# Productization lifecycle - turn an internal accelerator into a sellable product

Reference for `product-strategy`. This is the staged path for taking an INTERNAL accelerator - a
proven asset from the wd-practice-ops reuse catalog - and turning it into a sellable / hosted
CUSTOMER PRODUCT. Each stage has a GATE; you do not enter the next stage until the current gate
passes. The lifecycle exists because a product is an internal tool that GRADUATED, and graduation
has a bar - you do not "flip a switch" from internal to sellable.

Enter this lifecycle only AFTER the disposition gate (disposition-gate.md) lands CUSTOMER PRODUCT
(or a candidate has been demand-validated). If demand is unproven, stop and run market-research
first - productizing on a hunch is the most expensive mistake this lifecycle prevents.

## Table of contents

- [The one rule - you build it, you run it](#the-rule)
- [Stage 0 - validate demand (precondition)](#stage-0)
- [The seven stages + gates](#stages)
- [Stage detail](#stage-detail)
- [The operating-model implications](#operating-model)
- [What you hand off, and to whom](#handoffs)

---

<a name="the-rule"></a>
## The one rule - you build it, you run it

Productizing is not just a build task; it is an OWNERSHIP commitment. The moment an internal tool
becomes a customer product, someone owns its run cost, its support load, its security blast radius,
and its roadmap - for the life of the product, not just to launch. Name that owner and fund that
operating model BEFORE stage 1, or you will ship a product no team is resourced to run. This is the
platform-as-a-product / "you build it, you run it" framing (Team Topologies - INSPIRATION, cite,
do not copy) applied to the practice's own tools: an unowned product is a liability that degrades
until it embarrasses the firm.

---

<a name="stage-0"></a>
## Stage 0 - validate demand (precondition, not a stage you own)

Before ANY productization work, the demand must be real. An asset being reused a lot internally is a
strong SIGNAL but not proof that external buyers will PAY.

- **Gate to enter stage 1:** market-research has produced a GO - validated demand, whitespace,
  sizing, and a build-vs-native / build-vs-buy read - for THIS asset as an external product. A
  reuse-count is not a market. Do not skip this because "we already built it."

---

<a name="stages"></a>
## The seven stages + gates

| # | Stage | What happens | Gate to the NEXT stage |
|---|---|---|---|
| 1 | **Harden** | Make the internal tool robust - error handling, tests, mutation-proof coverage, no happy-path-only code | Builds green + tested to product bar (app-harness build discipline); no known internal-only shortcuts remain |
| 2 | **Generalize / de-client** | Strip every client / engagement specific; make it multi-customer and configurable, not hard-coded to one tenant | Zero client names / IDs / PII; genericized per the reuse-catalog de-brand transform; multi-tenant configurable |
| 3 | **Security + compliance uplift** | Multi-tenant isolation, data-residency, external-attestation readiness, threat model | app-harness conformance-checklist.md PASSes (AWS Well-Architected Agentic AI Lens + OWASP Top 10 for LLM Apps); tenancy isolation verified |
| 4 | **Support model** | Define the SLA, support channel, on-call / escalation, incident + rollback runbook, versioning + deprecation policy | A written support model + SLA a customer can be promised; a named owner accepts the "you run it" commitment |
| 5 | **Pricing + packaging** | Editions, price, licensing terms, contract paper | product-gtm (non-Workday) or bow-sales-enablement (Workday Marketplace / BoW) has priced + packaged it; wd-contracts has the paper |
| 6 | **Hosting** | Stand it up at the product hosting bar - multi-tenant, prod-grade observability + alarms, TCO-sized, PITR / rollback | app-hosting prod pipeline deploys it; observability + budget alarms live; TCO sized and accepted |
| 7 | **Launch** | List / announce, enable sales, close the loop back to the catalog | GTM launch kit shipped (product-gtm / bow-sales-enablement); reuse-catalog maturity updated proven -> productized |

**The gates are not bureaucracy.** Each one blocks a specific failure: shipping a fragile tool
(gate 1), leaking a client's data or name (gate 2), failing a customer audit (gate 3), promising an
SLA no one owns (gate 4), selling at a price that loses money (gate 5), a prod outage no one can roll
back (gate 6). Skipping a gate does not save time; it moves the cost to after launch, where it is
larger and public.

---

<a name="stage-detail"></a>
## Stage detail - the why behind each

**1. Harden.** An internal tool is allowed to be fragile because the team that runs it knows its
sharp edges. A customer does not. Harden to the product bar - real error handling, tests that would
catch a regression, no "this only works if you run it the way I do." Use the app-harness build
discipline (complexity routing, commit-at-every-green, mutation-proof testing).

**2. Generalize / de-client.** The asset was born on an engagement; it carries that engagement's
DNA - tenant IDs, client names, hard-coded org structures, one customer's assumptions. Strip all of
it. Use the reuse-catalog de-brand naming transform (wd-practice-ops reuse-and-asset-catalog.md) for
the name and the content-scrub rules for the guts. The output must be multi-customer and
CONFIGURABLE, not a second hard-coded fork. A product that only works for the client it was born on
is not a product.

**3. Security + compliance uplift.** This is the stage internal tools most often lack, and the most
expensive to retrofit. An internal tool trusts its users and its network; a customer product does
not. Add multi-tenant isolation (one customer cannot see another's data), data-residency handling,
and external-attestation readiness. The gate is the app-harness conformance checklist - grade against
the AWS Well-Architected Agentic AI Lens and OWASP Top 10 for LLM Apps and record a verdict per line.
An honest GAP is worth more than a green box that is not true.

**4. Support model.** A product a customer pays for comes with a promise: when it breaks, someone
answers. Define the SLA, the support channel, the on-call / escalation, the incident + rollback
runbook, and the versioning + deprecation policy. Crucially, a NAMED owner must ACCEPT the "you run
it" commitment here - this is the ownership gate. No owner, no product.

**5. Pricing + packaging.** Now it hands to GTM: editions, list price, licensing terms. Route by
channel - product-gtm for non-Workday (SaaS, AppExchange, ServiceNow, AppSource) or
bow-sales-enablement for the Workday Marketplace / BoW channel. wd-contracts turns the packaging into
contract paper. This skill decided it should be a product; GTM decides how it is sold.

**6. Hosting.** Stand it up at the CUSTOMER PRODUCT hosting bar via app-hosting - multi-tenant,
prod-grade observability + alarms (5xx / latency / agent-failure / budget burn), TCO-sized, with
PITR + rollback discipline. This is heavier than the internal accelerator's private-VPN-single-tenant
posture; that gap is exactly what the disposition posture warned about.

**7. Launch.** Ship the GTM launch kit, enable sales, announce / list. Then close the loop: update
the asset's maturity in the reuse catalog from proven to PRODUCTIZED, so the practice knows this
accelerator graduated and the next team finds the product, not the old internal fork.

---

<a name="operating-model"></a>
## The operating-model implications

Productizing changes the practice's operating model, not just its asset list:

- **A funded owner, for the life of the product.** Run cost, support, and roadmap are ongoing - budget
  them as cost of goods, not a one-time build. An internal tool's owner can go quiet; a product's
  cannot.
- **The blast radius grows.** An internal bug annoys the team; a product bug can breach a customer or
  break an SLA. The security + support bars (stages 3-4) are the price of that larger blast radius.
- **Two things now exist where there was one.** The internal accelerator may still be used internally
  AND a productized version sold externally. Decide whether they stay one codebase (versioned) or
  fork - and record BOTH in the catalog with their maturity. A shared codebase inherits the
  reuse-catalog downstream-impact discipline (a change to the shared core checks every consumer).
- **The disposition can be revisited.** If a product fails to sell, it can be retired TO an internal
  accelerator (drop the product posture, keep the tool) - a demotion is a legitimate outcome, not
  only a promotion.

---

<a name="handoffs"></a>
## What you hand off, and to whom

- **Up front (precondition):** market-research - validate external demand before stage 1.
- **Stages 1-3 (build / harden / secure):** app-architecture (shape), app-hosting (host),
  app-agentic (agent runtime), app-harness (build discipline + the conformance ship gate).
- **Stage 5 (price / package / paper):** product-gtm (non-Workday channels) or bow-sales-enablement
  (Workday Marketplace / BoW); wd-contracts (SaaS / subscription agreement); wd-estimate
  (productization LOE).
- **Stage 7 (launch + close loop):** the GTM skill's launch kit; wd-practice-ops
  reuse-and-asset-catalog.md - update maturity proven -> productized.

This skill OWNS the staged decision and the gates; each stage's actual work is done by the skill it
hands to. Keep the disposition record (from disposition-gate.md) attached through all seven stages so
every downstream skill inherits the CUSTOMER PRODUCT bar.
