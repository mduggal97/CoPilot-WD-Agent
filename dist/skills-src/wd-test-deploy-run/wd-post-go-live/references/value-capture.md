# Value Capture - proving the app was worth building

The app shipping is not the outcome; the outcome is the metric moving. This reference owns the value-measurement loop: baseline it at discovery, lock it at design sign-off, check it at 30/60/90 days, snapshot it at closeout, and harvest it into sales assets. **A KPI without a baseline is a wish** - this whole reference exists to prevent that.

It also owns the **CSAT pulse** definition (section 4). `adoption-and-feedback.md` consumes it; do not redefine it there or anywhere else.

## 1. Baseline at discovery - the requirement

Name **3-5 outcome metrics per app** during discovery, captured alongside the volume questions discovery already asks (wd-discovery owns the intake mechanics - this is a content requirement it carries):

- Candidate metrics: cycle time (request -> completion), hours saved per period, error/rework rate, volume shifted off the legacy path, compliance/audit findings avoided.
- Each metric gets a **measurement source** at capture time: where the current-state number comes from (legacy report, manual log, client's own estimate - label estimates as estimates).
- No source, no metric - swap it for one the client can actually measure. Three measurable metrics beat five aspirational ones.

## 2. Design sign-off - lock the KPI table

At design sign-off, every KPI on the design doc's **KPI & Reporting tab** (wd-design-doc owns the tab) carries four filled cells:

| Column | Rule |
|---|---|
| Baseline | The discovery number, dated. Missing baseline = yellow-highlight open item, not a blank. |
| Target | Agreed with the process owner - a number and a by-when, not "improve." |
| Source | The app's OWN reporting where possible (its WQL/report/KPI page) - the app should measure itself; standard inclusion per wd-estimate proposal-content.md. |
| Review date | When actuals get compared to target (align to the 30/60/90 check-ins below). |

## 3. 30/60/90-day value check-ins

Three short check-ins from first production use (the first lands inside hypercare; run it alongside the daily monitoring, not instead of it):

- **Adoption**: active users vs licensed/target population; transaction volume vs the Volumes Questionnaire forecast - hypercare's volume-sanity monitoring (`SKILL.md`) already collects this, just read it against target.
- **KPI actuals vs target**: pull from the sources locked in section 2. Early reads are noisy - trend matters more than the day-30 number - when the source is WQL/RaaS, pull it via tenant-ops and file the query + timestamp with the snapshot (wd-extend-dev references/tenant-ops.md).
- **Output: a one-page value snapshot to the sponsor** each cycle - metric | baseline | target | actual | trend | one interpretation line. This is the same snapshot the sponsor one-pager consumes (wd-pm references/steering-committee.md pulls value-delivered from here by reference).
- A metric moving the wrong way is a finding, not a footnote: diagnose (adoption gap? training gap? design gap?) and route - adoption/training -> `adoption-and-feedback.md`, design gap -> enhancement backlog (`account-growth.md`).

## 4. CSAT pulse (owned definition)

A short satisfaction pulse - **5 questions max, 1-5 scale plus one free-text** - run at exactly two moments:

| Moment | Audience | Asks |
|---|---|---|
| Hypercare exit | End users + process owner | Ease of use, fit to the process, support responsiveness during hypercare, vs the old way, one thing to improve |
| Closeout | Sponsor | Outcome vs expectation, delivery experience, likelihood to recommend / build the next app with the firm, one thing to improve |

- Keep it lightweight - a form link, 3 minutes, anonymous for end users, attributed for the sponsor.
- Results route two ways: lessons learned (`handoff-and-closeout.md` closeout) and the renewal / managed-services conversation (`account-growth.md`, `managed-services.md`) - a strong sponsor pulse is the natural opening for the roadmap workshop.

## 5. Closeout gate additions

Two rows on the closeout checklist (`handoff-and-closeout.md` carries them):

- **Benefits snapshot delivered** - the final value snapshot (section 3 format, closeout-dated) handed to the sponsor. If targets aren't met yet because the review date hasn't arrived, deliver the trend-to-date and name the follow-up review date and owner.
- **Reference-rights ask made** - see section 6.

**Unmet KPIs become a named follow-up, never silence**: classify the gap (config change / training push / enhancement) and log it with an owner - enhancement-class gaps go to the backlog (`account-growth.md`); silence at closeout converts a measurable win-in-progress into a client's vague disappointment.

## 6. Sales-asset harvest - closeout is a sales event

Every closeout produces reusable proof. Do this while the sponsor is warm:

- **Reference-rights ask, scripted into the closeout meeting** (not an afterthought email): offer tiers - anonymized reference / named logo / quote / case study - and log the answer with **date + approver name**. A "not yet" gets a revisit date.
  - **Consent must be WRITTEN** - a confirmation email from the approver is the minimum artifact; a verbal yes in the meeting is a pending item until it's in writing. Consent is **tier-scoped** (a yes to "anonymized reference" is not a yes to "named case study" - record which tier was granted) and the artifact is **filed with the engagement record**, not left in an inbox.
  - **Before ANY named external use, cross-check the EXECUTED agreement's marketing-reference clause** (wd-contracts references/saas-agreement.md section 8.2 - the clause clients most often ask to strike). If section 8.2 was struck or modified in the executed copy, contract terms override the closeout consent conversation - resolve with legal before using the name. Mandatory, per use, not once.
- **Case-study one-pager**: challenge -> approach -> outcome (the section 5 benefits snapshot supplies the outcome numbers). Render with neutral formatting; content pattern here.
- **Claims-register feed**: each harvested metric is filed as a **bow-sales-enablement** claims-register row (references/claims-register.md) - arrives as `Confirm-Firm` with source = the closeout benefits snapshot + date, and follows that register's Confirm-Firm -> External-OK path (reference rights from this section gate the external status). Client-named rows carry a **consent-evidence pointer** - the written-consent artifact + date + tier and the section 8.2-checked confirmation, not just a status word. Never quote a client metric externally that hasn't cleared that gate.
- **Relevant-experience library**: append a short archetype-tagged summary (archetype per wd-estimate references/calibration.md, drivers, outcome metrics, reference status) that wd-estimate proposals pull from - the "we've done this before" paragraph should be an excerpt, not a memory exercise.

## Boundaries

- **Discovery intake mechanics** (how baselines get asked) -> **wd-discovery**; this reference defines what must come back.
- **KPI & Reporting tab format** -> **wd-design-doc**; this reference defines the four cells that must be filled.
- **Claims governance** (statuses, the external gate) -> **bow-sales-enablement** references/claims-register.md - feed it, never fork its rules.
- **Adoption interventions and feedback loops** -> `adoption-and-feedback.md` (consumes section 4's CSAT pulse); **roadmap/renewal use of these outputs** -> `account-growth.md`.
