# Agent Loop - budgeted, metered, multi-turn tool use

Once the provider seam exists (see `provider-seam.md`), the agent loop is what
turns a single model call into an agent: the model asks to use a tool, you run
it, hand the result back, and repeat until the model produces a final answer.

The whole point of THIS loop is that it is **guarded**. Every turn is metered to
a ledger, every budget has a cap, and the loop STOPS when a cap is hit - before
the next tool touches a customer, not after.

---

## Why a budget cap is non-negotiable before a tool touches a customer

An unbounded tool loop is a runaway. Three failure modes, all real:

1. **Cost runaway.** A model that keeps calling tools and re-reasoning can burn
   many dollars in a minute. On a paid Bedrock/Anthropic backend that is real
   money, per run, with no upper bound unless you impose one.
2. **Side-effect runaway.** If the tools write to a customer tenant - create
   records, send messages, change config - an uncapped loop can perform those
   actions dozens of times before anyone notices. The cap is a blast-radius
   limit, not just a cost limit.
3. **Stuck-loop runaway.** A model that cannot satisfy its terminal condition
   will retry forever. Without a turn cap and a wall-time cap, "forever" is
   literal.

So the cap comes first, by construction: you `reserve` budget BEFORE the call,
`reconcile` the actual cost AFTER, and if the reservation is refused the tool
never runs. A budget you check only after spending is not a budget - it is an
invoice. For a tool that mutates customer state, "we noticed we went over" is
not an acceptable place to find out.

Keep the three caps distinct - they answer different questions:

- **turn cap** - how many model round-trips
- **tool-call cap** - how many tool invocations (the side-effect budget)
- **wall-time cap** - how long, in seconds (protects against a slow/hung turn)

And keep a **retry budget** separate from all three: a transient Bedrock blow
(throttle, 5xx, read-timeout) is worth retrying with backoff; a deterministic
bad request (validation error, access-denied) is not - retrying it just burns
budget. Conflating them means either no self-healing or infinite retries.

---

## SpendGuard + SpendLedger - metering with a hard cap

Every model call goes through a reserve-then-reconcile guard against a DB
ledger. The ledger is the durable record; the guard is the gate.

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Reservation:
    """Handed back by SpendGuard.check; passed to record() or release()."""
    subject: str        # who/what the budget is keyed to
    est_micros: int     # upper-bound cost estimate, in micro-dollars


class SpendLedger:
    """Durable spend record + atomic reserve/reconcile (invented, generic).

    Micro-dollars (integers) not floats: money math on floats accrues rounding
    error over thousands of calls. A ledger row per call is the audit trail.
    """

    def reserve(self, subject: str, est_micros: int, *, limit_micros: int) -> bool:
        """Atomically reserve est_micros against subject's remaining budget.

        Returns False when the reservation would breach limit_micros. Atomic so
        two concurrent calls cannot both slip past a nearly-spent budget - the
        pre-flight read is only an early warning; THIS is the gate.
        """
        ...

    def record(self, r: Reservation, actual_micros: int, *, tokens: int) -> None:
        """Reconcile estimate -> actual after the call, and write the usage row."""
        ...

    def release(self, r: Reservation) -> None:
        """Give back a reservation whose call failed before producing a result."""
        ...


class SpendGuard:
    """Reserve before a model call; reconcile or release after. The gate."""

    def __init__(self, ledger: SpendLedger, *, weekly_limit_micros: int) -> None:
        self._ledger = ledger
        self._limit = weekly_limit_micros

    def check(self, *, subject: str, est_micros: int) -> Reservation:
        """Reserve budget or refuse the call.

        Raises BudgetExceeded (surface it as HTTP 429) when the cap is hit. The
        model call never happens - that is the whole value: the guard fails
        CLOSED, before a tool runs, not after the money is spent.
        """
        if not self._ledger.reserve(subject, est_micros, limit_micros=self._limit):
            raise BudgetExceeded(f"weekly budget spent for {subject}")
        return Reservation(subject=subject, est_micros=est_micros)
```

Wire the guard around the provider seam so metering is automatic and no call
site can forget it:

```python
def metered_generate(provider, guard, *, subject, est_micros, **call):
    """Every model call: reserve -> call -> reconcile / release."""
    r = guard.check(subject=subject, est_micros=est_micros)  # may raise 429
    try:
        reply = provider.generate(**call)
    except Exception:
        guard.release(r)   # failed before a billable result - give the reservation back
        raise
    guard.record(r, actual_micros=_price(reply), tokens=reply.input_tokens + reply.output_tokens)
    return reply
