# Guided delivery - walk any user through a project, start to finish

For "walk me through it", "start a new project", "what do I do next", "I've never done
this before" - or whenever the user's questions suggest they'd benefit from being LED
rather than handed a map. This mode turns the phase map into a **consultative companion**:
Claude tracks where the project is, drives to the next step, and holds every exit gate.
It works for a single app, a single integration, or a multi-app program, and for any user -
new colleague, experienced lead, or a client-side team using the suite.

## Step 0 - calibrate once, then remember

At the start of a guided engagement, establish (ask only what you can't infer):
1. **Scope**: single Extend app / single integration / program of many (program -> also
   run wd-pm program-mode registers from day one).
2. **Where the project actually is** - never assume day zero. Ask what exists (contract?
   design doc? code? live app?), then enter the walkthrough at the right phase. A live app
   + a change request = the Change/enhancement path, not this greenfield walk.
3. **User depth**: novice -> give click-level guidance (wd-deployment
   tenant-task-recipes.md, wdcli-setup.md, the novice token/setup guides) and explain WHY
   each gate exists; experienced -> terse checklist mode, gates only. Re-calibrate silently
   as you observe them work.
4. **Colleague or client-side user**: the delivery walkthrough is identical; skip the
   firm-internal steps for client users (UET pricing, win/loss debrief, claims-register
   feeds, calibration write-back - marked (i) internal below).

## Step 1 - instantiate the Delivery Tracker (the state that survives sessions)

Create a per-project tracker at the project folder root (`<Project>_Delivery_Tracker.md`,
or a Smartsheet via wd-smartsheet if the program runs one): one row per step below -
Phase / Step / Owner / Status / Artifact produced / **Gate check + result** / Date.
Every guided session OPENS by reading it ("you are here, X is next, gate Y is unmet") and
CLOSES by updating it. If both an .md tracker and a program Smartsheet exist, the
Smartsheet is the source of truth and the .md is a per-app working view - reconcile on open. This tracker is how "every time" survives context loss, handoffs,
and weeks between sessions. Mirror the gate rows into the real project plan as dated
tasks (wd-pm) - a gate nobody scheduled is a wish.

## Step 2 - walk the phases

Each phase: **confirm entry conditions -> do the steps (owning skill) -> produce the
artifacts -> RUN THE EXIT GATE -> record the result -> advance.** Never advance past an
unmet gate silently - either meet it, or log the exception as a RAID/yellow item with an
owner. Gate states are three-valued (quality-gates.md "Carried-exception status"): a
**CARRIED** gate (what's missing + who accepted + when it closes) is an ALLOWED phase
exit; an **UNMET** one is not - that distinction is what makes this rule enforceable
rather than aspirational. Full check definitions: [quality-gates.md](quality-gates.md).

| # | Phase | Do (owning skill) | Artifacts | Exit gate |
|---|---|---|---|---|
| 1 | Qualify & estimate (i) | wd-estimate: qualification, LOE, timeline, UET, proposal | Estimate + proposal | Calibration cross-check; proposal claims sourced |
| 2 | Contract (i) | wd-contracts from the estimate | SOW/SaaS DRAFT | DRAFT-for-legal stamp; deviations flagged |
| 3 | Kickoff | Lifecycle kickoff checklist + client onboarding packet + sponsor charter (wd-pm) + tracker/RAID stood up + ai-data-governance terms confirmed | Packet, charter, tracker, this Delivery Tracker | Every kickoff-checklist box checked or RAID'd |
| 4 | Discovery | wd-discovery (playbook A/B/C) + outcome-metric baselines + solution options (net-new) | Discovery doc, baselines, options memo | Solution-options recommendation approved by named client approver |
| 5 | Design | wd-design-doc + wd-design-visuals + wd-pm meeting-intake after every session; unit scenarios derived NOW (wd-testing) | Design doc + visuals + scenario list | Gap-analysis clean (incl. SOW-conformance); client sign-off; baseline archived |
| 6 | Architecture review | wd-extend-dev architecture-review.md (reviewer != designer) | ADR-lite in Tech Spec tab | All checklist rows pass; findings fixed or logged |
| 7 | Build | **ENTRY (hard): measure-twice requirements captured - the SECURITY section (domains/ISU/ISSG/segments/scopes) enumerated from the design + owning skills; a blank security section = DO NOT ENTER BUILD** (quality-gates.md "Measure twice"). Then: wd-extend-dev for O4I, or wd-integration-dev for EIB/Studio/CC/DT (integration-build/studio refs): PoC first + acceptance demo, then build; standards, efficiency, citizenship; pull-latest+diff on shared apps; bi-weekly build demos (wd-demo) | PoC (accepted), working code, demo cadence | Gotcha sweep + validator per touched artifact; comments current |
| 8 | Test | wd-testing: derive/execute scenarios, UAT (tester experience!), triage; **browser-driven execution of the plan against the running app with captured evidence (wd-test-execution)**; API-headless smoke/regression (wd-testing automation-harness) | Results on Unit Testing tab (with evidence); UAT sign-off | Scenarios pass incl. negative security tests; each run evidenced; defects triaged; sign-off artifact |
| 9 | Deploy & cutover | wd-deployment: Volumes Questionnaire (+ Perf if >50K) **for Extend apps**, promotion + per-tenant re-setup, cutover plan, go/no-go (incl. people-readiness); **per-tenant setup runnable live via the browser, confirm-each-write, dev/sandbox only (wd-tenant-config)** | Gating docs, cutover plan, deployment guide | Extend apps: Workday prod approval. Integrations: migration-checklist Complete per tenant + DART clean. Both: go/no-go passed; security re-setup verified per tenant |
| 10 | KT & handoff | wd-kt: guides (user/admin/runbook/deployment), KT sessions, teach-backs | The doc set + KT sign-off | Security-section domain tables populated; runbook triage tree present; teach-backs done |
| 11 | Hypercare & adoption | wd-post-go-live: monitoring, adoption-and-feedback, 30/60/90 value checks | Value snapshots, CSAT pulse | Adoption metric watched; unmet KPIs get named follow-ups |
| 12 | Closeout | wd-post-go-live handoff-and-closeout: actuals (i), firm-access revocation, tech-debt transfer, reference-rights (i), case study (i) | Closeout artifact, value snapshot | Every closeout-checklist row checked; client countersigns access removal |
| 13 | Steady state | QBR/renewal (account-growth) (i) / release regression each R1/R2 / enhancements via the Change path | QBR decks, regression results | Regression after every release; QBR before renewal windows |

**Integrations-only projects**: same walk; phases 4-5 use the integration variants
(integration-discovery questionnaire, the IDD); phase 7 uses wd-integration-dev integration-build.md/studio.md;
**phase 9's Workday prod-approval gate and Volumes Questionnaire apply to Extend apps ONLY -
the integrations exit gate is the migration checklist Complete per tenant + DART clean +
cutover plan**; phase 10 uses the INT KT template.
**Programs**: every app walks this table individually; the program adds wd-pm
program-mode's registers (dependency, tech-debt, capacity) reviewed at each phase-5 gate,
plus steering cadence (steering-committee.md) from phase 3.

Gates that assert tenant state - security re-setup per tenant, data seeded, no in-flight BPs at cutover, adoption watched - are assertable live via tenant-ops reads; record the read result as the tracker's gate evidence (wd-extend-dev references/tenant-ops.md).

## Technical inputs & client access by phase (the reference thread)

The suite's technical knowledge is filed by topic; this map surfaces, per phase, WHICH facts to pull and WHICH client access should already be provisioned - so nothing load-bearing is discovered late. Client-access column follows the staged plan in [customer-technical-roles.md](customer-technical-roles.md).

| Phase | Technical facts to pull | Client access provisioned by now |
|---|---|---|
| Kickoff | Platform opt-in (O4I/Extend SKU); tenant landscape + gateway hosts (`wdcli tenant list`); prerequisites.md | Security Partner + SLA; Community + dev-tenant/dev-site accounts requested |
| Discovery | Existing data sources / custom objects / integrations - read live (tenant-ops); API-surface feasibility (rest-api-catalog + WSDL fetch) | Builders: read + sandbox to start learning; Prism/Reporting: read to explore |
| Design | Per-op `x-workday-secured-by-domains` (rest-api-catalog) -> the design's domain list -> hand to the Security Partner EARLY; RefID/data-source liveness (tenant-ops) | Extend devs: dev tenant + App Manager; Prism/Reporting: create/manage domains as their design lands |
| Build | pmd-gotchas / model / orchestration / studio refs; **data-loading-and-retrieval.md (load-in/read-out decision map + landmines)**; app-catalog samples for shapes; validator + retry-config patterns; seed test data + browser-validate the running app as you go (wd-tenant-config / wd-test-execution) | Full build domains per role; ISU/ISSG; app functional-area domains (S22 until granted) |
| Test | Scenario data seeded via tenant-ops patterns or the browser (wd-tenant-config); browser-driven execution + evidence (wd-test-execution); systemMetrics for perf evidence | Client testers: end-user security; team runs alongside |
| Deploy | migration-checklist; Volumes/Perf gating docs; the tenant-readiness read-set per tenant | Per-tenant re-grant (access does NOT promote) - verify, don't assume |
| Run | data-retention/export patterns; release-impact watch (+ re-export REST schemas each R1/R2) | Support/admin domains to the ongoing owners |

The recurring lesson: the **secured-by-domains for what you're building is knowable at design** - pull it then and give the Security Partner runway, so go-live isn't the first time they see the grant list.

## The consultative stance (how to behave in this mode)

- **Drive, don't wait.** Each session: state where the project is, do the next step, name
  the coming gate. End with "next time we...".
- **One gate at a time for novices** - don't dump the full table on someone at phase 3.
- **Refuse to skip gates cheerfully.** "We can absolutely move faster - the gate exists
  because X; here's the 20-minute version" beats silent compliance AND beats lecturing.
- **One exit per phase.** In guided mode every phase has exactly one allowed exit: the
  next phase's entry gate. When a phase completes, say so - "the only exit from here is
  the architecture review" - and decline mid-flow jumps to unrelated phases ("while we're
  at it, let's draft the user guide" during design). Park those asks as notes on the
  Delivery Tracker and return to them when their phase arrives; otherwise the walkthrough
  dissolves into ad-hoc task-hopping and the gates stop meaning anything. (Pattern from a
  community skill-craft survey, 2026-08-06 - rebuilt for this suite.)
- **Artifacts are born from templates, never from scratch** (bundled assets + build-specs);
  quality checks run before the user ever sees a draft labeled final.
- **Every report-out is consistent**: status (wd-pm format), SteerCo (deck skeleton),
  demos (wd-demo structure) - same shapes every time, so quality is recognizable.
- **Fence every step the user takes OUTSIDE the session** (suite-wide convention, owner-set
  2026-08-06). Tenant UI tasks, interactive logins (`wdcli`, browsers), hidden-prompt
  credential entry, emails to third parties - these are where users get lost, because they
  cross out of the conversation. Present them as a clearly labeled **"Your steps (outside
  this session)"** numbered block, never interleaved with narrative or with steps Claude
  runs. Each step names WHERE it happens (which terminal / tenant / Workday screen);
  prompts and forms get a per-prompt table of exact values (never "enter the credentials");
  say what the user will SEE ("hidden prompt - pasting shows nothing; paste, press Enter",
  "the secret displays once - keep the window open"); end with the handshake: how to say
  it's done and what Claude runs to verify. Worked example: the First-time setup runbook in
  wd-extend-dev references/tenant-ops.md.
