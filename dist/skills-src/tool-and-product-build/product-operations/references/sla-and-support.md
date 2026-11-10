# SLA and support - the promise you make to a paying customer

Reference for `product-operations`. Once a customer pays for a hosted product, "best
effort" is no longer the posture (that is the internal-accelerator posture per
product-strategy's disposition-gate.md) - a customer product needs a written SLA, a real
support channel, and an incident discipline a stranger could execute at 2am. This file is
self-contained: read it without having read anything else in the suite.

Why this gets its own file, not a paragraph in app-hosting: app-hosting's
`references/observability.md` and `references/operations.md` tell you HOW to detect and
recover from a production problem (alarms, rollback mechanics). This file tells you what you
PROMISE the customer around that mechanism, and how you run the human side of an incident -
severity, escalation, communication, postmortem. The infra can be perfectly healthy and the
SLA still broken if nobody told the customer anything for six hours.

## Table of contents

- [Uptime SLA tiers](#uptime-tiers)
- [Incident severity definitions (Sev1-4)](#severity)
- [Support channels and hours](#support-channels)
- [Escalation and on-call rotation](#escalation)
- [Status page](#status-page)
- [Incident runbook](#incident-runbook)
- [Postmortem discipline](#postmortems)
- [Error budgets](#error-budgets)
- [What to remember](#remember)

---

<a name="uptime-tiers"></a>
## 1. Uptime SLA tiers

State uptime as a percentage measured over a stated window (monthly is standard), define
what counts as downtime, and name the exclusions - a target with no exclusions is a target
nobody can actually hold.

| Tier | Typical target | Allowed downtime / month | Fits |
|---|---|---|---|
| Best-effort | No numeric target | - | Free/trial tier, early-access product |
| Standard | 99.5 percent | ~3h 39m | Most SMB-priced SaaS tiers |
| Business | 99.9 percent | ~43m | Mid-market / Pro tier |
| Enterprise | 99.95 - 99.99 percent | ~22m - ~4m | Enterprise tier, usually with a credit remedy |

**"Nines" math is a real design constraint, not a marketing number.** 99.9 percent allows
roughly 43 minutes of downtime a month; 99.99 percent allows roughly 4 minutes. Going from
99.9 to 99.99 is not a 0.09-point tweak - it typically means multi-AZ, automated failover,
and a much stricter change-management process. Do not promise a nines tier the underlying
app-hosting posture cannot hold; check the deploy/rollback posture in
`app-hosting/references/operations.md` before committing to a number. The AWS Well-Architected
Framework's reliability pillar frames this as designing for the failure modes your target
implies, not just hoping the infra holds
(https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html). The AWS
Well-Architected SaaS Lens applies the same reliability thinking specifically to a
multi-tenant SaaS control plane and per-tenant isolation
(https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/saas-lens.html) - read it
before quoting an availability number for a multi-tenant product.

**Define downtime precisely.** Typical definition: the percentage of total minutes in the
billing period during which the core service returns a non-error response within an agreed
latency threshold, EXCLUDING scheduled maintenance (announced per release-management.md),
customer-caused outages, and force majeure. Write the definition into the SLA document
itself - a vague "uptime" promise is unenforceable and invites a dispute at renewal.

**Credits, not refunds, are the standard remedy.** Most SaaS SLAs remedy a miss with a
service credit (a percentage of the period's fee) against a future invoice, not a cash
refund - keep this consistent with whatever wd-contracts drafts into the SaaS agreement;
this file states the operational target, the contract states the legal remedy.

---

<a name="severity"></a>
## 2. Incident severity definitions (Sev1-4)

Carry a numbered severity scale so a support ticket and an internal incident conversation
share one vocabulary. This mirrors the Sev1-3 scale wd-post-go-live uses for a Workday app's
hypercare/managed-services phase - deliberately, so the discipline transfers - extended to a
4th tier for a customer product's higher ticket volume.

| Severity | Definition | Target response | Target resolution |
|---|---|---|---|
| Sev1 - Critical | Product down or unusable for all/most customers, data loss or corruption, a security incident | Immediate, all-hands, page on-call | Workaround ASAP; fix on the next safe deploy |
| Sev2 - High | Major feature broken or blocked for a customer, no workaround, or degraded for many customers | Within the tier's response SLA (below) | Within the tier's resolution SLA |
| Sev3 - Medium | Feature broken with a workaround, affects a subset of customers | Next business day | Next scheduled release |
| Sev4 - Low | Cosmetic, minor, or an enhancement request | Logged, triaged at the regular backlog review | Backlog / roadmap |

**Response vs. resolution are two different clocks.** Response is "a human acknowledged
this and is working it." Resolution is "the issue is fixed or worked around." Quote both
separately in the SLA - a fast-response/slow-resolution promise and a slow-response/
fast-resolution promise read very differently to a customer even at the same headline
percentage.

**Security incidents get pulled out of the severity scale, not folded in.** A "cosmetic"
data-visibility bug is still a security incident even though it would score Sev3/4 on
functional impact. Triage question at intake: does this involve access, credentials, or
data reaching someone/somewhere it should not? If yes, treat it as Sev1 regardless of
functional severity, and run it against the breach-notification duties in
`compliance-ops.md` in parallel with the technical fix.

---

<a name="support-channels"></a>
## 3. Support channels and hours

State three things explicitly per pricing tier, because "support" alone is not a
commitment:

1. **Channel** - ticketing system, email, chat, phone, a named Slack/Teams connect channel.
   More channels for higher tiers is a common differentiator (see `billing-and-metering.md`
   for tying this to entitlements).
2. **Coverage hours** - business hours in a named time zone, extended hours, or 24x7. Name
   the time zone explicitly; "business hours" alone is ambiguous across a customer base.
3. **Named contacts** - require the customer to designate a primary and alternate support
   contact authorized to open tickets. This keeps ticket volume attributable (useful for the
   health-scoring signal in `customer-success.md`) and prevents side-channel escalations that
   bypass the queue.

Do not promise a channel or hour coverage the support team cannot actually staff -
under-delivering on a stated support hour is worse than not stating one.

---

<a name="escalation"></a>
## 4. Escalation and on-call rotation

**A rotation needs an unambiguous handoff, or "on-call" is a name with no one behind it.**
At minimum, define:

- **Primary and secondary on-call**, with a defined handoff time and a paging tool (do not
  rely on a person checking a channel voluntarily).
- **An escalation path with a time-boxed trigger** - e.g., if Sev1 is not acknowledged in 15
  minutes, page the secondary; if not resolved or mitigated in an hour, pull in engineering
  leadership. Write the trigger as a clock, not a feeling.
- **A single incident commander per active Sev1/Sev2** - one person owns the incident's
  decisions and communications; everyone else executes or advises. Splitting ownership mid-
  incident is a common cause of slow, contradictory customer updates.

Tie the paging mechanism to the alarms already defined in
`app-hosting/references/observability.md` section 4 (the four alarms that page: 5xx/health,
latency, agent failure rate, spend burn) - those alarms are the automated trigger for the
human rotation above; this file is the human process that receives the page, not a
replacement for it.

---

<a name="status-page"></a>
## 5. Status page

**A public status page is the first thing an anxious customer checks during an outage -
if you do not have one, they open a ticket instead, adding load exactly when the team is
busiest.** A status page needs, at minimum: current status per component, an incident
timeline with timestamped updates, and a subscribe mechanism (email/RSS/webhook) so
customers do not have to poll it.

Two build approaches, in increasing cost/control:

- **Hosted status-page product** (e.g., Atlassian Statuspage, a comparable SaaS) - fastest
  to stand up, independent infra from the product itself (important: if your product's own
  infra is down, the status page must not be, or it is useless exactly when needed)
  (https://www.atlassian.com/software/statuspage).
- **Self-hosted, on separate infrastructure** - more control, more to build and keep
  running; only worth it once status-page needs outgrow what a hosted product offers.

**The independent-infra rule is non-negotiable regardless of approach.** A status page
hosted on the same App Runner service or the same AWS account/region as the product goes
down with the product. Host it separately (a different provider, or at minimum a different
account/region with no shared dependency).

**Update cadence during an active incident:** commit to a stated cadence (e.g., an update at
least every 30 minutes for a Sev1, even if the update is "still investigating") - silence
reads as "no one is working on it" even when someone is.

---

<a name="incident-runbook"></a>
## 6. Incident runbook + postmortem discipline

**The runbook is the checklist a half-awake on-call engineer follows without having to
think.** Shape:

1. **Detect** - an alarm fires (observability.md) or a customer reports it.
2. **Triage** - assign severity (section 2), confirm scope (one customer vs. all).
3. **Declare** - open an incident record, name an incident commander (section 4), post the
   first status-page update (section 5) for a Sev1/Sev2.
4. **Mitigate** - the fastest safe path to restoring service; this is where
   `app-hosting/references/operations.md` section 3 (prod rollback - retag the previous good
   image, `start-deployment`) is the concrete mechanic for a bad-deploy-caused incident. A
   mitigation is not the same as a root-cause fix - ship the mitigation first.
5. **Resolve** - confirm the fix, close the status-page incident with a final update.
6. **Postmortem** - see below. Every Sev1, and every Sev2 that recurs, gets one.

<a name="postmortems"></a>
### Postmortem discipline

**Blameless, written, and time-boxed.** A postmortem that assigns blame teaches people to
hide problems, not surface them - the goal is a system fix, not a person to point at. Shape:

- **Timeline** - what happened, when, in the order it was learned (not the order it makes
  the team look best).
- **Root cause** - the actual mechanism, not just "a bad deploy." If the deploy was bad
  because a migration was non-additive, say so and tie it to the expand-contract discipline
  in `app-hosting/references/operations.md` section 1.
- **Customer impact** - who was affected, for how long, and whether an SLA credit is owed
  (feed to billing-and-metering.md).
- **Action items with owners and dates** - not "we will be more careful." A postmortem with
  no action items is a story, not a fix.

Publish a customer-facing summary for any incident that breached the SLA or affected
multiple customers - a short, honest account (what happened, impact, fix, prevention) builds
more trust than silence. Keep the internal postmortem more detailed than the customer-facing
one; do not publish internal blame-adjacent detail externally.

---

<a name="error-budgets"></a>
## 7. Error budgets

**An error budget turns "99.9 percent uptime" from a lagging scorecard into a forward
operating rule.** If the SLA target is 99.9 percent, the error budget for a 30-day month is
the inverse: about 43 minutes of allowed unreliability. Track consumption against that
budget continuously (Google's SRE book popularized this framing:
https://sre.google/sre-book/embracing-risk/).

**The operating rule the budget buys you:** while budget remains, the team can ship features
and take calculated risk (a canary rollout, a riskier migration). Once the budget is
exhausted for the period, the team's priority shifts to reliability work (bug fixes,
hardening, paying down the incidents that burned the budget) until it recovers. This gives
engineering leadership an evidence-based way to say "no more feature risk this month" that
is not just a gut call - and it gives a customer-facing team a number to point to when
asked "are you meeting the SLA" before the month closes.

Tie the budget's real-time consumption to the same telemetry app-hosting already produces
(the `5xxStatusResponses` and health-check metrics in observability.md section 3) rather
than building a second measurement pipeline.

---

<a name="remember"></a>
## What to remember

- State uptime with a precise definition and named exclusions, sized to what the app-hosting
  posture can actually hold - do not promise nines the infra cannot back.
- Sev1-4 with separate response and resolution clocks per tier; pull security incidents out
  of the functional severity scale entirely.
- Support channel, hours, and named contacts stated per tier, staffed as promised.
- On-call needs a defined handoff, a time-boxed escalation trigger, and one incident
  commander per active incident - tied to the existing observability alarms, not a parallel
  system.
- A status page lives on independent infrastructure from the product itself, with a stated
  update cadence during an incident.
- Every Sev1 (and repeat Sev2) gets a blameless postmortem with owned action items; publish
  a customer-facing summary for SLA-breaching or multi-customer incidents.
- An error budget converts the uptime target into a real-time operating rule, not just a
  monthly scorecard.
