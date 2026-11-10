# Steering Committee & Sponsor Governance

The executive layer above weekly status: the standing SteerCo forum, the sponsor
relationship, and the exec-facing artifacts. Applies per project and (more often)
at program level - in program mode there is **one** SteerCo for the program, not
one per app.

**One sourcing rule governs everything here:** every number on a SteerCo slide
traces to the same Smartsheet data as the weekly status (via **wd-smartsheet**).
There is no separately-maintained "exec truth" - if the exec view and the weekly
status disagree, one of them is wrong and both lose credibility.

## Standing SteerCo deck skeleton (6-8 slides)

Same skeleton every time - the committee learns where to look, and prep becomes
assembly rather than authorship. Deck/page **rendering** defers to
the **pptx** skill (neutral formatting); this reference owns the content.

| # | Slide | Content |
|---|---|---|
| 1 | Program RAG rollup | The one-line-per-app RAG table from `program-mode.md`'s status rollup - reuse it, don't rebuild it. RAG transitions since last SteerCo get one sentence each. |
| 2 | Milestone burn-up | Milestones completed vs baseline plan over time. Slips shown against the **baseline**, not against last month's re-forecast. |
| 3 | Budget vs actuals | Per-app: budget / actuals / EAC / variance %, plus the financial RAG - the Financials block from `status-reporting.md`, rolled up. Include the cumulative approved-CR line from `raid-log.md`'s CR rollup. |
| 4 | **Decisions required** | The slide the meeting exists for. Each decision follows the **1-3-1 shape** (same discipline as wd-comms' decision-needed email in `wd-comms/references/templates.md`): **one** question, exactly **three** options (one may be "do nothing" - one option is a demand, two a coin flip, four+ an analysis dump), and **one** delivery-team recommendation with its definition-of-done. Keep cost of delay and decide-by date per decision. No decision leaves the room as "noted." |
| 5 | Top risks | 3-5 max, from the RAID (score >=6 / Leadership escalation level). Each risk carries a **specific ask** of the committee - a risk without an ask is an FYI and belongs in the pre-read, not on a slide. |
| 6 | Look-ahead | Next period's milestones, go-lives, and client-side commitments coming due (from the sponsor charter, below). |
| 7-8 | Optional | Live demo (outcome-framed), value delivered to date (wd-post-go-live's value-capture reference), or a deep-dive the sponsor requested last time. |

## Cadence and attendance

- **Monthly** (default) or **6-weekly** for slower programs. Fixed calendar slot,
  set at kickoff for the whole engagement.
- **Decision-makers only.** The SteerCo decides; it doesn't get briefed. Anyone
  who can't say yes to slide 4's decisions is an optional attendee at best.
- **Pre-read goes out 48 hours ahead** (send via **wd-comms** - SteerCo pre-read
  template in `wd-comms/references/templates.md`). The meeting starts from the
  decisions, not from a page-turn of the deck.
- 60 minutes. If the deck skeleton doesn't fit in 60 minutes, the program has
  more Reds than a SteerCo can absorb - fix that in the weekly rhythm first.

## No-surprises protocol

Extends status-reporting.md's send-it-the-day-it-goes-Red rule into a sponsor
protocol: **nothing appears Red on a SteerCo slide that the sponsor is seeing
for the first time.**

Sequence, always in this order:

1. **Team** knows (weekly status, RAID).
2. **PM** escalates same-day (the escalation note in `status-reporting.md`).
3. **Sponsor 1:1** - pre-wire before the forum: what happened, what we're doing,
   what we'll ask the committee for. The sponsor walks into SteerCo already
   aligned on the ask.
4. **Forum** - the SteerCo sees it with the mitigation and ask attached.

A sponsor ambushed by their own program in front of their peers stops being an
ally. The 1:1 costs 15 minutes; the ambush costs the relationship.

## Decisions flow back same-day

Every decision made in the forum goes to the program Decisions log **the same
day**, with date + decider + rationale - the same discipline as `raid-log.md`
(see its Decisions log section; don't fork the format). SteerCo decisions are
the most expensive decisions on the program to re-litigate; they're also the
first ones lost when they live only in a deck.

## Sponsor charter + decision rights (set at kickoff)

One page, agreed with the sponsor at kickoff - before the first thing goes
wrong, not after.

**Decision types the program will bring the sponsor** (5-8, each with an
expected turnaround):

| Decision type | Expected turnaround |
|---|---|
| Design sign-off per app | 5 business days from walkthrough |
| CR approval above threshold (hours/$ per governance) | 5 business days |
| Go / no-go per go-live | At the go/no-go meeting |
| Red-status interventions (resources, priorities, dates) | 48 hours |
| Scope trade-off calls (defer X to hold date Y) | 5 business days |

**Decision-rights table** - decision type x who decides / who's consulted /
escalation body. This table is what `raid-log.md`'s CR log means by its
**"Approval Body (per governance)"** column - the CR log points here; keep one
source.

**Sponsor-side commitments, with names** - security-admin turnaround SLA, SME
availability at UAT peaks, steering attendance, sign-off SLAs. Each one becomes
a RAID **Assumption** row on day one (per `raid-log.md`): if it proves false,
the plan changes, and the row is what lets you say so without it being personal.

## Executive one-pager + roadmap

One page, quarterly or on-demand (sponsor's boss, board prep, renewal
conversations). Content:

- **Apps by phase** - the tracker's phase column, drawn not listed.
- **Next-90-day milestones** - dates the executive can hold someone to.
- **Headline financial line** - program budget vs EAC, one line.
- **Top 3 risks in business language** - "invoice approvals stay manual through
  Q3," not "INT-041 dependency slip."
- **Value delivered to date** - consume **wd-post-go-live**'s value-capture
  reference; don't re-derive metrics here.
- **The "so what" rule:** every metric on the page carries one interpretation
  line. An executive should never have to ask "is that good?"

**Roadmap render:** the go-live waves and shared constraints program-mode
already tracks (master timeline, tenant windows, shared-SME peaks), drawn as a
sequenced picture - waves on a timeline, constraints as annotations. Rendering
defers to **pptx** (neutral formatting); the master timeline in
`program-mode.md` is the data source.

### Roadmap render grammar

How to actually DRAW the exec roadmap (the grammar, not the palette - color stays
neutral). (adapted from an internal firm skill, 2026-08-28)

- **Lanes** = domains / workstreams (rows); **Time** = quarters or months (columns).
- **Sequence:** the FOUNDATION lane anchors Q1 and gates its dependents - a dependent
  cannot start before its prerequisite completes. Show slips against the **baseline**, not
  against the last re-forecast (same rule as the milestone burn-up above).
- **Bars = durations; DIAMONDS = point-in-time milestones / go-lives.**
- **Ongoing workstreams** (governance cadence, change management, hypercare) span the whole
  timeline at 50-60% opacity / dashed, so they read as context, not active build.
- **Priority shading:** immediate = strong fill, near-term = medium, ongoing = muted.
- **Readability:** roll 20+ items up to **4-6 workstreams per lane**, not one bar each.
- **Format:** PPTX for the SteerCo pack; interactive HTML when the client resists
  PowerPoint (it consistently lands better). Same data source either way -
  `program-mode.md`'s master timeline.
