# Solution Options Assessment - Decide WHAT to Build Before Designing It

The options assessment sits at the **pursuit -> design boundary**: after discovery has surfaced the problem, before wd-design-doc starts specifying an Extend app. Its job is to force the "is an Extend app even the right answer?" question while it is still cheap - an Extend build chosen by default, when tenant config or a delivered report would have done, is the most expensive kind of scope. The deliverable is one matrix + a one-page recommendation with a **named client approver**.

## When it's required

- **Required** for any net-new app, and for any build above the program's size threshold (set one per program - e.g., anything estimated over ~100 build hours; (!) confirm the threshold with the program lead).
- **Skippable** for like-for-like enhancements to a live app (Playbook C work that changes behavior inside an approach already chosen). Record the skip as a one-line decision, not silence.

## The options matrix

Rows = candidate approaches. Score every row, even the ones that feel obviously wrong - the rejected rows are what stop the question being relitigated later.

| Candidate approach | Consider when |
|---|---|
| **Extend app** (PMD UI + BOs + orchestrations) | Custom UI, custom data, custom workflow - the full build |
| **Studio / traditional integration** (EIB, Core Connector, DT) | The need is data movement, not a user experience |
| **Prism** (datasets + delivered reporting) | The need is blended/high-volume analytics, not transactions |
| **Tenant configuration** (BP config, condition rules, custom validations) | Workday's delivered process almost fits - config beats code |
| **Calculated fields + delivered custom report** | The need is a derived view of existing data |
| **Buy from Marketplace** | A shipped BoW app already covers most of it - subscribe, don't rebuild |
| **Don't build - wait for the Workday roadmap** | Workday has announced (or is likely to deliver) the capability natively |
| **Workday agent (native or custom)** | The interaction is conversational, the user's intent is variable, or a GA agent already covers the domain (25+ agents GA/coming through 2027: SSA, Recruiting, Payroll, Planning, BP Optimize, Case, Job Architecture, Financial Audit, etc.) |
| **Data Cloud (LDQ / Data Lake)** | The need is real-time or materialized analytics over Workday data without ETL; GA 26R2 (Oct 2026) - include as a forward-looking option with a Prism fallback |

Columns = the evaluation dimensions, scored per row:

- **Functional fit** - % of the requirement each approach actually covers, and what falls off.
- **Platform limits hit** - which known constraints bite (25 s page-sync cap, BO REST limits, SOAP-only FDM creation, etc.); pull the specifics from **wd-extend-dev**'s limits references (`references/orchestration.md`, `references/model.md`) rather than restating them.
- **Licensing / SKU cost** - does the approach require a SKU the client doesn't own (Extend, Prism, Orchestrate)? A technically-perfect answer on an unowned SKU is a commercial question, not a technical one.
- **Build + run LOE** - sized via **wd-estimate**'s archetypes (rough S/M/L is fine at this stage); include run cost (support, release regression), not just build.
- **Evergreen risk** - will Workday deliver this natively, stranding the custom build? Check **wd-extend-dev** `references/release-impact.md` for roadmap exposure; a 2-year build against a 1-year roadmap item scores itself.
- **Ongoing API / Flex Credit cost** - non-Workday-built integrations and Extend apps count toward the customer's annual API entitlement; overages consume Flex Credits, Workday-built Core Connectors are free, and native agents meter at their Rate Card rate (numbers in **wd-estimate** `references/flex-credits.md`). A build that's cheaper to implement but expensive to run may lose to one with higher build cost but zero API overhead. Include estimated annual run cost, not just build LOE.

## Retro-validation mode - when design is already approved and the assessment was never produced

A common real-world state (hit live 2026-08): a year of discovery, eleven design sessions, a client-approved design workbook - and no options-matrix artifact anywhere. The build-path decision genuinely WAS made and is well evidenced in the meeting record; it was never assembled into the required shape with a named approver. The miss surfaces at the pre-build architecture review (which checks the decision is on file) - the most expensive possible moment to discover a paperwork gap. Neither Playbook C (enhancing a live app) nor the lifecycle Change path covers this greenfield-skipped-a-gate state, so:

- **Do NOT reopen design.** The gate's purpose (force the build-vs-alternatives question while cheap) can no longer be served pre-design; reframing, not relitigating, is the goal.
- **Reconstruct the matrix from the existing record** - transcripts, tracker decisions, the design doc's own rationale rows. Mark each row **verdicted-from-record** (cite where) versus **still-unexamined**.
- **Expect the unexamined rows to be "Buy from Marketplace" and "Wait for the roadmap"** - a team deep in design has usually reasoned about the build alternatives but never about NOT building. Examine those two for real.
- **Reframe the artifact as an architecture-review INPUT**, not a discovery deliverable - it closes the review finding and gives the rejected-options rows the design doc needs, with the named approver signing the reconstruction.
- **The reconstruction does not gate a prototype.** PoC work can proceed in parallel; the artifact must exist before BUILD proper.

This is a CARRIED gate in lifecycle terms - see wd-extend-lifecycle `references/quality-gates.md` (carried-exception state): record what's missing, who accepted carrying it, and that it closes at the architecture review.

## The recommendation page

One page, four parts:

1. **Recommended approach** and the two-sentence why.
2. **Rejected options with rationale** - one line each, dated. These rows carry forward into the design doc's Discovery-tab decision rows (per `discovery-to-design.md` - decisions record their rejected alternatives), because the rejected option is the first thing relitigated at UAT ("why didn't we just use a report?").
3. **Named client approver + date** - a person, not a committee. An options assessment nobody signed is an opinion.
4. **Conditions that reopen the decision** - e.g., "revisit if volumes exceed 10x estimate" or "revisit if Workday ships X."

## Where the output feeds

- **wd-estimate** - the chosen approach picks the LOE archetype; the matrix's LOE column is the estimate's starting point.
- **wd-design-doc** - rejected options + rationale land on the Discovery tab; the chosen approach is the design's opening assumption.
- **wd-extend-dev** `references/architecture-review.md` - the pre-build architecture review checks that this decision is on file; a build with no options assessment is a review finding.
