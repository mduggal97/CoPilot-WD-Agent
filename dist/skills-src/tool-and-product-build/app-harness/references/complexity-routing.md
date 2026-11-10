# Complexity Routing and Orchestration Invariants

Reference for `app-harness`. This is the "how we build" layer for developing a
hosted tool with Claude Code - the build-discipline loop, distinct from the
"what we host" skills (`app-architecture`, `app-hosting`, `app-agentic`).

**Lineage / attribution.** These patterns are modeled on the jackal harness (a
private fork of `ed3d-plugins`), which itself derives from `obra/superpowers` by
Jesse Vincent. We MODEL the patterns here; we do not copy upstream source. Keep
this attribution line with the patterns if you reuse them - the upstream carries
a copyleft-style attribution requirement and its exact license terms are still
being clarified with the jackal author (see `security-hooks.md` "License
caution"). Everything below is an independent adaptation, written from scratch.

---

## Why route by complexity at all

The failure this prevents: an agent that treats every task the same way either
over-engineers a one-line fix (a full design + plan + review cycle on a typo) or
under-engineers an architectural change (charging into an ambiguous, multi-system
build with no design and no human in the loop, producing confident-looking code
that solves the wrong problem). Routing forces an explicit up-front read of *how
much ceremony this unit of work actually needs*, and it puts a hard stop in front
of the one case where autonomous building is genuinely dangerous.

Read the work-unit's complexity once, at the top of the loop, before dispatching
anything. Everything downstream keys off that classification.

---

## The routing table

| Tier | What it looks like | Pipeline | Human gate |
|---|---|---|---|
| **Simple** | Under ~1 day. A bug fix, a single-concern change, one file or a tight cluster. No architectural choice left open. | Implement directly. One review pass. **No plan, no design.** | None (autonomous). |
| **Standard** | Multi-file, but acceptance criteria are clear and the shape is known. | **Plan into phases** -> implement each phase -> review. | None (autonomous), but the plan is written and disk-committed first. |
| **Complex** | Architectural decisions, ambiguous scope, cross-system contracts, anything where "what to build" is itself unresolved. | **STOP.** Require a human-run design first. | **Mandatory.** Never build autonomously. |

### Simple - implement directly

- One implementor dispatch against the work-unit doc.
- No planning phase and no design phase - the ceremony would cost more than the change.
- Exactly **one review pass** by default. Route the verdict through the fix loop
  (below): on issues found, dispatch a fix and re-review, stopping after 3 cycles.
- **Security carve-out.** A Simple change that touches auth, credentials, payments,
  user/tenant data, or crypto escalates its review to the deep (Opus) reviewer even
  though the change is small. Small does not mean low-risk on those surfaces.

### Standard - plan then implement then review

- Dispatch a **planner** to turn the work-unit into a design plan plus ordered
  **phase files** written to disk. Phases are the unit of dispatch and the unit of
  resumability.
- Execute phases per the phase scheduler: each phase file is the complete spec for
  that phase; the implementor reads it just-in-time, implements, tests, verifies,
  and commits.
- Review is tiered by risk (see review routing below). Final review is always
  mandatory.

### Complex - stop and require a human design

- **Do not attempt autonomous execution.** Report plainly: "This is Complex - it
  needs design decisions a human must make. Run the design step first."
- The design is a human-in-the-loop artifact (for an Extend/hosted-tool build
  that is typically the Extend design doc - see `wd-design-doc`). It resolves the
  open architectural questions *before* any code is written, and it becomes the
  input the planner reads.
- Only after a human has produced and signed off the design does the work-unit
  re-enter the loop, now routed as Standard (design exists -> plan -> execute).

**Why the hard stop is load-bearing.** An agent will happily generate plausible
code for an under-specified Complex task; the code compiles, the tests it wrote
pass, and it is wrong at the architecture level in a way no per-phase review
catches. The stop is the cheapest possible place to catch that - before a single
line is written. Removing it is the single highest-regret change you can make to
this loop.

---

## Orchestration invariants

These hold regardless of tier. They are what make an autonomous multi-agent build
recoverable instead of a black box that either finishes or silently corrupts
itself.

### 1. One long-lived supervisor, many stateless one-shot workers

- **Exactly one** long-lived orchestrator/supervisor holds all state: the backlog,
  what is done, what each worker returned, the routing decisions. It is the only
  context that accumulates knowledge across the session.
- **Workers are stateless one-shots.** Each implementor / reviewer / planner
  dispatch receives its full context in-prompt, does one unit of work, and returns.
  It carries nothing forward on its own.
- The supervisor never writes code, never runs the project's correctness tests for
  itself, and never greps the codebase to investigate patterns. If it finds itself
  about to do any of those, it stops and dispatches a worker instead. Its job is
  routing and state, not implementation.

**Why.** A single stateful brain is easy to reason about and easy to resume; a
web of agents that each remember things is neither. Concentrating state in one
place is what lets a killed session pick up exactly where it left off.

### 2. Coordination is ONLY through git and issues - never shared memory

- Workers coordinate through **git** (worktrees, branches, commits) and the
  **issue/backlog** - never through any shared in-memory channel, and never by one
  agent reading another agent's live context.
- Every meaningful step lands as a commit. The disk is the shared truth; an agent's
  claim about what it did is not.

**Why.** Two agents that coordinate through memory have no durable record of what
happened - a crash loses it, and neither can verify the other. Git is the audit
log, the conflict-detection surface, and the recovery point all at once.

### 3. Workers NEVER spawn workers (belt-and-braces)

Enforce this two ways, both required:

1. **Capability.** Deny the sub-agent-dispatch tool (the `Agent`/`Task` tool) in
   every worker's definition. A worker that cannot call it cannot fan out.
2. **Instruction.** Also put the sentence in every dispatch prompt, verbatim:
   *"Do not dispatch or invoke any subagents - do the work directly with your own
   tools."*

Belt and braces: the frontmatter denial is the hard stop, the prompt line makes
the intent explicit so a worker never even tries and burns a turn discovering the
denial. The supervisor is the **sole** dispatch-holder. All parallelism comes from
the supervisor dispatching multiple named workers in one message - never from a
worker recursively spawning its own helpers.

**Why.** Worker-spawned workers destroy the "one brain holds all state" invariant:
now there is a tree of contexts, no single place knows the whole picture, and a
mid-tier agent's mistake fans out to every child it spawned. Keep the topology
flat.

### 4. Every dispatch names its model tier explicitly - `model=null` is a defect

Every single dispatch specifies its `model` explicitly. Leaving it on the harness
default (`model=null`) is treated as a **defect**, not a style lapse - it silently
abandons tier discipline, and in an audited upstream session the large majority of
dispatches had quietly drifted to the default.

Reference tier table (adapt the tool/agent names to your build):

| Dispatched worker | Tier | Rationale |
|---|---|---|
| Planner (design -> phases) | **Opus** | Design-shaped reasoning. |
| Implementor (default) | **Sonnet** | The safe default; when unsure, pick Sonnet. |
| Implementor (mechanical slice only) | **Haiku** | Opt-in, see below. |
| Reviewer (standard) | **Sonnet** | Per-phase and default final review. |
| Deep reviewer (high-risk / Complex) | **Opus** | Security, concurrency, contract boundaries. |
| Mechanical scanners / sentinels | **Haiku** | Bounded, deterministic-evidence jobs. |

**Haiku is opt-in for mechanical slices only.** Drop an implementor to Haiku
*only* when the phase is mechanical and fully specified: it names its exact files,
carries a concrete spec it executes rather than designs, touches **no** auth /
payments / user data / crypto / contract boundary, and is not the integration
phase that wires other phases together. State the one-line reason in the dispatch.
If a Haiku worker stalls or the slice turns out larger than specified, re-dispatch
that slice cold on Sonnet - Haiku is an optimization for the easy case, never a
floor to grind against. (The GENERAL route-up/route-down guardrails are owned by
session-orchestration `references/model-routing.md`; this section is their
build-loop application - change the general rule there, not here.)

**Opus for design and deep review.** The expensive tier is reserved for where
reasoning depth actually changes the outcome: planning, and reviewing high-risk
diffs.

### 5. Read-only-reviewer discipline

A reviewer observes; it never mutates. Enforce it in the reviewer's definition by
denying `Edit`, `Write`, and the notebook-edit tool, and forbid tree-mutating work
via Bash as well:

- No writing to any tracked path from Bash - no `cp`/`mv`/`>`/`>>`/`tee`/`sed -i`/
  `patch`/`rm` onto a repo file, **not even to restore it afterward**.
- No mutating git - no `stash`/`checkout`/`switch`/`restore`/`reset`/`apply`/
  `add`/`commit`/`rebase`/`clean`. Read-only git (`diff`/`log`/`show`/`status`) is
  fine.
- When verification genuinely requires running or A/B-testing modified code, do it
  in a scratch dir outside the tree under review (e.g. `mktemp -d`, then
  `git archive HEAD | tar -x` into it, or `git show <sha>:<path>` into a temp file).

**Why.** The reviewer is looking at a **live** tree that other agents are actively
committing to. A file it overwrites "just for a moment" can be committed by
another agent, or left reverted if the reviewer crashes or times out mid-experiment
- silently discarding someone else's work. This has actually happened upstream: a
reviewer A/B-tested two revisions by `cp`-ing over the tracked file in place while
the implementor was committing that same file. A reviewer that corrupts the build
is worse than no reviewer.

### 6. Honest stopping point + commit at every green

- The moment a worker has something that compiles/passes, it **commits**. Green
  state on disk is a resumable checkpoint.
- If a worker stops before the unit of work is fully done - context limit,
  ambiguity, a blocking dependency, a genuine stall - it commits whatever compiles
  and reports a **resumable, disk-truthful** stopping point: what landed (cite the
  commit SHA and changed files), what remains, and the exact next step.
- A worker never claims progress it cannot back with an on-disk observation, and
  never implies the work is further along than the committed state proves. "Stopped
  here, N of M done, resume at X" is correct behavior, not a failure.

**Why.** These builds run unattended and can die at any point (context exhaustion,
a shared-credential lapse, an operator closing the laptop). If every green state is
committed and every stop is honest, a context death leaves fully resumable work on
disk. If work only lives in an agent's context, a death loses it - and worse, a
dishonest "done" report leaves the supervisor believing work exists that never
landed.

### 7. Verify-don't-trust when relaying delegated work

The supervisor never restates a worker's success claim in its own status unless it
has made a **same-turn on-disk observation** that backs it - a `git log` / `git
diff` / reading the changed file this turn - and cites that evidence. A worker
reporting "done" is a claim, not a fact. This is the delegated-work form of
verification-before-completion: an agent completing is not the same as the diff
showing the change.

### 8. Mutation proof - prove a test can actually fail

A test that cannot fail proves nothing, and a tautological assertion is worse than
no test because it manufactures false confidence. Before trusting a test as
coverage, prove it has teeth:

1. Revert (or deliberately break) the implementation the test covers.
2. Run the test and **quote the failure** - confirm it fails for the right reason,
   naming the assertion that fired.
3. Restore the implementation and confirm the test passes again.

Only a test observed failing-then-passing is real coverage. Bake this into the
implementor's discipline and make the reviewer flag any test whose failure was
never demonstrated. (This is the "revert impl, quote the failure, restore" loop -
the mutation check that separates a real test from a green rubber stamp.)

### 9. The conflict gate - what is someone else already changing?

Before dispatching work against a set of files, run a conflict gate that
enumerates the **live** branches/worktrees and the files they are changing, then
compares against the candidate's in-scope paths:

- Same file touched by live work -> **hard block** (do not dispatch; report it).
- Same directory, different files -> **soft warning** (proceed with a note).
- No overlap -> **clear**.

Two disciplines make the gate trustworthy:

- **Enumerate every live ref, not a name-glob.** A branch-name glob narrower than
  "every ref" silently under-reports and the gate never fires. Enumerate against
  the fork point (two-dot `merge-base ... <ref>`) so a merged/dead branch does not
  produce a false block on already-finished work.
- **Ledger-file exemption.** Some files are touched by *every* change by policy
  (a changelog, a version registry, a lockfile). An overlap **only** on those
  downgrades from hard block to a visible note - otherwise all parallel work blocks
  forever. The exemption is only sound if ledger edits are **serialized late** (done
  once, at finish time, on a freshly-rebased branch), so exactly one writer touches
  them. An overlap on anything other than ledger files still hard-blocks.

**Why.** Parallel autonomous workers on one repo will happily edit the same file
from two branches and produce a merge disaster. The gate is the cheap pre-check
that keeps parallelism safe; the "enumerate every ref" and "two-dot merge-base"
details are exactly the bugs that made an upstream gate silently return empty for
months.

---

## Review routing (Standard and Complex)

After each phase, decide whether to review now or defer to the final review:

| Condition | Action |
|---|---|
| Phase touches auth, payments, user/tenant data, or crypto | Review now (deep tier). |
| Phase is the final phase | Full review. |
| Implementor's self-review flagged uncertainty | Full review. |
| Phase is pure infrastructure/config | Skip per-phase; catch in final review. |
| All other phases | Skip per-phase; catch in final review. |

**Final review is always mandatory** and tiered by risk: standard (Sonnet)
reviewer by default; deep (Opus) reviewer for Complex issues and for any diff
touching auth / payments / user data / crypto / contract boundaries.

**Fix loop.** When review finds Critical or Important issues: dispatch a fix,
re-run review, and if the same issues persist after **3 cycles**, stop and report
to a human. Minor issues are reported, not blocked.

---

## The build loop, end to end

```
Read the work-unit and classify complexity
    |
    +-- Simple   -> implement directly -> one review pass (+ fix loop) -> finish
    |
    +-- Standard -> plan into phases -> per-phase implement/commit/review
    |                                -> mandatory final review -> finish
    |
    +-- Complex  -> STOP. Require a human-run design first.
                    (design signed off -> re-enter as Standard)
```

At `finish`: the change lands through a Pull Request, never by a direct commit to
the protected branch. The PR is the only completion path (the branch guard in
`security-hooks.md` enforces this mechanically). Rebase if behind, push, open the
PR, then continue the loop - do not block waiting for a human to merge.

---

## Adapting this to your build

- These are **patterns, not a drop-in**. Map the worker roles onto whatever agent
  set your build uses; the invariants are what matter, not the exact names.
- The backlog can be GitHub Issues or any durable issue store the supervisor reads
  - the requirement is that coordination state lives on disk / in the tracker, not
  in agent memory.
- The complexity read is a judgment call, but bias toward the hard stop: when
  "Standard vs Complex" is genuinely unclear, treat it as Complex and get a human
  design. The cost of an unnecessary design is hours; the cost of an autonomous
  Complex build gone wrong is the whole session plus the cleanup.
