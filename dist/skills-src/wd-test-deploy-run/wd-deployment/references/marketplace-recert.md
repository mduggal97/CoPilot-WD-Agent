# Marketplace Re-Certification - Enhancing an Already-Shipped BoW App

This reference owns the **enhancement** lifecycle of a product that is **already
live on the Workday Marketplace / Built-on-Workday (BoW) catalog**: versioning
the shipped app, deciding whether a change forces **re-submission to Workday**,
re-running the production-approval gate for the delta, updating the public
listing, and promoting the enhancement across tenants and existing subscribers.

Initial go-live (first questionnaire, first listing, first program admission) is
covered elsewhere - this file starts on the day someone says *"the app is live,
now we're changing it."*

## Scope boundaries (respect these)

- **Initial listing / program-application content** (Marketplace catalog fields,
  taxonomies, imagery checklist, BoW Program Application market case) - owned by
  **bow-sales-enablement** (`references/marketplace-listing.md`,
  `references/bow-program-application.md`). This file only says *which* of those
  fields a re-cert updates and defers the field mechanics there.
- **Promotion mechanics** (DEV -> IMPL -> SBX -> PROD, one-way promotion, the
  "app is not the whole deployment" bundle, the per-tenant re-setup matrix) -
  owned by `references/promotion-and-environments.md`. Do not restate.
- **The two gating docs' cell-level content** - owned by
  `references/volumes-questionnaire.md` and `references/perf-testing-template.md`.
  This file says *when* a re-cert re-triggers them; those files say how to fill.
- **.xlsm / .docx file mechanics** -> xlsx / docx skills. **Yellow-highlight
  open-items convention** -> wd-design-doc.

## Product versioning for a shipped app

A shipped BoW app carries a **product version** distinct from the wdcli app
version number. Adopt semantic-style versioning and record it in one place the
whole enhancement traces to:

- **MAJOR** - new capability, new API surface, new integration, or a breaking
  change to a business object / attribute contract that existing subscribers
  consume. Forces re-certification (see triggers below).
- **MINOR** - additive, backward-compatible enhancement (a new optional config
  attribute, a new optional section, an added report) that does not add a
  Workday API surface or change security. Usually a listing "version notes"
  refresh, not a full re-submission.
- **PATCH** - bug fix, copy change, cosmetic PMD tweak. No re-cert, no listing
  change beyond an optional changelog line.

The **design-doc version is the anchor** - the Perf Testing header F4 already
tracks it precisely so a resubmission can be tied to a design version (see
`perf-testing-template.md` section header block). Bump the design-doc version on every
enhancement and carry the same number onto the questionnaire, the listing
version notes, and the release notes so all four agree.

## What triggers re-certification vs. what doesn't

Re-certification = re-running Workday's production-approval gate (a **new/updated
Volumes Questionnaire, and Perf Testing when thresholds move**) via a Workday
Customer Care case, per the SKILL.md "production-approval process" body. The
"bump and resubmit if the design changes materially" rule there is the governing
principle - this table makes it concrete for a shipped product.

| Change | Re-submit to Workday? |
|---|---|
| **New Workday API surface** (a SOAP op, RaaS report, WQL path, or REST endpoint the app did not previously call) | **Yes** - the API inventory is the single most common gap (`volumes-questionnaire.md` section API inventory); a new surface must be declared. |
| **New integration** (a new outbound/inbound INT, especially an external REST/OAuth call) | **Yes** - new load and a new dependency to declare; treat as a new use-case row on Perf Testing. |
| **New security domain(s)** the enhancement secures | **Yes** - re-run the gate and the per-tenant security setup for the new domains. |
| **Order-of-magnitude volume change** (new user population, new bulk path) | **Yes** - may cross the ~50K thresholds (50,000 active Extend workers / ~50K annual transactions) that drive whether Perf Testing is even required (`volumes-questionnaire.md` threshold logic). |
| **Breaking change** to a BO/attribute existing subscribers read | **Yes** - plus a subscriber-impact plan (below). |
| Additive optional attribute/section, no new API/security, volumes unchanged | **No** - listing version-notes refresh only. |
| Bug fix / copy / cosmetic PMD change | **No.** |

When in doubt, treat it as a re-cert - a rejected under-declared case costs more
than an unnecessary resubmission.

