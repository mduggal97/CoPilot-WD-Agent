# wdcli - the build/deploy workflow

The Workday Developer CLI (`@workday/wdcli`, oclif-based) drives everything. Installed at `C:\Program Files\Workday\wdcli\bin\` and on PATH. Every command supports `-f json` (machine output) and `--ci` (non-interactive, fail-fast) - always use both when scripting.

**Session pre-flight (do it right the first time):** the whoami / upload-before-deploy / verify-live / re-seed checks below are consolidated into a single start-of-session checklist in wd-extend-lifecycle operational-preflight.md - run it to avoid the wrong-version / wrong-account / stale-copy time-sinks.

## Authentication - owned by wd-auth

`wdcli auth login` / `wdcli tenant login` open a browser for OAuth (an agent cannot run them -
the user runs them in their own terminal). All auth facts - which login to run, the three
token lifetimes, expiry recovery, and multi-org switching - live in **wd-auth**, the single
owner; do not re-derive them here. Start at `wd-auth/references/auth-decision-tree.md` (wdcli =
Mode 1) and `wd-auth/references/auth-troubleshooting.md` (expiry, wrong-org errors).

The pure verify commands (safe anytime; stored token, no browser):

```powershell
wdcli whoami            # identity + active developer org
wdcli tenant list       # available tenants + promotion levels
```

## The build loop

```powershell
wdcli app create "My App" --app-type EXTEND -d "description"   # scaffold (EXTEND | INTEGRATION)
# ... edit local source files ...
python <skills>\wd-extend-dev\scripts\pmd_preflight.py "C:\path\to\app"   # LINT FIRST (see below)
wdcli app upload "C:\path\to\app"                              # upload = BUILD; SOURCEDIRECTORY is POSITIONAL (NOT -d like download)
wdcli app deploy <referenceId> -t <tenant-alias> --latest-version
wdcli tenant open                                               # preview in browser
```

> **Preflight lint is a standing pre-upload step.** `scripts/pmd_preflight.py <app-root>`
> codifies every mechanically-detectable gotcha from pmd-gotchas.md (~25 checks: invalid
> properties, reserved words, id collisions, wrong binding sources, silent-failure widget
> shapes) so they're caught before a build cycle is spent on them - the gotcha list
> documents trips AFTER they happened; the linter prevents the repeat. Exit 1 = FAIL
> findings (fix before upload); WARNs are judgment calls (read each - most are silent
> runtime traps). Verified 2026-09-04: clean on a delivered production app, 23 seeded
> violations all caught. When a NEW mechanically-detectable gotcha lands in
> pmd-gotchas.md, add its check to the linter in the same pass.

> **upload vs. download arg difference:** `app upload` takes SOURCEDIRECTORY as a POSITIONAL
> argument (not a flag). `app download` uses `-d <dir>` as a flag. Mixing them up causes a
> "Nonexistent flag: -d" error on upload, or a silent no-op if the arg is omitted in a
> non-interactive context (see wdcli-setup.md error catalog). Always write the path explicitly:
> `wdcli app upload "C:\path\to\app"` - never `wdcli app upload -d "..."`. (Verified 2026-09-03.)

> **wdcli ERROR CATALOG is owned by [wdcli-setup.md](wdcli-setup.md) section 3** - do not
> re-derive it here. That single table owns every "why did it fail" gotcha: deploy-always-
> prompts-for-`-t`, `app create` fails under Git-Bash, the masked
> `Cannot read properties of undefined (reading 'success')` = non-additive-BO **Error 10**, the
> **instant-fail vs. log-lag / infra-transient two-step read** (plus the config-rejection
> bisect caveat), `app validate` not-authorized -> use `app upload`, the build-log fetch
> commands (`wdcli app builds ... logs`), and the `download` "A version is required" /
> `--overwrite` flags. Consult it before debugging ANY wdcli failure. Below are only the
> mechanics unique to the build CYCLE itself.

Loop-specific mechanics (the cycle, not the errors):

- **`app upload` is the build gate.** A bad PMD/AMD/SMD fails at upload, before any deploy - so upload first and read that result before deploying.
- **`app deploy` deploys the LAST UPLOADED build - it does NOT re-read source files** (verified 2026-08-25: deploy-only cycles showed Success while the page ran old code; the tell is the IDENTICAL build ID across deploys). Every change cycle is `app upload` THEN `app deploy --latest-version -t <tenant>`. If behavior did not change after a "successful" deploy, compare build IDs before debugging the code.
- **A deploy CAN wipe all BO instance data in the dev tenant - treat it as likely, not certain** (corrected 2026-10-10; this line used to say every cycle wipes, and that got repeated to a client as fact).
  - **Observed:** 2026-08-25, one build session - BO data was gone after upload+deploy cycles. Sep 2026, one engagement's dev tenant - 10 of 10 deploys of a new BUILD into the SAME app version (same versionId) kept all BO data.
  - **Hypothesis (unconfirmed - no controlled before/after test yet):** the wipe follows a deploy that creates a new app VERSION, not a new build within the same version.
  - **Safe default:** snapshot BO data (GET-all per collection - tenant-ops.md) before any deploy that creates a new version, and before any deploy when you cannot tell which kind it is. Re-seed test data after such a deploy.
  - **Scope - business-object INSTANCE data only.** What a page shows is not a guide to what is at risk: Extend pages often mix BO rows with rows fetched from an external API through an orchestration, and only the BO rows can be wiped. Find the at-risk data by listing `model/*.businessobject` and reading each collection, not by looking at the UI. Never warn a client their data will be lost without that count.
  - NEVER use "is the data still there?" across a deploy as a persistence test - a possible wipe contaminates it (a real persistence investigation lost time to exactly this). Record each deploy's versionId with a before/after BO count; that is the controlled test that would settle the hypothesis.
- **Scripting-harness caveats** (verified in a delivered build session, 2026-08-05): PowerShell `2>&1 | Out-String` on wdcli output can raise a false NativeCommandError / exit 1 on SUCCESSFUL commands - match the output text ("Build completed") and parse the deploy JSON `success` field explicitly rather than trusting exit codes; a wrapper that printed "deployed" unconditionally masked a real auth failure. From Python, `wdcli` may not resolve via `subprocess` directly - invoke through the shell or by full path.
- `wdcli app preview` gives a local live preview server (rebuilds on save) without deploying - tightens the edit->see loop when available.
- **STANDARD: every new app with a home page ships a home Model Task** (`model/<App>.task`, `routePath: "/"`) - it is the ONLY thing that makes the app appear in the tenant SEARCH bar and launch its home; without it the app is reachable by URL but invisible to users. Add it as part of scaffolding, not an afterthought. Full schema + id-space + securing rules: model.md `.task`. Re-run "Activate Pending Security Policy Changes" after the deploy that first adds it.

## Learning schemas: download, don't guess

`wdcli app download <REF> -d <dir>` (directory is the `-d` flag, NOT positional) pulls a known-good app's source. This is the fastest way to learn any file schema - find a working example with `wdcli app list -f json --ci` + grep, download it, read it. Also the way to pull a co-owned app's latest before editing (workflow.md rule 1).

- **`download` flag errors** ("A version is required" -> add `--latest-version`; "filename conflict" on a populated dir -> add `--overwrite`) are in the [wdcli-setup.md](wdcli-setup.md) section 3 error catalog - not restated here.
- **Ignore `tenantConfiguration/config.dat` in downloads** - it's a compressed tenant-configuration snapshot (`{"schemaVersion": 4, "content": "<zlib+base64 blob>"}`), not hand-editable source. Leave it untouched and exclude it from diffs-of-interest when comparing downloads (verified across delivered production apps, 2026-08-05).
- Full form: `wdcli app download <REF> -d <dir> --latest-version --overwrite --ci`. Uses the stored token (no browser) - works whenever `wdcli whoami` shows the right org active; run `wdcli account switch` first if the wrong org is active.

## Cloning apps

`wdcli app copy <srcRefId> <destDir> -n "Name" --app-type EXTEND|INTEGRATION --ci` clones BOs + pages + flows to a NEW reference ID, rewrites internal refs, leaves the source untouched. New app => security domains must be re-granted in the tenant before BO data works (S22 until then).

- **CLONE CAVEAT - home Model Task does NOT come along if the source lacked it.** Cloning (or porting `model/`) from an app built before the home-`.task` standard inherits the ABSENCE: the new app builds and deploys fine but never shows in tenant search. ALWAYS verify a home `.task` exists after `app copy`/port and add one if missing. (Verified 2026-08-11: an expiry-tracking product, cloned from a pre-standard app, was reachable by URL yet absent from search until a `"/"` .task was added - see model.md `.task`.)
- **CLONE CAVEAT - the copy needs its OWN ISU.** An ISU binds to one Extend app per tenant, so a copy cannot reuse the parent's. Before the first deploy, create a dedicated ISU (same ISSG as the parent's), repoint the copy's `.smd` `siteAuth` ISU username to it, and assign it in App Manager - symptoms and detail in security-setup.md.
- **REBRAND CAVEAT - sweep EVERY page for the old app name, not just home.** When cloning an app to a new product/name, the old name lingers in per-page **footers**, page **titles**, and intro `richText` on all the copied PMDs - fixing `home.pmd` alone leaves the old name on every other page (footers especially). After renaming, grep the whole `presentation/` tree for the old name (`grep -rl "Old Name" presentation/`) and replace across all `.pmd`/`.card`/`.script`; the space-delimited display name (e.g. `"Inventory Expiry"`) is safe to bulk-replace because the no-space code refs (domains `ManageInventoryExpiryPages`, collections `expiryAssignments`) don't match it. (Verified 2026-08-11: an expiry-tracking product shipped with 16 pages still footer-branded "Inventory Expiry".)

## Multi-org work (e.g., a firm dev org + client org)

- `wdcli whoami` shows the active developer org; switch with `wdcli account switch`. `app upload`/`deploy` act under the active org; pass `-a <orgShortId>` on `app create`. `app deploy` also accepts an account flag (`-a` / `--account=<shortId>`) to pin the org per command instead of relying on global state - confirm the exact spelling via `wdcli app deploy --help` (flag names shift between CLI releases).
- **Multi-org pre-flight is owned by wd-auth.** The standing rule (run `wdcli whoami` before any `upload`/`deploy`/`download`/`tenant` call because account state is machine-global and a parallel session can silently flip the active org) lives in `wd-auth/references/auth-preflight.md`. The tell-tale mis-route **"tenant ... was not found or is not a development tenant"** on a tenant that definitely exists = wrong active account, not a bug - full remediation (account switch + per-tenant login) is in `wd-auth/references/auth-troubleshooting.md`.
- Cross-org port mechanics: only the `.amd`/`.smd` carry the reference ID (`applicationId`/`siteId`); PMDs use the portable `<% site.applicationId %>`. Port = copy `model/` + `presentation/`, rename the `.amd`/`.smd` files to the new refId, and replace the old refId string inside those two files only. Keep the destination's `appManifest.json` from its own `app create`.
- Two source trees for the same app do NOT auto-sync - mirror `model/` + `presentation/` deliberately, then upload under each account.
- `app deploy` only targets DEVELOPMENT-level tenants; reaching IMPLEMENTATION tenants requires `wdcli app promote` (see the wd-deployment skill).

## Engagement inputs (pull from project memory; never hardcode)

This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- **Developer org id(s)** - the firm's own dev org and each client org in play. `wdcli whoami` shows the active one; `wdcli account switch` changes it.
- **Dev + IMPL tenant aliases** - discover via `wdcli tenant list`. `app deploy` only targets DEVELOPMENT-level tenants; reaching IMPL tenants needs `app promote` (see wd-deployment).

If a value isn't in memory, ask. For branded output, use neutral formatting (no firm brand skill is installed).

Two commands that consume those values (identical for any engagement):

- Tenanted REST testing: `wdcli tenant token <alias> --ci` prints a ~1-hour bearer token.
- Pre-upload orchestration lint: `python scripts\validate.py` in your Extend workspace (structural checks: JSON validity, node-name uniqueness, BranchOnConditions schema, 32-char hex ids). If it isn't present, regenerate it from the build-spec in [scripts.md](scripts.md). It is a linter, not a compiler - upload is still the real gate.
