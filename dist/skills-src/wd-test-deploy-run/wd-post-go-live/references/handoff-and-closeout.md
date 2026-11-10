# Handoff & Closeout

Three deliverable sets end the engagement: the **post-production guide**, the **support-ownership matrix**, and the **project closeout** (actuals, lessons learned, memory updates). Hypercare exit and closeout are separate gates - hypercare exit means the app is stable; closeout means the engagement's obligations are discharged and the learning is banked.

## 1. Post-production guide (dual-audience pattern)

One document, two audiences, split into parts so each reader can stop where their job ends:

- **Part 1 - Business / functional.** Written for the process owner and end-user support: what the app does in plain English, who uses it, the happy path with screenshots, common user questions and their answers, how to report an issue (the intake channel + severity definitions from hypercare), known limitations.
- **Part 2 - Technical / administrative.** Written for the client admin and any future developer: architecture overview (BOs, orchestrations, integrations, security groups/ISU), the monitoring runbook (orchestration logs with `wd_log_type = remote` / `wd_response_code` checks, BP event queues, integration events), configuration reference (config BOs, reference attributes, schedules), data retention/export/purge procedures (see `data-retention-export.md`), the release-regression critical-path checklist (see `release-regression.md`), and escalation paths.

**Real examples of the pattern** (structure reference, not content to copy):
- A prior `<your workspace>\<Use-Case>_PostProduction_Guide.docx` and its sibling use-case guides in neighboring folders.
- Related precedent: a headless O4I integration package (no end-user UI) paired a **User Guide** (integration-administrator audience, brand-compliant, auto-refresh TOC, screenshot placeholders) with a **Deployment Guide** (config, ISU/ISSG, reference attributes, schedule) - the same split by audience, delivered as separate docs when the app has no end-user UI.

Mechanics of producing the .docx (styles, TOC, template handling) -> the **docx** skill. Wireframe/screenshot embeds follow the standing rule: the designer provides clean exports for final docs; anything Claude renders is a draft placeholder.

## 2. Support-ownership matrix

A one-page table that ends the "who do I call" ambiguity. Rows = support activities; columns = **Client admin / Delivery team / Workday**. Draft it during hypercare, ratify it at exit.

| Activity | Client admin | Delivery team | Workday |
|---|---|---|---|
| First-line user questions | **Own** | Escalation | - |
| Defect triage + severity assignment | **Own** (post-hypercare) | Advise | - |
| App code/orchestration fixes | - | **Own** (per support agreement) | - |
| Config changes (config BOs, reference attributes, schedules) | **Own** | Advise | - |
| Security assignments (groups, ISU, domain policies) | **Own** | Advise | - |
| Monitoring runbook execution | **Own** | Spot-check during warranty | - |
| Release regression pass (R1/R2) | **Own** (after first cycle) | First cycle + fixes | - |
| Data export / audit extract runs | **Own** or client data team | Pipeline fixes | - |
| Retention purge orchestration monitoring | **Own** | Fixes | - |
| Platform outages, tenant issues, Extend platform bugs | Report | Diagnose/route | **Own** (Customer Care case) |

Adjust per the actual support agreement - the point is that every row has exactly one **Own**. Note the Workday column is reached via a Customer Care case; make sure the client knows who on their side is authorized to raise one, and that the app's Volumes Questionnaire is already on file with Workday from production-readiness.

## 3. Project closeout

### Actuals vs. estimate - the write-back to wd-estimate

Record actual effort **by phase** against the original estimate:

| Phase | Estimated | Actual | Delta | Why |
|---|---|---|---|---|
| Discovery/design | | | | |
| Build (UI/PMD) | | | | |
| Build (orchestrations/integrations) | | | | |
| Testing (unit/E2E) | | | | |
| Deployment/cutover | | | | |
| Hypercare | | | | |

Then **write the delta back into wd-estimate's calibration table** - per-phase multipliers or notes keyed to app characteristics (BO count, integration count, BP complexity, Prism involvement). Also capture actual transaction/user volumes vs. the Volumes Questionnaire estimates while you're at it - those calibrate the next questionnaire too.

**This feedback loop is what keeps future quotes honest.** An estimate model that never sees actuals drifts optimistic; every closed project that skips the write-back makes the next SOW a little more wrong. Treat the write-back as a closeout exit criterion, not a nice-to-have. (The calibration data itself lives with **wd-estimate** - this step produces and delivers it, nothing more.)

### Lessons learned

Short structured capture, 30-60 min with the delivery team while memory is fresh:

- What in the design survived contact with the client unchanged? What got reworked, and would earlier discovery have caught it?
- Which open items lingered longest, and who should have owned them sooner?
- Any platform surprises (API limits, referential 500s, release breakage, tenant quirks) worth encoding as standing guidance?
- Hypercare: actual defect volume/severity mix vs. expectation; did the SLAs hold?

Route durable findings to their proper home: platform lessons -> the relevant skill's references; client/program facts -> memory; estimation lessons -> the wd-estimate calibration notes above.

### Memory / documentation updates

- Update the app's project memory file: delivered status, final doc locations/versions, resolved vs. still-open items, support-ownership summary.
- Confirm the design doc's final version matches production (post-hypercare fixes included) and its Open Items tab reflects closeout state.
- File the post-production guide, monitoring runbook, critical-path checklist, and support matrix in the app's folder alongside the design doc.

### Closeout checklist

- [ ] Hypercare exit criteria met and signed off
- [ ] Post-production guide (Parts 1 + 2) delivered
- [ ] Support-ownership matrix ratified
- [ ] Monitoring runbook handed over and executed once by the client admin
- [ ] Release-regression critical-path list stored with app docs
- [ ] Data retention/export/purge decision documented (no "TBD" cells left)
- [ ] Actuals-vs-estimate recorded and delta written to wd-estimate calibration
- [ ] Lessons learned captured and routed
- [ ] Memory + design doc updated to closeout state
- [ ] KT complete -> owned by **wd-kt** (sessions, admin training, developer KT docs) - verify done, don't duplicate here
- [ ] Benefits snapshot delivered to the sponsor (`value-capture.md` section 5 - unmet KPIs get a named follow-up, never silence)
- [ ] CSAT pulses run - hypercare-exit (users + process owner) and closeout (sponsor) per `value-capture.md` section 4
- [ ] Reference-rights ask made and logged with date + approver (`value-capture.md` section 6)
- [ ] Case-study one-pager drafted; harvested metrics filed to the bow-sales-enablement claims register (`value-capture.md` section 6)
- [ ] Open tech-debt items transferred to the program tech-debt register (wd-pm references/program-mode.md) - debt transfers, it never dies with the project
- [ ] Opportunity log reviewed and qualified rows routed (`account-growth.md` section 4)
- [ ] **Delivery-team access revoked:** enumerate every engagement-created access path - consultant tenant accounts, dev/test API clients and refresh tokens, demo proxy rules and demo test-cast assignments - and remove each, or mark DNU where the client wants it parked (naming convention per wd-extend-dev `references/standards.md`). The credential-lifecycle table in wd-extend-dev `references/security-setup.md` is the enumeration source; anything a departing consultant held gets rotated, not just de-assigned
- [ ] **Client countersigns the access-revocation list** - a client security admin confirms each row was removed/rotated; attach the countersigned list to the closeout artifact (it is also the standing answer to the client security questionnaire's consultant-access question - wd-deployment `references/security-questionnaire.md`) - spot-check by negative test: a retired profile's tenant-ops check-tenant must FAIL post-revocation
