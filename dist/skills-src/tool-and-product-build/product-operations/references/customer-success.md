# Customer success - onboarding through renewal, the account-growth analogue

Reference for `product-operations`. A sold hosted product does not stop needing attention
once it is live - a customer who never activates, never adopts, and quietly churns at
renewal is a business failure even if the infra never went down. This is the Track-2 twin of
wd-post-go-live's value-capture, adoption-and-feedback, and account-growth references for a
Workday Extend app - same discipline (baseline early, measure continuously, act on the
trend), different motion (a subscription renewal instead of a project closeout). This file
is self-contained: read it without having read anything else in the suite.

## Table of contents

- [Onboarding and activation](#onboarding)
- [Adoption and health scoring](#health-scoring)
- [QBRs](#qbrs)
- [Renewal and expansion](#renewal-expansion)
- [Churn signals](#churn-signals)
- [What to remember](#remember)

---

<a name="onboarding"></a>
## 1. Onboarding and activation

**Onboarding ends at activation, not at signup.** A customer who signed up and never
completed the setup steps to get real value is not onboarded - they are a churn risk with a
credit card on file. Define activation concretely and specifically for the product (e.g.,
"connected their first data source and ran a report" - not "logged in").

- **Time-to-first-value is the metric that matters most in the first days.** The faster a
  new customer reaches their activation milestone, the more likely they convert to a
  retained, paying account. Instrument the onboarding funnel (signup - first login - key
  setup steps - activation event) so a stall is visible, not anecdotal.
- **A guided setup beats a documentation link.** Where the product supports it, an in-app
  checklist or guided flow for the first-run setup measurably outperforms "read the docs and
  figure it out" for activation rate - reserve deep documentation for reference use after
  activation, not as the primary onboarding path.
- **A human touch for higher tiers.** A self-serve/Starter tier can onboard entirely through
  product UX; a Pro/Enterprise tier customer typically expects (and the pricing usually
  assumes, per `product-gtm/references/pricing-and-value.md` section 6) a named onboarding
  contact or a kickoff call. Match onboarding intensity to the tier the customer bought, not
  a one-size approach.
- **Capture a baseline at onboarding**, not later. Ask the customer's own numbers (current
  process time, error rate, cost) at kickoff, the same way wd-discovery baselines outcome
  metrics for a Workday engagement - this baseline is what makes a later QBR's "value
  delivered" claim honest rather than invented after the fact.

---

<a name="health-scoring"></a>
## 2. Adoption and health scoring

**A health score is a leading indicator; revenue and renewal are the lagging ones.** By the
time a renewal is at risk, the underlying health problem has usually existed for months -
the point of scoring health continuously is to act while there is still time to change the
outcome.

Build a health score from signals in at least three categories, not one:

| Category | Example signals |
|---|---|
| Usage | Login frequency, feature breadth used vs. available, usage trend (growing/flat/declining), time since last active session |
| Support | Ticket volume trend, unresolved Sev1/Sev2 age, repeated tickets on the same issue (a training gap, not a bug) |
| Commercial | Payment/dunning status (billing-and-metering.md section 5), seat utilization vs. purchased, expansion or downgrade requests |
| Relationship | Champion still employed there, executive sponsor engaged, QBR attendance and engagement |

**Weight usage decline heavily and act on it early.** A customer whose usage trend is
declining - even if every ticket is closed and every invoice is paid - is a churn risk
building quietly. Treat a sustained usage decline the way wd-post-go-live treats low
adoption on a live Workday app: a finding worth a proactive outreach, not a metric to
observe passively.

**A single combined score (e.g., red/yellow/green) is useful for triage, but keep the
underlying signals visible** - a green-scoring account with one badly-trending signal
(champion just left) needs a different response than a genuinely all-green account, and a
blended score can hide that.

---

<a name="qbrs"></a>
## 3. QBRs

**A quarterly business review is a standing checkpoint that proves value and surfaces risk
before renewal, not a sales call in disguise.** Shape, adapted from the wd-post-go-live
account-growth pattern for a subscription product:

1. **Usage and health recap** - the adoption trend and health score since the last QBR, in
   the customer's own terms (their team, their workflows), not raw product-analytics jargon.
2. **Value delivered** - outcome metrics against the onboarding baseline (section 1) - hours
   saved, errors avoided, volume processed - the same discipline as a Workday value-capture
   check-in, applied to a subscription product.
3. **Support and reliability recap** - notable incidents (sla-and-support.md), how they were
   handled, and any SLA credits issued - transparency here builds trust more than omission
   does.
4. **Roadmap and what's coming** - relevant upcoming releases (release-management.md's
   changelog, forward-looking) that matter to this customer specifically.
5. **Asks and expansion** - open items from the customer, and where their usage pattern
   suggests a natural tier upgrade or add-on (expansion revenue, section 4).

**Cadence by tier.** Enterprise accounts typically get quarterly reviews; a self-serve tier
usually gets an automated or lighter-touch equivalent (an emailed usage/value summary) since
a live QBR is not economical to staff for every account at that price point. Match review
intensity to what the tier's pricing can economically support.

---

<a name="renewal-expansion"></a>
## 4. Renewal and expansion

**Start the renewal motion well before the renewal date, not at it.** A renewal
conversation that starts the week the contract expires is a negotiation from weakness, not a
relationship checkpoint. A common pattern is a T-minus-90/60/30-day cadence:

- **T-minus 90** - a health check: is this account on track to renew based on the health
  score (section 2)? A red/yellow account gets a save-motion plan now, while there is still
  time to change the trajectory.
- **T-minus 60** - the renewal QBR (a natural place to fold in the regular QBR if timing
  aligns), presenting the value delivered case and surfacing any expansion opportunity.
- **T-minus 30** - the commercial conversation: renewal terms, any price change, and paper
  through wd-contracts.

**Expansion signals to watch for, sourced from usage data (section 2), not just a sales
guess:** a customer approaching or exceeding their seat/usage entitlement consistently, a
customer asking about a capability gated to a higher tier, or a customer's usage pattern
matching a documented use case for an add-on. Feed genuine expansion opportunity into the
same GTM motion `product-gtm` and `bow-sales-enablement` use for a new deal - an expansion is
a sale, and it deserves the same rigor (a real value case, not just "you're growing, buy
more").

---

<a name="churn-signals"></a>
## 5. Churn signals

**Churn is rarely a surprise if the health signals (section 2) were being watched - the
failure mode is usually that no one was watching, not that the signals were absent.**
Named signals worth an explicit playbook response, not just observation:

| Signal | What it usually means | First move |
|---|---|---|
| Usage decline, sustained | Value is not landing, or a champion left | Proactive outreach; re-run onboarding/training if a new user took over |
| Champion departure | The account's internal advocate is gone | Identify and cultivate a new champion immediately - do not wait for the QBR |
| Dunning / repeated payment failure | Could be operational (card expired) or a budget-cut signal | A human call, not just another automated retry email (billing-and-metering.md section 5) |
| Support ticket spike on the same issue | A training gap or a real product gap | Escalate to product/engineering if it's a real gap; targeted re-training if it's a usage gap |
| Downgrade request | Usage no longer justifies the tier, or budget pressure | Understand which - a usage-fit downgrade is healthy; a budget-driven one is a churn precursor |
| Non-response to QBR/outreach | Disengagement | Escalate to the executive sponsor relationship, not just the day-to-day contact |

**Run a loss review on every churn, win or lose the save.** Even a churn that could not have
been saved teaches something about onboarding, health scoring, or product fit - feed the
finding back into onboarding (section 1) or the product roadmap rather than treating each
churn as an isolated event.

---

<a name="remember"></a>
## What to remember

- Onboarding ends at a defined activation event, not at signup; capture the customer's
  outcome baseline at kickoff so later value claims are honest.
- Score health continuously from usage, support, commercial, and relationship signals
  together - usage decline is the earliest and most important leading indicator.
- QBR cadence matches the tier's economics; every QBR ties value delivered back to the
  onboarding baseline.
- Start the renewal motion at T-minus 90, not at the renewal date; feed real expansion
  signals into the same GTM rigor as a new sale.
- Named churn signals (usage decline, champion departure, dunning, ticket spikes, downgrade
  requests, disengagement) each get a specific playbook response, not passive observation;
  run a loss review on every churn.
