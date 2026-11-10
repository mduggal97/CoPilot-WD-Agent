# Migrating an Extend app to a NEW developer tenant (dev-tenant expiry / refresh)

When a WCP development tenant approaches expiry (or the dev-tenant program is refreshed, e.g. wcpdev ->
custdev - see release-impact.md "Developer-tenant lifecycle"), your Extend apps do NOT move
automatically. This is the runbook to carry an app into a fresh dev tenant.

> Distilled 2026-08-12 from Workday's official Developer-forum post "Development Tenant Expiry Process"
> (forum.developer.workday.com topic 45231; login-gated - do not redistribute the source). Follow the
> linked Workday docs in the post for the exact UI/wdcli steps; verify against your release before relying
> on any detail here.

## Scope first - don't migrate everything

Migrate only what must stay deployed: apps **actively in development** and apps **already in production**.
Skip test apps, duplicates, and tutorial apps.

## The mental model - three buckets

1. **App source (AMD/PMD/Orchestrations)** - deploys with the app via **Save and Deploy**. The job here is
   to make it **tenant-agnostic** (no hardcoded IDs) so it installs cleanly anywhere.
2. **Tenanted artifacts** - the app depends on tenant-level config (reports, calc fields, security,
   integration systems, BPs, dashboards, custom tasks). Some can be **packaged and auto-installed** via
   **Reusable Tenant Configuration (RTC)**; the rest are **rebuilt by hand** in the new tenant.
3. **MCBO data** - data in the app's Model Component Business Objects does NOT deploy with the app; it is
   moved **separately** as its own migration.

## Phase A - prepare the app in the SOURCE tenant (before expiry)

1. **De-hardcode tenant-specific values -> App Attributes.** Find every hardcoded WID, Report ID,
   Integration System ID, and environment constant; create an **Application Attribute** for each value
   that differs by tenant; point AMD/PMD/Orchestrate at the attribute instead of the literal. Document
   each attribute (name, purpose, how to set it in a fresh tenant). This portability step is good design
   beyond migration.
2. **Inventory every tenanted artifact.** One master list: name, type (BP config, Integration System,
   ISU, dashboard, ...), purpose, dependencies (security roles, other artifacts), rebuild method (UI /
   API / EIB), and whether it is **required** for the app to function. This list drives Steps 3 and 8.
3. **Build Reusable Tenant Configuration (RTC) for the packageable artifacts.** RTC bundles supported
   tenant-level setups (e.g. custom reports, calculated fields) INTO the app package so they auto-install
   in the new tenant instead of being hand-rebuilt.
   - **Which qualify:** check the tenant's **Object Transporter Supported Objects (OX)** report. Listed
     type -> package it via RTC. Not listed -> it goes on the manual-rebuild list (Step 8).
   - **Prereq (both tenants):** Object Transporter enabled AND Customer Central set up.
   - Create the reusable tenant configuration in the source tenant, then add it to the app.
4. **Decide the MCBO data strategy (config vs transactional).**
   - Classify each MCBO: **configuration data = in scope**; **transactional data = out of scope** (a dev
     tenant should have none worth migrating - regenerate test data instead of moving it).
   - For each in-scope MCBO, note its relationships to other MCBOs: **no dependency**, **one-way**, or
     **bi-directional**. This sets load order:
     - No-dependency MCBOs load **first**.
     - One-way: load the **dependency first**.
     - Bi-directional: load one, then load the second, then **return and PATCH the first** to add the
       back-reference.
   - **Pick the tool by volume:** < ~20 instances -> UI/manual; ~30-500 -> API tool (Postman/Bruno,
     `?bulk=true`); high volume -> EIB. (One tool can do all; match tool to volume for efficiency.)
   - Document: which MCBOs migrate, the load order, and the chosen tool per MCBO.
5. **Write the cutover runbook + readiness check.** You should be able to answer YES to all: no
   tenant-specific IDs hardcoded; you know exactly which tenanted artifacts the app needs and how to
   rebuild them; you have a config-data plan (MCBOs, dependencies, tools); test/transactional data is
   regenerate-not-migrate; and you have a short ordered runbook to stand up the new tenant.

## Phase B - stand up the app in the NEW tenant

6. **Save and Deploy from App Builder** -> select the newly provisioned dev tenant (authenticate to it if
   prompted). This moves the app SOURCE.
7. **Install via App Manager.** Depending on the app: create/configure App Attributes; create/configure
   Security Domains; create/configure Business Processes; configure delivered security domains (account
   for new/changed ISSGs the ISU needs); activate the security policy changes; **create the ISU, assign
   ISSGs, and add the ISU to the app via App Manager**; create non-model custom tasks; and **install the
   RTC** onto the new tenant.
   - **Prereq:** Object Transporter enabled + Customer Central set up in the NEW tenant *before* installing
     the reusable configuration (same as 3.2).
   - This confirms the suite's standing rule: ISU/ISSG, security, keys, and API clients never travel
     tenant-to-tenant and are recreated here (wd-integration-dev `integration-build.md` +
     `security-setup.md`). RTC reduces the manual set; it does not eliminate the security rebuild.
8. **Manually rebuild the OX-unsupported artifacts** from the Step-2 inventory (complex dashboards, custom
   tasks, specific integration setups, security configuration packages), **in dependency order**, so the
   tenant architecture is whole before any data load.
9. **Execute the MCBO data recreation** from the Step-4 plan (right tool, right order, patch the
   bi-directional case). Then **reconcile**: build a custom report per MCBO and compare **row counts and
   values** between the source and new tenants; resolve every difference.
10. **Validate before the source tenant expires:** app builds and deploys; key pages load; orchestrations
    run; configuration data is correct (instance counts + relationships); test flows work on regenerated
    data. Fix issues in the new tenant, and **capture any surprise manual step back into the runbook** for
    next time.

## Gotchas worth flagging

- **RTC/OX prereqs are per tenant** - Object Transporter + Customer Central must be set up in BOTH the
  source (to package) and the new tenant (to install), or the RTC install fails.
- **Portability is the make-or-break** - a single hardcoded WID/Report/Integration-System ID breaks the
  deploy in the new tenant. Do Step 1 thoroughly; App Attributes are the mechanism.
- **Dev tenants carry no transactional data worth moving** - migrate configuration MCBOs only; regenerate
  test data. Don't try to move transactional instances.
- **Reconcile by counts AND values**, not just "it loaded" - the custom-report row/value compare is the
  proof the config data landed intact.

## Neighbors

- Packaging/deploy mechanics + `wdcli whoami`/host facts: `wdcli-*` refs and `tenant-ops.md`.
- Not-migratable security/keys/API-clients recreated per tenant: wd-integration-dev `integration-build.md`,
  `security-setup.md`. Platform-timing/status of a dev-tenant refresh: `release-impact.md`.
