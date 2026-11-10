---
name: wd-project-delivery
description: "Use for running a Workday engagement day to day: meeting agendas, project plans, timelines, weekly status reports, RAID log, action items, turning a meeting transcript into decisions and actions, Smartsheet tracker updates, client emails, Teams posts, escalation notes and go-live announcements, user guides, admin guides, runbooks, release notes, training decks and knowledge-transfer sessions, organizational change management (stakeholder analysis, change impact, communications plan, training plan, adoption metrics), and preparing or scripting a demo."
---

# Project management, communications, training and change

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

### wd-pm

**Use for:** Project-management routines for Workday Extend delivery - agendas, project plans, timelines, status reports, weekly status, RAID (risks and issues), action items, follow-ups, task trackers, milestones, and "who owns what" questions. Use when asked for a meeting agenda, a project plan or timeline, a weekly status report, a RAID log update, action-item capture or follow-up review, a task tracker, milestone tracking, or program-level coordination across multiple Extend apps and integrations. Also owns meeting intake: a pasted or attached meeting transcript, a Teams/Zoom transcript, meeting recording or notes, or "update the design/tracker from this meeting" WITH the transcript provided - it extracts decisions/answers/actions and delegates the edits. Authoring a recap or minutes WITHOUT source input belongs to wd-comms. This skill owns PM content and routines; Smartsheet API mechanics belong to wd-smartsheet (this skill calls it for transport).

**Start here:** `wd-pm/GUIDE.md`

**Reference files:**

- `wd-pm/references/client-onboarding-packet.md` - Client Onboarding Packet - What We Need From You, By When
- `wd-pm/references/meeting-intake.md` - Meeting Intake - Transcript -> Synchronized Artifacts
- `wd-pm/references/program-mode.md` - Program Mode - Coordinating Multiple Extend Apps
- `wd-pm/references/project-plan-format.md` - Project Plan Format (Smartsheet-Importable Excel)
- `wd-pm/references/raid-log.md` - RAID Log + CR Log + Decisions Discipline
- `wd-pm/references/scripts.md` - Scripts this skill uses - regenerate-on-demand build-spec
- `wd-pm/references/status-reporting.md` - Weekly Status Reporting
- `wd-pm/references/steering-committee.md` - Steering Committee & Sponsor Governance

### wd-smartsheet

**Use for:** Read and update Smartsheet sheets, rows, and project trackers via the Smartsheet REST API (using a personal API access token; MCP not available on some managed/corporate machines). Use when the user mentions Smartsheet, says "update the tracker", references the RAID log, project plan rows, a sheet ID, needs to find a workspace/sheet, needs help getting a Smartsheet API token, or asks to "mark task complete in smartsheet" - any task that reads from or writes to a Smartsheet sheet, report, or workspace.

**Start here:** `wd-smartsheet/GUIDE.md`

**Reference files:**

- `wd-smartsheet/references/api-details.md` - Smartsheet REST API - detail reference
- `wd-smartsheet/references/install.md` - Installing this skill - plain-language guide (start here)
- `wd-smartsheet/references/scripts.md` - Scripts this skill uses - regenerate-on-demand build-spec
- `wd-smartsheet/references/smartsheet-registry-template.md` - Smartsheet Sheet Registry - per-engagement template
- `wd-smartsheet/references/sync-contract.md` - Two-way sync - column ownership (anti-clobber)
- `wd-smartsheet/references/token-setup.md` - Get your Smartsheet API token (novice guide)

### wd-comms

**Use for:** Draft CLIENT-FACING project communications for Workday Extend engagements - status emails, Teams posts, escalation notes, decision-needed emails, meeting recaps, announcements, go-live comms, stakeholder updates. Trigger on: "draft an email to the client", "Teams post", "status email", "escalation note", "announcement", "go-live comms", "stakeholder update", "let the client know". Owns message content, tone, and per-client branding profiles. For firm-internal deliverables (decks, proposals), use neutral formatting; for Word/PowerPoint file mechanics use the docx/pptx skills - this skill owns message content, tone, and client-branding profiles. Meeting recaps here are authored WITHOUT source input; if a transcript, recording, or meeting notes are PROVIDED, wd-pm owns the extraction and delegates the recap.

**Start here:** `wd-comms/GUIDE.md`

