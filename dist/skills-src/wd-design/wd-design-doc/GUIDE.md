---
name: wd-design-doc
description: Author, update, and quality-check Workday Extend and Integration design documents in Excel - the 16/17-tab Extend template, client variants (e.g. a client-mandated 16-tab format), the BoW/Marketplace 10-tab template, the Integration Design Document (IDD), or a customer-specific template. Use this skill whenever the task involves a design document, design doc, functional/technical spec workbook, requirements tab, field specifications, object model tab, open items list, design gap review, design sign-off, or updating a design after a decision. Also owns the yellow-highlight open-items convention and design change control used across the whole delivery - consult it whenever those come up, even from other skills.
---

# Workday Extend / Integration Design Documents

The design doc is the project's contract: developers build from it, testers derive scenarios from it, the client signs it. Everything this skill enforces exists to keep that contract current, complete, and professional-looking in a client review.

## Choose the template family first

| Situation | Template | Reference |
|---|---|---|
| No template supplied or mandated | **Neutral default** (17-tab: 16-tab structure + KPI & Reporting) - **regenerate** with `python scripts/build_extend_design_doc.py`, then style with `scripts/xlsx_brand_style.py` (neutral by default; or obtain a branded master per engagement) | [references/16-tab-spec.md](references/16-tab-spec.md) for tab intents; [references/template-builder.md](references/template-builder.md) to regenerate/obtain a template or rebrand it |
| Client mandates a specific 16-tab format | **16-tab format** | [references/16-tab-spec.md](references/16-tab-spec.md) |
| Marketplace / BoW app (products team involved) | **BoW 10-tab template** - required by the Marketplace products team | [references/bow-template.md](references/bow-template.md) |
| Traditional integration (Studio/EIB/Connector or O4I delivered as an INT) | **Integration Design Document / IDD (.xlsm)** | [references/idd-template.md](references/idd-template.md) |
| Customer-supplied template | Use theirs; apply this skill's conventions (yellow rule, formatting, versioning) inside their structure. Census its fills with `--discover-roles` and record `templates/<slug>.json`, then the same G1-G18 gates run against it | [references/document-quality-gates.md](references/document-quality-gates.md) |
| Customer requests THEIR branding | Keep the structure and gates; swap only palette/fonts/logo via `brands/<client>.json` | [references/document-quality-gates.md](references/document-quality-gates.md) section  Branding policy |

Naming: `<CODE>_<Name>_Design_Document_v<major.minor>.xlsx` (e.g. `XTND010_Expense_Review_Design_Document_v2.0.xlsx`). Minor bump per working revision, major at sign-off milestones.

### Don't have a template? / Rebrand for a customer

See [references/template-builder.md](references/template-builder.md). Which scripts ship bundled vs. regenerate on demand (`build_extend_design_doc.py`, `build_idd_structure.py`, the styler/gate scripts) is catalogued in [references/scripts.md](references/scripts.md).

- **No template handy?** This skill no longer ships proprietary binary masters - **regenerate a working structural template from text**, or **obtain the branded master per engagement** (engagement store - see the environment memory). Extend: `python scripts/build_extend_design_doc.py` produces a faithful, complete 17-tab rebuild (no macros/logo, nothing lost). IDD: `python scripts/build_idd_structure.py` produces a **structural `.xlsx` skeleton** - all 22 sheets + headings + READ ME as cells, but **NOT the macro `.xlsm`**: the Integration-Type visibility macro, the ISU/ISSG auto-formulas, and the READ ME text box cannot be regenerated from text, so obtain the branded macro master when you need those. Both builders emit neutral/unbranded output; style it with `scripts/xlsx_brand_style.py`.
- **Rebrand to a customer's colors/logo?** Only when the user directs it (default = the neutral brand). Preferred: style the pre-style workbook with `scripts/xlsx_brand_style.py --brand-profile <client>`, then place their logo with `scripts/xlsx_place_wordmark.py`. To recolour an already-styled copy, or on a machine without Excel, run `scripts/rebrand_template.py` to produce a rebranded copy (never overwrites the source). Extend `.xlsx` = openpyxl cell recolor; IDD `.xlsm` = COM recolor + per-tab logo swap that preserves VBA/formulas.

## The yellow-highlight convention (owned here, used everywhere)

Any cell where information is missing or a follow-up is needed: solid yellow fill **FFFF00** plus text stating the actual question (e.g. `TBD - Q: who owns PV2 review?`). When the answer arrives: replace with the confirmed value and REMOVE the fill. Yellow = "still need to collect this" - it's the at-a-glance open-items signal in client reviews, so a yellow cell with no question in it is a bug.

- Best-effort derivable values: fill in the estimate marked "(est.)" - do NOT yellow those.
- Open Items tab: status Open / "Open - decided" / "Resolved - pending" -> full-row yellow; Closed/Resolved/Deferred -> no fill.
- On Discovery tabs, yellow BOTH the question and empty response cells.

