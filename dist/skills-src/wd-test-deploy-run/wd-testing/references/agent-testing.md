# Agent and API metering test considerations

Test-design implications of the Aug 2026 Workday AI platform changes (Flex Credits,
native agents, Data Cloud) - what and how you test when a solution includes Workday
agents or meaningful API/integration volume.

**Numbers live elsewhere.** For the commercial model itself - entitlement tiers, credit
pricing, the agent Rate Card, what counts, and the non-production metering rule - see the
canonical owner, `wd-estimate/references/flex-credits.md`. Do not restate the figures here;
this reference owns only the test-design implications.

---

## Non-production testing is cheap, but verify per-agent

Non-production API and integration testing consumes no Flex Credits, and MOST agents also do
not meter in sandbox - so run high-volume, edge-case-heavy suites in dev/impl tenants without
budget concern. A few agents DO meter in non-prod, so confirm the specific agent in the current
Rate Card (see flex-credits.md) before assuming a given test run is free.

## Agent testing scenarios

For solutions that include Workday agents (SSA, BP Optimize, Payroll Monitoring, custom agents),
add agent-specific test scenarios to the unit test and E2E test plans:

- **Knowledge base quality** - test SSA responses against the customer's actual knowledge base.
  Bad answers in production trace to duplicate policies, outdated content, or missing topics.
  Test the **top 20 expected questions** and verify answer accuracy, source attribution, and
  fallback behavior.
- **Agent skill coverage** - verify which SSA skills are enabled (there are 7 - most customers
  only activate 2-3 initially). Test each enabled skill with representative scenarios; confirm
  disabled skills do not surface.
- **BP Optimize recommendations** - test that process optimization suggestions are accurate and
  actionable for the customer's actual business process configurations. Verify recommendations
  against known BP bottlenecks.
- **Payroll Monitoring accuracy** - test monitoring outputs against known payroll scenarios
  (including edge cases like retroactive changes, off-cycle runs, and boundary amounts) before
  enabling in production.
- **Custom agent flows** - for Extend-built custom agents (`.agent`/`.agentskill`/`.agentflow`),
  test the full agent conversation flow, error handling, and fallback behavior. Include
  multi-turn conversations, ambiguous inputs, and permission-boundary scenarios.

## API volume estimation testing

During performance/load testing, capture API call counts **per integration and per Extend app**.
These actuals feed the Flex Credit impact estimate in the design doc (wd-design-doc owns the tab).
Compare test API volumes to the estimates - significant variances should update the design doc
before go-live. This is the cheapest way to validate credit projections since non-production calls
are free.

## Production smoke test credit awareness

When running post-go-live smoke tests in production, note that those API calls **DO count** toward
entitlements and agent actions **DO consume credits**. Keep production smoke tests targeted and
efficient - run the critical-path set only, not the full regression suite.

## Exclude non-counting responses from estimates

Some responses (e.g. 5XX errors) do not count toward metering - see flex-credits.md for the full
list. Do not include server-error retries in credit consumption estimates.
