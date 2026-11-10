# User Guide Pattern

The house pattern for Extend app user guides, proven on the delivered **Employment End
Date Automation (O4I) User Guide** (Word, firm-branded template, from
`User Guide_Template.docx`; delivered 2026-07-23 alongside the design doc, process
flow, and deployment guide).

## Document skeleton

1. **Cover + TOC** - the engagement's template, or neutral formatting; set the TOC field to auto-refresh
   on open (`updateFields`) so page numbers stay honest after edits.
2. **Introduction** - one page, plain English: what the app does, who uses it, where
   it lives in Workday. A reader should know within 60 seconds whether this guide is
   for them.
3. **Per-role sections** - one section per role that touches the app (e.g. Requester,
   Approver, Administrator). Each section is self-contained: a user in one role should
   never need to read another role's section to do their job. Order sections by the
   process flow (requester before approver).
4. **Task walkthroughs, screenshot-per-step** - inside each role section, one
   walkthrough per task. Every step the user takes on screen gets:
   - A numbered instruction in imperative voice ("Click **Submit Request**").
   - A screenshot of that screen, cropped to the relevant region, with a callout
     box/arrow on the control being used.
   - If screenshots aren't available yet, insert a grey placeholder box with
     the exact caption of the screenshot that goes there (house convention) - never
     ship a step without at least the placeholder.
5. **FAQ** - harvested from UAT, not invented. Pull every question asked during UAT
   and KT sessions (transcripts via wd-pm meeting-intake), answer in plain language,
   group by role. If UAT asked it once, production will ask it weekly.
6. **Error-message table** - three columns:

   | What the user sees | What it means | What to do |
   |---|---|---|
   | Exact on-screen text (verbatim, in quotes) | Plain-English cause | Self-fix steps, or "contact X with Y information" |

   Enumerate every validation message and error state in the app. This table is the
   support desk's first line and doubles as the seed of the triage runbook.

## Language rules

- **Explain it to your mother.** No Workday jargon without a one-line definition at
  first use ("a *business process* - Workday's word for an approval workflow").
- Short sentences, imperative voice, one action per numbered step.
- Name screens and buttons exactly as they appear in the app, in **bold**.
- Never explain internals (orchestrations, RaaS, SOAP) in the user guide - that lives
  in the design doc and the dual-audience spec's Part 2.

## Integration-only apps (no UI)

Apps like Employment End Date Automation have no end users - the guide is an
**operations guide framed for the Integration Administrator**:

- **Launching** - how to trigger (manual launch prompt vs. schedule), what each
  launch parameter means in business terms, screenshot of the launch prompt.
- **Monitoring** - where the integration events live, how to read run logs, what a
  healthy run looks like (INFO trail), what a warning looks like (non-200 -> WARNING
  per house logging convention).
- **Restart / retry** - safe re-run guidance: what happens if the same run is
  launched twice, which failures self-heal on retry vs. need data fixes first.
- **Error table** - same three-column format, but "what the user sees" becomes the
  log/event message text.
- Screenshot targets shrink to the launch prompt and the integration event/messages
  screens (the O4I guide shipped with exactly those two placeholders).

## Production notes

- Author in Word via the `docx` skill; store the delivered copy in the app's document
  folder next to the design doc and process flow.
- Version the guide (v1.0 at go-live); hypercare findings feed a v1.1.
- The tenant-setup content (ISSGs, ISUs, config attributes) belongs to the
  **Deployment Guide (wd-deployment `references/deployment-guide.md`)** - link to it from
  the admin section, don't duplicate it. For a no-UI O4I app that Deployment Guide is the
  standalone deliverable this guide is paired with (the Employment End Date precedent
  shipped both).
