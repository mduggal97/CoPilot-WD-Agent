# Reading an Extend app's own diagnostics (the developer-site log stream)

**The trap this reference exists to close:** an Extend app's `console.info` / `console.error`
output does **NOT** appear in the browser console. It goes to the **developer site's Logs view**.
`read_console_messages` on an Extend app page returns platform noise and nothing the app said.

**Cost of not knowing this:** on one engagement an open design question - "does the upstream
platform have data for this tenant, or is the call just slow?" - stayed open for a full day of
guessing at an empty picker. The answer was one search away in the log stream, and settled it in
minutes. Both of the guesses turned out to be wrong.

---

## What this changes in the run loop

- **`read_console_messages(onlyErrors)` being empty is NOT evidence the app is healthy.** The app's
  own errors do not go there. Treat an empty browser console as "the platform did not complain",
  nothing more. Keep asserting it; stop reading it as an all-clear.
- **When a page renders but shows the wrong thing (empty grid, empty picker, missing button),
  go to the log stream before hypothesising.** A page that shows nothing cannot tell you WHICH of
  its inputs was empty. Its logs can.
- **Evidence discipline still applies.** A log line is evidence of what the page received; it is
  not evidence of stored state. Read the BO back to assert persistence (suite rule:
  wd-extend-lifecycle references/verify-in-tenant.md).

---

## Where it is

Workday developer site -> **Apps** -> the app -> two runtime tabs:

- **Logs** - everything the app's code logged, per page, per user, per run.
- **Orchestration Activity** - every orchestration run, with status and **compute time**.

(Activity and Promotions are deploy history, not runtime.)

**Two gotchas that waste minutes:**

- **The company selector at the top must be the right org**, or every app route renders
  "Page Not Found".
- **The app routes are single-page.** Pasting a deep link into the address bar fails - navigate by
  clicking from the Apps list. Browser back works.

---

## The Logs view - query shape

The search box takes **KQL**. **Type the query, then click the apply/refresh control** beside the
date range; pressing Enter alone stages it without running it, and the result count does not move.

Fields that carry the weight:

| Field | Use |
|---|---|
| `wd_app_id` | the app; pre-filled |
| `wd_log_type` | `"app"` = the app's own console output. `"audit"` = deploy/download noise - exclude it |
| `wd_page_id` | the PMD page that emitted the line |
| `wd_message` | the logged text; wildcards work (`wd_message:*someFn*`) |
| `wd_level` | `INFO` / `ERROR` |
| `wd_tenant` | which tenant the run was in |
| `wd_response_code` | gateway status on HTTP lines |

**Four searches that cover most questions:**

```
wd_app_id:"<appId>" and wd_log_type:"app"
wd_app_id:"<appId>" and wd_page_id:"<PageName>" and wd_log_type:"app"
wd_app_id:"<appId>" and wd_message:*<functionName>*
wd_app_id:"<appId>" and not wd_response_code:200
```

**Long messages truncate in the result list.** Expand the row (arrow at the left) and read
`wd_message` in the detail table, or use the JSON tab for the whole record.

**Observed 2026-10-06:** Enter alone did run each query. If the result count does not move,
click refresh.

**Faster: query by URL (verified 2026-10-07).** The Logs tab is an iframe from
`analytics.us.developer.workday.com`. Read its `src`, then open that address in its own tab with
your own KQL and time range in it. The page is then same-origin, so `document.body.innerText` can be
parsed into a timeline, and a run is one query away:

```
.../_plugin/kibana/app/dashboards#/view/<dashboard id>?embed=true&show-query-input=true&show-time-filter=true
  &_g=(time:(from:now-1d,to:now))
  &_a=(query:(language:kuery,query:'wd_orch_id:<first 8 chars of the run id>*'))
```

- **Run list:** `wd_app_id:"<appId>" and wd_message:"has started"` gives every flow run with its id.
- **One run, every step:** `wd_orch_id:<id prefix>*` - step names, failures, and whether it reached
  the end step.
- **Quoted phrases, not wildcards, for hyphenated text:** `wd_message:"SRF-ERROR"` matched;
  `wd_message:*SRF-ERROR*` found nothing.

**Time zones (verified 2026-10-06):**
- **The result list shows the browser's time zone.**
- **`wd_date_time` in the record is UTC.**
- **A KQL range on `wd_date_time` is read in the browser's time zone,** not UTC. A row listed at
  07:20 EDT had `wd_date_time` 11:20 UTC, and `wd_date_time >= "2026-10-05T07:00:00"` matched it.
- **So convert a tester's local time to the browser's zone before querying,** not to UTC.

**A page that logs what it loaded gives a timeline of stored state.** Each line shows what was
saved at that open. Use it to tell "never saved" from "saved, then cleared" when a tester's
recording shows a value on screen (recording-review.md).

---

## Orchestration Activity - slow vs. empty

**This is how you separate "the call is slow" from "the call returned nothing".**

- The orchestration list shows a colour bar per orchestration summarising recent runs.
- Open one for its individual runs: run id, status, start time, **compute time**, tenant.
- **Compute time is the honest measure.** A run showing `00:00:00` did not take 30 seconds,
  whatever the browser appeared to do. Client-side waits and orchestration duration are different
  numbers.

**Green does not mean useful.** A successful call returning an empty list is a completed run.
Confirm the payload in the Logs view before concluding the upstream data exists.

---

## The diagnosis pattern worth copying

1. **Orchestration Activity first** - did the call run, and how long did it actually take? This
   kills or confirms the performance theory in one look.
2. **Logs, filtered to the page** - find the line where the app states its conclusion, then read
   the lines ABOVE it for the inputs. The conclusion is usually correct; the question is which
   input made it come out that way.
3. **Compare the two lists that feed the decision.** In the worked case the decisive line reported
   the upstream list and the derived list together - one populated, one empty. That single line
   ended a day-old debate: the upstream data existed, and the empty thing was the team's own
   un-seeded configuration table.
4. **Only then form a hypothesis.**

**Second worked case (2026-10-07) - the cost of skipping step 1.** A vendor-break test left a
picker silently empty. Three code changes and three deploys followed, each assuming the flow had
not failed. One log query then showed every run HAD failed, exactly as designed; the empty picker
is simply how a page shows a failed flow (wd-extend-dev pmd-gotchas #85). Rule: **after any
surprising result in a vendor-break test, read the run in the log before changing code.**

**Generalisable lesson:** when a page shows nothing, the failure is upstream of the render, and
the render cannot name it. Do not test theories against the UI - read the log line where the app
says what it decided and why.

---

## Instrumentation this makes worth asking for

If an app you are testing logs nothing useful, that is a finding for **wd-testing** defect-triage
(class b - design silent), not a reason to guess. An app that logs its **inputs** alongside its
**decision** is diagnosable in minutes; one that logs only the decision is not.

**Also worth knowing:** a logged line can be stale. On one app a message reported a query the code
no longer ran, against a different row limit. **Prefer a line reporting a value the page acted on**
over one reporting what the page intended to do.
