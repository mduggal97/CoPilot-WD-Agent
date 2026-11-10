---
name: wd-smartsheet
description: >-
  Read and update Smartsheet sheets, rows, and project trackers via the Smartsheet REST API
  (using a personal API access token; MCP not available on some managed/corporate machines). Use when the user
  mentions Smartsheet, says "update the tracker", references the RAID log, project plan rows, a
  sheet ID, needs to find a workspace/sheet, needs help getting a Smartsheet API token, or asks
  to "mark task complete in smartsheet" - any task that reads from or writes to a Smartsheet
  sheet, report, or workspace.
---

# wd-smartsheet - Smartsheet transport & API mechanics

This skill owns Smartsheet transport/API mechanics only; project-management content and routines (agendas, status, RAID practice) belong to wd-pm.

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **Getting the skill onto a machine** (unzip, where it goes, success check) | [references/install.md](references/install.md) |
| **Generating + securely storing a Smartsheet API token** (novice, click-by-click) | [references/token-setup.md](references/token-setup.md) |
| **Read/write endpoints, pagination, cell anatomy, column-type rules, error codes, automation-mirrored comment columns** | [references/api-details.md](references/api-details.md) |
| **Regenerating the `smartsheet_api.py` helper** (build-spec) | [references/scripts.md](references/scripts.md) |
| **Per-engagement sheet-id registry** (template to fill) | [references/smartsheet-registry-template.md](references/smartsheet-registry-template.md) |
| **Two-way sync anti-clobber contract** (co-edited registers) | [references/sync-contract.md](references/sync-contract.md) |

## 0. First-time setup (Claude DRIVES this - do as much FOR the user as possible)

**Getting the skill onto a machine** (unzip, where it goes, success check, and the "runs locally in
Claude Code, not claude.ai" caveat) is the plain-language [references/install.md](references/install.md)
- point a non-technical user there first.

Once the skill is loaded, run the one-time setup and **do everything you safely can for the user rather
than handing them commands.** This skill drives a small Python helper (`scripts/smartsheet_api.py`).
Assume the user is non-technical.

**Claude's job - do these FOR the user:**
- **Fill in real paths.** Compute the skill's actual folder and substitute the full path into every
  command you show. NEVER show `<path-to-skill>` or `...` to the user - write the real path.
- **Check Python yourself** (`python --version`). If missing, give the user the ONE action (their
  software portal, e.g. Company Portal) - see token-setup Step 0; don't make them diagnose.
- **Install deps yourself** when you can (`pip install requests keyring`). If a corporate proxy blocks
  pip, supply the exact `--proxy`/`--trusted-host` fix or hand the one command to the user.
- **Regenerate the helper silently** from [references/scripts.md](references/scripts.md) if
  `scripts/smartsheet_api.py` is missing - don't make the user copy code.
- **Run the connection test yourself** (`test`) and just report "Connected as <email>"; run
  `workspaces`/`find` for them. They should never type a discovery command.

**The user's job - the ONLY irreducible manual steps.** Hand these over one at a time, with exact
click-by-click hand-holding, fenced as a **"Your steps (outside this session)"** block:
1. **Open a terminal (PowerShell)** - token-setup Step 0 shows exactly how.
2. **Generate their Smartsheet token** in the browser - token-setup Step 1 (exact clicks).
3. **Run ONE command you give them** (with the real path already filled in):
   `python <realpath>\scripts\smartsheet_api.py set-token`, and paste the token at the hidden prompt.
   This one MUST be the user - the token must never pass through chat.

Skip setup if Python + a stored token are already in place (just run `test` to check).

## 1. Auth & access - REST via a personal API token

**REST is the working path.** On some managed/locked-down machines the Smartsheet MCP server can't be connected (IT policy), and even where allowed the `smartsheet-mcp` server has been observed configured-but-not-surfacing-tools. So do not wait on MCP: use the REST helper (`scripts/smartsheet_api.py`). (If a future environment DOES surface `mcp__smartsheet*` tools, they're fine to use, but never block on them.)

**The token.** Each user supplies their own personal API access token. The helper finds it in this order:
- `SMARTSHEET_API_TOKEN` environment variable
- Windows Credential Manager, under a keyring **service name** (setting: `SMARTSHEET_KEYRING_SERVICE`), entry `default/smartsheet_token`
- `.env` in the current directory

