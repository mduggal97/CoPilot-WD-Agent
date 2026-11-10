# Release management - versioning and deprecation for a customer product

Reference for `product-operations`. An internal accelerator can ship a breaking change on a
Tuesday because the whole user base is one Slack message away. A customer product cannot -
someone integrated against your API, someone built a workflow around a UI that just moved,
and nobody warned them. This file is self-contained: read it without having read anything
else in the suite.

This is the discipline layer above `app-hosting/references/operations.md`, which owns the
deploy MECHANICS (the two-account pipeline, migration safety, prod rollback). This file owns
what you PROMISE the customer about how the product changes over time, and it reuses
operations.md's mechanics rather than redefining them - especially the expand-contract
migration discipline and the retag-based prod rollback.

## Table of contents

- [Versioning (semver)](#versioning)
- [The customer-visible changelog](#changelog)
- [Backward compatibility](#backward-compat)
- [Deprecation notice windows](#deprecation)
- [Maintenance windows](#maintenance-windows)
- [Staged and canary rollout](#staged-rollout)
- [Rollback - tie-in to app-hosting](#rollback)
- [What to remember](#remember)

---

<a name="versioning"></a>
## 1. Versioning (semver)

**Use semantic versioning (MAJOR.MINOR.PATCH) for anything a customer integrates against** -
a public API, an SDK, a downloadable client, an exported schema
(https://semver.org/):

- **MAJOR** - a breaking change (a removed field, a changed auth mechanism, an incompatible
  response shape). Bumping MAJOR is itself the signal to a customer: "read the changelog
  before you upgrade."
- **MINOR** - backward-compatible new functionality (a new endpoint, a new optional field).
- **PATCH** - backward-compatible bug fixes.

**A pure SaaS UI product with no public API can version more loosely** (a date-stamped
release, a simple release-number) - semver's discipline matters most where a customer's OWN
code depends on your interface staying stable. If the product exposes an API, an SDK, or a
webhook payload schema, apply semver strictly to that surface even if the UI itself ships
continuously.

**Never reuse a version number, and never silently change what a released version means.**
A customer or their tooling may have pinned to a specific version; a version number is a
promise about a fixed set of behavior, not a label you can repaint.

---

<a name="changelog"></a>
## 2. The customer-visible changelog

**Every customer-visible change gets a changelog entry, written for the customer, not the
engineering team.** This mirrors the three-field release-notes pattern wd-kt uses for a
Workday app's enhancements (what changed / opt-in vs. automatic / action required) -
deliberately, so the discipline is consistent across both tracks:

| Field | Answers |
|---|---|
| What changed | Plain-language description, not a commit message or a Jira ticket title |
| Opt-in vs. automatic | Does the customer have to do anything to get this, or does it just show up |
| Action required | If anything - a config change, a re-authorization, nothing |

**Group entries by release, dated, newest first.** Tag each entry Added / Changed /
Fixed / Deprecated / Removed / Security (the "Keep a Changelog" convention -
https://keepachangelog.com/ - is a reasonable, widely recognized shape to start from;
INSPIRATION, not a template to copy verbatim).

**A breaking change gets flagged loudly in the changelog, not buried in a MINOR-looking
entry.** If the entry describes a MAJOR-version change, say "BREAKING" in the entry itself -
do not make the customer cross-reference the version number to realize their integration is
about to fail.

---

<a name="backward-compat"></a>
## 3. Backward compatibility

**The default posture: new versions are additive, and existing integrations keep working
without the customer taking action.** This is the same expand-contract instinct
`app-hosting/references/operations.md` section 1 applies to database migrations, applied one
level up to the customer-facing interface:

- Add new fields/endpoints without touching existing ones.
- Never repurpose a field's meaning - add a new field instead.
- Support at least N-1 (the previous major version) for API consumers for a stated window
  (see deprecation windows below) so a customer is never broken by a release they did not
  explicitly opt into.

**When a breaking change is unavoidable**, it goes through the deprecation process below
rather than shipping as a surprise inside a MINOR or PATCH release. A breaking change hidden
in a non-major version is a trust failure the customer will remember at renewal.

---

<a name="deprecation"></a>
## 4. Deprecation notice windows

**State a minimum notice period before a deprecated capability is removed, and hold it.**
There is no single universal number - it depends on the product and the customer base's
integration depth - but the discipline is the same regardless of the chosen window:

1. **Announce** the deprecation in the changelog and (for API/integration surfaces) via a
   direct notification to affected customers, not just a changelog line they may not read.
2. **State the removal date explicitly**, not "in a future release" - a customer needs a
   date to plan a migration against.
3. **Keep the deprecated capability functioning, possibly with a warning header/response
   field, for the full notice window** - do not remove it early because "we already told
   them."
4. **Provide a migration path** - what replaces the deprecated capability and how to move to
   it, not just notice that it is going away.
5. **Remove on schedule** and note the removal in the changelog as a MAJOR-version change if
   it affects the versioned surface.

A common industry pattern for API deprecation notice is measured in months, not weeks, for
an enterprise-sold product - size the window to how embedded the capability likely is in a
customer's own systems, and err longer for an enterprise tier than a self-serve one.

---

<a name="maintenance-windows"></a>
## 5. Maintenance windows

**A planned maintenance window is excluded from the uptime SLA (sla-and-support.md) only if
it is announced with adequate lead time and scheduled to minimize customer impact.** State,
in the SLA and in customer communication:

- **Advance notice** - a stated minimum (e.g., 48-72 hours for routine maintenance; longer
  for anything with expected customer-visible downtime).
- **Preferred timing** - lowest-traffic window for the customer base, not the vendor's
  convenience; for a multi-region customer base this may mean there is no single "off
  hours" and a canary/rolling approach (below) is preferable to a hard maintenance window at
  all.
- **What "maintenance" covers** - a routine RDS patch, a scheduled migration, a planned
  capacity change - vs. what does NOT count as maintenance (an unplanned incident is an
  incident, not maintenance, and does not get the SLA exclusion).

Where the underlying platform supports zero-downtime deploys (App Runner's rolling
deployment behavior, per `app-hosting/references/aws-architecture.md` /
`cloudformation-pipeline.md`), prefer that over a customer-visible maintenance window
entirely - reserve announced windows for changes that genuinely require one (a database
engine version upgrade, a breaking infra change).

---

<a name="staged-rollout"></a>
## 6. Staged and canary rollout

**Ship risky changes to a small slice of traffic or customers before the whole base sees
them.** This is the practical way to keep an error budget (sla-and-support.md section 7)
intact while still shipping: a bad change is caught against 5 percent of traffic, not 100
percent.

- **Canary by traffic percentage** - route a small percentage of requests to the new version,
  watch the same alarms `app-hosting/references/observability.md` section 4 already defines
  (5xx rate, latency, agent-failure rate), and only promote to full traffic once the canary
  is clean for a stated bake time.
- **Staged by customer segment** - roll out to an internal/beta customer cohort first, then a
  named early-adopter tier, then general availability. Fits a product with distinct
  self-serve vs. enterprise tiers, where an enterprise customer would rather NOT be the
  first to see a change.
- **Feature flags** - decouple deploy from release: the code ships to production but stays
  off until a flag is flipped, which allows instant rollback of the FEATURE without an image
  rollback. Useful for any change riskier than a pure bug fix.

**Communicate a beta/early-access designation honestly.** A feature behind a canary or a
beta flag should be labeled as such to the customers who see it early, with an explicit note
that its SLA/support commitment may differ (e.g., best-effort until general availability).

---

<a name="rollback"></a>
## 7. Rollback - tie-in to app-hosting

**Do not redefine rollback mechanics here - this file's job is to say WHEN a release
decision invokes them and what to tell the customer.** The actual mechanic (retag the
previous good prod image to `:latest`, then `start-deployment` - there is no prior-SHA
redeploy in prod because the org-wide SCP denies `apprunner:UpdateService`) is owned by
`app-hosting/references/operations.md` section 3.

**The release-management-side rule that makes that mechanic SAFE:** a release is only
freely rollback-safe if its database migration was additive (expand-contract, operations.md
section 1). Before shipping any release that pairs a schema change with new code, confirm
which of the three expand-contract phases (expand / migrate-and-switch / contract) it is -
only a contract-phase release burns the rollback bridge, and that should be a deliberate,
isolated decision, not an accident discovered mid-incident.

**Customer communication on a rollback:** if a rollback is customer-visible (a feature that
was live disappears, or behavior reverts), say so in the status page and/or changelog - a
silent rollback that a customer notices independently reads as either a bug or a cover-up.

---

<a name="remember"></a>
## What to remember

- Semver strictly on any surface a customer integrates against; a UI-only product can
  version more loosely, but its API/webhook/export surfaces still get semver.
- Every customer-visible change gets a changelog entry in the three-field shape (what /
  opt-in-vs-automatic / action-required); breaking changes are flagged loudly, not buried.
- Default posture is additive/backward-compatible; breaking changes go through a stated
  deprecation window with a real migration path, never shipped as a surprise inside a minor
  release.
- Maintenance windows are announced with adequate lead time and excluded from the SLA only
  when announced properly; prefer zero-downtime deploys over a window at all where the infra
  supports it.
- Canary/staged rollout catches a bad release against a slice of traffic or customers before
  it reaches everyone, protecting the error budget.
- Rollback mechanics live in app-hosting operations.md; this file's job is knowing WHEN a
  release is safe to roll back (expand-contract discipline) and how to tell the customer
  when a rollback is visible to them.
