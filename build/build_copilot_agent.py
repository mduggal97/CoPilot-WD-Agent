#!/usr/bin/env python3
"""Build the Microsoft 365 Copilot agent package from the installed Claude skill suite.

WHY THIS EXISTS
    A Microsoft 365 Copilot declarative agent accepts at most 8 skills, and each skill's
    SKILL.md must stay under 20,000 characters. The Claude suite has 35 in-scope skills,
    several with a SKILL.md larger than that. So we do not rewrite anything: we MERGE.
    Each of the 8 Copilot skills is a thin "group router" SKILL.md, and every original
    skill rides along untouched inside it as <member>/GUIDE.md plus its references.

    The suite stays the single source of truth. Re-run this script after any suite
    upgrade and the Copilot package is regenerated - never hand-edit dist/.

WHAT IT DOES (in order)
    1. Copies each member skill into dist/skills-src/<group>/<member>/.
    2. Generates the group SKILL.md (routing rules + member list + reference index).
    3. Zips each group with SKILL.md at the zip ROOT (the layout Microsoft documents).
    4. Checks every documented platform limit and runs the sanitize sweep.
    5. Writes dist/BUILD_REPORT.md. Exit code 1 if any hard check fails.

USAGE
    python -I -B build_copilot_agent.py                # build from ~/.claude/skills
    python -I -B build_copilot_agent.py --suite PATH   # build from another copy
    python -I -B build_copilot_agent.py --update-name-hashes
                                                       # maintainer only: refresh name-hashes.json

Standard library only, on purpose: it must run on any teammate's machine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
DIST = PROJECT / "dist"
# Windows refuses paths over 260 characters unless they carry the \\?\ prefix. The
# package nests 4 folders deep, so a project kept in a long folder path hits that limit.
if sys.platform == "win32" and not str(DIST).startswith("\\\\?\\"):
    DIST = Path("\\\\?\\" + str(DIST))

# --- Platform limits (Microsoft Learn, checked 2026-11-10; sources in README) ---------
MAX_SKILLS = 8                 # skills per agent
MAX_SKILL_MD_CHARS = 20_000    # "Skill instructions under 20,000 characters"
MAX_FILES_ALL_SKILLS = 350     # "350 files across all skills"
MAX_DIR_DEPTH = 3              # "Maximum directory depth is 3"
MAX_ZIP_BYTES = 50 * 1024**2   # Agent Builder: 50 MB per zip
MAX_FILE_BYTES = 25 * 1024**2  # Agent Builder: 25 MB per file
MAX_INSTRUCTION_CHARS = 8_000  # agent "instructions" field
MAX_DESCRIPTION_CHARS = 1_000  # agent "description" field
MAX_NAME_CHARS = 100           # agent "name" field
MAX_STARTERS = 12              # conversation starters

# Resource file types the platform accepts inside a skill folder.
ALLOWED_RESOURCE_EXT = {
    ".json", ".xml", ".yaml", ".yml", ".ini", ".config", ".utf8", ".docx", ".doc",
    ".docm", ".pdf", ".txt", ".rtf", ".md", ".ppt", ".pptx", ".ppsm", ".xlsx", ".xls",
    ".xlsm", ".csv", ".tsv", ".html", ".htm", ".png", ".jpg", ".jpeg", ".gif", ".bmp",
    ".log",
}
# Scripts are deliberately NOT shipped in v1. Two reasons, both verified:
#   - 299 markdown files + 74 scripts would break the 350-file cap.
#   - The Copilot sandbox has no network and cannot install packages, and most suite
#     scripts need one or the other (wdcli, Smartsheet, openpyxl). Untested = not shipped.
# TODO(backlog #3): test each script in the sandbox, then ship the ones that run.
SCRIPT_EXT = {".py", ".js", ".mjs", ".cjs", ".ts", ".mts", ".sh", ".bash", ".ps1"}
SKIP_DIRS = {".claude", "__pycache__", ".git"}
SKIP_FILES = {"_ASSETS_REMOVED.md"}

# --- Sanitize sweep --------------------------------------------------------------------
# From the suite README "Distributing these externally" list. A hit is not automatically
# a leak (docs use example.com and placeholder IDs) - every hit is listed for a human to
# clear. BLOCKING patterns fail the build; REVIEW patterns only report.
SWEEP_BLOCKING = {
    "author home path": re.compile(r"[A-Za-z]:\\Users\\(?!<|you\b|USERNAME|username|me\b|name\b)[A-Za-z0-9._-]+", re.I),
    "author OneDrive path": re.compile(r"OneDrive\s*-\s*[A-Z][A-Za-z]+"),
    # "engagement or author name" is added in main() from PRIVATE_NAMES_FILE, when present.
}

# Real client, engagement and author names must never sit in this repo - not even inside a
# regex that hunts for them. So the name check has two halves:
#
#   1. name-hashes.json (COMMITTED) - a one-way fingerprint of each name. Anyone who clones
#      the repo gets the BLOCK: the build fails if a packaged file contains a listed name.
#      The fingerprint cannot be turned back into the name by reading it.
#   2. private-names.local.json (GIT-IGNORED, maintainer only) - the real names:
#        {"names": ["<name>", ...],                       <- source of the fingerprints
#         "blocking_names": "<one regex, case-insensitive>",
#         "redactions": [["<regex>", "<replacement>"], ...]}  <- the auto-REPLACE map
#      A fingerprint can say "a name is here" but not what to replace it with, so
#      auto-replace only runs on a machine that has this file.
#
# HONEST LIMIT: a fingerprint of a short or guessable name can be reversed by trying many
# guesses. It stops reading and searching, not a determined person with repo access.
# Keep the repo private.
PRIVATE_NAMES_FILE = "private-names.local.json"
NAME_HASHES_FILE = "name-hashes.json"
NAME_LABEL = "engagement or author name"
NAME_HASHES = {"salt": "", "hashes": set()}   # filled in main()
_NAME_SEEN: dict[str, bool] = {}              # candidate -> is it a listed name (memo)
_RUN = re.compile(r"[A-Za-z0-9]+")
_CAMEL_PART = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|[0-9]+")


def normalize_name(name: str) -> str:
    """Lower-case and drop everything but letters and digits: 'Acme Health' -> 'acmehealth'."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def name_hash(salt: str, normalized: str) -> str:
    return hashlib.sha256((salt + normalized).encode("utf-8")).hexdigest()


