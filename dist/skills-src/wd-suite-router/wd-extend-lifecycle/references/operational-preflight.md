# Operational pre-flight and build hygiene - do it right the first time

The recurring time-sinks are not code bugs - they are operational slips: deploying the
WRONG version, being in the WRONG account/org/tenant, editing a STALE copy, testing as the
wrong worker. This checklist gathers the "check before you act" steps that prevent them.
Run the start-of-session block once, and the per-action blocks before each risky step.

Each fact is owned by a home reference (cited); this file is the consolidated procedure.
It is a hard quality gate - the "Build/tenant session pre-flight" row in quality-gates.md.

## 0. Start of any build / tenant session (identity + auth)

- **AUTH preflight FIRST - owned by wd-auth, not restated here.** BEFORE the first wdcli/API/tenant
  action, run the **wd-auth** auth preflight (`wd-auth/references/auth-preflight.md`): who am I / which
  account+ORG is active (`wdcli whoami`), tenant/token auth valid, right auth mode selected. It confirms
  the active account/ORG matches the target app (account state is MACHINE-GLOBAL - a parallel session can
  silently flip it, and the classic "tenant ... was not found or is not a development tenant" on a real
  tenant is a WRONG-ACTIVE-ACCOUNT symptom, not an app bug), and that the three independent expiries
  (tenant login, auth login, ~1-hour REST bearer) are fresh. wd-auth owns the steps and the USER-ACTION
  blocks; this checklist just requires that its preflight passed before the operational items below.
- **Confirm the TENANT is the one you mean, and that it is DEV/SANDBOX - never prod.** For a
  browser session, confirm the URL host AND a read-back (the dual identity check) - the URL you
  think you are on is not proof until a read confirms it; wrong ORG makes custom-org pickers
  silently empty. (wd-tenant-config safety-and-scope.md.)
- **If testing personas: confirm you are PROXIED as the intended worker** (Start Proxy / Sign In
  As). A blank page under the wrong worker or wrong org is a PRECONDITION fault, not a defect;
  `workers/me` returns S21 for implementer/admin accounts. (wd-test-execution browser-mechanics.md.)

## 1. Before EDITING an existing app (code currency)

- **Pull latest, then DIFF.** `wdcli app download <refId> --latest-version --overwrite` and diff
  against your local tree BEFORE editing. Another developer (often the client's) may have changed
  it since you last pulled - clobbering their work costs trust you do not get back. (wd-extend-dev
  workflow.md, wdcli-workflow.md.)
- **Edit against the CURRENT design, not the original.** Re-read the latest signed design-doc
  version and enumerate every file the change touches before writing. (wd-extend-dev workflow.md.)
- **Change-list, not a direct edit, when a client developer owns the code.** (wd-extend-dev.)

## 2. Before DEPLOY (load the RIGHT version)

- **UPLOAD first, every time: `wdcli app upload .` THEN `wdcli app deploy <refId> --latest-version`.**
  `deploy` reuses the LAST UPLOADED build - it does NOT re-read your source files. Deploying
  without uploading pushes stale code that looks like success. The tell: an IDENTICAL build id
  across deploys means you deployed the old build. (wd-extend-dev wdcli-workflow.md.)
- **Model changes are ADDITIVE only** - append new fields at the end; never insert/reorder/remove
  on a deployed BO, or the redeploy fails with "duplicate metadata" (wdcli masks it as a
  `reading 'success'` error). (wd-extend-dev model.md.)
- **Instant build failure = LOG LAG, not always transient.** Real errors populate seconds later -
  wait ~5s, re-fetch `app builds logs`, THEN classify. (wd-extend-dev wdcli-workflow.md.)
- **OWNERSHIP GATE - fail closed before you package** (adapted from an internal firm
  ownership-guard, 2026-08-28). Before building any deploy/promotion bundle for a shared or
  co-owned app, confirm every artifact it ships was last changed by YOU (or your team). Diff the
  fresh `wdcli app download --latest-version` against your local tree (section 1); any file that
  changed and you did not touch is presumed another dev's - it BLOCKS the package unless it is
  byte-identical to the reference pull OR an explicit exception is recorded (who + date +
  additive-only reason) in an ownership-exceptions note kept with the app. If ownership cannot be
  established (no baseline, unreadable pull), BLOCK - never pass on "probably fine."
- **CONTAINERS CARRY PAYLOADS.** A wrapper artifact can look like yours while EMBEDDING someone
  else's work that overwrites it on deploy (a mirrored second-org tree, a re-bundled
  orchestration, any file that includes another artifact's body). Check the embedded/mirrored
  content's ownership, not just the wrapper's - shipping a stale wrapper silently reverts the
  other dev's fix, the worst failure mode because it looks like success.

## 3. After DEPLOY (verify the right version is actually live + reset state)

- **Verify the change is LIVE - do not trust "success" alone.** The tenant can keep serving the
  PRIOR build while the CLI reports success. Confirm by exercising the change (a page shows the
  new behavior, or a REST write uses a new field and is accepted, not S5 "unrecognized field"). A
  DEV tenant serves the latest build immediately. (wd-extend-dev model.md rule 7.)
- **An upload+deploy CAN WIPE dev BO data** (suspected trigger: a new app version). Check the
  seed and re-seed before you test or demo, or every
  data-dependent scenario false-fails and you chase a non-bug. (wd-extend-dev wdcli-workflow.md;
  seed via wd-tenant-config; the deploy-wipes trap is also in data-loading-and-retrieval.md.)
- **New securable items (a new `.task`, new domains) need "Activate Pending Security Policy
  Changes"** after the deploy, or they stay hidden / return S22. (wd-extend-dev model.md.)

## 4. First-time-right discipline (every touched artifact)

- **Run the pmd-gotchas sweep on every touched PMD** - "too small to sweep" is the #1 defect
  source. (wd-extend-dev pmd-gotchas.md.)
- **Run the validator/linter before presenting** anything as done. (wd-extend-dev scripts.md.)
- **In a tenant: plan-first, confirm each write; security/system commits are handed to the user.**
  (wd-tenant-config safety-and-scope.md.)
- **Meet the exemplar bar and report its self-check** with the deliverable. (wd-extend-dev
  standards.md.)

## The one-line habit

Before you act, answer: **who am I / where am I / is my copy current / am I about to load the
right version / will I verify it landed?** Ten seconds of pre-flight beats an hour of chasing a
ghost. When a session DID lose time to one of these, that is a signal to sharpen the check here
(the daily learnings sweep watches for exactly this class of slip).
