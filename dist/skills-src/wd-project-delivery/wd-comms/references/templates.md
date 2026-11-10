# Message templates

Ready-to-adapt skeletons. Replace `[bracketed]` placeholders; delete sections
that don't apply. Keep the final message shorter than the template if you can.
Apply the client's branding profile (terminology, sign-off, cc norms) from
`references/clients/<name>.md` before finalizing.

---

## 1. Weekly status email

Pairs with wd-pm's status format - pull RAG, accomplishments, and risks from
the same data wd-pm reports; don't re-derive them.

```
Subject: [FYI] [Project name] weekly status - week of [date]

Hi [name(s)],

Headline: [one sentence - overall RAG + the single most important thing this week].

Progress this week:
- [accomplishment 1]
- [accomplishment 2]

Coming up next week:
- [planned item + owner]

Risks / needs from your team:
- [risk or ask - owner, date needed]

Next steps:
- [action] - [owner], by [date]

[Sign-off per client profile]
```

---

## 2. Meeting recap + actions

Pairs with wd-pm meeting-intake output - use its extracted decisions/actions as
the source; this template is the client-facing rendering.

```
Subject: [FYI] Recap + actions - [meeting name], [date]

Hi all,

Thanks for the time today. Quick recap:

Decisions made:
- [decision 1 - one line]

Open questions:
- [question - who owes the answer, by when]

Actions:
- [action] - [owner], by [date]
- [action] - [owner], by [date]

Please flag anything I've mis-captured by [day].

[Sign-off]
```

---

## 3. Decision-needed email

The 1-3-1 shape (pattern from a community skill-craft survey, 2026-08-06 -
rebuilt for this suite): ONE problem statement, exactly THREE options, ONE
recommendation. Why three: one option is a demand, two is a coin flip, four or
more is analysis dumped on the decider. "Do nothing" is a legitimate third
option - pricing its cost is often what makes the decision move. Same shape as
wd-pm's SteerCo Decisions Required slide (steering-committee.md) - one
discipline, two surfaces.

```
Subject: [Decision needed by [date]] [topic]

Hi [decision-maker],

We need your decision on [topic] by [date] to hold [milestone/date].

The problem (one statement): [what's unresolved and what it affects - 2-3 lines max].

Options (exactly three; one may be "do nothing"):
- Option A - [description]. Pros: [one line]. Cons: [one line].
- Option B - [description]. Pros: [one line]. Cons: [one line].
- Option C - [description]. Pros: [one line]. Cons: [one line].

Our recommendation: Option [X], because [one line].
Done looks like: [the observable state once this is decided and implemented].
First step on a yes: [first implementation action] - [owner], by [date].

If we don't hear back by [date], we will [default path / impact].

[Sign-off]
```

---

## 4. Escalation note

State root cause honestly - including when it's on the firm's side. One specific
ask, not "please advise."

```
Subject: [Action needed by [date]] Escalation - [issue, one phrase]

Hi [name],

Impact: [what is blocked/at risk, in business terms - dates, users, dollars].

Root cause: [plain statement of what happened and why, honestly attributed].

Options:
- [Option A - effect on timeline/scope/cost]
- [Option B - effect on timeline/scope/cost]

Ask: [the specific decision or resource needed], by [date], from [whom].

Happy to walk through live - I'm free [windows].

[Sign-off]
```

---

## 5. Design-review invite

```
Subject: [Action needed - pre-read] Design review: [app/feature], [date/time]

Hi all,

We're reviewing the [app name] design on [date, time]. To make the session
count, please pre-read before the meeting:

Pre-read (~[X] min): [link to design doc - specific tabs/sections]

Decisions on the table:
- [decision 1 - the question, one line]
- [decision 2]

If you can't attend, send input on the decisions above to [name] by [date].

[Sign-off]
```

---

## 6. Go-live announcement (stakeholders)

```
Subject: [FYI] [App name] is live as of [date]

Hi all,

[App name] went live in production on [date]. [One sentence: what it does,
in plain English.]

What this means:
- [key change for the business, one line]
- [key change 2]

Support: issues go to [channel/contact]; response within [SLA].
Hypercare: [team] is monitoring closely through [date].

Thank you to [client team names] for [specific contribution].

[Sign-off]
```

---

## 7. End-user "what's changing" note

Written for people who use the system, not project stakeholders. Zero jargon.
Also the changed-behavior notice for post-go-live enhancements to a live app, not
just initial go-live - source the content from wd-kt's release notes (what changed /
opt-in vs automatic / action required).

```
Subject: Starting [date]: a new way to [task, in the user's words]

Starting [date], you'll [do task] in [system name the client uses] instead
of [old way].

What's changing:
- [old step] -> [new step, one line each, max 3]

What's NOT changing:
- [reassurance - approvals, timing, whatever stays the same]

Where to get help: [job aid link] / [support contact]

No action needed before [date].
```

---

## 8. UAT defect / status update

```
Subject: [FYI] UAT update - [app name], [date]

Hi [name(s)],

Testing status: [X of Y scenarios passed]; on track / at risk for [exit date].

Defects:
- Open: [n] ([n] high, [n] med/low)
- Fixed since last update: [n] - ready for retest: [list or link]
- New this period: [one line each for high-severity only]

Needs from your testers:
- [retest ask - owner, by date]

Next update: [date].

[Sign-off]
```

---

## 9. Sponsor brief (monthly / milestone)

For the executive sponsor, not the working team. Outcome language, not RAG
minutiae - pairs with wd-pm's steering-committee.md (exec one-pager rules).
Three bullets of progress, one thing needing their weight, one value line.

```
Subject: [FYI] [Program name] - sponsor brief, [month / milestone]

Hi [sponsor name],

Progress since last brief:
- [outcome, in business terms - "managers now approve X in the app", not "build 80% complete"]
- [outcome 2]
- [outcome 3]

Where we need your weight:
- [ONE decision or risk - what it is, what we recommend, what happens if it waits]

Looking ahead: [one forward-looking value line - what the business gets next, and when].

[Sign-off per client profile]
```

---

## 10. SteerCo pre-read / invite

Goes out 48 hours before the steering committee (wd-pm steering-committee.md
owns the deck content and cadence rules - this is the transmittal).

```
Subject: [Action needed - pre-read] [Program name] Steering Committee, [date/time]

Hi all,

Steering committee is [date, time]. Pre-read attached/linked (~[X] min).

We will start from the decisions, not a deck walkthrough. Decisions on the
table:
- [decision 1 - the question, one line, decide-by date]
- [decision 2]

Also on the agenda: [one line - e.g., program RAG, budget position, top risks].

If you can't attend, please send your position on the decisions above to
[name] by [date] - they will be decided in the session.

[Sign-off]
```
