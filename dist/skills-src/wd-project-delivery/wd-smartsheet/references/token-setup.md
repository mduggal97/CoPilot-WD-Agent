# Get your Smartsheet API token (novice guide)

The skill talks to Smartsheet over the REST API, and the API needs a **personal
API access token** - a long secret string that stands in for your Smartsheet
login. You generate it once, store it on your machine, and the skill picks it up
automatically. If a user hits "No Smartsheet token found," walk them through this.

> **What the token is, plainly:** it acts as **you**. Anything you can see or edit
> in Smartsheet, a script holding this token can see or edit - nothing more. So a
> Viewer-shared sheet stays read-only; an Editor-shared sheet can be written. Treat
> the token like your password.

## Step 0 - install Python (one-time; skip if you already have it)

The skill's helper is a small Python script, so Python must be on your machine.

> **How to open a terminal (PowerShell) on Windows** - you'll use it for the commands in this guide.
> Press the **Start** button (or the Windows key), type **`PowerShell`**, and click **Windows
> PowerShell** in the results. A window with a text prompt opens - that is your "terminal." You type a
> command there and press **Enter**. (It's a separate place from the Claude chat box.) On a Mac, open
> **Terminal** from Applications > Utilities.

**Check first** whether Python is already installed - in that terminal, type this and press Enter:

```bash
python --version
```

If that prints `Python 3.9` or higher, skip to Step 1. If it errors (`not recognized` / `command not found`), install Python:

**Your steps (outside this session):**
1. **On a managed/corporate machine:** open your org's software portal (e.g. the **Company Portal** app; Start menu -> search "Company Portal"), search **Python**, and install the listed **Python 3** package. The software portal is the approved installer on managed devices, so you do not need admin rights or an IT ticket.
   **On a personal / unmanaged machine:** download Python 3.9+ from [python.org/downloads](https://www.python.org/downloads/) and run the installer - on Windows, **tick "Add python.exe to PATH"** on the first screen.
2. Close and reopen your terminal, then confirm: `python --version` (if Windows still errors, try `py --version`).
3. Install the two packages the helper needs:
   ```bash
   pip install requests keyring
   ```
   (`urllib3` comes with `requests`. `keyring` saves the token in your operating system's own secret store - **Windows Credential Manager, macOS Keychain, or Linux Secret Service** - so the secure one-time store in Step 3 works on any platform.)
   - *If `pip` errors behind a corporate proxy/firewall* (you'll see connection/SSL errors): paste the error to Claude - it can retry with the right `--proxy` / `--trusted-host` flags or give you the exact one-line command to run.
4. Tell me it's done and I'll continue.

**You don't compute file paths.** Several commands below show `<path-to-skill>` or `...`. You never have to figure that out - **Claude gives you each command with your real folder path already filled in.** If you're reading this on your own, ask Claude "what's the exact set-token command for my machine?"

**If the `scripts/smartsheet_api.py` helper is missing** from the skill on your machine (a fresh install, or only part of the skill was copied), I can recreate it from [scripts.md](scripts.md) - just ask, or see SKILL.md section 0.

## Step 1 - generate the token in Smartsheet

*(Official steps - [Smartsheet Learning Center](https://help.smartsheet.com/articles/2482389-generate-API-key). Labels can shift slightly by release; the flow is stable.)*

1. Sign in to Smartsheet in your browser.
2. Click your **Account icon** in the **lower-left corner** of the screen.
3. Choose **Personal Settings**.
4. Click the **API Access** tab.
5. Click **Generate new access token**.
6. **Name it** something you'll recognize (e.g. `Extend skill - <your name>`) and click **OK**.
7. **Copy the token value immediately** - Smartsheet shows it **only once**. If you
   lose it, you delete that token and generate a new one (no harm done).

Keep it on your clipboard for the storage step below. **Do not paste it into this
chat, a document, email, or any file you'll commit to git.**

## Step 2 - store it ONCE, securely (recommended)

The skill checks three places, in this order: `SMARTSHEET_API_TOKEN` env var ->
Windows Credential Manager -> a `.env` file.

> **Keyring service name (overridable).** In Credential Manager the token is stored
> under a keyring *service name* - a generic default that you can override by setting
> the `SMARTSHEET_KEYRING_SERVICE` environment variable. `set-token`, `clear-token`,
> and `test` all use whichever name is in effect, so as long as it's consistent the
> token is found automatically. (A firm may have a historical/standard service name;
> that lives in environment memory, not in this skill.)

**Do this - the secure one-time store.** Run this once **in your own terminal**
(not in Claude chat). It prompts for the token with **hidden input**, so the token
never appears on the command line, in your shell history, in any file, or in chat -
and it's saved encrypted in **Windows Credential Manager**, where the skill reads it
automatically from then on:
```
python <path-to-skill>\scripts\smartsheet_api.py set-token
```
- At the hidden `Smartsheet token:` prompt, **paste your token and press Enter** (you
  won't see it - that's expected).
- It stores the token and immediately verifies it, printing `...verified as: <your
  email>` on success (**never the token itself**).
- That's it - **you never enter the token again**, in any future session, on this
  machine. (If Python says keyring is missing: `pip install keyring`, then re-run.)
- To remove it later (e.g. before handing off the machine): `python ...\smartsheet_api.py clear-token`.

Why this over the alternatives: it never puts the secret on a command line (which
would land in shell history) or in a plaintext `.env`/registry value. It's the
"provide it once and forget it" path.

*Fallback if you can't use keyring - environment variable.* Less secure (setx writes
the value in plaintext to your user environment), but works: run `setx
SMARTSHEET_API_TOKEN "PASTE_TOKEN_HERE"` once in PowerShell, then open a **new**
terminal. Prefer `set-token` above whenever possible.

## Step 3 - verify it works

```
python <path-to-skill>\scripts\smartsheet_api.py test
```
Success prints `Connected as: <your email>`. Then you can browse to your work:
```
python ...\smartsheet_api.py workspaces        # your workspaces (pick one by name)
python ...\smartsheet_api.py find "<sheet name>"  # find a sheet by name
```

## Troubleshooting

- **No "API Access" tab, or "Generate" is greyed out** -> your Smartsheet plan/license
  doesn't include API access. This is an account/licensing setting, not something the
  skill can fix - ask your Smartsheet workspace admin to enable API access for your
  user (typically needs a licensed user on a Business/Enterprise plan).
- **`401 Unauthorized` on every call** -> the stored token is wrong, expired, or was
  revoked. First run `python smartsheet_api.py check-token` - it says whether a token is
  stored, where it came from (env var / Credential Manager / .env), shows a masked
  preview (first/last 4 only), and live-tests it, WITHOUT exposing the value. Then
  regenerate (Step 1) and re-store (Step 2) if it's bad.
- **`403` on a specific sheet** -> the token works, but that sheet isn't shared to you
  with enough access. Get it shared (Viewer to read, Editor to write) - the token
  can't exceed your own Smartsheet permissions.
- **SSL / certificate errors on a corporate network** -> expected (corporate SSL
  inspection); the skill's helper already sets `verify=False` to handle it.

## Security rules (non-negotiable)

- Never paste the token into chat, docs, email, or committed files.
- One named token per person/purpose so it's easy to revoke a single one.
- Rotate/revoke in the same **Personal Settings -> API Access** screen if it's ever
  exposed or a teammate leaves.