def name_candidates(line: str):
    """Yield (normalized text, text as written) for every spot a name could hide in a line.

    A fingerprint only matches a whole string, so we must guess the name's boundaries:
      - each word                        Acme
      - camel-case pieces of a word      AcmePayroll -> Acme, Payroll, AcmePayroll
      - 2 and 3 neighbouring words       Acme Health, Acme_Health_v2
    Not caught: a name glued inside one all-lower-case word (acmepayroll).
    """
    runs = _RUN.findall(line)
    low = [r.lower() for r in runs]
    for i, run in enumerate(runs):
        yield low[i], run
        parts = _CAMEL_PART.findall(run)
        if 1 < len(parts) <= 8:
            for a in range(len(parts)):
                for b in range(a + 1, len(parts) + 1):
                    if b - a < len(parts):
                        piece = "".join(parts[a:b])
                        yield piece.lower(), piece
        for n in (2, 3):
            if i + n <= len(runs):
                yield "".join(low[i:i + n]), " ".join(runs[i:i + n])


def find_hashed_name(line: str) -> str | None:
    """Return the first listed name found in the line (as written), or None."""
    for cand, shown in name_candidates(line):
        hit = _NAME_SEEN.get(cand)
        if hit is None:
            hit = _NAME_SEEN[cand] = name_hash(NAME_HASHES["salt"], cand) in NAME_HASHES["hashes"]
        if hit:
            return shown
    return None


def mask(text: str) -> str:
    """First letter plus stars. The build report is committed, so it must not print a name."""
    return text[:1] + "*" * (len(text) - 1)


