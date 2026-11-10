---
name: wd-post-go-live
description: >-
  Run the post-go-live phase of a Workday Extend app - hypercare, production support and
  monitoring, data retention and archival, exporting Extend data (BO REST, RaaS, WQL, LDQ, Prism
  export), twice-yearly Workday RELEASE regression, support handoff, closeout, and warranty. Also
  owns production integration-failure triage - diagnose a failed run, find the error, event status
  and logs ("the integration failed, where's the log", "the nightly integration errored", "check
  the process monitor"). Use when the app is live ("app is live now what"), planning hypercare,
  answering data-retention/audit questions, exporting Extend or Prism data, triaging a live
  integration failure, moving to steady-state support, or closing out the engagement. WQL/RaaS
  query-authoring PATTERNS and code fixes for production incidents are wd-extend-dev; general/UAT
  regression methodology is wd-testing.
---

# wd-post-go-live - Hypercare, Production Support & Closeout

The app shipped. This skill covers everything between "deployed to production" and "engagement closed": the hypercare window, production monitoring, data retention/export strategy, Workday release regression, support handoff, and project closeout (including feeding actuals back to estimation).

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **Hypercare, production support, managed services** (incl. prod integration-failure triage) | [references/managed-services.md](references/managed-services.md) |
| **Data retention / archival / export** (BO REST, RaaS, WQL, LDQ, Prism export) | [references/data-retention-export.md](references/data-retention-export.md) |
| **A DSAR / right-to-erasure request** against the live app | [references/dsar-runbook.md](references/dsar-runbook.md) |
| **A Workday R1/R2 release regression pass** on the live app | [references/release-regression.md](references/release-regression.md) |
| **Support handoff + project closeout + actuals-to-estimation** | [references/handoff-and-closeout.md](references/handoff-and-closeout.md) |
| **Value capture** - KPI actuals vs baseline, ROI, CSAT pulse | [references/value-capture.md](references/value-capture.md) |
| **Adoption** - champions, low-usage findings, feedback loops | [references/adoption-and-feedback.md](references/adoption-and-feedback.md) |
| **Account growth** - roadmap, QBR, renewal playbook | [references/account-growth.md](references/account-growth.md) |

## When to use this skill

- Planning or running a **hypercare** window after go-live
- Client asks about **data retention, archival, audit exports, or purging** Extend/Prism data
- Servicing a **DSAR / right-to-erasure / data-subject access** request against the live app (`references/dsar-runbook.md`)
- Scripting an **export of Extend BO or Prism data** (REST, RaaS, WQL, LDQ, data lake)
- A **Workday release (R1/R2)** is approaching and the live app needs a regression pass
- Building the **post-production guide**, support-ownership matrix, or closeout deliverables
- Recording **actuals vs. estimate** at closeout
- Running **value check-ins** (KPI actuals vs baseline, benefits snapshot, CSAT pulse) or proving the app's ROI
- Driving **adoption** (champions, low-usage findings, feedback loops) after go-live
- Planning the **roadmap workshop, QBR, or renewal** on a live app

## Hypercare structure

Hypercare is a defined, time-boxed window - **typically 2-4 weeks** after first production use - with elevated support intensity. Set it up BEFORE go-live, not after the first defect.

**The frame:**

| Element | Standard |
|---|---|
| Window | 2-4 weeks from first production use (not deploy date). Extend if exit criteria unmet. |
| Daily triage stand-up | 15-30 min, same time daily: new defects, in-flight status, trend. Drop to 2-3x/week as volume falls. |
| Defect intake channel | ONE channel (Teams channel, shared inbox, or client ticketing queue). No side-channel DMs - everything gets logged with severity, reporter, repro steps. |
| Severity SLAs | Sev1 (app unusable / data corruption): same-day response, all-hands. Sev2 (blocked path, workaround exists): 1 business day. Sev3 (cosmetic/enhancement): backlog, weekly review. Agree these with the client in writing. |
| Who's on point | Named developer with reserved availability (don't fully reassign the builder during hypercare) + a client-side admin counterpart who shadows every fix. |
| Exit criteria | Defect intake trend is flat/declining for >=1 week, no open Sev1/Sev2, client support team has resolved at least one issue end-to-end without the delivery team, monitoring handed over. |
| Transition | Formal handoff to the steady-state support model (see the support-ownership matrix in `references/handoff-and-closeout.md`) with a short exit note: open Sev3 backlog, known limitations, monitoring runbook. |

**Enhancement requests are not defects.** Log them separately during hypercare; they feed the backlog and the next SOW, not the triage queue.

