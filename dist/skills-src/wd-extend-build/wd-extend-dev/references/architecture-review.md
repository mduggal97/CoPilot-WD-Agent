# Architecture Review - the Internal Pre-Build Gate

An internal review **by the building organization** (the delivery firm on firm-led builds; the client's own team when they build) of the technical approach **before build starts** - distinct from client design sign-off. The client signs off on *what* the app does; this review checks *how* it will be built, by someone with the standing to say "that write path won't survive production." Its whole value is catching the landmines the build validator never sees (sync-cap breaches, PUT ripple, unsized limits) while they still cost a diagram change instead of a rebuild.

## Ground rules

- **Reviewer != designer.** The reviewer is an engagement architect or dev lead who did NOT author the technical design - self-review rubber-stamps the exact assumptions that need challenging.
- **Timing:** after design sign-off, before build kickoff - or before a PoC is promoted to the development base (SKILL.md section Proof of Concept: untagged PoC shortcuts become production bugs; this review is where they get caught).
- **Scope:** one sitting, checklist-driven, 60-90 minutes for a typical app. Findings are either fixed before build or logged as design open items (wd-design-doc conventions) - never verbally waived.

## Reviewer checklist

- [ ] **Designed from the full toolbox, not a reflex pattern.** Challenge whether a more efficient or more capable option fits the problem better than the familiar shape chosen - a native widget over a hand-rolled workaround, a Graph combined mutation over N calls, an AI Gateway call, Prism for volume, a card/agent instead of custom UI. The design doesn't have to use the newest thing; it has to have *considered* the options and be able to say why the chosen shape wins (the ADR-lite "alternatives rejected" line). See [references/solutioning.md](solutioning.md). Reflexive copy-the-last-app with no alternatives weighed is a finding.
- [ ] **Every write path named, with API + auth context.** Each write states its surface (SOAP op / BO REST / businessProcess endpoint / orchestration) and whether it runs as user-context or ISU - this must match the design doc's Data & Webservice Mapping tab (wd-design-doc), where every write already names ISU vs user context. An unnamed write path is the finding, not a detail.
- [ ] **Every orchestration classified sync vs async against the 25 s page-sync cap** ([references/orchestration.md](orchestration.md)). Any large read or multi-record write designed as page-sync is a redesign now, not a perf-test surprise later.
- [ ] **BO schema reviewed for field-addition landmines** ([references/model.md](model.md) section adding a field): null guards for pre-existing records, backfill plan (or an explicit "old rows excluded" open item), and the PUT full-replace ripple - every existing PUT payload must carry any new field forward. Prefer PATCH for status back-writes.
- [ ] **Limits headroom stated.** BO REST `limit` <= 100 / pagination or WQL for larger sets, expected row counts vs the limits in [references/orchestration.md](orchestration.md) and [references/efficiency.md](efficiency.md), and what happens at 2-3x the estimated volume. Row counts are measurable live via tenant-ops (WQL count) where the data already exists; check new custom objects against the tenant inventory (customObjectDefinition read) while at it (references/tenant-ops.md).
- [ ] **Solution-options decision on file** (wd-discovery `references/solution-options.md`) - the "why is this an Extend app at all" question was asked and a named client approver signed it. Missing assessment = review finding.
- [ ] **Platform citizenship:** retries bounded (backoff on 5xx only, never 4xx), reads bounded (no unbounded WQL), writes bulked (`?bulk=true` where it exists), no polling loops - the non-negotiables block in [references/standards.md](standards.md) section Platform citizenship.
- [ ] **No preview/DevCon feature on the critical path without a named GA fallback** ([references/release-impact.md](release-impact.md) rule) - a design that only works if an unshipped capability GAs on time is a finding.

## The ADR-lite record

The review produces a short architecture-decision record - enough that month-12 maintainers know *why*, not a formal ADR process:

- **Approach** - the chosen technical shape in 2-4 lines (write surfaces, sync/async split, key BOs).
- **Alternatives rejected** - one line each, with the reason (this is what stops the approach being relitigated by the next developer).
- **Reviewer name + date** and the disposition of each checklist finding.

Append it to the design doc's **Technical Specification tab** (wd-design-doc owns the tab format) so the record lives with the design it governs, versioned with it.

## Invariants contract (ships with the ADR-lite)

Beyond acceptance criteria ("what done looks like"), pin the INVARIANTS - the assumptions the design silently depends on, each with a concrete check. An invariant with no check is a hope.

| Invariant | Why the result is wrong if it fails | How to check (a test a reviewer can run) |
|---|---|---|

Typical Extend invariants: a required SINGLE_INSTANCE reference (WID/RefID) exists in EVERY target tenant; a currency value is carried as a STRING with its code; a BO key is unique before a create loop; a PUT sends the COMPLETE payload (full-replace); a dynamic/derived field is never written to. Carry the contract into the design-to-code sweep (workflow.md Rule 3) so no builder quietly drops one, and check every entry at review - a design that survives its own invariants contract is genuinely build-ready.

(adapted from an internal firm skill, 2026-08-28)