def update_name_hashes() -> int:
    """Maintainer command: rewrite name-hashes.json from the private names list."""
    private_path = HERE / PRIVATE_NAMES_FILE
    if not private_path.is_file():
        print(f"FAIL: build/{PRIVATE_NAMES_FILE} not found. Only the maintainer's machine can refresh the hashes.")
        return 1
    names = sorted({normalize_name(n) for n in json.loads(private_path.read_text(encoding="utf-8")).get("names", [])} - {""})
    if not names:
        print(f'FAIL: build/{PRIVATE_NAMES_FILE} has no "names" list.')
        return 1
    out_path = HERE / NAME_HASHES_FILE
    # Keep the existing salt so an unchanged name keeps its fingerprint (small, readable diffs).
    salt = json.loads(out_path.read_text(encoding="utf-8")).get("salt") if out_path.is_file() else None
    salt = salt or secrets.token_hex(16)
    doc = {
        "_comment": "One-way fingerprints (salted SHA-256) of names the build must block. Generated - do not hand-edit. Refresh with: python -I -B build/build_copilot_agent.py --update-name-hashes",
        "algorithm": "sha256(salt + lower-cased name with only letters and digits)",
        "salt": salt,
        "hashes": sorted(name_hash(salt, n) for n in names),
    }
    out_path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote build/{NAME_HASHES_FILE}: {len(names)} name fingerprints. Commit that file.")
    return 0
SWEEP_REVIEW = {
    # Not a Copilot limit (it was a claude.ai upload rule), so it reports, not blocks.
    "non-ASCII character": re.compile(r"[^\x00-\x7F]"),
    "email address": re.compile(r"[A-Za-z0-9._%+-]+@(?!example\.|contoso\.|client\.|company\.|your|domain\.|acme\.|firm\.)[A-Za-z0-9-]+\.[A-Za-z]{2,}"),
    "long numeric ID (sheet/workspace?)": re.compile(r"(?<![\w.])\d{15,19}(?![\w.])"),
    "tenant URL": re.compile(r"https?://[a-z0-9.-]*myworkday\.com/(?!<|\{|tenant\b|your|TENANT)[A-Za-z0-9_]+", re.I),
    "phone number": re.compile(r"(?<!\d)\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)"),
}


def read_frontmatter_description(skill_md: Path) -> str:
    """Return the `description` from a SKILL.md YAML front matter.

    Hand-rolled (no PyYAML dependency). Handles the two shapes the suite uses:
    a single-line value, and a folded block (`description: >-` plus indented lines).
    """
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    block = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        block.append(line)
    out, grabbing = [], False
    for line in block:
        if grabbing:
            if line.startswith((" ", "\t")) or not line.strip():
                out.append(line.strip())
                continue
            break
        m = re.match(r"description:\s*(.*)$", line)
        if m:
            grabbing = True
            first = m.group(1).strip()
            if first not in (">", ">-", "|", "|-", ">+", "|+"):
                out.append(first.strip("\"'"))
    return " ".join(p for p in out if p).strip()


def first_heading(md: Path) -> str:
    """First markdown H1/H2 in a file - used as the one-line label in the reference index."""
    try:
        for line in md.read_text(encoding="utf-8", errors="replace").splitlines()[:40]:
            if line.startswith("#"):
                return line.lstrip("#").strip()
    except OSError:
        pass
    return ""


