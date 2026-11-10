---
name: wd-test-deploy-run
description: "Use for Workday Extend and integration testing, deployment and run: deriving unit test scenarios, UAT planning, deciding defect versus change request, writing a test execution plan and evidence record, tenant promotion across development, implementation, sandbox and production, cutover and go-live planning, data conversion, the Workday production-approval documents (volumes questionnaire, performance testing), tenant setup recipes, end-user security design and segregation of duties, creating test data, hypercare, production integration failure triage, data retention and export, release regression and closeout."
---

# Testing, deployment, tenant setup and post-go-live

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

### wd-testing

**Use for:** DERIVES the test scenarios and runs the testing lifecycle for Workday Extend apps and integrations - unit test scenario derivation (at design time), UAT planning and support, and E2E/UAT defect and change-request triage. Use when the user mentions unit test, test scenarios, test scripts, UAT, defect, bug logged, change request, E2E, test results, regression, or asks "did we test", "was this tested", or "is this a bug or a CR". Owns scenario-derivation methodology and defect-vs-CR triage decisions. Use THIS for DERIVING scenarios / UAT / triage; for browser-driven EXECUTION of the plan see wd-test-execution; the design doc's Unit Testing tab format see wd-design-doc; code fixes see wd-extend-dev; performance testing see wd-deployment.

**Start here:** `wd-testing/GUIDE.md`

**Reference files:**

- `wd-testing/references/agent-testing.md` - Agent and API metering test considerations
- `wd-testing/references/automation-harness.md` - Test-automation / regression harness
- `wd-testing/references/defect-triage.md` - Defect & Change-Request Triage - E2E/UAT Decision Tree
- `wd-testing/references/integration-testing.md` - Functional testing of traditional integrations (EIB / Studio / CC / DT / O4I-as-INT)
- `wd-testing/references/uat-support.md` - UAT Support - Client-Executed, Consultant-Supported
- `wd-testing/references/unit-testing.md` - Unit Testing - Derivation Method and Execution Detail

### wd-test-execution

**Use for:** DRIVES the in-app browser to RUN a written test plan and capture evidence - navigates the deployed Extend app / integration and its tenant via the Browser pane (mcp__Claude_Browser__*), exercises each scenario, asserts the observable result, captures screenshots / console / network reads, and records pass/fail. Use when the user says "test the app" (a bare "test the app" defaults here - run it), "test the app in the browser", "run the test plan", "validate these scenarios", "click through the app and check it works", "walk the app", or turn a written plan into an actual executed run with proof. Use THIS for browser-driven EXECUTION + evidence; for DERIVING scenarios / UAT scripts / defect-vs-CR triage see wd-testing; API-driven headless smoke/regression see wd-testing automation-harness.md; driving the browser to CONFIGURE a tenant or create test data see wd-tenant-config; code fixes see wd-extend-dev. NEVER types credentials, MFA codes, or CAPTCHAs - login is a user handoff (wd-auth).

**Start here:** `wd-test-execution/GUIDE.md`

**Reference files:**

- `wd-test-execution/references/accessibility-execution.md` - Accessibility execution - verifying a11y against the BUILT app
- `wd-test-execution/references/app-log-stream.md` - Reading an Extend app's own diagnostics (the developer-site log stream)
- `wd-test-execution/references/browser-mechanics.md` - Driving the in-app Browser pane against Workday
- `wd-test-execution/references/execution-workflow.md` - The run loop, assertions, evidence, and reporting
- `wd-test-execution/references/recording-review.md` - Reviewing a tester's screen recording
- `wd-test-execution/references/scenario-flows.md` - Standard reusable test-scenario flow templates
- `wd-test-execution/references/scripts.md` - Scripts - build-specs + usage
- `wd-test-execution/references/test-plan.md` - The executable test-plan format

### wd-deployment

**Use for:** Workday Extend deployment lifecycle, the tenant-setup RECIPE CONTENT, and the end-user SECURITY MODEL. Owns tenant promotion (DEV, IMPL, SBX, PROD), cutover and data-conversion planning, go-live EXECUTION, and Workday's production-approval docs (Extend Volumes Questionnaire, Performance Testing Template). Owns the setup recipes (R1-R12: security domains, ISU/API clients, App Attributes, BP config, schedules) and the client's production security design (roles, security groups, constrained vs unconstrained, segregation of duties / SoD, security design workbook) - the security HUB that maps every security question to its owner. Use when the user says deploy to production, promote, sandbox, impl tenant, cutover, go-live, the tenant-setup recipe, migrate the app, data conversion, volumes questionnaire, performance testing, or security design. DRIVING the browser to do setup or test data live is wd-tenant-config; wdcli build/deploy ERRORS are wd-extend-dev; hypercare/closeout is wd-post-go-live.

**Start here:** `wd-deployment/GUIDE.md`

**Reference files:**

