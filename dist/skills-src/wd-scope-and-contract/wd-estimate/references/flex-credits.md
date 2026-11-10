# Flex Credits + API metering - the canonical fact block (single owner)

This is the ONE place the suite states the Flex-Credit commercial model. Every other skill that
needs a number points here rather than restating it (the propagation rule - one owner, no drift).
Numbers are the May-2026 platform policy; verify the current Rate Card + entitlement for a live
engagement (Workday updates them and runs promotions).

## Pricing

- **1 credit = $0.10.**
- **Overage: 60 credits per 10,000 API calls = $6.00 per 10K calls** once the annual entitlement
  is exhausted.

## Annual API entitlement (by org size)

- **Base entitlement: ~2.5M to 6.5M API calls / year**, scaled by org size (the low end for small
  orgs, the 6.5M ceiling for the largest base tier).
- **Extend SKU holders get a +50% multiplier** on the base entitlement - a real incentive for Extend
  over standalone integrations. Example: a 10K-29K-worker org's 4.5M base becomes **6.75M effective**
  (post-multiplier; the 6.5M figure is the BASE-tier ceiling, so a post-multiplier number can exceed
  it - that is expected, not a conflict).
- **Complimentary credits: ~15K to 200K per year**, by tier, on top of the call entitlement.

## What counts toward the entitlement (overages = Flex Credits)

- ALL EIB integrations; ALL Studio / CLAR integrations; certified partner integrations;
  customer-built Extend apps; Core Connectors **augmented by Studio** (the augmented portion);
  external apps + third-party AI agents.

## What does NOT count (free / included)

- Workday-built Core Connectors (when not augmented); Workday agents on the Flex Credit Rate Card;
  Built-on-Workday partner apps; Workday acquisitions (HiredScore, Paradox); Workday Everywhere
  (Slack/Teams); specific third-party time-clock endpoints; 5XX errors.

## Agent Rate Card (agents meter by the card, NOT raw API calls)

Wrapping logic in an agent can be commercially better than raw API consumption. Per-agent credit
cost (canonical units - use these, do not restate in other units):

- **Self-Service Assistant = 1 credit** (per request).
- **Payroll Monitoring = 5 credits per 10 worker records per run** (the precise unit; earlier
  "5-10 credits/request" phrasings collapse to this - cite this form).
- **Planning agent = 8 credits** (per request).

## Non-production

- **Non-production / sandbox testing is free for MOST agents** - but NOT categorically universal:
  a few agents DO meter in non-prod. **Verify per-agent in the current Rate Card** before assuming a
  test run is free. (This is the harmonized statement - do not restate "non-prod is free" as an
  absolute.)

## Design + delivery implications

- Every integration build, IDD, and proposal should include an **API consumption estimate**.
- When a **Workday-built Core Connector** can serve the use case, it is free at the API layer -
  prefer it. A **Studio augmentation** makes the entire connector's calls metered - factor that in.
- Promotions/entitlement change over time (promotions ran through ~Oct 2026) - confirm current terms
  per engagement.

## Who points here

wd-estimate (owner - LOE/pricing), wd-contracts (SOW cost terms), wd-design-doc (design API-cost
line), wd-deployment (go-live cost), wd-post-go-live (run cost), wd-integration-dev (integration
metering), wd-discovery solution-options.md (build-vs-buy cost), wd-extend-dev solutioning.md +
custom-agents.md (design-time cost dimension). Deeper model + counting rules + promo history:
project-memory reference "WD Flex Credits Model".