**Keyring service name (overridable).** The service name under which the token is stored in Credential Manager is a setting - override it via the `SMARTSHEET_KEYRING_SERVICE` environment variable, with a generic default (the helper ships with `smartsheet_api_token`, entry `default/smartsheet_token`). If nothing is set, use the generic default the helper ships with. (A firm may have a historical or standard service name it stores tokens under; that value lives in environment memory, not in this skill.) `set-token`/`clear-token`/`test` all read whatever service name is in effect, so a token stored under one name is found again as long as the same name is in effect.

Token goes in the `Authorization: Bearer {token}` header. **Never hardcode, echo, or ask the user to paste the token into chat** - they store it locally themselves.

**One-time secure store (the setup to recommend):** have the user run `python scripts/smartsheet_api.py set-token` **in their own terminal**. It reads the token at a HIDDEN prompt (never on the command line, in shell history, in a file, or in chat), stores it encrypted in Windows Credential Manager where the helper already reads it, and verifies it (prints their email, never the token). After that it's picked up automatically in every future session - the token is never entered again. (`clear-token` removes it.) Full walkthrough in [references/token-setup.md](references/token-setup.md).

**If no token is found (or `/users/me` returns 401), walk the user through [references/token-setup.md](references/token-setup.md)** - the novice, step-by-step guide to generating a Smartsheet token (Account icon -> Personal Settings -> API Access -> Generate) and storing it where the helper looks. Don't just error out; a missing token is the #1 first-run blocker.

**Corporate SSL note:** a corporate network with SSL inspection (MITM certs) makes Python `requests` fail cert verification against api.smartsheet.com. The helper sets `verify=False` + suppresses `InsecureRequestWarning` - expected here, not a hole (still TLS to the corporate proxy).

Connection test: `python scripts/smartsheet_api.py test` (`GET /users/me`) - prints the token owner's email if valid.

## 2. The helper script (preferred for REST work)

`scripts/smartsheet_api.py` wraps everything below with column-title-keyed dicts:

```python
from smartsheet_api import get_sheet, find_rows, add_rows, update_rows, resolve_contacts

columns, rows = get_sheet(RAID_SHEET_ID)              # rows = list of dicts keyed by column title, + "_row_id"
open_items = find_rows(sheet_id, lambda r: r.get("Status") == "In-Progress")
add_rows(sheet_id, [{"Title": "New risk", "Type": "Risk", "Status": "Not Started"}])
update_rows(sheet_id, [{"row_id": 123456, "updates": {"Status": "Completed"}}])

# Contact columns: pass contact dicts / a list of them - the helper builds objectValue.
# Look emails up from a roster first (never guess an address):
watchers = resolve_contacts(["<Full Name>", "<Full Name>"], CONTACT_LIST_SHEET_ID)   # -> [{"name","email"}, ...]
add_rows(sheet_id, [{"Change Request Title": "...", "Watcher(s)": watchers}])  # ID/system cols auto-skipped
```

Standalone commands (all read-only, for pointing at the right target):
```
python smartsheet_api.py test                 # /users/me - confirms token + whose account
python smartsheet_api.py workspaces            # every workspace the token can see (id + name)
python smartsheet_api.py sheets <workspace_id> # sheets directly in that workspace
python smartsheet_api.py find <name>           # search ALL sheets by name (finds folder-nested too)
python smartsheet_api.py sheet <sheet_id>      # a sheet's columns + row count
python smartsheet_api.py describe <sheet_id>   # EVERY column: type, SYSTEM/FORMULA/VALIDATED/LOCKED, options, fill% - run before any write
python smartsheet_api.py check-token           # diagnose a stored token WITHOUT exposing it (source, masked preview, live test)
```
Discovery helpers in code: `list_workspaces()`, `list_sheets_in_workspace(id)`, `find_sheets_by_name(substr)` - this is how a user "directs" us to a workspace/sheet by NAME; not limited to any pre-known registry (see section 6). Verified live 2026-08-03: the REST path enumerated 28 workspaces and read a sheet cleanly; the `smartsheet-mcp` server is configured but was NOT surfacing tools that session, so REST is the reliable path.

