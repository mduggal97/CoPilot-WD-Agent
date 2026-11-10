# Operations - migration safety, prod rollback, run cost / TCO

The tail of the deploy story: the three things you must have a written answer for
BEFORE the reference hosted-app architecture carries real work - how a schema
change fails safe, how you undo a bad prod release, and what the running platform
costs per month. Each has a non-obvious trap baked into the platform's own shape,
so each gets a concrete answer here rather than a hand-wave.

Read `cloudformation-pipeline.md` and `deploy-runbook.md` first - this file
assumes the two-account, dev-immutable / prod-mutable pipeline and the
`alembic upgrade head` Migrate/MigrateProd stages. It reuses their vocabulary.

Placeholders: `<APP_NAME>`, `<REGION=us-east-2>`, `<DEV_ACCOUNT_ID>`,
`<PROD_ACCOUNT_ID>`. Generic examples only - no real account IDs, image URIs,
service URLs, or client names.

---

## Contents

1. Migration safety - expand-contract or you break prod on rollback
2. RDS backups + PITR - the real safety net under migrations
3. Prod rollback - retag the previous good image to :latest
4. Hosted-app run cost / TCO - a pre-build sizing approach
5. The App Runner CPU-throttle trap (interacts with min-size cost)
6. A generic monthly-cost worksheet
7. What to remember

---

## 1. Migration safety - expand-contract or you break prod on rollback

**The hazard, stated exactly.** The pipeline runs `alembic upgrade head` in the
Migrate (dev) and MigrateProd stages, and MigrateProd runs BEFORE DeployProd -
so the schema is always migrated ahead of the new image (see
`cloudformation-pipeline.md` s3). That ordering is correct, but it creates a
one-way trap: **the migration lands first and is not automatically rolled back if
the deploy is bad.** If a migration is destructive (drops or renames a column,
tightens a constraint), then the moment it runs, the CURRENTLY-RUNNING old image
- which still expects the old schema - can start throwing errors, and a rollback
to that old image cannot fix it because the schema it needs is already gone.

**The rule: migrations must be strictly additive within a release.** Never
combine a schema change and the code that depends on it destructively in one
release. Split every breaking change across releases using expand-contract (also
called parallel-change): add the new shape first, move traffic onto it, and only
remove the old shape in a LATER, separate release once nothing reads it.

**Expand-contract, concretely.** Say you want to split a single `full_name`
column into `first_name` / `last_name`.

```
Release 1 - EXPAND (purely additive; old code still works)
  - Migration: add first_name TEXT NULL, add last_name TEXT NULL.
    Both NULLABLE. A NOT NULL column with no default breaks every INSERT the
    still-running old image issues, so new columns are ALWAYS nullable at birth
    (Alembic op.add_column with nullable=True:
    https://alembic.sqlalchemy.org/en/latest/ops.html).
  - Code: new image writes BOTH the old full_name AND the new columns
    (dual-write), and still READS full_name. Old image, if still running,
    ignores the new columns harmlessly. This release is safe to roll back - the
    old schema shape is untouched.

Release 2 - MIGRATE DATA + SWITCH READS
  - Backfill: a one-off/idempotent job populates first_name/last_name from
    full_name for existing rows. Run it as data, not as a blocking DDL step.
  - Code: new image now READS first_name/last_name; still dual-writes full_name
    as a safety belt. Rollback is still safe - full_name is still current.

Release 3 - CONTRACT (the destructive step, alone, later)
  - Only after Release 2 is proven in prod and you are confident you will not
    roll back past it: drop full_name (and stop writing it).
  - This is the ONLY release that is unsafe to roll back across, which is exactly
    why it is isolated - a rollback now would go back to code that needs the
    dropped column. By the time you ship it, that risk is deliberate and small.
```

The discipline in one line: **add nullable/new first, backfill, switch reads,
drop later in a SEPARATE release.** Each individual release is rollback-safe;
only the final contract step burns a bridge, and it does so alone and on purpose.

