# Security Domain Apply - Safety Design

Read this before ever running `security_domain_apply.py apply --execute` against a
real tenant. This tool can change a client's production security posture. Getting
it wrong has real consequences for real people's access - treat every guardrail
below as load-bearing, not optional.

## The core idea

**Plan, then apply.** Nothing is written during `plan` - it only reads, computes,
and saves a file. `apply` is the only command that can write, and even then it
defaults to a dry run. A human has to explicitly opt into every real write, every
time, with the exact change list in front of them.

## Guardrail 1 - dry run is the default

**Running `apply` without `--execute` never touches the tenant.** It prints
exactly what would happen and stops. You have to add `--execute` on purpose to
get past that.

## Guardrail 2 - production is a hard block, not a warning

**`--tenant-type` only accepts `dev`, `impl`, or `sandbox`.** Typing `prod` or
anything else fails immediately, before any network call - argparse rejects it
at the command-line level. This tool will never write to a tenant declared as
production. A production change stays a manual, in-tenant action.

## Guardrail 3 - the ISSG is validated by WID, twice

**Every plan confirms the WID you supplied actually names the group you typed,**
by looking it up in the tenant and comparing descriptors - before any GET or PUT
runs. It checks again, a second time, right before `apply` starts writing. A
copy-paste mismatch between the group name and its WID gets caught here, not
after a grant lands on the wrong group.

## Guardrail 4 - freshness check before every write

**Right before touching each domain or BP, the tool re-fetches its current state
and compares it to what the plan was built from.** If anything changed in the
tenant since you ran `plan` - someone else made a change, or time has just
passed - that item is aborted and the whole run stops. A stale plan never gets
silently applied on top of a tenant that has since moved.

## Guardrail 5 - one item at a time, stop on first failure

**Every domain or BP is processed individually**, not as one batch call. Before
each write: back up the current document. After each write: verify the change
actually landed. **Any failure - a fault response, a verification miss, a
staleness abort - stops the whole run right there.** It never continues to the
next item after something goes wrong, so a mistake can't cascade through a list
of changes.

## Guardrail 6 - a backup before every single write

**The exact pre-change document is saved to a local file, timestamped, before
the PUT goes out** - `security_domain_apply_runs/<tenant>/backups/`. If a change
needs reverting, that file is the reference for what it looked like before.

## Guardrail 7 - a full audit trail

**Every write attempt - success, failure, or abort - is logged** to
`security_domain_apply_runs/<tenant>/audit_log.jsonl`, one line per event, with
the timestamp, the item, the result, and the backup path. Nothing happens
silently.

## Guardrail 8 - success means verified, not just "no error"

**A 200 response with no fault is not treated as proof.** After every write, the
tool re-fetches the same object and confirms the new group actually shows up in
the right permission list. If it doesn't, that's logged as a failure and the
run stops - a silent no-op PUT never gets reported as a success.

## Guardrail 9 - the riskiest access level needs an extra flag

**View and Modify grants - the highest-risk access level - are skipped by
default even with `--execute`.** You have to add `--allow-modify-grants`
on purpose to let those through. Get Only / Get and Put / View Only grants
don't need this extra flag; View and Modify does.

## Guardrail 10 - typed confirmation, not a yes/no prompt

**Before any write, the tool prints the tenant name, the target ISSG, and the
full itemized change list, then asks you to type the tenant alias exactly** to
proceed. A reflexive "y" can't accidentally confirm a change to the wrong
tenant.

## Guardrail 11 - this tool never activates the change

**Every domain and BP security policy change lands as PENDING in Workday.** A
human still has to go into the tenant, review it under "View Security Policies
for Pending Change," and Activate it. This tool deliberately does not do that
step - it's Workday's own last checkpoint before a change takes effect, and
removing it would remove the safety net entirely.

## What's deliberately NOT automated (do these by hand)

**Overriding inheritance on a subdomain.** The correct payload mirrors the
parent's existing grants into a new subpolicy for that one subdomain - subtle
behavior that wasn't live-verified. `plan` will skip these with a clear message
rather than guess.

