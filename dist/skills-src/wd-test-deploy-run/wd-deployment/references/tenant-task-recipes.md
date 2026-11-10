# Tenant-Task Recipe Library

Reusable, copy-pasteable, **novice-grade** recipes for the tenant-side setup steps an
Extend app or integration needs in each Workday tenant. Drop the relevant recipe into a
per-app setup guide (see `tenant-setup-guide.md`) and replace every `<PLACEHOLDER>` with
the app's real names.

**Audience assumption:** the reader is a tenant admin who has **never done this before**.
So every recipe uses the exact Workday task name (the thing you type into the search bar),
one action per numbered step, no unexplained jargon, and a "You're done when..." check plus
the failure symptom if the step is skipped or wrong.

> **Assembling the guide's security section:** these recipes are the *tasks* (Part 1). A
> complete guide security section also needs the **naming conventions** to apply and an
> **enumerated domains-and-permissions table** - see `security-setup-section.md`, which pulls
> the recipes below together with the naming block and the domain table into the one section a
> guide ships.

## How to use this library

1. Pick the recipes your app actually needs (Extend BO app vs. O4I integration need
   different subsets - see the dependency map).
2. Copy the recipe into the app's setup guide.
3. Replace every `<PLACEHOLDER>` (e.g. `<APP DOMAIN NAME>`, `<INT ID>`) with this app's
   real value. Fill a **Program defaults** block once at the top of the guide for values
   that repeat (tenant aliases, security-group names, notification distribution list).
4. Anything a source could not pin down exactly is marked **(!) confirm exact label
   in-tenant** - leave that note in for the admin, don't guess.
5. Workday task names occasionally differ by tenant release. When a recipe gives two
   names ("A" or "B"), the admin should search both.

## Dependency order (what must precede what)

Do the steps in this order. Skipping order is the #1 cause of "the app is broken" false
alarms.

```
0. Deploy / promote the app to this tenant            (prerequisite - see promotion-and-environments.md)
      |
      +- Extend BO app path -----------------------------------------------
      |   1. Provision/confirm the security groups     (client owns names)
      |   2. R1  Grant the app's security domain(s) to the group(s)
      |   3. R2  Activate Pending Security Policy Changes         <- unblocks S22
      |   4. R7  Configure each Business Process definition / approver chain
      |   5. R8  Set each App Attribute to this tenant's value (WID via WQL)
      |   6. (if external REST/WQL) R6 Register API Client + Refresh Token
      |
      +- O4I integration path ---------------------------------------------
          1. R9  Generate/register SSH & PGP keys (do the NOT-migratable ones in the master tenant first)
          2. R3  Create the ISU
          3. R4  Create the ISSG -> add the ISU -> grant its integration domains
          4. R2  Activate Pending Security Policy Changes            <- nothing takes effect until this
          5. R5  Create the Integration System -> map the ISU credential
          6. R8b Create/fill Integration Attributes (per environment) - DEVELOPER does this, not the client admin
          7. R10 Configure Integration Notifications
          8. R11 Schedule / Launch the integration (test tenant first, validation mode)
```

Key precedence rules:
- **R3 (ISU) before R4 (ISSG)** - the ISSG recipe adds the ISU as a member, so the ISU must exist first.
- **R2 (Activate) after every domain grant** - R1 and R4 both end by pointing at R2. Grants are invisible until activated.
- **R9 not-migratable keys / R6 API clients before the tenant that needs them** - API clients, PGP private keys, and x509 private key pairs **do not migrate** (private pairs cannot migrate up to Production); create them in the master tenant / Production so a later refresh carries them down (see those recipes).
- **R5 (Integration System) after R3/R4** - you assign the ISU to the integration system, so it must exist.

### Symptom -> the step you missed (the reverse index)

The order above answers "what do I do next?". This answers the question you actually arrive
with: "I have this error - which step did I miss?" Observed on a copied Extend app
(field-observed Sep 2026, one engagement's dev tenant).

| What you see | What was missed | Recipe |
|---|---|---|
| "You are not authorized to access this page" on EVERY page | The domain security policy was never created or activated | R1 + R2 |
| BO data calls return S22 "permission denied" | A domain grant is missing or not yet activated | R1 + R2 |
| A 500 with a null response body on every `isuAuth` endpoint | The app has no ISU assigned in App Manager (an ISU binds to one app per tenant - a copy needs its own) | R3, then assign it in App Manager (see also R6) |
| Orchestrations fail with an empty endpoint, client id or secret | App Attributes were never set for this tenant | R8 |
| "Business Process Definition Error" lands in My Tasks | The BP type exists but has no definition in this tenant | R7 |
| The app is missing from tenant search | No launcher exists | A source-side `.task` file (wd-extend-dev model.md); R12 only as a fallback |

The ISU 500 and the BP Definition Error point nowhere near their cause - check this table
before debugging code.

---

## R1 - Grant a security domain to a security group  (X) THE BLOCKING STEP

> This is the one everyone forgets and then thinks the app is broken. **Until this is done
> and activated (R2), every business-object data call returns an S22 "permission denied"
> error.** Pages may still load; the data will not.

**Workday task:** `Maintain Permissions for Security Group` - **or** open the domain
directly with `View Security for Securable Item` and use its related action **Domain ->
Edit Security Policy Permissions**. (Confirmed 2026-08-03: **either route accomplishes the
task** - use whichever the admin prefers.)

**When to use:** after the **first** deploy of the app to a tenant, and again after every
`wdcli app copy` (a copy is a new app with new domains).

**Prerequisites:** the app is deployed (Step 0); the target security group exists
(R4 for an ISSG; a role-based group for user access - client-provisioned).

**Steps:**
1. In the Workday search bar, type the task name above and open it.
2. Find the app's security domain by its exact name: `<APP DOMAIN NAME>` (e.g. an app
   declares one domain per `.securitydomain` file - list them all; a delivered Extend app
   used as an example declared a Data domain for its business-object data and a Pages
   domain for its PMD pages).
