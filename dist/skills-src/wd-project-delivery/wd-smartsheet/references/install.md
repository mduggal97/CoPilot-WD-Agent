# Installing this skill - plain-language guide (start here)

**What this is:** a Claude "skill" that lets Claude read and update your Smartsheet trackers for
you. You set it up once, then just ask Claude in plain English (e.g. "update our RAID log in
Smartsheet") and it does the work.

You do NOT need to be technical. Claude does almost all of the setup for you. There are only three
small things that have to be done by a person (installing Python if it's missing, getting your
Smartsheet token from the website, and pasting that token in once). Claude walks you through each,
click by click, and fills in anything technical (like file paths) for you.

## Where this runs (read this first)

This skill does its work **on your own computer** - it runs a small program locally, uses a token
saved securely on your machine, and uses your normal network. So it is built for **Claude Code**
(the Claude app that runs on your computer / laptop).

- **Use Claude Code on your computer** to actually read and update Smartsheet.
- If you open Claude in a **web browser (claude.ai)**, it can read these instructions, but it
  **cannot reach your Smartsheet or your saved token**, so it can't actually update your sheets
  there. Install it in Claude Code.
- Not sure which you have? Ask whoever sent you this, or ask Claude: "Am I in Claude Code or on
  claude.ai?"

## Step A - unzip the file

1. Find `WD_Smartsheet_Skill_shared.zip` (probably in your Downloads folder).
2. Right-click it -> **Extract All...** -> **Extract**. You now have a folder that contains a
   `wd-smartsheet` folder.

## Step B - put the `wd-smartsheet` folder where Claude looks for skills

Claude Code looks in one specific folder on your computer:

1. Open **File Explorer**.
2. Click the **address bar** at the top, type this exactly and press Enter:
   `%USERPROFILE%\.claude\skills`
3. If Windows says the folder doesn't exist: type `%USERPROFILE%\.claude` and press Enter instead;
   if that's missing too, type `%USERPROFILE%`. Then create the missing folders by right-clicking ->
   **New -> Folder** and naming them `.claude` and then `skills` inside it. (A folder name that
   starts with a dot is normal here.)
4. Copy the `wd-smartsheet` folder (from Step A) **into** this `skills` folder. When done you should
   have a file at: `...\.claude\skills\wd-smartsheet\SKILL.md`.
5. **Close and reopen Claude Code** (new skills are picked up when it restarts).

**Did it work?** Ask Claude: *"what skills do you have?"* or just say *"help me update a Smartsheet."*
It should recognize **wd-smartsheet**. If it doesn't, double-check the folder is exactly at
`...\.claude\skills\wd-smartsheet\SKILL.md` and that you restarted Claude Code.

*(If your team uses claude.ai's Skills upload instead: open Settings, find the Skills area, and upload
the zip. Remember the "Where this runs" note above - to actually update sheets, use Claude Code on
your computer.)*

## Step C - let Claude finish the setup FOR you

Now just tell Claude what you want to do with Smartsheet. The first time, Claude runs a short one-time
setup and does everything it safely can for you:

- checks whether Python is installed (and if not, tells you the one thing to click);
- fills in every command with your real file paths - **you never have to figure out a path**;
- runs the connection test and the sheet look-ups itself.

The only parts that must be done by you (Claude will hand you each with exact steps):

1. **Install Python** if it's missing - one click in your software portal (e.g. Company Portal).
2. **Get your Smartsheet token** from the Smartsheet website (a short click-through).
3. **Paste that token once** into a hidden prompt in a terminal (Claude gives you the exact command
   with the path already filled in).

Details and exact clicks for those three are in [token-setup.md](token-setup.md) - but you don't have
to read it first; Claude will guide you live. If anything shows an error, just paste the error text to
Claude and it will sort it out.
