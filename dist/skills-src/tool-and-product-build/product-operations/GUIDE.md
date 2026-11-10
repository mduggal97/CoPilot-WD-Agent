---
name: product-operations
description: >-
  Run a SOLD, customer-hosted product as a business - the Track-2 analogue of wd-post-go-live.
  Owns everything that starts once a customer is PAYING: SLA tiers and support/incident response,
  release and deprecation management, billing and metering against the pricing model, customer
  success (onboarding through renewal), and the operational side of compliance (SOC 2, GDPR/CCPA,
  security questionnaires). Use when the ask is "run a sold product", an SLA or support tier,
  incident/on-call/escalation, a status page, a versioning or deprecation policy,
  billing/metering/entitlements, customer onboarding / success / renewal / churn, SOC 2 or a DPA
  in practice, a security questionnaire, or "operate a SaaS product". Downstream of
  product-strategy (sets the support-model bar) and product-gtm (sets the pricing); runs on top of
  app-hosting (the infra). NOT the Workday post-go-live phase (wd-post-go-live) and NOT the
  contract paper (wd-contracts) - it operates against both but owns neither.
---

# product-operations - run a sold hosted product as a business

This skill is a thin index. It owns ONE moment: **a Track-2 hosted tool has a paying
customer, and someone has to run it like a business** - not just keep the servers up.

That is a different job from shipping the infra (app-hosting) and a different job from
deciding whether to sell it (product-strategy). It is the ongoing operating discipline: SLA
and support, release and deprecation, billing and metering, customer success, and the
operational side of compliance. It is the Track-2 twin of what `wd-post-go-live` is for a
Workday Extend delivery - same discipline, run against a different stack and a different
sales motion.

## What this skill owns

- **SLA and support** - uptime/response/resolution targets by severity, support channels
  and hours, incident severity definitions, on-call and escalation, a status page, incident
  and postmortem discipline, error budgets.
- **Release management** - versioning and deprecation policy a customer can plan against,
  the customer-visible changelog, backward compatibility, maintenance windows, staged
  rollout, and the rollback tie-in to the infra layer.
- **Billing and metering** - usage capture, plans/tiers/entitlements billed against the
  product's pricing model, invoicing patterns, overage/proration, dunning.
- **Customer success** - onboarding and activation, adoption and health scoring, QBRs,
  renewal and expansion, churn signals.
- **Compliance operations** - SOC 2 readiness, GDPR/CCPA operational duties, a
  security-questionnaire answer bank. Operational guidance only - not legal advice and not
  an audit (see the guardrail in `references/compliance-ops.md`).

## Reference map - read what you need

| You're working on | Read |
|---|---|
| SLA tiers, support channels/hours, incident severity, on-call/escalation, status page, postmortems, error budgets | [references/sla-and-support.md](references/sla-and-support.md) |
| Versioning/deprecation policy, customer-visible changelog, backward compat, maintenance windows, staged/canary rollout, rollback | [references/release-management.md](references/release-management.md) |
| Usage metering, plans/tiers/entitlements, invoicing patterns, overage/proration, dunning, margin | [references/billing-and-metering.md](references/billing-and-metering.md) |
| Onboarding/activation, adoption/health scoring, QBRs, renewal/expansion, churn signals | [references/customer-success.md](references/customer-success.md) |
| SOC 2 readiness, GDPR/CCPA operational duties, DPA-in-practice, subprocessors, DSAR, breach notification, security-questionnaire answer bank | [references/compliance-ops.md](references/compliance-ops.md) |

## Boundaries

- **app-hosting** is the infrastructure and observability this skill's product RUNS on -
  App Runner/RDS/Bedrock/Entra, deploy pipelines, migration safety, prod rollback mechanics,
  and the 4-alarm observability baseline (`references/observability.md`,
  `references/operations.md`). This skill is the CUSTOMER-facing run-as-a-business layer
  sitting above that infra - it consumes app-hosting's rollback and alarm mechanics rather
  than redefining them (see release-management.md and sla-and-support.md).
- **product-strategy** decides disposition (internal vs. customer product) and sets the
  support-model BAR as stage 4 of its productization lifecycle
  (`references/productization-lifecycle.md`). This skill is what stage 4 points to for the
  actual SLA/support/versioning content, and it is what keeps running that bar for the life
  of the product after launch. product-strategy decides the product needs an SLA; this skill
  writes and runs the SLA.
- **product-gtm** sets the pricing model and tiers (`references/pricing-and-value.md`) this
  skill bills against. Pricing/packaging strategy and the value calculator live there; the
  metering, invoicing mechanics, and entitlement enforcement live here.
- **wd-post-go-live** is the Workday-delivery analogue - hypercare, managed services,
  release regression, and account growth for a Workday Extend app. Same discipline (SLA
  tiers, incident severity, QBR/renewal, actuals write-back), different track and different
  platform. Read it for pattern parallels; do not apply its Workday-specific mechanics
  (WQL/RaaS monitoring, R1/R2 regression) to a Track-2 product.
- **wd-contracts** drafts the paper - the SaaS agreement, DPA, and SLA-as-contract language.
  This skill defines the operational SLA/support/compliance CONTENT that paper encodes; it
  never drafts or finalizes legal terms itself (see the guardrail in compliance-ops.md).
- **app-agentic** owns the SpendGuard ledger and per-run cost metering for an agentic
  product. This skill's billing-and-metering.md consumes that ledger as a metering SOURCE
  for usage-based billing; it does not re-implement spend tracking.

## Lifecycle neighbors

- **Fed by:** product-strategy (a CUSTOMER PRODUCT disposition, stage-4 support-model
  acceptance) and product-gtm (the priced/packaged tiers). app-hosting hands off the running
  infra this skill operates against.
- **Feeds:** the renewal/expansion motion back into product-gtm and bow-sales-enablement
  (an account-growth opportunity), and wd-practice-ops (operational actuals and lessons feed
  the reuse-catalog maturity record).
- **Runs at:** from the moment the first customer is live and paying, continuously for the
  life of the product - it does not end like a project closeout; it is the steady state.

**Track-2 scope note (2026-09-10):** this skill assumes the customer-sold hosted-product
path is being built out (per the `practice-lifecycle` Track-2 scope note and the
product-strategy disposition-gate scope gate). Where a referenced capability - public status
page hosting, multi-tenant billing integration, a real SOC 2 audit - does not exist yet in
the practice's toolset, the references say so plainly rather than assuming it is already
built.

**Quality-gate rule (suite-wide):** every artifact this skill produces (SLA document,
incident postmortem, changelog, billing policy, customer-success playbook, compliance
answer bank) has a named check in wd-extend-lifecycle `references/quality-gates.md` (the
writing-quality gate, and the external-claims/provenance gates where a compliance or
security-questionnaire answer makes a factual assertion) - run it before presenting work as
final and report the result with the deliverable.
