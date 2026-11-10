# Smartsheet Sheet Registry - per-engagement template

> **Fill this per engagement** from discovery and/or `GET /workspaces` ->
> `GET /workspaces/{id}`. **The actual values live in the engagement's project
> memory, not in this skill** - this file is only the shape a registry takes.
> Never hardcode another engagement's IDs here; sheet IDs are not visible in the
> browser URL, so resolve them by name via the API (`find <name>`, `sheets <workspace_id>`).

## Workspace

| Item | ID |
|---|---|
| Workspace: **\<engagement workspace name\>** | `<workspace-id>` |
| Root folder | `<root-folder-id>` |

## Sheet ID map

One row per tracker the engagement uses. Give each a short stable `<name>` key you
can reference in code/prose, and the live sheet ID.

```python
SHEET_IDS = {
    "<name>":  <sheet-id>,   # e.g. "raid_log": 0000000000000000
    "<name>":  <sheet-id>,
    # ...one entry per in-scope tracker...
}
```

## Per-sheet key columns

For each sheet above, capture the columns you actually read/write - because
schemas differ project-to-project and people edit them, so always confirm against
the live sheet (`describe <sheet_id>`) before writing. Suggested shape:

- **\<name\>** - *\<sheet title\>* (~N rows). One row per \<unit\>. Key columns:
  `<identifier col>`, `<status col(s)>` (note picklist options), `<scope/filter col>`,
  `<owner/contact col(s)>`, `<date col(s)>`, plus any `SYSTEM`/`FORMULA`/`VALIDATED`
  columns to skip on write.
- *(repeat per sheet)*

## Gotchas to record per engagement

Note anything the live sheets do that will bite a writer, e.g.:

- Column-name inconsistencies across sheets (`Workstream` vs `Work Stream`,
  `In Scope` vs `In-Scope`, spacing around hyphens in `Assigned To` columns).
- Which `Scope` value to filter on before aggregating or bulk-updating.
- Free-text vs picklist status columns (free-text writes are unconstrained - match
  the existing format exactly).
- Auto-number / column-formula columns that must not be written.