3. On that domain, choose the action to **edit the security policy permissions**.
4. Under **Report/Task Permissions** (for the page/UI/report side), add the security group
   `<SECURITY GROUP NAME>` with **View and Modify** access.
5. Under **Integration Permissions**, add the same group with **Get and Put** access.
   (Integration Permissions govern **SOAP web services only**; REST API calls - including
   BO REST and WQL - are governed by the Report/Task View/Modify permissions in step 4,
   for ISUs and humans alike. Grant both sets regardless. Per Workday Admin Guide
   (Integrations), Jul 2026.)
6. Click **OK / Done** to save the policy edit. (This only *stages* the change.)
7. **Now run R2 (Activate Pending Security Policy Changes).** The grant does nothing until
   you do.

**You're done when:** after R2, a signed-in test user in `<SECURITY GROUP NAME>` can open
the app **and** load business-object data (a grid/list populates instead of erroring), and
an integration Get/Put against the app's collection succeeds.

**If you skip it (or skip R2):** business-object data calls fail with **S22 "permission
denied"** even though pages render - the classic "looks deployed but nothing works"
symptom.

**Fill-in:** `<APP DOMAIN NAME>` (one per `.securitydomain`), `<SECURITY GROUP NAME>`
(a test group your test user is in for early testing; the real role-based / ISSG groups
for UAT and PROD).

---

## R2 - Activate Pending Security Policy Changes  (its own step - the one everyone forgets)

> Every security-policy edit in Workday is **staged**, not live. This task publishes all
> staged changes at once. It is a separate, easy-to-forget step and the reason a
> "completed" grant still shows S22.

**Workday task:** `Activate Pending Security Policy Changes`

**When to use:** immediately after **any** domain grant, ISSG permission change, or other
security-policy edit (i.e. the last step of R1 and R4).

**Prerequisites:** you have made at least one security-policy change this session.

**Steps:**
1. Search for `Activate Pending Security Policy Changes` and open it.
2. Review the list of pending changes shown (confirm your domain/group edits appear).
3. Enter a **Comment** describing the change, e.g. `<APP/INT NAME> security setup`.
4. Click **OK**, then **Confirm** on the confirmation screen.

**You're done when:** the task completes and the pending-changes list is empty; the grant
from R1/R4 now actually takes effect (re-test the data call - S22 should be gone).

**If you skip it:** every grant you just made stays invisible. Symptoms look identical to
"I never granted the domain at all" (S22 / 403), which sends people re-doing R1 in
confusion.

**Scope & rollback (per Workday Admin Guide (Authentication & Security), Jul 2026):**
- Only **security-policy** changes are staged pending activation (domain/BP policy grants,
  enabling domains/functional areas, delegation). **Security-group definitions and
  user<->group assignments take effect immediately** - no activation needed. So R4 step 5
  (adding the ISU to the ISSG) is live at once; the domain grants are not.
- Preview what's pending before activating: **Domain Security Policies with Pending
  Changes** / **Business Process Security Policies with Pending Changes** reports.
- **Rollback:** `Activate Previous Security Timestamp` reverts the tenant to a prior
  security configuration (pick the timestamp from the **View All Security Timestamps**
  report). Timestamps after the reverted point become invalid - this is a rewind, not an
  undo of one change.

---

## R3 - Create an Integration System User (ISU)

> The ISU is a **service account** the integration runs as when scheduled. It is never
> used by a person and must not expire, or the nightly run silently dies.

**Workday task:** `Create Integration System User`

**When to use:** once per integration system, per tenant, before the integration's first
run.

**Prerequisites:** you have security-administration access in the tenant.

**Steps:**
1. Search for `Create Integration System User` and open it.
2. In **User Name**, enter `<ISU USER NAME>` (e.g. `ISU_INT####`; the design-doc long-form
   reference is `ISU <INT ID> <Description> <Type> <Direction>`).
3. Set a **strong, generated password** and store it in the project password vault. Do not
   reuse another ISU's password.
4. Check **Do Not Allow UI Sessions** (this account should never log into the UI).
5. Set **Session Timeout Minutes** to `0` (Workday auto-populates 0 for ISUs - leave it;
   no idle-timeout for the service account).
6. Click **OK** to create the user.
7. Search `Maintain Password Rules` and add this ISU to the field literally named
   **"System Users Exempt from password expiration"**, so a rotating password never
   silently breaks a scheduled run.

**You're done when:** the ISU exists, cannot open a UI session, has no session timeout, and
appears on the password-expiration exempt list.

**Doc notes (per Workday Admin Guide (Integrations), Jul 2026):** the settings above
(Session Timeout 0, Do Not Allow UI Sessions, the password-expiration exemption) are
verbatim official guidance, not just house practice. Each ISU can be tied to a **single
integration system only** - official backing for the one-ISU-per-integration naming
standard. Also: the ISU's **locale and display-language preferences control the language
integration data is extracted/saved in** - set them deliberately for multi-language tenants.

