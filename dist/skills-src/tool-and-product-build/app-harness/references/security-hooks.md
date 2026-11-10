# Security and Guard Hooks (Reusable Templates)

Reference for `app-harness`. Three guard hooks for a Claude Code build loop,
presented as **reusable templates you adapt** - a secrets/client-data bash guard,
a branch guard, and a credential preflight. Together they stop the three most
common ways an autonomous build hurts you: leaking a secret or client datum into
the model context or off-box, mutating a protected branch or a shared worktree,
and dispatching a long agent run into a credential that will expire mid-flight.

**License caution.** These hooks MODEL the structure of the jackal harness hooks
(a private fork of `ed3d-plugins`, itself building on `obra/superpowers` by Jesse
Vincent). We wrote our own implementations from the patterns; no upstream source
is copied. The upstream license state is currently ambiguous - the plugin
manifests say "UNLICENSED" while the actual LICENSE files say CC-BY-SA-4.0
(copyleft, attribution-required) with an MIT `superpowers` core - so until that is
clarified with the jackal author we treat everything here as pattern-only and
keep this attribution note traveling with the patterns. Do not paste upstream
`.py` files into your repo; author from these templates instead.

---

## What all three hooks have in common (the contract)

Every hook here is:

- **Pure Python, zero-dependency, stdin-JSON.** Claude Code invokes the hook and
  pipes it a JSON object on stdin describing the tool call
  (`tool_name`, `tool_input`, `cwd`, ...). The hook reads stdin, decides, prints
  one JSON object on stdout, and exits 0.
- A **PreToolUse** hook (fires before the tool runs, so it can block) or a
  **PostToolUse** hook (fires after, so it can only advise). The bash guard and
  branch guard are PreToolUse; a "you just wrote a secret-looking file" reminder
  is PostToolUse; the credential preflight is PreToolUse on agent dispatch.
- A hook that emits one of two shapes:
  - a **decision** - `{"hookSpecificOutput": {"hookEventName": ...,
    "permissionDecision": "deny"|"ask", "permissionDecisionReason": "..."}}` - to
    block outright (`deny`) or force an explicit human approval (`ask`); or
  - **advice** - `{"hookSpecificOutput": {"hookEventName": ...,
    "additionalContext": "..."}}` - to inject a warning into the agent's context
    without blocking anything.
- **Fail-open on any internal exception.** If the hook's own logic throws, it
  swallows the exception and exits 0 (allow). This is deliberate and it is the
  single most important property: **a guard that crashes the session is worse than
  a guard that misses a case.** A false deny blocks real work over a state the
  agent cannot fix; a missed case is caught by the next layer. Fail toward letting
  work proceed.
- **Env-var overridable.** Every deny/ask rule has an environment-variable escape
  hatch so an operator who genuinely needs the blocked action can proceed for the
  session without ripping the hook out.
- **Paired with a test file.** Each hook ships a `test_*.py` next to it that feeds
  crafted stdin payloads and asserts the decision. Guards are security-critical and
  silent by design (a working guard produces no visible output on the happy path),
  so they need tests more than ordinary code does - an untested guard that has
  quietly stopped firing looks identical to one that is working.

### The generic skeleton (invented illustration - copy this shape, not upstream)

```python
#!/usr/bin/env python3
"""Generic PreToolUse guard skeleton: deny / ask / fail-open contract."""
import json
import os
import sys

TRUTHY = {"1", "true", "yes", "on"}
OVERRIDE_ENV_VAR = "MYORG_ALLOW_THING"


def override_active() -> bool:
    return os.environ.get(OVERRIDE_ENV_VAR, "").strip().lower() in TRUTHY


def emit(decision: str, reason: str) -> None:
    # decision is "deny" or "ask"
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def emit_advice(message: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": message,
        }
    }))
    sys.exit(0)


def evaluate(tool_name: str, tool_input: dict, cwd: str) -> None:
    # ... your checks here; call emit("deny", ...) / emit("ask", ...) to act.
    return  # returning without emitting == allow


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError):
        sys.exit(0)                      # unparseable input -> fail open
    if not isinstance(data, dict):
        sys.exit(0)
    if override_active():
        sys.exit(0)                      # operator opted out for this session

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}
    cwd = data.get("cwd") or os.getcwd()

    try:
        evaluate(tool_name, tool_input, cwd)
    except SystemExit:
        raise                            # emit()/allow already decided - let it through
    except Exception:
        sys.exit(0)                      # FAIL OPEN: never crash the session
    sys.exit(0)                          # no rule fired -> allow


if __name__ == "__main__":
    main()
```

