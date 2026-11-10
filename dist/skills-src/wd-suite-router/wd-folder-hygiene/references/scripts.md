# Scripts this skill uses - bundled, with verbatim regeneration source

This skill bundles ONE script: **`scripts/archive_old_versions.py`** - it does two jobs: the
version-family **archiver** (plan -> confirm -> apply -> manifest) and the standard-structure
**scaffolder** (`--scaffold`). It normally ships inside the skill. If it is ever missing (a partial
copy, a share package that stripped it), Claude regenerates it by writing the verbatim source below
back to `wd-folder-hygiene/scripts/archive_old_versions.py`.

Because the script is small and fully self-contained, the **canonical regeneration source is the
script itself** (below), not a paraphrased method spec - copy it byte-for-byte rather than
re-deriving the version-token logic.

- **Language / runtime:** Python 3, standard library only (`sys, re, os, csv, shutil, datetime, pathlib`).
- **Third-party deps:** none. Cross-platform (Windows / Mac / Linux). Runtimes: `wd-extend-lifecycle/references/prerequisites.md`.
- **Usage:**
  ```
  python scripts/archive_old_versions.py "<folder>"                 # archive dry run (KEEP/ARCHIVE plan)
  python scripts/archive_old_versions.py "<folder>" --apply         # move superseded -> Archive/
  python scripts/archive_old_versions.py "<folder>" --recurse       # also process subfolders
  python scripts/archive_old_versions.py "<folder>" --archive-name "_Archive"
  python scripts/archive_old_versions.py "<folder>" --match "OldName" [--apply]   # archive by name (renames/legacy)
  python scripts/archive_old_versions.py "<folder>" --scaffold [--apply]          # create the STANDARD numbered structure
  python scripts/archive_old_versions.py "<folder>" --scaffold --phases "01_A,02_B" --apply   # custom phase set
  ```
- **Key behaviors to preserve:** default is a DRY RUN (never moves/creates without `--apply`); never
  deletes; keeps the latest of each version family in place; writes an appendable
  `archive_manifest.csv` (timestamp / original / archived-to) for reversibility; skips Office lock
  files (`~$...`) and locked/open files (reports them). Version-token precedence is
  **semver > date > copy-number > unversioned** (see the `version_key` sortkey tuples). `--scaffold`
  creates the standard `01_Assessment..08_Commercial` folders (each with an `Archive/`) plus
  `_source/`, is idempotent (existing folders reported EXISTS), and can create the top folder itself.
- **Gotchas:** copy-number families (`(12)` vs `(13)`) are NOT guaranteed chronological - the dry-run
  review is where the human sanity-checks. `--match` unions with the version plan and overrides
  keep-latest for matched files (a rename makes even the newest old-named file legacy). Detection is
  filename-only; it won't know a `v1.9` was the good one - that's the human's call at dry-run.
- **Regeneration confidence:** **Exact** - the source is embedded verbatim below; copy it as-is.

Cross-reference: [versioning-and-archive.md](versioning-and-archive.md) (detection rules, edge cases,
undo procedure), [folder-structure-standard.md](folder-structure-standard.md) (the standard numbered
layout + the auto-archive-on-new-version rule), and `SKILL.md` (the safety contract + workflow).

---

### If this script is missing, write this file

Write the following verbatim to `wd-folder-hygiene/scripts/archive_old_versions.py`:

