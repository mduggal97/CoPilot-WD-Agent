---
name: wd-suite-feedback
description: >-
  Capture and route feedback on the shared Workday Claude skill suite - report an issue,
  share a learning, propose an addition or an update to any skill, or ask a question,
  and file it as a GitHub Issue on the suite repo (primary channel) or a structured
  local file (offline fallback) the maintainer can triage. Use when the user says "log a
  skill-suite issue", "report a problem with a skill", "I learned something we should
  add", "suggest a change to <skill>", "skill feedback", "submit suite feedback", or
  when a skill was wrong / missing / hard to use and that should get back to the
  maintainer. Also carries the MAINTAINER mode: harvest everyone's feedback (GitHub
  Issues, or legacy feedback files) into a triage report grouped by target skill so the
  suite can be updated. This closes the shared-suite feedback-and-improvement loop.
---

# wd-suite-feedback - the shared-suite feedback & improvement loop

The suite is shared as a Claude Code plugin marketplace (and a zip). This skill is the built-in
channel for colleagues' feedback to travel back so the suite keeps improving. It has two modes:
**submit** (any user, the default) and **triage** (the maintainer).

**Channel = whatever repo this machine is configured to post to.** No repo is baked into the suite.
Set `WD_SUITE_FEEDBACK_REPO` (or pass `--repo`) to file Issues next to the code, where they are
searchable, labelled and assignable.

**With no repo configured - the current default - records are written to a local file instead.**
Nothing is posted anywhere. That is deliberate: a feedback record must never be published to a
guessed destination. The local records are complete and parseable, so they can be replayed into a
repo later once one is set.

## Golden rule - genericize before you file (read first)

A feedback record is retrieved and reviewed by others, and may live on shared storage. It MUST NOT
contain client-identifying or sensitive data:
- **No client / employer names**, tenant IDs, real worker names, or engagement identifiers - use a
  generic label ("a healthcare client", "the dev tenant").
- **No PHI / PII** (names, IDs, addresses, medical/pay data), **no credentials / tokens / keys**.
- **No pasted screenshots of tenant data.** Describe the screen; don't attach the data.
This mirrors the suite's own standing discipline. If in doubt, abstract it out.

## Submit mode (default - any user)

Goal: turn "the skill got X wrong" or "we should add Y" into one clean, structured file.

1. **Gather six things** (ask the user only for what's missing):
   - **type** - one of: `issue` (something wrong/broken), `learning` (a verified fact/pattern to add),
     `addition` (a new reference/skill idea), `update` (change existing content), `question`.
   - **skill** - the target skill folder name (e.g. `wd-extend-dev`), or `suite` if cross-cutting, or
     `unknown`.
   - **reference** (optional) - the specific reference file if known (e.g. `pmd.md`).
   - **summary** - one line.
   - **detail** - what happened / what you learned, and (for issues) how to reproduce. Pass a
     proposed fix separately via **`--suggested`** - it populates the record's "Suggested change"
     section (folding it into `--detail` leaves that section "(none provided)").
   - **submitter** - the user's name/handle (REQUIRED - a non-interactive run without `--submitter`
     exits with an error). Filing for a colleague without O365 access? Add `--reported-by "<their name>"`.
   - For an `issue`, also a **severity**: `low` / `medium` / `high` (severity is only recorded on
     issues; on other types the script quietly stamps `n/a`).
2. **File it - GitHub Issue is the primary channel.** With `gh` authenticated once per machine
   (`gh auth login`), file straight to the repo (stdlib only - no installs):
   ```bash
   python scripts/file_feedback_issue.py \
     --type issue --skill wd-extend-dev --reference pmd.md --severity medium \
     --submitter "<your-name>" \
     --summary "rowVariableName rejects hyphenated ids" \
     --detail "Building a grid, the id with a hyphen failed validation. Repro: ..." \
     --suggested "Note the JEXL word-operator trap in pmd.md."
   ```
   It opens a labelled Issue (`suite-feedback` + `type:*` + `skill:*`, and `sev:*` for issues; labels
   are auto-created) on the repo named by `--repo` or the `WD_SUITE_FEEDBACK_REPO` env var, and
   prints the issue URL. **With neither set it does not post - it writes the local record.** Use
   `--dry-run` to preview without filing.
   - **No Claude Code / no `gh`?** File the same fields from the web: repo **Issues -> New issue ->
     "Suite feedback"** form (`.github/ISSUE_TEMPLATE/suite-feedback.yml`). The maintainer's triage
     recovers type/skill from the form body.
   - **Offline / `gh` not set up?** `file_feedback_issue.py` auto-falls back to `scripts/log_feedback.py`
     below (writes the same parseable record to a local or SharePoint-synced folder) so nothing is lost.

   **Legacy / offline file path** - `scripts/log_feedback.py` (stdlib only). It stamps the date,
   suite version, and submitter, and writes a parseable Markdown file:
   ```bash
   python scripts/log_feedback.py \
     --type issue --skill wd-extend-dev --reference pmd.md --severity medium \
     --submitter "<your-name>" \
     --summary "rowVariableName rejects hyphenated ids" \
     --detail "Building a grid, the id with a hyphen failed validation. Repro: ... Suggested: note the JEXL word-operator trap." \
     --dest "<optional path to your synced SharePoint feedback subfolder>"
   ```
   Or run it with no content flags for an interactive prompt. If `--dest` is omitted it writes to
   `~/.claude/suite-feedback/<submitter>/` locally. **No-script fallback:** if Python is unavailable,
   copy [references/feedback-template.md](references/feedback-template.md) and fill it by hand - it is
   the same parseable record the script emits.