## What to monitor daily during hypercare

1. **Orchestration run logs** - in the app's log viewer or via WQL over the log BO. Filter `wd_log_type = remote` to isolate outbound API calls; read `wd_response_code` and `wd_message` on each entry. Non-2xx `wd_response_code` values are your early-warning signal - a spike in 400s usually means bad input data, 500s usually means a referential/config problem or Workday-side issue.
2. **BP event queues** - for apps that launch or advance business processes: check for events stuck "In Progress" or "Awaiting Action" past expected age (routing gaps, missing security assignments, unassigned steps surface here first).
3. **Integration event logs** - for apps with scheduled orchestrations or Integration Framework triggers: verify each scheduled run completed, check WARNING/ERROR message counts, and confirm the schedule actually fired (a silently-unscheduled integration is a classic hypercare miss).
4. **Volume sanity** - compare actual transaction counts to the Volumes Questionnaire estimates. Big deltas either way are worth a conversation (and go into the closeout actuals - see below).

All four checks (plus the adoption line in adoption-and-feedback.md) are runnable as tenant-ops reads - WQL log/count queries, businessProcess events, RaaS over an events/signon report, systemMetrics - capture each day's results as evidence (wd-extend-dev references/tenant-ops.md; production person-data stays aggregate per ai-data-governance).

Write the checks above into a one-page monitoring runbook and walk the client admin through executing it before hypercare exits.

## Data retention and export - settle this BEFORE audit season

Extend BO data and Prism tables live **inside the Workday tenant**. Clients will eventually ask: how long is it kept, how do we get it out for audit, and can we purge it? Do not wait for the auditor's email. Full decision guide, export-option tradeoffs (BO REST vs RaaS vs WQL vs LDQ vs rolling data-lake export), retention policy questions, and purge design:

-> **`references/data-retention-export.md`**

**Servicing an actual data-subject request** (GDPR DSAR / right-to-erasure,
CCPA/CPRA delete, FERPA record request) against the live app - locate the subject's
instances across the app BOs, choose soft-delete vs field-scrub vs full-delete,
honor legal-hold/retention overrides, propagate to downstream systems, and log for
audit:

