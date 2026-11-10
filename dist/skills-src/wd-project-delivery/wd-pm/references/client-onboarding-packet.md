# Client Onboarding Packet - What We Need From You, By When

The client-facing twin of the kickoff checklist (**wd-extend-lifecycle** SKILL.md,
"Kickoff checklist"). That checklist is firm-internal; this packet turns the same
items into a document the client sponsor can circulate: what their team owes the
project, who owns each item, when it's due, and what it costs when it's late.
The internal checklist tracks; this packet ASKS.

## Why it exists

Every day-0 blocker on the internal checklist has a client-side owner with a lead
time measured in weeks (security-admin queues, test-user provisioning, sample-data
pulls). Raising them one at a time as they block work makes the delivery team the nag and the
client the bottleneck. Issuing them once, in writing, at kickoff - with named owners
and dates - makes them commitments.

## Contents (four parts)

### 1. Responsibilities-by-phase table (the core)

One row per client obligation, grouped by phase:

| What we need | Named client owner | Needed by | Est. client hours | If late |
|---|---|---|---|---|
| e.g. Security-admin contact + domain-grant turnaround SLA | | Kickoff +1 wk | 1-2 | Every testing milestone slips by the queue length |
| e.g. Named owners for each technical role (integrations / Extend / Prism / reporting) + early tool/sandbox access so they can learn | | Kickoff -> Discovery | per role | Client team can't co-build or take ownership; KT compresses into go-live |
| e.g. Named UAT testers + manager sign-off on their hours | | UAT -2 wks | per tester | UAT window slips or runs understaffed |

Rules:
- **Named owner, not a team** - same discipline as actions (`raid-log.md`).
- **"If late" states the consequence in schedule terms**, not blame terms - it's the
  column that gets items prioritized.
- Estimated hours let managers actually release the time; an unhours'd ask gets
  squeezed out by day jobs.
- Source rows from the internal kickoff checklist + the app's design-session plan;
  add app-specific rows (sample data, legacy exports - see **wd-discovery**'s
  request-before-first-call list) as discovery scopes them.
- **Client technical-team access is a staged set of rows, not one line.** Pull the
  per-role, per-phase provisioning milestones from wd-extend-lifecycle
  `references/customer-technical-roles.md` and put them on THIS table (and the project
  plan) - provisioning early enough that each counterpart can learn the tool before
  their workstream needs output is the point; a single "grant access" row at go-live
  misses it.

### 2. Decision calendar

Derived from the design-session plan: the decisions the client will be asked to make,
roughly when, and who should be in the room for each (decision-makers, not observers -
the sign-off cadence in `SKILL.md` section Design-review cadence). Clients who see the
decision load up front staff the sessions properly; clients who don't send observers
and re-litigate later.

### 3. Long-lead standing asks (flag on page one)

The items that gate everything and take weeks when they go wrong - pull them out of
the table and repeat them up front:

- Security-admin turnaround (drives every ISU/domain-grant, every tenant)
- Client security-office / incident-notification contact (name + channel + after-hours
  path), captured at kickoff - this is the notification chain **wd-post-go-live**
  references/managed-services.md invokes for security incidents; hunting for the
  contact during an incident is the failure mode this row prevents
- Test users provisioned (real client accounts - consultant accounts are not UAT,
  per **wd-testing** references/uat-support.md entry criteria)
- Sample/real data extracts (real transactions, not templates - wd-discovery)
- Sign-off SLAs: how long the client needs to turn a design sign-off, a UAT
  acceptance, a go/no-go

### 4. Kickoff "what to expect" note (template)

A short customer-voiced cover note issued with the packet - voice rules per
**wd-comms** SKILL.md (plain register, lead with the ask, no unadopted jargon):

> Over the next ~N weeks we'll take <app> from design to live. Here's the shape:
> [3-5 phase bullets with rough dates]. Your team's commitments are in the attached
> table - the first three are needed by <date>. You'll get a status note every
> <weekday>; decisions we need from you will always arrive as "[Decision needed]"
> emails with options and a recommendation, never as surprises in a meeting.

## Re-issue at each phase gate

The packet is not a one-time kickoff artifact - re-issue a refreshed version at each
gate, because what's needed changes:

| Gate | What the refresh adds/retires |
|---|---|
| Design sign-off | Retire discovery asks; add build-phase items (SME availability for demos, security-group population) |
| UAT entry (-2 wks) | Named testers + hours + manager cc (the T-2-weeks tester ask - **wd-testing** references/uat-support.md), test-data confirmation |
| Cutover | Go-live-week asks: freeze-window approval, champion/office-hours staffing (**wd-post-go-live** references/adoption-and-feedback.md), day-of contacts |

Unmet items from the prior issue carry forward visibly - they don't get a fresh date
without a conversation (same aging discipline as actions in `SKILL.md`).

## Boundaries

- Internal tracking of the same items -> the kickoff checklist (**wd-extend-lifecycle**)
  and the RAID log (`raid-log.md`); this packet is the client-facing render.
- Message voice/formatting for the cover note -> **wd-comms**.
- Tester-ask specifics -> **wd-testing** references/uat-support.md.