**Why this matters MORE on this platform.** Prod has no automatic
schema-plus-image atomic rollback (see s3 - prod rolls a mutable `:latest` image,
and migrations already ran). Expand-contract is what makes each release
independently reversible so that an image rollback is actually a safe move
instead of a move into a schema that no longer matches.

---

## 2. RDS backups + PITR - the real safety net under migrations

Expand-contract keeps you from NEEDING to undo a migration. RDS backups are what
you fall back on when a migration or a bad job corrupts data anyway - the real
safety net, not the discipline.

- **Automated backups are on and retained.** RDS takes daily snapshots and
  continuously ships transaction logs; set a deliberate backup retention period
  (1 - 35 days; 7 is a reasonable default for an internal tool)
  (https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.BackupRetention.html).
  A retention of 0 DISABLES automated backups - never set it to 0 on a
  data-backed environment.
- **Point-in-time recovery (PITR).** With automated backups on, you can restore
  to any second within the retention window; RDS uploads transaction logs to S3
  about every 5 minutes, so worst-case recovery granularity is a few minutes
  (https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html). PITR
  restores to a NEW instance - it does not overwrite the live one - so the
  recovery move is: restore to a new instance at a timestamp just before the bad
  change, verify, then repoint `DATABASE_URL` (the Secrets Manager secret from
  `deploy-runbook.md`) at it.
- **Take a manual snapshot before a known-risky migration.** For a migration you
  are nervous about (a large backfill, a constraint tightening), snapshot the
  prod DB immediately before the release. It is a named, retained restore point
  that does not age out with the automated retention window.

KT note: PITR is a floor, not a plan. Restoring prod to a point in time loses
every write since that point - it is the break-glass option. Expand-contract (s1)
is what keeps you from ever pulling the glass. Have both; reach for the discipline
first.

---

## 3. Prod rollback - retag the previous good image to :latest

**Why prod rollback is not "redeploy the previous SHA."** Dev pins an IMMUTABLE
`:<git-sha>` image and deploys with `update-service`, so a dev rollback is
"point the service at the previous SHA." Prod cannot do that. The org-wide SCP
denies `apprunner:UpdateService` in the prod account, so prod runs a MUTABLE
`:latest` tag and deploys with `start-deployment` only (see
`cloudformation-pipeline.md` s5). `start-deployment` redeploys whatever `:latest`
currently points at - it has no "deploy that other image" parameter. So there is
no prior-SHA redeploy in prod. The rollback path has to MOVE the `:latest` tag.

**The runbook: retag the previous good image to :latest, then start-deployment.**

```
PROD ROLLBACK - <APP_NAME>, prod account <PROD_ACCOUNT_ID>, <REGION=us-east-2>

Precondition: you know the digest of the last-good prod image. Every promotion
pushed the tested bytes to prod ECR; the previous good image is still in the
repo (it was overwritten as a TAG, not deleted as an IMAGE - the digest persists).
Find it from the ECR image list / push history, or from the pipeline execution
that promoted it.

1. AUTH: assume the prod deploy role in <PROD_ACCOUNT_ID> (SSO + MFA; human step).
     aws sts get-caller-identity   # confirm <PROD_ACCOUNT_ID>

2. RETAG the previous good image to :latest (no rebuild - reuse the exact bytes).
   Pull the manifest by its digest and re-put it under the :latest tag:
     MANIFEST=$(aws ecr batch-get-image \
       --repository-name <APP_NAME>-prod \
       --image-ids imageDigest=sha256:<PREV_GOOD_DIGEST> \
       --query 'images[0].imageManifest' --output text)
     aws ecr put-image \
       --repository-name <APP_NAME>-prod \
       --image-tag latest \
       --image-manifest "$MANIFEST"
   # :latest now points at the previous good image's bytes.

3. START-DEPLOYMENT on the prod App Runner service (NOT update-service - the SCP
   denies it; update-service surfaces as a misleading iam:PassRole error).
     aws apprunner start-deployment --service-arn <PROD_SERVICE_ARN>

4. POLL to RUNNING, then smoke-test over the VPN:
     GET /health            -> 200 {"status":"ok"}
     GET /api/v1/auth/config-> 200 with PROD's client id
     the failing feature    -> now serving the rolled-back behavior

5. SCHEMA CHECK (the load-bearing caveat). This rolls the IMAGE only; it does NOT
   un-run MigrateProd. It is safe ONLY if the release you are rolling back from
   was expand-contract-additive (s1), so the previous image still matches the
   migrated schema. If the bad release included a DESTRUCTIVE migration, an image
   rollback is NOT enough - you also need a data restore (s2, PITR / snapshot).
```

