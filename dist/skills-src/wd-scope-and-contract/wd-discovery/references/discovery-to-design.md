# From Discovery to Design Doc

Discovery output has exactly one destination: the design document (authored per the **wd-design-doc** skill, which owns the 16-tab template, the yellow-highlight convention, and open-items formatting - this file only describes how discovery content flows in, never how it is formatted).

## The Discovery tab: Q&A format

Discovery lands on the design doc's Discovery tab as structured Q&A rows. For each question:

- **Question** - as actually asked, kept close to the phrasing used in-session so the client recognizes it on review.
- **Answer** - the substance of what was decided or stated.
- **Source** - who answered and when (person + session date). This matters because answers get relitigated months later; "decided by [functional lead] in the 6/18 design session" ends arguments that "we decided" cannot. When two sessions conflict, record both and mark which is authoritative (typically the later one).
- **Status** - answered vs. open.

Organize rows by the discovery dimension they came from (actors, triggers, data, volumes, security, integrations, reporting, lifecycle) so a reviewer can spot an under-covered dimension by scanning - a dimension with two rows probably wasn't asked, and that gap is easier to see here than to discover in E2E testing.

Record **decisions with their rejected alternatives**, not just the outcome. "Manual paste; OCR/file-upload considered and dropped because vendor formats are not standardized" survives a personnel change; "manual paste" alone invites someone to reopen the question in six months. Discovery sessions where an option was explored and killed deserve a row saying so, with the date it was killed.

## Unresolved answers become open items

Any Discovery-tab row with status = open gets a corresponding entry on the design doc's Open Items tab, carrying:

- The question, restated so it stands alone (a reader of the Open Items tab shouldn't need the Discovery tab for context).
- An owner (a named person, not a team) and a target date.
- What it blocks, if anything - "blocks data-model design" gets chased; ownerless, blocks-nothing items rot.

Formatting, highlighting, and status conventions for open items are the **wd-design-doc** skill's domain - follow it exactly; consistency across the program's design docs is the point. Real projects carry 10-20 open items out of discovery into design. That is healthy: an open item logged in discovery is a question you had the discipline to ask; the same question surfacing in E2E testing is an escalation.

## Volume answers flow forward

Volume numbers captured in discovery are reused at least twice downstream, so capture them once, well:

- **Workday's Volumes Questionnaire** and the **Extend Performance Testing Template** (both owned by the **wd-deployment** skill) need transactions/year, peak-period rates, and user counts. Discovery is the only phase where the client is naturally talking about these - pre-fill from the Discovery tab rather than re-asking months later.
- Record each number **with its source and basis**: "~1,752 requests in FY25 per legacy-system report" is durable; "about 2,000" is not. Estimates are acceptable but must be *flagged* as estimates so downstream documents can carry the caveat honestly.
- Capture the multipliers, not just the headline: peak-to-average ratio, and approval-chain depth (an N-step approval chain makes approval actions run ~N times request volume - often the app's highest-frequency action, and exactly what the performance template asks about).

## Retro path - discovery changes after design is already approved

The solution-options gate and this handoff checklist are designed for a forward path (discovery -> design). When circumstances require revisiting discovery or solution options after design is already approved, the process differs by context:

- **Client/custom projects:** route through the formal change-control process - CR log, SOW/estimate impact, re-sign-off by the named client approver. A design-doc update without a CR is scope risk, not just a doc edit. (Design change-control mechanics: wd-design-doc/references/change-control.md; CR-log pattern: wd-pm.)
- **BoW / internal Marketplace apps:** the process is lighter but documentation still matters - record *what changed*, *why* (new constraint, user testing finding, scope discovery), and *who agreed* in the design doc's change log and the version note. This creates a traceable rationale if the decision is questioned later, without the overhead of a full CR.

In both cases: re-run the gap analysis and quality gates against the updated design before the next delivery checkpoint. A change that touches solution options, integration surface, or data model typically needs the security and data-mapping tabs re-reviewed as well.

## Handoff checklist

Before declaring discovery done and moving to design authoring (the **wd-design-doc** skill):

1. Every discovery dimension has Discovery-tab rows (integration builds: every section of the integration questionnaire, too).
2. Every open question is an Open Items entry with a named owner and date.
3. Every decision records its rejected alternatives and decision date.
4. Volumes are captured with sources and estimate flags.
5. Vendor and security-provisioning lead times are on the project plan, not just in notes.
6. The straw-man process flow has survived at least one client correction pass - a flow the client has never marked up is a flow nobody has actually reviewed.
