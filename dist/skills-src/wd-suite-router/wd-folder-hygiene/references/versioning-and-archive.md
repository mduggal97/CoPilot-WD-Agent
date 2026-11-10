# Version detection, edge cases, and undo

The engine is `scripts/archive_old_versions.py` (bundled, stdlib-only, cross-platform). This is the reasoning behind it and the cases to watch.

## How a family is formed

For each file, the tool finds the **last** version token in the stem and removes it to get the family **base**; files sharing `(base, extension)` are one family. The token also yields a sort key so the family's newest member can be picked.

Precedence (a higher class always outranks a lower one within a family):

1. **Semver** - `[ _-]v<major>[.<minor>[.<patch>]]` (case-insensitive): `_v1.0`, ` v0.9`, `_v2.0.1`. Key = `(3, major, minor, patch)`.
2. **Date** - `_YYYYMMDD` or `_YYYY-MM-DD`: `_20260623`. Key = `(2, dateint)`.
3. **Copy number** - a trailing ` (n)`: `Report (13).docx`. Key = `(1, n)`.
4. **None** - no token. Key = `(0,)` - an unversioned file ranks **below** any versioned sibling, so `Design Doc.xlsx` is archived in favor of `Design Doc_v2.0.xlsx`.

Ties (same key class and value) break by file **modified time** (newer wins). A family with only **one** member is never touched.

## What gets archived vs. kept

- **Kept (in place):** the single highest-ranked file in each family, and any file that is the only member of its family.
- **Archived (moved to `Archive/`):** every *other* member of a family that has >=2 members.
- **Ignored entirely:** the `Archive/` folder itself, `archive_manifest.csv`, and Office lock files (`~$...`).

## Edge cases to watch (call these out in the dry-run review)

- **Copy numbers aren't guaranteed chronological.** OneDrive/Drive conflict copies like `Deck (12)` / `Deck (13)` are ranked by the number, but `(13)` isn't *always* the newest content. Have the user eyeball copy-number families before `--apply`.
- **Mixed tokens in one family.** If a base has both `_v1.0` and a `_20260623` dated copy, semver outranks date - the tool keeps the semver one. If that's wrong for a given folder, move by hand or rename first.
- **Different extensions are different families.** `Foo_v1.xlsx` and `Foo_v1.pdf` don't compete - each extension is its own family. (An export PDF of an old version won't be archived just because a newer `.xlsx` exists.)
- **Base-name drift / renames.** If the base was renamed between versions (`Draft Design` -> `Design Document`, or an app rename `OldName_...` -> `NewName_...`), the two lineages won't group - the safe failure (nothing wrongly archived). Clean up the legacy lineage with **`--match "<old name>"`** (archives every matching file regardless of version), which is the intended remedy for a rename.
- **Version marker with no separator.** The detector only reads `_v2`/` v2`/`-v2` (a separator before `v`), so a marker jammed onto the name - `OldNameV2_Wireframes` vs `...V3...` - is NOT parsed as a version, and both are kept. This is intentional (loosening it would false-positive on real names ending in a letter+number). Handle these with `--match` or move by hand.
- **Realignment/backlog vs. the design doc.** These are *separate* families (different base), so a `Realignment_Backlog_v0.6` is kept independently of `Design_Document_v2.0` - correct.
- **Macro workbooks (`.xlsm`) / IDDs.** Treated like any versioned file; the tool only moves them, never opens them, so VBA/macros are untouched.
- **Non-version noise** (`FINAL`, `DRAFT`, `OLD`, `backup`) is **not** parsed as a version - those files stay unless they also carry a real version token. Archiving by keyword is intentionally out of scope (too easy to get wrong); do it by hand if needed.

## Recurse mode

`--archive-name <Name>` changes the archive folder's name from the default `Archive` (e.g. a client
folder that already uses `_Archive` or `Superseded` - match their convention rather than adding a
second archive folder).

`--recurse` processes the top folder **and every subfolder** (except `Archive/`), each independently - so a parent with per-app subfolders (each holding its own `..._v0.1..v2.0`) gets each app tidied into that app's own `Archive/`. The manifest is written once at the top folder. Default (no `--recurse`) is a single folder - the safer choice; start there.

## Undo

Every applied move is appended to `archive_manifest.csv` at the top folder: `timestamp, original, archived_to`. To reverse, move each `archived_to` back to `original` (a few lines of Python/PowerShell over the CSV, or by hand). Because nothing is deleted, a mistaken archive is always recoverable while the `Archive/` folder exists.

## Before --apply - the checklist

1. Ran the **dry run** and the KEEP list is genuinely the current file of each family.
2. Eyeballed any **copy-number** families.
3. Confirmed with the user (shared folder).
4. No target files are **open** in an app (they'll be skipped and reported; close + re-run for those).