## Professional formatting rules (all templates)

Client-facing workbooks are judged on polish before content. The bar: **a novice reader - not a seasoned developer - can follow the document without resizing a single column, cell, or font.** And the standing principle: leave every document better-formatted than you found it. The headline rules:

- **Text in a cell gets borders around it.** Populated content regions read as bordered tables, not floating text; tabular content lives in real tables (header row, one column per attribute), never prose clumped down a single column.
- **Ran out of template rows? INSERT rows carrying the table's formatting - and shift everything below down cleanly.** Overwriting content beneath a table, or appending unformatted rows, are both defects.
- **Never lose the template's formulas or formatting when filling it** (openpyxl can drop them - switch to COM or restore explicitly, and verify against the blank template). Full COM-vs-openpyxl rationale + the COM reliability gotchas live in one owner: [references/scripts.md](references/scripts.md) ("Why COM, not openpyxl").
- **Yellow cells always carry their question** - the FFFF00 fill AND text stating what's needed and the follow-up action.
- **No silently blank template tables** - populate (derive from existing design content) or add one yellow "TBD - none identified thus far (<date>)" row; revisit every TBD-none row at each version.
- **Final pass before any version goes out**: open every tab with fresh eyes at 100% zoom - clipped text, missing borders, clumped columns, lost formulas are what clients notice first; run a programmatic border/row-height checker when the doc was edited programmatically.

**The FULL checklist - including image-embedding geometry, border continuity/uniformity, gridline hygiene, style cloning, and the dated incident notes - is [references/formatting-checklist.md](references/formatting-checklist.md). Run it before ANY version goes out; the headlines above are not the whole bar.**

**Formatting is a MECHANICAL gate, not an eyeball pass (added 2026-08-06 after a client-facing miss).** Run on every Excel deliverable:

```bash
python scripts/xlsx_format_audit.py <workbook> [--fix]
```

It flags clipped text, missing wrap, wrapped-but-centre-aligned cells, images overlapping live content (rows never pushed down), and text under 4.5:1 contrast on its own fill (every tab, READ ME and hidden tabs included). Then **verify by render** - export a tab to PDF and look at it; a property check is not evidence a page reads correctly. Note **Excel's AutoFit silently ignores merged cells**, which is how a long narrative in a merged block ends up visibly cut off mid-sentence.

### Quality gates are brand-agnostic - [references/document-quality-gates.md](references/document-quality-gates.md)

**The 18 presentation gates (G1-G18) apply to every design doc regardless of source template or branding.** Branding picks colours, fonts and wordmark; it never decides whether the document is well made. That reference is the authority - the full gate table, the mandatory run ORDER (several steps undo each other if reordered, and widths must settle before heights), and the traps. Read it before any formatting pass, and report the gate result with the deliverable. **A mandatory content-coverage guard (`scripts/xlsx_coverage_guard.py`) runs after EVERY pipeline step and aborts if any cell value disappears** - the one check that catches a merge or reshape silently deleting content.

**Colour consistency is not layout consistency.** Unifying the palette (2 fonts, 2 sizes, 3 fills, 1 border neutral) leaves a document that can still read as ragged: section bands and table headers spanning different widths on the same tab, stacked tables with different right edges, one column starved to 10 wrapped lines while its neighbour sits idle, and rows of identical text at three different heights. G12-G15 (`xlsx_balance_columns.py`, `xlsx_normalize_layout.py`) exist for that, and they are where "it still looks inconsistent" feedback usually lands.

### Matching a hand-cleaned reference - the layout engine ([references/layout-engine.md](references/layout-engine.md))

The authoritative "how it works" is layout-engine.md; the build-outcomes record (what shipped and the traps that shaped it) is [references/layout-engine-findings.md](references/layout-engine-findings.md).

The mechanical passes RESTYLE a tab but cannot RE-LAY-OUT it: they inherit the template's cell topology. When a human cleans a tab they also choose column widths by judgment, group fields into panels, merge cells into callouts, and sometimes author new structure. Those LAYOUT decisions live in a per-tab spec - a **calibration**, `templates/layouts/<slug>.json` - and are reproduced deterministically:

