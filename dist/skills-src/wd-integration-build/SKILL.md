---
name: wd-integration-build
description: "Use for traditional Workday integrations: EIB inbound and outbound, Workday Studio assemblies, Core Connector, Document Transformation, XSLT, flat-file output, integration naming (integration IDs, integration system users and security groups), build and design checklists, migration, code review of Studio or EIB source, and inventorying a tenant's SOAP web services. Not for Orchestrate flows or Extend apps."
---

# Traditional Workday integrations

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

### wd-integration-dev

**Use for:** Build, review, and document TRADITIONAL Workday integrations - EIB (inbound/outbound), Workday Studio / CLAR assemblies, Core Connector, Connector with Document Transformation (DT), and the XSLT 3.0 behind them. Use for "build a Studio integration", EIB templates, Core Connector config, Document Transformation, XSLT/XTT/ETV flat-file output, Studio assembly vocabulary (assembly.xml, cc:, cloud:), MVEL, integration naming (INT IDs, ISU, ISSG, integration systems, security segments, calculated-field / sequence-generator names), build/design checklists, DART migration, code review of Studio or EIB source, or inventorying a tenant's SOAP web services (WWS) catalog (which operations an ISU can call, WSDLs). Small Studio or XSLT changes have migration and streaming landmines; consult before editing. Which web services a DOMAIN uses by design is wd-solution-playbooks; O4I / Orchestrate flows and Extend APPLICATIONS (PMD, pods, business objects, Model BPs, wdcli) are wd-extend-dev.

**Start here:** `wd-integration-dev/GUIDE.md`

**Reference files:**

- `wd-integration-dev/references/core-connector.md` - Core Connector - configuration, change detection, and the DIS security exception
- `wd-integration-dev/references/document-transformation.md` - Document Transformation (DT) - authoring guide + the O4I pre-formatter pattern
- `wd-integration-dev/references/eib.md` - EIB (Enterprise Interface Builder) - inbound and outbound walkthrough
- `wd-integration-dev/references/integration-build.md` - Traditional integration build - per-type guidance + build gates
- `wd-integration-dev/references/integration-naming.md` - Integration naming standards - INT IDs, ISUs, ISSGs, calc fields, and friends
- `wd-integration-dev/references/integration-review.md` - Integration review checklist - the reviewer's QA pass (IDD stage + Build/CLAR stage)
- `wd-integration-dev/references/scripts.md` - Scripts this skill references - regenerate-on-demand build-specs
- `wd-integration-dev/references/studio-patterns.md` - Workday Studio - named reusable patterns
- `wd-integration-dev/references/studio.md` - Workday Studio - project anatomy, assembly vocabulary, and when to use it
- `wd-integration-dev/references/wws-catalog.md` - Workday SOAP Web Services (WWS) - catalog retrieval
- `wd-integration-dev/references/xslt3.md` - XSLT 3.0 for Workday integrations - streaming, maps, and XTT/ETV

## Suite map (where every skill lives)

- **wd-suite-router**: practice-lifecycle, wd-extend-lifecycle, wd-delivery-methodology, wd-practice-ops, wd-suite-feedback, session-orchestration, wd-folder-hygiene
- **wd-scope-and-contract**: market-research, wd-estimate, wd-contracts, wd-discovery
- **wd-design**: wd-design-doc, wd-design-visuals, wd-systems-diagrams, wd-solution-playbooks
- **wd-extend-build**: wd-extend-dev, wd-auth
- **wd-integration-build** (this skill): wd-integration-dev
- **wd-test-deploy-run**: wd-testing, wd-test-execution, wd-deployment, wd-tenant-config, wd-post-go-live
- **wd-project-delivery**: wd-pm, wd-smartsheet, wd-comms, wd-kt, wd-change-adoption, wd-demo
- **tool-and-product-build**: app-architecture, app-hosting, app-agentic, app-harness, saas-integration, product-strategy, product-operations

Not in this agent: the Marketplace sales-enablement and product go-to-market skills. If a guide points to `bow-sales-enablement` or `product-gtm`, say that content is not included.
