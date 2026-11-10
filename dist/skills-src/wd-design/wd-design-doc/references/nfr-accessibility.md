# Non-functional requirements (NFRs) - the design-time checklist

Functional requirements say what the app does; NFRs say how well it must do it - and they're the recurring hole the suite's own gap-reports flag ("no error-handling standards, accessibility, or browser/device support anywhere"). This is a design-time checklist that feeds [gap-analysis.md](gap-analysis.md): each row is a thing to capture in the doc plus the "done" bar the gap sweep checks it against.

**Where NFRs live in the doc.** Most land on the **Technical Specification** tab (see [16-tab-spec.md](16-tab-spec.md) - orchestrations, limits, App Attributes already live there); the testable ones also get a numbered **Requirements** row ("the system shall...") so wd-testing can trace a scenario to them. Don't scatter them - one "Non-Functional Requirements" section on Technical Specification, cross-referenced from Requirements, is the pattern.

**How to use this.** Walk every category once per design review. For each: either the doc answers it, or it becomes a yellow open item with an owner (the standard SKILL.md yellow rule - a blank NFR table is the same defect as any other silently-blank table). Right-size the bar to the app: an internal single-institution app clears most rows with a short stated standard, not a workstream.

---

## 1. Accessibility (WCAG 2.1 AA basics for PMD)

PMD renders standard Workday UI, so most AA behavior is inherited - the design's job is to capture the app-specific choices that break it. Capture as a short "Accessibility" block on Technical Specification.

| Capture in the doc | "Done" bar for gap-analysis |
|---|---|
| Every input/picker/grid column has a real **label** (not placeholder-only); icon-only buttons carry accessible text | No input relies on placeholder or color alone to convey its meaning |
| **Keyboard-only** path through each primary flow works (tab order, OK/Cancel reachable) | Stated as a UAT check; no mouse-only interaction (e.g. hover-only reveal) in a required path |
| **Contrast** of any custom `richText`/status color meets AA (4.5:1 text, 3:1 large) | Custom status colors (the progress-bar/`richText` pattern in the pmd-gotchas reference of the wd-extend-dev skill, #38) listed with a contrast note; status never conveyed by color only - pair with text/icon |
| **Screen-reader** sensibility: table semantics, meaningful headings, error text tied to its field | Error messages are programmatic field errors (section 2), not just a banner a reader can't associate |

State the target explicitly (default: **WCAG 2.1 AA, inherited from Workday PMD except where noted**) so the exclusions are visible rather than assumed.

## 1b. Deliverable accessibility (the docs/decks/diagrams we SHIP, not just the app)

Section 1 covers the app UI. The **deliverables** the suite produces - Word user/admin guides, PDFs, PPTX
decks, Balsamiq wireframes, swimlane/systems diagrams - carry their own accessibility obligation, and
higher-ed / government clients often **require Section 508 / WCAG 2.1 AA conformance in the contract**.
Default target for every client-facing deliverable: **WCAG 2.1 AA / Section 508**. The bar:

- **Contrast:** body text >= 4.5:1, large text / UI / graphical objects >= 3:1 against their background
  (supersedes any lower "readability" floor - see document-quality-gates.md G16). Re-verify after any brand
  palette swap.
- **Never color-alone:** status / grouping / membership always carries a second cue (text label, icon, or
  pattern/dash), not hue only. (The RAG text labels, integration-type dash-arrays, and chart
  `accessibilityMode` pattern-fills are the models to copy.)
- **Alt text / text alternative:** every embedded image/screenshot has alt text; every diagram ships a text
  equivalent (the enumerated node/edge or step list, as a caption or appendix). A hover-only tooltip is NOT
  an accessible alternative and is lost on PNG/PPTX export.
- **Tagged PDF:** export native tagged PDF (Word/PowerPoint "Save as PDF" preserves tags); a render-to-PNG
  path (rasterizing to images) destroys tags + reading order - if used, the image needs alt text + a text
  equivalent.
- **Structure:** real heading levels + reading order; table HEADER rows tagged (machine-readable), not just
  visually bolded; meaningful link text (not "click here"); a minimum readable body font size.
- **Branding inherits, never overrides:** brand colours/fonts must meet the contrast bar. The
  neutral default (`brands/neutral.json`) is pre-checked: band text on band 14.5:1, header text on
  header fill 14.3:1, body text on white 14.7:1. Two rules to enforce on top for ANY palette:
  **readable text uses the brand's body-text colour on white or the header fill** (lighter greys
  usually fail the 4.5:1 body bar), and **light accent type sits only on the dark band colour, never
  on white or the header fill**. Verify any client-brand palette the same way (compute the ratios)
  before shipping.