**The two traps to know going in:**

- **Do not chase `iam:PassRole` in prod.** If step 3 is attempted with
  `update-service` it fails as a PassRole AccessDenied - that is the SCP denying
  `UpdateService`, not a missing grant. Granting PassRole does nothing. Use
  `start-deployment`. (Full explanation: `cloudformation-pipeline.md` s5.)
- **`:latest` being mutable is what makes this both possible and dangerous.**
  Possible: you can move the tag back. Dangerous: whoever holds prod ECR push can
  change what prod runs by moving a tag - so prod ECR push is tightly scoped to
  the pipeline's cross-account deploy role, and a manual retag like the above is a
  deliberate break-glass action, logged and done by a human.

**KT note - keep a few prior prod images.** Set the prod ECR lifecycle policy to
RETAIN the last several images (do not expire aggressively), or a rollback has no
previous digest to retag to. An over-eager "delete untagged after 1 day" policy
quietly removes your rollback targets.

---

## 4. Hosted-app run cost / TCO - a pre-build sizing approach

Size the monthly run cost BEFORE you build, so the number is a design input, not
a surprise on the first invoice. The platform has three cost centers: App Runner
(compute), RDS (the shared database), and Bedrock (model spend). LOE / build-hours
are a SEPARATE estimate - cross-link `wd-estimate` for the effort side; this is
the running-infrastructure side.

