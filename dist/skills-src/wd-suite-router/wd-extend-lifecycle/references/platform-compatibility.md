# Where these skills run - Claude Code vs claude.ai

These skills work across Claude surfaces, but the RUNTIME differs. The content (methodology, design
guidance, drafting) is identical everywhere; what changes is whether a skill's **local actions** can execute.
This page tells a user, at install time, what to expect - and tells Claude how to degrade gracefully instead
of failing when a task needs something the current environment cannot do.

## The two environments

- **Claude Code** (CLI / desktop / IDE): runs on the **user's own machine** - full filesystem, shell,
  Python + PowerShell, `wdcli`, Office/COM on Windows, local OS keychain, and the user's network (so live
  Workday/Smartsheet API calls work). This is the full-power environment the suite was built for.
- **claude.ai** (web) with Skills: runs a skill inside a **Linux code-execution sandbox**, NOT the user's
  machine. What that means:
  - **No Windows Office / COM** -> macro `.xlsm` (IDD, Volumes/Perf questionnaires) and Word-COM rendering
    do NOT run; the **openpyxl / python-docx** cross-platform paths DO.
  - **No PowerShell, no `wdcli`, no local files/folders, no OneDrive** -> anything that drives the local
    machine or a project folder is out.
  - **Restricted outbound network** -> live Workday REST/SOAP/WWS, `wdcli` deploy, Smartsheet API writes,
    and logo fetches generally will NOT run in the sandbox.
  - **No OS keychain / interactive terminal** -> the keyring + hidden-prompt credential flow is local-only;
    on claude.ai, secrets come via an enabled **MCP connector** or the action moves to Claude Code.
  - **Python doc-generation DOES run** (openpyxl, python-docx, reportlab, pandas, Pillow, PyMuPDF) -> design
    docs (non-macro), proposals, spreadsheets, and diagrams from UPLOADED data generate fine; file rendering
    can also defer to claude.ai's own docx/pptx/xlsx/pdf skills.
  - **Upload requirement: ASCII-clean** - claude.ai skill upload rejects non-ASCII; this suite is already
    ASCII-clean (enforced maintainer-side by `fix_suite_ascii.py`/`validate_suite.py` in
    `~/.claude/skill-asset-masters/_suite-maintenance/` before distribution), so it uploads cleanly.

## Compatibility by skill

**Legend:** **Full** = works on claude.ai as-is - **Partial** = the design/plan/author part works on
claude.ai; the marked feature needs Claude Code + the user's machine/tenant - **Claude Code** = needs the
local machine or a live tenant to do its core job.