**Matching a BP's Initiate-permission task to an inbound web service.**
`security_domain_discovery.py` prints every task on the BP with its current
grants so a human can eyeball the match - auto-matching risks granting the
wrong task.

**Creating a new ISU or ISSG.** Only grants on EXISTING domains, BPs, and
security groups are supported. Object creation is a separate, larger blast
radius and isn't built yet.

## First live test (2026-09-04) - succeeded, and found a third bug

**Test:** grant Get Only on "Custom Report Creation" to "SecurTest-ISSG" in
a dev tenant (chosen specifically as the lowest-stakes
option - no client data, no client-facing consequences). The maintainer approved this
exact domain/group/level combination before it ran.

**Result: the write succeeded.** The PUT returned a clean, empty
`Put_Domain_Security_Policies_Response` (no fault), and the change is now
confirmed sitting in Workday's pending-changes queue - visible via
`domainSecurityPoliciesWithPendingChanges`, timestamped to the second against
the PUT, attributed to the correct user identity. **It has not been activated**
and will not take effect until a human does that in-tenant.

**The third bug this caught: post-write verification was checking the wrong
thing.** The tool re-fetched the ACTIVE policy immediately after the write and
correctly found nothing there - because Workday never shows a pending change on
a normal Get, by design, until it's Activated. My original verification logic
treated that as a failure and stopped the run. It wasn't a failure; it was the
verification checking a state that structurally cannot show the answer yet.
Fixed: verification now checks `domainSecurityPoliciesWithPendingChanges` (for
domains) and `businessProcessSecurityPoliciesWithPendingChanges` (for BPs) -
matched by descriptor and a timestamp after the write, since (see below) these
sources carry their OWN internal WID for the same domain, incompatible with the
WID used to fetch/PUT the policy itself. This confirms a pending change now
exists for the right object very recently - it does NOT independently confirm
which exact group/level landed. That finer-grained certainty still belongs to
the human's own review in "View Security Policies for Pending Change" before
Activate - this check exists to catch a PUT that silently did nothing, not to
replace that review.

## Three real bugs this testing caught (why live-verification matters)

**Wrong ID type on the new grant.** the partner tool's own XSLT templates label a
WID-formatted value as `Tenant_Security_Group_ID` - a type/value mismatch that
either fails resolution outright or, worse, could silently resolve to the wrong
object if that string ever collided with a real tenant ID somewhere. Fixed to
use `wd:type="WID"`, the one identifier guaranteed to resolve correctly.

**Subdomain WIDs are not valid fetch targets.** `Get_Domain_Security_Policy_Request`
only resolves TOP-LEVEL domain WIDs - passing a subdomain's own WID is rejected
with a validation error. Every subdomain case (inheriting or not) has to fetch
via its parent's WID and locate the target inside that document. Caught by
testing against a real tenant, not by reading the XSLT alone.

**Post-write verification checked the wrong state** (see "First live test"
above) - fixed to check the pending-changes queue instead of the active policy.

The first two were found and fixed BEFORE any real write was attempted; the
third only surfaces after a real write, which is exactly why the first live
test was run as a small, deliberate, approved experiment rather than skipped -
dry-run testing alone could not have caught it.

## Pattern worth banking generally: WIDs are not portable across Workday API surfaces

Found twice independently in this build: `allDomains`'s own `domain`
self-reference field carries a WID that `Get_Domain_Security_Policy_Request`
rejects as an invalid `Domain_Reference`; separately,
`domainSecurityPoliciesWithPendingChanges`'s own `domainSecurityPolicy`
reference carries a DIFFERENT WID for the same conceptual domain than the one
used to fetch/PUT its policy. The same conceptual object can have multiple,
non-interchangeable WIDs depending on which Workday service or WQL data source
is looking at it. Never assume a WID obtained from one API surface is valid on
another - confirm within the same surface, or match by descriptor + a
recency/identity check instead when a WID can't be safely reused across
surfaces (as this script does for pending-change verification).