3. **Tell the user where it landed and how it gets to the maintainer:**
   - The script resolves its destination in priority order: `--dest` > `WD_SUITE_FEEDBACK_DEST` env var
     > a saved default > a local per-submitter folder. It prints which one it used.
   - **Best setup - make it automatic once (the least-typing path):** have the user **sync the
     SharePoint "Shared Skills" library** (SharePoint web -> Sync / Add shortcut to OneDrive), then run
     `python scripts/setup_autosync.py --name "<their-name>"` **once**. The helper auto-detects the
     synced folder, creates their `Feedback/<name>` subfolder, and saves it as the default destination.
     After that, every record writes there and **OneDrive uploads it automatically** - no manual step,
     no credentials. (Manual equivalent: `log_feedback.py --set-dest "<synced folder>"`.) There is no
     direct SharePoint API post; OneDrive sync is the automatic channel.
   - **Not synced?** The file stays local - upload it to the SharePoint `Feedback/<your-name>/`
     subfolder by hand (see the shared `Feedback/README.md`).
   - **No O365/SharePoint access at all?** The record is a self-contained `.md` file - hand it to the
     maintainer (or any colleague with access) by whatever channel you DO have: email, Teams, a shared
     drive. The colleague files it with `--reported-by "<original finder>"` so the attribution travels
     with the record instead of being lost in a chat thread. Never let a finding die because the
     submission channel is blocked - the most locked-down users hit the most constraints and are exactly
     the ones the loop most needs to hear from.
   - The plain `_TEMPLATE.md` in the Feedback folder is the no-skill fallback: copy it, fill it in, drop
     it in your subfolder. Same fields, same result.

## Triage mode (the suite maintainer)

Harvest everyone's feedback and decide what to fold in. **Primary:** `python scripts/triage_issues.py
--out triage_report.md` reads every `suite-feedback` GitHub Issue (grouped by target skill), then apply
via the owning skill + gates and close the issue with what shipped. A legacy SharePoint-file harvest
(`pull_feedback.py`) exists for offline filers. Full maintainer procedure (both channels, the sync/
placeholder gotcha, the report shape, the scrub-flag limits): [references/triage-mode.md](references/triage-mode.md).

## Suite-health mode (the maintainer, systemic issues)

Triage handles individual records. When the problem is SYSTEMIC - the suite "covers a lot but is clunky
to get started", a plain question routes to the wrong skill, content has drifted, or a portable learning
got stranded in personal memory instead of shipping in a skill - use
[references/suite-health-playbook.md](references/suite-health-playbook.md). It covers the first-mile
on-ramp (progressive disclosure), the triggering eval (measure routing objectively + the anti-overfit
rule), the memory-to-skills sweep, single-owner drift control, and how to make suite-wide edits safely.

## Stay-current mode (pull updates - the other half of the loop)

Feedback flows IN; improved skills flow back OUT as new versions. Users should periodically check the
shared SharePoint "Shared Skills" folder for a newer release. This skill helps:

- **Check the installed version vs the latest:**
  ```bash
  python scripts/check_version.py --changelog "<path to a synced Shared Skills/CHANGELOG.md>"
  ```
  It reads the installed `SUITE_VERSION.txt` (dropped into the skills folder by the distribution zip)
  and compares it to the newest `## vX.Y` entry in the shared `CHANGELOG.md`, then reports up-to-date
  or update-available. Read-only - it never downloads or installs anything.
- If behind, tell the user to download the newest `workday-claude-skill-suite_vX.Y.zip` from the shared
  folder and re-install (remove/overwrite old skill folders, unzip, start a fresh session) - see the
  distribution's INSTALL guide, "Staying current".
- Suggest making the check a periodic habit (e.g. monthly), since fixes and additions land as feedback
  is triaged.

## What this skill deliberately does NOT do

- It uses only the user's own **GitHub CLI** (`gh`) to open/list issues - no stored automation
  credentials, no SharePoint API. The offline fallback produces files; their sync/upload is a human step.
- It is not a substitute for the quality gates - a folded-in learning still runs the suite validator.

## Lifecycle neighbors

- Feeds the **suite maintainer**, who applies changes via the owning skill and the wd-extend-lifecycle
  quality gates. Pairs with the shared `INSTALL` guide and `SKILL-CATALOG` in the distribution.
- The submit-side genericize rule is the user-facing echo of the suite's data-governance discipline
  (wd-extend-lifecycle `references/ai-data-governance.md`).

**Quality-gate rule (suite-wide):** the triage report is an artifact - state, when you present it, how
many records it covered and how many were scrub-flagged, so nothing is silently dropped.