Note up front: App Runner is closed to NEW AWS customers as of the 2025
availability change, though existing accounts continue to use it
(https://docs.aws.amazon.com/apprunner/latest/dg/monitor-cw.html). The reference
architecture already runs on it; a brand-new account may need an ECS/Fargate
equivalent, and the same sizing logic below transfers.

### App Runner (compute) - provisioned vs on-demand, and min-size

App Runner bills two things differently, and understanding the split is the whole
game (https://aws.amazon.com/apprunner/pricing/,
https://docs.aws.amazon.com/apprunner/latest/dg/manage-autoscaling.html):

- **Provisioned instances** - the reserve kept ready to serve. You pay for their
  MEMORY, per GB-hour, whenever they exist. Their CPU is throttled while idle
  (see s5), so you are NOT paying for active CPU on them.
- **Active instances** - the subset actually processing requests right now. You
  pay for their CPU (per vCPU-hour) on top of the memory.

Quoting the docs directly: "You pay for the memory usage of all the provisioned
instances. You pay for the CPU usage of only the active subset"
(https://docs.aws.amazon.com/apprunner/latest/dg/manage-autoscaling.html).

The lever that most affects cost is **min-size** (minimum provisioned instances):

| min-size | Behavior | Cost effect |
|---|---|---|
| 0-effectively (scale to a single idle provisioned instance) | Default: App Runner keeps one CPU-throttled provisioned instance warm; near-zero cold-start | You pay memory for one warm instance 24x7; CPU only when serving |
| `>= 1` (explicit floor of 1+) | At least this many provisioned instances ALWAYS exist | Higher steady memory cost - you are paying to keep N instances warm around the clock |

**When to raise min-size >= 1:** when cold-start latency matters, OR - critically
for an agentic tool - when the app must do BACKGROUND work between requests (see
s5; a durable agent run continuing after the HTTP response). A higher min-size
keeps an instance warm and un-throttled enough to make that viable, but it costs
more, every hour, whether or not anyone is using the tool. Size it to real
concurrency (App Runner max-concurrency x expected peak instances), not to a
round number.

### RDS (the shared database) - instance + storage

The reference architecture uses ONE shared RDS Postgres instance per environment,
schema-per-module (`aws-architecture.md`) - so the database cost is shared across
all modules, not per-app. Two components:

- **Instance** - per-hour by instance class, running 24x7 (a database is not
  scale-to-zero). This usually dominates the RDS bill. Multi-AZ roughly doubles
  it - worth it for prod, often skippable for dev.
- **Storage** - per GB-month of allocated storage, plus backup storage beyond the
  free allotment (backups up to the size of the DB are typically free; retention
  and manual snapshots beyond that are billed). PITR's transaction-log storage
  rides along with automated backups (s2).

Because RDS is shared, allocate its cost across the tools that use it rather than
charging it wholly to the first app - the schema-per-module design is what makes
that allocation clean.

### Bedrock (model spend) - the variable, per-run cost

Model spend is the one cost that scales with USAGE, not with uptime: per input +
output token, per model. This is exactly what SpendGuard meters to the ledger and
caps (`app-agentic/agent-loop.md`). For sizing, do NOT invent token prices -
pull the current per-model rate and multiply by an estimated tokens-per-run x
runs-per-month. Cross-link:

- The SpendGuard ledger already records micro-dollars per call - once live, it IS
  your Bedrock cost telemetry; the observability soft-budget alarm
  (`observability.md` s4) warns before the cap.
- The hard cap is your guaranteed ceiling: monthly Bedrock spend cannot exceed
  (per-subject weekly cap) x (subjects) x (weeks) by construction. That makes the
  worst case a KNOWN number, which is what makes the worksheet's Bedrock row
  bounded rather than open-ended.

---

## 5. The App Runner CPU-throttle trap (interacts with min-size cost)

This is the correctness point that ties the cost lever (s4 min-size) to the
agent-runtime design, and it is easy to get wrong.

**App Runner throttles a container's CPU to near-zero when it is not processing
an HTTP request.** App Runner is request-driven: outside the handling of an active
request, a provisioned instance is CPU-throttled (that is precisely why you pay
only memory, not CPU, for the provisioned reserve - s4). The runtime is designed
around stateless request/response - "no state persists beyond the duration of
processing a single incoming web request"
(https://docs.aws.amazon.com/apprunner/latest/dg/develop.html).

**The consequence for background work.** A durable agent run
(`app-agentic/durable-runs.md`) returns HTTP 202 immediately and keeps working
in the background AFTER the response is sent. On App Runner, the CPU that
background task needs can be throttled away the instant the originating request
completes - so the "background" work stalls or crawls unless something keeps the
instance active. Three ways to make background agent work actually run:

| Approach | How it keeps the CPU alive | Cost / tradeoff |
|---|---|---|
| **min-size >= 1 + keep-alive** | Keep >=1 provisioned instance and drive enough activity (a lightweight internal keep-alive / steady request pressure) that an instance stays active while the job runs | Simplest to keep in App Runner; costs more (steady warm instances) and is fragile - a long job on a bursty service can still get throttled between requests |
| **Offload to Fargate / AWS Batch** | Run the long job as a separate container task that owns its own CPU for its whole lifetime | Clean separation; the right answer for minutes-long agent runs. More infra to wire |
| **Orchestrate with Step Functions** | A state machine drives the steps; each step is a short task that fits the request model or runs on Fargate | Best for multi-step, resumable pipelines; most infra |

**The design rule:** App Runner is excellent for the request/response API and for
SHORT agent loops that finish inside a request. For genuinely long-running
background agent work, either commit to min-size >= 1 with keep-alive (and pay for
it, and accept the fragility) OR offload the long work to Fargate / Batch / Step
Functions. Do NOT assume a fire-and-forget background task keeps running at full
speed on a default App Runner service - it will get throttled between requests.
This is the same tradeoff the s4 min-size lever describes, seen from the runtime
side: paying to keep an instance warm is not just a cold-start question, it is
what makes between-request work possible at all.

KT note: this interacts with `durable-runs.md`'s restart/resume story. Even with
min-size >= 1, a deploy or recycle still interrupts an in-flight run - which is
exactly why durable runs heartbeat to Postgres and resume orphans. Throttling and
restarts are two different reasons the same job can stall; the durable-run pattern
handles restarts, min-size/offload handles throttling. You need both.

---

## 6. A generic monthly-cost worksheet

Fill this before build with your own environment's rates (pull current App Runner,
RDS, and Bedrock prices for `<REGION=us-east-2>` - do not hardcode figures that
drift). Shape, not real numbers:

```
MONTHLY RUN COST - <APP_NAME>, <env>, <REGION=us-east-2>

APP RUNNER (compute)
  provisioned memory   = min_size_instances x mem_GB x $/GB-hr x 730 hr
  active CPU           = avg_active_instances x vCPU x $/vCPU-hr x active_hours
  active memory (add'l over provisioned, if active > provisioned)
  --> raise min_size only if cold-start OR background work requires it (s5)

RDS (shared - allocate a share to this app)
  instance             = instance_class $/hr x 730 hr   (x2 if Multi-AZ, prod)
  storage              = allocated_GB x $/GB-month
  backups/PITR         = billed backup storage beyond the free (~DB-size) allotment
  --> divide across the modules sharing the instance (schema-per-module, s4)

BEDROCK (model spend - usage-scaled, capped)
  per run              = (in_tokens x $/in-token) + (out_tokens x $/out-token)
  monthly              = per_run x runs_per_month     (by model: Haiku/Sonnet/Opus)
  ceiling              = SpendGuard weekly cap x subjects x ~4.3 weeks  (hard max)
  --> live actuals come from the SpendGuard ledger once running (agent-loop.md)

OTHER (usually small)
  CloudWatch logs      = ingested_GB x $/GB + retained_GB x $/GB-month
                         (set log retention - observability.md s3 - or this creeps)
  Secrets Manager      = secrets x $/secret-month
  ECR storage          = stored_GB x $/GB-month (keep a few prior prod images, s3)

MONTHLY TOTAL (per env) = App Runner + RDS-share + Bedrock + Other
Remember: dev and prod are separate accounts - size BOTH. Dev can skip Multi-AZ
and run min_size lean; prod carries the availability cost.
```

For the LOE / build-hours side of the estimate (design, build, test, deploy
effort by role and phase), cross-link `wd-estimate` - this worksheet is
running-infrastructure cost only, not the cost to build.

---

## 7. What to remember

- **Migrations must be additive per release (expand-contract):** add nullable/new
  first, backfill, switch reads, drop later in a SEPARATE release. MigrateProd
  runs before DeployProd and is not auto-undone, so a non-additive migration
  makes an image rollback unsafe.
- **RDS automated backups + PITR are the real safety net** (restore to a new
  instance at a timestamp, repoint `DATABASE_URL`); snapshot before a risky
  migration. The discipline (expand-contract) keeps you from needing the net.
- **Prod rollback = retag the previous good image to :latest + start-deployment**
  - there is no prior-SHA redeploy in prod (SCP denies `UpdateService`). Keep
    prior prod images in ECR or there is nothing to retag. It rolls the image
    only, NOT the schema.
- **App Runner throttles CPU to near-zero between requests** - background agent
  work stalls unless min-size >= 1 + keep-alive, or the work is offloaded to
  Fargate / Batch / Step Functions. This is the runtime face of the min-size cost
  lever, and it is separate from (and additional to) the durable-run restart
  story.
- **Size run cost before build across App Runner + shared RDS + capped Bedrock;**
  the SpendGuard hard cap makes the Bedrock worst case a known number. LOE is a
  separate estimate - see `wd-estimate`.