```

KT note on N turns = N reservations: an N-turn loop reserves N times, never once
for the whole session. Each turn is a real cost and a real gate. A single
session-level reservation would let a runaway loop through after the first turn.

---

## The loop skeleton (invented, generic)

`run_tool_loop` drives the conversation. Read the budget checks as the
load-bearing part; the tool plumbing is ordinary.

```python
from collections.abc import Callable
import time


@dataclass
class RuntimeBudgets:
    """Caps + live counters. Readable after the loop returns (e.g. for logging)."""
    max_turns: int
    max_tool_calls: int
    wall_time_s: int
    retry_budget: int = 2          # transient Bedrock errors only
    turns_used: int = 0
    tool_calls_used: int = 0
    retries_used: int = 0
    start: float = 0.0
    stop_reason: str = "unknown"

    def wall_time_exceeded(self) -> bool:
        return (time.monotonic() - self.start) >= self.wall_time_s


def run_tool_loop(
    provider,                      # ModelProvider (see provider-seam.md)
    guard,                         # SpendGuard
    *,
    subject: str,
    model,                         # ModelId
    system: str,
    seed_messages: list[dict],
    tools: list[dict],
    dispatch: Callable[[str, dict], dict],   # (tool_name, input) -> tool result
    terminal_tool: str,            # the tool whose call ENDS the loop
    validate_terminal: Callable[[dict], object],  # raises on a bad terminal payload
    budgets: RuntimeBudgets,
    max_tokens: int = 4096,
):
    """Drive a guarded, budgeted tool loop to completion.

    Returns the validated terminal object, or None on a graceful degrade
    (budget spent, wall-time hit, or the model gave up). Never a partial or
    fabricated result - a caller can trust that a non-None return is a real,
    validated answer.
    """
    budgets.start = time.monotonic()
    messages = seed_messages

    for _turn in range(budgets.max_turns):
        # --- CAP 1: wall time. Check before the (slow, costly) call. ---------
        if budgets.wall_time_exceeded():
            budgets.stop_reason = "wall_time"
            return None

        budgets.turns_used += 1

        # --- the model call: metered + retry-aware -------------------------
        try:
            reply = _generate_with_retry(
                provider, guard, subject=subject, budgets=budgets,
                model=model, system=system, messages=messages,
                tools=tools, max_tokens=max_tokens,
            )
        except BudgetExceeded:
            budgets.stop_reason = "budget"     # the gate fired - stop cleanly
            return None
        except Exception:
            budgets.stop_reason = "provider_error"  # transient retries already spent
            return None

        # Re-add the assistant turn using ONLY the normalized ModelReply fields
        # (text + tool_calls) defined in provider-seam.md - so the loop never
        # depends on a raw provider block shape. Each backend's adapter maps its
        # native response onto these two fields; here we map back to the
        # provider-neutral content list the next request needs.
        assistant_content = []
        if reply.text:
            assistant_content.append({"type": "text", "text": reply.text})
        for call in reply.tool_calls:
            assistant_content.append({"type": "tool_use", **call})  # {id, name, input}
        messages.append({"role": "assistant", "content": assistant_content})

        if not reply.tool_calls:
            budgets.stop_reason = "no_tool_use"   # model answered without the terminal tool
            return None

        # --- run each requested tool --------------------------------------
        results = []
        for call in reply.tool_calls:
            name, tool_input = call["name"], call.get("input", {})

            if name == terminal_tool:
                # Terminal tool is NOT budget-gated - it ends the loop.
                try:
                    answer = validate_terminal(tool_input)
                except Exception as exc:
                    # Steer the model with the rejection, spend a retry, continue.
                    if budgets.retries_used >= budgets.retry_budget:
                        budgets.stop_reason = "terminal_rejected"
                        return None
                    budgets.retries_used += 1
                    results.append(_error_result(call["id"], str(exc)))
                    continue
                budgets.stop_reason = "submitted"
                return answer      # the one trusted exit

            # --- CAP 2: tool-call budget (the side-effect limit) ----------
            if budgets.tool_calls_used >= budgets.max_tool_calls:
                results.append(_error_result(
                    call["id"],
                    f"tool budget spent ({budgets.max_tool_calls}). Call {terminal_tool} now.",
                ))
                continue

            budgets.tool_calls_used += 1
            results.append(_ok_result(call["id"], dispatch(name, tool_input)))

        messages.append({"role": "user", "content": results})

    budgets.stop_reason = "max_turns"      # CAP 3: turn cap fell through
    return None
```

The retry wrapper keeps transient failures from killing a run while refusing to
retry deterministic ones:

```python
_TRANSIENT_BACKOFF_S = (1.0, 4.0, 10.0)


