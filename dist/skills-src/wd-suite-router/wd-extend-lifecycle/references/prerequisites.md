# Suite prerequisites & script portability - read this first on a new machine

These skills are shareable. Most of what they carry is **prose conventions** - those work
for anyone with Claude Code, no setup. A subset of tasks run **helper scripts** (Excel/Word
generation, Balsamiq/draw.io rendering, Smartsheet/Workday REST). This page is the one-time
setup so those work for a new user, and it explains how the suite avoids depending on files
that live only on the original author's machine.

## Fastest setup - run the doctor, or just ask Claude

**You do not need to know what any of the tools below are.** Two ways in:

- **Just ask Claude** - say *"set up this suite for me."* Claude runs the doctor, tells you in plain
  language what is ready and what is missing, and - **with your approval** - installs the core Python
  packages for you. This is the standing convention across the suite: **on first use, a skill checks its
  own dependencies and offers to install or regenerate what is missing rather than assuming you have it**;
  you approve, Claude does the work, and secrets are always entered by you at a secure prompt (never by Claude).
- **Or run the doctor yourself** (stdlib only - works before anything is installed):
  ```bash
  python wd-extend-lifecycle/scripts/setup_doctor.py            # report only - changes nothing, no network
  python wd-extend-lifecycle/scripts/setup_doctor.py --install  # installs MISSING core packages (asks y/N first)
  ```
  It detects your OS, checks Python + pip + the core packages + the external tools, prints OK/missing per
  item with a where-to-get line for the tools it cannot install, and **never handles passwords/tokens/keys**
  (those are entered securely at each skill's own prompt - see Secrets below). Build-spec in `scripts.md`.

## How scripts are handled in this suite (so nothing is a dead path)

1. **Bundled scripts ship inside a skill's `scripts/` folder** - they travel with the
   skill. Check each skill's `scripts/` folder for what ships (notably:
   `wd-design-doc/scripts/idd_audit.py` + `write_idd_readme.py` + `rebrand_template.py`,
   `wd-smartsheet/scripts/smartsheet_api.py`, `wd-folder-hygiene/scripts/archive_old_versions.py`,
   `wd-systems-diagrams/scripts/` incl. the bundled diagram engine); each skill's
   `references/scripts.md` marks what's bundled vs build-spec-only. Run bundled scripts from
   the skill folder.
2. **Larger/heavier scripts are NOT shipped as files.** Instead each skill that uses one
   carries a **build-spec** (in its `references/scripts.md`, or its main reference) - the
   inputs, outputs, method, and gotchas needed to (re)generate an equivalent on demand. If the
   original file isn't on your machine, **Claude writes it fresh from the build-spec** rather
   than pointing at a path you don't have. This also means Claude generates the right variant
   for **your** OS (e.g. a cross-platform path instead of a Windows-only Excel-COM one).
3. **Absolute paths in "Engagement inputs" / "Program defaults" blocks are examples**, not
   requirements. Treat them as "here's what a real one looked like," and regenerate or
   re-point to your own copy.

So: a new user is never blocked by a missing script - worst case Claude rebuilds it from the
spec. The setup below just makes the **shipped** scripts and the **regenerated** ones actually run.

## Runtimes

| Need | For | Notes |
|---|---|---|
| **Python 3.9+** | every `.py` helper (design docs, wireframes, renders, Smartsheet/Workday REST) | `python --version`; on Windows the `py` launcher also works |
| **PowerShell 5.1+** | the `.ps1` helpers (project plan, markdown->Word) | ships with Windows; PowerShell 7 is fine too |
| **Node / draw.io CLI** *(optional)* | headless PNG export of `.drawio` process flows | only if you render flows to PNG via CLI; otherwise export from the draw.io app |
| **wdcli** *(dev/deploy only)* | the Workday Extend CLI (`app deploy/promote`, schema pull) | user-installed; **auth is interactive - the user runs `wdcli auth login` / tenant login**, never automated |
| **Workday Studio** *(Studio integrations only)* | building/deploying Studio mediation assemblies (CLARs) | Eclipse-based IDE, downloaded via Workday Community; deploy + tenant auth are interactive (no CLI). Reviewing/diffing Studio code needs NO install - `ws/WSAR-INF/assembly.xml` + XSLTs are plain XML (see `wd-integration-dev/references/studio.md`) |

### Installing Python (first time, if `python --version` errors)

