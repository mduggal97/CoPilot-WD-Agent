# Agent & Flex Credit Go-Live Checklist

These items apply when the implementation includes Workday AI agents, Extend apps
that consume Flex Credits, or API-heavy integrations under the consumption model
(Aug 2026 platform changes). Work them into the go/no-go cutover checklist and the
go-live prep session.

**Numbers live elsewhere - single owner.** For every commercial figure - entitlement
tiers, credit pricing, complimentary-credit amounts, the Extend multiplier, the agent
Rate Card, and the non-production metering rule - see the canonical owner,
`wd-estimate/references/flex-credits.md`. The actions below REFERENCE those figures
rather than restating them; never hardcode a number here.

## The checklist items

- **UMSA verification before go-live:** Confirm the customer has signed the
  Unified Master Subscription Agreement (UMSA). Without it, no agent features
  are accessible in production. Self-migration takes 24-48 hours. If the
  customer has not signed, flag this as a go-live blocker.
- **Agent System of Record (ASOR):** At go-live, agents must be registered in
  ASOR for governance and provisioning. Verify agent registrations, skill
  configurations, and access controls are set before cutover.
- **Platform Consumption Console (PCC):** Ensure the customer has PCC access
  configured. PCC is the monitoring dashboard for Flex Credit consumption, API
  usage, and agent activity - this is how the customer will see ongoing costs
  post-go-live. Walk them through it during go-live prep. (The post-go-live
  review cadence is owned by wd-post-go-live SKILL.md "Flex Credit and agent
  monitoring" - monthly PCC review, quarterly in the QBR per `references/account-growth.md`.)
- **Complimentary credit activation:** Confirm the customer's complimentary
  credit tier is active (amounts in flex-credits.md). Credits are pro-rated
  if signed mid-year. No rollover year to year.
- **API entitlement baseline:** Document the customer's annual API entitlement
  and any SKU multipliers (see flex-credits.md) in the go-live checklist.
  Post-go-live API consumption is metered and visible to the customer in PCC.
- **Complete testing in non-production first:** Non-production tenant usage is
  cheap (most agents and all API/integration testing do not meter in sandbox -
  verify per-agent in flex-credits.md), so finish agent and API testing in
  non-production before go-live.
- **New Workday Experience timeline:** If the implementation includes UI
  changes, note the current state: the New Workday Experience opt-in opened
  Jan 31 2026 and became the default in 26R1 (both already past); it becomes
  permanent in 26R2. AI semantic search in the new experience requires UMSA/ISA.

## Lifecycle handoff

These are go-live-gate items (owned here). Once live, ongoing PCC review cadence,
credit burn-rate alerting, ASOR agent-performance monitoring, and the quarterly
Flex Credit review move to **wd-post-go-live** (SKILL.md, Flex Credit and agent
monitoring section).