- `wd-deployment/references/bp-configuration-admin.md` - Business process configuration - native tenant BPs
- `wd-deployment/references/configurable-security-admin.md` - Workday configurable security - the concept and rules layer
- `wd-deployment/references/cutover-planning.md` - Cutover Planning - Data Conversion, Legacy Coordination, Go-Live
- `wd-deployment/references/deployment-guide.md` - Deployment Guide - The Client-Facing Deliverable Pattern
- `wd-deployment/references/go-live-agent-checklist.md` - Agent & Flex Credit Go-Live Checklist
- `wd-deployment/references/marketplace-recert.md` - Marketplace Re-Certification - Enhancing an Already-Shipped BoW App
- `wd-deployment/references/migration-checklist.md` - Integration Migration Checklist - per-integration tenant-migration tracker
- `wd-deployment/references/migration-readiness-gates.md` - Migration Readiness Gates - wave go/no-go for a phased data conversion
- `wd-deployment/references/perf-testing-template.md` - Extend Performance Testing Template - How to Complete It
- `wd-deployment/references/promotion-and-environments.md` - Tenant Promotion & Environments
- `wd-deployment/references/scripts.md` - Scripts this skill references - regenerate-on-demand build-specs
- `wd-deployment/references/security-questionnaire.md` - Client Security / InfoSec Questionnaire - Answer Bank for an Extend App
- `wd-deployment/references/security-role-design.md` - Client production security-role design (the end-user security model)
- `wd-deployment/references/security-setup-section.md` - The Security Setup Section - the novice spec every guide embeds
- `wd-deployment/references/tenant-setup-guide.md` - Tenant Setup Guide - The Deliverable Pattern
- `wd-deployment/references/tenant-task-recipes.md` - Tenant-Task Recipe Library
- `wd-deployment/references/volumes-questionnaire.md` - Extend Volumes Questionnaire - How to Complete It

### wd-tenant-config

**Use for:** LIVE BROWSER EXECUTION of Workday in-tenant setup and test-data creation - drives the in-app Browser pane (mcp__Claude_Browser__*) to run the tenant-setup recipes (ISU/ISSG, security domains, API clients, App Attributes, BP config, schedules) and create synthetic test records (workers, orgs, cost centers) in a DEV/SANDBOX tenant, plan-first and confirming each write. Use when the user is in a tenant and says "set up the tenant", "configure this in the tenant", "grant the security", "create test data / seed some records", "make a few test workers", "do the tenant setup for this app", or "walk the recipe live". The setup RECIPE CONTENT (R1-R12) and security-model design are wd-deployment; test EXECUTION of an app is wd-test-execution; bulk data via EIB/API is wd-integration-dev / wd-extend-dev; browser login handoff is wd-auth. NEVER types credentials/MFA/CAPTCHAs, NEVER modifies security or system settings itself, NEVER touches production or real customer data.

**Start here:** `wd-tenant-config/GUIDE.md`

**Reference files:**

- `wd-tenant-config/references/config-execution.md` - Config execution - driving the setup recipes in the browser
- `wd-tenant-config/references/config-flows.md` - Config flows - named, browser-executable tenant configuration procedures
- `wd-tenant-config/references/safety-and-scope.md` - Safety and scope - the load-bearing rules for driving a tenant
- `wd-tenant-config/references/test-data.md` - Test data - creating synthetic records in-tenant via the browser

### wd-post-go-live

**Use for:** Run the post-go-live phase of a Workday Extend app - hypercare, production support and monitoring, data retention and archival, exporting Extend data (BO REST, RaaS, WQL, LDQ, Prism export), twice-yearly Workday RELEASE regression, support handoff, closeout, and warranty. Also owns production integration-failure triage - diagnose a failed run, find the error, event status and logs ("the integration failed, where's the log", "the nightly integration errored", "check the process monitor"). Use when the app is live ("app is live now what"), planning hypercare, answering data-retention/audit questions, exporting Extend or Prism data, triaging a live integration failure, moving to steady-state support, or closing out the engagement. WQL/RaaS query-authoring PATTERNS and code fixes for production incidents are wd-extend-dev; general/UAT regression methodology is wd-testing.

**Start here:** `wd-post-go-live/GUIDE.md`

**Reference files:**

- `wd-post-go-live/references/account-growth.md` - Account Growth - from delivered app to program of work
- `wd-post-go-live/references/adoption-and-feedback.md` - Adoption & Feedback - Getting the App Used, Not Just Live
- `wd-post-go-live/references/data-retention-export.md` - Data Retention & Export for Live Extend Apps
- `wd-post-go-live/references/dsar-runbook.md` - DSAR / Erasure Runbook - Servicing a Data-Subject Request Against a Live Extend App
- `wd-post-go-live/references/handoff-and-closeout.md` - Handoff & Closeout
- `wd-post-go-live/references/managed-services.md` - Managed Services - Steady-State Production Support
- `wd-post-go-live/references/release-regression.md` - Workday Release Regression for Live Extend Apps
- `wd-post-go-live/references/value-capture.md` - Value Capture - proving the app was worth building

## Suite map (where every skill lives)

- **wd-suite-router**: practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, wd-suite-feedback, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract**: market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design**: wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build**: wd-extend-dev, wd-auth
- **wd-integration-build**: wd-integration-dev
- **wd-test-deploy-run** (this skill): wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery**: wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build**: app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: the Marketplace sales-enablement and product go-to-market skills. If a guide points to `bow-sales-enablement` or `product-gtm`, say that content is not included.