**Framed example (illustrative - client literals stay out of the instruction
voice):** an existing card/expense Marketplace app was enhanced under a client
SOW with additive config (read-only section control, attestation, attachments)
*and* a brand-new external real-time REST card-issuing integration (an
OAuth2/mTLS call to a card network). The additive config alone is a
MINOR/listing refresh; the **new REST integration is the trigger** - the
enhancement note recorded that it *"likely requires re-submission to Workday."*
That is exactly the "new API surface + new integration" row.

**Bespoke single-client live apps - (!) confirm.** Whether Workday's
production-approval gate re-triggers for an update to a client's OWN
(non-Marketplace) live Extend app has not been practitioner-confirmed - the
only evidence on file is that enhancement note's "likely requires
re-submission." **Conservative default: assume yes** - treat any bespoke-app
change matching the trigger table above (new API surface, new integration, new
security domains, order-of-magnitude volume change, breaking BO change) as
requiring an updated Volumes Questionnaire / Customer Care case, and plan the
same 4-6-week lead time. Confirm with Workday (via the app's existing case)
before relying on a "no re-cert needed" answer; record the confirmed answer
here.

## The re-approval checklist (for the delta only)

Submit **4-6 weeks ahead of the enhancement's move-to-production**, same lead
time and same Customer Care case discipline as an initial go-live (SKILL.md
section process mechanics). Reopen the app's existing case or open a new one referencing
the prior case.

- [ ] **Design doc versioned** and the enhancement's new objects/attributes/APIs
      documented (wd-design-doc; carry the new version to F4).
- [ ] **Volumes Questionnaire updated** - add the new API surfaces to the API
      inventory, revise any changed volumes with basis, re-check the
      50,000-active-worker threshold (`volumes-questionnaire.md`). Never overwrite the formula-driven
      Recommendations tab.
- [ ] **Perf Testing updated *when thresholds change*** - add a use-case row for
      each new code path / integration; re-execute if the change pushes the app
      over ~50K annual transactions, or if program practice requires it even
      under threshold (`perf-testing-template.md`). Route executed testing
      through the Perf Test Lead.
- [ ] **Listing content refresh** (bow-sales-enablement `marketplace-listing.md`)
      - Key Features / Key Benefits for the new capability, **Works With** if the
      enhancement adds a Workday product dependency, updated imagery/screenshots
      for changed UI, and **version notes / changelog**. Every new quantified
      benefit needs a Public claims-register row.
- [ ] **Program Application market facts** - only if the enhancement changes the
      addressable-market or premier-app case (bow-sales-enablement
      `bow-program-application.md`); most enhancements don't touch it. Keep the
      twinned facts (one-liner, category, Works-With) from drifting between the
      listing and the program app.
- [ ] **Release notes** for existing subscribers (what changed, opt-in vs.
      automatic, any action required).

## Coordinating the enhancement across tenants (promote the delta)

The enhancement is a **new app version promoted through the same DEV -> IMPL ->
SBX -> PROD path**, one-way, with the full promotion bundle - pull all mechanics
from `promotion-and-environments.md`; do not restate. Enhancement-specific notes:

- **Promote the delta as a bundle.** A new integration or RaaS report added by
  the enhancement **promotes separately from the app version** and must be
  re-created/registered in every tenant (`promotion-and-environments.md` section "the
  app is not the whole deployment").
- **Re-run per-tenant setup for what the enhancement adds** - new security
  domains, a new ISU/ISSG or API client for a new external REST integration, new
  App Attributes - in each tenant. Promotion carries none of it (the re-setup
  matrix). Front-load the client security-admin requests (1-2 weeks each).
- **Validate in SBX right before go-live** - SBX is refreshed weekly from PROD,
  so it is the prod-like check for the delta, not a durable stage.
- **Fix forward.** Promotion is one-way; a bad enhancement version is corrected
  with a newer version, never a demote - matters more here because PROD already
  has live subscribers on the prior version.

## Enhancement rollback - designed, not improvised

Promotion is one-way (`cutover-planning.md` says it for go-lives; it is just as
true for enhancements), so "rollback" for a live app means **roll forward to a
corrected version or redeploy the prior version as a new version** - and both
only work if you prepared before promoting.

- **Pre-promotion snapshot rule.** Before ANY enhancement deploy to PROD,
  archive the exact deployed source (`wdcli app download` of the live version)
  plus the design-doc version it implements, labeled with the product version.
  Without the snapshot, "redeploy the prior version" is an archaeology project
  during an incident.
- **Schema-change reversal analysis, per change.** New BO fields **cannot be
  un-added**, and data written to them survives a code rollback. Before
  promoting, state one of: (a) a **data-reversal plan** (which records/fields
  get corrected or nulled, by what mechanism, PATCH-preferred), or (b) an
  explicit **roll-forward-only decision** on record - "if this version is bad,
  we fix forward; the prior version cannot be safely restored over the new
  data." Silence is choosing (b) without telling anyone.
- **Roll-forward vs redeploy-prior: decide the criteria and the decider in
  advance** - mirror `cutover-planning.md`'s abort-criteria pattern (severity
  thresholds + one named decision-maker). Default shape: data-corrupting or
  security-exposing defect -> redeploy prior version (if the reversal analysis
  said it's safe); functional defect with a workaround -> roll forward on the
  normal cadence. The call belongs to the same role that owns go/no-go, not to
  whoever is on the incident bridge.
- For a Marketplace app, either path is itself a **version event**: subscribers
  on the bad version need release notes for the corrective version, and the
  listing version notes must not skip it.

## Backward-compatibility & existing-subscriber impact

The enhancement lands on tenants that are **already running the prior version in
production**. Before promoting to PROD:

- **Default to additive + opt-in.** New config attributes should default to the
  prior behavior so an existing subscriber who does nothing sees no change
  (e.g., a new "enable attestation" flag defaults off).
- **Breaking BO/attribute changes need a migration plan** - data backfill,
  a deprecation window, and subscriber comms; never silently repurpose a field
  existing subscribers read.
- **Regression the existing paths, not just the new one** - the enhancement must
  not break shipped functionality (wd-testing owns the evidence).
- **Communicate the version bump** - release notes + go-live comms to subscribed
  tenants; coordinate managed-services support on the new version.

## Standing program obligations ((!) open questions - ask the partner manager)

A live Marketplace/BoW listing carries **standing obligations that run even when
the app never changes** - but their exact terms are program facts held by
Workday, not something to assert from memory. Per this file's honest pattern,
frame each as an (!)-open question to the **Workday partner manager** (the
program-application fact grid names one - bow-sales-enablement
`references/bow-program-application.md`), get the answer in writing, and record
it here:

- (!) **Periodic listing/re-certification cadence** - does the program require a
  periodic re-attestation or listing recert **independent of app changes**
  (annual review, program renewal), on top of the change-triggered re-certs this
  file covers? If yes: cadence, artifact, and who submits.
- (!) **Publisher support expectations** - what response/coverage does Workday
  expect behind the listing's public support contact? Wire the answer into the
  managed-services SLA model (wd-post-go-live `references/managed-services.md`)
  so the contracted support tier actually meets the program bar.
- (!) **Partner-scorecard metric refresh** - the program application's fact grid
  carries C-Sat, Extend Activity, deployments, Extend-dev counts. How often does
  Workday refresh/re-request these, and from what source? Treat a confirmed
  refresh cycle as a trigger to update the fact grid (bow-sales-enablement owns
  the grid; this file owns knowing the trigger exists).
- (!) **Listing-content review cycle** - does Workday periodically re-review
  listing content (claims, imagery, Works-With) outside of publisher-initiated
  updates? If yes, align the claims-register review (bow-sales-enablement) to
  that cycle.

Until answered, the conservative default is to behave as if all four exist:
refresh the listing and fact grid at least annually and keep the support
contact's inbox monitored.

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them
from the current engagement's project-memory file, ask the user, or discover
live:

- **Move-to-production windows + tenant path** - the enhancement follows the
  same windows and tenant path as initial go-lives (see
  `promotion-and-environments.md` / SKILL.md Engagement inputs).
- **Volume posture vs. the thresholds** - whether the program's apps run under
  Workday's gates (50,000 active Extend workers / ~50K annual transactions); a
  re-cert still refreshes the questionnaire and completes Perf Testing per
  program practice even when under threshold.
- **Perf Test Lead** - the named person to route executed perf testing through.

If a value isn't in memory, ask. For branded output, use neutral formatting
(no firm brand skill is installed).
