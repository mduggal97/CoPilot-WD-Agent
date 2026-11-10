# Scripts this skill uses - regenerate-on-demand build-spec

`scripts/smartsheet_api.py` is the REST helper this skill drives. It normally ships inside the
skill folder. **If it is not on this machine** (a fresh install, or only some files were copied),
regenerate it: create `scripts/smartsheet_api.py` and write it with the EXACT contents of the
fenced Python block below. It is the canonical, verbatim source - no edits needed.

**Prerequisites to run it:** Python 3.9+ and two packages, `pip install requests keyring`.
`urllib3` ships with `requests`; `keyring` is imported lazily, so the environment-variable and
`.env` token paths still work even if `keyring` is not installed. Full first-time setup -
including how to install Python (on a managed/corporate machine: via your org's software portal, e.g. the **Company Portal**) - is in
[token-setup.md](token-setup.md) Step 0.

**No client data lives here.** This helper is generic; client sheet/workspace IDs live in the
registry reference (a per-client swap), never in this script.

To regenerate from a session: read the code block below and write it verbatim to
`scripts/smartsheet_api.py`, then run `python scripts/smartsheet_api.py test` to confirm.

## Known column-type gotchas

**Assigned To, Watchers, and Workstream-style columns mis-report their type** - Smartsheet's column API returns `TEXT_NUMBER` for these columns, but the write API requires their actual specialized type. Writing a plain string value to an Assigned To or Watchers column returns a 400 error. Workaround: always fetch the live column list with `GET /sheets/{id}/columns` and identify these columns **by name**, not by the reported type. Build your write payload using the column-specific format the API expects (Assigned To = `{"objectType": "CONTACT", "email": "..."}`, Watchers = array of contacts). Never infer write format from the `type` field on these columns. (Verified causing write 400s in a delivered session, 2026-08-21.)

## Comment / discussion helpers (function contract)

These wrap the row-Conversation flow that SKILL.md section 4 ("Adding a COMMENT") and section 4b
require - so a narrative update goes to a row's discussion, never to an automation-mirrored cell.
They already exist in `scripts/smartsheet_api.py`; documented here so the spec matches the code.
Contract only - do not re-paste the code (it is in the canonical block below):

- **`add_row_comment(sheet_id, row_id, text)`** - POST `/sheets/{id}/rows/{rowId}/discussions` with
  `{"comment": {"text": text}}`. Posts one comment into a row's Conversations panel (NOT a cell
  value). Write `text` WITHOUT an author prefix - the sheet automation prepends it. Returns the
  created discussion object. NOTE: this notifies the row's assignees/watchers, exactly like a
  comment typed in the UI, so get the wording right the first time.
- **`add_row_comments(sheet_id, comments)`** - `comments` is a list of `{"row_id": 123, "text":
  "..."}`. Posts several row comments; the API has no batch endpoint for discussions, so these go
  one row at a time and a failure on one row raises immediately (not silently skipped). Returns the
  list of created discussion objects.

**Intentionally raw-REST (no helper function).** Reading comments back and deleting one are NOT
wrapped - call them directly per SKILL.md section 4: read via `GET /sheets/{id}/discussions?includeAll=true`
(the sheet-level list is authoritative; the single-row `?include=discussions` has returned nothing
right after a write), and remove one via `DELETE /sheets/{id}/comments/{commentId}` (the
`/discussions/{id}` route 400s with `errorCode 5087`). The 4b upsert/header-scoring logic is
likewise raw-REST orchestration built on `get_sheet` / `add_rows` / `update_rows`, not its own
helper function.

## smartsheet_api.py (canonical source - write verbatim)

