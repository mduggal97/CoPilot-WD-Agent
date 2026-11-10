# Coding standards - naming, comments, change logs

These standards exist because Extend code gets handed to client developers who weren't in the room. Every convention below reduces the KT burden later; skipping them creates silent debt that surfaces during handoff.

## The exemplar standard - north-star, every time (READ FIRST)

Everything this suite BUILDS - Extend/O4I code, Studio/XSLT/EIB transforms, Python/PowerShell tooling, AND what we configure IN a tenant - ships as a **reference specimen**: the artifact a colleague opens later to learn "how it's done here." Not merely working - **best-of-the-best, every time, top to bottom.** The rest of this file operationalizes the bar; this section IS the bar. It applies from the FIRST generated line - PoCs and throwaways included (throwaways become permanent).

An artifact is exemplar only when ALL of these hold. Run this self-check before calling anything done:

- **Correct AND verified** - it runs and does the right thing, PROVEN (a green build proves nothing - pmd-gotchas.md, wd-testing evidence discipline). Clean code that isn't verified is not exemplar.
- **Efficient by design** - the efficiency non-negotiables below and in efficiency.md, chosen at design time, not bolted on as cleanup.
- **Readable + idiomatic** - descriptive names, matches the house idioms; a developer who wasn't in the room follows it without you.
- **Commented at KT level** - intent, not restatement of syntax; the header + change-log block; the per-function usage header; stage markers in long functions (all defined below).
- **Documented** - the WHY and the HOW-TO-USE/RUN live somewhere durable: a companion README/runbook, the design-doc entry, or (for tenant config) the evidence trail + naming record. An artifact nobody else can pick up is not exemplar, however clean the code.
- **Reusable as a pattern** - no shortcut that only works here; someone can lift the shape to the next app or client.

**Honesty rule:** if scope or time forces a shortcut below this bar, SAY SO - a `// TODO` / `"_comment"` plus a note to the user or a RAID/open item. A flagged gap is acceptable; a silent compromise dressed as finished is not.

**Promote the standouts:** when an artifact is genuinely best-of-breed, nominate it as a cited reference exemplar (wd-practice-ops reuse-and-asset-catalog for cross-engagement IP; app-catalog-registry.md for Extend shapes) so the team has a real north-star to point at, not just a rule.

This is enforced every-time via the "Exemplar artifact" row in wd-extend-lifecycle references/quality-gates.md - report the self-check result with the deliverable.

## Naming conventions

| Thing | Convention | Example |
|---|---|---|
| PMD page ids/files | lowerCamelCase, verb-prefixed by intent | `addLine.pmd`, `approveCostCenter.pmd`, `manageAssignments.pmd` |
| Page intent prefixes | add / edit / approve / revise / review / details / request / inactivate / ...Micro for micro-pages | `checkOutConfirm.pmd` |
| Business objects / BPs | PascalCase nouns | `ExpiryAssignment.businessobject`, `CreateCostCenterRequest.businessprocess` |
| Security domains | PascalCase, role-aligned, suffix Pages/Data | `ManageInventoryExpiryPages`, `InventoryExpiryData` |
| Orchestrations | Descriptive with underscores or PascalCase; name says trigger + action | `Position_Costing_Allocation_Event_Sequence_Generator`, `PutCostCenterOnApproval` |
| Script files | lowerCamelCase by domain | `reportCalc.script`, `requestScript.script` |
| Do-not-use / parked pages | `DNU` prefix | `DNUadminConfig.pmd` |
| App reference IDs | lowerCamelCase app name + org suffix (assigned by wdcli) | `<appName>_<org-suffix>` (e.g., a delivered app on the current program) |
| Variables | Descriptive, no single letters (`transactionTotal`, not `tq`) | - |

For traditional integration naming (INT numbers, ISUs, security groups, calculated fields, EIB/Studio names), see integration-naming.md in the wd-integration-dev skill.

## Comments - knowledge-transfer level, layman's terms