## 3. Read patterns

Base URL `https://api.smartsheet.com/2.0`. Paginate `GET /sheets/{id}?pageSize=500&page=N` until you've collected `totalRowCount`; build a `columnId -> title` map from `columns` and key each row by column TITLE, preferring `displayValue`; always retain the row ID as `_row_id` for later writes; strip HTML from rich-text cells. Reports (`GET /reports/{id}`) are read-only, same shape; `GET /users/me` = connection test. Full read endpoints, pagination contract, and cell anatomy: [references/api-details.md](references/api-details.md).

## 4. Write patterns

### Before you write - review EVERY column (schemas vary, people change them)

The single biggest lesson: **Smartsheet schemas differ project-to-project and people edit them, so never assume a fixed set of fields - inspect the live sheet every time.** Before adding/updating a row:

1. **Describe the sheet:** `python scripts/smartsheet_api.py describe <sheet_id>` (or `column_report(sheet_id)`) - lists every column with its type, `SYSTEM`/`FORMULA`/`VALIDATED` flags, picklist `options`, and **`fill_rate`** (how often it's already populated across existing rows).
2. **Decide populate-vs-skip for EACH column - not just the obvious ones:**
   - **High fill-rate + you were about to leave it blank = a likely MISS** - a field the team consistently fills and expects. Populate it; if you don't have the value, flag it and ask (default-and-flag). *(This is exactly how we'd have caught `Workday Domain Area(s) Impacted` - 96% filled - which we first dropped.)*
   - **`SYSTEM` / `FORMULA`** columns -> skip (the helper does this automatically).
   - **`VALIDATED` / picklist** columns -> use an exact option from the list (free text 400s); read `options` first.
   - **Low fill-rate optional** columns -> fill if you have a value, otherwise leave blank.
3. **Echo the intended row** - populated + intentionally-blank + flagged-unknown - to the user before writing (the safety rule below).

### Look across the workspace for related values

Rows routinely reference data that lives in **other sheets** - a `RAID ID`, an owner, a related record, a linked design/tracker item, contact emails. Before writing, check sibling sheets in the same workspace (`sheets <workspace_id>`, `find <name>`, the registry) and pull those in rather than inventing or leaving them blank. Examples: `resolve_contacts(...)` reads emails from the roster; a `RAID ID` comes from the RAID log; a design status from the design tracker.

### Writing mechanics

Writes take `columnId` (never a title); batch multiple row objects per call (~500/request, never one-row-per-call). Body shapes (add `POST /sheets/{id}/rows` / update `PUT /sheets/{id}/rows` - list only the cells you change), placement (`toBottom`/`toTop`/`parentId`/`siblingId`), EVERY column-type rule, and the full error-code table are in [references/api-details.md](references/api-details.md). The `smartsheet_api.py` helper handles the quirks that bite by VALUE SHAPE (pass the right Python value and it builds the payload) - the four to know:

- **System / column-formula columns** (auto-number `ID`, Created/Modified) are read-only - the helper auto-skips them; let the auto-number assign the ID.
- **Contact columns often need `objectValue` even when `describe` reports `TEXT_NUMBER`** (Watcher(s), Owner, Assigned To, Approver, ...). Pass a contact dict / list / `"Name <email>"` / bare email; needs a real EMAIL, so **never guess** - use `resolve_contacts(names, contact_sheet_id)`. The helper auto-coerces these titles (`_looks_like_contact_column`) and `describe` flags them `LIKELY_CONTACT`; on a NEW title pattern, still resolve up front.
- **Locked columns reject the ENTIRE batch** (`errorCode 1051` names only a column id, killing valid updates with it). `describe` flags them `LOCKED`; the helper skips with a warning. Comment-style locked column -> post a row Conversation instead.
- **Multi-select / validated dropdowns need a LIST of exact `options`, not a comma string** (the helper wraps for `validation:true`+`options` columns); a genuinely-declared `PICKLIST` is single-select and must NOT be wrapped (`errorCode 5536`). One sheet can carry both shapes - read `options` from `describe` first.

### Adding a COMMENT: post a Conversation, never write the comment column

