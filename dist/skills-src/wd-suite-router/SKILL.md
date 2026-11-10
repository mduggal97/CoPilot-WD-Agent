---
name: wd-suite-router
description: "Front door for Workday practice work. Use when the user is starting something new, asks what to do next, which phase a project is in, which skill handles a task, or wants to be walked through a Workday Extend or integration project start to finish. Also owns the delivery quality gates, the kickoff checklist, the AI data-handling rules, full-program Workday deployment methodology (phases, roles, RACI, governance, configuration guides), practice operations (onboarding, certifications, staffing, utilization, partner program), project-folder structure and archiving rules, and splitting work across sessions."
---

# Suite router, methodology and practice operations

This skill bundles several skills from the Workday Practice Delivery suite.
Each one lives in its own folder with its full method in `GUIDE.md`.

## How to use this skill

1. **Pick the one member skill** below that owns the task.
2. **Read that member's `GUIDE.md` first.** It is the full method. Do not answer from the summary here.
3. **Open only the reference files the guide points to.** Paths inside a guide are relative to that member's folder.
4. **Follow the guide's quality check** before presenting work as final, and report the check result with the deliverable.
5. **Never invent Workday facts.** If the guide and its references do not cover it, say so.

## Reading a guide written for another tool

The guides were written for Claude Code, which runs on the user's own machine. Translate as you read:

- **"SKILL.md" of a named skill** means that skill's `GUIDE.md`.
- **"Invoke skill X" or "route to X"** means open X's guide. Find X in the suite map below.
- **`../<skill>/references/<file>`** points at another member's folder, possibly in another skill.
- **`scripts/...` files are not included here.** Describe what the script does and produce the result by hand, or hand the step off.
- **You cannot run `wdcli`, call a live Workday tenant or Smartsheet, drive a browser, or touch local folders.**
  - Do the design, plan, draft, payload or row values here.
  - Then name the boundary plainly and give the exact steps under a heading **"Finish this on your machine"**.
  - Never say or imply that a live action ran.
- **Never ask for, accept or repeat a password, token or API key.**

## Member skills

### practice-lifecycle

**Use for:** The TOP-LEVEL front door for the Workday Practice Delivery and Innovation suite: forks the two tracks and points to the right router. Use when starting something new and unsure of the track, when the request is "build a tool / build an app / build a product / an internal accelerator" and is NOT obviously a Workday Extend app, or for "which track / where do I start / what can this suite do". TRIGGERS: "build a tool", "build an app", "build a product", "internal tool", "accelerator", "not a Workday app", "which skill / which track", "where do I start", "what do you want to build", "productize this". Track 1, WORKDAY DELIVERY (a client Extend/Integration project): wd-extend-lifecycle. Track 2, BUILD A TOOL/PRODUCT (a web app or agentic tool on AWS, not an Extend app): app-architecture, plus market-research for whether to build. A clearly Workday delivery phase (estimate, discover, design, Extend build, tenant, deploy) goes straight to wd-extend-lifecycle.

**Start here:** `practice-lifecycle/GUIDE.md`

### wd-extend-lifecycle

**Use for:** The map of the Workday Extend/Integration delivery lifecycle and its mandatory steps - and the GUIDED walkthrough that leads any user (novice to expert, colleague or client) through a project start to finish with enforced quality gates. Use this skill when starting a new Extend or integration project or phase, when the user says "walk me through it" / "what do I do next" / "I've never done this before", when asking "what's next / what am I forgetting / which skill handles X", at project kickoff, when planning phase transitions (design sign-off, build complete, go-live approaching), or for the checklist of Workday-required documents (Volumes Questionnaire, Performance Testing) and client prerequisites. Invoke directly with /wd-extend-lifecycle for the full phase map. Also the entry point for suite setup on a new machine ("set up this suite for me" - prerequisites, Python packages, script regeneration) and for "which skill handles X" routing questions.

**Start here:** `wd-extend-lifecycle/GUIDE.md`

**Reference files:**

- `wd-extend-lifecycle/references/ai-data-governance.md` - AI & client-data governance - the gate before anything client goes into an AI tool
- `wd-extend-lifecycle/references/customer-technical-roles.md` - Customer technical roles, access & enablement - set the client's team up for success
- `wd-extend-lifecycle/references/deliverable-review.md` - Deliverable review - read it as the reviewer, before it ships (suite-wide)
- `wd-extend-lifecycle/references/guided-delivery.md` - Guided delivery - walk any user through a project, start to finish
- `wd-extend-lifecycle/references/operational-preflight.md` - Operational pre-flight and build hygiene - do it right the first time
- `wd-extend-lifecycle/references/platform-compatibility.md` - Where these skills run - Claude Code vs claude.ai
- `wd-extend-lifecycle/references/prerequisites.md` - Suite prerequisites & script portability - read this first on a new machine
- `wd-extend-lifecycle/references/quality-gates.md` - Quality gates - the every-time enforcement registry
- `wd-extend-lifecycle/references/scripts.md` - Scripts this skill ships - build-specs
- `wd-extend-lifecycle/references/verify-in-tenant.md` - Verify-in-tenant - the standing "trust-but-verify" rule
- `wd-extend-lifecycle/references/writing-quality-gate.md` - Writing quality gate - the "AI draft -> release-ready" check (suite-wide)

### wd-delivery-methodology

