# Design gap analysis - finding the holes before the client does

Run this before every design review and mandatorily before sign-off. Complexity hides gaps; this checklist makes them enumerable. Output: a list of gaps, each either fixed on the spot or logged as a yellow open item with an owner.

## Per-tab completeness

- Every Discovery question has a response or is yellow with an owner.
- Every requirement is numbered, testable ("the system shall..." with an observable outcome), and has a priority. Vague requirements ("should be easy to use") get rewritten or flagged.
- Every field in Field Specifications has: type, required?, validation, and a SOURCE (entered / derived / from API X). "Source: TBD" is a yellow item.
- Every BO field in the Object Model appears in Field Specifications (and vice versa); relationships (SINGLE/MULTI_INSTANCE targets) are stated.
- Every write path in Data & Webservice Mapping names the exact operation (op name + version for SOAP; endpoint for REST/WQL/RaaS) and its auth (ISU vs user context).
- Every BP has: initiator, approver chain (or "configured in-tenant by X"), deny behavior, send-back behavior (send-back requires a revise page - a known build constraint), and notifications.
- Security tab has a who-sees-what matrix covering EVERY page and EVERY role - including the negative statements ("Specialists cannot see Reporting").
- Every requirement maps to at least one Unit Testing scenario (derivation methodology: wd-testing).
- Wireframes cover every screen; process flow covers every exchange (thoroughness rules: wd-design-visuals).

## Cross-cutting consistency checks

**Cross-tab name sweep (run before every review):** these five tabs share names that must match exactly - a rename in one that doesn't propagate is the most common gap found in review:
- **Object Model <-> Field Specifications** - every BO and field name matches in both directions; no Field Spec row references a BO that doesn't exist in the model (and vice versa).
- **Object Model <-> Security** - domain targets name real BOs/BPs from the model.
- **Object Model <-> Data & Webservice Mapping** - read/write targets cite the actual BO Reference IDs, not aliases.
- **Field Specifications <-> Wireframes** - label text on wireframes matches the Field Spec name column (the design gets built from the wireframe; drift here causes build rework).
- **Field Specifications <-> Unit Testing** - input column headers in test scenarios match the Field Spec name column.
- **Open Items <-> any content tab** - every cross-reference ("per OI-06") resolves to an actual row on the Open Items tab with matching status.

