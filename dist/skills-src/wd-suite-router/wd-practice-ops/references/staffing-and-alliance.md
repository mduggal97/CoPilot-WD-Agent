# Staffing, capacity & the Workday alliance relationship

Two practice-ops functions: putting the right people on the right work, and tending the firm's relationship
with Workday. Vendor-neutral.

## Staffing & resourcing

Match people to work by **capability + availability**, transparently:
- **Inputs:** the competency matrix + certifications (practitioner-enablement.md) for capability; a current
  **bench/availability view** (who is rolling off, who is free, when) for availability.
- **Demand:** open pursuits (a sized deal from wd-estimate names the roles/skills it needs) and in-flight
  engagements' staffing changes.
- **Match:** staff by the skills the work actually needs and who is genuinely available - not habit or
  loudest-voice. Flag capability gaps that no available person covers (a signal to enable, subcontract, or
  decline/rescope) rather than staffing someone underqualified.
- **Ramp overlap:** plan roll-on/roll-off overlap so knowledge transfers; a hard swap mid-engagement leaks context.

## Utilization & capacity

- **Utilization** = billable time vs. available time; set a target RANGE per role (too high starves enablement,
  pursuits, and PTO; too low is margin leakage). Track it, don't just hope.
- **Invest time is not waste** - enablement, reuse-asset building, pursuits, and the alliance relationship are
  deliberate non-billable investments; name them so they are protected, not accidentally squeezed to zero.
- **Portfolio capacity planning** - roll individual availability up to a practice view: can we take the next
  engagement, and when? This is the cross-engagement view (a single engagement's staffing hours stay in wd-pm).
- **Boundary:** deal-level margin/pricing lives in wd-estimate; engagement-level plan/hours live in wd-pm. This
  is the people-supply side that feeds both.

## The Workday alliance / partner relationship

Treat Workday as a relationship to tend, not a case queue - it compounds and feeds both delivery and sales:
- **Partner status/tier** - know the practice's current standing in Workday's partner program and what
  sustains it (certified-consultant counts, delivery quality, specializations). Lapsed certs
  (practitioner-enablement.md) can erode it - another reason to track recert due dates.
- **Built-on-Workday / Innovation partner program** - if the practice ships productized apps, the BoW/partner
  program status and requirements gate Marketplace listing (the GTM side is bow-sales-enablement; the
  relationship/eligibility side is here).
- **Workday Community + Customer Care** - Community (roadmap, What's-New, brainstorms, docs) and Customer Care
  (cases) are ongoing channels: mine Community for roadmap signal and known issues, not only when blocked.
- **Roadmap-intelligence intake** - capture forward signal (DevCon, Community roadmap, release previews) about
  features that may (a) simplify or (b) strand in-flight custom builds. Route it two ways:
  - to **wd-extend-dev `release-impact.md`** - specifically the **GA-status tracker** there, so "is feature X
    GA yet?" resolves in one place and the many verify-GA caveats across the build skills have an answer;
  - to **wd-discovery `solution-options.md`** Evergreen-risk column - so pursuits weigh "will Workday deliver
    this natively?" before designing a custom build.

## Where this goes

Availability/capacity -> staffing decisions + wd-estimate (can we resource this deal, and when). Alliance
status -> pursuit credibility (bow-sales-enablement) + delivery risk awareness. Roadmap intelligence -> the GA
tracker (wd-extend-dev release-impact.md) + solution-options Evergreen risk (wd-discovery).
