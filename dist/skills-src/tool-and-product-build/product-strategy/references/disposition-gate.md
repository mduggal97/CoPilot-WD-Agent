# Disposition gate - internal accelerator or customer product?

Reference for `product-strategy`. This is a **gate you RUN**, not prose to read. Given a
build-worthy idea (market-research says GO) or an existing internal tool (from the reuse catalog),
this gate outputs one disposition - INTERNAL ACCELERATOR or CUSTOMER PRODUCT - and the downstream
POSTURE that disposition sets for the build, host, and support work.

Run it BEFORE the build hardens. The two dispositions diverge on nearly every non-functional axis,
and those axes are cheap to design in and costly to retrofit. Deciding once, deliberately, means the
build is held to the right bar the first time.

## Table of contents

- [How to run this gate](#how-to-run)
- [The seven criteria](#criteria)
- [Decision rule - reading the answers](#decision-rule)
- [The two postures - what each disposition sets downstream](#postures)
- [The middle case - "internal now, product maybe"](#middle-case)
- [Output - the disposition record](#output)

---

<a name="how-to-run"></a>
## How to run this gate

1. **Answer all seven criteria** below for the tool in question - one line each, evidence not hunch.
2. **Apply the decision rule** - the criteria point to a disposition; a mixed answer resolves via
   the escalation rule (any single "sold externally" or "external customer is the user" answer
   forces the CUSTOMER PRODUCT posture - the higher bar wins).
3. **Read off the posture** for the disposition - that is the bar the app-* build, host, and support
   work is held to.
4. **Record the disposition** (see the output block) and hand off - internal stays in the reuse
   catalog with a light posture; a product routes into the productization lifecycle.

**Right-size it.** An obvious internal script needs a one-line disposition, not a full gate. Run the
full seven when the answer is genuinely in question or when someone is arguing "we could sell this."

---

<a name="criteria"></a>
## The seven criteria

Answer each for the tool. The right column names which posture the answer pulls toward.

| # | Criterion - the question | INTERNAL pulls when... | CUSTOMER PRODUCT pulls when... |
|---|---|---|---|
| 1 | **Who is the user?** Who sits in front of it day to day? | The practice / delivery team itself | An external customer / buyer outside the firm |
| 2 | **Is it sold or free?** Does money change hands for access to it? | Free - a cost the practice absorbs to go faster | Sold - a customer pays a price / subscription |
| 3 | **Support / SLA expectation.** What happens when it breaks at 2am? | Best-effort; the team that runs it fixes it when it can | A promised SLA, a support channel, an on-call - a customer is waiting |
| 4 | **Security / compliance / data-residency bar.** What data does it touch and whose rules apply? | Internal data, firm's own governance, no external audit | Customer data, external audit / attestation, data-residency + tenancy isolation |
| 5 | **IP / licensing.** Who owns it and under what terms is it used? | Firm-internal use; provenance scrubbed but no license grant | A licensed / subscribed grant to a customer; contract paper; IP cleanly firm-owned + sellable |
| 6 | **Who runs it long-term?** Who owns the run cost + blast radius after launch? | The building team (you build it, you run it, quietly) | A named product owner + operating model funded to run it for customers |
| 7 | **TCO tolerance.** How much ongoing run + maintain cost is acceptable? | Low - it must pay for itself in team time saved; kill it if it does not | Higher - run cost is a cost of goods; it is justified by revenue, not just time saved |

**Note on criterion 4 and 6 - these are the retrofit-expensive ones.** Data-residency / tenancy
isolation and a funded operating model are the two axes that are painful to bolt on after the fact.
If either points to CUSTOMER PRODUCT, treat the disposition as a product early even if the others are
mixed - retrofitting isolation onto a single-tenant internal tool is often a rebuild.

---

<a name="decision-rule"></a>
## Decision rule - reading the answers

- **All / mostly INTERNAL** -> **INTERNAL ACCELERATOR.** Take the light posture. Stay in the reuse
  catalog. Do not build to a product bar you will never need - that is gold-plating.
- **All / mostly CUSTOMER PRODUCT** -> **CUSTOMER PRODUCT.** Take the full posture. Route into the
  productization lifecycle (productization-lifecycle.md).
- **Mixed - the higher bar wins.** Any single answer of "an external customer is the user" (crit 1)
  OR "it is sold" (crit 2) OR "customer data / external audit" (crit 4) forces the CUSTOMER PRODUCT
  posture. You cannot sell a thing on an internal support / security bar. The higher bar wins because
  the cost of under-building a product (a breach, a broken SLA, an unshippable audit) dwarfs the cost
  of over-building an internal tool.
- **Genuinely undecided** -> default INTERNAL now, and record it as a productization CANDIDATE (see
  the middle case). Do NOT build to the product bar speculatively - validate demand first
  (market-research), then productize deliberately. Building product-grade on spec is the most common
  waste this gate exists to prevent.

---

<a name="postures"></a>
## The two postures - what each disposition sets downstream

The disposition is not a label; it is a BAR. Here is what each posture sets for the downstream skills.

| Downstream axis | INTERNAL ACCELERATOR posture | CUSTOMER PRODUCT posture |
|---|---|---|
| **GTM** | None - skips GTM entirely | Full GTM - product-gtm (non-Workday channels) or bow-sales-enablement (Workday Marketplace / BoW): listing, messaging, pricing, battlecards |
| **Governance / claims** | Light - reuse-catalog genericize + provenance scrub only | Full - claims register, sourced marketing claims (bow-sales-enablement governance) |
| **Support model / SLA** | Best-effort; owning team fixes when it can | Named support channel, promised SLA, on-call / escalation path |
| **Security / compliance** | Firm's internal governance; no external attestation | Full conformance (app-harness conformance-checklist.md), external audit / attestation, tenancy isolation, data-residency |
| **Hosting posture (app-hosting)** | Lighter - private ingress behind VPN is enough; single-tenant fine | Full - multi-tenant isolation, prod-grade observability + alarms, TCO sizing, PITR / rollback discipline |
| **Build polish (app-architecture / app-harness)** | Functional; conformance checklist is advisory | Product-grade; conformance checklist is a hard ship gate |
| **IP / licensing** | Provenance scrubbed; internal-use only | Clean firm-owned + sellable IP; contract paper (wd-contracts) |
| **TCO treatment (app-hosting operations)** | Must pay for itself in team time; low tolerance | Cost of goods, justified by revenue; sized and budgeted |
| **Ownership / operating model** | You build it, you run it - the building team, quietly | Funded product owner + operating model for the life of the product |

**The one-line why:** an internal accelerator gets a LIGHTER support + hosting + governance posture
and skips GTM + external conformance, because its only "customer" is the team that runs it. A customer
product gets the FULL GTM + conformance + TCO + support treatment, because an outside buyer is
depending on it and paying for it.

---

<a name="middle-case"></a>
## The middle case - "internal now, product maybe"

Many strong products start as internal accelerators. When the gate lands INTERNAL but the tool looks
like it COULD sell:

- **Keep the internal posture for now** - do not over-build to a product bar on speculation.
- **Flag it as a productization candidate** in the reuse catalog (wd-practice-ops
  reuse-and-asset-catalog.md - a frequently-reused, well-proven asset is exactly this candidate).
- **When someone wants to productize it, go validate demand first** (market-research) - a candidate
  is not a decision. Only a demand-validated candidate enters the productization lifecycle.
- **Then re-run this gate** with the product answers and take the full posture deliberately.

This keeps the cheap path cheap while leaving the door open - you graduate to the product bar when
there is evidence, not when someone had a hopeful afternoon.

---

<a name="output"></a>
## Output - the disposition record

Record the decision so the downstream skills inherit the right bar. Keep it short:

```
DISPOSITION: Internal accelerator | Customer product
Tool / asset: <name + one-line what-it-does>
Criteria answers: 1 user=... 2 sold=... 3 SLA=... 4 security=... 5 IP=... 6 owner=... 7 TCO=...
Deciding factor: <the criterion/criteria that set it; note if higher-bar-wins triggered>
Long-term owner: <named team / product owner - the "you run it" answer>
Downstream posture set: <GTM yes/no, conformance hard/advisory, hosting light/full, support model>
Candidate flag (if internal): productization candidate? yes/no -> reuse catalog
Route: internal -> reuse catalog (light posture) | product -> productization-lifecycle.md
```

Hand the record to whoever picks up the build - it tells app-architecture / app-hosting which bar
to build to, and it tells wd-practice-ops how to record the asset's maturity.
