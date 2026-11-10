# Quality gates - the every-time enforcement registry

**The rule: no artifact ships without its named check - every time, no exceptions.**
When Claude produces or updates ANY artifact type below, run its checks BEFORE presenting
the work as final, and **report the check result WITH the deliverable** ("gap-analysis
clean, 2 yellow opens remain" / "idd_audit: 0 findings" / "gotcha sweep: #17 applies,
fixed"). A deliverable presented without its check result is not done. If a mechanical
check's script is missing on this machine, regenerate it from the owning skill's
build-spec (`references/scripts.md`) - never skip silently.

**SELF-QA BEFORE HANDOFF (owner-set 2026-09-10, STANDING - a HARD, always-on gate regardless of entry point).**
Before handing ANY artifact to the user for review, QA it yourself first - the same bar a senior developer
clears before a review, and the user is exacting about "nit-picky" presentation. Two passes, both mandatory:
1. **Correctness** - the artifact's named check above (mechanical + manual), plus for sign-off-grade work the
   cold-reader/fresh-eyes test (a zero-context reviewer at full strength - see "Verification mechanics" below).
2. **Presentation-polish** - it reads and looks right: no typos/broken links/stale counts/leftover placeholders;
   consistent formatting; renders correctly (RENDER an xlsx/docx/pptx and LOOK; ASCII/format-clean for suite
   files); chunked + verb-first for human-facing text; borders/formatting/formulas intact for workbooks.
**Presentation matters** - a defect or a sloppy render reaching the user wastes their review and means you did
not measure twice on your own output. State that you self-QA'd and the result WITH the deliverable. "Too small
to QA" is the #1 tell you are about to miss something.

**MEASURE TWICE - THE PRE-BUILD REQUIREMENTS GATE (owner-set 2026-09-10, STANDING - "measure twice, cut once").**
This gate fires BEFORE you touch a script (not before you ship) - the front of the loop. Before writing or
modifying ANY build artifact (Extend app, O4I/integration, hosted tool), capture the requirement set in
writing, DERIVED from the owning skills - never remembered, guessed, or inferred from a sibling:
- **Functional** - from the signed design doc (read the FULL latest version before building each vertical; never infer from a sibling).
- **Data / integration** - the web services, RaaS/WQL sources, and connectors the design implies (wd-solution-playbooks for the domain; wd-integration-dev for a traditional integration).
- **SECURITY (MANDATORY, first-class - the recurring miss).** Enumerate EVERY security object the design implies -
  domains (with view/modify/get/put level), ISU, ISSG/segments, API client + scopes, RaaS/report security -
  derived from the design's Security tab / IDD WD Solution tab + the owning skills (wd-deployment
  `references/security-role-design.md` + `security-setup-section.md` "enumerated domains-and-permissions table";
  wd-extend-dev `references/security-setup.md`; wd-solution-playbooks for which web services a domain uses).
- **Tenant prerequisites** - R1-R12 (wd-deployment `references/tenant-task-recipes.md`).
- **NFRs** - limits/perf/accessibility/data-governance as applicable.

**HARD STOP on security gaps (owner rule 2026-09-10):** a **blank or unresolved SECURITY section is a hard stop -
do NOT start building.** Look it up with the skills first; the tools to know exactly what's required already
exist - the failure is not using them up front. (Functional/data/tenant/NFR gaps are flagged as open items and
you may proceed; only the SECURITY section blocks the build.) This is the codified form of the muscle-memory a
seasoned developer has - front-loaded, not rediscovered mid-build. Report the captured security requirement set
before the first build/edit action. A mechanical enforcer ships: run `wd-extend-dev/scripts/requirements_preflight.py <app-root>`
before upload/deploy (it fails when an app defines security surfaces with no captured security requirements);
and once a skeleton exists, `wd-extend-dev/scripts/security_domain_discovery.py` resolves the app's actual
reports/WS-ops/BPs to their securing domains to VERIFY the hand-derived list.

**Track scoping of the security enumeration:** the domain/ISU/ISSG/segment/scope vocabulary above is the
**WORKDAY** build's security surface. For a **Track-2 hosted tool** (app-* family) the same measure-twice
principle applies but the surface is different - IAM roles + least-privilege, secrets management, identity
provider (Entra) config, the ISU/scopes for any Workday reads (see saas-integration
`references/workday-from-a-hosted-tool.md`), and trust-boundary/prompt-injection controls; capture it in
`app-architecture/references/discovery-and-design-brief.md` (NFR/security section) before scaffolding. The
Workday enumeration here does NOT apply to a non-Workday hosted tool - do not treat its blank Workday fields
as the hosted-tool gate.

