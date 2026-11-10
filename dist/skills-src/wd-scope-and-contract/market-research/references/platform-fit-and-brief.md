# Move 5 - Platform fit, then the opportunity brief + go/no-go

A ranked opportunity is only real if you can actually distribute and monetize it on the target marketplace.
Check platform fit, then synthesize everything into a one-page brief with a build / no-build recommendation.

## Platform-fit checklist (the marketplace is a PARAMETER - same questions, different answers)

Answer these for the chosen target; the questions are platform-neutral, the answers are platform-specific:
- **Program & eligibility** - is there a partner/marketplace program, and can we qualify (partner tier,
  certification, security review, company requirements)?
- **Distribution & reach** - how do buyers discover and install? How big/active is that marketplace's audience
  for this category?
- **Monetization & fees** - allowed pricing models, the platform's **revenue share** / listing fees, billing
  (platform-billed vs your own), and how that reshapes the price you modeled in sizing.
- **Technical fit & entitlement** - what must the buyer already own to run it (a SKU/tier/entitlement), and
  what does building on this platform require (APIs, extension framework, review/cert, data/security rules)?
- **Platform-dependency risk** - roadmap/native-overlap (the Evergreen risk again), API stability, and the
  business risk of building on someone else's platform (terms changes, deprecation, take-rate hikes).
- **Compliance & trust** - security review, data residency, privacy, and any attestation the marketplace requires.

**Instantiations (examples - not the only ones):**
- **Workday Marketplace / Built-on-Workday (BoW):** the BoW/partner program + certification; buyer must own the
  relevant Workday products (and, for agent/AI or pro-code apps, the right Extend tier - e.g. **Extend
  Professional** entitlement, see wd-extend-dev release-impact.md); revenue/terms per the Workday partner
  agreement. The GTM/listing execution then lives in **bow-sales-enablement** (this skill decides the bet;
  that skill sells it).
- **Salesforce AppExchange / ServiceNow Store / Microsoft AppSource:** each has its own partner program,
  security/technical review, revenue share, and native-overlap risk - run the same checklist.
- **Standalone SaaS (no marketplace):** distribution is yours to build (content, outbound, PLG) - higher cost,
  full control, no platform-dependency risk or take-rate.

## The opportunity brief (the deliverable)

One page per opportunity - the decision artifact:
1. **The need** - the under-served problem, who has it, severity/frequency, and the demand signals (sourced).
2. **The whitespace & wedge** - what exists, the gap, your differentiation and moat.
3. **The market** - TAM/SAM/SOM (bottom-up, sourced), ICP + JTBD, willingness-to-pay evidence.
4. **Platform fit** - target marketplace, distribution, monetization/fees, entitlement, dependency risk.
5. **The score** - the scorecard total + rank vs alternatives (assess-and-prioritize.md), with the biggest
   risks called out (especially Evergreen / platform-native).
6. **Reuse & feasibility** - head start from the reuse catalog; rough build feasibility (hand the real LOE to
   wd-estimate).
7. **Recommendation - GO / NO-GO / VALIDATE-FURTHER** - with the specific evidence still needed if
   "validate", and the proposed next step.

Keep it evidence-first: every number and claim carries a source + date; label assumptions; a blank is a
research gap, not a fact.

## Gate & handoffs

- **Gate:** a **go** decision requires the brief complete - validated demand (evidence ladder), a credible
  whitespace + wedge, a bottom-up SOM, confirmed platform fit, and the scorecard - with Evergreen/native risk
  explicitly assessed. A go on conviction without the evidence is the failure mode this skill exists to prevent.
  (Named check in wd-extend-lifecycle quality-gates.md.)
- **On GO -> hand off:** **bow-sales-enablement** (build the go-to-market kit for the chosen app),
  **wd-estimate** (build LOE + pricing), the **design skills** (build), and **wd-practice-ops** (log it as a
  productization candidate + reuse-catalog asset). Any market claim carried into marketing inherits
  bow-sales-enablement's **claims-register** governance (source + status per claim).
- **On NO-GO / VALIDATE:** record the rationale (so the same idea is not re-litigated) and the specific
  evidence that would change the answer.