- **On a managed / enterprise machine:** install Python 3 from **your organization's software
  portal** (on Windows/Intune-managed devices this is the **Microsoft Company Portal** app - search
  "Python", install Python 3; no admin rights or IT ticket needed). This is the approved path on
  locked-down corporate machines.
- **On a personal / unmanaged machine:** download Python 3.9+ from
  [python.org/downloads](https://www.python.org/downloads/); on Windows tick **"Add python.exe to
  PATH"** on the first installer screen.
- Reopen the terminal and confirm `python --version` (Windows fallback: `py --version`), then install
  packages below. (Firm-specific install notes, if any, live in the firm environment notes in memory.)

## Python packages

Install what a task needs (or let Claude `pip install` on demand):

```bash
pip install openpyxl python-docx pywin32 pymupdf pillow requests urllib3 keyring
```

| Package | Import name | Used by | Cross-platform? |
|---|---|---|---|
| `openpyxl` | `openpyxl` | Excel `.xlsx`/`.xlsm` read/write (design docs, rebrand, UET/questionnaire fills) | [x] |
| `python-docx` | `docx` | Word `.docx` **template builders** (naming-standards, KT plan/templates, runbooks) - the cross-platform path that regenerates a working `.docx` without Word/COM | [x] |
| `pywin32` | `win32com.client` | **Excel COM & Word COM** - `.xlsm` formatting that must preserve VBA/macros/formulas; Word `.docx` generation; rendering tabs via Excel | [X] **Windows + the Office app installed** |
| `pymupdf` | `fitz` | render an Excel/PDF page to PNG to **visually verify** a deliverable | [x] |
| `pillow` | `PIL` | Balsamiq draft-preview PNG (`bmpr_render`) | [x] |
| `requests`, `urllib3` | `requests`, `urllib3` | Smartsheet REST, Workday REST/WQL/OAuth | [x] |
| *(stdlib)* | `sqlite3` | Balsamiq `.bmpr` files are SQLite - no install | [x] |

### The Windows-only caveat (important when sharing)

Anything that goes through **Excel COM or Word COM (`pywin32`)** runs **only on Windows with
Office installed**. That covers: `.xlsm` styling/macro-preserving edits, the IDD rebrand path,
and Word-COM document generation. A Mac/Linux user should ask Claude for the **openpyxl /
python-docx** variant instead (works for `.xlsx` and plain `.docx`; the trade-off is it can't
drive Excel's own macro engine, so for a true macro `.xlsm` you still need Windows - see
`wd-design-doc/references/idd-template.md`, which already says "copy the master, don't
rebuild"). When in doubt, tell Claude your OS and it picks the right path.

**Document-generation reliability (build-session learning).** **Word/Excel COM (`pywin32`) can HANG** - it may
block on an interactive Office dialog (a trust/first-run prompt, or a file open in a viewer) and never return,
even for a simple docx->pdf export. So for generated deliverables, **prefer the cross-platform Python builders
(`python-docx`, `openpyxl`, `reportlab`) and VERIFY by rendering to an image (PyMuPDF `fitz`) and looking** -
rather than driving Office over COM. Reserve COM for the one thing only it does: macro/VBA-preserving `.xlsm`
edits. Two more gotchas seen: writing to an **open or OneDrive-synced file fails** ("device or resource busy")
- write a fresh versioned filename instead of failing; and PDF-from-Office should use the app's native
"Save as PDF" (tagged) where accessibility matters (see nfr-accessibility.md 1b), not a render-to-image path.

**Long-output reliability when an LLM generates the artifact (tooling learning).** If you build a tool
that has a model generate a long artifact in one shot (a full XSLT, a whole document, a big review
table), the model can hit its output-token ceiling and return a **truncated** result that looks
plausible but is unusable. Guard it: **detect truncation** (the response's stop reason is `max_tokens`,
or the expected closing marker - e.g. `</xsl:stylesheet>` or the last table row - is missing), **surface
it loudly** ("INCOMPLETE - do not use") and block copy/download, then **continue-generate**: send the
tail of what was produced back and ask the model to resume from exactly there, and **stitch** by trimming
the overlapping prefix (largest suffix-of-existing that is a prefix-of-continuation). May take more than
one continue for very long output. The sibling review-tool learning - **auto-mark N-A anything a text/CSV
export cannot verify** (highlighting, folder contents) rather than failing it - lives in wd-integration-dev
`references/integration-review.md`.

**Shell caveat when authoring a shipped command (PowerShell vs bash).** Windows PowerShell (5.1) does NOT
expand wildcard globs before handing arguments to a native executable the way bash does - a command like
`tool *.drawio` passes the literal `*.drawio` to the exe, which then fails "file not found." Any command or
helper the suite ships must either self-expand the glob (Python `glob`, or `Get-ChildItem`) or name files
explicitly. **VERIFY a shipped command in PowerShell, not just bash** - "works on my machine" often means
"works in my bash," and the user's default shell here is PowerShell.

## bow-sales-enablement build toolchain (only if rendering that kit's files)

The GTM kit's document builds use a Node + PDF + LibreOffice toolchain beyond the Python set above. Install only if you render those artifacts (usage lives in the bundled Wave-2 Build Kit + `bow-sales-enablement/references/build-and-brand.md`):

| Need | Install | For |
|---|---|---|
| Node builders | `npm i -g docx pptxgenjs sharp react-icons react react-dom` | docx-js / pptxgenjs artifact builds |
| weasyprint | `pip install weasyprint` | PDF render via the `kit.css` prelude pattern |
| Fonts | none to install - `kit.css` uses a system font stack | A client brand that licenses its own fonts sets them in its prelude |
| **LibreOffice** (`soffice`) | platform LibreOffice install | backs `recalc.py` (Excel formula recalc) and the anthropic `xlsx` skill's `office.soffice`; run `recalc.py` in that env |

None of these are needed for the wd-* skills - only the bow build kit.

## wd-systems-diagrams engine (integration landscape diagrams)

The bundled SFD engine (`wd-systems-diagrams/scripts/sfd_engine/`) needs `pip install pandas openpyxl networkx pydantic` (required) + `python-pptx` (only for PPTX output; skips gracefully if absent). `requests`/`Pillow` are imported by the bundled logo module but the headless path runs offline (logo lookup skipped). No Node/browser needed - SVG/Draw.io/PPTX render directly.

## Secrets (the one-page rule - single source of truth)

**Every secret in this suite follows the same rule: never hardcode, never echo, never paste into chat;
prefer the OS keychain (`keyring`) via a hidden prompt; use interactive/native login where possible; Claude
never types a credential - you enter it at a secure prompt.** Scripts and skills point here rather than
restating it. The mechanisms:

| Secret | For | How it's handled (secure) |
|---|---|---|
| `SMARTSHEET_API_TOKEN` | wd-smartsheet REST helper | Run `python wd-smartsheet/scripts/smartsheet_api.py set-token` once (hidden prompt -> OS keychain; auto-read forever). Env var / `.gitignored` `.env` also work. See `wd-smartsheet/references/token-setup.md`. |
| Workday API client id / secret / refresh token | Workday BO REST / WQL (wd-extend-dev) | Run `python wd-extend-dev/scripts/tenant_toolkit.py set-creds` (hidden prompt -> OS keychain, per tenant profile); `check-tenant` / `delete-creds` manage it. Shown once at registration; regenerate any secret that lands in plaintext. |
| Workday API-client bearer (SOAP WWS inventory - OPTIONAL, gated tenants only) | `wd-integration-dev/scripts/wws_inventory.py` live mode | WSDL crawl is anonymous by default - no credential needed. For gated tenants, `client_id`/`client_secret`/`refresh_token` are read from the OS keychain (service `wd-wws-inventory`). Basic auth (`WD_USER`/`WD_PASS`) was retired ~R2 2026 and the script no longer reads it. |
| Workday tenant / Extend login | wdcli, Studio | **Interactive by design** - the user runs `wdcli auth login` / tenant login (browser OAuth) or Studio's own login. Automating these is a boundary violation; Claude never does it. |
| Any corporate CA / proxy | live REST behind TLS interception | `pip install truststore` (validates against the OS trust store); `WD_CA_BUNDLE` points at a corporate root CA `.pem`. Never disable verification except `WD_INSECURE=1` as a last resort on a trusted network. |

## Self-check on a new machine

**Run the doctor** (top of this page) - it is the self-check, and it offers to fix what's missing:
`python wd-extend-lifecycle/scripts/setup_doctor.py`. Manual fallback if you prefer one-liners:

```bash
python --version                                  # 3.9+
python -c "import openpyxl, requests; print('core ok')"
python -c "import win32com.client; print('win32 ok')"   # Windows only; failure just means use the openpyxl/docx path
```

If `import win32com` fails, you're not broken - you're on non-Windows or without Office; use
the cross-platform variants. If a referenced script file is absent, ask Claude to regenerate
it from the skill's build-spec.