**Companion presentation rule (owner-set 2026-08-06):** whenever a check or workflow step
requires the USER to act **outside the Claude session** (a Workday tenant UI task, an
interactive `wdcli`/browser login, hidden-prompt credential entry), fence those steps as a
labeled **"Your steps (outside this session)"** numbered block - where each step happens,
exact value per prompt, what they'll see, and how to signal done. Convention detail in
guided-delivery.md; worked example = the First-time setup runbook in wd-extend-dev
references/tenant-ops.md. Session-boundary crossings are the #1 place users get lost.

This registry consolidates checks that live in (and are owned by) the skills below -
consult the owning reference for the how; this table is the *what must run*.

**Provenance ladder (canonical - the single definition the whole suite uses).** Every load-bearing platform
fact/claim ranks by how it was confirmed, strongest first: **build-verified** (we built it and saw it work) >
**sample-verified** (seen in a canonical Workday DevRel sample) > **official-docs** (Workday doc/Community,
date-stamped) > **doc-sourced/unverified** (secondary or inferred - carries a `(!)`/verify caveat). Rule:
**observed behavior beats documented shape** where they conflict. This is the "verify-before-promote" ladder
every reference tags against (it is the build-side analogue of bow-sales-enablement's claims register).
**Propagation rule (applies to ANY change, not just facts):** whenever you change a shared value - a corrected
platform fact, a count/number, a skill or file NAME, a moved/renamed reference, an ownership pointer, a
version/date - **grep the WHOLE suite for the old token and reconcile every occurrence in the same pass.** The
recurring failure mode is a change landing in one file but not its siblings (observed this build: the
`SendPrismRequest` correction, the pmd "not solved" contradiction, the reuse-catalog move's 6 pointers, the
"12 guides" count in two places). It is the #1 reason "going back to update an existing artifact" goes wrong.

**Updating an EXISTING artifact - the every-time discipline (suite docs, skills, or client deliverables):**
1. **Re-open the LATEST version first** (never edit a stale copy - the "audit the latest source" cardinal rule;
   for client apps, `wdcli app download`; for suite files, read the file, don't trust memory of it).
2. **Change it and every reference to it** (propagation rule above) - the file you opened is rarely the only
   place the value lives.
3. **Re-run the artifact's named gate** before calling it done - for suite files that means
   `fix_suite_ascii.py` + `validate_suite.py` (MAINTAINER-side tooling at
   `~/.claude/skill-asset-masters/_suite-maintenance/` on the maintainer's machine - it runs on the
   canonical copy before distribution; suite RECIPIENTS skip this step); for a rendered document, RENDER it and look (Word/Excel COM can
   hang - prefer the cross-platform python-docx/openpyxl/reportlab builders and verify with a PyMuPDF render;
   if the output path is open/locked, e.g. a synced OneDrive file, write a fresh versioned filename rather
   than failing). 4. **Record what changed** in the version change-log / project memory.

| Artifact | Mechanical check | Manual check (owning reference) | Evidence to record |
|---|---|---|---|
| Extend design doc (any template) | - | wd-design-doc gap-analysis.md full sweep (incl. SOW-conformance row) + references/formatting-checklist.md + fresh-eyes pass per tab | Gap-analysis result noted in the version's change-log entry |
| NFR / accessibility (design) | - | wd-design-doc nfr-accessibility.md - non-functional requirements + accessibility captured; **PHI/PII/FERPA data classification and the BAA-before-sign-off gate** (a hard sign-off blocker) | NFR/accessibility section complete; sensitive data classified; BAA status confirmed before design sign-off |
| **Any design doc - presentation (any template, any branding)** | `wd-design-doc/scripts/xlsx_format_audit.py` + `xlsx_brand_style.py` + `xlsx_normalize_borders.py` (+ `xlsx_coverage_guard.py` after every pipeline step) | wd-design-doc **document-quality-gates.md** G1-G18, in the stated ORDER; **G18 = verify by RENDER, never optional**; the mandatory content-coverage guard aborts on any dropped cell value | Which gates ran, what they found/fixed, anything knowingly left |
| IDD (.xlsm) | `wd-design-doc/scripts/idd_audit.py` (hard gate) | idd-template.md rules (READ ME as cells, N/A-not-blank, Flow + Examples present) | Audit-clean statement with the delivery note |
| **Change/build entry - acceptance criteria** | - | wd-extend-dev workflow.md Rule 0 - scoped, testable acceptance criteria before any wdcli edit; high-impact (security/data/migration/integration) changes mandatory | Criteria filed; feeds wd-testing scenario derivation |
| Orchestration / O4I flow | `wd-extend-dev` validate.py (build-spec in scripts.md) | orchestration.md limits + error-handling guards; standards.md platform-citizenship block | Validator output; guards named per risky node |
| **Any built artifact (code / script / transform / tenant config) - the EXEMPLAR bar** | header + change-log + KT comments present; validator/linter clean | wd-extend-dev standards.md "exemplar standard" self-check: correct-AND-verified, efficient-by-design, readable/idiomatic, KT-commented, DOCUMENTED (companion doc or evidence trail), reusable-as-a-pattern; any shortcut FLAGGED not silent | Self-check reported with the deliverable; a genuine standout nominated to the reuse catalog / app-catalog-registry as a cited north-star |
| **Deliverable content review (client/senior-facing, pre-ship)** | - | wd-extend-lifecycle deliverable-review.md: set the bar, review in the receiver's voice, pre-mortem, verify claims/currency, verdict + located fixes, the client-facing floor; strategic "read-the-room" flags for customer-facing artifacts; name independence honestly (self-check != independent) | Verdict (Ready/Needs work/Not ready) + located fixes recorded; floor items cleared for client/final work |
| **Session auth preflight (before the first wdcli/API/tenant action)** | wd-auth auth-preflight.md sequence run (whoami org/account, tenant/token auth, env/cred profile as applicable) | wd-auth references/auth-preflight.md: tokens valid, active account/ORG is the intended one, right auth mode selected - catches expiry / wrong-org / missing-cred before a misleading "tenant not found" / 401 / invalid_grant failure | Auth preflight run + passed (or the failing check + its USER-ACTION block surfaced) before any wdcli/API/tenant call |
| **Build / tenant session pre-flight (do-it-right-the-first-time)** | `app upload` PRECEDED `app deploy`; target tenant is dev/sandbox, not prod | wd-extend-lifecycle operational-preflight.md: pull-latest + diff before editing an existing app; RIGHT version verified LIVE after deploy (not just CLI "success"); re-seed after deploy wiped dev BO data; proxied as the intended worker for persona tests (the AUTH portion is the wd-auth row above) | tenant confirmed dev; upload-before-deploy done; live version verified; re-seed done - or the slip logged so the check gets sharpened |
| **Verify-in-tenant (trust-but-verify, standing rule)** | authoritative programmatic read (WQL / REST / RaaS / SOAP) where one exists; browser check only when no API covers it | wd-extend-lifecycle verify-in-tenant.md: never assume tenant state - read it before referencing/creating/designing-against it, and after any write confirm it landed (not just "the UI did not error"); a browser "none/empty" is suspect (async / security-gated) until confirmed programmatically. Technique detail: wd-extend-dev tenant-state-verification.md | What was read + how + what it confirmed, reported with the deliverable; unverified assumption presented as fact = failed gate |
| PMD page / script | `wd-extend-dev` scripts/pmd_preflight.py (run on the app root BEFORE every `wdcli app upload`) | pmd-gotchas.md FULL numbered sweep (use whatever number the file ends at) on every touched PMD - the linter covers the mechanically-detectable subset, the sweep covers the runtime-behavior traps; standards.md + efficiency.md | Preflight result (0 FAIL) + "gotcha sweep done" + any numbers that applied |
| UI design self-review (client-facing page/dashboard, before demo/ship) | - | wd-extend-dev ui-design-principles.md section 10: screens x states enumerated; visual pass + UX pass; density/numeric-alignment/state-design/accessibility-numbers honored | Two-pass review done + self-score noted; accessibility deviations recorded as design-doc NFR caveats |
| Whole app (pre-go-live, takeover, or periodic) | - | wd-extend-dev app-review-audit.md 8-step sweep | Findings report (`<APP>_Review_Findings_v.xlsx`) |
| Integration build (Studio / EIB / CC / DT / O4I-as-INT) | DART run | wd-integration-dev integration-build.md build gates (per-type highlights) + studio.md anti-pattern list (manifest-as-runbook current, no test data committed) | Build-gate checklist initialed; DART clean |
| Integration REVIEW (2nd-eyes on an IDD or a build) | - | wd-integration-dev integration-review.md: IDD-stage (21) or Build/CLAR-stage (41) checklist + Studio code-quality rubric; auto-N-A the text-unverifiable, never inflate a met bar to Partial | Scorecard + Critical-Findings paragraph (completion % optional) |
| Integration functional test | full-volume run + reconciliation counts | wd-testing integration-testing.md: field-level output vs IDD mapping, transport/security/schedule, error/audit, outbound parallel-run vs legacy, integration UAT in the downstream system | Reconciliation + parallel-run result recorded; downstream UAT signed off |
| Browser-driven test run (per scenario) | - | wd-test-execution execution-workflow.md: every scenario actually driven + asserted via read_page/console/network; NO "Pass" without a captured observable (screenshot or record/event ID); failures carry a repro + evidence and route to wd-testing defect-triage.md | Per-scenario status + evidence ref recorded into the Unit Testing tab; never mark a scenario passed you did not drive |
| In-tenant browser WRITE (config or test data) | tenant identity confirmed (Browser pane host + wdcli whoami) = dev/sandbox, never prod | wd-tenant-config safety-and-scope.md: correct action tier (FREE / confirm-each-write / hand-to-user); security & system-settings commits handed to the user; synthetic data only; each committed write has a read-back | Tenant confirmed dev; per-write confirmation obtained; read-back evidence recorded |
| Integration tenant migration | tenant-ops cross-tenant read-set diff (counts/refs per tenant) | wd-deployment migration-checklist.md (type-applicability matrix; migrator -> reviewer statuses) | Row Complete per integration per tenant |
| **Pre-promotion "evaluate" (per hop)** | tenant-ops read-set (domains / ISU / RefIDs resolve) | wd-deployment promotion-and-environments.md go/no-go - security domains, ISU scope, error handling, retry/idempotency, reliability (complements Volumes/Perf, does not replace) | Go/no-go recorded with named decider; filed with the promotion package |
| Cutover plan / go-no-go | tenant-ops in-flight BP events check (businessProcess /events) | wd-deployment cutover-planning.md + the SKILL go/no-go checklist (incl. people-readiness + GA-features rows) | Go/no-go outcome recorded with named decider |
| Discovery doc + outcome baselines | - | wd-discovery playbook completeness (A/B/C) + 3-5 baselined metrics with sources (wd-post-go-live value-capture.md section 1) | Baselines filed; feeds the design doc Discovery tab |
| Data-conversion load | tenant-ops WQL count vs source | wd-extend-dev data-conversion.md; reconciliation counts source vs loaded | Counts recorded; variances explained |
| Migration wave gate (phased conversion) | reconciliation harness evidence (counts / DQ / control totals per wave) | wd-deployment migration-readiness-gates.md verdict per wave (Pass / Conditional Pass / Fail, threshold-before-the-gate, conditions carry forward, rollback tested not documented) | Verdict per wave + carry-forward conditions (with owners) recorded |
| Tenant API write (test/demo/config load) | tenant_toolkit check-tenant identity gate | wd-extend-dev tenant-ops.md WRITE GATE (never prod; allowlist; synthetic only; cleanup plan; soft-delete flags set) | Load-log + cleanup plan filed WITH the load |
| Any output artifact - sensitive-data egress (tracker / RAID / status / design doc / guide / comm / diagram / screenshot) | - | wd-extend-lifecycle ai-data-governance.md section 6: no PHI/PII/FERPA or secrets by default; match artifact exposure to data sensitivity; least-identifying form only where already scoped; synthetic examples + scrubbed screenshots | Confirmed clean before write/send; any real identifier justified + minimized |
| Release notes (enhancements) | - | wd-kt three-field pattern (what changed / opt-in vs automatic / action required) | Issued with the change; recert checklist row satisfied |
| Demo (any track) | tenant-ops pre-flight reads (picker sources, seed counts, stray events) | wd-demo playbook: staged synthetic data, same-day smoke run, script variant matched to track | Dry-run done - never demo un-smoke-tested |
| Systems diagrams (client-facing) | Engine renders valid SVG/drawio/PPTX | wd-systems-diagrams input-schema completeness; scope/hub settings match the ask | Reviewed against the integration tracker before sending |
| QBR deck / value snapshot / closeout artifact | tenant-ops WQL/RaaS pull of the locked KPI sources | wd-post-go-live account-growth.md + value-capture.md shapes; numbers trace to monitoring data | Snapshot filed; consent checked before any external reuse |
| Project plan / RAID stand-up | - | wd-pm plan-skeleton (gates as named dated tasks) + raid-log.md conventions | Mandatory-gate rows present in the plan |
| Change-impact assessment (OCM) | - | wd-change-adoption impact-and-readiness.md High/Med/Low rubric, validated vs BP inventory + design doc; tracked in the RAID log, not a parallel sheet | Impacts in RAID; severity matched to comms/training intensity |
| Communications & training plans (OCM) | - | wd-change-adoption comms-and-training-plan.md: comms matrix complete (audience/channel/sender/cadence/theme) + role x curriculum from the role map, pilot-in-UAT planned | Plans filed; message drafting -> wd-comms, training build -> wd-kt; dates on the project plan |
| Change-readiness assessment (OCM) | - | wd-change-adoption impact-and-readiness.md repeated-round survey + readiness checklist (trend, not a snapshot) | Readiness trend recorded; falling High-impact group = escalation |
| Adoption metrics (OCM) | - | wd-change-adoption adoption-measurement.md: baseline at discovery, target at design sign-off, leading+lagging, segmented by stakeholder group | Baseline + target locked in the KPI table; actuals handed to wd-post-go-live |
| Reusable-asset harvest (closeout) | - | wd-practice-ops reuse-and-asset-catalog.md: reusable pieces genericized/scrubbed (README share sweep + ai-data-governance IP rule) and catalogued with type/maturity/reuse-count/owner | New/updated catalog rows filed; productization candidates flagged to bow-sales-enablement |
| Test-automation harness run | tenant_toolkit check-tenant identity gate (never prod) | wd-testing automation-harness.md: synthetic data only, WRITE GATE respected, idempotent with cleanup | Pass/fail per path with evidence; cleanup plan filed with the run |
| Practice-ops artifact (competency matrix / staffing / cert tracker) | - | wd-practice-ops: skills matrix current, certification recert-dates tracked, staffing matched by capability + availability | Matrix/cert status current; capability gaps flagged for enablement, subcontract, or rescope |
| Opportunity brief / build-no-build (market-research) | - | market-research platform-fit-and-brief.md: a GO needs validated demand (evidence ladder) + whitespace/wedge + bottom-up SOM + confirmed platform fit + the scorecard, with Evergreen/platform-native risk assessed; every number sourced+dated | Brief complete + go/no-go recorded with rationale; GO hands off to bow-sales-enablement / wd-estimate; claims inherit the claims-register |
| Architecture (before build) | - | architecture-review.md checklist, reviewer != designer | ADR-lite appended to the design doc Tech Spec tab |
| Solution choice (net-new) | - | wd-discovery solution-options.md matrix + recommendation | Named client approver + rejected-options rationale filed |
| Security-role design (client end-user model) | - | wd-deployment security-role-design.md: role-to-domain-to-BP grid complete; SoD matrix run with conflicts split or a documented compensating control; constrained-by-default (each unconstrained group justified); positive + negative security testing planned | SoD matrix filed; documented in the design-doc Security tab; role-based test cases handed to wd-testing |
| Wireframes / process flows | - | wd-design-visuals intra-frame overlap/fit checks; clean-export rule (generated render = draft placeholder) | Clean export embedded, or draft explicitly labeled |
| Volumes Questionnaire / Perf Testing | Formula-preservation check (never overwrite Recommendations formulas) | volumes-questionnaire.md rejection-cause playbook (every API surface inventoried, stated basis per volume, peak not average) | Capacity-ledger row updated |
| Unit/UAT test artifacts | wd-testing unit-testing.md Section 1a quality gate (4-gate authoring check on every scenario before it lands on the tab) | wd-testing scenario coverage vs Requirements tab; unit-testing.md Section 1a anti-pattern sweep (implementation-coupled / tautological / horizontal-slice); regression scope per the change rules; any defect routes through defect-triage.md Step 2 fix protocol (investigate before propose; 3-attempt escalation rule) | Results recorded on the Unit Testing tab / UAT log with k-value per critical-path scenario (pass@1 = capability evidence; pass^3 minimum for go/no-go gating - all 3 runs succeed; pass^k for Sev1-prevention and data-write paths) |
| Client guides (user/admin/deployment/runbook) | - | wd-kt patterns + security-setup-section completeness (**a blank domain table is a defect**) + document-polish rules | Section checklist; KT sign-off artifact |
| Client comms / status / SteerCo | - | wd-comms voice rules + user read-through before send; wd-pm no-sandbagging RAG rules (schedule AND financial) | Sent after read-through; numbers trace to the tracker |
| AI-assisted writing (any client-facing/external text) | - | wd-extend-lifecycle writing-quality-gate.md: no em dash; AI-tell word + structural-pattern sweep at the context-profile strictness; human-in-the-loop (author adds 2-3 sentences in their voice + verifies facts) | Gate run; author contributed + confirmed facts/numbers/names; never presented as send-ready without it |
| Smartsheet writes | `describe <sheet_id>` before ANY write | wd-smartsheet section 4 pre-write column review + before->after diff echo | Diff confirmed by user (unless exact change pre-approved) |
| Estimate / proposal | - | wd-estimate calibration cross-check; proposal-content rules (own quantified claims need a register/value-capture source) | Archetype + confidence noted |
| Contract paper | - | wd-contracts DRAFT-for-legal stamp + placeholder rule (never invent terms) | DRAFT marking present; deviations flagged |
| Contract paper - counsel sign-off (pre-use gate) | - | wd-contracts: a draft does not leave for the client or go to signature until reviewed by qualified legal/contracts | **Named legal/contracts reviewer + date recorded** before send/execution (DRAFT stamp alone is not sign-off) |
| Data-protection terms (design sign-off) | - | wd-design-doc nfr-accessibility.md classification: for any PII/FERPA/EU-personal-data (not just PHI/BAA), the applicable DPA / breach-notification / cross-border basis + AI sub-processor coverage must be confirmed in the paper | Blocks sign-off as a Red open item until confirmed - same posture as the PHI/BAA gate |
| Third-party-asset clearance (before packaging/share) | - | README sanitize sweep: no third-party-authored binary/document ships unless its license clears redistribution (vendor/Workday Community docs, fonts, images, copied code). ALSO covers generated OUTPUT: a deliverable that embeds third-party marks fetched at runtime (e.g. wd-systems-diagrams logo lookup via Clearbit/Google) needs logo-usage rights confirmed, or regenerate with logos disabled / a cleared logo set, before external distribution | Cleared-or-excluded list recorded; vendor docs referenced by link + regenerated, not bundled; runtime-fetched logos cleared or disabled for external output |
| Deliverable accessibility (client-facing Word/PDF/PPTX/diagram) | - | wd-design-doc nfr-accessibility.md 1b: WCAG 2.1 AA / 508 - contrast 4.5:1 body / 3:1 large; color never the only signal; alt text on images + text-equivalent per diagram; tagged-PDF export; header-row semantics; min font | Target stated + met (or client-agreed exception recorded); a 508/WCAG contract clause makes this a delivery gate |
| FERPA disclosure (student data out) | - | wd-design-doc nfr-accessibility.md FERPA row: any student report/export/outbound integration filters on the directory-information privacy-block and states its disclosure basis (directory / consent / legitimate-educational-interest) | Privacy-block filter applied; disclosure basis recorded; education-record roles carry a legitimate-educational-interest justification |
| Regulated-data access (kickoff prerequisite) | - | wd-extend-lifecycle ai-data-governance.md section 1: for a PHI/FERPA engagement, the BAA / data-handling agreement is executed BEFORE any consultant tenant access or data ingestion | Executed agreement confirmed + recorded before access; distinct from (and earlier than) the design-time BAA gate |
| Platform factual assertion (into client-facing output) | live confirm via tenant-ops / rest-api-catalog / wws-catalog for names | any definitive platform fact (numeric limit, task/report/node/API name, version, threshold, "Workday does X") entering a security questionnaire / design doc / proposal / contract / deployment guide carries a provenance tag or a (!)/verify caveat + source + date where doc-sourced | Provenance tag or verify note present; asserted names live-confirmed or labeled "confirm current" |
| External claims / case studies | - | bow claims-register gate + written tier-scoped consent + executed-section 8.2 check | Consent-evidence pointer on the register row |
| Any AI-ingested client material | - | ai-data-governance.md data gate (before ingestion) + named-human review before anything leaves | Reviewer = author of record |

**Cadence rule:** these gates also appear as dated tasks in the project plan (wd-pm) - a
gate nobody scheduled is a wish. The guided walkthrough
([guided-delivery.md](guided-delivery.md)) carries them as phase gates: the
**measure-twice requirements gate (security hard stop) is a phase-7 (Build) ENTRY condition**
(you do not enter Build with a blank security section), and the ship-time checks above are the
per-artifact EXIT conditions.

**When a check fails:** fix, or record the finding as a yellow open item / RAID entry with
an owner - never deliver silently past a failed gate. "We knew and accepted it" must be
visible in the artifact, not in someone's memory.

**Carried-exception status - the third gate state.** The gate vocabulary is three-valued: **MET / UNMET / CARRIED**. Real projects routinely pass a gate WITH a known hole, deliberately and with the client's agreement - a design signed off without its NFR section, an options assessment reconstructed after design approval. Calling that "unmet" misdescribes reality (sign-off happened); calling it "met" hides the hole; without the third word a tracker author either overstates (blocker) or loses it (met). A CARRIED gate requires three attributes, so it cannot become a shrug: (1) **what specifically is missing**, (2) **who accepted carrying it, and when**, (3) **which later gate or date it must close by**. Treat it as unmet for external reporting unless the named approver has signed off. A gate row with no exception record and no pass result is just skipped - that is never acceptable.

Example tracker row: `Design sign-off | CARRIED | missing: NFR/accessibility section | accepted: <client sponsor>, 2026-08-12 | closes by: architecture review (phase 6)`.

## Verification mechanics (when the check is judgment, not a script)

Most rows above name a mechanical check or a checklist. When the check is a judgment call -
"is this readable, complete, sign-off-worthy?" - use one of these three named mechanics,
listed weakest-need to strongest. Any gate row can invoke them by name. (Pattern from a
community skill-craft survey, 2026-08-06 - rebuilt for this suite.)

**Verification mode taxonomy.** Every gate row uses one of three verification modes.
Name the mode when recording evidence - a script result and a human sign-off are not
interchangeable, and the evidence record must be honest about which was used.

- **Code-grader (deterministic).** A script, query, or automated check returns a
  clear pass/fail. Examples: `idd_audit.py`, pmd_preflight 0-FAIL, WQL count vs source,
  `validate_suite.py` clean. Preferred whenever the criterion is mechanically decidable:
  fastest, most reproducible, removes human variance.
- **Model-grader (rubric-based).** A Claude reviewer evaluates an open-ended artifact
  against a named rubric (the cold-reader and dual-blind mechanics below). Returns a
  structured verdict per rubric row. Use for prose, design docs, proposals - things where
  "is this clear and complete?" requires judgment, not arithmetic.
- **Human-grader (manual - always attach a risk level).** A named person reviews and
  signs off. Use when the check requires contextual authority the code and model cannot
  provide: legal language, executive sign-off, compliance attestation, a claim only the
  client sponsor can verify. Always record reviewer name + date. Attach a risk level -
  **LOW** (stylistic gap), **MEDIUM** (functional/coverage gap), **HIGH** (regulatory
  or contractual) - so the evidence record conveys urgency, not just completion.

**Test reliability framing: pass@k vs pass^k.** When a scenario or smoke check passes
once, name what kind of pass it is before calling it evidence.

- **pass@k:** at least 1 success in k attempts. Exploratory confidence: the capability
  exists and the path is reachable. A single passing run is pass@1. It confirms the path
  exists, not that it is reliable.
- **pass^k:** ALL k attempts succeed. Production reliability: the path is consistent under
  normal variation (different data seeds, different tenants, different times of day).

Practical rule: a smoke-run result is pass@1 evidence - sufficient for capability
verification, not for go/no-go gating. To gate a go-live decision on a scenario, require
pass^3 (all 3 runs succeed). Sev1-prevention scenarios, orchestration timing-sensitive
paths, and critical data-write paths are pass^k requirements: all attempts must succeed
before go-live sign-off. Log the k-value with the evidence: "3 runs: 3/3 Pass (pass^3)"
says more than "Pass."

- **Cold-reader test.** Spawn a zero-context reviewer: a fresh subagent given ONLY the
  artifact plus a one-line profile of its intended reader - none of the build context, no
  design history, no chat thread. It reads AS that reader and reports three things: where
  it got lost, what it would ask, and what it would do next. This is the fresh-eyes pass
  (document-polish rules) taken to full strength - a same-author fresh-eyes sweep still
  carries the author's context, and that context silently fills the gaps the real reader
  will fall into. Default mechanic for: design docs at sign-off, client guides, proposals,
  any artifact whose eventual reader wasn't in the room when it was written.
- **Dual-blind review.** Reserve for the highest-stakes artifacts only - the design
  sign-off package, the Workday gating docs (Volumes Questionnaire / Performance Testing),
  contract drafts. Two reviewers with no shared context score the SAME rubric
  independently and return structured verdicts: pass/fail per rubric row plus one sentence
  each. Both must pass. Fixes are re-checked by FRESH reviewers, never the originals (a
  reviewer re-reading their own findings confirms them). Hard cap: 3 rounds, then the
  remaining disagreement escalates to the human.
- **Iteration terminator.** Applies to every review loop, including the two above: after 3
  consecutive rounds without substantive change, stop. Whatever is still contested goes to
  the human as a named open item (yellow / RAID, per the failed-gate rule above) - never a
  4th round of the same argument.

**Pre-generation gates.** Some artifacts have a mandatory attribute without which the
artifact is worthless: a runbook without a named owner, a CR without approval, an external
claim without a claims-register source. For these, the gate runs BEFORE generation -
refuse to produce the artifact until the attribute exists, rather than producing it and
flagging the hole. The suite already works this way for builds ("no build on an unapproved
CR" - the Change path's entry condition); apply the same stance to ownerless runbooks (a
document with no owner decays fastest) and unsourced claims.

## Review verdict schema + multi-agent operating lessons

The mechanics above say HOW to run a judgment review; this says what a review RETURNS and how to run the crew that produces it. (adapted from an internal firm skill, 2026-08-28)

**Review verdict schema** (what dual-blind / cold-reader / any crew review returns):

| Field | Holds |
|---|---|
| `verdict` | pass / conditional / fail |
| `confidence` | + `confidence_rationale` = specifically WHY NOT one level higher |
| `must_fix` | critical/high only, deduped across reviewers |
| `open_risks` | still-uncertain items, carried forward HONESTLY, never dropped to look done |
| `would_change_verdict` | the facts/checks that would move it up (or reveal it should be down) |
| `decisions_for_the_user` | calls the crew cannot legitimately make (business preference / risk appetite / facts nobody in the room can know) |
| `handoff` | each deliverable -> where it routes next -> why |

Rule: **WEIGH the lenses, don't average** - one critical correctness failure outranks three clean passes. An honest clean pass is a valid result; never invent findings to look thorough.

**Multi-agent operating lessons** (for the Workflow harness that runs these reviews - the general forking/dispatch discipline is owned by **session-orchestration** `references/dispatch-discipline.md`; these are the review-specific notes):

- **FEED CONTEXT IN, don't send agents foraging.** Extract a compact digest in the main thread and pass it; "go read the repo/tenant to ground yourself" makes an agent spiral (token blowups). Naming specific files is fine (bounded); turning it loose on a directory is not.
- **PASS success criteria explicitly** - a completeness reviewer is only as sharp as its definition of done.
- **TELL reviewers what a prior pass already found** ("already fixed - go past it") or they burn the budget rediscovering known issues and look thorough while adding nothing.
- **KEEP SCHEMAS PERMISSIVE on free-form fields** - an over-strict schema causes a runaway retry loop that never converges; reserve enums for genuinely closed sets.
- **A KILLED RUN IS NOT A FAILED RUN.** Agents write structured output as they finish - salvage the completed pieces first and relaunch only the missing phases; don't throw away paid work.

## Red flags (rationalizations the gates exist to refuse)

The gates don't fail because someone rejects them - they fail because someone talks
themselves out of them in the moment. The recurring scripts, each with its counter:

- *"This change is too small for the sweep."* Small changes have the highest
  landmine-per-line rate; the sweep is sized to the change, never skipped.
- *"We're behind schedule - run the gate after delivery."* A gate run after delivery is a
  retrospective, not a gate.
- *"The client is waiting - send it now, polish later."* The client remembers the version
  they received.
- *"I already checked it while writing."* Author self-review is the weakest check we have -
  that's exactly why the verification mechanics above exist.

When one of these thoughts occurs, that IS the trigger to run the gate.
