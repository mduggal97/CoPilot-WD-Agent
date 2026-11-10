---
name: market-research
description: >-
  Identify and validate MARKET / PRODUCT opportunities - whether there is unmet demand
  for an app you could build and ship to a marketplace, and whether it is worth
  building. Platform-neutral: Workday Marketplace / Built-on-Workday AND any other
  marketplace or SaaS (Salesforce AppExchange, ServiceNow Store, Microsoft AppSource,
  standalone SaaS). Use for market research, opportunity or whitespace / gap analysis,
  "what should we build", a demand assessment, competitive analysis, market sizing
  (TAM/SAM/SOM), idea prioritization, a build-vs-buy or build/no-build (go/no-go)
  decision, product-market-fit hypothesis, or an opportunity brief for a new productized
  app. Use THIS for the upstream "whether and what to build" call; it hands a validated
  concept to bow-sales-enablement (GTM), wd-estimate (build LOE), and the design skills.
  NOT client-requirements discovery for a delivery engagement (wd-discovery); NOT
  go-to-market for an app already chosen (bow-sales-enablement).
---

# market-research - opportunity discovery, validation & the build/no-build call

Before a product exists there is a bet: that a real, sizeable, under-served need exists and that you can serve
it better than the alternatives. This skill runs that bet deliberately - find the demand signal, map the
whitespace, size it, validate it, score it against other ideas, check platform fit, and produce a one-page
opportunity brief with a **go / no-go** recommendation. It is deliberately **platform-neutral**: the method is
the same whether the target is the Workday Marketplace / Built-on-Workday, Salesforce AppExchange, ServiceNow
Store, Microsoft AppSource, or a standalone SaaS - the target marketplace is a parameter, handled in the
platform-fit reference.

## When to use this skill

- "What should we build?" / "Where is there a market need we could serve with an app?"
- Opportunity / whitespace / gap analysis for a marketplace or SaaS category
- Market sizing (TAM / SAM / SOM), demand assessment, product-market-fit hypothesis
- Prioritizing several product ideas; a build-vs-buy or **build / no-build (go/no-go)** decision
- Turning a "we keep building this for clients" pattern into a productization case

## The flow (five moves -> one brief)

| Move | What it answers | Reference |
|---|---|---|
| 1. Signal | Where is the demand, and is it real? | [references/opportunity-signals.md](references/opportunity-signals.md) |
| 2. Whitespace | What already exists, and where is the gap / differentiation? | [references/assess-and-prioritize.md](references/assess-and-prioritize.md) |
| 3. Size & validate | How big is it, who buys, is it a painkiller, will they pay? | [references/assess-and-prioritize.md](references/assess-and-prioritize.md) |
| 4. Score & rank | How does it compare to the other ideas (one scorecard)? | [references/assess-and-prioritize.md](references/assess-and-prioritize.md) |
| 5. Platform fit + brief | Can we distribute/monetize it on the target marketplace, and what's the recommendation? | [references/platform-fit-and-brief.md](references/platform-fit-and-brief.md) |

Right-size to the decision: a quick "is this worth a deeper look?" triage is moves 1-2; a real build/no-build
runs all five and produces the brief.

## Core principles

1. **Painkiller over vitamin.** The strongest opportunities relieve a frequent, expensive, or risky pain -
   not a nice-to-have. Rank problem SEVERITY x FREQUENCY, not feature appeal.
2. **The best signal is your own delivery pattern.** A capability the practice **keeps custom-building for
   client after client** is pre-validated demand with a reuse head start - mine the reusable-asset catalog
   (wd-practice-ops reuse-and-asset-catalog.md) first; effort is a tiebreaker, not the sort key -
   rank by cross-client pattern recurrence, not by how easy something is to build.
3. **Whitespace, not wishful thinking.** An idea is only an opportunity if it is under-served: map what the
   marketplace already offers and where incumbents/natives fall short before claiming a gap.
4. **Beware the platform eating your lunch.** For a marketplace app, the biggest strategic risk is the
   PLATFORM VENDOR shipping the capability natively ("Evergreen risk" - the same question wd-discovery
   solution-options.md scores for a custom build). Weight it heavily.
5. **Validate before you build, cheaply.** Prefer cheap signals (interviews, a landing-page smoke test, a
   design partner, pre-orders) over building on conviction; a go decision needs evidence, not a hunch.
6. **Evidence and honesty.** Every demand claim, size number, and competitor fact carries a **source + date**
   and the verify-before-promote discipline; do not fabricate a market. Research uses public/ethical sources
   only (see the governance note in opportunity-signals.md). Claims that will later go into marketing inherit
   bow-sales-enablement's claims-register governance.

## Boundaries

- **bow-sales-enablement** owns go-to-market for an app you have ALREADY decided to build (listing, messaging,
  pricing, battlecards). THIS skill is upstream of it: it decides WHETHER and WHAT to build, then hands a
  validated concept over. (Some artifacts rhyme - a market-sizing here vs the value calculator there - but the
  decision vs the sell are different jobs.)
- **wd-discovery** owns requirements discovery for a specific client delivery engagement. THIS skill studies a
  MARKET (many buyers), not one client's requirements.
- **wd-estimate** owns sizing/pricing a specific deal or build LOE. THIS skill does MARKET sizing (TAM/SAM/SOM)
  and hands the chosen concept to wd-estimate for the build LOE.
- **wd-practice-ops** owns the reusable-asset catalog (what we have built); THIS skill reads it as the #1
  demand signal and feeds productization candidates back to it and to bow-sales-enablement.

## Lifecycle neighbors

- **Feeds (route by track):** a GO decision forks by what's being built. **Workday build** -> the Workday
  design/build skills (wd-design-doc, wd-extend-dev) + wd-estimate (LOE) + bow-sales-enablement (Workday
  Marketplace/BoW GTM). **Non-Workday hosted tool/product** -> **product-strategy** (internal-tool-vs-customer-product
  disposition first) -> **app-architecture** (the tool-building entry: discovery/design brief + estimate, then
  shape it; then app-hosting/app-agentic) -> **product-gtm** (non-Workday-channel GTM: standalone SaaS,
  AppExchange, ServiceNow Store, AppSource). Also feeds wd-practice-ops (productization candidate + reuse
  catalog), and **wd-estimate `proposal-content.md` - the market evidence (why-now, whitespace, sizing,
  native/build-vs-buy risk) is a REQUIRED, sourced input to every proposal and product pitch**. This skill is
  PLATFORM-NEUTRAL (Workday Marketplace, Salesforce AppExchange, ServiceNow, standalone SaaS - the target is a
  parameter); do not let its GO decision dead-end into the Workday-only build lifecycle.
- **Draws from:** wd-practice-ops reuse catalog (recurring-build signal), wd-discovery solution-options
  (Evergreen / build-vs-native framing), and public market/competitor sources.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle
`references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
