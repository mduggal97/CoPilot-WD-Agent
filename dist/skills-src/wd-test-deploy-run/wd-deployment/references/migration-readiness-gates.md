# Migration Readiness Gates - wave go/no-go for a phased data conversion

A wave-by-wave readiness scorecard that sits ON TOP of the conversion build and the
cutover plan and returns a defensible go/no-go per wave. It does not do the loading or the
cutover; it gives each wave one verdict - Pass / Conditional Pass / Fail - with named
blockers, so "are we ready to move this wave" is answered by evidence, not by feel.

Sits on top of the conversion BUILD (wd-extend-dev `data-conversion.md`) and hands a clean
gate to `cutover-planning.md`. Each gate returns one verdict; the **reconciliation harness**
(the one built once and reused every cycle in `data-conversion.md`) supplies the evidence.
Run at the END of each wave, before UAT sign-off, and at cutover go/no-go.

## The gates

Adapt the wave count to the program; the ordering and the mandatory items are the point.

1. **Profile.** Source profiled + extract repeatable + scope baselined.
2. **Transform.** Transform rules validated + first load run, count variance < the agreed
   threshold.
3. **Reconcile.** Reconciliation passed + data quality >= threshold + zero P0 open.
4. **Business rules.** Business rules + referential integrity hold + SME sign-off on a
   reviewed sample.
5. **Volume.** FULL-volume load + within SLA. A partial-volume load can never pass this
   gate.
6. **Rehearsal.** Dress rehearsal in a prod-equivalent tenant + ROLLBACK TESTED (not just
   documented).
7. **UAT.** Business users executed the tests themselves + signed acceptance.
8. **Cutover.** All prior gates formally passed + rollback DECISION POINT (time + trigger)
   agreed in advance + a named client decision-maker.

## Verdict rules (per gate)

- Any mandatory item unmet -> **Fail**.
- All mandatory met, 1-2 advisory gaps -> **Conditional Pass** (name the conditions + their
  owners).
- All met -> **Pass**.

## Standing disciplines (each has cost someone a slipped go-live)

- **THRESHOLD BEFORE THE GATE.** The data-quality %, count-variance %, and completeness bar
  are agreed BEFORE the results are seen - never tuned after seeing the numbers.
- **CONDITIONS CARRY FORWARD.** A Conditional Pass lets the wave proceed with named
  conditions due before the NEXT gate. Any still open at the next review makes that gate
  START as a Fail.
- **ROLLBACK IS TESTED, NOT DOCUMENTED.** A cutover gate with an untested rollback is a
  Fail, full stop.
- **UAT IS EXECUTED BY THE BUSINESS.** Delivery-team-prepared results a business user
  merely reviewed do NOT satisfy user acceptance (mirrors `uat-support.md`).
- **"SIGNED OFF" = a durable artifact** (email / tracker sign-off / minutes with explicit
  approval). Verbal does not qualify.
- **RETROSPECTIVE HONESTY.** If a gate is reviewed AFTER the wave already moved, flag the
  timing gap and state what evidence is reconstructable - do not back-date a pass.

## Output shape

Concise; never re-list what passed. One row per gate:

```
Gate | Verdict | Blockers (Fail) | Conditions (Conditional, w/ owner) | Advisory risks noted | one-line recommended next action
```

## Where this sits in the suite

- **Fed by:** wd-extend-dev `references/data-conversion.md` - its reconciliation harness is
  the evidence source for gates 2-5, and its dry-run + sign-off feeds gate 6.
- **Consumed by:** `cutover-planning.md` - gate 8's passed-prior-gates + agreed rollback
  decision point is the entry condition for the cutover go/no-go, and its freeze/rollback
  section governs the calendar around these gates.
- **Named in the quality-gate registry** as "Migration wave gate" (wd-extend-lifecycle
  `references/quality-gates.md`) so it shows up as a scheduled phase-exit check.

(adapted from an internal firm skill, 2026-08-28)