```python
"""
smartsheet_api.py - small Smartsheet REST helper for tracker read/write work.

WHAT THIS FILE IS (plain English):
Smartsheet stores every sheet as rows of "cells", and each cell only knows the
numeric ID of the column it belongs to - not the column's name. That makes the
raw API awkward to work with. This helper does the boring translation for you:
you read and write rows as ordinary Python dicts keyed by the column TITLES you
see in the Smartsheet UI (e.g. {"Status": "Completed"}), and the helper looks up
the numeric column IDs behind the scenes.

AUTH (no token is ever hardcoded here):
The API token is found in this order:
  1. SMARTSHEET_API_TOKEN environment variable
  2. Windows Credential Manager (keyring), under a keyring service name,
     overridable via SMARTSHEET_KEYRING_SERVICE; default "smartsheet_api_token",
     entry "default/smartsheet_token"
  3. A .env file in the current directory (legacy: .env)

SSL NOTE (why verify=False):
A corporate network may inspect HTTPS traffic by re-signing it with its own
certificates ("SSL inspection" / man-in-the-middle proxy). Python does not trust
those corporate certificates by default, so certificate verification fails even
though the connection is fine. We therefore disable verification and silence the
warning. On a normal network you could remove both lines.

STANDALONE USE:
    python smartsheet_api.py test        # calls GET /users/me to verify the token works
    python smartsheet_api.py sheet <id>  # prints column titles + row count for a sheet
"""
from __future__ import annotations

import os
import re
import sys
from typing import Any, Callable, Optional

import requests
import urllib3

# Silence the "InsecureRequestWarning" that urllib3 prints every request when
# verify=False. See SSL NOTE in the module docstring for why this is OK here.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SMARTSHEET_BASE_URL = "https://api.smartsheet.com/2.0"

# Smartsheet accepts at most ~500 rows per add/update request, so we chunk.
MAX_ROWS_PER_REQUEST = 500

# Keyring coordinates. Service name is overridable via SMARTSHEET_KEYRING_SERVICE;
# default "smartsheet_api_token". If your token is under a historical service name,
# set SMARTSHEET_KEYRING_SERVICE to it.
KEYRING_SERVICE_NAME = os.environ.get("SMARTSHEET_KEYRING_SERVICE", "smartsheet_api_token")
KEYRING_ENTRY_NAME = "default/smartsheet_token"


# ---------------------------------------------------------------------------
# Token lookup - env var first, then Windows Credential Manager, then .env
# ---------------------------------------------------------------------------

def load_api_token() -> str:
    """Find the Smartsheet API token. Raises with a helpful message if missing."""
    # 1. Environment variable - the simplest and most portable location.
    token_from_env = os.environ.get("SMARTSHEET_API_TOKEN")
    if token_from_env:
        return token_from_env

    # 2. Windows Credential Manager via keyring (service name from SMARTSHEET_KEYRING_SERVICE).
    try:
        import keyring  # imported lazily so the script works without it installed
        token_from_keyring = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_ENTRY_NAME)
        if token_from_keyring:
            return token_from_keyring
    except Exception:
        pass  # keyring not installed or no entry - fall through to .env

    # 3. Legacy .env file (a ".env" in the current directory). Parsed with a tiny
    #    stdlib reader so this documented fallback works with NO extra install -
    #    python-dotenv is NOT a dependency of this helper (it used to be silently
    #    required here, which made the .env path a no-op on standard installs).
    try:
        with open(".env", "r", encoding="utf-8-sig") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                if key.strip() == "SMARTSHEET_API_TOKEN":
                    val = val.strip().strip('"').strip("'")
                    if val:
                        return val
    except OSError:
        pass

    raise RuntimeError(
        "No Smartsheet token found. Set the SMARTSHEET_API_TOKEN environment "
        "variable, or store it in Windows Credential Manager under service "
        f"'{KEYRING_SERVICE_NAME}', or put it in a .env file."
    )


# ---------------------------------------------------------------------------
# HTTP session - one shared session with the Bearer token attached
# ---------------------------------------------------------------------------

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    """Build (once) and return a requests session with auth headers set."""
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({
            "Authorization": f"Bearer {load_api_token()}",
            "Content-Type": "application/json",
        })
        # Corporate SSL inspection bypass - see module docstring.
        _session.verify = False
    return _session


def _request(method: str, path: str, params: dict | None = None,
             body: Any = None) -> dict:
    """One API call. Raises requests.HTTPError with the API's message on failure."""
    response = _get_session().request(
        method, f"{SMARTSHEET_BASE_URL}{path}", params=params,
        json=body, verify=False,
    )
    if not response.ok:
        # Surface Smartsheet's own error message (much more useful than "400").
        raise requests.HTTPError(
            f"{method} {path} -> HTTP {response.status_code}: {response.text[:500]}",
            response=response,
        )
    return response.json()


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

def _strip_html(value: Any) -> Any:
    """Smartsheet rich-text cells can come back with HTML tags - remove them."""
    if not isinstance(value, str):
        return value
    # Turn common "line break" style tags into spaces so words don't glue together.
    clean = re.sub(r"<br\s*/?>|</p>|</div>|</li>", " ", value, flags=re.IGNORECASE)
    clean = re.sub(r"<[^>]+>", "", clean)  # drop any remaining tags
    clean = (clean.replace("&amp;", "&").replace("&lt;", "<")
                  .replace("&gt;", ">").replace("&nbsp;", " "))
    return " ".join(clean.split())


def _rows_to_dicts(columns: list[dict], raw_rows: list[dict]) -> list[dict]:
    """Turn Smartsheet's cell arrays into plain dicts keyed by column title.

    We prefer 'displayValue' (what a human sees in the UI - formatted dates,
    picklist labels) over the raw 'value'. Every dict keeps the Smartsheet row
    ID under '_row_id' because updates require it later.
    """
    column_id_to_title = {col["id"]: col["title"] for col in columns}
    row_dicts = []
    for raw_row in raw_rows:
        record: dict[str, Any] = {"_row_id": raw_row["id"]}
        for cell in raw_row.get("cells", []):
            column_title = column_id_to_title.get(cell.get("columnId"))
            if not column_title:
                continue
            cell_value = cell.get("displayValue")
            if cell_value is None:
                cell_value = cell.get("value")
            record[column_title] = _strip_html(cell_value)
        row_dicts.append(record)
    return row_dicts


def _get_column_map(sheet_id: int) -> dict[str, dict]:
    """Fetch just the columns of a sheet: {column title -> full column object}.

    We keep the full column object (not just the ID) so callers can also check
    things like 'type' (PICKLIST, CONTACT_LIST) and picklist 'options'.
    Fetching with pageSize=1 keeps the payload tiny - we only need columns.
    """
    sheet_data = _request("GET", f"/sheets/{sheet_id}",
                          params={"pageSize": 1, "include": "columns"})
    return {col["title"]: col for col in sheet_data.get("columns", [])}


# ---------------------------------------------------------------------------
# Public API - reads
# ---------------------------------------------------------------------------

def test_connection() -> dict:
    """GET /users/me - the standard 'is my token good?' check."""
    return _request("GET", "/users/me")


def get_sheet(sheet_id: int) -> tuple[list[dict], list[dict]]:
    """Fetch a whole sheet, following pagination until every row is collected.

    Returns (columns, rows) where:
      columns = Smartsheet's raw column objects (id, title, type, options, ...)
      rows    = list of dicts keyed by column TITLE, each with '_row_id'
    """
    first_page = _request("GET", f"/sheets/{sheet_id}",
                          params={"pageSize": 500, "page": 1})
    columns = first_page.get("columns", [])
    raw_rows = first_page.get("rows", [])
    total_row_count = first_page.get("totalRowCount", 0)

    # Keep asking for the next page until we have every row the sheet reports.
    page_number = 2
    while len(raw_rows) < total_row_count:
        next_page = _request("GET", f"/sheets/{sheet_id}",
                             params={"pageSize": 500, "page": page_number})
        page_rows = next_page.get("rows", [])
        if not page_rows:  # safety valve - never loop forever
            break
        raw_rows.extend(page_rows)
        page_number += 1

    return columns, _rows_to_dicts(columns, raw_rows)


def find_rows(sheet_id: int, filter_fn: Callable[[dict], bool]) -> list[dict]:
    """Fetch the sheet and return only the row-dicts your filter accepts.

    Example: find_rows(raid_sheet_id, lambda r: r.get("Status") == "In-Progress")
    """
    _columns, rows = get_sheet(sheet_id)
    return [row for row in rows if filter_fn(row)]


# ---------------------------------------------------------------------------
# Public API - writes
# ---------------------------------------------------------------------------

# Column titles that routinely turn out to be CONTACT_LIST/MULTI_CONTACT_LIST
# even when `describe`/the columns API reports them as TEXT_NUMBER. Learned
# the hard way on a live Extend task tracker: "Assigned To" and "Watchers" both
# report TEXT_NUMBER with validation:false, yet reject plain-string writes
# with HTTP 400 "Use objectValue instead."
CONTACT_TITLE_HINTS = (
    "assigned", "watcher", "owner", "approver", "requested by",
    "reviewer", "contact",
)


def _looks_like_contact_column(column: dict) -> bool:
    title = (column.get("title") or "").lower()
    return any(hint in title for hint in CONTACT_TITLE_HINTS)


def _contact_obj(v: Any) -> dict:
    """Build a Smartsheet CONTACT object from a dict {name?, email?}, a
    'Name <email>' string, a bare email, or a bare name."""
    if isinstance(v, dict):
        c = {"objectType": "CONTACT"}
        if v.get("name"):
            c["name"] = v["name"]
        if v.get("email"):
            c["email"] = v["email"]
        return c
    text = str(v).strip()
    m = re.match(r"^(.*?)\s*<\s*([^>]+@[^>]+)\s*>$", text)
    if m:
        return {"objectType": "CONTACT", "name": m.group(1).strip(), "email": m.group(2).strip()}
    if "@" in text:
        return {"objectType": "CONTACT", "email": text}
    return {"objectType": "CONTACT", "name": text}


def _cell_for(column: dict, new_value: Any, strict_picklists: bool):
    """Build one cell dict, choosing value vs objectValue by the VALUE SHAPE
    (robust even when a column mis-reports its type - some contact columns
    report as TEXT_NUMBER yet still require objectValue). Returns None for
    system/formula columns, which are NOT writable and must be skipped."""
    cid = column["id"]
    ctype = column.get("type")
    # 1) system / column-formula cells are not writable
    if column.get("systemColumnType") or column.get("formula"):
        return None
    # 2) a LIST of contacts -> MULTI_CONTACT (shape wins over declared type)
    if isinstance(new_value, (list, tuple)) and new_value and all(
        isinstance(x, dict) and ("email" in x or "name" in x) for x in new_value
    ):
        return {"columnId": cid, "strict": False,
                "objectValue": {"objectType": "MULTI_CONTACT", "values": [_contact_obj(x) for x in new_value]}}
    # 3) a single contact dict -> CONTACT
    if isinstance(new_value, dict) and ("email" in new_value or "name" in new_value):
        return {"columnId": cid, "objectValue": _contact_obj(new_value), "strict": False}
    # 4) contact-typed columns given a plain string
    if ctype == "CONTACT_LIST" and isinstance(new_value, str):
        return {"columnId": cid, "objectValue": _contact_obj(new_value), "strict": False}
    if ctype == "MULTI_CONTACT_LIST" and isinstance(new_value, str):
        parts = [p.strip() for p in new_value.split(",") if p.strip()]
        return {"columnId": cid, "strict": False,
                "objectValue": {"objectType": "MULTI_CONTACT", "values": [_contact_obj(p) for p in parts]}}
    # 5) multi-select -> MULTI_PICKLIST objectValue, from a LIST of strings OR
    #    a single plain string (wrapped as a one-item list). Covers real
    #    MULTI_PICKLIST columns AND validated multi-select columns that
    #    mis-report as TEXT_NUMBER but still require objectValue (e.g. a
    #    "Domain Area(s) Impacted" or "Workstream" dropdown) - a plain string
    #    into one of these 400s with "did not conform to ... type
    #    MULTI_PICKLIST" even though `describe` shows TEXT_NUMBER.
    #    IMPORTANT: a column whose declared type is genuinely PICKLIST is
    #    SINGLE-select - wrapping its value in a MULTI_PICKLIST objectValue
    #    400s with errorCode 5536 "did not conform to the strict requirements
    #    for type PICKLIST". Only apply the wrap to declared MULTI_PICKLIST
    #    columns, or to validated columns that MIS-REPORT as something else
    #    (TEXT_NUMBER). One sheet can carry both shapes: on one live Extend Task
    #    Tracker, "Workstream" mis-reports as TEXT_NUMBER and NEEDS the wrap,
    #    while "Workday Domain Area" is a true PICKLIST and must NOT get it.
    if (ctype == "MULTI_PICKLIST"
            or (ctype != "PICKLIST" and column.get("validation") and column.get("options"))):
        if isinstance(new_value, (list, tuple)) and all(isinstance(x, str) for x in new_value):
            return {"columnId": cid, "strict": False,
                    "objectValue": {"objectType": "MULTI_PICKLIST", "values": list(new_value)}}
        if isinstance(new_value, str):
            return {"columnId": cid, "strict": False,
                    "objectValue": {"objectType": "MULTI_PICKLIST", "values": [new_value]}}
    # 5b) columns whose TITLE strongly suggests a person/people field
    #    (Assigned To, Watcher(s), Owner, Approver, Requested By, Reviewer,
    #    Contact) routinely turn out to be CONTACT_LIST/MULTI_CONTACT_LIST
    #    columns that mis-report as TEXT_NUMBER - this is the #1 recurring
    #    write failure on Extend task trackers (400: "Use objectValue
    #    instead"). Treat a plain string as a comma-separated contact list
    #    rather than free text, UNLESS the column is already a known
    #    non-contact type (PICKLIST/validated) or the value came in as a
    #    dict/list (already handled above).
    if ctype not in ("CONTACT_LIST", "MULTI_CONTACT_LIST", "PICKLIST", "MULTI_PICKLIST") \
            and not column.get("validation") and isinstance(new_value, str) \
            and _looks_like_contact_column(column):
        parts = [p.strip() for p in new_value.split(",") if p.strip()]
        if len(parts) > 1:
            return {"columnId": cid, "strict": False,
                    "objectValue": {"objectType": "MULTI_CONTACT", "values": [_contact_obj(p) for p in parts]}}
        return {"columnId": cid, "objectValue": _contact_obj(new_value), "strict": False}
    # 6) default: plain value
    cell: dict[str, Any] = {"columnId": cid, "value": new_value}
    if not strict_picklists and ctype in ("PICKLIST", "MULTI_PICKLIST"):
        cell["strict"] = False
    return cell


def _build_cells(row_values: dict, column_map: dict[str, dict],
                 strict_picklists: bool = True) -> list[dict]:
    """Convert {"Column Title": value} into Smartsheet's cell objects.

    - Contact / multi-contact / multi-picklist columns are written via
      `objectValue` automatically (pass a contact dict `{"name","email"}`, a
      list of them, a `"Name <email>"` string, or a comma-joined string).
    - System / column-formula columns (auto-number ID, "created by", etc.) are
      silently SKIPPED - they aren't writable (a warning is emitted).
    Raises with a clear message if a column title doesn't exist on the sheet.
    """
    cells, skipped, skipped_locked = [], [], []
    for column_title, new_value in row_values.items():
        if column_title.startswith("_"):
            continue  # skip helper keys like _row_id
        column = column_map.get(column_title) or column_map.get(column_title.strip())
        if column is None:
            known = ", ".join(sorted(column_map.keys()))
            raise KeyError(
                f"Column '{column_title}' not found on this sheet. "
                f"Known columns: {known}"
            )
        # Locked columns: Smartsheet rejects the ENTIRE multi-row request
        # (errorCode 1051) if even ONE cell targets a locked column, silently
        # killing every other valid update in the batch. Skip-and-warn instead,
        # the same way system/formula columns are handled. `lockedForUser` is
        # the authoritative per-token flag (a sheet Admin may write a `locked`
        # column, so `locked` alone doesn't mean unwritable for us).
        if column.get("lockedForUser"):
            skipped_locked.append(column_title)
            continue
        cell = _cell_for(column, new_value, strict_picklists)
        if cell is None:
            skipped.append(column_title)
            continue
        cells.append(cell)
    if skipped:
        print("wd-smartsheet: skipped non-writable system/formula column(s): "
              + ", ".join(skipped), file=sys.stderr)
    if skipped_locked:
        print("wd-smartsheet: skipped LOCKED column(s) (one locked cell 400s the "
              "whole batch, errorCode 1051): " + ", ".join(skipped_locked)
              + " - post the text as a row comment (add_row_comment) or ask a "
              "sheet Admin to unlock", file=sys.stderr)
    return cells


def _chunked(items: list, chunk_size: int = MAX_ROWS_PER_REQUEST):
    """Yield the list in slices - Smartsheet caps rows per request (~500)."""
    for start in range(0, len(items), chunk_size):
        yield items[start:start + chunk_size]


def add_rows(sheet_id: int, new_rows: list[dict], to_top: bool = False,
             parent_id: int | None = None,
             strict_picklists: bool = True) -> list[dict]:
    """Add rows to a sheet. Each item in new_rows is {"Column Title": value}.

    Placement: bottom of the sheet by default; to_top=True for the top;
    parent_id=<row id> to nest the new rows under an existing parent row
    (used on hierarchical sheets like project plans).

    Returns the API's created-row objects (they include the new row IDs).
    """
    column_map = _get_column_map(sheet_id)
    row_payloads = []
    for row_values in new_rows:
        payload: dict[str, Any] = {
            "cells": _build_cells(row_values, column_map, strict_picklists),
        }
        if parent_id is not None:
            payload["parentId"] = parent_id
        elif to_top:
            payload["toTop"] = True
        else:
            payload["toBottom"] = True
        row_payloads.append(payload)

    created_rows: list[dict] = []
    for batch in _chunked(row_payloads):
        result = _request("POST", f"/sheets/{sheet_id}/rows", body=batch)
        created_rows.extend(result.get("result", []))
    return created_rows


def update_rows(sheet_id: int, updates: list[dict],
                strict_picklists: bool = True) -> list[dict]:
    """Update existing rows. Each item: {"row_id": 123, "updates": {"Status": "Done"}}.

    Only the columns named in 'updates' are touched - every other cell in the
    row keeps its current value. Note: cells containing formulas cannot be
    written this way; Smartsheet will reject the request.

    Returns the API's updated-row objects.
    """
    column_map = _get_column_map(sheet_id)
    row_payloads = []
    for update in updates:
        row_payloads.append({
            "id": update["row_id"],
            "cells": _build_cells(update["updates"], column_map, strict_picklists),
        })

    updated_rows: list[dict] = []
    for batch in _chunked(row_payloads):
        result = _request("PUT", f"/sheets/{sheet_id}/rows", body=batch)
        updated_rows.extend(result.get("result", []))
    return updated_rows


def add_row_comment(sheet_id: int, row_id: int, text: str) -> dict:
    """Post a comment into a row's Conversations panel (NOT a cell value).

    This is the right home for narrative updates - meeting outcomes, answers,
    decisions - on sheets that keep a 'Latest Comment' style column: the column
    is fed from the conversation by the sheet's own automation, so writing the
    cell directly fights that automation and loses the author/timestamp trail.
    Also the fallback when a column is locked (errorCode 1051).

    Note: this notifies the row's assignees/watchers, same as a comment typed
    in the UI. Returns the created discussion object.
    """
    return _request("POST", f"/sheets/{sheet_id}/rows/{row_id}/discussions",
                    body={"comment": {"text": text}})


def add_row_comments(sheet_id: int, comments: list[dict]) -> list[dict]:
    """Post several row comments. Each item: {"row_id": 123, "text": "..."}.

    The API has no batch endpoint for discussions, so these go one at a time;
    a failure on one row is raised immediately rather than silently skipped.
    """
    return [add_row_comment(sheet_id, c["row_id"], c["text"]) for c in comments]


def resolve_contacts(names: list[str], contact_sheet_id: int,
                     name_col: str = "Full Name", first_col: str = "First Name",
                     last_col: str = "Last Name", email_col: str = "Email") -> list[dict]:
    """Look up emails for person NAMES from a contact-list / roster sheet.

    Returns a list of contact dicts [{"name","email"}] ready to pass straight
    into a contact column via add_rows/update_rows. Names not found come back
    name-only, and the unresolved names are printed to stderr so you can supply
    those emails manually (never guess an address). Match is case-insensitive
    on the full name (falls back to First + Last).
    """
    _, rows = get_sheet(contact_sheet_id)

    def full(r):
        f = str(r.get(name_col) or "").strip()
        if not f:
            f = (str(r.get(first_col) or "").strip() + " " + str(r.get(last_col) or "").strip()).strip()
        return f

    index = {}
    for r in rows:
        nm, em = full(r).lower(), r.get(email_col)
        if nm and em:
            index[nm] = str(em).strip()

    out, unresolved = [], []
    for n in names:
        em = index.get(str(n).strip().lower())
        out.append({"name": n, "email": em} if em else {"name": n})
        if not em:
            unresolved.append(n)
    if unresolved:
        print("wd-smartsheet: no email found for: " + ", ".join(unresolved)
              + " (added name-only; supply emails to finalize)", file=sys.stderr)
    return out


def column_report(sheet_id: int) -> list[dict]:
    """Describe every column for a PRE-WRITE review - the schema varies per
    sheet and people change it, so never assume; inspect it live.

    Each entry: title, type, whether it's system/formula (NOT writable),
    validated + its picklist `options`, and **fill_rate** = the fraction of
    existing rows where the column is populated. A high fill_rate on a column
    you were about to leave blank is a likely MISS (a field the team expects) -
    decide populate-vs-skip for every column, don't just fill the obvious ones.
    """
    cols, rows = get_sheet(sheet_id)
    n = len(rows) or 1
    report = []
    for c in cols:
        title = c["title"]
        filled = sum(1 for r in rows if str(r.get(title, "")).strip() not in ("", "None"))
        report.append({
            "title": title,
            "type": c.get("type"),
            "system": bool(c.get("systemColumnType")),
            "formula": bool(c.get("formula")),
            "validated": bool(c.get("validation")),
            "options": c.get("options") or None,
            "filled": filled,
            "total": len(rows),
            "fill_rate": round(filled / n, 2),
            "likely_contact": c.get("type") not in ("CONTACT_LIST", "MULTI_CONTACT_LIST")
                and _looks_like_contact_column(c),
            "locked": bool(c.get("lockedForUser") or c.get("locked")),
        })
    return report


# ---------------------------------------------------------------------------
# Discovery - let a user point us at the right workspace / sheet by NAME
# ---------------------------------------------------------------------------

def list_workspaces() -> list[dict]:
    """Every workspace this token can see: [{id, name, permalink}]. This is how a
    user 'directs' us - they name a workspace, we resolve it to its id here.
    Bounded by the token account's Smartsheet sharing (you only see what's shared)."""
    result = _request("GET", "/workspaces", params={"includeAll": True})
    return result.get("data", result.get("workspaces", []))


def list_sheets_in_workspace(workspace_id: int) -> list[dict]:
    """Sheets directly in a workspace: [{id, name}]. (Sheets inside folders are
    reached via the workspace's 'folders' - expand if a client nests them.)"""
    detail = _request("GET", f"/workspaces/{workspace_id}")
    return detail.get("sheets", [])


def find_sheets_by_name(name_substring: str) -> list[dict]:
    """Search every visible sheet by name (case-insensitive substring) ->
    [{id, name, workspace}]. Use when the user names a sheet but not its workspace
    or id. Uses Smartsheet's search so it also finds folder-nested sheets."""
    result = _request("GET", "/search", params={"query": name_substring})
    hits = []
    for item in result.get("results", []):
        if item.get("objectType") == "sheet" and name_substring.lower() in (item.get("text", "").lower()):
            hits.append({"id": item.get("objectId"), "name": item.get("text"),
                         "context": item.get("contextData", [])})
    return hits


# ---------------------------------------------------------------------------
# Standalone entry point - quick smoke tests from a terminal
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "test"

    if command == "test":
        # Proves the token works and shows whose token it is.
        me = test_connection()
        print(f"Connected as: {me.get('email')} ({me.get('firstName', '')} "
              f"{me.get('lastName', '')})".strip())

    elif command == "sheet" and len(sys.argv) > 2:
        # Quick look at a sheet: column titles and how many rows it has.
        target_sheet_id = int(sys.argv[2])
        sheet_columns, sheet_rows = get_sheet(target_sheet_id)
        print(f"Sheet {target_sheet_id}: {len(sheet_rows)} rows, "
              f"{len(sheet_columns)} columns")
        for col in sheet_columns:
            print(f"  - {col['title']}  ({col.get('type')})")

    elif command == "workspaces":
        # List every workspace the token can see (user picks one by name).
        for w in list_workspaces():
            print(f"  {w.get('id')}  {w.get('name')!r}")

    elif command == "sheets" and len(sys.argv) > 2:
        # List the sheets in a workspace (user picks one by name).
        for s in list_sheets_in_workspace(int(sys.argv[2])):
            print(f"  {s.get('id')}  {s.get('name')!r}")

    elif command == "find" and len(sys.argv) > 2:
        # Find sheets by name across all workspaces (when only the name is known).
        for s in find_sheets_by_name(" ".join(sys.argv[2:])):
            print(f"  {s.get('id')}  {s.get('name')!r}")

    elif command == "describe" and len(sys.argv) > 2:
        # PRE-WRITE column review: every column with type, flags, options, and
        # how consistently it's already filled (sorted most-filled first).
        report = sorted(column_report(int(sys.argv[2])),
                        key=lambda d: d["fill_rate"], reverse=True)
        print(f"{len(report)} columns (fill% = how often already populated; "
              f"review every one before writing):")
        for d in report:
            flags = " ".join(f for f, on in (("SYSTEM", d["system"]),
                             ("FORMULA", d["formula"]), ("VALIDATED", d["validated"]),
                             ("LOCKED-one locked cell 400s the whole batch", d.get("locked")),
                             ("LIKELY_CONTACT-verify before plain-text write", d["likely_contact"])) if on)
            opts = ("  options=[" + ", ".join(map(str, d["options"][:6]))
                    + ("..." if len(d["options"]) > 6 else "") + "]") if d["options"] else ""
            print(f"  {int(d['fill_rate']*100):3d}%  {d['title']!r:44} "
                  f"{str(d['type']):16} {flags}{opts}")

    elif command == "set-token":
        # Store the token ONCE, securely, in Windows Credential Manager (keyring)
        # where load_api_token() already reads it. The token is typed at a HIDDEN prompt
        # (getpass) - it never appears in chat, in shell history, or in a file, and
        # is never echoed back. Persists across sessions/reboots; do this one time.
        import getpass
        try:
            import keyring
        except ImportError:
            print("keyring is not installed. Run:  pip install keyring"); sys.exit(1)
        print("Paste your Smartsheet API token, then press Enter.")
        print("(Input is HIDDEN - not shown, not logged, not sent to chat.)")
        token_value = getpass.getpass("Smartsheet token: ").strip()
        if not token_value:
            print("No token entered - nothing stored."); sys.exit(1)
        keyring.set_password(KEYRING_SERVICE_NAME, KEYRING_ENTRY_NAME, token_value)
        del token_value  # don't keep it in memory
        # Verify by making a call (which re-reads it from the store) - never print the token.
        try:
            me = test_connection()
            print(f"Stored securely in Windows Credential Manager and verified as: "
                  f"{me.get('email')}. You won't need to enter it again.")
        except Exception as exc:  # noqa: BLE001
            print("Stored, but the verification call failed - double-check the token. "
                  f"({str(exc)[:80]})")

    elif command == "check-token":
        # Diagnose a stored token WITHOUT exposing it: report whether one is
        # stored, its length, and a masked preview (first/last 4 only), then test.
        try:
            import keyring
            stored = keyring.get_password(KEYRING_SERVICE_NAME, KEYRING_ENTRY_NAME)
        except Exception:
            stored = None
        env = os.environ.get("SMARTSHEET_API_TOKEN")
        src = "env var" if env else ("Credential Manager" if stored else None)
        tok = env or stored
        if not tok:
            print("No token found in env var or Credential Manager. Run set-token."); sys.exit(1)
        preview = (tok[:4] + "..." + tok[-4:]) if len(tok) > 8 else "(too short)"
        looks_odd = (len(tok) < 20) or any(c.isspace() for c in tok)
        print(f"Token source: {src} | length: {len(tok)} | preview: {preview}"
              + ("  (!) looks truncated or contains whitespace - likely a bad paste" if looks_odd else ""))
        try:
            me = test_connection()
            print(f"Live check: VALID - {me.get('email')}")
        except Exception as exc:  # noqa: BLE001
            print(f"Live check: INVALID - {str(exc)[:90]}. "
                  "Generate a FRESH token in Smartsheet and re-run set-token.")

    elif command == "clear-token":
        try:
            import keyring
            keyring.delete_password(KEYRING_SERVICE_NAME, KEYRING_ENTRY_NAME)
            print("Removed the stored Smartsheet token from Windows Credential Manager.")
        except Exception:  # noqa: BLE001
            print("No stored token found (nothing to remove).")

    else:
        print("Usage: python smartsheet_api.py test | set-token | check-token | "
              "clear-token | workspaces | sheets <workspace_id> | find <name> | "
              "sheet <sheet_id> | describe <sheet_id>")
        sys.exit(1)
```
