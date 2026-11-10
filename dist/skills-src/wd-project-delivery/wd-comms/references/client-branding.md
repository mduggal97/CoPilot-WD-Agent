# Client branding profiles - capture-once pattern

Each client gets a profile captured **once**, then applied to every
communication and client-facing document afterward. Profiles live as separate
files: `references/clients/<name>.md`. Check for a profile at the start of
every wd-comms draft; apply it silently.

## Current profiles

Profiles captured to date are listed under **Engagement inputs** at the bottom of
this file. When the user first requests a branded document
for a client that has no profile yet, prompt for source artifacts - a past
client-approved email, a branded Word/PPT deliverable, a style guide, or a
comms/distribution list - and build `clients/<name>.md` from them. Do not
invent client branding.

## What to capture per client

Create `references/clients/<name>.md` with these sections. Capture only what
is confirmed from real artifacts or the delivery lead's direct statements; mark everything
else `UNKNOWN - ask` rather than guessing.

### 1. Logo usage rules
Whose logo appears on client-facing docs (client's, the firm's, both), placement
(header/footer/cover), any co-branding rules, where the approved logo files
live.

### 2. Fonts and colors (if mandated)
Only if the client mandates them for documents they receive. Font names,
hex codes, where mandated (all docs vs. formal deliverables only). If not
mandated, note "no mandate - firm defaults OK".

### 3. Email sign-off conventions
How the delivery lead signs client emails on this account (name/title/practice line),
whether the client team uses first names, salutation norms ("Hi all" vs
"Team" vs formal).

### 4. Document header/footer requirements
Confidentiality footers, draft watermarks, version blocks, page-number
conventions, required legends (e.g. "Prepared for [Client] by [Firm]").

### 5. Terminology preferences
What the client calls the system and the project - often not the Workday
term. Examples of the kind of entries to capture:
- System name: what they call their Workday tenant/program
- Project name: their internal program name vs. the firm's SOW name
- App names: the client-facing name for each Extend app vs. its internal use-case/app ID
- Terms to avoid or gloss: Extend jargon they haven't adopted

### 6. Distribution norms
Who is cc'd on what - status emails, escalations, design reviews, go-live
comms. Named roles/people per message type. Which channel each message type
uses (email vs. Teams vs. both). Any "never email directly, go through PM"
rules.

## Profile file skeleton

The canonical skeleton to copy is **`references/clients/_template.md`** (one owner - copy that
file, don't retype a shape from memory). Capture at minimum: logo usage, fonts/colors, email
sign-off, doc headers/footers, a Say/Not terminology table, a Distribution table (message type /
To / Cc / channel), and open questions - all as slots in the template.

## Maintenance

- When a draft reveals a new convention (the delivery lead corrects a term, adds a cc),
  update the profile file in the same session.
- Date-stamp additions; note the source artifact or conversation.
- Scope note: these profiles govern **communications and document trim** for
  client-facing output. Firm-internal deliverables use neutral
  formatting, and Word/PPT mechanics follow docx/pptx.

## Engagement inputs (pull from project memory; never hardcode)
This skill needs these per-engagement values. Do NOT hardcode them - read them from the current engagement's project-memory file, ask the user, or discover live:

- The current client / engagement.
- Which client branding profiles already exist (`clients/<name>.md`) vs. still need
  capture - track them here, one row per client:

| Client | Profile file | Status |
|---|---|---|
| <client name> | `clients/<name>.md` | Not yet captured / Captured [date] |

Build a client's `clients/<name>.md` from that client's real artifacts on first
request; do not invent branding. If a value isn't in memory, ask. For branded
output, use neutral formatting (no firm brand skill is installed).