Note the `except SystemExit: raise` before the broad `except Exception`: the
`emit` helpers exit via `SystemExit`, and you must let that propagate rather than
have the fail-open handler swallow your own deny.

### hooks.json wiring (generic shape)

A plugin's `hooks/hooks.json` maps a tool-name matcher to the command that runs
the hook. `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin directory at runtime.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/check-bash-guard.py\"",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/check-branch-guard.py\"",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "Agent|Task",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/check-credential-preflight.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/check-sensitive-file.py\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

The `matcher` is a regex on the tool name. Set a **short timeout** (5-10s): a hook
runs synchronously in front of every matched tool call, so a slow hook taxes every
turn. If the hook overshoots its timeout the harness moves on - which is just
fail-open by another route.

---

## Hook 1: Secrets / client-data bash guard (PreToolUse on Bash)

**Goal.** Catch a Bash command that would read a secret (or, in the client-data
variant, a client/tenant identifier or PII) into the model context or ship it
off-box, and stop it before it runs.

**Structure.** The pipeline is: **tokenize -> split into pipeline stages ->
run per-check functions -> deny or ask.**

1. **Tokenize** the command with `shlex.split` so quoted text stays one token and
   `echo "cat .env"` never looks like a `cat` invocation. On a quoting error, fall
   back to a naive `str.split` rather than guessing.
2. **Split into pipeline stages** on unquoted `|` (and, for a branch-aware variant,
   on `;`/`&&`/`||`). Many checks are per-stage: `env | grep TOKEN` is only
   dangerous because of what the second stage does with the first stage's output.
3. **Run each check function.** Each returns a reason string (act) or `None`
   (nothing to say). High-confidence checks map to `deny`; medium-confidence,
   sometimes-legitimate patterns map to `ask` so a human decides.

**Detection surface = two sets crossed together:**

- `SECRET_WORDS` - substrings in a variable or file name that suggest a secret:
  `secret`, `token`, `password`, `passwd`, `key`, `credential`, `auth`, `private`,
  `api_key`, `apikey`, `access_key`.
- `SECRET_FILE_PATTERNS` - regexes for files that typically hold secrets:
  `\.env$`, `\.env\.`, `\.envrc$`, `credentials`, `secrets?\.`, `\.pem$`,
  `\.key$`, `\.netrc$`, `\.npmrc$`, `aws/credentials`.

A name "looks secret" if it contains any `SECRET_WORDS` entry; a path "looks
secret" if it matches any `SECRET_FILE_PATTERNS` regex. Every check is one of
those two matchers applied to a specific command shape.

### DENY - high-confidence leaks (no legitimate use the safe alternative doesn't serve)

- **`echo`/`printf` of a secret-named variable** - `echo $API_TOKEN` prints the
  value straight into context. (Safe alternative to suggest in the reason:
  `[[ -v API_TOKEN ]] && echo set || echo unset` - existence, not value.)
- **`printenv SECRET`** with a secret-named argument - reads the value.
- **Length / substring parameter expansion on a secret var** - `${#TOKEN}` leaks
  the length (narrows the search space, confirms the format); `${TOKEN:0:8}` leaks
  a prefix that dramatically narrows a brute force. A partial secret is still a
  secret.
- **`declare -p SECRET`** - dumps the variable's value.
- **Polyglot env readers** - a language one-liner reading an env var:
  `python -c "import os; print(os.environ['SECRET'])"`, `node -e
  "console.log(process.env.SECRET)"`, `ruby -e "puts ENV['SECRET']"`,
  `perl -e 'print $ENV{SECRET}'`, `awk 'BEGIN{print ENVIRON["SECRET"]}'`. Same leak,
  routed around bash - so the guard has to know the polyglot shapes, not just bash
  builtins.

### ASK - medium-confidence (real uses exist, dangerous by default)

- **`env | grep TOKEN`** (or `export`/`set` piped to `grep`) **without `-q`** -
  grep without quiet prints the matching line, value and all. With `-q` it is a
  silent existence check; without, it is a leak.
- **`cat`/`less`/`sed`/`base64`/`xxd`/`dd if=` on a secret-looking file** - any
  content-reading command aimed at `.env`/`.pem`/`credentials`. (Reason suggests
  `grep '^[A-Z_]*=' file | cut -d= -f1` to see structure without values.)
- **Token embedded in a git URL** - `https://$TOKEN@host/...` persists the secret
  in `.git/config` and shell history.
- **Token in a curl URL query string** - `?api_key=$KEY` gets logged in server
  access logs, proxies, and history; the header form is safer.
- **curl exfil of a secret file** - `curl -d @.env ...` / `curl -F file=@.env ...`
  POSTs the whole credential file to a remote.

The DENY/ASK split is the whole design: deny only where there is no legitimate use
that the safe alternative would not also serve; ask everywhere a real workflow
occasionally needs the pattern, so the human - not the hook - carries that call.

### Adapting this into a CLIENT-DATA guard

The exact same machine, retargeted. This is the pattern to **upgrade the existing
`wd-*` client-data git guard** into a general egress guard:

1. **Swap the detection sets.** Replace `SECRET_WORDS` with client/tenant
   identifiers and PII markers (client short-names, tenant IDs, engagement codes,
   `ssn`/`dob`/`mrn`-style field names) and `SECRET_FILE_PATTERNS` with the paths
   client data lands in (a `client-data/` tree, exported CSVs, tenant extracts).
   Keep these lists in one place so they are easy to extend per engagement, and
   remember: **never hard-code an actual client name into a shared skill or repo** -
   drive the guard from a local, gitignored config the operator populates.
2. **Add matchers on tools that egress**, not just tools that read. A secret leak
   is mostly "reads into context"; a client-data leak is mostly "leaves the box."
   So also inspect:
   - **Bash `curl`/`wget`/`scp`/`rsync`** to any non-approved host - deny/ask on a
     request body or upload that carries a client-data path or a matched identifier.
   - **`Write` to a shared path** - a PostToolUse (or PreToolUse on Write) check
     that fires when client data is being written outside the approved local
     working area (a synced drive, a shared/team path, anything that will replicate
     off-box).
3. **Bias toward `ask` over `deny`** for client data. Legitimate delivery work
   moves client data around constantly; the guard's job is to make an off-box move
   a conscious, approved action, not to make the work impossible.

### PostToolUse companion (the "you just wrote a secret file" reminder)

A tiny PostToolUse hook on `Write|Edit` that fires when the written path matches
`SECRET_FILE_PATTERNS` and injects `additionalContext` reminding the agent to
verify the file is gitignored (`git check-ignore -v`) and permissioned (`chmod
600`). It blocks nothing - it cannot, PostToolUse runs after the write - it just
makes the follow-up hygiene explicit. The client-data variant reminds the agent to
confirm the write landed in the approved local area, not a synced/shared one.

---

## Hook 2: Branch guard (PreToolUse on Edit/Write and Bash)

**Goal.** Keep autonomous work off protected branches and out of the shared
primary checkout, so the Pull Request stays the only path onto `main`/`master` and
no agent clobbers a worktree another session owns.

Four responsibilities, dispatched on `tool_name`, each with its own override:

1. **Write to a protected branch -> deny.** On `Edit`/`Write`/`NotebookEdit`,
   resolve the git repo of the **target file** (walk up to the nearest existing
   directory, then ask git), read its current branch via `git symbolic-ref
   --short HEAD`, and deny the write if HEAD is on a protected branch
   (`main`/`master` by default). Resolving per **target file** - not per process
   cwd - is what makes it worktree-aware: an edit to a file in a feature-branch
   worktree is fine even while the primary checkout sits on `main`.
   Override: `MYORG_ALLOW_MAIN_WRITES=1`.
2. **`git commit`/`git push` on a protected branch -> deny.** On Bash, parse the
   command into segments, find any `git` invocation (tolerating a leading
   `FOO=bar` env prefix and `-C <dir>`), resolve its working directory (apply any
   `cd` in an earlier segment), and deny `commit`/`push` when that directory's HEAD
   is protected. Same override as (1).
3. **Tree-mutating git in the shared PRIMARY worktree -> deny.** Deny
   `checkout`/`switch`/`rebase`/`reset`/`merge`/`cherry-pick`/`commit`/`am`/
   `apply`/`revert`/`restore` when the command runs in the repository's **primary**
   checkout, on any branch. Detect "primary" by comparing `git rev-parse
   --absolute-git-dir` to `--git-common-dir`: a linked worktree's git-dir sits
   under `.git/worktrees/<name>/` while its common-dir points at the shared `.git`,
   so the two paths differ; the primary reports the same path for both. The primary
   is shared global state no session owns - that work belongs in a linked worktree.
   Override: `MYORG_ALLOW_PRIMARY_TREE=1`.
4. **`git stash` mutation ANYWHERE -> deny.** Deny every mutating stash form
   (`push`/`save`/`pop`/`apply`/`drop`/`clear`/`branch`/`create`/`store`, and the
   bare `git stash`) in **any** working tree, primary or linked - because the stash
   reflog lives in the repository's shared `.git` and is common to every linked
   worktree, so stashing from one worktree can pocket or re-apply another worktree's
   uncommitted work. `git stash list` and `git stash show` are read-only and always
   allowed. Override: `MYORG_ALLOW_STASH=1`.

**Fail open** on anything ambiguous: not a git repo, a detached HEAD (no branch to
protect), git missing, a gitignored scratch path, or a `/tmp`-style scratch prefix.
**Fail closed** (deny) only on a confirmed protected branch, a confirmed primary
checkout, or a confirmed stash mutation. Each override is independent - none of the
others also disables the stash guard, and the stash override does not disable the
other two.

Make the deny reason **actionable**: tell the agent exactly what to do instead
(`git switch -c <type>/<slug>` then re-apply and finish through a PR;
`git worktree add ...` then run the command there; `cp` a file aside instead of
stashing) and name the override for the deliberate-exception case. A guard that
only says "no" gets worked around; a guard that says "do this instead" gets
followed.

Parsing tips that matter: split on operator boundaries (`;`/`&&`/`||`/`|`/`&`) so
a quoted `echo "git commit"` is never mistaken for a real commit; skip `--help`/
`-h` and `push --dry-run` since they mutate nothing; and always resolve the git
directory defensively (nearest existing dir, then git) so a path that does not yet
exist does not crash the hook.

---

## Hook 3: Credential preflight (PreToolUse on agent dispatch, Bedrock/AWS-SSO)

**Goal.** Before a long unattended agent dispatch, warn if the shared AWS SSO
token the whole fleet authenticates through is expired, near-expiry, or
non-refreshable - so the operator re-auths *before* launching work that would
otherwise die mid-flight. **This one is Bedrock/AWS-SSO specific** by design.

**Why it exists.** When Claude Code runs on Amazon Bedrock, every agent in the
fleet authenticates through **one** cached SSO token. When that token lapses,
every in-flight agent dies within the same second - including the orchestrator,
which is then unable to run its own stall-recovery logic. A dispatch launched into
a soon-to-expire session is the failure this check prevents.

**What it does, reading only local files (no STS calls, no network, no token
values):**

- Fires **only** when `CLAUDE_CODE_USE_BEDROCK` is set (otherwise the SSO token is
  irrelevant - exit 0). Gated to the dispatch tools (`Agent`/`Task`), since a
  dispatch is the thing that runs unattended long enough to outlive a token;
  interactive tool calls fail visibly and get retried.
- Resolves which cached token the active profile depends on: read `~/.aws/config`
  for the profile's `sso_session` (following `source_profile` hops, since Bedrock
  profiles are usually assumed-role chains where only the last hop names the
  session), then locate `~/.aws/sso/cache/<sha1(session)>.json`. Fall back to the
  most-recently-modified cache file that actually holds an `accessToken`.
