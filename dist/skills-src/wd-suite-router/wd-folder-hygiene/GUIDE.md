---
name: wd-folder-hygiene
description: Tidy a project/document folder by archiving superseded file versions into an Archive subfolder - keeping the latest of each, never deleting - AND scaffold the firm-standard numbered project-folder structure. Use when the user says clean up this folder, archive old versions, tidy the project folder, move outdated/old docs to an archive, "we have too many versions", declutter, or wants a folder of versioned deliverables (design docs v0.1..v2.0, proposals, IDDs, decks) reduced to just the current files. ALSO use to set up / scaffold a new project or app folder in the standard numbered structure (01_Assessment..08_Commercial, each with an Archive/ subfolder, plus _source/); and it owns the STANDING RULE that creating a new version of a deliverable auto-archives the prior version into that folder's Archive/. Plans first (dry run), confirms, then moves; writes a manifest so every move is reversible.
---

# wd-folder-hygiene - Standard folder structure + archive superseded versions

Two jobs: (1) **scaffold** a new project/app folder in the firm-standard numbered structure, and (2) keep each folder tidy by moving **superseded document versions** into its `Archive/` subfolder. It **never deletes**, never touches a family's latest file, and always shows the plan before moving.

## The standard project/app folder structure (scaffold it every time)

Every new app/product project uses the **same numbered layout** (the "Cadre" / Phys Management standard): `01_Assessment` `02_Market_Research` `03_Design` `04_Prototype` `05_Proposal` `06_Estimate` `07_Demo` `08_Commercial`, **each with its own `Archive/` subfolder**, plus a `_source/` support folder. Scaffold it (idempotent - safe to re-run to fill gaps):

```
python scripts/archive_old_versions.py "<Project Name>" --scaffold          # preview
python scripts/archive_old_versions.py "<Project Name>" --scaffold --apply   # create
```

Full taxonomy, what each phase holds, and `--phases` override: [references/folder-structure-standard.md](references/folder-structure-standard.md).

## Standing rule: new version -> auto-archive the old one

**Whenever a new version of a deliverable is created, the immediately-superseded prior version moves into that folder's `Archive/` as part of the same save.** The full policy - authorization, producing-skills list, deterministic-vs-ambiguous handling - is OWNED by [references/folder-structure-standard.md](references/folder-structure-standard.md) (its "auto-archive" section); bulk or ambiguous cleanups still use the full dry-run -> confirm -> apply contract below.

## The safety contract (non-negotiable)

- **Never delete.** Only *move* into `Archive/`. Every move is logged to `archive_manifest.csv` (timestamp / original path / archived-to path) so it's fully reversible.
- **Keep the latest of every version family, untouched.** Only files that clearly have a **newer sibling in the same family** are archive candidates. A file with no newer version stays put.
- **Plan -> confirm -> apply.** Always run the **dry run first** and show the KEEP / ARCHIVE plan. Only `--apply` after the user confirms. This is a shared-folder action - echo the plan, don't move blind.
- **Be conservative on ambiguity.** Don't archive files the tool can't confidently place in a family. When unsure, leave it and mention it.
- **OneDrive / open-file aware.** Locked or open files can't move - the tool skips them and reports which; the user closes them and re-runs. Office lock files (`~$...`) are ignored.

## Workflow

1. **Point at the folder** (one folder by default; add `--recurse` to process subfolders too - e.g. a parent with a per-app subfolder each holding versions).
2. **Dry run:** `python scripts/archive_old_versions.py "<folder>"` -> prints, per folder, the **KEEP (latest)** files and the **ARCHIVE (superseded)** files, plus a total.
3. **Review with the user.** Confirm the latest-of-each looks right (watch copy-number families - `(12)` vs `(13)` - since a higher copy number isn't guaranteed newer; the user should sanity-check). Adjust scope if needed.
4. **Apply:** `python scripts/archive_old_versions.py "<folder>" --apply` -> moves the superseded files into `<folder>/Archive/` (**the `Archive/` folder is created automatically if it doesn't exist** - no need to make it first; a create failure skips that folder with a clear message rather than crashing), writes the manifest, and reports any skipped (locked) files.
5. **Report** what moved and where; note the manifest path for undo.

## How families & "latest" are decided

Files are grouped into **version families** by base name after stripping a version token; the highest-ranked member is the latest (kept), the rest are archived. Recognized tokens (highest precedence first):

| Token | Example | "Latest" = |
|---|---|---|
| Semver | `_v1.0`, ` v0.9`, `_v2.0.1` | highest major.minor.patch |
| Date | `_20260623`, `_2026-06-23` | most recent date |
| Copy number | `Report (13).docx` | highest number *(sanity-check - may not be chronological)* |
| None (unversioned) | `Design Doc.xlsx` alongside `Design Doc_v2.0.xlsx` | ranks below any versioned sibling -> archived |

Full detection rules, edge cases, and the undo procedure: [references/versioning-and-archive.md](references/versioning-and-archive.md).

## Archiving by name (renames / legacy prefixes)

Version detection is deliberately conservative - it won't cross a **rename** (`OldName_...` -> `NewName_...`) or catch a version marker jammed on without a separator (`OldNameV2`). For those, use **`--match <pattern>`** (case-insensitive substring/regex) to archive **every file whose name matches**, regardless of version, e.g. after an app rename:

```
python scripts/archive_old_versions.py "<folder>" --match "OldName"        # dry run
python scripts/archive_old_versions.py "<folder>" --match "OldName" --apply # move them
```

`--match` unions with the version-family plan and overrides keep-latest for matched files (a rename makes even the newest old-named file legacy). Same safety: dry-run first, manifest for undo, locked files skipped.

## Boundaries

- **Not a delete tool** and **not git** - it archives within the filesystem; it doesn't remove history or touch source control.
- **Doesn't judge content**, only filenames/versions - it won't know a `v1.9` was actually the good one; the dry-run review is where the human catches that.
- File-format mechanics (opening/reading the docs) belong to the xlsx/docx/pptx skills - this skill only moves files.

## Setup

Pure Python 3 stdlib (`pathlib`, `shutil`, `re`, `csv`) - no packages, cross-platform. Runtimes: see `wd-extend-lifecycle/references/prerequisites.md`. If `scripts/archive_old_versions.py` is missing, regenerate it from the verbatim source in [references/scripts.md](references/scripts.md).

## Lifecycle neighbors

Cross-cutting utility - usable in **any phase**, on any project folder, whenever versioned deliverables pile up. It has no fixed upstream or downstream skill; it tidies the folders the delivery skills (**wd-design-doc**, **wd-estimate**, **wd-contracts**, **wd-design-visuals**, and the rest) fill with versioned artifacts, and defers file-format mechanics to the xlsx/docx/pptx skills.

**Global rule pointer:** the user's `~/.claude/CLAUDE.md` rule 10 ("Folder hygiene") states this skill's
intent as a standing preference and defers here for the mechanics. If the numbered taxonomy or the
auto-archive policy changes, update that rule in the same pass so the two do not drift.

**Quality-gate rule (suite-wide):** this skill's outputs are archive moves rather than a design artifact, so the check is the **dry-run plan + manifest** - show the KEEP/ARCHIVE dry run and get confirmation before `--apply`, and report the `archive_manifest.csv` path (every move reversible) with the result.
