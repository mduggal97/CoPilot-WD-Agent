---
name: session-orchestration
description: >-
  Fork work out to other agents, sessions, and models to parallelize, and pick the RIGHT model for
  each piece - route up (stronger) or down (cheaper) by task. Cross-cutting: applies to ANY Claude
  Code work in either suite track. Use when work could run in parallel, a job reads across many
  files, or a subtask wants a different model or another session. TRIGGERS: "fork this",
  "parallelize", "run these in parallel", "fan out", "delegate to another agent/session", "spin up
  agents", "which model should I use", "use a cheaper model", "use a stronger model", "route
  up/down", "background this", "have another session do X", "run this on a schedule", "too much to
  do in one session". Answers four questions: should I fork, to WHAT mechanism (subagent, peer or
  cloud session, scheduled run, Workflow), which MODEL, and how to dispatch so the result is
  trustworthy. The build-loop use of model tiers is app-harness; this skill owns the GENERAL
  forking and model-routing decision.
---

# Session Orchestration - fork work, pick the model, gather safely

This skill is a thin index over how to **parallelize work across agents, sessions, and models**
without losing correctness. It generalizes the model-tiering + dispatch discipline in `app-harness`
(which applies it to the hosted-tool build loop) to **any** work - research fan-outs, cold-reads,
bulk authoring, verification, analysis.

The whole thing is four questions. Answer them in order.

## 1. Should I fork this at all?

Fork when the work is one of:

- **Parallelizable** - independent pieces that don't depend on each other's output (N files to review, M skills to cold-read, several drafts to write). Serial is wasted wall-clock.
- **Read-heavy across many files** - a broad sweep where you only need the conclusion, not every file in your own context. Delegating keeps your context clean.
- **Better on a different model** - a mechanical bulk job that a cheaper model does fine (route down), or a hard reasoning job worth a stronger model (route up).
- **Long-running or detached** - work that should outlive this turn, run in the background, or run on a schedule.

Do NOT fork when: the task is a single quick fact you already know the location of; the pieces are tightly coupled and share a lot of evolving context (keep it in one brain); or the coordination overhead exceeds the work.

## 2. Fork to WHAT? (pick the mechanism)

| The work is... | Use | Why |
|---|---|---|
| A few independent side-tasks, results needed THIS session | **In-process subagents** (the Agent tool) | Fast, parallel in one message, results return as notifications |
| Dozens-to-hundreds of agents, or findings that must be cross-checked against each other | **A Workflow** (opt-in: `ultracode`) | Deterministic script orchestrates fan-out + adversarial verify |
| Something a DIFFERENT live session should do (a peer on this machine, a cloud session) | **Cross-session message** (ListAgents + SendMessage) | Hand a peer a task; plain text only, no context travels |
| A brand-new separate session to carry a task | **Spawn a background session** (`/bg`, `/fork`, or a task chip) | A persistent session under a supervisor, survives your turn |
| A polling / works-toward-a-condition job while this session stays open | **`/loop`** (session-scoped, 1-min min) | Cron-in-session; pick a cheap model for polling |
| Unattended, must survive your machine being off, runs on a schedule | **A cloud Routine** (`/schedule`, 1-hour min) | Runs on Anthropic cloud, independent of any session |

Full mechanics, parameters, and the reach/limits of each: [references/mechanisms.md](references/mechanisms.md).

## 3. Which MODEL - up or down?

The heart of it. **Name the model on every dispatch - leaving it on the default is a defect** (it silently abandons tier discipline). Quick read:

- **Down to Haiku** - mechanical, fully-specified, bounded-evidence, high-volume-cheap (scanners, bulk formatting, deterministic checks, polling loops). Fastest, cheapest.
- **Sonnet - the safe default** - standard build, review, drafting, most fan-out reviewers. Best speed/intelligence ratio; when unsure, pick Sonnet.
- **Up to Opus** - design, architecture, deep/high-risk review (security, contracts, concurrency), ambiguous scope.
- **Up to Fable** - the most demanding long-horizon reasoning; slowest and priciest, reserve for where depth changes the outcome.

The full routing table, the cost/capability tradeoffs, reasoning-effort levels, and how to SET the model per subagent: [references/model-routing.md](references/model-routing.md).

## 4. How to dispatch so the result is trustworthy

- **Self-contained prompts** - a subagent does NOT inherit your conversation history; put everything it needs in the prompt.
- **Report-only vs edit** - deny Write/Edit for research/review agents; grant them only when the agent must change files.
- **Verify, don't trust** - a worker reporting "done" is a claim; confirm with your own same-turn observation (read the file, `git diff`) before you rely on it.
- **Parallel in ONE message** - dispatch independent agents together, not one-wait-one.
- **Watch the long-single-file-edit trap** - a subagent making one huge edit to an existing file can stall or drift; prefer authoring NEW files via subagents and doing large edits to existing files yourself, or split the edit.

Full discipline + named patterns (map-reduce cold-read, research-benchmark, parallel-authoring, supervisor-worker): [references/dispatch-discipline.md](references/dispatch-discipline.md).

## Reference map - read what you need

| You're working on | Read |
|---|---|
| **Which model - up or down** - the routing table, cost/capability, effort levels, setting the model | [references/model-routing.md](references/model-routing.md) |
| **Which mechanism** - subagents, cross-session, Workflow, scheduled/cloud - parameters, reach, limits | [references/mechanisms.md](references/mechanisms.md) |
| **How to delegate well** - self-contained prompts, verify-don't-trust, parallel dispatch, the named fan-out patterns | [references/dispatch-discipline.md](references/dispatch-discipline.md) |

## Boundaries

- **The hosted-tool BUILD LOOP** (supervisor/planner/implementor/reviewer, phases, git/PR, the conflict gate) is **app-harness** `references/complexity-routing.md` - the specialized application of these invariants to building a tool. This skill owns the GENERAL forking + model-routing decision; don't duplicate the build pipeline here.
- **Authoring or optimizing a skill** (evals, description tuning) is the skill-creator skill, not this one.
- **The agentic RUNTIME of a hosted tool** (a deployed tool that itself calls models / runs tool-loops) is **app-agentic** - a different thing from orchestrating YOUR Claude Code work.

## Lifecycle neighbors

Cross-cutting / meta - it serves both suite tracks and general Claude Code work. Reach for it whenever a task is big enough to split. It has no ship gate of its own; it's a way of working, not a deliverable.

> Version note: the exact tool names, parameters, model ids, and CLI commands here are current as of authoring against the official Claude Code + Claude API docs, but this surface moves fast. Confirm specifics (model aliases, `/bg` vs task chips, cross-session reach, Workflow opt-in) against your Claude Code version - the DECISION framework (when to fork, which model, verify-don't-trust) is stable even as the mechanics shift.