**Reference files:**

- `wd-comms/references/client-branding.md` - Client branding profiles - capture-once pattern
- `wd-comms/references/clients--_template.md` - Client branding profile - <Client Name>
- `wd-comms/references/scripts.md` - Scripts this skill uses - regenerate-on-demand build-spec
- `wd-comms/references/templates.md` - Message templates

### wd-kt

**Use for:** Knowledge transfer and client enablement for Workday Extend apps - user guides, admin guides, training, documentation for the client, handoff to client developers, runbooks, KT sessions, teach-the-client-team enablement. Also owns RELEASE NOTES authoring, the per-integration KT document, and the training/facilitator DECK. Use when producing any end-of-project documentation (user guide, admin/config guide, support runbook), release notes for an enhancement, the integration KT document, a training/facilitator deck, planning or running KT/training sessions, or transitioning code ownership to client developers.

**Start here:** `wd-kt/GUIDE.md`

**Reference files:**

- `wd-kt/references/client-dev-enablement.md` - Client-Developer Enablement
- `wd-kt/references/dual-audience-spec.md` - Dual-Audience Document Pattern (Part 1 Business / Part 2 Technical)
- `wd-kt/references/int-kt-template.md` - Integration KT Document - the per-integration handoff reference
- `wd-kt/references/kt-sessions.md` - KT Session Planning
- `wd-kt/references/rebrand-and-screenshot-mask.md` - Rebrand a deliverable + OCR-mask sensitive data in screenshots
- `wd-kt/references/scripts.md` - Scripts this skill uses - bundled template builders + regenerate-on-demand
- `wd-kt/references/training-deck.md` - Training / facilitator deck
- `wd-kt/references/triage-runbook-pattern.md` - Triage Runbook Pattern - The Support-Desk Deliverable
- `wd-kt/references/user-guide-pattern.md` - User Guide Pattern

### wd-change-adoption

**Use for:** Plan and run the organizational change management (OCM) and user-adoption workstream for a Workday program - the people side that runs parallel to the build so users actually adopt what ships. Use for change management, OCM, a change plan / strategy, stakeholder analysis, change-impact assessment, change readiness (assessment/survey), a change network / champions / super-users, a communications PLAN or matrix (program-level who/what/when/channel), training-needs analysis or a role-based training PLAN, adoption metrics, resistance management, or "build the change plan / how do we drive adoption". Use THIS for the OCM program structure and its planning artifacts; an individual client-facing MESSAGE is wd-comms (THIS owns the comms PLAN that tells it what to write); training CONTENT, guides, job aids, and KT sessions are wd-kt (THIS owns the training PLAN that scopes them); post-go-live adoption feedback is wd-post-go-live; project plan / RAID / status is wd-pm.

**Start here:** `wd-change-adoption/GUIDE.md`

**Reference files:**

- `wd-change-adoption/references/adoption-measurement.md` - Adoption measurement
- `wd-change-adoption/references/comms-and-training-plan.md` - Communications plan & training plan
- `wd-change-adoption/references/impact-and-readiness.md` - Impact, readiness, stakeholders & the change network

### wd-demo

**Use for:** Stage and deliver demos of Workday Extend apps - demo prep, demo scripts for delivery-track demos, demo-tenant staging and seed data, demo dry runs, and handling live questions. Trigger on: demo, demo prep, demo script, demo tenant, demo data, PoC demo, build demo, steering/SteerCo demo, prospect demo, "show the app", "walk the client through it", dry run before a demo, or resetting a tenant between demos. Owns tenant staging and delivery-track demo craft; the productized Marketplace demo-script/deck artifacts belong to bow-sales-enablement (this skill points there).

**Start here:** `wd-demo/GUIDE.md`

**Reference files:**

- `wd-demo/references/demo-playbook.md` - Demo Playbook - Staging, Track Variants, Live-Question Triage

## Suite map (where every skill lives)

- **wd-suite-router**: practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract**: market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design**: wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build**: wd-extend-dev, wd-auth
- **wd-integration-build**: wd-integration-dev
- **wd-test-deploy-run**: wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery** (this skill): wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build**: app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: `bow-sales-enablement`, `product-gtm`, `wd-suite-feedback`. If a guide points to one of these, say that content is not included.
