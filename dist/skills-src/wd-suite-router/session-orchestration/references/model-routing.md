# Model routing - up or down

How to pick the model for a piece of work, and how to set it. The rule that governs everything:
**name the model on every dispatch.** Leaving a subagent on the inherited/default model is a
**defect**, not a style lapse - it silently abandons tier discipline, and dispatches quietly drift
to the default when nobody names one.

## Table of contents

- The models (as of authoring)
- Route DOWN (cheaper) when
- Route UP (stronger) when
- A routing table by task type
- Reasoning effort (a second dial)
- How to SET the model
- The one discipline that makes this work

## The models (as of authoring - verify current)

Four tiers. Prices are approximate per-million-tokens (MTok) and **change - confirm current pricing
before quoting cost**; they're here for the RELATIVE tradeoff, which is stable.

| Model | Alias | Full id | Relative cost (in/out per MTok) | Best for |
|---|---|---|---|---|
| **Haiku 4.5** | `haiku` | `claude-haiku-4-5-20251001` | ~$1 / $5 (cheapest) | Fast, simple, bounded, high-volume work |
| **Sonnet 5** | `sonnet` | `claude-sonnet-5` | ~$2 / $10 | The balanced default - speed + intelligence |
| **Opus 5** | `opus` | `claude-opus-5` | ~$5 / $25 | Complex reasoning, coding, deep review |
| **Fable 5.1** | `fable` | `claude-fable-5-1` | ~$10 / $50 (priciest) | The most demanding long-horizon reasoning |

Cost scales in BOTH directions that matter for forking: a stronger model costs more per token, AND
a fan-out of many agents multiplies whatever tier you pick. A 20-agent sweep on Opus is not a
casual choice; the same sweep on Haiku or Sonnet often gets the same answer for a fraction of the
spend.

## Route DOWN (cheaper) when

Drop to **Haiku** (or from Opus to Sonnet) when the task is:

- **Mechanical and fully specified** - it executes a concrete spec rather than deciding anything
  (rename these symbols, reformat these files, extract these fields).
- **Bounded-evidence adjudication** - a scanner/sentinel that reads a small, pre-assembled packet
  and returns a yes/no or a short structured verdict. (A deterministic pre-pass that hands each
  cheap agent a tiny evidence bundle is the pattern - the cheap model never has to crawl.)
- **High-volume, cost-compounding** - a big fan-out where per-agent cost multiplies. Route down
  unless each agent genuinely needs the reasoning.
- **Polling / works-toward-a-condition** (a `/loop` checking CI or a deploy) - use the cheapest
  model that can read the state and decide "done or keep waiting."
- **Read-and-summarize** with no hard reasoning.

Guardrail: **Haiku is opt-in for the easy case, never a floor to grind against.** If a Haiku worker
stalls, or the slice turns out bigger/fuzzier than specified, re-dispatch it cold on Sonnet. Haiku
also does not support the reasoning-effort dial (below), so it's the wrong tool for anything that
needs deliberate thinking.

## Route UP (stronger) when

Go to **Opus** (or **Fable** for the extreme end) when the task is:

- **Design / architecture** - resolving "what to build," cross-system contracts, tradeoff calls.
- **Deep or high-risk review** - security, auth, payments, user/tenant data, crypto, concurrency,
  contract boundaries. A small change on those surfaces still earns a strong reviewer.
- **Ambiguous scope** - the task itself is under-specified and needs judgment to frame.
- **Long-horizon agentic work** - a multi-hour investigation, a competing-hypotheses probe, a
  hard debug. Fable is the top of this range; reserve it for where reasoning depth actually changes
  the outcome (it's the slowest and most expensive).

The expensive tiers are for where **reasoning depth changes the result**, not as a default "to be
safe" - a strong model on a mechanical task just burns money slower.

## A routing table by task type

| Task | Model | Note |
|---|---|---|
| Bulk rename / reformat / field-extraction (specified) | **Haiku** | Mechanical; re-run cold on Sonnet if it stalls |
| Scanner / sentinel over a pre-built evidence packet | **Haiku** | Bounded, deterministic-ish |
| `/loop` polling (CI, deploy, queue) | **Haiku / Sonnet** | Cheapest that can decide "done?" |
| Cold-read / QA reviewer (one dimension) | **Sonnet** | The default reviewer tier |
| Authoring a doc / reference / draft | **Sonnet** | Bulk drafting; up to Opus if the content is genuinely hard |
| Standard code implement / edit | **Sonnet** | The safe default; when unsure, Sonnet |
| Research with source-checking | **Sonnet** | Up to Opus if synthesis is the hard part |
| Design / architecture / plan | **Opus** | Design-shaped reasoning |
| Deep review of a high-risk diff | **Opus** | Security / contracts / concurrency |
| Multi-hour investigation, competing hypotheses, hard debug | **Fable** | Only when depth changes the outcome |

Adapt freely - this is a starting bias, not a law. When genuinely unsure between two tiers, pick the
cheaper one and escalate only if the result is thin.

## Reasoning effort (a second dial)

Independent of the model, some models take a reasoning-effort setting that trades tokens for
deliberation: `low` (short, latency-sensitive), `medium` (cost-sensitive), `high` (the default
balance), `xhigh` (deeper, higher token cost), `max` (most demanding - test before adopting broadly).

- Supported on the stronger tiers (Fable / Opus / Sonnet families); **Haiku does not take an effort
  setting** - another reason it's for simple work.
- `ultracode` is a session-level mode = `xhigh` reasoning + automatic Workflow orchestration (see
  mechanisms.md). It's how you opt a whole session into heavier multi-agent work.

Rule of thumb: pick the MODEL for the capability, then raise EFFORT only if the task needs more
deliberation per step. Don't reach for `max` reflexively - it costs tokens and hits diminishing
returns.

## How to SET the model

In Claude Code (confirm against your version):

- **Per dispatch** - pass `model` on the Agent tool call (`opus` / `sonnet` / `haiku` / `fable`, or
  the full id). This wins over everything else.
- **Per subagent definition** - `model: sonnet` (or `model: inherit` to use the main session's
  model) in the subagent's frontmatter.
- **Session-wide subagent default** - the `CLAUDE_CODE_SUBAGENT_MODEL` env var; a force-flag can
  pin all subagents to one model.
- Resolution order: per-call `model` > subagent-definition `model` > the env default > the main
  conversation's model.

## The one discipline that makes this work

**Every dispatch names its model, with a one-line reason when you route off the default.** "Haiku -
mechanical field extraction, no judgment." "Opus - security-sensitive auth review." That single
habit is what keeps a fan-out from silently running everything on one tier and either overspending
or under-reasoning. It's the same rule app-harness `complexity-routing.md` enforces for build
workers, generalized to any dispatch.
