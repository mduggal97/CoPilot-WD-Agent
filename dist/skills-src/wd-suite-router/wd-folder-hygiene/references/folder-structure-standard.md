# The standard project/app folder structure (firm standard)

Every new app/product project folder uses the **same numbered structure** (the "Cadre" / Phys
Management layout). Scaffold it once at project start, and keep to it - consistent folders make
any project navigable by anyone, and make the archive rule below automatic.

## The canonical layout

```
<Project Name>/
  01_Assessment/        Archive/
  02_Market_Research/   Archive/
  03_Design/            Archive/
  04_Prototype/         Archive/
  05_Proposal/          Archive/
  06_Estimate/          Archive/
  07_Demo/              Archive/
  08_Commercial/        Archive/
  _source/
```

- **Numbered phase folders (`01_`..`08_`)** run in delivery order, so the folder list reads as the
  project timeline. Numbers keep them sorted; the leading zero keeps 01..08 in order past nine.
- **`Archive/` inside every phase folder** - where superseded document versions go (see the rule
  below). Present even when empty, so there is always an obvious place for old versions.
- **`_source/`** (underscore-prefixed) - working/build source that isn't a client-facing
  deliverable (scripts, raw exports, app build source). The `_` sorts these support folders above
  the numbered phases and marks them as "not a deliverable stage." Add other `_`-prefixed support
  folders as needed (e.g. `_crops`, `_screens` under `03_Design`).

## What lives in each phase

| Folder | Holds |
|---|---|
| `01_Assessment` | Opportunity/feasibility assessment, initial notes |
| `02_Market_Research` | Market/whitespace research, competitive scan, sizing |
| `03_Design` | Design doc, wireframes, process flows, screens |
| `04_Prototype` | Built app source / PoC, prototype notes |
| `05_Proposal` | Proposal / pitch deck |
| `06_Estimate` | LOE / UET / pricing workbook |
| `07_Demo` | Demo script, demo data, demo deck |
| `08_Commercial` | SOW / contract / subscription paperwork |

This phase set is the default (a productized / BoW app lifecycle). For a project that genuinely
needs a different set, override with `--phases "01_Discovery,02_Design,..."` - but prefer the
standard so folders stay consistent across projects.

## Scaffold it (every new project)

```
python scripts/archive_old_versions.py "<Project Name>"  --scaffold          # preview
python scripts/archive_old_versions.py "<Project Name>"  --scaffold --apply   # create
```

Idempotent: existing folders are reported `EXISTS` and left untouched, so it is safe to re-run on
a partially-built folder to fill in any missing phase or `Archive/`.

## The auto-archive-on-new-version RULE (standing)

**Whenever a new version of a deliverable is created, the immediately-superseded prior version(s)
of that same family move into that folder's `Archive/` as part of the same save.** Only the
current version of each deliverable ever sits loose in a phase folder; the history lives in
`Archive/`.

- This is the firm standing default - the user has authorized it as policy, so a **single,
  deterministic supersession** (e.g. writing `Cadre_Design_Document_v0.4.xlsx` next to `_v0.3`)
  archives the older file(s) automatically and is just **reported**, not separately confirmed.
- It is enforced by Claude following this rule when it writes a new version - not a background
  process. The producing skills (wd-design-doc, wd-estimate, wd-contracts, wd-design-visuals, the
  deck/doc skills) apply it when they emit a new version into a phase folder.
- Mechanically it is the same archiver: after writing the new version, run
  `archive_old_versions.py "<phase folder>" --apply` (or move the one superseded family member by
  hand) so only the latest remains outside `Archive/`. The manifest still records every move.
- **Bulk or ambiguous cleanups keep the safety contract** - a whole-folder or multi-family tidy is
  still dry-run -> review -> `--apply`. The auto rule covers only the clear, one-family
  supersession that the user just triggered by saving a new version.