Plain-language / novice-reader writing standard is owned by **wd-extend-lifecycle** (SKILL.md "Writing standard"). Its application here: comments are for the next developer, so state the INTENT of the block - what business outcome it serves - not a restatement of the syntax.

- **PMD JSON:** use `"_comment"` keys on endpoints, sections, and outbound blocks. Cite design decisions and open items by ID so code is traceable to the design doc: `"_comment": "Assign Room no longer commits. On OK it stashes the entered values in flow scope; assignConfirm reviews them and runs the POST when the user confirms. Per 7/15 design, OI-06."` On a secondary/dependent endpoint, say WHY the call exists and when it's skipped, not just what it fetches: `"_comment": "Parent assignment (absent for ad-hoc). Used only to reach the par location -> its source inventory site for the average-cost lookup."`
- **Script files / script blocks:** `//` comments; open each script FILE with a NOTE block explaining which pages use it and what it does overall; comment each function's purpose and edge cases. Inside a long function, put a one-line `//` marker above each stage stating the intent of the next few lines (e.g. `// Extract WorkdayIDs of canceled transactions`, `// Filter lines within the reporting window`, `// Total quantity and cost per par location`) - the markers read as a plain-English outline of the algorithm. State intent, not restatement: `// prefer the average cost at the source site; keep unit price if none returned` beats `// set unitCostField`.
- **Orchestrations:** name nodes descriptively (the node name is the comment surface) and keep a Log node narrating each phase; builder scripts (Python) carry full docstring headers.
- **PowerShell/Python tooling:** header block with purpose, prerequisites, usage, caveats.
- When you change code, change its comments in the same edit - stale comments actively mislead the next developer.

## Header + change-log block (the standard going forward)

Every `.script` file, substantial page script block, and generated orchestration gets a header. Existing files gain one on their next touch - don't mass-retrofit.

```
// ============================================================
// reportCalc.script - expiry reporting calculations
// Used by: expiryReporting.pmd (onLoad + Run Report button)
// Purpose: single source of truth for report figures; filters
//          lines/transactions by date range and returns a map
//          the page renders. Plain-English: this file does the
//          math for the reporting page.
// Change log:
//   2026-07-16  Exclude canceled-transaction lines (bug fix)
//   2026-06-18  Initial version (date-range rerun pattern)
// ============================================================
```

