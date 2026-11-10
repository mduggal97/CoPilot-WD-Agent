# Smartsheet REST API - detail reference

Base URL: `https://api.smartsheet.com/2.0`. All calls: `Authorization: Bearer {token}`,
`Content-Type: application/json`. On a corporate network with SSL inspection use `verify=False` (SSL
inspection re-signs TLS with certificates Python doesn't trust).

## Read endpoints

| Purpose | Call |
|---|---|
| Connection test / whoami | `GET /users/me` |
| List workspaces | `GET /workspaces` |
| Workspace contents (folders, sheets -> IDs) | `GET /workspaces/{id}` |
| List all sheets visible to token | `GET /sheets?includeAll=true` |
| Sheet (columns + rows, paginated) | `GET /sheets/{id}?pageSize=500&page=N` |
| Columns only (cheap) | `GET /sheets/{id}?pageSize=1&include=columns` |
| Single row | `GET /sheets/{sheetId}/rows/{rowId}` |
| Report rows (read-only) | `GET /reports/{id}?pageSize=500` |
| Sheet-level search | `GET /search/sheets/{id}?query=...` |
| Row attachments / discussions | `include=attachments,discussions` on the sheet GET |

### Pagination contract

The sheet GET returns `totalRowCount`. Keep requesting `page=2,3,...` (same `pageSize`)
and appending `rows` until collected count >= `totalRowCount` or a page returns no rows.

### Cell anatomy (read)

```json
{"columnId": 1234567890123456, "value": "2026-08-01", "displayValue": "08/01/26",
 "formula": "=SUM(...)", "hyperlink": {...}, "objectValue": {...}}
```

- `displayValue` = what the UI shows (formatted). Prefer it for presentation/matching.
- `value` = typed raw value (bool for checkboxes, number for numbers, ISO string for dates).
  Use `value` when you need the real type (e.g. checkbox true/false).
- `formula` present => this cell is formula-driven => **do not write to it**.
- Rich-text cells return HTML in the string - strip tags.
- Contact cells: `value` is the email; `displayValue` is the display name;
  multi-contact lives in `objectValue`.

### Reading rows into dicts

Build a `columnId -> title` map from the sheet's `columns` array, then key each row's cells
by column TITLE (prefer `displayValue`). Always retain the row ID as `_row_id` - you need it
to update the row later.

## Write endpoints

Writes take a `columnId`, never a column title - resolve titles from a prior read or the
columns-only GET (`GET /sheets/{id}?pageSize=1&include=columns`).

| Purpose | Call |
|---|---|
| Add rows | `POST /sheets/{id}/rows` |
| Update rows | `PUT /sheets/{id}/rows` |
| Delete rows | `DELETE /sheets/{id}/rows?ids=1,2,3` (ask user before ever using) |
| Add column | `POST /sheets/{id}/columns` |
| Add comment to a row | `POST /sheets/{sheetId}/rows/{rowId}/discussions` |
| Attach file/URL to row | `POST /sheets/{sheetId}/rows/{rowId}/attachments` |

### Add rows - body shape

```json
[
  {"toBottom": true,
   "cells": [
     {"columnId": 111, "value": "RAID-0512"},
     {"columnId": 222, "value": "High"},
     {"columnId": 333, "value": true}
   ]},
  {"parentId": 4567890123456789,
   "cells": [{"columnId": 111, "value": "Child task"}]}
]
```

Placement attributes (one per row object): `toBottom` (default choice), `toTop`,
`parentId` (nest under a row - hierarchy sheets), `siblingId` (insert after a row),
optionally combined with `above: true`. Mixing location types in one request can 400 -
keep placement consistent per batch.

### Update rows - body shape

```json
[
  {"id": 7654321098765432,
   "cells": [{"columnId": 222, "value": "Completed"}]}
]
```

- `id` = the row ID (`_row_id` from a read). Only listed cells change.
- To clear a cell, send `"value": ""`.
- Response envelope: `{"message": "SUCCESS", "resultCode": 0, "result": [rows...]}` -
  check `message`/`resultCode`, and report the count of `result` rows back to the user.

### Batching & rate limits

- ~500 rows max per add/update request - chunk larger sets.
- ~300 requests/minute per token; HTTP 429 means back off (respect any `Retry-After`).
- One batched call of 200 rows beats 200 single-row calls in every way.

### Column-type rules for writes

| Column type | Rule |
|---|---|
| PICKLIST | `value` must exactly match an option or the request 400s (errorCode 1042-ish). Read the column's `options` array first; or set `"strict": false` on the cell to force free text (changes tracker hygiene - prefer exact match). |
| CHECKBOX | `value` must be boolean `true`/`false`, not "Yes". |
| DATE | ISO format `"YYYY-MM-DD"`. |
| CONTACT_LIST / contact | Email as `value`; `objectValue` (`MULTI_CONTACT`) for multiple. Needs a valid EMAIL - name-only is rejected for multi-contact; **never guess an address** (look emails up from a roster sheet via a `resolve_contacts(names, contact_sheet_id)` helper). (!) Some contact columns report `type` as `TEXT_NUMBER` yet still require `objectValue` (seen on Watcher(s) / Workstream Owner) - detect by INTENT, not declared type. A helper that dispatches by VALUE SHAPE (a contact dict `{name,email}`, a LIST of them -> multi-contact, a `"Name <email>"` string, or a bare email) builds the right objectValue regardless of the column's declared type. |
| MULTI_PICKLIST (and validated multi-select that REPORTS as TEXT_NUMBER but stores `"A, B, C"`) | Pass a LIST of exact options (the helper builds the `objectValue`); a comma STRING 400s with `CELL_VALUE_FAILS_VALIDATION`. Read `options` from `describe` first. |
| Validated / restricted dropdown (incl. TEXT columns with `validation:true` + `options`) | Rejects any value not in the option list; use an exact option or leave the cell blank. |
| TEXT_NUMBER | String or number (unless validated / contact per the rows above). |
| Formula-bearing cells | Cannot be set via `value` - remove those columns from your payload. Column-level formulas make the whole column read-only. |
| System columns (Created Date, Modified By, auto-number) | Read-only - never include in writes. |

### Project-plan `% Complete` (dependency-enabled sheets)

On a project plan with dependencies enabled (has Predecessors / Duration / Baseline columns), `% Complete` behaves differently from an ordinary number column - two rules, both learned the hard way:

1. **Write LEAF (child) rows ONLY; never write a parent row's `% Complete`.** On these sheets the parent value is an auto-calculated, duration-weighted rollup of its children. Writing to a parent cell is ignored and forces a recalc that can surface previously-stale rollups (looks like the parent "dropped"). Check `parentId` membership first to confirm a row is a leaf before writing - and note that sub-parents (rows that themselves have children) are also rollups, so bump THEIR children, not them.
2. **Write the value as a DECIMAL number (`0.85`), NEVER a percent string (`"85%"`).** A string displays but is non-numeric, so parent rollups can't aggregate it and the parents go to 0% or blank. Sending `0.85` stores it numerically and the parents roll up correctly.

To reflect progress: bump the leaf-task decimals and let the parents roll up on their own. (This applies to true project PLANS; a plain task/status tracker without dependencies is an ordinary number column.)

### Common error codes

| HTTP | errorCode | Meaning / fix |
|---|---|---|
| 401 | 1002/1003/1004 | Invalid or expired token - regenerate in Smartsheet Personal Settings -> API Access |
| 403 | 1004 | Token OK, sheet not shared to that user |
| 404 | 1006 | Bad sheet/row ID |
| 400 | 1042 | Cell value doesn't validate (picklist/strict) |
| 400 | 1036 | Attempt to write to a formula cell |
| 400 | 1051 | `CANT_EDIT_LOCKED_COLUMN` - the column is locked. `describe`/`get_sheet` expose `locked` and `lockedForUser` on the column; `lockedForUser: true` means THIS token's user can't write it even if they can read it. Only a sheet Admin/Owner can unlock (right-click the column header -> Unlock Column). **A whole multi-row PUT is rejected on one locked cell**, so a single comment field can silently kill an otherwise-valid batch - check for locked columns BEFORE building the payload, and split the write so a locked field can't take the rest down with it. Alternative needing no unlock: post the text as a row discussion (`POST /sheets/{id}/rows/{rowId}/discussions`), which lands in the row's Comments panel instead of the column. |
| 400 | 5536 | `CELL_VALUE_FAILS_VALIDATION ... type PICKLIST` - a single-select PICKLIST was sent a `MULTI_PICKLIST` objectValue. Declared-`PICKLIST` columns take a plain `value` + `strict:false`; only declared `MULTI_PICKLIST`, or validated columns that MIS-report as TEXT_NUMBER, take the list wrap. One sheet can carry both shapes (one live Extend task tracker had `Workstream` needs the wrap, `Workday Domain Area` must not get it). |
| 400 | 5087 | Deleting a row comment: use `DELETE /sheets/{id}/comments/{commentId}`, NOT `DELETE /sheets/{id}/discussions/{id}` - the latter returns "insufficient permissions to delete a comment". |
| 429 | 4003 | Rate limit - back off and retry |

## Comment columns fed by automation (detect and never write directly)

A tracker's "Latest Comment" / "Notes" / "Status Update" column is very often NOT a field you fill
in - it is populated by a **sheet automation that mirrors the newest row Conversation**, prepending
the author name and truncating (~350 chars, ending in `...`). Writing it directly fights the
automation:

- your value is **silently overwritten** the next time anyone comments;
- if your text already starts with the author name you get a **doubled prefix** ("Author Name -
  Author Name - ...");
- **watchers are never notified**, because notification rides on the Conversation, not the cell.

**Detect it before writing.** Read a few populated rows of that column: an entry ending in `...`,
carrying an `Author Name - ` prefix nobody typed, or matching the row's newest discussion, means an
automation owns the column - treat it as read-only.

**So to comment:** `POST /sheets/{id}/rows/{rowId}/discussions` with `{"comment": {"text": "..."}}`,
text **without** an author prefix (the automation adds it). The column then updates itself and the
right people are notified. Read comments back from `GET /sheets/{id}/discussions?includeAll=true`
(the single-row `?include=discussions` has been observed returning nothing right after a write - the
sheet-level list is authoritative). To remove one: `DELETE /sheets/{id}/comments/{commentId}` (the
`/discussions/{id}` route 400s with `errorCode 5087`).

**Notification cost is real.** Every Conversation post emails the row's watchers, so a
delete-and-repost to fix formatting notifies them a second time. Get the text right the first time,
and confirm with the user before a corrective repost.

## Safety recap (applies to every write)

1. Read the target rows first (get current values + `_row_id`).
2. Show the user a before -> after diff and get confirmation, unless they already
   specified the exact change.
3. Batch, write, then report the API's returned row count and any failures.
4. Never delete rows without an explicit, per-instance user instruction.
