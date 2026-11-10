# Verify-in-tenant - the standing "trust-but-verify" rule

**At a glance:** never assume tenant state - verify it before relying on it. Use the
authoritative programmatic read (WQL / REST / RaaS / SOAP) wherever one exists; fall back to
a browser check only when no API covers it. This is a suite-wide standing rule, not a
one-project step.

## The rule (one sentence)

**Never assume tenant state - verify it before relying on it, using the authoritative
programmatic read (WQL / REST / RaaS / SOAP) wherever one exists; fall back to a browser
check only when no API covers it.**

## Why this is a standing rule, not a nicety

**It is the natural extension of the exemplar / north-star standard.** Exemplar work is
correct-AND-verified, not correct-by-assumption. "The design says the tenant has it" and "the
UI did not throw an error" are assumptions, not verification. A build that relies on tenant
state it never read is a shortcut - and the exemplar bar says shortcuts get FLAGGED, never
taken silently. Reading the state IS the verification.

## When it fires

Run the authoritative read in each of these moments - before you let the assumption drive a
design, a build, or a claim:

- **Before referencing that something EXISTS** - a BO, field, instance, worker, org, cost
  center, security domain, integration, or config value. Confirm it is actually there before
  you design or code against it.
- **Before CREATING a record** - confirm it is not already there, so you do not create a
  duplicate or collide with existing data.
- **After ANY tenant WRITE** - confirm it landed. "The UI did not error" is not proof; read
  the record back and see the new value / new instance / accepted field.
- **When a browser read says "none" / "empty"** - treat it as suspect, not settled. A blank
  list is often an ASYNC lag or a SECURITY-GATED artifact (wrong org/proxy hides rows), not a
  true absence. Confirm programmatically before concluding it is not there.
- **When DESIGNING against native data** - ask whether the tenant even HOLDS that data. A
  bare dev tenant will not have realistic workers/orgs/transactions; do not design or demo
  against data that is not in THIS tenant.

## How to verify (the technique lives next door)

This file owns the RULE. The "to confirm X, read Y" cookbook - which WQL / REST / RaaS / SOAP
read confirms each kind of tenant state - lives in **wd-extend-dev
references/tenant-state-verification.md**. Open that for the concrete read per artifact type.

Precedence for the read:

1. **Programmatic first** - WQL / REST / RaaS / SOAP. This is the authoritative read.
2. **Browser check only as fallback** - when no API covers the artifact. A browser read is a
   last resort, and a browser "empty" result gets the async / security-gated caveat above.

## Reporting

When a deliverable depends on tenant state, **report the verification with it** - what you
read, how (WQL / REST / RaaS / SOAP / browser), and what it confirmed - the same way every
other quality gate reports its result. An unverified assumption presented as fact is a failed
gate.

## Cross-ref

- Technique cookbook ("to confirm X, read Y"): wd-extend-dev references/tenant-state-verification.md
- Session-start operational checks: [operational-preflight.md](operational-preflight.md)
- The gate row: [quality-gates.md](quality-gates.md) ("Verify-in-tenant" standing gate)
- The exemplar / north-star standard this extends: wd-extend-dev references/standards.md
