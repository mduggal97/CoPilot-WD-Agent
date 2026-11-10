# Canonical IDD "READ ME" content (authored as CELLS, not a text box)

This is the single source of truth for the IDD READ ME sheet. It is written into the
workbook as **formatted worksheet cells** by `scripts/write_idd_readme.py` (NOT as a floating
text box/image - shapes get dropped when an IDD is rebuilt by any non-COM path, which caused
repeated "READ ME missing" defects). Keep this file and the script's `BLOCKS` list in sync.

A macro master obtained per engagement may already carry this as cells, and any IDD copied
from such a master inherits it; if you ever produce an IDD that lacks it, run `python scripts/write_idd_readme.py <idd.xlsm>`.

---

**HOW TO USE THIS DOCUMENT:**  *(title - bold, underlined, dark blue)*

- This document has macros - in order to enable the macros and share your designs on a client's repository you must follow the following steps:

*(dark navy banner block, white text - the macro-enable steps)*
```
1. Tap the start button or Windows key and type Internet Options.
2. Select Internet Options from the search results and the Internet Properties dialog box appears.
3. On the Security tab, select Trusted Sites, and then select Sites.
4. Type the URL of the site or server that contains the Microsoft 365 files with the macros you want to run, and then select Add.
        1. URL: <CLIENT REPOSITORY URL>
5. Select Close, and then OK.
6. Close and reopen the doc from Client Repository
```

Step 1: Fill out the Overview tab, this tab has certain fields that will autopopulate data across multiple sheets.
   a) Integration Type - includes a macro that will drive what tabs are hidden/unhidden

Step 2: Manually hide/unhide tabs that may or may not be needed and not included in the macro configuration

Step 3: Fill out the Question tab.

Step 4: Complete IDD as it relates to your integration.

TIPS:

- Version Control Tab:
   a) Keep this tab up-to-date to track design and functional changes. Create an initial entry titled "Initial Draft" to track when you started the design
   b) Make sure to track changes to the document and give proper descriptions of what changes were made (ex: If the functional team adds 3 new requirements that you add to the Requirement Tab, document this under the Detail Changes Summary column on the Version Control Tab)
