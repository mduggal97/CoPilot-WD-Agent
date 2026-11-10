# Adoption measurement

Adoption is an outcome you measure, not a hope. This reference defines the metrics and the measurement
program; the post-go-live feedback loop that ACTS on them belongs to wd-post-go-live (adoption-and-feedback.md).

## The measurement arc

- **Baseline at discovery.** Capture the current-state numbers you intend to move (cycle time, error rate,
  manual-effort hours, satisfaction) alongside wd-discovery's outcome metrics. No baseline = no adoption story.
- **Target at design sign-off.** Lock the target values with the sponsor when the design doc's KPI table is
  signed (wd-design-doc). A target nobody agreed to is not a target.
- **Track through hypercare and beyond.** Report actuals vs. baseline/target at 30/60/90 days
  (wd-post-go-live value-capture.md), then at QBRs.

## What to measure (leading vs. lagging)

- **Leading indicators (are people using it, now):** active users vs. eligible users, task/transaction volume
  vs. the expected volume (from the Volumes Questionnaire), % of transactions done in the new system vs. the
  old/workaround, feature-usage spread, training completion, and support-ticket rate/topics.
- **Lagging indicators (did it produce the outcome):** the business KPIs from the baseline - cycle time,
  error/rework rate, manual-effort reduction, and user satisfaction (CSAT/pulse; the CSAT definition is owned
  by wd-post-go-live value-capture.md).
- **Adoption-quality signals:** are people using it *correctly* (rework, override rates, data-quality errors)
  - high usage with high error means training or design needs a fix, not celebration.

## How to read the numbers

- **Low usage during hypercare is a Sev2-equivalent finding** (wd-post-go-live), not a "give it time" - route
  it like a defect: find the cause (access gap, training gap, a clunky step, a live workaround) and fix it.
- **Segment by the stakeholder groups** from the change-impact assessment - an average hides the one High-impact
  population that is struggling. Report adoption per group, not just program-wide.
- **Close the loop to the plan:** a group with low usage or high error becomes the next comms theme, a targeted
  job aid (wd-kt), or a readiness re-check - measurement feeds the plan, it does not just decorate a status slide.

## Where the data comes from

For a Workday Extend/O4I app, the usage numbers are readable from the tenant itself (login/usage reports,
transaction/BO counts, orchestration run logs) - the same reads wd-post-go-live's hypercare monitoring uses
(wd-extend-dev references/tenant-ops.md). Keep production person-level data aggregate per the AI/data
governance rule (wd-extend-lifecycle references/ai-data-governance.md). Put the recurring adoption read on the
hypercare monitoring runbook so it is captured every day, not reconstructed at the QBR.

## Where this goes

Metric definitions + targets -> the design doc KPI table (wd-design-doc) and the value-capture baseline
(wd-post-go-live). Ongoing actuals -> wd-post-go-live (value check-ins, QBR, renewal narrative). Adoption gaps
-> back into this skill's comms/training plans as the next intervention.
