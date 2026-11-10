# Scripts this skill ships - build-specs

- **`scripts/setup_doctor.py`** - the suite setup doctor. BUNDLED and ready to run; usage in
  [prerequisites.md](prerequisites.md) ("Fastest setup").

---

### setup_doctor.py - suite setup doctor / bootstrap
- **Language / runtime:** Python 3, **standard library only** (must run before anything is installed).
- **Third-party deps:** none.
- **OS constraints:** cross-platform (Windows / macOS / Linux); detects the OS and adjusts (e.g. skips
  pywin32/COM off Windows).
- **Inputs:** CLI flags - none = report only (no changes, no network); `--install` = install MISSING core
  Python packages (prompts y/N first); `--yes` = skip the confirm (use only after the user has approved).
- **Outputs:** a plain-language console report grouped as Runtime / Core packages / Windows Office automation
  / Task-specific packages / External tools, each item marked `[ OK ]` / `[MISS]` / `[ -- ]`; a summary; and,
  with approval, a `pip install` of the missing core packages. Never prints or handles secrets.
- **Method:** `importlib.util.find_spec` to test each package without importing; `shutil.which` to probe
  external tools on PATH; `subprocess` to run `python -m pip install` only under `--install` (+ confirm).
  `CORE` = {openpyxl, python-docx, requests, urllib3, keyring, truststore, PyMuPDF, Pillow};
  `OPTIONAL` = {pandas, networkx, pydantic, python-pptx}; Windows-only = pywin32; `EXTERNAL` = PowerShell,
  Node, LibreOffice, wdcli, draw.io - each with a where-to-get line and what-breaks-without-it note.
- **Key constants:** the CORE/OPTIONAL/EXTERNAL tables above; requires Python >= 3.9.
- **Gotchas:** report-only by default on purpose (safe to run anywhere); it installs nothing without
  `--install` + confirm; it deliberately does NOT touch credentials (each skill prompts securely at use -
  see prerequisites.md "Secrets") and does NOT auto-install GUI/vendor tools (wdcli/Studio/Balsamiq/
  LibreOffice/Node), only reports where to get them.
- **Regeneration confidence:** High - stdlib-only and fully specified; the package/tool lists are the only
  thing that evolves (keep them in sync with prerequisites.md).