-> **`references/dsar-runbook.md`** (the legal determination of WHAT must be erased
is the client's/counsel's call, not the implementer's)

Key facts to keep in your head:
- **There is no bulk DELETE** in Extend - purge is an orchestration loop or retention-by-design, and referential constraints throw 500s.
- **Soft-deleted rows persist.** If the app uses the soft-delete pattern, "deleted" data is still in the tenant and still in scope for retention/legal-hold conversations.
- **One delivered program's answer**: rolling 18-24 month export of all custom Extend BOs and Prism tables to the client data lake, which becomes the system of record for aged records. Reuse this pattern where it fits.

## Workday release regression (R1/R2)

Workday's twice-yearly releases (R1/R2 - release calendar owned by wd-extend-dev `release-impact.md`) can affect live Extend apps. Run a preview-window regression pass on the app's critical paths every cycle, check deprecation notices for PMD widgets and orchestration node types, and re-run perf-sensitive flows. Keep a per-app critical-path checklist - source it from the design doc's Unit Testing tab.

-> **`references/release-regression.md`**

## Handoff and closeout

Deliverables: the **post-production guide** (dual-audience: Part 1 business / Part 2 technical), a **support-ownership matrix** (client admin vs. the delivery team vs. Workday), and the **project closeout** - actuals-vs-estimate by phase written back into wd-estimate's calibration table, plus lessons learned and memory updates.

-> **`references/handoff-and-closeout.md`**

The actuals write-back is not optional bookkeeping: it is the feedback loop that keeps future quotes honest. Skipping it means the next estimate repeats this project's misses.

## Value capture, adoption, and account growth

The phase's other job is proving the app was worth building and converting that proof into the next engagement:

- **Value capture** - outcome-metric baselines (set at discovery), the design doc's KPI table locked at sign-off, 30/60/90-day value check-ins, the sponsor benefits snapshot, the **CSAT pulse** (owned definition - hypercare exit + closeout), and the closeout sales-asset harvest (reference rights, case-study one-pager, claims-register feed). -> **`references/value-capture.md`**
- **Adoption & feedback** - champions/super-users, people-readiness go/no-go inputs, adoption as a hypercare monitoring metric ("low usage is a Sev2-equivalent finding"), and the enhancement-request feedback loop. -> **`references/adoption-and-feedback.md`**
- **Account growth** - the hypercare-exit roadmap workshop, the quarterly QBR on the live base, the T-minus-6-months renewal playbook, and the opportunity log. -> **`references/account-growth.md`**

## Boundaries

- **Word document mechanics** (building/editing the post-production guide .docx) -> use the **docx** skill; this skill defines the content and structure.
- **Estimation calibration data itself** lives with **wd-estimate** - this skill produces the actuals and delivers them there; it does not own the calibration table.
- **Knowledge-transfer deliverables** (KT sessions, admin training, developer KT docs) are owned by **wd-kt** - this skill hands off to it and cross-references, not duplicates.

## Flex Credit and agent monitoring (post-go-live)

The Aug 2026 Workday AI platform changes (Flex Credits, Agent System of Record, Platform Consumption Console) create a new post-go-live monitoring and advisory surface that did not exist before. Customers have **never had visibility into integration costs** until now - this is net-new operational hygiene.

**PCC dashboard review cadence:**
Recommend a **monthly review** of the Platform Consumption Console (PCC) with the customer. PCC shows Flex Credit consumption by agent, API usage vs. entitlement, and burn rate trends. Walk the customer admin through interpreting it during hypercare; after hypercare, it becomes a standing agenda item in the QBR cycle (see account-growth.md).

**Credit burn rate alerting:**
Help customers set up monitoring for credit consumption trends. There is **no auto-shutoff at zero** - negative balances are reconciled at true-up, so customers need proactive awareness before they overshoot. Flag if consumption consistently exceeds complimentary credits (meaning they need to purchase additional credits from Workday). The complimentary tier and entitlement multipliers vary by org size - see `wd-estimate/references/flex-credits.md` for the tiers, multipliers, and rate card.

**Agent performance monitoring:**
Track agent effectiveness through the **Agent System of Record (ASOR)**. Key metrics to review:
- **Action completion rate** - are agents finishing the tasks they start?
- **User adoption rate** - is the intended user population actually engaging?
- **Knowledge base quality** (for Self-Service Agent) - bad answers almost always trace to duplicate or outdated policies in the knowledge base, not to agent logic. Audit the KB content as part of every review cycle.

**API volume trending:**
Monitor API call volumes against the customer's entitlement (tiers in `wd-estimate/references/flex-credits.md`). Non-Workday-built integrations (EIBs, Studio integrations, Extend apps) **all count** toward the cap. Core Connectors are free unless augmented by Studio. If volumes trend toward the entitlement ceiling, recommend optimization:
- Consolidate integrations that hit the same endpoints
- Migrate eligible integrations to Core Connectors where possible (Core Connector calls are free)
- Review polling frequencies and batch sizes on scheduled orchestrations

**Agent tuning:**
- **Self-Service Agent (SSA):** The primary post-go-live task is knowledge base optimization - audit content, remove duplicates, ensure policies are current. Bad SSA answers are a content problem, not a model problem.
- **BP Optimize:** Review process recommendations and acceptance rates. Low acceptance usually means the recommendations don't match the org's actual routing preferences - feed findings back to the customer's process owners.
- Feed all tuning findings back into the customer's operational review cycle (the QBR or the managed-services runbook if the engagement continues).

**Quarterly Flex Credit review:**
Propose a **quarterly business review** that includes:
1. Credit consumption vs. budget (actual spend against the estimate from the design doc / proposal)
2. Agent adoption metrics (from ASOR)
3. API volume trending against entitlement
4. Recommendations for optimization or additional credit purchase

This is a **new advisory touchpoint** that did not exist before Flex Credits - and a natural attach for ongoing managed-services engagements.

**Actuals recording:**
Record actual credit consumption against the estimate from the design doc / proposal. Feed variances back to `wd-estimate`'s calibration table so future Flex Credit estimates improve. This follows the same pattern as the existing closeout actuals write-back (see handoff-and-closeout.md) but adds credit consumption as a tracked dimension alongside hours and timeline.

## Lifecycle neighbors

- **Previous:** `wd-deployment` (production deploy, cutover, go-live readiness)
- **Feeds:** `wd-estimate` (closeout actuals -> calibration table) and `wd-kt` (handoff docs, support-team enablement)

## Managed services (steady-state, after hypercare)

When the engagement continues past hypercare into an ongoing support offering, see [references/managed-services.md](references/managed-services.md): the hypercare->steady-state transition, SLA tiers/coverage, the ongoing support runbook (incl. R1/R2 regression as a recurring service), in-scope vs. change-order, and how it's priced (wd-estimate) and contracted (wd-contracts). A natural recurring-revenue attach to a Marketplace/BoW subscription.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
