# Observability - the RUN phase (structured logs, alarms, agent tracing)

Deploy is not the finish line. Once the reference hosted-app architecture is
live behind the VPN, the question stops being "did it deploy" and becomes "is it
healthy right now, and when it is not, can I find out why in one read." This file
is the RUN-phase playbook: what to log, what to alarm on, and how to trace a
single multi-step agent run end to end.

It is the operational-excellence companion to the deploy references
(`aws-architecture.md`, `cloudformation-pipeline.md`, `deploy-runbook.md`) and the
agent-runtime references in `app-agentic` (`agent-loop.md` for the SpendGuard
ledger, `durable-runs.md` for run state). It reuses their vocabulary - `run_id`,
`stop_reason`, SpendGuard - rather than reinventing it.

Placeholders: `<APP_NAME>`, `<REGION=us-east-2>`, `<DEV_ACCOUNT_ID>`. Generic
examples only - no real account IDs, service URLs, or client names.

---

## Contents

1. Why observability is a first-class deliverable, not an afterthought
2. Structured JSON logging + the correlation id
3. CloudWatch log groups, metric filters, and the signals that matter
4. Alarms - the four that page, and why each
5. Tracing a multi-step agent run
6. On-call / alerting - the minimal note
7. Well-Architected Agentic AI Lens tie-in
8. What to remember

---

## 1. Why observability is a first-class deliverable, not an afterthought

An agentic tool is harder to operate than a plain CRUD app for one structural
reason: its behavior is stochastic. The same input can drive a different tool
sequence, a different token count, a different cost. The AWS Well-Architected
Agentic AI Lens states the consequence plainly - if you cannot trace a decision
end to end, you cannot debug, optimize, or audit it
(https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html).

So observability is designed in, not bolted on:

- A **plain 500** on a CRUD route is a bug you reproduce. A **runaway agent
  loop** is money and blast radius spent while you are still reading the logs -
  you need the alarm to fire before you go looking, not after.
- A multi-step run touches the model, several tools, Postgres, and maybe a
  customer tenant. When it fails, "which step, on whose behalf, spending what"
  must fall out of one query, not a cross-file reconstruction.
- Behind the VPN there is no public status page and no external synthetic
  monitor - the CloudWatch signals ARE the outside view.

---

## 2. Structured JSON logging + the correlation id

**Log JSON, not prose.** A human-readable log line (`"processing request for
user..."`) is unqueryable at 2am. A JSON object is: CloudWatch Logs Insights and
metric filters can select on its fields. Every log line is one flat JSON object
with a stable set of keys. (OWASP's Logging Cheat Sheet makes the same call -
log in a parseable, consistent, structured format:
https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html.)

**The correlation id is the spine.** One id is minted at the edge of every
request and threaded through every log line, every tool call, and - for an agent
job - the durable `run_id` from `durable-runs.md`. That id is what turns a pile
of independent log lines into a single traceable story. Without it you have
logs; with it you have a trace.

```python
# INVENTED illustration of the logging shape - not real platform code.
import json, logging, sys, time, uuid
from contextvars import ContextVar

# Set once per request in middleware; read anywhere downstream without
# plumbing it through every function signature.
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")


class JsonFormatter(logging.Formatter):
    """One flat JSON object per line. Fixed top-level keys so a metric filter
    can select on them; free-form detail goes under `extra`, never at the top
    level where it could collide with a reserved key."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,               # INFO / WARNING / ERROR
            "logger": record.name,
            "msg": record.getMessage(),
            "correlation_id": correlation_id.get(),  # THE spine - on every line
            "service": "<APP_NAME>",
            "env": getattr(record, "env", "-"),
        }
        if record.exc_info:
            payload["error_type"] = record.exc_info[0].__name__
        # Structured extras: run_id, principal_id, tool, stop_reason, etc.
        for k, v in getattr(record, "fields", {}).items():
            payload[k] = v
        return json.dumps(payload, separators=(",", ":"))


def configure_logging() -> None:
    h = logging.StreamHandler(sys.stdout)   # App Runner ships stdout to CloudWatch
    h.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [h]
    root.setLevel(logging.INFO)
```