A "Latest Comment" / "Notes" / "Status Update" column is very often an **automation-mirrored**
column (fed by the newest row Conversation), not a field you fill in - writing it directly gets
silently overwritten, doubles the author prefix, and never notifies watchers. **Detect** it (entry
ends in `...`, carries an untyped `Author Name - ` prefix, or matches the newest discussion) and
treat it read-only. **To comment:** `POST /sheets/{id}/rows/{rowId}/discussions` with text lacking
an author prefix - the column updates itself and watchers are notified. Full detection + read-back +
delete-route + notification-cost detail: [references/api-details.md](references/api-details.md)
("Comment columns fed by automation").

### Safety rule - trackers are shared team artifacts

Before ANY update: read the target rows first and echo a **before -> after diff** to the user for confirmation - UNLESS the user already approved the exact change (e.g. "set RAID-042 Status to Completed" is exact; "clean up the RAID log" is not). Never blind-write. For adds, echo the row(s) you're about to create. After a write, report the API's returned row count and any partial failures.

**Sensitive-data egress check (every write).** A tracker is widely shared, so before writing confirm no PHI/PII/FERPA person detail or secrets land in cells that do not need them - use the least-identifying form (a worker ID or role, not name+SSN+DOB) and only where the sheet's access is already scoped to those entitled; reference sensitive data where it already lives rather than copying it into a row. Owner rule: wd-extend-lifecycle `references/ai-data-governance.md` section 6.

## 4b. Two-way sync - column ownership (anti-clobber)

When a sheet is co-edited by a human (Smartsheet UI) AND this tool (API) - a live
defect/RAID/tracker register - declare each column HUMAN-OWNED or TOOL-OWNED, PULL only human
columns, PUSH only tool columns, skip blank source cells, upsert by a stable key, and never
PUSH-write an automation-mirrored comment column. Full anti-clobber contract:
[references/sync-contract.md](references/sync-contract.md). Used when wd-pm (raid-log) and
wd-testing (defect intake) drive a shared register.

## 5. Error handling

Full status / errorCode table and fixes: [references/api-details.md](references/api-details.md) ("Common error codes"). Quick reflexes: **401** -> re-check token/keyring (regenerate in Smartsheet -> Personal Settings -> API Access); **403** -> sheet not shared to the token owner; **404** -> wrong sheet/row ID (check the registry + engagement memory); **400 / 1042** -> read `options`, match exactly or `strict:false`; **429** -> back off and batch.

## 6. Finding the right workspace & sheet

**Start by orienting to the workspace.** Extend work almost always lives in one of two kinds of workspace - confirm which one the user means, then discover sheets inside it (`sheets <workspace_id>` or `find <name>`):
- **Client engagement workspace** - the delivery team's per-client space (each client typically has one, often under a program name). Client trackers, RAID, plans live here.
- **Products / Marketplace workspace** - where the products / BoW / Marketplace team works. Use this for Marketplace product builds rather than a client space.

### Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Engagement workspace id** - the client-delivery workspace (and any separate testing/sandbox workspace) for this program. Pull from project memory or discover via `GET /workspaces` (`workspaces` command); confirm the name matches the client you mean.
- **Sheet-id registry** - the map of `<name> -> sheet-id` (and per-sheet key columns) for this engagement's trackers. Pull from project memory or discover via `sheets <workspace_id>` / `find <name>`; never hardcode a prior engagement's IDs. Template shape: `references/smartsheet-registry-template.md`.
- **Products / Marketplace workspace id** - if the work is a BoW/Marketplace product build rather than client delivery. Pull from project memory or discover live.

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).

The sheet ID is NOT in the browser URL, so resolve by name via the API (`find <name>` searches all workspaces incl. folder-nested; `sheets <workspace_id>` lists a workspace's sheets), or ask for the sheet URL/ID.

## Lifecycle neighbors

Serves **wd-pm** (status routines, RAID practice, agendas - it decides *what* to write, this skill does the writing), **wd-pm meeting-intake** (pushing meeting-derived actions/decisions into trackers), and any skill in the wd-* suite that needs tracker I/O.

**Quality-gate rule (suite-wide):** every artifact this skill produces has a named check in wd-extend-lifecycle `references/quality-gates.md` - run it before presenting work as final and report the result with the deliverable.