For PMD pages (JSON can't hold a comment block at top level), put the equivalent in a `"_comment"` on the page's root `presentation` object: one line of purpose + dated change entries appended at each edit.

The change log answers "why is it like this?" without a git archaeology session - client developers usually don't get the git history.

**Per-function usage headers (adopted from a delivered production app, 2026-08-25):** in shared script modules, each exported function opens with a JSDoc-style block giving purpose, the `"include"` wiring a consuming page needs, the call signature, parameters, and return value - so a page developer can use the module without opening its internals. Example shape:

```
// gridColumnValidator - checks if all rows in a grid have at least one of the
// specified columns populated.
// Include on the page: "include": ["gridColumnValidator.script"]
// Call: gridColumnValidator.validate(gridWidget, ['costCenter','fund'])
// Params: gridWidget - the grid widget instance; columns - list of column ids.
// Returns: true when every row has a value in at least one listed column.
```

## Leave it better than you found it

When touching an existing file for any reason, bring what you touch up to these standards: rename throwaway variables you're editing anyway, add the missing header/change-log block, fix comments that drifted from the code. Scope it to what you touch - don't mass-reformat a file for a one-line fix (that buries the real change in the diff) - but never add new code below the current bar. The same principle governs documents (wd-design-doc owns that side).

## Code quality expectations

Efficiency and reuse are part of the standard, not a nice-to-have. The full pattern catalog with real snippets lives in [efficiency.md](efficiency.md); the non-negotiables:

- **Compute once, reuse many.** When two or more widgets derive from the same data, compute it once in `onLoad` into `pageVariables` and have widgets read the result - don't put a heavy `.filter()`/loop in each binding, which re-runs per widget and per re-render.
- **Externalize reused/complex WQL** into `presentation/wqlQueries/*.wqlquery` and reference by `queryId` instead of copy-pasting `string:pathEncode` SELECT strings across pages. One definition, no manual escaping.
- **You OWN every line you copy.** Scaffolding a new page/flow/script from a sibling vertical or template is encouraged - copying it VERBATIM is not. Before you ship copied code, know what each block does and ADAPT it to the new object: verify field names against the source (they fail at runtime, not build - wql.md), keep WQL in the component form and on a WQL endpoint type (pmd-gotchas #78), rename script vars and widget bindings, and replace every placeholder (no `Lorem Ipsum` in a non-DNU page). A build pass proves none of this. When you hand adapted work back, state what you changed and why. (MDR Program review, 2026-09-04 - the build-side twin of the design rule "read the full design, don't infer a vertical from its sibling.")
- **Set-based `list:` helpers over nested loops.** `list:filterMultiple` / `list:excludeMultiple` for in-set/not-in-set joins, `list:sort(..., false)[0]` for newest-by-field, `list:flatten(...).distinct()` for de-duping nested collections - instead of `for` loops with an inner `.find()`.
- **Avoid dead round-trips.** Don't re-fetch what an endpoint already loaded; gate dependent lookups with an endpoint `"exclude"` expression so they only fire when their input exists; respect the BO REST 100-row cap (pmd-gotchas.md #15) with WQL rather than N+1 endpoint calls.
- **Logic in script FILES**, reusable/diffable/commentable, exported as a helper map and called by name - rather than duplicated inline expressions across widgets. Early-return guards (`empty x ? '' : x[0].field`) over deep nesting.
- Follow the null-guard discipline from pmd-gotchas.md - every nullable read guarded, every payload branch explicit.
- Match the app's existing idioms when editing: same confirm patterns, same date formatting, same grid conventions. Consistency IS the UX.
- **Debug logging convention:** gate `console.info()` diagnostics behind a Boolean app-attribute flag - standard attribute name **`debugLogging`** (`attrstore.debugLogging ? console.info(...) : null`) - so tenants can switch verbose logging on/off without a redeploy. Verified as the working pattern in delivered production apps (2026-08-05; adopted as the QA-gate standard 2026-08-25): NO stray ungated logs ship, and leave the gated calls in shipped code rather than stripping them.
- **Portability (clone-survival) rules, verified on a delivered app port (2026-08-25):** never hardcode `api.workday.com` URLs in pages (use dataProviders/`baseUrlType` bindings), and never hardcode app-prefixed enum/reference IDs (`<appRefId>_<BO>_ID=...` string literals) - namespace them `{{site.applicationId}}_...` so the app survives `app copy` / a refId change. Same family as the `.graphquery` hardcoded-refId gotcha in model.md. Grep for the old refId before any port.

## Platform citizenship (non-negotiables)

Workday is shared tenant infrastructure - every API call an Extend app makes rides the same gateway as the client's payroll runs and everyone else's tenants. Design as if every call is metered, because Workday's production-approval review (wd-deployment) effectively treats it that way.

- **Retry discipline:** retry with backoff on 5xx/timeouts ONLY - never retry a 4xx (the request is wrong; retrying it is load without hope). `_DEFAULT_WORKDAY_RETRY_CONFIG` is the default posture for orchestration Workday calls. Remember [orchestration.md](orchestration.md)'s caveat: `SendWorkdayApiRequest` does not hard-fail on 4xx - check the response status explicitly, don't paper over silent rejections with retries.
- **No polling loops.** Prefer BP/event-triggered orchestrations (`IntegrationFrameworkTrigger`, Model BP steps) over anything that wakes up to ask "anything new?". A schedule that exists only to poll is a design finding.
- **Bound every read.** No unbounded WQL - always constrain by date range, status, or key set; respect the BO REST 100-row cap with pagination or WQL rather than N+1 calls (see [efficiency.md](efficiency.md)).
- **Bulk the writes.** Row-at-a-time writes where `?bulk=true` exists (POST/PATCH/DELETE, ~100/batch - [model.md](model.md), [orchestration.md](orchestration.md)) are a review finding, not a style preference.
- **No page-load endpoint fan-out.** Gate dependent endpoints with `exclude` expressions so they fire only when their input exists - a page that fires six endpoints on load to maybe use two is spending shared capacity on speculation.

Rate limits (per Workday Admin Guide (Integrations), Jul 2026 - doc-confirmed, not practitioner-verified): Workday limits API calls **per second, per tenant**; exceeding the threshold returns **HTTP 429**, and calls succeed again once the rate drops. The threshold itself is **contract-based** (visible on the Entitlements dashboard), so the exact number is intentionally unpublished - do not invent one. Retry-on-429 with exponential back-off is officially recommended. Companion fact: during the Weekly Service Update, new inbound API calls fail and in-flight calls fail at window start (typically 503/500, code not guaranteed) - design for caching + rerun-after-WSU + back-off retry. Still document observed behavior (throttling responses, latency under load) per app and per tenant, and let the Volumes Questionnaire / Performance Testing evidence (wd-deployment) carry the load story.

## Mock mode for external integrations (house standard)

Any app that calls an external system ships a **mock-vs-live toggle**: a packaged App Attribute (e.g. `<System>MockMode`, default mock/yes) that the calling flow or page branches on - mock returns a canned representative payload, live hits the real endpoint. Verified in a delivered production app (external EHR integration, 2026-08). Benefits: demoable without partner connectivity, unit-testable in dev tenants, and the switch is tenant config (no redeploy). Pair with endpoint mocking on the page side: `presentation/testing/*.mock_config` + `*.mock_response` (sample-verified in official catalog apps - see the mocking exemplars in app-catalog-registry.md).

## Anti-patterns (review findings, verified in delivered code 2026-08-25)

- **Dated backup copies committed next to live files** (`HomePageCopy0628.pmd`, `*Bckup06192026.script`). The repo is the version control; a backup page still deploys, still shows in App Manager, and confuses the next developer. Use git history; a deliberately parked page gets the `DNU` prefix (naming table above) and a `_comment` saying why.
- **Duplicated app trees** (two working copies of the same app in sibling folders). One canonical source dir per app; scratch copies live outside the app folder (wdcli upload also rejects extra files in the app dir).
- **All logic inline in PMD with zero `pageVariables` / script modules** - see Code quality expectations; an app-wide sweep finding, not a per-page nit.

## Mark how sure you are, and how you know (reporting standard)

When reporting results, tag each material claim so a completed step and a skipped step never
read the same (adapted from an internal firm response-style skill, 2026-08-28):

- **verified** - ran it, read the log, saw the value. Say what you ran.
- **read** - found it in a file / listing / snapshot. Say where.
- **assumed / recalled** - from memory or inference, not checked this session. Flag it and say
  what would confirm it.

State plainly what you did NOT do: not run, not deployed, not tested, only one env checked. This
is the reporting face of the exemplar bar's honesty rule (flag shortcuts, never silent).

## Config-driven UI text (house standard for Marketplace-grade apps)

Any app going to more than one tenant (Marketplace/BoW, or multi-entity clients) must NOT hard-code page titles, help text, or instructions. The verified delivered pattern (2026-08-05): load them from a configuration BO (or per-page App Attributes) once in `onLoad` into a `pageVariables` map, and have every label/title read `pageVariables.config.get('key') ?: 'sensible default'`. The `?:` fallback means a missing config row degrades to shipped copy instead of a blank widget. Tenants then change wording via data/attributes - no code change, no redeploy, no per-tenant fork. For single-tenant custom apps this is optional; for anything productized it's the standard.