```python
# The middleware that mints (or accepts) the correlation id per request.
async def correlation_middleware(request, call_next):
    # Honor an inbound id if one is present (an upstream caller may already have
    # opened the trace); otherwise mint one. Same header name in and out so a
    # client can quote it in a support ticket.
    incoming = request.headers.get("x-request-id")
    cid = incoming or uuid.uuid4().hex
    token = correlation_id.set(cid)
    try:
        response = await call_next(request)
    finally:
        correlation_id.reset(token)
    response.headers["x-request-id"] = cid   # echo it back so the user can cite it
    return response
```

**What to log - and what NOT to.** Log the shape of the work, never its
sensitive contents. Log `principal_id` (who), `run_id` (which job), `tool` name,
token counts, `stop_reason`, latency, and outcome. Do NOT log the JWT, the
`DATABASE_URL`, the full prompt/response bodies verbatim, or any customer PII
that rides through a tool - a log group is not an encrypted store, and a leaked
token in a log line is a leaked token. (OWASP: exclude credentials and sensitive
data from logs - same cheat sheet.) When you must log a model exchange for
debugging, log a hash or a truncated, PII-scrubbed summary, gated behind a debug
flag that is off in prod.

**KT note - why a ContextVar, not a function argument.** Threading a
`correlation_id=` parameter through every function is the naive fix, and it rots:
one refactor forgets to pass it and the trace breaks silently. A `ContextVar` is
set once at the edge and read anywhere, so the id is present by construction, not
by everyone remembering.

---

## 3. CloudWatch log groups, metric filters, and the signals that matter

App Runner writes two log streams to CloudWatch automatically:

- **Service logs** - App Runner's own lifecycle events (deployments, health
  checks, scaling).
- **Application logs** - whatever your container writes to stdout/stderr (the
  JSON above).

Keep one log group per service per environment, e.g.
`/aws/apprunner/<APP_NAME>-dev/.../application`. Set an explicit retention on it
(a log group defaults to never-expire, which quietly accrues cost forever) - 30
to 90 days for app logs is a sane default; longer only where audit requires it.

**Metric filters turn a log pattern into a number you can alarm on.** CloudWatch
cannot alarm on raw log text; it alarms on metrics. A metric filter scans the log
group for a JSON pattern and emits a CloudWatch metric each time it matches
(https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/MonitoringLogData.html).
Because the app logs structured JSON, the filter patterns are precise - they
select on fields, not on fragile substring matches.

| Signal you want | Metric filter pattern (JSON) | Emits |
|---|---|---|
| Agent run failures | `{ $.stop_reason = "provider_error" \|\| $.stop_reason = "terminal_rejected" }` | `AgentRunFailures` count |
| Budget refusals (429) | `{ $.event = "budget_exceeded" }` | `BudgetRefusals` count |
| Interrupted durable runs | `{ $.event = "run_interrupted" }` | `RunInterruptions` count |
| Unhandled 500s | `{ $.level = "ERROR" && $.http_status = 500 }` | `AppErrors` count |

Two metric SOURCES, used together:

- **App Runner's own CloudWatch metrics** (namespace `AWS/AppRunner`) - published
  without any filter: `5xxStatusResponses`, `4xxStatusResponses`,
  `RequestLatency`, `Requests`, `Concurrency`, `ActiveInstances`, plus
  `CPUUtilization` / `MemoryUtilization`
  (https://docs.aws.amazon.com/apprunner/latest/dg/monitor-cw.html). These are
  the infrastructure view - the platform reporting on itself.
- **Your metric filters** over the application log group - the application view -
  agent failures, budget burn, business-level errors the platform cannot see.

You alarm on both. The platform metrics catch "the service is unhealthy"; the
filter metrics catch "the service is up but the agents are misbehaving."

---

## 4. Alarms - the four that page, and why each

An alarm you would not act on is noise that trains you to ignore the ones that
matter. Keep the paging set small and each one tied to a real remedy. Point every
alarm at an SNS topic (reuse the `ApproveProd` notification wiring from
`cloudformation-pipeline.md`); an alarm with no `AlarmActions` is a dashboard
widget, not an alert
(https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html).

| # | Alarm | Fires on | Why it pages / first move |
|---|---|---|---|
| 1 | **App Runner 5xx / health** | `5xxStatusResponses` over threshold in N min, OR App Runner health check failing (service not RUNNING) | The service itself is broken or wedged. Check the deploy just rolled; consider a rollback (see `operations.md`). A failing `/health` means the container is not answering `200` on `:8080` - see `deploy-runbook.md` s3. |
| 2 | **Latency** | `RequestLatency` p90 over threshold sustained | Users are timing out (App Runner hard-caps a request at 120s). Often a slow model call or a stalled DB query; correlate by `correlation_id`. |
| 3 | **Agent failure rate** | `AgentRunFailures` per interval over threshold | The agents are failing even though the service is up (a bad prompt change, a downstream tool down, a Bedrock throttle). Read the failing runs' `stop_reason`. |
| 4 | **SpendGuard budget burn** | `BudgetRefusals` spiking, OR a derived spend-rate metric crossing a soft ceiling BEFORE the hard cap | Money is being spent fast. The SpendGuard hard cap (`agent-loop.md`) fails the call closed at the limit; THIS alarm warns you at, say, 70% of budget so a human looks before the cap starts refusing real work. |

**Why a soft budget alarm in front of the hard cap.** The SpendGuard cap is a
gate - it stops spend at 100%. But by the time the cap is refusing calls, users
are already hitting 429s. A CloudWatch alarm on the spend RATE (or on
`BudgetRefusals` starting to appear) is the early-warning smoke detector: it lets
a human decide "raise the cap" or "something is looping" while there is still
budget left to serve legitimate work. The cap protects the wallet; the alarm
protects the user experience. Keep both.

**Tune thresholds against a baseline, not a guess.** Run for a week, read the
normal p90 latency and normal daily spend, then set thresholds a clear margin
above normal. A threshold set from imagination either never fires or cries wolf.

---

## 5. Tracing a multi-step agent run

A CRUD 500 is one log line. An agent run is a dozen: the model call, each tool
dispatch, the budget reservations, the durable-run heartbeats. Tracing is the
discipline that lets you replay that dozen in order, for ONE run, from a single
query.

**The mechanism is the correlation id joined to `run_id`.** Every line a run
emits carries both. So the trace is one Logs Insights query:

```
# CloudWatch Logs Insights - the whole story of one run, in order.
fields ts, level, msg, tool, stop_reason, tokens, latency_ms
| filter run_id = "0f8c...e21"      # or: correlation_id = "<the id the user quoted>"
| sort ts asc
```

Log these span-boundary events so the trace is legible without a full tracing
backend:

```python
# At each meaningful step, one structured line keyed to the run.
log.info("tool.start", extra={"fields": {
    "run_id": str(run_id), "tool": name, "turn": budgets.turns_used}})
# ... run the tool ...
log.info("tool.end", extra={"fields": {
    "run_id": str(run_id), "tool": name,
    "latency_ms": elapsed_ms, "ok": ok}})

# At loop exit - the single most useful line for debugging an agent.
log.info("run.finished", extra={"fields": {
    "run_id": str(run_id),
    "stop_reason": budgets.stop_reason,      # submitted / budget / max_turns / ...
    "turns_used": budgets.turns_used,
    "tool_calls_used": budgets.tool_calls_used,
    "est_cost_micros": spent_micros}})
```

`stop_reason` (from `agent-loop.md`) is the field that most often answers "why
did this run behave this way" without reading the whole trace: `budget` means the
cap fired, `max_turns` means it churned without converging, `terminal_rejected`
means it kept producing an invalid answer, `submitted` means it succeeded.

**When to graduate to real distributed tracing.** The JSON-log-plus-correlation-id
approach is the right first rung and is enough for a single service. When the
platform grows to multiple services calling each other (a supervisor service
fanning out to workers, or an MCP server calling downstream tools), graduate to
OpenTelemetry spans exported to an OTel-compatible backend - CloudWatch is one.
The Agentic AI Lens builds tracing into the spec via W3C Trace Context keys
(`traceparent`, `tracestate`) carried in request metadata, so a trace crosses
service boundaries
(https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html).
Propagate the same id you already mint as the correlation id into `traceparent`
and the two models line up rather than fork.

---

## 6. On-call / alerting - the minimal note

You do not need a full incident-management program for an internal tool. You do
need the smallest thing that guarantees an alarm reaches a human who can act:

- **One SNS topic per environment, subscribed by the owning team** (email or a
  chat webhook). All four alarms publish to it. Confirm the subscription (AWS
  requires the click) - see the `ApprovalEmail` note in `deploy-runbook.md`.
- **A one-page runbook link in every alarm description.** The alarm's own
  description field should say what it means and the first move (a link to the
  relevant `operations.md` / `deploy-runbook.md` section). The person paged at
  2am should not have to reconstruct context.
- **Separate dev and prod topics.** A dev alarm should never wake anyone; a prod
  alarm should. Same alarm definitions, different SNS topics, different
  subscribers - the two-account split (`cloudformation-pipeline.md`) already
  gives you the separation.
- **Escalate on health + spend only.** 5xx/health (alarm 1) and budget burn
  (alarm 4) are the two that justify interrupting someone. Latency and agent
  failure rate can be next-business-day for an internal tool unless they are also
  taking the service down.

---

## 7. Well-Architected Agentic AI Lens tie-in

The RUN-phase practices above map directly onto the operational-excellence
guidance in the AWS Well-Architected Agentic AI Lens
(https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentic-ai-lens.html):

| Lens operational-excellence theme | How this platform satisfies it |
|---|---|
| Make every agent action observable / traceable end to end | Structured JSON logs keyed by `correlation_id` + `run_id`; span-boundary events per tool call and at loop exit (s2, s5). |
| Behavioral monitoring | Metric filters on `stop_reason` and budget events plus alarms on agent failure rate and spend burn - the "up but misbehaving" signals platform metrics miss (s3, s4). |
| Tracing + anomaly dashboards | App Runner + application metrics on one CloudWatch dashboard; graduate to W3C Trace Context / OpenTelemetry when the platform becomes multi-service (s5). |
| Human-in-the-loop governance | The SpendGuard hard cap fails closed (`agent-loop.md`); the soft budget alarm brings a human in BEFORE the cap starts refusing legitimate work (s4). |

The Lens's framing is the "why" behind the small paging set: because agents are
stochastic, a system that lacks structured logging, tracing, behavioral
baselines, and anomaly detection cannot diagnose a failure before it cascades.
The four alarms and the correlation-id trace are that baseline in its minimal,
internal-tool form.

---

## 8. What to remember

- **Log JSON, thread a correlation id through everything.** One id, minted at the
  edge, joined to the durable `run_id`, on every line - that is what makes a
  trace out of a log pile. Never log tokens, DSNs, JWTs, or customer PII.
- **Two metric sources, alarmed together.** App Runner's own `AWS/AppRunner`
  metrics (5xx, latency, active instances) for the infra view; metric filters
  over your JSON logs for the "up but misbehaving" view.
- **Four alarms that page, each with a remedy:** 5xx/health, latency, agent
  failure rate, budget burn. A soft budget alarm sits IN FRONT of the SpendGuard
  hard cap so a human looks before real work starts getting refused.
- **Trace a run with one query** keyed on `run_id`; `stop_reason` usually answers
  "why" without reading the whole trace. Graduate to OpenTelemetry / W3C Trace
  Context when the platform goes multi-service.
- **Minimal on-call:** one SNS topic per environment, dev never pages, every
  alarm description links its runbook step. Escalate on health and spend.