"Done" bar: each client-facing deliverable states its accessibility target and meets the bar above (or records
the specific client-agreed exception). Under a 508/WCAG contract clause this is a delivery gate, not a nicety.

## 2. Error-handling standards

The single biggest NFR gap. Two audiences: the end user (at the screen) and the admin/support team (when an orchestration fails unseen).

| Capture in the doc | "Done" bar |
|---|---|
| **User-facing message standard**: what a validation/failure looks like - plain-language, actionable, no raw 400/S-codes | Every submit path names its validation approach; cross-field rules use the `validations` array pattern (pmd-gotchas reference in the wd-extend-dev skill, #24), not silent failure |
| **Orchestration failure behavior** per integration: retry (count/backoff), dead-letter/hold, and who is **notified** on failure | Every orchestration/INT, in the terms of the orchestration reference in the wd-extend-dev skill, has a stated failure + notification path; mirrors gap-analysis's "failure behavior for every external dependency" |
| **Source-API-down behavior** (the "questions-nobody-asked" item): does the page degrade, block, or queue? | Answered for each external read; no flow silently shows empty data as if it were real |
| **Partial-failure / idempotency** for batch orchestrations (re-run safe? duplicate-guard?) | Stated for any multi-record load; test scenario exists (wd-testing owns derivation - see its unit-testing reference) |

Error scenarios are unit/UAT test rows, not just prose - wd-testing derives negative-path scenarios from this section.

## 3. Performance & concurrency (design-time targets)

Set the numbers at design time so the build can be measured against them and the perf-testing-template reference (wd-deployment skill) has something to test to. These same volumes feed the volumes-questionnaire reference (also wd-deployment) (omitted APIs are the #1 production-approval rejection).

| Capture in the doc | "Done" bar |
|---|---|
| **Response-time target** per key page/flow (e.g. list loads < X s) | Any page-sync orchestration respects the 25 s cap (owned by wd-extend-dev orchestration.md); a large read designed as page-sync is flagged (consistency check already in gap-analysis) |
| **Peak volume & concurrency**: rows per read, records/run, concurrent users, and the **peak window** (fiscal year-end, etc.) | Volumes on Discovery match the limit choices on Technical Specification; every named API appears in Data & Webservice Mapping |
| **Limits watch**: BO REST collection limit (owned by wd-extend-dev pmd-gotchas.md), pagination/WQL for larger sets; compute-once patterns for heavy pages | Any >100-row need names its pagination/WQL approach; efficiency patterns in the efficiency reference of the wd-extend-dev skill considered for dashboard/aggregation pages |

## 4. Browser & device support

Cheap to state, awkward to discover late. One line usually suffices.

- **Capture**: supported browsers (default: current Chrome/Edge/Safari/Firefox, matching the client's Workday support matrix), and desktop-vs-mobile intent - including Workday **mobile app / responsive** expectations and any scanner/kiosk hardware (barcode-via-text-field, pmd-gotchas reference in the wd-extend-dev skill, #37).
- **"Done" bar**: a stated support matrix; if mobile is in scope, the wireframes/flows note it - an app "assumed desktop" that users hit on a phone is a post-go-live surprise.

## 5. Security & audit (as NFRs)

The functional security model - domains, groups, who-sees-what matrix - lives on the **Security** tab and its own gap-analysis rows. Here, capture the *non-functional* security posture as a short block, cross-referencing the security-setup reference in the wd-extend-dev skill.

| Capture | "Done" bar |
|---|---|
| **Auth posture** per touchpoint: user-context (SSO) vs ISU, and least-privilege intent | Matches the auth column already required in Data & Webservice Mapping (every write names ISU vs user context) |
| **Audit trail**: what changed, by whom, when - and *what the auditor is shown* | The gap-analysis audit question is answered; config-change auditing has a home (report or BO) |
| **PII/sensitive-data handling**: which fields are sensitive, masking/visibility, and the never-in-URL/query rule from the pmd-gotchas reference in the wd-extend-dev skill | Sensitive fields identified; none placed in URL params or logs |

### Data classification (per-BO/field pass)

"Sensitive fields identified" means a **classification pass over every BO and field during field-spec authoring**, not a prose paragraph. Tag each field: **none / PII / PHI / FERPA / other-regulated**. Classify **attachments and free-text comment fields explicitly** - they default to "none" on every first pass, and they are exactly where regulated data actually leaks (a "notes" field on a student-adjacent app collects FERPA data whether the design intended it or not). Discovery's DATA dimension (wd-discovery) should surface candidate classifications; this pass makes them per-field decisions on record.

Each classification carries required design responses - the consequence table:

| Classification | Required design responses |
|---|---|
| PII | Masking/visibility rules per role; domain confidentiality where only some roles may see; never in URL params or logs |
| PHI | Everything in PII, plus: field-level audit grain; **minimum-necessary** (the HIPAA standard - expose, transmit, and report only the fields a role or integration actually needs, not the whole record); **BAA gate below**; export-destination constraints stated; no PHI in orchestration run-logs / monitoring extracts |
| FERPA | PII responses, plus: **directory vs non-directory** classified; any student-data report/export/outbound integration **must filter on the student directory-information privacy-block (opt-out) and state its disclosure basis** - directory / consent-on-file / legitimate-educational-interest; audit grain sized to "who viewed what". Roles granting access to education records record their legitimate-educational-interest justification (see security-role-design.md) |
| Any regulated class | Retention/legal-hold override per BO (a legal hold beats the standard purge - note it against section 6's retention target); **erasure-infeasibility**: if the BO holds erasure-eligible personal data (GDPR Art. 17 / CCPA) AND is BP-tied (cannot be purged - section 6), flag the legal-vs-technical conflict to the client at design time and document the compensating approach (soft-delete / field-scrub vs. an accepted, disclosed limitation) rather than discovering it at the first erasure request; export destinations constrained (which downstream systems may receive it - feeds data-retention-export decisions in the wd-post-go-live skill); **offshore-support flag** - if the client restricts offshore data processing, flag per wd-contracts `references/saas-agreement.md` section 3.6 |

**Gate: any PHI classification blocks design sign-off until the BAA dependency is confirmed** - mirror the contracts rule (wd-contracts saas-agreement section 3.2: confirm a BAA exists or placeholder the dependency). A PHI field with no confirmed BAA is a Red open item, not a yellow one. **Separately and EARLIER:** the firm-client BAA must be executed **before any consultant accesses a PHI-containing tenant or ingests PHI** (discovery, mock-conversion, UAT all happen before design sign-off) - that is a kickoff prerequisite, not a design-time gate (see wd-extend-lifecycle `ai-data-governance.md` section 1 + the kickoff checklist). This design-time gate covers the app's own PHI handling; the kickoff gate covers the firm's Business-Associate status.

- **"Done" bar**: every BO/field (including attachments and free text) carries a classification; every non-"none" classification shows its consequence-table responses in the design; no PHI without a BAA answer.

## 6. Data retention (NFR view)

Retention is already a first-class gap-analysis item; the NFR contribution is the **quantified target**. Capture the retention *period* and archive destination, and note the Extend realities (no bulk delete; BP-tied BOs are export-only) - full mechanism/tradeoffs live in the data-retention-export reference of the wd-post-go-live skill.

- **"Done" bar**: a stated retention period + purge/export decision per BO (or the explicit "export-only, BP-tied" answer); attachments addressed separately. Anything unstated is a yellow item.

## 7. Localization / i18n (low-priority checklist line)

One line, usually. For a **single-institution internal app this is typically out of scope - not a workstream** - but record the decision so it's an intentional exclusion, not an oversight.

- **Capture**: language(s), and date/number/currency formatting expectations if multi-region.
- **"Done" bar**: an explicit in/out-of-scope statement. Default note: *"Single-language (en-US); i18n out of scope - revisit if deployed beyond [institution]."* Only elevate to real work for genuinely multi-region deployments.

---

**Net done-bar for the whole section:** every category above is either answered on Technical Specification (with testable ones traced to a Requirements row) or carries a yellow open item with an owner. An NFR section that is entirely blank or entirely prose fails the sweep - the same standard gap-analysis applies to every other tab.
