# Managed Services - Steady-State Production Support

Hypercare is a **time-boxed surge**; managed services is the **standing offering that runs for the app's life**. This reference covers the ongoing production-support engagement that begins where hypercare/warranty ends (`SKILL.md` hypercare frame; exit + handoff in `handoff-and-closeout.md`) and keeps the app supported, monitored, patched, and release-regressed on a recurring, contracted basis. It answers the "who supports this in year two" question that the support-ownership matrix opens but does not fully close, and it supplies the content behind the "firm-provided managed service" pipeline-owner option named in `data-retention-export.md` (retention question #6).

This is an **optional, separately-priced** offering - some clients self-support after handoff (the matrix's client-admin-owns path), others retain the firm. Scope it as a decision, not a default.

## 1. Hypercare -> steady-state transition

Managed services **begins at hypercare exit**, not before. Reuse the hypercare exit criteria (`SKILL.md`) as the entry gate - don't start a paid retainer on an unstable app.

**Entry criteria (all must hold):**
- Hypercare exit criteria met and signed off (no open Sev1/Sev2, defect trend flat, monitoring handed over).
- KT sign-off complete - the client team can operate/support/extend per **wd-kt** (its sign-off artifact gates closeout in `SKILL.md`).
- Support-ownership matrix ratified (`handoff-and-closeout.md`) so every activity has exactly one **Own** - the retainer only covers the rows the client assigned to the firm.
- A signed support agreement in place (section 6) - otherwise support is uncontracted goodwill.

**What changes at the boundary:**

| | Hypercare | Managed services (steady-state) |
|---|---|---|
| Intensity | Reserved developer, daily stand-up | Pooled/on-call, ticket-driven |
| Cadence | Daily triage dropping to 2-3x/week | Monthly service review + as-incidents-arise |
| SLA basis | Elevated, all-hands on Sev1 | Tiered SLA by severity + coverage hours (section 2) |
| Cost | Bundled into the build/warranty | Separately priced retainer/subscription (section 5) |
| Who's on point | Named builder | Named support coordinator on each side (section 2) |
| Regression | The delivery team runs it | Recurring service or client-run-with-firm-fixes (section 3) |

## 2. Support tiers / SLA model

Carry the hypercare **severity definitions forward unchanged** (`SKILL.md`: Sev1 app-unusable/data-corruption, Sev2 blocked-path-with-workaround, Sev3 cosmetic/enhancement) - a client shouldn't relearn severities at handoff. What steady-state adds is a **committed response/resolution matrix and coverage hours**, put in writing in the support agreement:

| Severity | Target response | Target resolution* | Notes |
|---|---|---|---|
| Sev1 | Same business day | Workaround ASAP; fix per next safe deploy | All-hands; may trip SaaS section 1.6 network-integrity handling if platform-side |
| Sev2 | 1 business day | Within the service period | Workaround expected first |
| Sev3 | Logged, reviewed at monthly service review | Backlog / next release window | Enhancements are change-orders, not Sev3 (section 4) |

*Resolution targets are best-effort commitments, not warranties - the SaaS body disclaims warranties and caps liability (saas-agreement.md section 5/section 6). Never draft a resolution SLA that reads as a guarantee; that is a legal-risk clause (wd-contracts guardrail).

**Coverage hours** - state them explicitly: business hours in a named time zone vs. extended vs. 24x7. Coverage tier is a primary retainer price driver (section 5).

**Authorized support coordinators** - the client designates a **Primary + Alternate Support Coordinator** (this is SOW section 8 client-responsibility item (x), and the SaaS section 1.5 primary + escalation contact). Only coordinators may open tickets or raise a Workday Customer Care case; this prevents side-channel DMs (the same discipline as the hypercare single-intake-channel rule) and keeps volume attributable for renewal sizing.

### Security incidents - a classification of their own, not a severity

A **security incident** (credential exposure, data visible to the wrong role, an ISU or API client behaving anomalously, suspected exfiltration) is classified **separately from defect severity** - a "cosmetic" data-visibility bug is still a security incident, and the Sev1-3 response matrix above does not govern it. Triage question at intake: *does this involve access, credentials, or data reaching someone/somewhere it shouldn't?* If yes, run the containment recipe map **first**, investigate second.

**First-hour containment recipe map** (recipes by number in wd-deployment `references/tenant-task-recipes.md`):

| Suspected exposure | Containment move | Recipe |
|---|---|---|
| API client / refresh token compromised | Regenerate the client secret / revoke and re-issue the refresh token | R6 |
| ISU or its group over-reaching | DNU/disable the ISSG (or pull the ISU from it) - cuts the integration's access at the group | R4 |
| Runaway/abused orchestration | Unschedule / disable the launch config | R11 |
| Any of the above | **Snapshot logs BEFORE containment changes overwrite state**: orchestration run logs (`wd_log_type = remote`), integration events, sign-on logs for the ISU | - |

**Notification chain:** first call goes to the **client security-office / incident-notification contact captured at onboarding** - a standing row in the client onboarding packet (wd-pm `references/client-onboarding-packet.md`); if that row was never filled, the coordinator (section 2) is the fallback and filling the row becomes an action item. (!) Notification **timelines** are set by the BAA and contract terms, not by this runbook - check the executed paper (wd-contracts; breach-notification coverage in the SaaS body is a known cross-check item) and never commit to a notification window the contract doesn't define.

## 3. The ongoing support runbook

Steady-state support is the hypercare monitoring runbook (`SKILL.md`) turned into a **repeatable service**, plus the recurring release work. Build the runbook once, hand it over per **wd-kt** (its support-desk triage runbook: symptom -> cause -> fix or escalate), and execute it against the ratified matrix.

- **Incident intake** - one queue (client ticketing system or shared inbox), coordinator-gated (section 2), every ticket logged with severity/reporter/repro. Same single-channel rule as hypercare.
- **Triage** - map symptom to owner via the support matrix: config/security/first-line-user -> client admin; **app code/orchestration fixes -> the firm (per support agreement)**; platform/tenant/Extend-platform bug -> Workday via a Customer Care case (`handoff-and-closeout.md` matrix; confirm the client knows who is authorized to raise one).
- **Monitoring** - run the daily/periodic checks from the monitoring runbook (`SKILL.md`: orchestration logs `wd_log_type = remote` / `wd_response_code`, BP event queues, integration-event runs, volume sanity). In steady-state the client admin usually owns execution; the firm spot-checks or owns per the matrix.
- **Patching / fixes** - code and orchestration changes ship through **wd-extend-dev**'s change workflow (pull-latest + diff, KT-level comments, change-list); this reference does not restate that. A retained managed service owns the *fix*, the client owns *config*.
- **Workday R1/R2 regression as a recurring service** - the twice-yearly release pass is the largest predictable steady-state work item. Run it every cycle per `release-regression.md`: after handoff the client admin typically executes the critical-path checklist and **the firm (if retained) handles the fixes** - price this as a recurring line, not a surprise. This is the matrix's "Release regression pass (R1/R2): firm first cycle + fixes" row extended past the first cycle.
- **Data pipeline / retention runs** - if the client retained the firm as the pipeline owner (`data-retention-export.md` #6), export/purge-orchestration monitoring is a runbook item here; the matrix's "Retention purge orchestration monitoring - firm: Fixes" row applies.
- **Monthly service review -> quarterly QBR** - every third service review upgrades to the account-level QBR (service health + adoption/KPI trend + release outlook + backlog + asks); format, roll-up rules for multi-app clients, and the renewal-timing hook live in `account-growth.md` section 2.

## 4. In-scope vs. change-order

The retainer covers **keeping the delivered app running as-designed**: incident response, monitoring, break-fix on firm-owned code, and the recurring regression pass. Anything that **changes what the app does** is a change order, priced from the estimate model (wd-estimate), not absorbed:

- New features / enhancements (hypercare's "enhancement requests are not defects" rule carries forward - they feed the next SOW).
- New/changed integrations, custom report development, tenant-configuration remediation.
- Training beyond standard, extended/after-hours user support.
- **Refresh KT for a new client administrator** (the original admin left/moved) - a named line item, included-or-charged per the support agreement, never absorbed silently: the session pattern is **wd-kt**'s new-admin path (admin-guide reading order + teach-back), not a full KT redo. Decide included-vs-charged at contracting so the first admin turnover isn't a scope argument.

These mirror the SOW section 9 "Other Services" exclusions and the bow-pricing **charge-separately triggers** (customization, custom reports, training beyond standard, extended user support, tenant remediation). Keep the exclusion list in the support agreement aligned with those so silence reads as *out of scope*, not *free*.

## 5. Pricing the retainer -> wd-estimate

Retainer/subscription pricing is **owned by wd-estimate** - do not build the number here. Key hooks:

- A managed service is priced like a subscription, **to value, not to cost** (wd-estimate `bow-pricing-and-value.md`): the build-up defends a governed floor, the value case sets the ceiling; hold one governed floor across artifacts.
- Primary cost-to-serve drivers to size: coverage-hour tier (section 2), expected incident volume (calibrate from hypercare actuals - `handoff-and-closeout.md` closeout captures these), the two regression cycles/year (section 3), and any pipeline/retention monitoring.
- Cost-to-serve unknowns (support + regression hours) are **open items until calibrated**, never asserted margins (bow-pricing doctrine). Feed the hypercare/closeout actuals into that estimate so the first renewal is priced on real volume, not a guess.

## 6. Contracting it -> wd-contracts

The support terms **live in the contract paper** - draft them through **wd-contracts** (DRAFT-only guardrail applies; never invent or modify liability/warranty clauses):

- For a **Marketplace/BoW subscription**, ongoing support is already a scope component of the Provisioning SOW - "ongoing Technical Support via the firm's managed-services process for designated client support contacts" (sow.md section 1), with "Knowledge Transfer and Support" in section 7 Additional Services and the Primary + Alternate Support Coordinator in section 8(x). The SaaS master's section 1.5 Maintenance & Technical Support governs it at the legal layer (saas-agreement.md).
- For a **bespoke (services-built) app**, there is no confirmed firm managed-services template in the SaaS/SOW pair - a support retainer for a custom build routes to a separately-executed Professional Services Agreement (wd-contracts flags this; do not synthesize one from the subscription paper).
- Liability for support is capped by the SaaS section 6 cap (fees for the last 12 months under the applicable SOW) - another reason SLAs are best-effort targets, not warranties (section 2).

## 7. How it attaches to a Marketplace / BoW subscription product

For a productized app the managed service is **not a bolt-on - it is baked into the subscription**. The bow-pricing doctrine says *bundle deployment (and standard support) into the subscription; do not create a separately-discountable implementation/support SKU* - unbundling invites margin erosion. So:

- Standard steady-state support (this reference's section 2-section 3 at the base coverage tier) is **inside** the annual subscription fee (sow.md section 6 flat annual fee).
- Only the **charge-separately triggers** (section 4) and above-standard coverage tiers become add-on lines.
- The recurring R1/R2 regression pass is part of the subscription's "Updates and Upgrades" promise (sow.md section 4) - frame it as sustaining reliability, using the softened non-promissory language that section prefers.
- One app per Provisioning SOW; the support terms ride each app's SOW under the single client SaaS master.

## Boundaries

- **Hypercare, monitoring runbook content, closeout, and the support-ownership matrix** -> `SKILL.md` + `handoff-and-closeout.md`; this reference starts where hypercare ends and does not restate the matrix.
- **Retainer/subscription pricing** -> **wd-estimate** (`bow-pricing-and-value.md`); this reference names the cost drivers, not the number.
- **Support-agreement terms, SLAs-as-contract, liability** -> **wd-contracts** (SOW section 1/section 7/section 8, SaaS section 1.5/section 6); DRAFT-only, never draft warranty/liability language.
- **Support runbook / triage doc + KT sign-off** -> **wd-kt**; **code fixes and change workflow** -> **wd-extend-dev**; **the recurring regression pass mechanics** -> `release-regression.md`.
