# Workday SOAP Web Services (WWS) - catalog retrieval

How to inventory the SOAP web services and operations an implementer/ISU can call in a tenant - the
services EIB / Studio / Core Connector integrations invoke. This is the SOAP analog of the REST catalog
(`rest-api-catalog.md` in wd-extend-dev). Tool: `scripts/wws_inventory.py` (build-spec in scripts.md).

## Two ways to get the inventory

1. **In-tenant report (authoritative, no credentials, includes private/undocumented services).** Run the
   delivered **Public Web Services** report (lists every registered service + its documentation) and
   **Public Web Services and Related Operations** report (operations per service), export both to Excel,
   then: `python wws_inventory.py --reports Public_Web_Services.xlsx Public_Web_Services_and_Related_Operations.xlsx`.
   This is the complete list - use it when completeness matters.
2. **Live WSDL crawl (ANONYMOUS by default).** `python wws_inventory.py` with `WD_HOST/WD_TENANT` set.
   WSDL retrieval needs NO credentials (verified - corroborates wd-auth Mode 5 and wd-extend-dev
   tenant-ops.md); the script resolves the current WWS version, then reads each service's WSDL for its
   operations. An OPTIONAL API-client refresh-token bearer (keychain service `wd-wws-inventory`)
   covers gated tenants only. (Basic auth for web services was retired ~R2 2026 - a `WD_USER/WD_PASS`
   password no longer authenticates anywhere; the script no longer supports it.) Use this mode when
   you only have tenant access and no report export. For registering an API client + refresh grant
   when the bearer IS needed, see `wd-auth/references/auth-decision-tree.md` (Mode 2).

The per-service WSDL is always at `https://<host>/ccx/service/<tenant>/<Service>/<version>?wsdl`
(operations + request/response types); the whole-tenant directory would be `.../ccx/service/<tenant>`.

## Hard-won retrieval facts (verified against a live tenant)

- **SOAP is usually served on the `-services1` gateway host, not the tenant base URL.** From
  `wdcli tenant list -f json` you get `tenantBaseUrl` and `tenantGwUrl`; the base URL often 404s for
  `/ccx/service/...` while the `<pod>-services1.<...>` host serves it. The script tries both.
- **The browsable service directory (`/ccx/service/<tenant>`) is frequently DISABLED (404).** When it is,
  you cannot enumerate service names from the tenant over HTTP - hence the two options above: name-probe a
  known list (finds only well-known public services) OR export the in-tenant report (finds everything).
- **`?wsdl` with no version returns an OLD default version** (seen as `v15`, with far fewer operations than
  current). Always request an explicit current version - the script resolves it by probing `vNN.M`
  descending until a WSDL returns. All public services share one version per Workday release.
- **Auth is an API-client refresh-token bearer (`Authorization: Bearer ...`).** Basic auth for web
  services was RETIRED by Workday (~R2 2026), so an ISU/implementer `USER@tenant` password now returns
  401 / "invalid username or password" tenant-wide - do NOT use it. Register an API client and use the
  refresh grant instead (see `wd-auth/references/auth-decision-tree.md` Mode 2; Mode 3 documents the
  retired Basic path). wdcli's own bearer token does NOT work for SOAP - wdcli has no web-service
  inventory command (its scope is `account/app/auth/config/tenant`).
- **Corporate TLS interception** breaks Python's default cert validation
  (`SSLCertVerificationError ... CA cert does not include key usage extension`). Fix by validating against
  the OS trust store: `pip install truststore` (the script injects it automatically). Secure fallbacks:
  `WD_CA_BUNDLE` = corporate root CA `.pem`; `WD_INSECURE=1` only as a last resort on a trusted network.

## Public WWS directory (official-docs - developer.workday.com / community.workday.com, 2026-08-25)

A third inventory source needing NO tenant access at all: the Workday Community file-hosting
API directory is fully public (no login) at
`https://community.workday.com/sites/default/files/file-hosting/productionapi/index.html`.

- Currently lists **67 SOAP services at v46.2 (2026R1)**. Per-service files follow
  `{Service}/v46.2/{Service}.wsdl` (+ `.xsd` schema and `.html` per-operation descriptions);
  an alphabetical Operation Directory page lists every operation across services.
- **ALL historical versions stay hosted** under `.../productionapi/versions/` (back to at
  least v10) - useful when auditing an old integration pinned to an early version.
- The directory WSDL/XSD/HTML fetch is **anonymous** - corroborates wd-auth's Mode 5
  (no-auth WSDL access); the live in-tenant crawl is likewise anonymous by default (an
  optional bearer covers gated tenants - see mode 2 above).
- **RECONCILIATION - 67 public directory vs ~56 in-tenant:** a dev tenant's
  `publicWebServices` WQL source reports ~56 services and this file's name-probe found 38
  (wd-extend-dev tenant-ops.md holds the WQL figures). Both are true: the tenant-side count
  is ENTITLEMENT/registration-dependent (what THAT tenant serves), while 67 is the full
  public catalog Workday documents. For "what exists at all" use the public directory; for
  "what can THIS tenant/ISU call" use the in-tenant report/WQL.

## What "private" web services actually are

Workday does not expose a separate hidden/privileged SOAP tier. The full set an implementer can reach is
the tenant's registered public web services; access to any given OPERATION is gated by the ISU's security
policy. The services that feel "private" are simply the newer/niche ones that a name-probe can't guess and
that are lightly documented (e.g. Scheduling, Student Core, Moments, Flex Team, Org Studio, Drive, Prism
Analytics, Workforce Planning, Tenant Data Translation, External Integrations, ACA/Benefits Partner
Integrations). The in-tenant report surfaces them; a public name-probe will not. So: **for a complete
"what can this ISU call" answer, always use the in-tenant report export (option 1), and diff it against the
name-probe output to isolate the not-publicly-documented set** (the script marks each service
`NameProbeDiscoverable` yes/no for exactly this).

## When to use this

- Scoping an integration: confirm the operation exists and see its exact name/version before designing.
- Takeover/audit of an existing tenant: baseline the callable SOAP surface.
- Choosing SOAP vs REST/RaaS: compare against `rest-api-catalog.md` (wd-extend-dev) for the same data.
- Security review: the `NameProbeDiscoverable=no` set is a good prompt to confirm which of those the ISU's
  domains actually permit.