**Extend apps - one ISU per app (field-observed Sep 2026, one engagement's dev tenant):** an
ISU can be assigned to only ONE Extend app per tenant. App Manager's Add-ISU prompt lists only
unassigned ISUs, so an ISU already in use just returns **"No matches found"**. A copied app
needs its own ISU - create one here for the copy (same ISSG as the parent's) - see wd-extend-dev
`security-setup.md`.

**If you skip it (or skip the exempt list):** the integration has no identity to run as; or
worse, it runs fine for weeks and then the ISU password expires and every scheduled run
fails with an auth error that looks like a code bug.

**Fill-in:** `<ISU USER NAME>` (per naming standard - see wd-extend-dev
`integration-naming.md`, "one ISU per integration system").

---

## R4 - Create an ISSG, add the ISU, and grant its integration domains

> An Integration System Security Group (ISSG) is the **bucket that holds the ISU** and
> carries the domain permissions the integration needs (its Get/Put access).

**Workday tasks:** `Create Security Group` (to create it); `Maintain Permissions for
Security Group` **or** related action **Security Group -> Maintain Domain Permissions for
Security Group** (to grant domains); optionally **Integration IDs -> Edit Reference ID** to
set the ISSG's reference ID to the naming standard.

**When to use:** once per integration system, per tenant, **after** the ISU exists (R3).

**Prerequisites:** R3 done (the ISU to add as a member).

**Steps:**
1. Search for `Create Security Group` and open it.
2. Set **Type** = `Integration System Security Group (Unconstrained)`.
3. Set **Name** = `<ISSG NAME>` (e.g. `ISSG <INT ID> <Description> <Type> <Direction>`).
4. Click **OK**.
5. On the group, in the **Integration System Users** field, add the ISU `<ISU USER NAME>`
   from R3 as a member. **Save.**
6. Open `Maintain Permissions for Security Group` (or the group's related action to
   maintain domain permissions).
7. Add each domain the integration needs, with the access level shown, under **Integration
   Permissions** (Get and/or Put):
   - `<DOMAIN 1>` - `<Get / Put>`
   - `<DOMAIN 2>` - `<Get / Put>`
   - (For a Workday SOAP web-service call, the securing domain is the one that secures that
     web service. To find it exactly: search `View Security for Securable Item`, look up the
     web-service operation, e.g. `<WEB SERVICE OPERATION> (Web Service)`, and grant whatever
     domain(s) it lists. (!) Trust that lookup over any static list - domain names differ by
     tenant version. If the lookup shows **no domain** at all, the operation is secured by a
     **business process security policy** - check the BP security policy instead. Per Workday
     Admin Guide (Integrations), Jul 2026.)
8. (Optional but standard) Set the ISSG's reference ID via **Integration IDs -> Edit
   Reference ID** to match the naming standard.
9. **Run R2 (Activate Pending Security Policy Changes).**

**You're done when:** after R2, the ISU (via this ISSG) can perform the Get/Put the
integration requires - the integration's first run reaches Workday without a 403/permission
error.

**If you skip it:** the ISU exists but has no permissions; the integration authenticates but
every Workday call fails with a permission error (403 / access denied), typically on the
first `Send Workday API Request`.

**Fill-in:** `<ISSG NAME>`, `<ISU USER NAME>`, the `<DOMAIN n>` list with each Get/Put.
Typical Extend-orchestration domains for FDM writes are the functional areas the
orchestration calls (e.g. Financial Management, Resource Management, Staffing); a delivered
integration example granted **Process: Supplier Invoice**, **Integration Event**,
**Integration Process**, and **Integration Debug (Get)**.

---

## R5 - Create / attach the Integration System and map the ISU credential

> The Integration System is the tenant object that **wraps the deployed orchestration** so
> it can be launched, scheduled, secured, and configured. It also holds the environment
> configuration (Integration Attributes, R8b) and is where you tell Workday which ISU to
> **run as**.

**Workday task:** `Create Integration System`

**When to use:** once per O4I integration, per tenant, after the app is deployed (Step 0)
and the ISU/ISSG exist (R3/R4).

**Prerequisites:** app deployed to this tenant; R3 (ISU) done.

**Steps:**
1. Search for `Create Integration System` and open it.
2. Set **System Name** = `<INT ID> <Vendor> <Description> <Type> <Direction>` and **System
   ID** = `<INT_ID_UNDERSCORED>` (from the design doc; use exactly).
3. For the **template**, choose template type **`Orchestrate Integration Template`**
   (confirmed 2026-08-03) - the delivered Workday template for orchestration-based
   integrations. You point it at the app's main orchestration `<ORCHESTRATION NAME>` and
   supply the run configuration through the **Integration Attributes** (R8b), not on this
   screen. (If the deploy didn't finish or your user lacks Extend security, the app/
   orchestration won't be selectable - re-check Step 0 before escalating.)
4. Click **OK**.
5. Map the ISU credential (confirmed 2026-08-03): on the integration system, related action
   **Workday Account -> Edit**; on the next screen add the ISU `<ISU USER NAME>` from R3 in
   the account listbox/dropdown and click **OK**. For an Extend orchestration that references
   `_DEFAULT_WORKDAY_CREDENTIAL`, this ISU is the identity that credential resolves to.

**You're done when:** the integration system exists, points at the correct orchestration,
and shows the ISU as its run-as / Workday account credential.

**If you skip it:** there is nothing to schedule or launch; or it runs as the wrong identity
and fails on permissions.

**Gotchas (build-verified 2026-09-08, UAP v2 rollback IS setup):**
- **One ISU per Integration System -- Workday enforces 1-to-1.** A single ISU can back only ONE
  integration system; assigning it to a second IS via `Put_Integration_System` fails. Each
  orchestration IS needs its own dedicated ISU (create a separate ISU in R3 for each IS you add).
- **ISU attach often requires a second call.** The owner ISU cannot always be set in the same
  `Put_Integration_System` call that creates the integration (service context not established); the
  Workday SOAP call accepts the template + service + binding but rejects the ISU field on first
  create. Pattern for scripted setup: (1) `Put_Integration_System` without ISU_Reference to create;
  (2) a second `Put_Integration_System` (Add_Only=false, all fields included) to attach the ISU.
  Always include ALL three on both calls (template, service, ISU) to avoid silent-clear
  (Add_Only=false is a FULL replace - omitting Template/ISU/Services clears them).
- **IS --> orchestration binding lives in `Integration_Attributes_Data`.** When creating an IS that
  backs an Orchestrate integration, the specific orchestration is bound via an
  `Integration_Attributes_Data` block containing `Orchestration Name = <orchName>` and
  `Application Reference ID = <appReferenceId>`. To bind a new IS to a different orchestration,
  replicate this block with the new orchestration name; the `Integration Deployed Orchestrate Service`
  WID is the same across all apps and is NOT the discriminator.

**Fill-in:** `<INT ID>`, `<INT_ID_UNDERSCORED>`, `<ORCHESTRATION NAME>`, `<ISU USER NAME>`.

---

## R6 - Register an API Client and create a Refresh Token (external BO REST / WQL)

> This is only needed when something **outside** Workday needs to call the app's
> business-object REST API or WQL (test scripts, an external integration, a Python client).
> In-orchestration Workday calls do **not** need this - they auto-authenticate through the
> ISU on the integration system.

> **Cross-ref (keep in sync):** this recipe is the click-level HOW; the auth-mode / why lens
> for this same task (refresh_token vs PKCE vs basic, when to use which, credential storage)
> lives in `wd-auth/references/oauth-setup-guide.md`. They are complementary - update both
> together so they cannot diverge.

> **(!) Not migratable.** An API Client does **not** promote between tenants. Create it in
> the **master tenant** (the one refreshes flow down from); after the next planned refresh
> it will be present in the downstream tenant. Plan this ahead of the tenant that needs it.

**Workday task (confirmed 2026-08-03):** **`Register API Client for Integrations`** - the
house standard for **any** Extend app or integration. This ONE task registers the client
against a chosen ISU **and** issues the refresh token in the same step (grant type =
refresh_token), so you don't chase a separate secret/token task. (`Generate New API Client
Secret` exists only to *rotate* the secret later; the plain `Register API Client` is the
Authorization-Code-grant path for interactive/browser apps - not our pattern for
server-to-server BO REST/WQL.)

**When to use:** when external REST/WQL access is required, per tenant (via the master
tenant), before that external caller runs.

**Prerequisites:** you hold the **Tenant Setup - Security** / **Security Administration**
setup access (the System functional-area domains that gate API-client registration); the
ISU the client will run as exists (R3).

**Steps:**
1. Search for `Register API Client for Integrations` and open it.
2. Set **Client Name** = `<CLIENT NAME>`.
3. Select the **ISU** `<ISU USER NAME>` (from R3) this client runs as - the refresh token is
   bound to this user's access.
4. Set **Non-Expiring Refresh Tokens** (for an unattended caller that must never re-auth),
   **or** a **Refresh Token Timeout (in days)** `<1-365>` if it should expire.
5. In **Scope (Functional Areas)**, select only the functional areas the client truly needs
   (include the functional area of the app's custom domain if calling BO REST). Use
   **Include Workday Owned Scope** only if core non-functional-area domains are required.
6. (Optional, PROD-hardening) Set **Restricted to IP Ranges** and/or **Allowed Origin**.
7. Click **OK**. Record the **Client ID**, the **Client Secret**, and the **Refresh Token**
   in the vault - the secret and token are shown **once**.
8. Record the **token endpoint** for this tenant: `{base}/ccx/oauth2/{tenant}/token`.

**Token rotation/regeneration (per Workday Admin Guide (Authentication & Security), Jul
2026):** related action **API Client -> Manage Refresh Tokens for Integrations** - delete
and/or generate a new refresh token there. Max **1 refresh token per client + account
pair**, so generating a new one supersedes the old; re-vault it.

**You're done when:** an external caller can POST `grant_type=refresh_token` +
`refresh_token` + `client_id` + `client_secret` to the token endpoint, receive an
`access_token`, and use it as `Authorization: Bearer <token>` on a BO REST / WQL call that
returns data. (Cache the token and re-mint when older than ~15 minutes.)

**If you skip it (or try to migrate it):** external REST/WQL calls get 401/invalid-client;
and because API clients don't migrate, a client that "worked in DEV" is simply **absent**
in the promoted tenant until you register it there (via the master tenant) - a very common
promotion surprise.

**Fill-in:** `<CLIENT NAME>`, `<ISU USER NAME>`, timeout vs non-expiring, scope functional
areas, `{base}`/`{tenant}`.

---

## R7 - Configure a Business Process definition / approver chain

> The Extend source declares only a **single** approval step. The real multi-step approver
> routing lives on the **BP definition in the tenant** - you configure it here, per tenant,
> after deploy.

**Workday tasks:** `Edit Business Process` (edit the delivered custom BP's definition);
to create/copy/link a definition, related action **Business Process -> Create, Copy, or Link
Definition**.

**When to use:** once per custom BP, per tenant, after the app is deployed.

**Prerequisites:** app deployed; the security groups that will act as approvers exist
(client-provisioned).

**Steps:**
1. Search for `Edit Business Process` and select the app's custom BP `<BP NAME>`.
2. Add each approval/step in order, assigning the responsible group per the design doc:
   - Step 1 -> `<APPROVER GROUP 1>`
   - Step 2 -> `<APPROVER GROUP 2>`
   - ... (include any **conditional** steps and their condition, e.g. "only when
     `<CONDITION>`").
3. Set the **initiation security** (who may submit) = `<INITIATOR GROUP>`.
4. If the BP supports **Send Back / Revise**, confirm the revise route maps to the app's
   revise page (the Extend source must already declare the revise page route).
5. Save the definition.
6. Repeat for each custom BP the app declares.

**You're done when:** submitting the app's create/action task launches the BP and it routes
to the **configured first approver's inbox**; approve/deny/send-back behave as designed.

**If you skip it:** the BP either won't launch, routes to no one (stuck in the initiator's
inbox), or approvals go to the wrong role.

**Fill-in:** one row per `<BP NAME>` with its full ordered `<APPROVER GROUP n>` chain and
`<INITIATOR GROUP>` (build these from the design doc's BP-routing table).

---

## R8 - Set an App Attribute to this tenant's value (find the WID via WQL)

> An **App Attribute** holds a value the app reads at runtime that **differs per tenant**
> (most often an instance **WID**, since WIDs are tenant-specific). The app ships with the
> build tenant's defaults, so it *appears* to work - but against any other tenant those
> defaults are wrong. This is the most-missed step because the failure is silent.

**Workday task (confirmed 2026-08-03):** search `App Manager`, open the deployed app, and
choose **Configure** (the app) -> its **App Attributes** - set each attribute's value there,
per tenant.

**When to use:** each tenant, at deploy, for every attribute whose default belongs to a
different tenant.

**Prerequisites:** app deployed; you can read WIDs in this tenant (WQL access).

**Steps:**
1. Identify each App Attribute the app declares and what instance it points at
   (e.g. `<ATTRIBUTE NAME>` -> "this tenant's `<THING>` WID").
2. Find **this tenant's** WID for that instance with a WQL query. Example for an
   org-subtype WID: run `SELECT subtype FROM customOrganizations` and read each
   `subtype.id`. (Generalize: `SELECT <field> FROM <dataSource> [WHERE ...]`, then read the
   returned instance's `.id`.) You can run WQL via the tenant's WQL tooling or
   `GET https://api.us.wcp.workday.com/wql/v1/data?query=<url-encoded query>`.
3. Search `App Manager`, open the app for this tenant, and choose **Configure**.
4. In the app's **App Attributes**, set `<ATTRIBUTE NAME>` to the WID you found. Save.
5. Repeat for each tenant-specific attribute.

**You're done when:** each attribute holds **this tenant's** value (not the build tenant's
default), and a feature that depends on it (e.g. a picker filtered by that WID) returns the
correct data in this tenant.

**If you skip it:** the app runs on the **wrong tenant's** defaults - pickers come back
empty or wrong, with no error. Everyone assumes the feature is broken; it's just pointing at
another tenant's instance.

**Fill-in:** one row per `<ATTRIBUTE NAME>` with its WQL lookup and the tenant's WID.

**Adding attributes to an app that already has a configuration (field-verified 2026-10-03,
one engagement's dev tenant):** a deploy that adds attributes to `default.attributes` does NOT
add them to the existing configuration. **Edit** on the configuration keeps listing only the old
attributes. Run
**Update App Configuration** (the card under Configurations) -> tick **Confirm** -> **OK** first.
That re-syncs the attribute list and KEEPS every existing value, secrets included (verified by
count, and the app still authenticated afterwards). Then **Edit** shows the new rows. Each
value goes in through the row's **+** (Add Row) button inside the Values sub-grid.
- **Browser-pane tip:** the edit grid is unusable at a narrow pane width. Follow the one
  viewport rule in wd-tenant-config `test-data.md` ("Browser mechanics"): act by a fresh ref
  where you can. If the grid needs more width, emulate a MODERATE width the pane can show
  unscaled (a large one renders at ~25% and clicks miss), switch the grid to full-screen,
  re-`find`, and confirm the screenshot's scale before clicking each row's **+** by coordinate.
  Then click into the new value box and type. Check the text actually landed before OK (`find`
  the value).
- **Don't dump page text on this form.** `get_page_text` prints secret values (client secret) in
  clear. Check values with targeted `find` calls instead.
- The App Details "Installation Status: Not Configured" badge refers to the Configuration
  Package, not to attribute values. It stays the same after values are set.

### R8b - sibling: Integration Attributes (O4I integration systems) - **DEVELOPER task, not client admin**

An **O4I integration system** uses **Integration Attributes** (not App Attributes) for its
per-environment config. **Confirmed 2026-08-03: the Extend/integration developer configures
these in the tenant, not the client security admin** - so this belongs in the developer's
tenant-setup steps, NOT in the client-admin instruction sheet (unless a future release lets
you package the values as promotable configuration). Task: on the integration system,
related action **Integration System -> Configure / Maintain Integration Attributes**, then
edit values (exact label varies by version). The orchestration reads them by **exact name**
via `intsys.stringAttributeValue("<Attribute Name>")` - **the name must match exactly**
(same spelling, capitalization, spaces) or you get a runtime failure that looks like a
missing value. Create the attributes with `TBD` placeholders if a value is blocked, and edit
values as they arrive. Treat secret values (tokens) like passwords - vault them, don't email.

---

## R9 - Generate / register SSH & PGP keys for integrations

> File-based integrations use keys: an **SSH key pair** to authenticate the SFTP
> connection, and **PGP keys** to encrypt/decrypt files. **Which ones migrate matters** -
> get the non-migratable ones created in the master tenant first.

**Workday tasks (per key type):**
- `Create x509 Private Key Pair` - the SSH key pair for SFTP authentication (share the
  RSA-SSH public portion with the vendor).
- `Create PGP Public Key` - the vendor's public key, used to **encrypt outbound** files.
- `Create PGP Private Key Pair` - Workday's key to **decrypt inbound** files (give the
  public half to the file sender).
- `Create X509 Public Key` - the vendor's public key for **SAML/SSO** authentication.

**When to use:** before the integration's SFTP/encryption business-process step is
configured (R5's BP delivery/retrieval step references these).

**Migratable vs. not - plan around this:**

| Key | Task | Migrates? | Where to create |
|---|---|---|---|
| SSH x509 Private Key Pair (SFTP auth) | `Create x509 Private Key Pair` | **Not migratable to Production** - a pair created in a non-Production tenant cannot be migrated to Production | **Production** - Sandbox inherits Prod's keys via the weekly refresh |
| PGP Public Key (encrypt outbound) | `Create PGP Public Key` | **Migratable** | Any tenant |
| X.509 Public Key (SAML/SSO) | `Create X509 Public Key` | **Migratable** | Any tenant |
| PGP Private Key Pair (decrypt inbound) | `Create PGP Private Key Pair` | **Not migratable** | **Production** (the master tenant refreshes flow down from) - present downstream after the next planned refresh. (!) A PGP private pair created in **Sandbox is deleted at the next weekly service update** |
| ISU passwordless WWS auth (assign an x509 public key or SAML token to the ISU) | `Configure Web Service Security` | Tenant config - re-do per tenant | Each tenant the integration runs in |

> **Correction (per Workday Admin Guide (Integrations), Jul 2026):** the x509 private-key
> row previously read "Migratable - available in any IMPL tenant right away" (house-checklist
> sourced). Official guidance is the opposite: **create x509 private key pairs in
> Production** - non-Production-created pairs cannot migrate to Production. Same
> create-in-Prod guidance applies to PGP private pairs.

**Regeneration & expiry mechanics (per Workday Admin Guide (Integrations), Jul 2026):**
- Rotate a key: **View x509 / PGP Private Key Pair** report -> related action ->
  **Regenerate Key Pair** -> Confirm -> re-send the new public half to the partner.
- An optional **Do Not Allow Regeneration** checkbox at creation locks a pair against
  accidental rotation.
- Expiry-notification recipients need **Enable Security Emails** + a valid work email +
  **Modify on Security Administration** - all three, or the 30/15/7-day warnings reach no one.
- PGP vendor certs must be **self-signed SHA-256**; Workday only generates **RSA-2048**
  x509 pairs - tell the vendor up front.

**Steps (generic, per key):**
1. Search for the matching `Create ...` task above and open it.
2. Name the key per the naming standard: `EK <INT ID> <Key Type> <Audience>` (e.g. an
   encryption key's public half), and set the reference ID accordingly.
3. Provide/generate the key material (paste the vendor's public key, or generate the pair).
4. Save; export/share the public portion with the vendor where the recipe above says to.
5. For the **not-migratable** private key pairs (PGP Private Key Pair AND the x509 private
   pair), do this in **Production** (the master tenant refreshes flow down from) so a later
   refresh carries it downstream - a non-Prod-created pair cannot be migrated to Production.
6. Ensure **Enable Security Emails** is on so Workday's expiry notifications (30/15/7/<7
   days) actually reach someone - keys expire and break integrations silently otherwise.

**You're done when:** each required key exists with a standards-compliant name/reference ID,
the vendor has whatever public half they need, and the not-migratable private key is present
in the master tenant.

**If you skip it (or create a non-migratable key in the wrong tenant):** SFTP auth fails,
or encrypted files can't be produced/decrypted; and a PGP **private** key created only in a
downstream tenant will be **missing after the next refresh** - the inbound decrypt breaks
with no obvious cause.

**Fill-in:** `<INT ID>`, key names/reference IDs, vendor public keys.

---

## R10 - Configure Integration Notifications  (bonus, O4I)

> The orchestration writes ERROR messages into the integration event; a **notification** is
> what makes a human actually look when a run fails.

**Workday task (confirmed 2026-08-03):** on the integration system, related action
**Integration Notification -> Configure Integration Notifications**.

**Steps:**
1. Open the integration system's related action to create an integration notification.
2. Create one notification with **Trigger Status** = **Failed** and **Aborted**.
3. Create a second with **Trigger Status** = **Completed with Errors**.
4. Set **Recipients** = `<SUPPORT DISTRIBUTION LIST>`.
5. Set the **Subject** and **Body** - use the standard calc fields `CF CT Integration
   Notification Message Content - Subject` and `CF CT Integration Notification Message
   Content - Body` unless a custom message is specified; the body should tell the recipient
   to open the integration event and read the ERROR messages.

**You're done when:** a deliberately failed test run emails `<SUPPORT DISTRIBUTION LIST>`.

**If you skip it:** failures accumulate silently in the event log; no one is alerted until
someone downstream notices missing data.

**Doc notes (per Workday Admin Guide (Integrations), Jul 2026):**
- Securing domain for this configuration is **Integration Build**.
- If the integration is connected to a business process, Workday recommends **BP
  notifications instead** of integration notifications - avoids duplicate messages.
- Do NOT select trigger statuses that never apply to integrations: **Initiated, Purged,
  Queued, Skipped, Throttled** - they just clutter the config.
- **Preview** sends a sample message showing **field names, not values** (routed per the
  Alerts setting in Edit Tenant Setup - Notifications) - useful for testing the recipient
  list without a real failure.
- Links to output files in the email require an **Integration Event Email template** with
  the **"Attachment Links"** dynamic content.

---

## R11 - Schedule / launch the integration  (bonus, O4I)

> Runs the integration on a schedule as the ISU. **Test-tenant first, validation mode
> first.** Do not schedule PROD until end-to-end testing passes and the go-live date is
> agreed.

**Workday task:** `Launch / Schedule Integration`

**Steps (smoke test -> schedule):**
1. Search `Launch / Schedule Integration`, pick the integration system `<INT ID> ...`.
2. **First run:** choose **Launch now** with the launch parameters `Validation Mode = true`
   and `Debug = true` (validation mode sends a validate-only request and skips any external
   status write; debug adds detail messages).
3. Open the event (search `Process Monitor` or follow the launch link) and confirm the
   expected INFO/summary messages and **no ERROR** messages.
4. Re-run with `Validation Mode = false` **in the TEST tenant only**, and verify the real
   outcome (record created in Workday, source system updated, and a re-run retrieves zero).
5. **To schedule:** choose **Schedule**, set frequency/time (avoid the tenant's heavy
   nightly windows), and set **Run As User** = the ISU `<ISU USER NAME>`.
6. Set schedule launch parameters `Validation Mode = false`, `Debug = false`. Leave the
   schedule **disabled/suspended** (or test-tenant only) until go-live.

**You're done when:** a validation-mode run is clean, a live test-tenant run produces the
correct result and a safe zero-record re-run, and the schedule is defined as the ISU
(disabled until go-live).

**If you skip it (or schedule too early):** an untested integration runs against real data;
or it runs as the wrong user and fails on the permissions from R4.

**Fill-in:** `<INT ID>`, `<ISU USER NAME>`, run time.

**Scheduling doc notes (per Workday Admin Guide (Integrations), Jul 2026):**
- Workday recommends start times **off the top of the hour** (everyone schedules :00 -
  contention); prioritization among same-start-time integrations is configured on **Edit
  Tenant Setup - Integrations**.
- The scheduling user **owns the schedule**. If that owner's security later becomes
  insufficient, runs show **"Not Run due to Exceptions on Future Process"** - one more
  reason Run As User = the ISU, and to keep the ISU's grants intact.
- Schedule around the **Weekly Service Update (WSU)**: runs in flight when the WSU begins
  are **auto-restarted afterward** - a double-send/double-load risk for non-idempotent
  integrations (and some templates and Run-Once schedules are NOT restarted at all). Runs
  scheduled inside the window simply start late.

---

## R11b - Integration-event triage toolkit  (ops reference, per Workday Admin Guide (Integrations), Jul 2026)

Not a setup recipe - the related actions and reports a support admin reaches for when a
run misbehaves. Keep with the support-ownership matrix / hypercare runbook.

- **Relaunch Integration Event / Re-Deliver Document** (related actions on the event):
  only available on events **less than 30 days old**; redelivery is capped at **5
  deliveries per event** and always uses the **current** transport configuration (a
  changed SFTP endpoint applies retroactively to redeliveries).
- **Integration Event -> Verify Status** refreshes a stuck status; events in progress
  **longer than 7 days are auto-failed** by Workday.
- **Force Failure**: only offered after **>=2 hours** of runtime; it marks the event failed
  but does **NOT stop running runtime jobs** - the work may still complete underneath.
- Bulk operations (relaunch / redeliver / abort across many events): the **Mass Action on
  Integration Events** report - runs gradually in the background.
- **Integration Event -> Retrieve Technical Files** pulls the event's documents/schema
  files for troubleshooting.
- A Workday-tenanted ISU named **"Verify Status"** background-checks event statuses - it
  is delivered plumbing; do NOT flag it as an orphan in security audits (R4-style reviews).
- Deleting an integration (`View Integration System` -> related action **Delete**) also
  deletes its **scheduled future processes**; requires Integration Build + the
  integration's functional-area domain (for EIBs: **Integrations: EIBs**).

---

## R12 - Instance-contextual custom task for an Extend app (Create Custom Task)

> House standard first: to make an app searchable by name, ship source-side `.task`
> model files - plain launchers, one per landing route, deploy with the app, no tenant
> work needed (wd-extend-dev model.md; build+deploy verified 2026-08-06). This recipe's
> screen is a DIFFERENT tool: **Create Custom Task builds an instance-contextual launch**
> - it asks for a Route Path plus a **Business Object** (and "is the select secured"),
> because it opens an app page in the context of a specific BO instance (e.g. from a
> Worker's related actions). Use it for exactly that. If you find yourself hunting for a
> Business Object value just to make a plain "open the app" entry point, stop - that's
> the signal you want a `.task` file and a redeploy instead. Fallback only: if a redeploy
> is truly off the table for a deployed app, this screen can serve as a launcher, but
> repeat it per tenant - custom tasks do not promote with the app.

**Workday task:** `Create Custom Task`. Where it lives differs by tenant release, so carry
both routes:
- **Primary - tenant search** (field-observed Sep 2026, a dev tenant): search `Create Custom
  Task`. On that tenant the App Details page ended at its Business Processes section - no
  Configurations tab, no tile.
- **Alternate - App Manager** (practitioner-confirmed 2026-08-05): App Manager -> the app ->
  **Configure** -> **Configurations** tab -> **Create Custom Tasks** tile.

**Steps:**
1. Search the tenant for `Create Custom Task` and open it.
2. If search does not find it, use the App Manager route above instead.
3. The form asks for a good bit of information - fill it deliberately (guidance below),
   don't accept blanks or defaults you don't understand.
4. Under **Security -> Domains**, pick the app's usage domain(s), and turn **Testing Mode
   Only** off (trap below). The groups holding those domains decide who can FIND the task in
   search.
5. Test as a real end user (not an admin): type the app name in Workday search and confirm
   the task appears and lands on the app home page.

**What to fill in (house guidance per field family):**
- **Task name/label:** the app's name AS USERS SAY IT - the words they'd type in search
  (e.g. `Expense Requests`), not the technical app/reference ID. If users know it by more
  than one name, put the alternates in the description/keywords so search still hits.
- **Description:** one plain-English sentence of what the user DOES there ("Request and
  track expense reports") - it shows in search results and doubles as the
  user's first impression; write it for the end user, not the admin.
- **Target page/route:** the app's HOME page (the tiles landing page per the UX standard),
  not a task-specific subpage - users orient from Home.
- **Security:** the app's end-user domain(s) - the form takes **Domains**, and the groups
  holding them follow. Never an admin-only domain, or real users can't find the task at all
  (the #1 way this step silently fails).
- **Business Object + "is the select secured":** these fields are WHY this is the
  instance-contextual tool (confirmed on the form 2026-08-06) - the BO is the instance
  context the task launches from. If you're using this screen as a fallback plain
  launcher, the BO prompt has no natural answer - which is the tell you should be
  shipping a `.task` file instead.
- **Where an instance-contextual task surfaces (field-verified 2026-10-02, one engagement's dev tenant):** NOT in the
  BO's related-actions menu. A task on Job Requisition with "No selection" did not appear under the
  requisition's related actions (the Workday Extend submenu held only "View Security for Extend Related
  Instance"), and tenant search returns only its "Custom Task Definition". It becomes reachable as a tab
  once it is added to the BO's composite-view profile group (e.g. "Details for Job Requisition Composite
  View"). **Membership is set on the profile group, NOT on the task** (corrected 2026-10-03): the Edit
  Custom Task form has no Profile Groups field (a "Profile Groups" line on a task's view page only
  reflects membership), and the profile group does not come up in tenant search by name. Run the task
  **Configure Profile Groups** -> pick the group in its prompt -> OK -> add the custom task as a new row
  -> OK (source: the vendor deployment guide's "Add Custom Task to Profile Group" step). Adding a task to a delivered profile group changes shared tenant UI for everyone
  who can open that object - confirm with the tenant owner first. **Testing Mode Only** (on by default,
  permitted testers listed) limits who sees the task, which keeps a new tab away from other testers.
  Turn it off before anyone else needs the task - see the trap below.
- **The form's full field list (field-observed Sep 2026, a dev tenant).** No Description field
  appeared on that form, so put the user-facing wording in the Title:
  1. **Title**.
  2. **Reference ID** - accepts spaces and parentheses; working examples set it identical to
     the Title.
  3. **Application ID**.
  4. **Site ID** - the same value as Application ID.
  5. **Route Path**.
  6. **Business Object**, plus a **Secured / Unsecured / No selection** radio.
  7. **Usages:** Allowed on Custom Dashboards; Enable for Mobile App.
  8. **Security:** Domains; **Testing Mode Only**; Permitted Testers; and a derived, read-only
     **Security Groups Needed**.
- **Trap - Testing Mode Only DEFAULTS ON.** It reveals a Permitted Testers list prefilled with
  the creator alone. Left on, it is a SECOND access gate stacked on top of the domains and
  invisible from the security groups - so granting a new tester access the documented way (a
  domain grant) silently fails. Uncheck it to make the domains the single gate.
- **Free check:** with Testing Mode Only off, **Security Groups Needed** populates from the
  domain policies. A populated list confirms R1 and R2 were done right.

**You're done when:** a member of the app's user security group finds the app by name in
search and lands on Home.

**If you skip it:** every user needs a bookmark or App-Manager directions, adoption drags,
and the help desk fields "where is the app?" tickets.

**Fill-in:** `<App Display Name>`, description text, security domain name(s).

---

## Provenance note

Per-recipe source citations are consolidated here rather than repeated under each recipe.
Every recipe is grounded in one or more of: a delivered Extend app's tenant-setup
cheatsheet (`TENANT_SETUP.md`), a delivered O4I integration's client tenant-setup guide
(used here as an example), the integration build checklist workbook (Orchestration / API
Clients / SSH & PGP Keys / Build sheets), and the existing wd-deployment / wd-extend-dev
references. Where a source did not pin down an exact task label, the step is written
generically and flagged **(!) confirm exact label in-tenant** rather than inventing a name.

**Practitioner confirmations (2026-08-03):** R1 (either route works), R5 (template type =
`Orchestrate Integration Template`; ISU via **Workday Account -> Edit** -> add in dropdown ->
OK), R8 (`App Manager` -> **Configure** the app -> App Attributes), R8b (**developer**-owned,
not client admin), and R10 (**Configure Integration Notifications**) are practitioner-
confirmed - flags removed. **R6 also confirmed 2026-08-03:** the house standard is
**`Register API Client for Integrations`** for any Extend app or integration - one task
registers the client against the ISU and issues the refresh token together (no separate
secret/token step). All 7 review items are now practitioner-confirmed; no (!) flags remain.

**Admin-guide pass (Jul 2026):** doc-sourced notes marked "per Workday Admin Guide (...)"
were added from the official Integrations / Authentication & Security guides. One
correction replaced prior text (R9: x509 private key pairs must be created in Production -
they do NOT migrate up); everything else lands as additive notes, with practitioner-verified
recipe steps unchanged.
