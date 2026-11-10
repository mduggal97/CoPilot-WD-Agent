# Workday Release Regression for Live Extend Apps

Workday ships two major releases a year - **R1 (March)** and **R2 (September)** - and both land on live tenants whether or not anyone tested. A live Extend app is exposed on several surfaces: PMD page widgets, orchestration node types, the delivered REST/SOAP/WQL APIs it calls, BP definitions it launches or advances, and security objects. Plan a lightweight regression pass **every cycle**, during the preview window, per live app.

## The cadence

1. **When the preview window opens** (roughly 5-6 weeks before the release goes live), get the app's target tenant onto the preview release - use the sandbox-preview tenant, or the designated IMPL preview tenant for implementation-phase programs.
2. **Read the release notes / deprecation notices first**, before touching the app. Specifically scan for:
   - **PMD widget deprecations or behavior changes** - grep the app's PMD source for any widget type named in the notices.
   - **Orchestration node deprecations** - same drill against the app's orchestrations.
   - **API version retirements** - Extend apps pin SOAP web-service versions (e.g., Staffing v43.0, Financial Management v46.1) and call versioned REST endpoints; confirm none of the pinned versions are entering retirement.
   - **WQL / RaaS changes** to data sources and fields the app queries.
3. **Run the critical-path regression** (below) in the preview tenant.
4. **Re-run perf-sensitive flows** - anything identified in the Performance Testing Template as high-volume or peak-window (bulk submits, scheduled batch orchestrations, large WQL reads). Releases occasionally shift API latency or paging behavior; a flow that was comfortably inside its window can drift.
5. **Log findings as defects** with the release tag; fix in preview, redeploy before the release hits production, and note the change in the app's change log.

## The per-app critical-path list

Keep a standing checklist per live app - 5-15 scenarios, not the full test suite. **Source it from the design doc's Unit Testing tab**: that tab already enumerates the scenarios the app was accepted against; the critical-path list is the subset that (a) touches money, HR actions, or approvals, (b) crosses an API boundary, or (c) runs on a schedule.

Typical shape:

| # | Path | Surface exercised | Pass criteria |
|---|---|---|---|
| 1 | Submit a request end-to-end through approval | PMD form, BO writes, BP launch | Event completes, data lands |
| 2 | Scheduled orchestration nightly run | Integration trigger, RaaS read, SOAP write | Run log clean, `wd_response_code` all 2xx |
| 3 | Bulk paste/import path | Bulk endpoint (100/req), validation | Full batch lands, errors surface |
| 4 | Approval routing to each role | BP definition, security groups | Right inbox, right step order |
| 5 | Report/export used by the client monthly | RaaS/WQL over app BOs | Row counts + fields match |

Store the list with the app's documentation (post-production guide Part 2, or alongside the design doc) so whoever owns steady-state support - often the client admin by the second release - can run it without the original developer.

## Who runs it after handoff

During hypercare/warranty: the delivery team runs the pass. After transition to steady-state: per the support-ownership matrix - usually the client admin executes the checklist, the delivery team (if retained) handles fixes. Make the checklist executable by a non-developer: exact navigation, exact inputs, expected screenshots.

## Cheap insurance

- Rows 2 and 5's pass criteria are machine-checkable via tenant-ops reads (WQL over the log BO; RaaS count/field diff preview vs prod - wd-extend-dev references/tenant-ops.md).
- Subscribe someone to Workday Community release-note feeds for Extend specifically; deprecations are announced a release or two ahead.
- After each pass, date-stamp the checklist ("last regressed: R2 2026, all pass") - auditors and new support staff both ask.
- If a release breaks something, capture it in lessons-learned at closeout and, if it cost real effort, in the actuals fed to wd-estimate.
