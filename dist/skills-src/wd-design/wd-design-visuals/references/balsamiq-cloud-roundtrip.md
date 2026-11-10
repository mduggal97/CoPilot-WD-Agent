# Balsamiq round-trip - getting the clean PDF into the doc

**Default path = the user exports; you embed.** On many policy-restricted / managed enterprise machines the **Claude in Chrome extension is blocked by policy**, so the browser-automation round-trip below is NOT available there - do not propose it where policy blocks it (check the engagement's environment facts in project memory). It also requires the extension (not just a Balsamiq login) even where allowed. So the reliable, standing workflow is manual and it already works:

1. Ask the user to export from Balsamiq: **Project -> Share/Export -> Download a file -> PDF**, and drop the PDF in chat.
2. Render PDF->PNG via PyMuPDF (`fitz`) at ~300dpi, crop the export header/page-marker and white margins (per output-formats.md), and embed it in the design doc's UI & Wireframes tab (wd-design-doc), replacing any draft render.

This is exactly how one clean export landed - a delivered task app, as an example. No automation needed; don't gate the deliverable on browser tooling.

---

## (Only if the extension is available) Browser-automation round-trip

Balsamiq has NO public REST API (confirmed 2026-07-30): the documented integration surface is the .bmpr file format itself; Cloud upload and PDF export are UI-only workflows. Where the Claude in Chrome extension IS installed and permitted, the automatable path is driving Balsamiq Cloud through the user's logged-in browser session (the user's real Chrome carries their SSO). Not usable where managed-Chrome policy blocks the extension - see above.

## Prerequisites

- The user is signed into Balsamiq Cloud (SSO) in Chrome, and grants browser-automation access for the session. First run: do this TOGETHER with the user - site layout drifts and the first pass calibrates the steps below.
- The generated .bmpr has already passed the local checks (proven typeIDs, unique IDs, intra-frame overlap check - see balsamiq-bmpr.md). Cloud upload is the verification of last resort, not the first.

## Workflow

1. Navigate to the user's Balsamiq Cloud space (balsamiq.cloud). Confirm the signed-in account before touching anything.
2. **Upload**: Projects list -> upload/browse control (the project list accepts .bmpr uploads; use the browser file-upload tool with the local path). Never overwrite an existing Cloud project without the user's explicit OK - upload as a new project.
3. **Verify**: open the imported project; confirm the expected screen/wireframe count; screenshot 2-3 screens and compare against the draft render for missing controls or layout drift. If something's wrong, fix the LOCAL .bmpr and re-upload (don't hand-edit in Cloud - the local file is the source of truth until handoff).
4. **Export PDF**: Project -> Share/Export -> Download a file -> PDF. Confirm the download landed; that PDF is the CLEAN export the design doc embeds (render PDF->PNG per output-formats.md).
5. Report to the user: project name/URL, screens verified, PDF path. The Cloud copy becomes the user's editing copy from here - if they adjust arrows/layout in Balsamiq, their re-export supersedes ours (never regenerate over their tuning).

## Boundaries

- Uploading to Balsamiq Cloud publishes the file to that workspace - confirm with the user before the first upload of any new project.
- If SSO prompts for credentials, STOP and hand control to the user - never enter credentials.
- Desktop Balsamiq automation (COM/UI scripting) is not supported - use the Cloud path or the user's manual export.

Sources for the no-API finding: [Balsamiq export docs](https://balsamiq.com/wireframes/cloud/docs/exporting/), [BMPR format docs](https://balsamiq.com/wireframes/desktop/docs/bmpr-format/), [PDF export docs](https://balsamiq.com/wireframes/cloud/docs/exporting/exporting-to-pdf/).