def copy_member(src: Path, dst: Path, log: dict) -> list[str]:
    """Copy one suite skill into the group folder. Returns its reference file paths.

    Layout produced (2 folder levels below the group root, inside the depth-3 limit):
        <member>/GUIDE.md              <- the original SKILL.md, renamed so the group
                                          SKILL.md is the only SKILL.md in the package
        <member>/references/<file>     <- unchanged names, so links inside GUIDE.md work
        <member>/assets/<file>         <- any other resource folder, flattened
    Anything nested deeper is flattened with '--' in the name and logged.
    """
    refs = []
    for f in sorted(src.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        if any(part in SKIP_DIRS for part in rel.parts) or f.name in SKIP_FILES:
            log["skipped"].append(f"{src.name}/{rel.as_posix()} (housekeeping file)")
            continue
        ext = f.suffix.lower()
        if ext in SCRIPT_EXT or rel.parts[0] == "scripts":
            log["scripts_excluded"].append(f"{src.name}/{rel.as_posix()}")
            continue
        if ext not in ALLOWED_RESOURCE_EXT:
            log["skipped"].append(f"{src.name}/{rel.as_posix()} (file type not accepted)")
            continue
        if rel.as_posix() == "SKILL.md":
            target = dst / "GUIDE.md"
        else:
            top = rel.parts[0] if len(rel.parts) > 1 else "references"
            folder = "references" if top == "references" else "assets"
            tail = rel.parts[1:] if len(rel.parts) > 1 else rel.parts
            if folder == "assets" and len(rel.parts) > 1 and top != "assets":
                tail = rel.parts  # keep the original folder name in the flattened name
            name = "--".join(tail)
            if len(tail) > 1:
                log["flattened"].append(f"{src.name}/{rel.as_posix()} -> {src.name}/{folder}/{name}")
            target = dst / folder / name
            refs.append(f"{folder}/{name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target)
        genericize(target, f"{src.name}/{rel.as_posix()}", log)
    return refs


# Filled from groups.json in main(). Ordered: longest / most specific pattern first.
REDACTIONS: list[tuple[re.Pattern, str]] = []
TEXT_EXT = {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}


def genericize(target: Path, label: str, log: dict) -> None:
    """Replace engagement-specific names in the PACKAGED copy only.

    The suite's lessons-learned notes cite the engagement they were proven on. That is
    useful provenance for the author and a client-name leak for everyone else, so the
    package carries the lesson and drops the name. The installed suite is never edited
    here - fixing it at the source is a separate, deliberate change.
    """
    if target.suffix.lower() not in TEXT_EXT or not REDACTIONS:
        return
    text = target.read_text(encoding="utf-8", errors="replace")
    total = 0
    for rx, repl in REDACTIONS:
        text, n = rx.subn(repl, text)
        total += n
    if total:
        target.write_text(text, encoding="utf-8", newline="\n")
        log["redactions"].append(f"{label}: {total} replacement{'s' if total != 1 else ''}")


EXCLUDED: list[str] = []   # filled from groups.json "excluded" in main()


def build_group_skill_md(group: dict, groups: list[dict], members: dict) -> str:
    """Generate the group router SKILL.md.

    Kept short on purpose: Copilot loads this whole file when the skill triggers, then
    pulls GUIDE.md / reference files only when the task needs them (progressive
    disclosure). So this file routes; it never restates a member skill's method.
    """
    gname = group["name"]
    out = [
        "---",
        f"name: {gname}",
        f"description: {json.dumps(group['description'])}",
        "---",
        "",
        f"# {group['title']}",
        "",
        "This skill bundles several skills from the Workday Practice Delivery suite.",
        "Each one lives in its own folder with its full method in `GUIDE.md`.",
        "",
        "## How to use this skill",
        "",
        "1. **Pick the one member skill** below that owns the task.",
        "2. **Read that member's `GUIDE.md` first.** It is the full method. Do not answer from the summary here.",
        "3. **Open only the reference files the guide points to.** Paths inside a guide are relative to that member's folder.",
        "4. **Follow the guide's quality check** before presenting work as final, and report the check result with the deliverable.",
        "5. **Never invent Workday facts.** If the guide and its references do not cover it, say so.",
        "",
        "## Reading a guide written for another tool",
        "",
        "The guides were written for Claude Code, which runs on the user's own machine. Translate as you read:",
        "",
        "- **\"SKILL.md\" of a named skill** means that skill's `GUIDE.md`.",
        "- **\"Invoke skill X\" or \"route to X\"** means open X's guide. Find X in the suite map below.",
        "- **`../<skill>/references/<file>`** points at another member's folder, possibly in another skill.",
        "- **`scripts/...` files are not included here.** Describe what the script does and produce the result by hand, or hand the step off.",
        "- **You cannot run `wdcli`, call a live Workday tenant or Smartsheet, drive a browser, or touch local folders.**",
        "  - Do the design, plan, draft, payload or row values here.",
        "  - Then name the boundary plainly and give the exact steps under a heading **\"Finish this on your machine\"**.",
        "  - Never say or imply that a live action ran.",
        "- **Never ask for, accept or repeat a password, token or API key.**",
        "",
        "## Member skills",
        "",
    ]
    for m in group["members"]:
        info = members[m]
        out += [f"### {m}", "", f"**Use for:** {info['description']}", "", f"**Start here:** `{m}/GUIDE.md`", ""]
        if info["refs"]:
            out.append("**Reference files:**")
            out.append("")
            for r in info["refs"]:
                label = info["titles"].get(r, "")
                out.append(f"- `{m}/{r}`" + (f" - {label}" if label else ""))
            out.append("")
    out += ["## Suite map (where every skill lives)", ""]
    for g in groups:
        here = " (this skill)" if g["name"] == gname else ""
        out.append(f"- **{g['name']}**{here}: {', '.join(g['members'])}")
    out += [
        "",
        "Not in this agent: " + ", ".join(f"`{s}`" for s in EXCLUDED) + ". If a guide points to one of these, say that content is not included.",
        "",
    ]
    return "\n".join(out)


def tighten_titles(group, groups, members, limit):
    """If a group SKILL.md is over the limit, drop reference labels (longest list first).

    The file paths always stay - the model needs them. Only the human-friendly labels go.
    """
    text = build_group_skill_md(group, groups, members)
    order = sorted(group["members"], key=lambda m: -len(members[m]["refs"]))
    trimmed = []
    for m in order:
        if len(text) < limit:
            break
        members[m]["titles"] = {}
        trimmed.append(m)
        text = build_group_skill_md(group, groups, members)
    return text, trimmed


def sweep(root: Path):
    blocking, review = [], []
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in {".md", ".txt", ".json", ".yaml", ".yml", ".csv"}:
            continue
        rel = f.relative_to(root).as_posix()
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            name_hit = False
            for label, rx in SWEEP_BLOCKING.items():
                m = rx.search(line)
                if m:
                    is_name = label == NAME_LABEL
                    name_hit = name_hit or is_name
                    blocking.append((label, rel, n, mask(m.group(0)) if is_name else m.group(0)[:60]))
            if NAME_HASHES["hashes"] and not name_hit:
                found = find_hashed_name(line)
                if found:
                    blocking.append((NAME_LABEL, rel, n, mask(found)))
            for label, rx in SWEEP_REVIEW.items():
                m = rx.search(line)
                if m:
                    review.append((label, rel, n, m.group(0)[:60]))
    return blocking, review


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--suite", default=str(Path.home() / ".claude" / "skills"), help="folder holding the suite's skill folders")
    ap.add_argument("--update-name-hashes", action="store_true", help="maintainer only: rewrite name-hashes.json from the private names list, then exit")
    args = ap.parse_args()
    if args.update_name_hashes:
        return update_name_hashes()
    suite = Path(args.suite)
    cfg = json.loads((HERE / "groups.json").read_text(encoding="utf-8"))
    groups = cfg["groups"]
    EXCLUDED[:] = cfg["excluded"]

    checks: list[tuple[str, bool, str]] = []  # (name, passed, detail)
    log = {"skipped": [], "scripts_excluded": [], "flattened": [], "redactions": []}
    # Private names first (most specific), then the generic patterns kept in groups.json.
    private_path = HERE / PRIVATE_NAMES_FILE
    private = json.loads(private_path.read_text(encoding="utf-8")) if private_path.is_file() else {}
    names_loaded = bool(private.get("blocking_names"))
    if names_loaded:
        SWEEP_BLOCKING[NAME_LABEL] = re.compile(private["blocking_names"], re.I)
    # Committed fingerprints: the name BLOCK that works on every machine.
    hash_path = HERE / NAME_HASHES_FILE
    hash_doc = json.loads(hash_path.read_text(encoding="utf-8")) if hash_path.is_file() else {}
    NAME_HASHES["salt"] = hash_doc.get("salt", "")
    NAME_HASHES["hashes"] = set(hash_doc.get("hashes", []))
    hashes_loaded = bool(NAME_HASHES["salt"] and NAME_HASHES["hashes"])
    checks.append(("Name fingerprint file present", hashes_loaded,
                   f"{len(NAME_HASHES['hashes'])} fingerprints in build/{NAME_HASHES_FILE}" if hashes_loaded else f"build/{NAME_HASHES_FILE} missing or empty"))
    # Drift guard: a name added to the private list but never fingerprinted would be
    # blocked on the maintainer's machine and silently allowed on everyone else's.
    private_names = {normalize_name(n) for n in private.get("names", [])} - {""}
    if private_names:
        want = {name_hash(NAME_HASHES["salt"], n) for n in private_names}
        in_sync = want == NAME_HASHES["hashes"]
        checks.append(("Name fingerprints match the private name list", in_sync,
                       "in sync" if in_sync else "out of sync - run --update-name-hashes and commit the file"))
    else:
        checks.append(("Name fingerprints match the private name list", True, "not checked here - the private list is not on this machine"))
    REDACTIONS[:] = [(re.compile(pat), repl) for pat, repl in private.get("redactions", []) + cfg.get("redactions", [])]

    src_root = DIST / "skills-src"
    zip_root = DIST / "skills"
    for d in (src_root, zip_root):
        # A cloud-synced folder (OneDrive) can hold a lock on an EMPTY folder for minutes.
        # Every file is still removed; a locked empty folder is harmless and gets reused.
        # The "stale file" check after the build proves nothing old survived.
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)
    stale = [p for d in (src_root, zip_root) for p in d.rglob("*") if p.is_file()]
    if stale:
        print(f"FAIL: could not clear {len(stale)} old file(s) from dist/, e.g. {stale[0]}. Close anything that has them open and re-run.")
        return 1

    # 1. Copy members -----------------------------------------------------------------
    members: dict[str, dict] = {}
    missing = []
    for g in groups:
        for m in g["members"]:
            src = suite / m
            if not (src / "SKILL.md").is_file():
                missing.append(m)
                continue
            dst = src_root / g["name"] / m
            refs = copy_member(src, dst, log)
            members[m] = {
                "description": read_frontmatter_description(src / "SKILL.md"),
                "refs": refs,
                "titles": {r: first_heading(dst / r) for r in refs if r.endswith(".md")},
            }
    checks.append(("Every listed member skill found in the suite", not missing, ", ".join(missing) or f"{len(members)} skills"))
    if missing:
        print("Missing skills:", missing)
        return 1
    no_desc = [m for m, i in members.items() if not i["description"]]
    checks.append(("Every member has a description", not no_desc, ", ".join(no_desc) or "all present"))

    # Scope guard: excluded skills must never slip in; nothing in scope may be forgotten.
    all_members = [m for g in groups for m in g["members"]]
    leaked = sorted(set(all_members) & set(cfg["excluded"]))
    checks.append(("No excluded skill packaged", not leaked, ", ".join(leaked) or "none"))
    dupes = sorted({m for m in all_members if all_members.count(m) > 1})
    checks.append(("No skill packaged twice", not dupes, ", ".join(dupes) or "none"))
    expected = set(cfg["suite_roster"]) - set(cfg["excluded"])
    forgot = sorted(expected - set(all_members))
    checks.append(("Every in-scope suite skill is packaged", not forgot, ", ".join(forgot) or f"{len(expected)} of {len(expected)}"))

    # 2. Group SKILL.md ----------------------------------------------------------------
    sizes = {}
    for g in groups:
        text, trimmed = tighten_titles(g, groups, members, MAX_SKILL_MD_CHARS - 500)
        (src_root / g["name"] / "SKILL.md").write_text(text, encoding="utf-8", newline="\n")
        sizes[g["name"]] = len(text)
        if trimmed:
            log["flattened"].append(f"{g['name']}/SKILL.md: reference labels dropped for {', '.join(trimmed)} to fit the size limit")
    over = {k: v for k, v in sizes.items() if v >= MAX_SKILL_MD_CHARS}
    checks.append((f"Each SKILL.md under {MAX_SKILL_MD_CHARS:,} characters", not over,
                   "; ".join(f"{k}={v:,}" for k, v in sizes.items())))
    checks.append((f"At most {MAX_SKILLS} skills", len(groups) <= MAX_SKILLS, f"{len(groups)} skills"))

    # 3. Zip (SKILL.md at the zip root) -------------------------------------------------
    zip_info, total_files, deepest, bigfile = {}, 0, 0, []
    for g in groups:
        gdir = src_root / g["name"]
        zpath = zip_root / f"{g['name']}.zip"
        files = sorted(p for p in gdir.rglob("*") if p.is_file())
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for p in files:
                rel = p.relative_to(gdir)
                deepest = max(deepest, len(rel.parts) - 1)
                if p.stat().st_size > MAX_FILE_BYTES:
                    bigfile.append(rel.as_posix())
                z.write(p, rel.as_posix())
        with zipfile.ZipFile(zpath) as z:
            ok_root = "SKILL.md" in z.namelist()
        zip_info[g["name"]] = (len(files), zpath.stat().st_size, ok_root)
        total_files += len(files)
    checks.append((f"At most {MAX_FILES_ALL_SKILLS} files across all skills", total_files <= MAX_FILES_ALL_SKILLS, f"{total_files} files"))
    checks.append((f"Folder depth at most {MAX_DIR_DEPTH}", deepest <= MAX_DIR_DEPTH, f"deepest file sits {deepest} folders below the skill root"))
    checks.append(("Each zip under 50 MB", all(v[1] <= MAX_ZIP_BYTES for v in zip_info.values()),
                   f"largest {max(v[1] for v in zip_info.values()) / 1024:,.0f} KB"))
    checks.append(("No file over 25 MB", not bigfile, ", ".join(bigfile) or "none"))
    checks.append(("SKILL.md at the root of every zip", all(v[2] for v in zip_info.values()), "all 8" if all(v[2] for v in zip_info.values()) else "see zips"))
    shipped_scripts = [p for p in src_root.rglob("*") if p.suffix.lower() in SCRIPT_EXT]
    checks.append(("No script files shipped (v1 decision)", not shipped_scripts, f"{len(log['scripts_excluded'])} scripts held back"))

    # Every reference path promised in a SKILL.md must exist on disk.
    broken = []
    for g in groups:
        text = (src_root / g["name"] / "SKILL.md").read_text(encoding="utf-8")
        for path in re.findall(r"`([a-z0-9-]+/(?:GUIDE\.md|references/[^`]+|assets/[^`]+))`", text):
            if not (src_root / g["name"] / path).is_file():
                broken.append(f"{g['name']}: {path}")
    checks.append(("Every file path listed in a SKILL.md exists", not broken, "; ".join(broken[:5]) or "all resolve"))

    # 4. Agent profile ------------------------------------------------------------------
    # Authored in build/agent/ (the source); copied to dist/ so dist is fully generated.
    instr = (DIST / "agent-instructions.txt")
    profile = (DIST / "agent-profile.json")
    for out_file in (instr, profile):
        src_file = HERE / "agent" / out_file.name
        if src_file.is_file():
            shutil.copyfile(src_file, out_file)
    if instr.is_file():
        n = len(instr.read_text(encoding="utf-8"))
        checks.append((f"Agent instructions at most {MAX_INSTRUCTION_CHARS:,} characters", n <= MAX_INSTRUCTION_CHARS, f"{n:,} characters"))
        itext = instr.read_text(encoding="utf-8")
        unnamed = [g["name"] for g in groups if g["name"] not in itext]
        checks.append(("Instructions name all 8 skills", not unnamed, ", ".join(unnamed) or "all named"))
    else:
        checks.append(("Agent instructions file present", False, "dist/agent-instructions.txt missing"))
    if profile.is_file():
        p = json.loads(profile.read_text(encoding="utf-8"))
        checks.append((f"Agent name at most {MAX_NAME_CHARS} characters", len(p["name"]) <= MAX_NAME_CHARS, f"{len(p['name'])}"))
        checks.append((f"Agent description at most {MAX_DESCRIPTION_CHARS:,} characters", len(p["description"]) <= MAX_DESCRIPTION_CHARS, f"{len(p['description'])}"))
        checks.append((f"At most {MAX_STARTERS} conversation starters", len(p["conversation_starters"]) <= MAX_STARTERS, f"{len(p['conversation_starters'])}"))
    else:
        checks.append(("Agent profile file present", False, "dist/agent-profile.json missing"))

    # 5. Sanitize sweep -----------------------------------------------------------------
    blocking, review = sweep(src_root)
    for extra in (instr, profile):
        if extra.is_file() and SWEEP_REVIEW["non-ASCII character"].search(extra.read_text(encoding="utf-8")):
            review.append(("non-ASCII character", extra.name, 0, ""))
    if names_loaded and hashes_loaded:
        sweep_scope = "author paths; names by private list and by fingerprint"
    elif hashes_loaded:
        sweep_scope = "author paths; names by fingerprint"
    elif names_loaded:
        sweep_scope = "author paths; names by private list only"
    else:
        sweep_scope = "author paths ONLY - name sweep OFF"
    checks.append((f"Sanitize sweep: no blocking hits ({sweep_scope})", not blocking, f"{len(blocking)} hits"))

    # 6. Report -------------------------------------------------------------------------
    failed = [c for c in checks if not c[1]]
    r = ["# Build report", "",
         f"**Result: {'PASS' if not failed else 'FAIL'}** - {len(checks) - len(failed)} of {len(checks)} checks passed.", "",
         f"Source suite: `{cfg['suite_version']}`. Limits checked against Microsoft Learn, 2026-11-10.", "",
         "## Checks", ""]
    for name, ok, detail in checks:
        r.append(f"- **{'PASS' if ok else 'FAIL'}** - {name}")
        r.append(f"  - {detail}")
    r += ["", "## The 8 skill packages", ""]
    for g in groups:
        n, size, _ = zip_info[g["name"]]
        r.append(f"- **{g['name']}.zip** - {len(g['members'])} member skill{'s' if len(g['members']) != 1 else ''}, {n} files, {size / 1024:,.0f} KB, SKILL.md {sizes[g['name']]:,} characters")
    if not names_loaded and not hashes_loaded:
        r += ["", "## WARNING - name sweep did not run", "",
              f"Neither `build/{NAME_HASHES_FILE}` nor `build/{PRIVATE_NAMES_FILE}` was found, so this build did not check for client, engagement or author names.",
              "Do not share this package until that is fixed."]
    elif not names_loaded:
        r += ["", "## Note - names were checked by fingerprint", "",
              "This machine does not have the private name list. That is normal for anyone but the maintainer.",
              "- **Blocking still works.** A listed name in the package fails this build.",
              "- **Auto-replace is off.** If the build fails on a name, fix the wording in the suite, or ask the maintainer to rebuild."]
    r += ["", "## Sanitize sweep - blocking hits", ""]
    r += [f"- {l}: `{f}` line {n}: `{s}`" for l, f, n, s in blocking] or ["- None."]
    r += ["", f"## Sanitize sweep - hits to review by eye ({len(review)})", "",
          "A hit here is a pattern match, not a confirmed leak. Each one needs a human look before sharing outside the team.", ""]
    r += [f"- {l}: `{f}` line {n}: `{s}`" for l, f, n, s in review] or ["- None."]
    r += ["", f"## Held back: scripts ({len(log['scripts_excluded'])})", "",
          "Not shipped in v1. See the README backlog, item 3.", ""]
    r += [f"- {s}" for s in log["scripts_excluded"]]
    r += ["", "## Skipped files", ""] + ([f"- {s}" for s in log["skipped"]] or ["- None."])
    r += ["", f"## Engagement names genericized in the package ({len(log['redactions'])} files)", "",
          "Any file listed here still carries an engagement name in the installed suite. Only the packaged copy was changed. Zero files means the suite is clean.", ""]
    r += [f"- {s}" for s in log["redactions"]] or ["- None."]
    r += ["", "## Renamed or flattened", "", "- Every member's `SKILL.md` is packaged as `GUIDE.md`."]
    r += [f"- {s}" for s in log["flattened"]]
    (DIST / "BUILD_REPORT.md").write_text("\n".join(r) + "\n", encoding="utf-8", newline="\n")

    for name, ok, detail in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}  [{detail}]")
    print(f"\n{'PASS' if not failed else 'FAIL'}: {len(checks) - len(failed)}/{len(checks)} checks. Review hits: {len(review)}. Report: dist/BUILD_REPORT.md")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
