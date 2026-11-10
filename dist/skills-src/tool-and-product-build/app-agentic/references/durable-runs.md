# Durable Runs - agent jobs that survive a closed tab and a restart

An agent loop (see `agent-loop.md`) can run for many minutes. No synchronous
HTTP request survives that: the browser tab times out, the user closes it, the
service redeploys mid-run. Durable runs are the pattern that makes a
multi-minute agent job outlive all three.

The shape in one line: **the endpoint returns a run id immediately (HTTP 202),
the agent works in the background, it heartbeats to Postgres as it goes, and a
service restart resumes any run whose heartbeat went stale.**

---

## READ THIS FIRST - the App Runner CPU-throttling constraint

The 202 + `BackgroundTasks` pattern below runs the agent **in the same container
after the response is sent**. On **AWS App Runner** (the platform in
app-hosting) that is a trap: App Runner **throttles a container's CPU to
near-zero whenever no HTTP request is actively being processed**
(https://aws.amazon.com/apprunner/faqs/). A detached 12-minute agent loop with
no in-flight request will stall or crawl, and a single throttled instance will
not reliably make progress. The heartbeat/resume machinery partially masks this
(a stalled run eventually looks interrupted and resumes) - but it resumes into
the same throttle, so it is not a fix.

Pick one before you rely on background runs on App Runner:

- **Keep an instance warm** - set App Runner min-size >= 1 AND keep a request in
  flight for the duration (a self-ping / keep-alive while a run is active). Works
  for modest, bounded runs; costs a warm provisioned instance (see
  app-hosting/references/operations.md for the cost tradeoff).
- **Offload the long run off the request-gated surface** (recommended for
  anything genuinely multi-minute): run the agent as an **ECS/Fargate task, AWS
  Batch job, or Step Functions execution**, with App Runner only creating the
  run row and kicking it off. The durable-run row + heartbeat + resume design
  below still applies - the WORKER just lives somewhere that gets steady CPU.

Everything below is correct once the worker runs somewhere with steady CPU. On a
platform that does NOT throttle idle CPU (a plain container, ECS/Fargate), the
in-process `BackgroundTasks` form is fine as-is.

---

## Why this pattern exists

Three things that WILL happen to a 12-minute job, and what each demands:

1. **The user closes the tab.** So the work cannot depend on the HTTP
   connection staying open. It must run detached, and status must live
   somewhere the user can re-attach to from a different tab, or a different
   machine, tomorrow. That "somewhere" is a database row, not server memory.
2. **The service restarts** (a deploy, a container recycle, a crash). So a run
   that was mid-flight must be detectable as interrupted and either resumed or
   honestly reported as failed - never left reading "running" forever while
   nothing is actually running.
3. **The user comes back and asks "is it done?"** So status must be a cheap
   read of durable state, servable by ANY instance of the service, not just the
   one that started the job.

A run stuck at "running" forever, and a run that is genuinely still working,
must not look identical. Making those two distinguishable is the entire job of
the heartbeat.

---

## The run lifecycle (states)

A small, explicit state machine. Store the status as a checked string, and
allow only named transitions - an illegal move is a lookup miss, not a
fall-through that quietly permits everything.

```
  QUEUED ---> RUNNING ---> SUCCEEDED   (terminal)
     |           |
     |           +-------> FAILED      (terminal)
     |           |
     +-----------+-------> CANCELLED   (terminal)
```

- **QUEUED** - the row is committed; the background work has not started.
- **RUNNING** - the work is executing and heartbeating.
- **SUCCEEDED** - finished; `result` holds the output.
- **FAILED** - finished; `error` holds an RFC 9457-shaped body. Includes the
  "interrupted" case (a distinct error type - the remedy differs: restart vs
  fix the input).
- **CANCELLED** - the user stopped it.

The three terminal states accept no further transition. That is what stops a
late-completing background task from resurrecting a run the stale-sweep (or the
user) already ended.

```python
from enum import StrEnum


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


_ALLOWED = {
    RunStatus.QUEUED:    frozenset({RunStatus.RUNNING, RunStatus.FAILED, RunStatus.CANCELLED}),
    RunStatus.RUNNING:   frozenset({RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.CANCELLED}),
    RunStatus.SUCCEEDED: frozenset(),
    RunStatus.FAILED:    frozenset(),
    RunStatus.CANCELLED: frozenset(),
}


def can_transition(current: RunStatus, target: RunStatus) -> bool:
    """Total: an unknown pairing is simply False. A terminal status accepts
    nothing - which is what keeps a zombie task from flipping a finished run."""
    return target in _ALLOWED.get(current, frozenset())
```

---

## The schema (generic)

One table. The comments are the design.

```python
from datetime import datetime
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB


class AgentRun(Base):
    __tablename__ = "agent_run"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Namespaced work identifier, e.g. "invoicerecon.synthesis". A string, not
    # an enum: a new job type is a new value, never a schema change - the
    # generic runner must not need to know its callers.
    kind: Mapped[str] = mapped_column(Text, nullable=False)

    # The owning aggregate (e.g. an engagement id) as opaque text. The
    # re-attach and cleanup key.
    subject_ref: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Who started it. The ONLY authorization key the poll route needs - a
    # caller reads their own runs, decidable without importing any module.
    principal_id: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(Text, nullable=False, default="queued")

    created_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # THE interrupted-run detector. Last time the work reported it was alive.
    # NULL until the first heartbeat; the staleness check falls back to
    # started_at so the gap between "marked running" and "first heartbeat" is
    # not misread as dead.
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Progress - a 12-minute wait needs more than a spinner, or the user
    # concludes it hung and starts a second expensive run.
    progress_current: Mapped[int | None] = mapped_column()
    progress_total:   Mapped[int | None] = mapped_column()
    progress_note:    Mapped[str | None] = mapped_column(Text)

    # Outcome: exactly one is set at terminal. `error` is RFC 9457-shaped so a
    # failed run surfaces like any other error on the platform.
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error:  Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Retention: set only when the run reaches terminal (an in-flight run has
    # no meaningful expiry). A background sweep deletes past this - a documented
    # expiry with nothing deleting it is not an expiry.
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # --- resume/lease columns (see "resuming orphans" below) ---
    owner_token: Mapped[str | None] = mapped_column(Text)   # which process owns it
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    attempt: Mapped[int] = mapped_column(default=1)         # fencing token, not a human knob

    __table_args__ = (
        # The re-attach query: "my in-flight runs of this kind for this subject".
        Index("ix_agent_run_lookup", "principal_id", "kind", "subject_ref"),
        # The sweep queries: stale detection + expiry.
        Index("ix_agent_run_status", "status"),
        Index("ix_agent_run_claimable", "status", "lease_expires_at"),
    )
```

---

## The route - return 202 + a run id, work in the background

The ordering here is load-bearing and NOT rearrangeable.

```python
from fastapi import APIRouter, BackgroundTasks, Depends

router = APIRouter()


@router.post("/api/v1/runs", status_code=202)
async def start_run(body: StartRunBody, tasks: BackgroundTasks, user=Depends(current_user), session=Depends(db)):
    """Create the row, return its id immediately, run the work AFTER the response.

    Ordering that makes durability work:
      1. Create the row in THIS request's session and commit it as part of the
         request. The 202 carries the id.
      2. Schedule the work with BackgroundTasks - Starlette runs it only AFTER
         the response is sent. This sequencing is load-bearing: scheduling the
         work inside the request would race the request's own commit, and the
         background task would find no row to mark RUNNING.
      3. The work opens its OWN db sessions - the request's session is closed by
         the time it runs.
    """
    run = await create_queued_run(
        session, kind=body.kind, principal_id=user.id, subject_ref=body.subject_ref,
    )
    await session.commit()   # (1) row is durable before the work looks for it

    tasks.add_task(execute_run, run.id, _build_work(body))  # (2) runs after the response
    return {"run_id": run.id}                                # 202 + id, immediately


@router.get("/api/v1/runs/{run_id}")
async def poll_run(run_id: uuid.UUID, user=Depends(current_user), session=Depends(db)):
    """Cheap durable read. A different service instance can serve this - status
    lives in Postgres, not in the instance that started the job.

    A run belonging to someone else is a 404, not a 403 - a 403 would confirm
    the id exists. Ownership is checked in the query, not as an after-the-fact
    filter a later refactor could silently drop.

    The REPORTED status is the EFFECTIVE one: a run whose heartbeat went stale
    reads FAILED (interrupted) even though the stored row still says RUNNING
    until the sweep catches up - otherwise a client spins forever on a run that
    died with its container.
    """
    row = await get_run(session, run_id)
    if row is None or row.principal_id != user.id:
        raise NotFound("no such run")
    return to_view(row, now=utcnow())   # applies effective_status()
```

**Make `start_run` idempotent.** An agent run is expensive - a double-click or a
client retry must not start two. Accept an `Idempotency-Key` header (or derive a
key from principal_id + subject_ref + kind), store it uniquely on the run row,
and on a repeat key return the EXISTING run's id (200/202) instead of creating a
second. Without this, the 202-returns-immediately design actively invites
double-submits.

---

## The runner - heartbeat, and record the outcome no matter what

`execute_run` runs detached, with nobody to catch an exception. So it must be
total: every exit path writes the row, or the run is stuck at RUNNING until the
sweep notices.

```python
async def execute_run(run_id, work):
    """Run `work`, heartbeating, and record the outcome. Never raises.

    Totality is the point: an escaped exception would leave the row RUNNING and
    lose the error that explains why. So success, failure, AND interruption each
    write the row."""

    async def report(*, current=None, total=None, note=None):
        """Heartbeat + optional progress. Swallows its own failure - a lost
        heartbeat is worth 12 minutes of work continuing on a blip. If
        heartbeats keep failing, the stale sweep fails the run, which is the
        honest outcome for work whose progress cannot be observed."""
        try:
            async with db_session() as s:
                await touch_heartbeat(s, run_id, now=utcnow(),
                                      current=current, total=total, note=note)
                await s.commit()
        except Exception:
            log.warning("heartbeat failed", extra={"run_id": str(run_id)})

    # Mark RUNNING (the one legal QUEUED -> RUNNING move). Missing/not-queued =
    # cancelled between the 202 and here; refusing to run is correct, not an error.
    async with db_session() as s:
        if await mark_running(s, run_id, now=utcnow()) is None:
            return
        await s.commit()

    try:
        result = await work(RunContext(run_id=run_id, report=report))
    except asyncio.CancelledError:
        # The restart path (a draining server cancels the background task). The
        # honest record is "interrupted", not "failed on its own merits" - the
        # remedy differs. Time-boxed + shielded so it never hangs shutdown; if
        # it cannot land, the stale sweep still recovers the run.
        await record_interruption(run_id)
        raise
    except Exception as exc:
        await record_failure(run_id, exc)   # the failure belongs on the row
        return

    async with db_session() as s:
        await mark_succeeded(s, run_id, result=result, now=utcnow(), ttl=DEFAULT_TTL)
        await s.commit()
```

The work is handed a `RunContext` with a `report` callback. Long steps should
report BETWEEN sub-steps, not only at stage boundaries - calling `report` is
what keeps the run out of the stale sweep.

```python
@dataclass(frozen=True, slots=True)
class RunContext:
    run_id: uuid.UUID
    report: Callable[..., Awaitable[None]]   # heartbeat + progress
```

---

## The restart story - resume orphaned runs

A "stale" run is one whose heartbeat is older than a threshold (sized well
above the slowest single step - e.g. 5 minutes). On startup, and on a periodic
tick, the service does two passes, IN THIS ORDER:

1. **Resume pass** - claim each orphaned RUNNING row this process can own, and
   re-dispatch its work.
2. **Stale-fail pass** - fail whatever could not be resumed (resume budget
   spent, or no way to rebuild the work).

Order matters and is not reversible: a terminal FAILED accepts no transition,
so a stale-fail that ran first would permanently poison a row the resume pass
would have rescued.

```python
async def resume_orphaned_runs(work_for):
    """Claim + re-dispatch every orphaned RUNNING row this process can own.

    A claim is atomic and fenced by owner_token + attempt: two instances racing
    to resume the same row, only one wins. attempt caps how many times a run may
    be resumed before the stale-fail pass is left to fail it - a run interrupted
    a third time is more likely meeting a repeatable problem than bad luck, and
    re-running it would spend tokens on a job that will not finish.

    A stale check in front of an expensive resume is one cheap SELECT - free
    next to a multi-dollar agent run."""
    now = utcnow()
    for run_id in await list_claimable_run_ids(now):
        attempt = await claim_run(run_id, owner_token=OWNER_TOKEN, now=now)
        if attempt is None:
            continue                       # another instance won the race
        row = await get_run(run_id)
        work = await work_for(row)         # rebuild the work for this kind
        if work is None:
            continue                       # cannot reconstruct - leave for stale-fail
        schedule_run(run_id, work, owner_token=OWNER_TOKEN, attempt=attempt)
```

`OWNER_TOKEN` is a fresh uuid minted once per PROCESS at startup - never a
hostname or instance id (two processes on one host must differ, and cloud
runtimes expose no stable instance identity). It is the lease owner the claim
records and the resumed run's writes are fenced against.

The generic runner cannot import a specific job's code, so the composition root
supplies `work_for(row) -> work | None`: a factory that rebuilds the work for a
given `kind`. Returning `None` for a kind it does not own is a REFUSAL, not an
error - a later pass (or the stale-fail) picks the row up.

---

## What to remember

- **202 + run id, then work in the background.** Commit the row in the request
  BEFORE scheduling the work, and schedule it to run AFTER the response - or the
  work races the commit.
- **Status lives in Postgres**, so any instance can serve the poll and the user
  can re-attach from any tab or machine. Poll answers "is it done?" as a cheap
  durable read; foreign runs 404.
- **The heartbeat is the whole point.** It is what makes "still working" and
  "died with its container" distinguishable. A stale heartbeat reads as FAILED
  on the effective-status projection, even before the sweep writes it.
- **The runner is total** - success, failure, and interruption each write the
  row; nothing escapes to leave a run stuck at RUNNING.
- **Restart = resume-then-fail, in that order.** Claim orphans with a
  process-minted owner token and a bounded attempt count; fail only what cannot
  be resumed. A terminal status is final, so the order is not negotiable.