def _generate_with_retry(provider, guard, *, subject, budgets, **call):
    attempt = 0
    while True:
        try:
            return metered_generate(provider, guard, subject=subject,
                                     est_micros=_estimate(call), **call)
        except Exception as exc:
            if not _is_transient(exc):
                raise                       # validation/access-denied -> do NOT retry
            if budgets.retries_used >= budgets.retry_budget:
                raise
            delay = _TRANSIENT_BACKOFF_S[min(attempt, len(_TRANSIENT_BACKOFF_S) - 1)]
            if budgets.wall_time_s - (time.monotonic() - budgets.start) <= delay:
                raise                       # no wall-time left to sleep - give up now
            budgets.retries_used += 1
            attempt += 1
            time.sleep(delay)
```

KT note on graceful degrade: every stop path returns `None`, never a
half-built answer. The caller distinguishes "no result" from "here is a
partial guess" - the second is worse than the first when a consultant will act
on it. `budgets.stop_reason` tells you WHY it stopped for logging.

---

## AgentSpec - the loop's inputs as declarative data (the model card)

Every field the loop needs - model, budgets, tools, prompt, terminal contract -
is data, not code. One frozen "model card" per agent. A reviewer reads one card
and can reproduce exactly what the agent will do, without tracing call sites.

```python
from pydantic import BaseModel, ConfigDict


class AgentSpec(BaseModel):
    """Declarative model card for ONE run_tool_loop invocation.

    frozen: built once, reused, never mutated on the hot path.
    extra='forbid': a typo'd or out-of-scope field is a validation error, not a
    silently ignored setting - the spec cannot drift from what the loop reads.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    model_id: ModelId
    system_prompt: str
    tools: list[dict]
    terminal_tool: str
    max_tokens: int

    # Budgets as data - a fresh RuntimeBudgets is built per run so mutable
    # counters never leak between runs.
    max_turns: int
    max_tool_calls: int
    wall_time_s: int

    def budgets(self) -> RuntimeBudgets:
        return RuntimeBudgets(
            max_turns=self.max_turns,
            max_tool_calls=self.max_tool_calls,
            wall_time_s=self.wall_time_s,
        )
```

Why data beats code here:

- **Reviewable.** A locked-down agent's budgets and tool list are one object to
  read, not a scavenger hunt.
- **Testable.** You can assert a spec's caps in a unit test with no model call.
- **Composable.** A supervisor that fans out to workers is just a spec that
  references other specs (below).

---

## Supervisor fan-out composition

For work that partitions - N chunks each handled independently, then merged -
compose specs: a **supervisor** spec dispatches to many **worker** specs, each
its own budgeted `run_tool_loop`, then reduces their results.

```python
class FanoutSpec(BaseModel):
    """A supervisor that maps a worker spec across a partition, then reduces.

    The worker/supervisor are real AgentSpecs, referenced not inlined. The caps
    that ONLY make sense at the fan-out level (how many workers run at once, how
    many re-dispatch rounds the supervisor gets) live HERE, never on a worker -
    a leaf spec has no business carrying an orchestration knob.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    worker: AgentSpec
    supervisor: AgentSpec
    pool_max_workers: int      # concurrency cap
    max_redispatch_rounds: int # bounded supervisor -> worker retries


def run_fanout(provider, guard, spec: FanoutSpec, partition: list[object]):
    """Each worker is its own guarded, budgeted loop. Total spend is bounded by
    (per-worker budget) x (worker count) - a knowable ceiling before you start,
    which is exactly what makes a fan-out safe to point at a customer tenant."""
    results = []
    for chunk in partition:                       # or a bounded thread pool
        r = run_tool_loop(
            provider, guard,
            subject=spec.worker.name,
            model=spec.worker.model_id,
            system=spec.worker.system_prompt,
            seed_messages=_seed_for(chunk),
            tools=spec.worker.tools,
            dispatch=_dispatch,
            terminal_tool=spec.worker.terminal_tool,
            validate_terminal=_validate,
            budgets=spec.worker.budgets(),          # FRESH budget per worker
            max_tokens=spec.worker.max_tokens,
        )
        results.append(r)
    return _reduce(spec.supervisor, results)
```

---

## What to remember

- **Cap first, spend second.** Reserve budget through the guard BEFORE the
  model call; the guard fails closed with a 429 so no tool runs on an
  overspent budget. That is the difference between a budget and an invoice.
- **Three caps, kept distinct** - turns, tool-calls (the side-effect budget),
  wall-time - plus a separate retry budget for transient-only errors.
- **N turns = N reservations.** Every turn is a real gate, metered to a durable
  ledger in micro-dollars with a usage row per call.
- **Graceful degrade returns None**, never a partial answer. `stop_reason`
  records why.
- **AgentSpec makes the loop's inputs data** - one reviewable, testable model
  card per agent; supervisor fan-out is specs referencing specs, with a
  knowable total-spend ceiling.