**Cross-tab CONTENT reconciliation (run as its own numbered pass, AFTER the per-tab sweep).** Two tabs can each be internally consistent and still contradict each other - and per-tab review never sees it. A real engagement shipped client-approved with the Security tab specifying EIGHT purpose-named domains and the Technical Specification tab specifying SIX under different names; the conflict surfaced at build planning, after sign-off. Security domains are hand-created per tenant and don't carry across promotions, so building from the stale list repeats the error in every downstream tenant. Pairs that must AGREE (not just match names):
- **Security tab <-> Technical Specification** - the security-domain LIST (count + names) is identical on both. Mechanically checkable: `idd_audit.py` diffs the domain sets when both tabs carry a domain column.
- **Object Model fields <-> Field Specifications fields** - full set comparison, not spot checks.
- **Requirement IDs referenced anywhere <-> requirement IDs defined on Requirements** - a referenced-but-undefined ID is a broken pointer; a defined-but-never-tested Must/Should requirement is a coverage gap (deliberately untested Won't rows are fine). Mechanically checkable: `idd_audit.py` runs this diff.
- **Tenant / environment identifiers** wherever they appear more than once - one naming scheme, everywhere.
When two tabs disagree, find the corroborating third source (open-items rows, meeting record) to decide which list is authoritative - never pick by recency alone.

- Names match across tabs (a BO renamed in the Object Model but not in Field Specs is a classic).
- Volumes stated in Discovery are consistent with the Technical Specification's limit choices (a 500k-row read designed as a page-sync orchestration violates the 25s cap).
- Every integration/API named anywhere appears in Data & Webservice Mapping - this same inventory later feeds the Volumes Questionnaire (wd-deployment), where omitted APIs are the #1 rejection cause.
- Every Reference ID, WQL data source, and web-service name/version the doc cites is verifiable live via tenant-ops (wd-extend-dev references/tenant-ops.md) - run the liveness reads against the target tenant before sign-off (subject to the ISSG/scope grant).
- FIN designs: sample worktag combinations, budget impacts, and posting-rule outcomes are verifiable live via tenant-ops (validateWorktags / runBudgetCheck / evaluateAccountPostingRules) before sign-off.
- Every open item referenced in a content tab (e.g. "per OI-06") exists on the Open Items tab with matching status.
- Attachment, retention, and audit expectations stated (they surface in post-go-live otherwise - wd-post-go-live).
- **SOW conformance (mandatory before sign-off)**: every design scope element traces to the SOW's enumerated scope or a logged change request; the SOW's assumptions/exclusions are reconciled against what the design actually does. A design element outside both = **STOP** - route it through change control (SKILL.md change-control process; CR log per wd-pm) before sign-off, never sign a design that silently exceeds its contract.

## The questions-nobody-asked sweep

For each of these, either the design answers it or you raise it: What happens on cancel/correction after approval? Who administers config (and via what page)? What does the app do when the source API is down? What's the empty-state (day one, no data)? Are there volume peaks (fiscal year-end)? What can NEVER be deleted (audit)? Who gets notified, on what events, and can they turn it off?

## Commonly-required capabilities - plan them, don't discover them post-go-live

Certain capabilities are needed by nearly every Extend app; each design either includes them or records the explicit decision to exclude:

- **Data retention export/purge process** (the one clients always need eventually): GAP CHECK - does this app need a retention/export plan? It almost always does, because Extend BO data accumulates and has no bulk delete (the mechanics - export options, purge paths, retention periods, tradeoffs - are owned by wd-post-go-live's data-retention-export reference, cross-referenced below). Two design-time realities to decide NOW, not post-go-live:
  - **Export != purge, and BP-tied BOs can't be purged.** A BO that's the target of a (Model) BP cannot be deleted (its BP event trail blocks it) - you can export it but not purge it. Mark which BOs are BP targets -> those are export-only + retention-by-design; only non-BP BOs get a purge orchestration (children before parents). An all-BP-driven app has no real purge - state that as the answer.
  - **Attachments are a separate stream.** If the app stores attachments, their binaries don't come out through row export - decide the archive destination (data lake, or an external ECM like OnBase = its own outbound integration/IDD line), preserve the row<->file linkage, and note attachments on BP-tied BOs also can't be purged.
  Design it as a requirement + spec entry + unit scenarios now; mechanism options and tradeoffs live in wd-post-go-live's data-retention-export reference.
- **KPI & executive reporting - designed in, never an afterthought.** Every design recommends the reports pertinent to the process the app administers (derive from its data: aging by status, throughput, estimated-vs-actual, exception counts, adoption/usage, config-change audit) with audience, KPIs, source objects, and delivery method (in-app view / Workday report over the Extend source / dashboard), marked "recommended - confirm in design sessions." The firm default template carries a KPI & Reporting tab for exactly this.
- Notifications design (events, recipients, opt-out).
- Failure behavior for every external dependency (API down, malformed data).
- Admin/config page for anything an admin maintains (statuses, thresholds, reference values).
- Audit answer: who changed what, when - and what the auditor will be shown.
- No silently blank template tables anywhere (populate or yellow "TBD - none identified thus far"; see SKILL.md).

## Managing what you find

Fix trivial gaps immediately. Everything else: yellow cell + Open Items row with owner and needed-by date, then drive them through meetings (wd-pm agendas pull the open yellow items automatically). A design review that ends without owners on every gap didn't end - it adjourned.

## Non-functional requirements (NFRs)

A complete design also answers the non-functional questions, which are easy to omit. Run the checklist in [nfr-accessibility.md](nfr-accessibility.md) - accessibility (WCAG AA basics), error-handling standards, performance/concurrency targets, browser/device support, security/audit, data retention - and treat an unanswered NFR like any other gap (yellow-flag with an owner).