**Use for:** Vendor-neutral full-program Workday delivery methodology: the phase model for a complete deployment (HCM, Financials, Student, Adaptive Planning, Prism), role playbooks and workstream RACI, standing delivery norms (RAID, configuration workbook, governance and decision rights, tenant strategy, testing ladder), the configuration-guide format, and the specialty tracks (Adaptive, Prism, release management, operating model, higher-ed). Use for how a full Workday deployment runs end to end, which phase a program is in, what a role does, a RACI, program governance, a configuration guide, or scoping a specialty track. Boundaries: the Extend/Integration build lifecycle and routing are wd-extend-lifecycle; this project's plan/RAID/status is wd-pm (staffing hours: wd-estimate); OCM is wd-change-adoption; test scenarios are wd-testing; promotion/cutover is wd-deployment; hypercare is wd-post-go-live. A firm-private methodology skill, if installed, layers on top and wins on conflict.

**Start here:** `wd-delivery-methodology/GUIDE.md`

**Reference files:**

- `wd-delivery-methodology/references/config-guide-pattern.md` - The configuration-guide pattern - format, reuse discipline, and building a library
- `wd-delivery-methodology/references/delivery-norms.md` - Standing delivery norms - the rhythms every program keeps
- `wd-delivery-methodology/references/phase-model.md` - The phase model - a full Workday deployment, end to end
- `wd-delivery-methodology/references/roles-and-raci.md` - Roles, counterparts, and the workstream RACI recipe
- `wd-delivery-methodology/references/specialty-tracks.md` - Specialty tracks - the workstreams that ride alongside a core deployment

### wd-practice-ops

**Use for:** Run the OPERATIONS of a Workday consulting practice - the meta layer that grows and runs the team, distinct from delivering any one engagement. Vendor-neutral practice management. Use for onboarding/ramping a new consultant, a competency / skills matrix, certification tracking (Workday Extend Pro, Integrations Pro, functional Pro certs, recerts), staffing / resourcing / bench / who-to-put-on-what, utilization or capacity planning across engagements, building the practice's enablement path, a reuse-asset catalog, or managing the Workday partner/alliance relationship (partner tier/status, Built-on-Workday / Innovation partner program, roadmap-intelligence intake). Use THIS for the practice layer; running a SINGLE engagement (plan/RAID/status/staffing-hours) is wd-pm; sizing/pricing a deal is wd-estimate; go-to-market for a productized app is bow-sales-enablement; the delivery craft is the wd-* delivery skills.

**Start here:** `wd-practice-ops/GUIDE.md`

**Reference files:**

- `wd-practice-ops/references/practitioner-enablement.md` - Practitioner enablement - onboarding, competency, certification
- `wd-practice-ops/references/reuse-and-asset-catalog.md` - Reusable-asset & IP catalog (build once, reuse many)
- `wd-practice-ops/references/staffing-and-alliance.md` - Staffing, capacity & the Workday alliance relationship

### session-orchestration

**Use for:** Fork work out to other agents, sessions, and models to parallelize, and pick the RIGHT model for each piece - route up (stronger) or down (cheaper) by task. Cross-cutting: applies to ANY Claude Code work in either suite track. Use when work could run in parallel, a job reads across many files, or a subtask wants a different model or another session. TRIGGERS: "fork this", "parallelize", "run these in parallel", "fan out", "delegate to another agent/session", "spin up agents", "which model should I use", "use a cheaper model", "use a stronger model", "route up/down", "background this", "have another session do X", "run this on a schedule", "too much to do in one session". Answers four questions: should I fork, to WHAT mechanism (subagent, peer or cloud session, scheduled run, Workflow), which MODEL, and how to dispatch so the result is trustworthy. The build-loop use of model tiers is app-harness; this skill owns the GENERAL forking and model-routing decision.

**Start here:** `session-orchestration/GUIDE.md`

**Reference files:**

- `session-orchestration/references/dispatch-discipline.md` - Dispatch discipline - how to delegate so the result is trustworthy
- `session-orchestration/references/mechanisms.md` - Mechanisms - where you can fork work to
- `session-orchestration/references/model-routing.md` - Model routing - up or down

### wd-folder-hygiene

**Use for:** Tidy a project/document folder by archiving superseded file versions into an Archive subfolder - keeping the latest of each, never deleting - AND scaffold the firm-standard numbered project-folder structure. Use when the user says clean up this folder, archive old versions, tidy the project folder, move outdated/old docs to an archive, "we have too many versions", declutter, or wants a folder of versioned deliverables (design docs v0.1..v2.0, proposals, IDDs, decks) reduced to just the current files. ALSO use to set up / scaffold a new project or app folder in the standard numbered structure (01_Assessment..08_Commercial, each with an Archive/ subfolder, plus _source/); and it owns the STANDING RULE that creating a new version of a deliverable auto-archives the prior version into that folder's Archive/. Plans first (dry run), confirms, then moves; writes a manifest so every move is reversible.

**Start here:** `wd-folder-hygiene/GUIDE.md`

**Reference files:**

- `wd-folder-hygiene/references/folder-structure-standard.md` - The standard project/app folder structure (firm standard)
- `wd-folder-hygiene/references/scripts.md` - Scripts this skill uses - bundled, with verbatim regeneration source
- `wd-folder-hygiene/references/versioning-and-archive.md` - Version detection, edge cases, and undo

## Suite map (where every skill lives)

- **wd-suite-router** (this skill): practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract**: market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design**: wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build**: wd-extend-dev, wd-auth
- **wd-integration-build**: wd-integration-dev
- **wd-test-deploy-run**: wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery**: wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build**: app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: `bow-sales-enablement`, `product-gtm`, `wd-suite-feedback`. If a guide points to one of these, say that content is not included.
