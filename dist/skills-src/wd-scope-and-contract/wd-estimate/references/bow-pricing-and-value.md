# BoW / Marketplace pricing - the estimation-side slice

Single-owner pointer, mirroring `flex-credits.md`: the **BoW/Marketplace pricing doctrine and the spend-snapshot value instrument are OWNED by the `bow-sales-enablement` skill** (`references/pricing-packaging-guide.md` and `references/spend-snapshot.md`). Do NOT restate the full doctrine or the calculator's design rules here - read them there, and pull governed figures from there rather than re-keying them. This file carries only the ESTIMATION-specific slice: how a productized subscription changes what the estimator does, and how the value instrument relates to the UET.

Use this when pricing a **Marketplace/BoW product subscription** (as opposed to a bespoke client Extend build, which is an hours build-up in the UET).

## What's different for the estimator (subscription vs. bespoke LOE)

- **It's priced to value, not to cost.** A bespoke build is an hours x rate build-up in the UET; a BoW subscription is a subscription number anchored on the customer's own value case. **The UET build-up still matters - it defends the floor** (your cost-to-serve), while the value case sets the ceiling. Produce the build-up as your internal floor check even though it is not the quoted number.
- **Deployment is bundled into the subscription** - do NOT model a separately-discountable "implementation" SKU. The estimate's delivery hours become cost-to-serve behind the subscription, not a line item.
- **Hold ONE governed floor.** The governed floor is an engagement input (a low-five-figures-per-year band is typical of this motion); reconcile to one number before quoting. Divergent floors across artifacts are a defect - the full doctrine on this is in the bow owner.
- **Cost-to-serve unknowns are open items, not asserted margins.** Implementation/support/regression hours you can't yet size stay flagged as open items (wd-design-doc yellow-highlight convention), never buried in an assumed margin.
- **Charge-separately triggers feed the SOW.** Out-of-standard-scope work (customization, custom reports, training beyond standard, extended support, tenant remediation/readiness) is charged separately and becomes SOW exclusions/charge-separately language - hand these to wd-contracts (`sow-handoff.md`). The full trigger list is in the bow owner.

## The spend snapshot relative to the UET

The pre-sales **spend snapshot** (rep-facilitated value calculator, owned by `bow-sales-enablement/references/spend-snapshot.md`) **precedes and pairs with the UET**: the snapshot turns the customer's own inputs into their value number (sets willingness-to-pay); the UET sizes delivery effort (sets cost-to-serve/floor). Sequence the snapshot first when both are in play. Build the calculator itself from the bow owner's design rules (do not re-derive them here).

## ICP / opportunity scoring (qualification)

For pursuit prioritization, the same weighted-scoring shape used for account targeting works for opportunity qualification: ~7 weighted dimensions -> 100 pts -> tier -> action (e.g., platform fit, workflow fit, buyer access, pain evidence, channel leverage, pricing potential, competitive openness). Weights and pricing bands are **per-app inputs**, not constants; flag them tunable. The full model + companion scorecard lives in bow-sales-enablement (`icp-brief.md` / `target-account-scorecard.md`).

## Credentials / "About the firm"

Do not re-key firm/partner credentials into proposals. Pull them from the **canonical fact block**: `bow-sales-enablement/references/firm-fact-block.md` (revenue, client/employee counts, consultant/dev counts, partner tenure, awards, C-Sat, support model). Those figures are time-sensitive and mostly need confirmation + an as-of date before use - treat per that file's governance.

## Boundaries
- The GTM artifacts (messaging house, playbook, battlecards, decks, listing, etc.) -> **bow-sales-enablement**.
- Drafting the actual SOW/SaaS paper (scope/assumptions/exclusions/term) -> **wd-contracts**; feed it the scope-boundary + charge-separately triggers above.
- UET mechanics + LOE calibration -> this skill (`uet-guide.md`, `calibration.md`).