```python
# -*- coding: utf-8 -*-
"""Archive superseded document versions AND scaffold the standard project-folder structure.

Two jobs, one tool:

1. ARCHIVE (default): groups files into VERSION FAMILIES (same base name, differing
   version token - `_v1.0`/`_v1.1`, a trailing `_YYYYMMDD` date, or a ` (2)` copy suffix),
   keeps the LATEST in each family in place, and moves the older ones into an `Archive/`
   subfolder. The `Archive/` folder is CREATED AUTOMATICALLY if it doesn't already exist. It
   NEVER deletes anything and never touches a family's latest file.

2. SCAFFOLD (--scaffold): creates the STANDARD numbered project/app folder structure
   (01_Assessment .. 08_Commercial by default), each phase folder with its own Archive/
   subfolder, plus a _source/ support folder. Idempotent - existing folders are reported and
   left untouched.

Default is a DRY RUN (prints the plan only). Pass --apply to actually move / create.
Cross-platform (pathlib + shutil). Archiving writes an archive_manifest.csv for reversibility.

Usage:
  python archive_old_versions.py "<folder>"                     # archive dry run (plan)
  python archive_old_versions.py "<folder>" --apply             # move older versions -> Archive/
  python archive_old_versions.py "<folder>" --recurse           # also process subfolders
  python archive_old_versions.py "<folder>" --match "OldName"   # archive by name (rename/legacy)
  python archive_old_versions.py "<folder>" --archive-name "_Archive"
  python archive_old_versions.py "<folder>" --scaffold          # preview standard structure
  python archive_old_versions.py "<folder>" --scaffold --apply  # create standard structure
  python archive_old_versions.py "<folder>" --scaffold --phases "01_Discovery,02_Design" --apply
"""
import sys, re, os, csv, shutil, datetime
from pathlib import Path

SEMVER = re.compile(r'[ _\-]v(\d+)(?:\.(\d+))?(?:\.(\d+))?', re.I)   # _v1.2 / v0.1
DATE8  = re.compile(r'[ _\-](\d{8})(?=\D|$)')                        # _20260623
DATEISO= re.compile(r'[ _\-](\d{4}-\d{2}-\d{2})')                    # _2026-06-23
COPYN  = re.compile(r' \((\d+)\)$')                                  # " (2)"
SKIP_PREFIX = ("~$",)        # Office lock files
SKIP_NAMES = {"archive_manifest.csv"}

# The STANDARD numbered project/app folder structure (the "Cadre" / Phys Management layout).
# Every numbered phase folder gets its own Archive/ subfolder; _source/ holds working/build source.
# This is the firm standard for a new app/product project folder - scaffold it EVERY time.
STANDARD_PHASES = [
    "01_Assessment", "02_Market_Research", "03_Design", "04_Prototype",
    "05_Proposal", "06_Estimate", "07_Demo", "08_Commercial",
]
STANDARD_SUPPORT = ["_source"]

def version_key(stem):
    """Return (base, sortkey) for a filename stem (no extension).
    sortkey ranks families: semver > date > copy-number > none; higher = newer."""
    m = list(SEMVER.finditer(stem))
    if m:
        last = m[-1]
        base = (stem[:last.start()] + stem[last.end():]).strip(" _-")
        maj, mnr, pat = (int(x) if x else 0 for x in last.groups())
        return _norm(base), (3, maj, mnr, pat)
    for rx, kind in ((DATE8, 'd8'), (DATEISO, 'iso')):
        m = list(rx.finditer(stem))
        if m:
            last = m[-1]; base = (stem[:last.start()] + stem[last.end():]).strip(" _-")
            d = last.group(1).replace("-", "")
            return _norm(base), (2, int(d))
    m = COPYN.search(stem)
    if m:
        base = stem[:m.start()].strip()
        return _norm(base), (1, int(m.group(1)))
    return _norm(stem), (0,)

def _norm(s):
    return re.sub(r'[ _\-]+', ' ', s).strip().lower()

def scan_folder(folder, archive_name):
    families = {}   # (base, ext) -> list of (path, sortkey, mtime)
    for p in sorted(folder.iterdir()):
        if p.is_dir() or p.name.lower() == archive_name.lower():
            continue
        if p.name.startswith(SKIP_PREFIX) or p.name.lower() in SKIP_NAMES:
            continue
        base, key = version_key(p.stem)
        ext = p.suffix.lower()
        try: mtime = p.stat().st_mtime
        except OSError: mtime = 0
        families.setdefault((base, ext), []).append((p, key, mtime))
    return families

def plan(folder, archive_name):
    fams = scan_folder(folder, archive_name)
    keep, archive = [], []
    for (base, ext), members in sorted(fams.items()):
        if len(members) < 2:
            keep.append(members[0][0]); continue
        # latest = max by (sortkey, mtime); everything else is superseded
        members_sorted = sorted(members, key=lambda t: (t[1], t[2]))
        latest = members_sorted[-1][0]
        keep.append(latest)
        for p, _, _ in members_sorted[:-1]:
            archive.append((p, latest))
    return keep, archive

def scaffold(folder, phases, support, archive_name, apply):
    """Create the STANDARD numbered folder structure, each phase with an Archive/ subfolder.
    Idempotent: existing folders are reported as EXISTS and left untouched. The top folder
    itself is created too when missing (so this can stand up a brand-new project folder)."""
    steps = [(folder, "exists" if folder.is_dir() else "create")]
    for name in phases:
        d = folder / name
        steps.append((d, "exists" if d.is_dir() else "create"))
        a = d / archive_name
        steps.append((a, "exists" if a.is_dir() else "create"))
    for name in support:
        d = folder / name
        steps.append((d, "exists" if d.is_dir() else "create"))
    print("\n=== Scaffold standard structure under: %s" % folder)
    for d, action in steps:
        try: label = d.relative_to(folder.parent)
        except ValueError: label = d
        print("  %-6s %s" % (action.upper(), label))
    to_make = [d for d, action in steps if action == "create"]
    print("\n%d folder(s) to create, %d already present." % (len(to_make), len(steps) - len(to_make)))
    if not apply:
        print("DRY RUN - nothing created. Re-run with --apply to create them.")
        return 0
    made = 0
    for d in to_make:
        try:
            d.mkdir(parents=True, exist_ok=True); made += 1
        except (OSError, PermissionError) as e:
            print("  !! could not create %s (%s)" % (d, str(e)[:60]))
    print("\nCreated %d folder(s)." % made)
    return 0

def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 2
    folder = Path(argv[0])
    apply = "--apply" in argv
    recurse = "--recurse" in argv
    scaffold_mode = "--scaffold" in argv
    archive_name = "Archive"
    if "--archive-name" in argv:
        archive_name = argv[argv.index("--archive-name") + 1]
    phases = STANDARD_PHASES
    if "--phases" in argv:
        phases = [p.strip() for p in argv[argv.index("--phases") + 1].split(",") if p.strip()]
    match = None
    if "--match" in argv:
        match = argv[argv.index("--match") + 1]   # name substring / regex, case-insensitive

    # SCAFFOLD mode: create the standard structure (top folder may not exist yet) and return.
    if scaffold_mode:
        return scaffold(folder, phases, STANDARD_SUPPORT, archive_name, apply)

    if not folder.is_dir():
        print("Not a folder:", folder); return 2

    folders = [folder]
    if recurse:
        folders += [d for d in folder.rglob("*") if d.is_dir() and d.name.lower() != archive_name.lower()]

    grand_archive = []
    for f in folders:
        keep, archive = plan(f, archive_name)
        # --match: also archive files whose NAME matches (rename/legacy cleanup), regardless of version
        if match:
            already = {p for p, _ in archive}
            for p in sorted(f.iterdir()):
                if p.is_dir() or p in already:
                    continue
                if p.name.startswith(SKIP_PREFIX) or p.name.lower() in SKIP_NAMES:
                    continue
                if p.name.lower() == archive_name.lower():
                    continue
                if re.search(match, p.name, re.I):
                    archive.append((p, None))   # None = matched by name, not superseded
        if not archive:
            continue
        print("\n=== %s" % f)
        latests = sorted({lat.name for _, lat in archive if lat is not None})
        if latests:
            print("  KEEP (latest of each version family):")
            for nm in latests:
                print("    * %s" % nm)
        print("  ARCHIVE -> %s/:" % archive_name)
        for p, lat in archive:
            print("    - %s%s" % (p.name, "" if lat is not None else "   [name match]"))
        grand_archive += [(f, p, lat) for p, lat in archive]

    print("\n%d file(s) would move to '%s/'." % (len(grand_archive), archive_name))
    if not apply:
        print("DRY RUN - nothing moved. Re-run with --apply to move them.")
        return 0

    # apply: move each into <its folder>/Archive/, log a manifest, skip locked files.
    # The Archive/ folder is created ON DEMAND (including the first run when it doesn't exist yet);
    # creation is per-folder, cached, and error-handled so a create failure skips that folder's
    # files with a clear message instead of crashing the whole run.
    moved, locked = [], []
    archive_dirs = {}   # folder -> Path(Archive) once created, or False if creation failed
    for f, p, lat in grand_archive:
        adir = archive_dirs.get(f)
        if adir is None:
            candidate = f / archive_name
            try:
                candidate.mkdir(parents=True, exist_ok=True)   # create Archive/ if absent
                if not candidate.is_dir():                      # e.g. a FILE named "Archive" is in the way
                    raise NotADirectoryError("'%s' exists but is not a folder" % archive_name)
                adir = archive_dirs[f] = candidate
            except (OSError, PermissionError, NotADirectoryError) as e:
                adir = archive_dirs[f] = False
                print("  !! could not create %s/ in %s (%s) - skipping this folder" % (archive_name, f, str(e)[:60]))
        if adir is False:
            locked.append((p, "no %s/ folder (create failed)" % archive_name))
            continue
        dest = adir / p.name
        n = 1
        while dest.exists():
            dest = adir / ("%s (%d)%s" % (p.stem, n, p.suffix)); n += 1
        try:
            shutil.move(str(p), str(dest))
            moved.append((p, dest))
        except (OSError, PermissionError) as e:
            locked.append((p, str(e)[:60]))
    # manifest (append) per top folder
    man = folder / "archive_manifest.csv"
    new = not man.exists()
    with open(man, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["timestamp", "original", "archived_to"])
        ts = datetime.datetime.now().isoformat(timespec="seconds")
        for src, dst in moved:
            w.writerow([ts, str(src), str(dst)])
    print("\nMoved %d file(s). Manifest: %s" % (len(moved), man))
    if locked:
        print("SKIPPED %d locked/open file(s) (close them and re-run):" % len(locked))
        for p, e in locked:
            print("  -", p.name, "::", e)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```