| Skill | claude.ai | What needs Claude Code (the local/live part) |
|---|---|---|
| wd-extend-lifecycle | Full | the setup doctor reports the local machine (not the sandbox) - informational only |
| wd-discovery | Full | - |
| wd-estimate | Full | macro-heavy UET workbooks render best with Excel; openpyxl fill works in-sandbox |
| wd-contracts | Full | - (docx via python-docx) |
| wd-comms | Full | - |
| wd-kt | Full | - (docx via python-docx) |
| wd-change-adoption | Full | - |
| wd-pm | Full | live Smartsheet transport (below); the `.ps1` plan generator is Windows - the openpyxl/prose path works |
| wd-practice-ops | Full | - |
| market-research | Full | web research uses web search + public sources (available on both surfaces); the opportunity brief renders via python-docx/openpyxl in-sandbox |
| wd-delivery-methodology | Full | vendor-neutral - shareable wherever the rest of the wd-* suite goes |
| wd-testing | Full (design) | the live smoke/regression **automation harness** runs against a tenant -> Claude Code |
| wd-post-go-live | Full (plan) | live data export / monitoring reads hit the tenant -> Claude Code |
| wd-design-doc | Partial | the **IDD `.xlsm`** (macros/READ-ME text box) + COM formatting/render gates are Windows; non-macro `.xlsx` design docs build in-sandbox |
| wd-design-visuals | Partial | **Balsamiq** (.bmpr, desktop app) + draw.io-app clean exports need local; SVG/drawio-XML/bmpr-render generate in-sandbox. NOTE: Balsamiq/MCP may be BLOCKED entirely on managed machines (not just local-only) - draw.io wireframes are the first-class no-desktop-app path (SKILL.md "Wireframes") |
| wd-systems-diagrams | Partial | works from an **uploaded** inventory (headless Python); **live Smartsheet pull** + logo fetch need network -> Claude Code |
| wd-extend-dev | Partial | **design/review/author Extend+O4I = works**; **build/deploy/run, `wdcli`, live-tenant REST, spike-flow probes = Claude Code + your machine + tenant** |
| wd-integration-dev | Partial | author/review Studio/EIB/XSLT works; **DART/migration, tenant deploy, live WWS inventory = Claude Code** |
| wd-deployment | Partial | prompts/planning work; the two Workday `.xlsm` gating docs (COM) + per-tenant setup + promotion = Claude Code |
| bow-sales-enablement | Partial | GTM content works; the Node/weasyprint/LibreOffice render **build kit** is heavy - on claude.ai render via its docx/pptx skills instead |
| wd-auth | Full | guidance/decision-tree works anywhere; the credential flows it describes (keychain, hidden prompts, wdcli login) execute on the local machine |
| wd-demo | Full | demo-script authoring works; running a live demo hits the tenant -> Claude Code |
| wd-solution-playbooks | Full | - (reference content) |
| wd-test-execution | Partial | scenario walkthroughs/evidence docs draft anywhere; **live in-tenant execution + the browser-driven runs + validate_output_file.py on local files = Claude Code** |
| wd-suite-feedback | Partial | record drafting works anywhere; the scripts (log/triage/pull/autosync) need local Python + the OneDrive-synced folder -> Claude Code |
| wd-tenant-config | Claude Code | drives the **Workday tenant UI via the browser pane** - no browser pane / live tenant in the sandbox; config PLANS still draft anywhere |
| wd-smartsheet | Claude Code | reads/writes a **live** Smartsheet via REST + local keychain token - on claude.ai it can DRAFT the row/update, but writing needs Claude Code (or an enabled Smartsheet MCP connector) |
| wd-folder-hygiene | Claude Code | tidies a **local project folder** - there is no local folder in the claude.ai sandbox |
| practice-lifecycle | Full | routing/methodology - the top-level track fork; no local dependency |
| product-strategy | Full | the disposition decision + productization methodology - text-only |
| product-gtm | Full | GTM content authoring; heavy render defers to the docx/pptx skills, same as bow-sales-enablement |
| saas-integration | Full (guidance) | integration PATTERNS + platform references draft anywhere; running an actual integration is part of a hosted tool (Claude Code / the deployed runtime) |
| app-architecture | Full (design) | module-contract/topology/design methodology works anywhere; `scaffold_module.py` + the local-dev stack need local Python/Docker -> Claude Code |
| app-hosting | Full (design) | the AWS hosting playbook is guidance; the actual CloudFormation/CodeBuild deploy needs AWS creds + CLI on a machine -> Claude Code |
| app-agentic | Full (design) | provider-seam/tool-loop/eval methodology works anywhere; the runtime executes where the tool is deployed |
| app-harness | Full (guidance) | complexity-routing + guard-hook + testing methodology reads anywhere; the guard hooks + Claude Code build loop are Claude-Code features |
| session-orchestration | Full (guidance) | the fork/model-routing decision framework reads anywhere; the mechanisms it describes (subagents, cross-session, Workflow, scheduled/cloud) are Claude-Code features |

Roughly: ~23 skills Full/Full-guidance, ~9 Partial (author/plan on claude.ai, execute on Claude Code), ~3 need Claude Code (wd-tenant-config, wd-smartsheet writes, wd-folder-hygiene). The newest cohort (app-*, product-*, saas-integration, session-orchestration, practice-lifecycle) is Full/guidance - text-only methodology; their EXECUTION (AWS deploy, running an integration, the Claude Code orchestration features) lands on Claude Code + a machine.
for their core job. **No skill is broken on claude.ai** - the methodology and drafting always work; only the
local-machine / live-tenant execution moves.

## How Claude should degrade (the convention)

When a task hits a step the current environment cannot execute (a live-tenant call on claude.ai, a
Windows-COM `.xlsm`, a local-folder op, a `wdcli` deploy):
1. **Do everything you can here** - the design, the plan, the draft, the cross-platform document (openpyxl/
   python-docx/reportlab), the exact request payload or row values.
2. **Name the boundary explicitly** and hand the user the exact steps/commands to finish in **Claude Code on
   their machine** (or via an enabled MCP connector) - as a fenced "Run this in Claude Code" block. Never
   fail silently or pretend a live action happened.
3. **Prefer the cross-platform path** when one exists (openpyxl over Excel-COM; SVG over the draw.io app;
   python-docx over Word-COM) so more of the task completes in-sandbox.

## Install-time guidance (what to tell a recipient)

- On **Claude Code**: everything works once the setup doctor's core packages are in (prerequisites.md).
- On **claude.ai**: upload the skills (they're ASCII-clean, so they upload); expect the Full skills to work
  end to end, the Partial skills to do the design/draft with the execution step handed back to Claude Code,
  and wd-folder-hygiene / live wd-smartsheet writes to need Claude Code. Enable relevant MCP connectors
  (e.g. Smartsheet) to close some of the network gap.
