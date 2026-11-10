# wdcli - install, verify, sign in, and fix common errors (novice guide)

`wdcli` is the **Workday-provided** Extend developer CLI (oclif-based). It drives every
build/deploy step in this suite. This page is the **first-run setup + troubleshooting**
companion: how to get `wdcli` on your machine, sign in, and unstick the errors that come up.
For what to *do* with it once it works - the create -> upload(build) -> deploy -> preview loop,
schema download, org/tenant switching - read [wdcli-workflow.md](wdcli-workflow.md). For the
Python/PowerShell/Node runtimes the suite's helper scripts need, see
the prerequisites reference in the wd-extend-lifecycle skill.

---

## 1. Install & verify

`wdcli` is not a public npm package you can guess at - it is distributed by Workday to
licensed Extend customers.

1. **Obtain the installer from Workday** - the Extend developer portal / Workday Community
   (search "Workday Developer CLI" / "wdcli"). Extend SKU / Innovation Services must be on the
   customer's contract first (see the prerequisites link above).
   > (!) **Confirm the exact install command in-tenant.** Do not assume an `npm install -g ...`
   > name - install from the Workday-provided package/installer, not an invented registry name.
2. **Known Windows install location:** `C:\Program Files\Workday\wdcli\bin\`. The installer
   normally adds this to your **PATH** so `wdcli` runs from any terminal.
3. **Verify it's on PATH and runnable** (PowerShell):
   ```powershell
   wdcli --version        # prints the installed version - proves install + PATH
   (Get-Command wdcli).Source   # shows which wdcli is being used, if --version fails
   ```
   If `wdcli` is "not recognized," the bin folder isn't on PATH - either open a **new**
   terminal (PATH changes only apply to terminals opened after install) or call it by full
   path once: `& "C:\Program Files\Workday\wdcli\bin\wdcli.cmd" --version`.
4. **First run:** every command supports `-f json` (machine-readable output) and `--ci`
   (non-interactive, fail-fast). Always pass **both** when scripting so a command can't hang
   on a hidden prompt. You are not signed in yet - do that next.

---

## 2. Auth & org / tenant sign-in - owned by wd-auth

Auth is no longer restated here. **wd-auth is the single owner** of the sign-in flow, the
token lifetimes, and account/tenant switching. Read it, don't re-derive it:

- **Which sign-in to run** (wdcli developer + tenant OAuth = **Mode 1**) and how the pieces
  fit: `wd-auth/references/auth-decision-tree.md`.
- **Token expired / "Not logged in" / "tenant ... was not found or is not a development
  tenant"** (which login to re-run, the three separate lifetimes, the wrong-org tell):
  `wd-auth/references/auth-troubleshooting.md`.
- **Pre-flight before the first wdcli command** (`wdcli whoami` active-org check):
  `wd-auth/references/auth-preflight.md`.

The one CLI-layer mechanic to keep in mind: sign-in is **interactive (browser OAuth) and must
be run by the USER** - an agent cannot automate it, so ask the user to run login in their own
terminal. Everything else about auth lives in wd-auth.

---

## 3. Common errors -> fixes

Scannable index of the wdcli gotchas verified across builds. Full context for the build-loop
ones lives in [wdcli-workflow.md](wdcli-workflow.md); promotion behavior lives in the
the promotion-and-environments reference in the wd-deployment skill.

| Symptom / error | Cause | Fix |
|---|---|---|
| `wdcli --version` -> "not recognized" | bin folder not on PATH, or terminal opened before install | Open a **new** terminal; or run by full path `C:\Program Files\Workday\wdcli\bin\wdcli.cmd` |
| `app create` fails: `'C:\Program' is not recognized` | Git-Bash mangles the unquoted install path | Run **`app create` from PowerShell**, not Git-Bash (`upload`/`deploy`/`tenant`/`whoami` work in either) |
| `app deploy` hangs forever on a tenant picker | deploy **always** prompts for a tenant - even with a default set and `--ci` | Pass the tenant explicitly: `wdcli app deploy <refId> -t <tenant-alias> --latest-version` |
| `app deploy` errors that the tenant isn't valid | `deploy` only reaches **DEVELOPMENT**-level tenants | Deploy to the DEV tenant, then `wdcli app promote` to go higher (see wd-deployment) |
| **"tenant ... was not found or is not a development tenant"** on a tenant you KNOW exists | The **wrong dev org is active** - an ACCOUNT problem, not an app or tenant problem | Full remediation (whoami -> account switch -> per-tenant login) is in `wd-auth/references/auth-troubleshooting.md` |
| **"A version is required"** on `app download`, `app deploy`, or `app promote` | bare command with no version selector | Add `--latest-version` (or `--version` / `--version-id`) to the command |
| `app download` errors: filename / version **conflict** | target directory already populated | Add `--overwrite`; full form: `wdcli app download <refId> -d <dir> --latest-version --overwrite --ci` (`-d` is a flag, not positional) |
| `app upload` runs but **no upload happens** and the next deploy ships the OLD build | running `upload` without the SOURCEDIRECTORY positional arg in a non-interactive (agent/CI) context; the CLI prompts for it, gets EOF, and silently skips the upload (verified 2026-09-03, UAP v2) | Always pass the source directory as a positional arg: `wdcli app upload "C:\path\to\app"`. Note: `upload` uses a POSITIONAL arg, NOT `-d` (that flag is for `download`). Also note: `--ci` does NOT suppress the prompt - the explicit positional arg is the only safe form in automated contexts. |
| `app validate` -> **not authorized** on this account | `validate` isn't enabled on all dev orgs (e.g., some client orgs) | Use **`wdcli app upload`** as the real build gate - a bad PMD/AMD/SMD fails at upload |
| Build failed but no reason shown | need the build log | `wdcli app builds <refId> --latest-version -f json --ci` -> then `wdcli app builds logs <buildId> --ci` |
| Auth / permission error on `download`/`upload`/`deploy` | stored token expired - the three lifetimes expire separately | Don't retry blindly - the error text says which login to re-run; the full which-login mapping is in `wd-auth/references/auth-troubleshooting.md` |
| BO data calls return **S22 permission denied** after a fresh deploy | new app's security domains not yet granted in the tenant | Not a wdcli bug - a tenant admin grants the domains (see the wd-deployment per-tenant re-setup matrix) |
| `deploy`/`upload` fails: **`Cannot read properties of undefined (reading 'success')`** | Often a **MASKED "Error 10: duplicate metadata"** - a non-additive BO field change (insert/reorder/remove renumbered existing field IDs), not a CLI glitch | Check the **App Builder UI** for the real cause; make the model additive (append new fields at END - see model.md). **Do NOT delete/recreate the app** - that forfeits the S22 grant + seeded data |
| **Instant** build failure with **no compile output** in the log | Two possibilities, resolved in order: (1) **LOG LAG** - the real errors populate a few seconds after the failure; (2) if the RE-FETCHED log still has no "Orchestration: INFO Build starting" / compile lines at all -> **pure infra transient** (seen twice in a row before clearing on the third identical upload). Verified across build sessions, 2026-08-05 | **Wait ~5s, re-fetch** (`wdcli app builds logs <buildId> --ci`), then read: no compile lines -> just re-upload; compile lines present ("Validation problem: At /nodes/... line/column") -> **real error, fix the code, don't retry** |

> (!) **Caveat on the "instant fail, no compile lines" signature (app audit, 2026-08-07):** a
> real CONFIG rejection can also wear that same-second, no-compile-line signature - a bad
> root-level field shape (e.g. an ill-formed `securityDomains`, see orchestration.md) failed 3x
> identically, yet reverting the one edit built cleanly. So: re-upload the SAME source once or
> twice for flake, but if an identical failure repeats ~3x, **bisect the last edit** (revert it
> and rebuild) before concluding infra - do not retry the same edit indefinitely.

> (!) For any flag above you can't confirm on your `wdcli --version`, run the command with
> `--help` (e.g. `wdcli app download --help`) to confirm the exact flag **in-tenant** rather
> than trusting a remembered spelling - flag names shift between CLI releases.

---

## Security & safety notes

- **Credential handling (never automate login, never paste tokens) is owned by wd-auth** -
  see `wd-auth/references/auth-decision-tree.md` and the credential-store guidance there. The
  CLI-relevant summary: login is browser OAuth an agent cannot run, and the stored token acts
  as you.
- Deploy/promote are consequential (promotion is **one-way** - see wd-deployment). Confirm the
  active org with `wdcli whoami` before any `upload`/`deploy` so you don't act under the wrong
  client's org (the full pre-flight is `wd-auth/references/auth-preflight.md`).
