---
name: wd-estimate
description: Estimate and quote Workday Extend / Integration work - review a customer RFP or opportunity, size level of effort (LOE) by role and phase, build a proposed timeline, and fill the UET (Unified Engagement Tool) workbook. Use this skill whenever the task involves an RFP, RFI, proposal, pursuit, quote, pricing, LOE, level of effort, scoping an opportunity, staffing plan, estimate, "how many hours", or the UET - even informal "what would this roughly take?" questions.
---

# Estimating & Quoting Extend/Integration Work

An estimate is a model of the delivery: scope -> work items -> hours by role over time -> price. Keep those layers explicit so when scope changes, the ripple is mechanical instead of a re-guess.

## The workflow

1. **Qualify the opportunity** (10 minutes, saves weeks): does the client own Extend / Innovation Services? What's their tenant landscape? Is there an incumbent process/tool? Who's the economic buyer and what's their deadline pressure? See the qualification checklist in [references/sow-handoff.md](references/sow-handoff.md).
2. **Decompose the ask**: from the RFP (or discovery notes), enumerate apps/integrations, and per app the complexity drivers: # business objects, # pages (worker/approver/admin variants count separately), # BPs and approval complexity, # orchestrations and their triggers, # external integrations, Prism involvement, data conversion, security complexity, number of stakeholder groups (drives design cycles). RFPs under-specify; every assumption you make goes into the assumptions list (they become the SOW's protective wall).
3. **Size against calibration**: map each app to an archetype in [references/calibration.md](references/calibration.md) and adjust by the drivers. Estimate per phase x role, not one blob - phase-level numbers expose unrealistic compression when the timeline negotiates.
4. **Build the staffing model**: roles across weeks (the shape the UET consumes). Typical Extend pod: Developer Lead (part-time across phases), Developer(s) (heavy in PoC->Build), Functional Consultant (heavy in Discovery/Design/Testing), PM (steady fraction), SME/MD (light oversight). Respect dependencies: design sign-off gates build; Workday gating docs (volumes/perf) need lead time before go-live (wd-deployment).
5. **Fill the UET**: follow [references/uet-guide.md](references/uet-guide.md) - visible input sheets only, in order: Start -> (Custom Bill Rates Table if custom rates) -> ResourceEffort -> PricingDetermination -> Review. Where information is missing, apply the yellow-highlight convention (wd-design-doc owns it) in any working Excel you produce; the UET itself gets conservative entries + a notes list.
6. **Sanity-check the output**: Review tab warnings resolved (e.g. "Missing Project Role Assignments"), contribution margin vs target, MD hours reasonable, timeline vs client deadline. Present LOE + timeline + assumptions as a package - never a bare number.

## Sizing an enhancement to a live app

Enhancements are not "a small greenfield." Build the LOE as:
**audit/discovery time** (the current-state sweep is **wd-extend-dev** references/app-review-audit.md - its findings already carry S/M/L effort tags, and L items route back here as change orders) **+ build + regression overhead + doc/KT refresh**. Regression and doc-refresh overhead do NOT shrink proportionally with change size - a one-field change still runs the critical-path regression set and refreshes the guides, so small changes carry a floor. Phase distribution differs from the greenfield split in [references/calibration.md](references/calibration.md): Design and PoC shrink, Testing's share grows.

Size against calibration.md's **"Marketplace app enhancement"** archetype row (its real examples and the one recorded ~40h anchor live THERE - calibration.md owns all anchor data; do not invent hours for the unbackfilled examples). Paper: change order under the existing SOW by default; a new/amended SOW when the scope is effectively a new module or app - the drafting and threshold language is **wd-contracts**.

## Timeline proposal

Derive from the phase LOE and pod size: Discovery (1-3 wks) -> Design (2-6 wks, stakeholder count drives it) -> PoC (parallel with design back half) -> Build -> Unit Test -> UAT/E2E support -> Perf/Volumes docs + prod approval (submit EARLY - Workday review lead time) -> Deploy/Cutover -> Hypercare (2-4 wks). Show it per workstream with the gates marked. wd-pm's plan skeleton mirrors these phases - reuse it for the delivery plan after the win.