- Assesses three states from the cached token JSON:
  1. Is it already **expired** (or how long until `expiresAt`)?
  2. Does it carry a **`refreshToken`**? Without one (the legacy non-refreshable
     format) expiry forces an interactive `aws sso login` - so any dispatch
     outliving it is doomed.
  3. Is the **client registration** (`registrationExpiresAt`) near expiry?
     Registration expiry defeats refresh, so a valid refresh token is not
     sufficient on its own - warn earlier on this one.
- Reads the dispatch's expected duration when the prompt carries one (e.g. an
  `EXPECT: ... within <n>m` line) and warns when remaining lifetime is shorter than
  the run needs.

**It WARNS, it does not deny (by default).** It emits `additionalContext`, not a
`permissionDecision` - a false deny would block real work over a credential state
the agent cannot fix, and only the operator can run `aws sso login`. Provide a
`MYORG_PREFLIGHT_BLOCK=1` override to make the unrefreshable-and-expiring case deny
instead, and a `MYORG_PREFLIGHT_DISABLE=1` to silence it entirely. Fail open on any
read error, exactly like the others - a preflight that crashes the dispatch is
worse than one that misses a warning.

**Adapting.** This hook is inherently tied to the AWS-SSO/Bedrock credential
model. If your build authenticates a different way, keep the *shape* - a
PreToolUse-on-dispatch check that reads a local credential artifact, computes
remaining lifetime against the expected run length, and warns rather than blocks -
but swap the AWS-specific token discovery for whatever your auth surface exposes.
For a build that never dispatches long unattended runs, this hook may simply not
apply.

---

## Putting them together

- Ship each hook as a small plugin (or a `hooks/` directory) with its own
  `hooks.json`, the `.py`, and a `test_*.py`.
- Keep the three concerns in separate hooks even though they could be one file:
  independent matchers, independent overrides, and independent failure blast
  radius. A bug in the credential preflight should never be able to take down the
  secrets guard.
- Test every hook with crafted stdin payloads: a payload that must deny, one that
  must ask, one that must pass, and one malformed payload that must fail open.
  These guards are silent on the happy path, so the tests are how you know they are
  still firing at all.
