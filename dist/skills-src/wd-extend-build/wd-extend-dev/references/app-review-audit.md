# App & integration review/audit - the playbook and the findings report

A repeatable procedure for auditing an EXISTING Extend app or Workday integration -
pre-go-live QA, post-go-live health check, takeover of someone else's build, enhancement
scoping, or a periodic managed-services review. This file sequences the suite's existing
checklists into one pass and defines the deliverable; the criteria themselves live in the
cited references (never restate them - read them as you go).

**Cardinal rule first: audit the LATEST source, never a stale copy.** Extend:
`wdcli app download <app> --latest-version --overwrite` ([wdcli-workflow.md](wdcli-workflow.md)).
Studio: confirm the local project matches what's deployed (Git + manifest timestamp; recency
caveats in studio.md in the wd-integration-dev skill). Also pull the latest signed design doc/IDD - parity
checks are against the CURRENT design, not the original.

## The sweep, in order

**0. Scope & inventory (30 min).** From source: pages (+ which are routed tasks), BOs +
fields, flows by type, security domains, app attributes, `.task`/cards, external endpoints.
(For O4I flows, the **Orchestrate Flow Viewer** community extension renders each `.orchestration`
as a diagram - a fast way to grasp trigger/branch/loop/error structure before reading the raw JSON;
see orchestration.md Debugging.)
From tenant/design doc: volumes, user population, BP wiring. This inventory heads the report
and sizes everything after it.

**1. Security posture.** Read [security-setup.md](security-setup.md) +
[external-apis-and-genai.md](external-apis-and-genai.md), then check: every PMD and flow
carries appropriate `securityDomains`; ISU-authenticated page endpoints are justified
(read-mostly config data) and documented; secrets live in App Attributes - and if a page
calls an external API directly, the key's exposure to page maintainers is a recorded,
accepted risk (else finding); no credentials hardcoded in source; domains map to the design
doc's Security tab (blank/mismatched = finding).

**2. Defect sweep.** Run every PMD against the full numbered list in [pmd-gotchas.md](pmd-gotchas.md) - this is
the highest-yield step; work the numbered list, don't skim. Flows: limits and error handling
per [orchestration.md](orchestration.md) (per-node errorHandler on risky nodes,
`responseStatusCode`/SOAP-fault guards on Send nodes - silent-4xx is the classic latent
defect), plus `validate.py` ([scripts.md](scripts.md)) for structural checks. Parked
`exclude: true` endpoints and `IN_PROGRESS_` flows = flag for intent.

Bug-report triage heuristics (verified on a delivered triage, 2026-08-25): a batch of
"critical" user-reported bugs usually decomposes into ONE or two real code bugs plus
downstream DATA CASCADES from the first bug (of 6 reported: 2 code bugs, 1 design gap,
3 cascades) - fix upstream first, then retest the rest before touching them. Two recurring
shapes: (a) a "missing feature" report on a page that exists is often a widget authored
`type: "hidden"` / inactive `visible` props; (b) an "empty dropdown" is often a picklist
sourced ONLY from prior transactional records (GROUP BY over the transaction BO) - with no
data yet it looks broken; the design fix is seeding pickers from a master lookup, never
solely from transactions.

**3. Efficiency sweep.** [efficiency.md](efficiency.md) as a checklist: externalized WQL,
compute-once into pageVariables, set-based `list:` helpers vs loops, `exclude`-gated
dependent endpoints, bulk writes batched (`?bulk=true` via flow, not row-at-a-time).

**4. Standards sweep.** [standards.md](standards.md) + integration-naming.md (in the wd-integration-dev skill):
naming, KT-level comments, header/change-log blocks, config-driven UI text (Marketplace-grade
apps), debug-flag convention. Style findings are real findings - this code gets handed to
client developers.

**5. Enhancement opportunities.** The forward-looking lens - absence is an opportunity, not
a defect: config-driven text, custom error pages, i18n (Translation BO), cards/hub
entry points, tenant sequence generator vs counter BO, flow-proxy for any page-direct
external call, and anything on [release-impact.md](release-impact.md)'s deprecation watch.

**6. Integration variant** (Studio/EIB/CC - replaces steps 2-4 above):
integration-build.md build gates + studio.md anti-patterns (both in the wd-integration-dev
skill). Minimum bar: logging/audit framework present (global catch, named per-step
catches, severity rollup); document retention set; standard launch-param block
(Validate/Debug/Debug-Event-WID); manifest-as-runbook current (stale `Sample` or cloned
descriptions = finding); XSLT streaming-appropriate for volumes (xslt3.md in the wd-integration-dev skill);
naming per standard; no committed test data or `$tf/` folders.

**7. Design parity.** Diff behavior against the latest signed design doc (wd-testing's
triage tree decides what each mismatch is: code defect, design ambiguity, or undocumented
requirement change -> route to change control). Code that outgrew its design doc is itself a
finding - the doc is the maintenance contract.

## The findings report (the deliverable)

One document: `<APP>_Review_Findings_v<maj.min>.xlsx` (or .md for internal-only), following
wd-design-doc's document-polish rules (in the wd-design-doc skill) if Excel.

1. **Executive summary** - one paragraph + counts by severity; overall health verdict.
2. **Inventory** (from step 0).
3. **Findings table**, severity-sorted:

| ID | Severity | Area | Where (file:line) | Finding | Recommendation | Effort |
|---|---|---|---|---|---|---|
| F-001 | Critical | Security | `foo.pmd:42` | ... | ... | S |

- **Severity:** Critical (data/security exposure, silent data loss) / High (defect users
  will hit) / Medium (defect in edge path, or efficiency issue at scale) / Low (standards/
  polish) / **Enhancement** (opportunity, not a defect - its own severity so it never
  inflates the defect count).
- **Effort:** S (<1/2 day) / M (<=3 days) / L (design needed). An estimate-worthy L goes to
  wd-estimate as a change order, not a guess in this report.
- Mark each finding **Verified** (reproduced/confirmed in source) or **Suspected** (needs a
  tenant test) - never present suspected as verified. Many Suspected findings can be promoted
  or cleared live via tenant-ops reads (WQL counts, BO state, refs, RaaS) inside the audit
  sitting (references/tenant-ops.md).
4. **Recommended sequencing** - quick wins vs change-control items; anything touching a
   signed design routes through wd-design-doc change control.

## Boundaries

Audit != fix. If the client's developer owns the code, findings feed the change-list handoff
([workflow.md](workflow.md)) - don't edit and deploy. Design-doc/IDD completeness audits are
wd-design-doc's `idd_audit.py` + gap-analysis. Post-release (R1/R2) regression of a healthy
live app is wd-post-go-live's checklist - this playbook is for when someone asks "how good
is this build, and what should we do to it?"
