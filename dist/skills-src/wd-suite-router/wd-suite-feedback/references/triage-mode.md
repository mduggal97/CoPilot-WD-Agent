# Triage mode (the suite maintainer)

Goal: harvest everyone's feedback records and decide what to fold into the suite. Maintainer-only; a
regular feedback submitter never needs this file.

## Primary - harvest the GitHub Issues (with `gh` authenticated)

```bash
python scripts/triage_issues.py --out triage_report.md          # all suite-feedback issues
python scripts/triage_issues.py --state open --out open.md      # just the open ones
```

It lists every `suite-feedback` issue (script-filed OR web-form), reads `type:*`/`skill:*`/`sev:*` from
the labels (recovering type/skill from the form body when a label is missing), and writes the report: a
master table plus sections grouped **by target skill** and by type, with open/closed status. Read-only.
Then apply changes via the owning skill + the suite quality gates and **close the issue with a comment on
what shipped** (`gh issue close <n> --comment "..."`) so the loop is auditable. For a fix that is itself a
skill edit, a PR that closes the issue is the cleanest trail.

## Legacy - harvest the SharePoint feedback files (only if colleagues still file the offline way)

0. **Get ALL users' feedback down to your machine first.** In the SharePoint "Shared Skills" library,
   click **Sync** (or *Add shortcut to OneDrive*) - this pulls every user's `Feedback/<name>/` subfolder
   to your OneDrive. Because OneDrive Files On-Demand can leave files as CLOUD-ONLY placeholders a script
   can't read, then right-click the synced **Feedback** folder -> **"Always keep on this device"**. (There
   is no SharePoint API pull; syncing is the channel.)
1. **Harvest + verify + triage in one step** with the maintainer helper - it finds the synced Feedback
   folder, reports how many records each user submitted, FLAGS any file still cloud-only (so you can force
   a full download before triaging), and writes the report:
   ```bash
   python scripts/pull_feedback.py --out triage_report.md
   # or point it explicitly:  --root "<path to the synced Shared Skills or its Feedback folder>"
   ```
   Prefer `--root` if you ALSO keep a local staging copy of "Shared Skills" (the folder you upload from) -
   two local "Shared Skills/Feedback" folders would exist and autodetect could pick the wrong one. Open
   the SYNCED SharePoint Feedback folder in your file manager, copy its path, pass it as `--root`.
   **One-time fix:** `--set-root "<synced path>"` saves it as the default (also honored: the
   `WD_SUITE_FEEDBACK_ROOT` env var), so every later run skips the search entirely. On Windows PowerShell,
   `cd` into `scripts/` first (`~` is not expanded when passed to `python`), and don't run from
   `C:\WINDOWS\System32`.
   (Lower-level: `triage_feedback.py --in "<Feedback folder>" --out triage_report.md` triages a folder
   directly, without the per-user / placeholder checks.)
2. **Read the report.** It parses every record's frontmatter and produces:
   - a master table (date, submitter, type, skill, severity, summary, status);
   - sections grouped **by target skill** (so you can route a batch to one skill at once) and by type;
   - counts, and a **flag list** for records that look unscrubbed. The mechanical detection covers **email
     addresses and long (9+) digit runs only** - it does NOT recognize client names or tenant tokens, so
     the maintainer still eyeballs each record for those before it travels further.
3. **Decide and apply** using the suite's normal discipline: verify-before-promote (don't fold an
   unverified claim as fact - flag it), single-owner-per-concept, run the ASCII + validator gates, and
   record what changed. Then mark handled records (`status: applied` / `declined`) so the loop is auditable.