## Writing the proposal or pitch

The estimate prices the work; the proposal sells it. Read [references/proposal-content.md](references/proposal-content.md) whenever producing a proposal, RFP response, or internal pitch - it covers the methodology/tools depth buyers expect beyond the executive summary, the AI-acceleration framing rules (internal pitches advocate co-building with Claude Code; customer proposals sell the expedited timeline, never reduced hours), the visuals requirement (mockups, concept graphics, consistent professional imagery - proposals without visuals don't sell), the competitive-positioning library for contested deals ("why Extend + the firm", honest Extend-vs-ISV framing), and the internal Marketplace-product pitch variant.

## Pricing a Marketplace / BoW product (subscription)

Pricing a **productized Marketplace/Built-on-Workday app** is a different motion from bespoke-project LOE - it's a subscription priced to value, not an hours build-up. Read [references/bow-pricing-and-value.md](references/bow-pricing-and-value.md): the pricing doctrine (bundle deployment into the subscription, price-to-value, hold ONE governed floor, never anchor to the Marketplace list price, charge-separately triggers, tier-by-scope), the pre-sales **value instrument** ("spend snapshot" - customer's own inputs -> their value number, which pairs with and precedes the UET), and the ICP opportunity-scoring model. The full GTM kit that owns these artifacts is the **bow-sales-enablement** skill; pull firm credentials from its canonical `firm-fact-block.md` rather than re-keying them into proposals.

## Flex Credits / ongoing cost in the estimate

As of May 2026, every Extend app and non-Workday-built integration carries measurable ongoing API costs to the customer. **Include an annual run-cost estimate alongside the build LOE.** The commercial model itself - entitlement tiers, credit pricing, the Extend multiplier, the agent Rate Card, and what counts - lives in this skill's own [references/flex-credits.md](references/flex-credits.md); use those canonical numbers rather than restating them here. Estimate-specific method:

- **Estimate annual API call volume** for the solution (orchestration calls, BO REST reads/writes, WQL queries, RaaS requests). Each counts toward the customer's API entitlement.
- **Check the volume against the customer's entitlement tier** (see references/flex-credits.md). If the solution's API volume risks exceeding the entitlement, price the Flex Credit overage.
- **For agent-enabled builds**, include the per-agent Rate Card cost (see references/flex-credits.md) and estimate annual action volume based on user population and frequency.
- **Compare build options by total cost of ownership** (build LOE + annual run cost), not just implementation hours. A Core Connector (free at the API layer) vs. a custom Studio integration (metered) is a real cost difference the customer will see.
- **Surface this in the proposal** as a "Flex Credit Impact" section or appendix -- customers increasingly need this to budget for ongoing AI/platform costs alongside implementation fees.

## After the estimate

- Feed the SOW: scope language, assumptions, exclusions, client responsibilities - [references/sow-handoff.md](references/sow-handoff.md); drafting the actual SOW/SaaS agreement documents is the wd-contracts skill. The estimate's assumptions ARE the change-order baseline (wd-design-doc change control picks this up post-sign-off).
- Close the loop: at project closeout, wd-post-go-live records actuals vs estimate and updates the calibration table. Estimates only get honest through this loop - protect it.
- **Every pursuit outcome gets a 20-minute debrief - won AND lost.** Run [references/win-loss.md](references/win-loss.md): the 10-question debrief, finding routing (pricing -> calibration, patterns -> proposal-content, competitor facts -> bow battlecards), and the won/lost log whose hit-rate-by-archetype feeds the next qualification.

Use the xlsx skill for Excel mechanics; this skill owns estimation content and the UET procedure.

## Lifecycle neighbors

next = wd-contracts (paper the win - turn the quote's scope/assumptions/pricing into the SOW), then wd-discovery (deeper intake after signature); receives actuals back from wd-post-go-live.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
