# Billing and metering - turning pricing into an invoice

Reference for `product-operations`. `product-gtm/references/pricing-and-value.md` decides
WHAT to charge (the model, the tiers, the governed floor). This file is what makes that
decision real every month: capturing usage, enforcing entitlements, generating an invoice,
and handling the messy edges - overage, proration, and a card that fails. Self-contained:
read it without having read anything else in the suite.

## Table of contents

- [Usage capture and metering](#usage-capture)
- [Plans, tiers, and entitlements](#entitlements)
- [Invoicing approaches](#invoicing)
- [Overage and proration](#overage-proration)
- [Dunning](#dunning)
- [Margin - cross-linking run cost](#margin)
- [What to remember](#remember)

---

<a name="usage-capture"></a>
## 1. Usage capture and metering

**Meter as close to the billable event as possible, and record it durably before you ever
try to bill against it.** A metering pipeline that recomputes usage from application logs
after the fact is fragile - logs rotate, get filtered, or get sampled. Emit a metering event
(or an increment to a running counter) at the moment the billable action happens, written to
a durable store (the product's own Postgres, per `app-architecture`'s schema-per-module
data isolation) as the source of truth, with the billing PROVIDER as a secondary system fed
FROM that record, not the other way around.

**What counts as a metering event depends on the pricing model** (see
`product-gtm/references/pricing-and-value.md` section 2 for the model catalog):

| Model | Meter |
|---|---|
| Per-seat | Active/named users at billing-period close (a seat-count snapshot, not a live tally) |
| Usage/consumption | API calls, records processed, jobs run, GB stored, agent tokens/runs |
| Tiered/flat | No per-event meter needed; entitlement checks only (section 2) |

**For an agentic product, the SpendGuard ledger is already the metering source.** If the
product runs on `app-agentic`'s budgeted tool-use loop, SpendGuard already records
micro-dollars per call to a ledger for spend-cap enforcement - do not build a second,
parallel usage-tracking pipeline. Read that ledger as the metering input for a token/run-based
usage plan, and reconcile it against the billing provider's own usage records periodically
(the ledger is the source of truth; the biller should agree with it, not silently diverge).

**Idempotency matters more in metering than almost anywhere else.** A retried request that
double-emits a usage event double-bills the customer. Key every metering event with an
idempotency key (the originating request's correlation id, per
`app-hosting/references/observability.md` section 2, is a natural choice) so a retry is a
no-op against an already-recorded event.

---

<a name="entitlements"></a>
## 2. Plans, tiers, and entitlements

**An entitlement is the enforceable version of a pricing tier's promise.** Pricing-and-value
decides "Pro tier includes 10,000 API calls/month and 3 seats"; entitlements are the runtime
checks that actually stop the 10,001st call or the 4th seat, or that meter it as overage
(section 4) instead of silently allowing it.

- **Check entitlements at the point of action**, not just at signup - a customer can
  legitimately grow past their tier mid-period, and the system needs to know in real time
  whether that is an overage-billable event or a hard block.
- **Decide per capability whether the limit is a hard stop or a billable overage.** A seat
  limit is often a hard stop (cannot add a 4th user without upgrading); a usage limit is
  often a soft overage (keep working, get billed for the excess) - state this per capability
  in the plan definition, because customers experience these very differently and an
  unexpected hard stop mid-workflow is a support-ticket generator.
- **Surface entitlement state to the customer**, not just to your own billing system - a
  usage dashboard showing "7,200 / 10,000 calls this period" lets a customer self-manage
  before hitting a wall, and reduces both support load and surprise-overage disputes.

**Entitlements should be data, not code.** Hard-coding "if tier == 'pro': limit = 10000"
throughout the codebase makes every pricing change a deploy. Model plans/entitlements as
configuration the billing/entitlement service reads, so product-gtm can adjust a tier
boundary without an engineering release.

---

<a name="invoicing"></a>
## 3. Invoicing approaches

**Describe the pattern; do not hand-roll payment processing.** PCI-scope, tax calculation,
and dunning logic are exactly the kind of undifferentiated heavy lifting a billing platform
exists to absorb - building it in-house is rarely the right call for a practice-built
product.

- **Stripe Billing** is the most commonly reached-for pattern for a SaaS product: it models
  Products, Prices, Subscriptions, and Invoices, and has first-class support for both
  flat/tiered subscription billing and metered/usage-based billing (report usage against a
  metered price, and Stripe computes the invoice)
  (https://docs.stripe.com/billing, https://docs.stripe.com/billing/subscriptions/overview,
  https://docs.stripe.com/billing/subscriptions/usage-based). Its APIs and pricing details
  change over time - treat any specific field/endpoint name here as a starting point to
  verify against current docs, not a frozen spec.
- **Other reputable options** exist (e.g., a payment processor's own billing add-on, or a
  dedicated subscription-billing platform) - the pattern below applies regardless of
  provider; the specific API surface does not.
- **The pattern, provider-agnostic:**
  1. Create a customer record in the billing provider at signup, linked to the product's own
     customer/tenant id (never let the billing provider's id be the only reference - own
     your own customer identity).
  2. Subscribe the customer to a Price representing their tier.
  3. For usage-based components, report usage records to the provider on a schedule (or in
     near-real-time) sourced from the durable metering store (section 1) - the provider
     bills from what you report, so accuracy of the report IS the accuracy of the bill.
  4. Let the provider generate and send the invoice; do not build a parallel invoice
     renderer unless the provider's invoicing genuinely cannot meet a specific need.
  5. Receive webhooks for invoice paid / payment failed / subscription updated and react
     (unlock/lock features, trigger dunning - section 5).

**Never handle raw card numbers.** Use the billing provider's hosted checkout or
client-side tokenization (e.g., Stripe Elements/Checkout) so card data never touches the
product's own servers - this is both a PCI-DSS scope reduction and a hard rule regardless of
which provider is chosen.

---

<a name="overage-proration"></a>
## 4. Overage and proration

**Overage** - usage beyond a plan's included allotment, billed at a stated per-unit rate.
State the overage rate up front in the pricing (product-gtm owns the rate); this file's
concern is the mechanics: meter it the same way as included usage (section 1), and surface
it to the customer proactively (a usage-alert threshold, e.g. "you are at 90 percent of your
included calls") rather than letting the invoice be the first they hear of it - a surprise
overage bill is one of the most common sources of billing disputes and churn risk (see
`customer-success.md` for churn signals).

**Proration** - adjusting a charge for a partial billing period, typically triggered by a
mid-cycle plan change (upgrade/downgrade) or a mid-cycle cancellation.

- **Upgrade mid-cycle** - typically charge the prorated difference immediately so the
  customer gets the new tier's capability right away without waiting for the next cycle.
- **Downgrade mid-cycle** - typically apply at the NEXT billing cycle rather than refunding
  mid-cycle, to avoid a partial-period refund workflow; state this policy clearly so it is
  not a support surprise.
- **Cancellation mid-cycle** - state whether the customer retains access through the paid
  period's end (common) or loses access immediately (less common, usually reserved for a
  for-cause termination) - this is a policy decision that belongs in the contract paper
  (wd-contracts) as much as here; keep the two consistent.

Most billing platforms compute proration automatically once a subscription's price/quantity
changes - verify the provider's specific proration behavior before assuming it matches the
policy stated to customers, rather than assuming a default matches your intent.

---

<a name="dunning"></a>
## 5. Dunning

**Dunning is the automated process of chasing a failed payment before it becomes a lost
customer or an involuntary churn event.** A failed card is usually NOT a customer trying to
avoid paying - it is often an expired card or a bank decline - so the default posture is
recovery, not immediate cutoff.

A typical dunning sequence:

1. **Payment fails** - retry automatically on a schedule (many billing platforms retry a
   failed charge several times over 1-2 weeks using smart retry timing) rather than
   retrying immediately and repeatedly, which just repeats the same decline.
2. **Notify the customer** at each failed attempt with a clear, actionable message (update
   your card) and a self-service link - do not make updating payment info require a support
   ticket.
3. **Grace period** - keep the account active (or degrade gracefully rather than a hard cutoff)
   for a stated grace period while retries continue, sized to the product's tier and
   contract terms.
4. **Suspend, then cancel** - if retries and the grace period are exhausted, suspend access,
   and after a further stated period, cancel the subscription. State both thresholds clearly
   in the customer-facing terms so this is never a surprise.

**Tie dunning outcomes into customer success.** A customer entering dunning is itself a
health/churn signal (`customer-success.md`) worth a proactive outreach, not just an
automated email chain - a real conversation often recovers an account an automated retry
sequence would eventually lose.

---

<a name="margin"></a>
## 6. Margin - cross-linking run cost

**Billing without knowing run cost is bookkeeping, not margin management.** Pull the
monthly run-cost worksheet from `app-hosting/references/operations.md` section 4/6 (App
Runner compute + shared RDS share + Bedrock/model spend) and compare it against what a given
customer or tier actually bills, at least at the tier level:

- **A usage-priced tier should track run cost closely** - if a heavy customer's Bedrock/
  compute spend is growing faster than their bill, the pricing model or the tier boundary
  needs revisiting (feed this back to `product-gtm/references/pricing-and-value.md` section
  5, which names this exact risk for a flat price over usage-driven cost).
- **A flat or per-seat tier can hide a margin problem** for a long time because the bill does
  not move with cost - periodically sample actual run cost per customer on flat tiers, not
  just on usage tiers, so a margin inversion is caught before it compounds across the base.
- **The SpendGuard hard cap (app-agentic) puts a ceiling on the worst case per customer** for
  an agentic product - use that ceiling as a sanity check that no single customer can run
  the product cost so far past their bill that it moves the whole tier's margin.

---

<a name="remember"></a>
## What to remember

- Meter durably and close to the billable event, keyed with an idempotency key; for an
  agentic product, the SpendGuard ledger already IS the metering source - do not duplicate it.
- Entitlements are the runtime-enforced version of a pricing tier's promise; model them as
  data so a tier change is a config edit, not a deploy, and decide per capability whether a
  limit is a hard stop or a billable overage.
- Use a reputable billing platform (Stripe Billing is the common pattern) rather than
  hand-rolling payment processing; never let raw card data touch the product's own servers.
- Communicate overage proactively via a usage dashboard/alert, not just via the invoice;
  state proration policy for upgrade/downgrade/cancellation clearly and keep it consistent
  with the contract paper.
- Dunning defaults to recovery (retry + notify + grace period) before suspension/
  cancellation, and a customer entering dunning is a churn signal worth a human outreach.
- Reconcile billed revenue against actual run cost from app-hosting's cost worksheet
  regularly, on flat/per-seat tiers as well as usage tiers - a flat price can hide a margin
  problem that a usage price would surface immediately.