- **Calibrate from the reference:** `python scripts/xlsx_extract_layout.py <hand-cleaned-copy> --tabs "..." --baseline <pre-style-backup-or-current-output> --write --calibration <doc-slug>` records per-tab `widths` and derives `structure` directives by diffing the reference against the baseline.
- **A calibration applies ONLY to its own document.** `--write` binds it to the baseline's identity cells (IDD: `Overview!J8` Integration ID + `J9` Integration Name, declared as `identity_cells` in `templates/idd.json`); every layout script asks `scripts/xlsx_layout_match.py` which calibration matches the workbook, and with no match the generic passes lay the tab out. Never put `tab_layouts` in a template profile - every script loads that profile by default, so one doc's widths and text landed on every regenerated IDD and Extend doc (2026-10-16). `check_profiles.py` fails the build if it happens again. An unbound calibration (`match` null) never applies; bind it once on its own pre-style backup with `python scripts/xlsx_layout_match.py <backup> --bind <slug>`.
- **Apply, safely:** `xlsx_apply_layout.py` sets the calibrated WIDTHS (widths only, by hard rule); `xlsx_apply_structure.py` applies the `structure` directives - `merge` / `unmerge` / `move` / `inject` / `border` (+ optional `row_pt`). Every merge **unmerges intersecting merges first** (so Excel can't absorb a neighbour - the cascade that once deleted a 27-row table), asserts its tail is empty, and asserts value-coverage before saving. **Merges are the LAST structural op** - `apply_structure` runs AFTER `normalize`, and within a tab merges come after moves/injects, so a band never merges empty.
- **Escape hatch:** when a tab is too bespoke to model, `xlsx_transplant_sheet.py` copies the fully-authored reference sheet wholesale (coverage + branding checked).
- **A calibration is taken FROM A SPECIFIC REFERENCE.** Its `inject`/`move` directives carry that reference's CONTENT and its widths fit that reference's columns, so another integration's IDD gets its own calibration (`extract_layout --baseline --write --calibration <its-slug>`), never another doc's. The identity binding enforces this: the coverage/tail guards alone cannot, because injecting text into an empty cell deletes nothing.
- **RENDER and look (G18) is the arbiter** - the numbers only rank candidates.

Two profiles drive the styler, which is why one set of gates covers every case:

```bash
python scripts/xlsx_brand_style.py <workbook>                      # neutral default
python scripts/xlsx_brand_style.py <workbook> --brand-profile acme # client branding
python scripts/xlsx_brand_style.py <workbook> --discover-roles     # unknown template
```

- **No branding specified -> the neutral default.** `brands/neutral.json` is the default (slate and grey, the system font pair, no wordmark); nobody has to ask for it.
- **Client wants their branding -> honour it for that project.** Copy `brands/_example-customer.json` to `brands/<client>.json` (it lists exactly what to request from the client), then pass `--brand-profile <client>`. Colours, fonts and logo change; **every structural gate stays identical** and the doc still comes out cleanly formatted. Check band-text and header-text contrast - dark-on-dark is the usual failure when a client palette drops in.
- **Unknown source template -> `--discover-roles`**, then record the fill->role mapping in `templates/<slug>.json`. Never infer hierarchy from cell shape; templates already encode it in their fills.
- **Never restyle meaning.** Yellow `FFFF00` and semantic status colours (RAG scales, test-status rules - usually conditional formatting) survive every rebrand.
- **Changed a profile or a script's default? Run `python scripts/check_profiles.py`.** It fails if any default points at a missing profile, if more or fewer than one brand is the default, or if a brand lacks a palette role the scripts read.
- **Changed a layout rule or a builder's sheet layout? Run `python scripts/xlsx_layout_rules.py`.** Its self-test fails if a builder band heading would be demoted to a note, if the "Need more rows?" footer hint drifts, or if a two-column tab stops splitting at its gutter.
- **Changed a COM script? Run `python scripts/xlsx_com.py check`, then `python scripts/selftest_checks.py --com`.** Every script drives Excel through `xlsx_com.py`: exit 3 means Excel refused edits (the step did not apply), exit 4 means another Excel is running (it is never touched).

**The neutral brand is the standing default.** No firm brand ships in this skill, and no binary masters (per-engagement masters come from the engagement store, idd-template.md path 2). When a client brand carries a logo:

```bash
python scripts/xlsx_place_wordmark.py <workbook> --brand-profile <client>
python scripts/xlsx_brand_style.py    <workbook> --brand-profile <client> --wordmark-only
```

The first places the client's wordmark at its **locked ratio** on **every** sheet including hidden ones (hidden tabs un-hide via the Integration-Type macro and would otherwise ship without it). The second re-anchors it, because placement keeps each earlier logo's position. Wrap and row-height repair, including merged ranges that Excel's AutoFit ignores, is `scripts/xlsx_repair_wrap.py`.

Use the xlsx skill for Excel file mechanics; this skill owns the content, structure, and conventions.

## Flex Credits / API consumption in design docs

As of the May 2026 platform policy update, every Extend app and non-Workday-built integration carries measurable API costs to the customer via the Flex Credits model. The commercial numbers (entitlement tiers, credit pricing, the Extend multiplier, the agent Rate Card, and what counts) live in the canonical owner - **wd-estimate `references/flex-credits.md`**; cite those, do not restate them here. **Every design doc should address API consumption:**

- **On the Technical Architecture or Overview tab:** note that the app/integration will consume API entitlements. State the estimated annual API call volume and, if the customer risks exceeding their entitlement, the resulting Flex Credit overage cost (see flex-credits.md for the rate).
- **On the Open Items tab (if volumes are unknown):** add a yellow item: "TBD - Q: estimated annual API call volume for Flex Credit impact assessment?"
- **For Extend apps:** note that the Extend SKU provides an API entitlement multiplier (see flex-credits.md).
- **For integrations:** note whether the integration is a Workday-built Core Connector (free at the API layer) or a custom build (counts toward entitlements). If a Core Connector is augmented by Studio, note that the augmented portion counts.
- **For agent-enabled apps:** note the per-agent Rate Card costs (see flex-credits.md) in addition to any API consumption.

This is not optional -- a design doc that omits API cost implications sends a build to production without the customer knowing the ongoing cost.

## Keeping the doc complete - gap analysis

Red flag: "it's a minor update, skip the gap analysis" - minor updates are exactly what introduce the interior blanks the audit exists to catch.

Run [references/gap-analysis.md](references/gap-analysis.md) before any review or sign-off: it enumerates what "done" means per tab and the cross-tab consistency checks (every requirement traced to fields/pages/tests; every BO in the object model appears in field specs; every integration touchpoint has a security answer; unit-test scenarios cover every requirement - derivation methodology belongs to wd-testing). Non-functional requirements (accessibility, error handling, performance, browser/device) have their own design-time checklist, [references/nfr-accessibility.md](references/nfr-accessibility.md), folded into the gap-analysis.

## Design change control (after sign-off)

Once a design version is signed, changes go through [references/change-control.md](references/change-control.md): baseline the signed version, log the change request (ID, requester, description, LOE impact via wd-estimate if material), get re-approval, THEN update the doc with a version bump and change-log entry. Silent edits to a signed design destroy the baseline that defect triage (wd-testing) depends on.

## Working rhythm

- After design meetings, prompt for the transcript - wd-pm meeting-intake extracts decisions/answers and routes updates back here.
- Update the doc the same day a decision lands; a design doc that trails reality by a week generates phantom defects.
- **Every initial draft ships with a "Recommended Next Steps" companion document** for the design owner: the design-session meeting plan (sessions grouped by open-item topic, with attendance, duration, cadence, pre-reads - wd-pm's agenda discipline applies), a realistic design-phase timeline with milestones/gates, the LOE recap, and this-week actions. A draft design without a path to sign-off stalls; this document is the path.
- **...and with a Design Kickoff deck** (via the pptx skill, neutral formatting unless the engagement supplies a brand): orientation + working agreement for the design team - what we're building, methodology/gates, the design-phase timeline and session plan, roles & responsibilities (who decides / prepares / attends), working conventions (yellow = open, transcripts sync the doc, scenarios grow with the design), build-arc preview, standard inclusions, this-week actions. Speaker notes on every slide. Tables and graphics over prose - it's presented, not read.
- **Every draft design ships with a process flow AND wireframes from the first version** - at minimum the standard swimlane template instantiated with the app's flows (lanes that don't apply get an explicit note, e.g. "no custom BPs in MVP") and a draft wireframe render with the editable `.bmpr` saved next to the doc. A design without visuals reads as half-thought; wd-design-visuals owns the mechanics and the clean-export rule for finals.
- **When a design ships COMPANION ARTIFACTS, make one of them the SOURCE OF TRUTH and GENERATE the
  rest.** On a template integration whose design doc, README, sample data file and three example
  transformation scripts all had to state the same field contract, hand-editing them drifted
  immediately - the workbook shipped attachments describing a 20-column layout while its own spec
  tab said 22. Fix: a single spec module (a plain Python file holding the column list and mapping
  tables) plus generators that emit every other artifact and SELF-VALIDATE (column counts, header
  equality, packed-field parsing, XML well-formedness). Then re-embed the regenerated files on the
  Examples tab. Never hand-edit a generated artifact; change the spec and re-run. This makes drift
  structurally impossible rather than a thing to remember.
  - Corollary: **embedded object attachments are COPIES.** Editing the source file afterwards does
    NOT update the workbook - re-embed, or the doc ships a stale contract.
- **Unit-test scenarios grow with the design, in the same pass.** Whenever design content changes (new requirement, new screen, changed behavior), add or update the corresponding Unit Testing scenarios before the version goes out - an empty or stale Unit Testing tab at any review is a defect (derivation methodology: wd-testing). Results land in the tab as testing executes (wd-testing owns execution).

## Lifecycle neighbors

previous = wd-discovery (its answers fill the Discovery tab); next = wd-extend-dev (build to this doc) and wd-testing (scenarios from Requirements).

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
