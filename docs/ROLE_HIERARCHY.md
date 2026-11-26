# OptiFreight AI — Portal Role Hierarchy

The application has five portals arranged into four hierarchy tiers.

| Tier | Portal / displayed role | Account role | Relationship / scope |
|---|---|---|---|
| 1 | Owner Portal (`Owner`) | `platform_owner` | One platform account configured by server-side `PLATFORM_OWNER_EMAIL` and `PLATFORM_OWNER_PASSWORD`; not publicly registrable |
| 2 | Company Portal (`Company`) | `organization_owner` | Independent company-owning account; manages its own company onboarding and profile |
| 2 | Client Portal (`Client`) | `client` | Independent client account; publishes and manages only its own cargo listings |
| 3 | Company Admin Portal (`Company Admin`) | `organization_admin` | Operational administration within its own company, subject to assigned permissions |
| 4 | Driver Portal (`Driver`) | `driver` | Driver's own profile, cargo discovery, requests, assignments and delivery activity |

Public registration offers exactly four roles: Client, Company, Company Admin, and Driver. Company Admin and Driver registrations must select an active approved company. The Owner account is created on first successful login using the single server-configured email and password; those credentials are not part of the public registration form.

## Tier 2 relationship

The Company and Client portals are peers. The Client Portal is not a child of a company, is not managed by a Company account, and does not inherit Company permissions. Likewise, a Company account does not gain access to a client's private cargo listings. The two account types share a hierarchy tier only; their data boundaries and permissions remain separate.

## Security rule

Hierarchy labels are explanatory UI/product structure, not authorization. Every protected operation must continue to enforce the authenticated role, resource ownership and company scope on the backend.

## Safety and profile permissions

| Account | Safety/profile access |
|---|---|
| Platform Owner | View all user/company profiles; blacklist companies, company admins and drivers; permanently ban any account or company |
| Company Owner | View their company, admins and drivers; blacklist or permanently ban their admins and drivers |
| Company Admin | View company drivers; review driver reports and strike challenges; remove strikes; blacklist or permanently ban drivers |
| Driver | View their own profile and strike history/reasons; submit written strike challenges |
| Client | View their own profile; report drivers only on their own accepted shipments with an assigned driver; view the accepted company and assigned driver |

Driver reports remain pending until a Company Admin reviews them. Only accepted reports create strikes. Five active strikes trigger a permanent driver ban. Permanent bans are not reversible; blacklists are reversible only by an authorized role. All state changes retain history. Identity values used for ban prevention are stored as keyed fingerprints, not returned by profile APIs or sent to government providers. Ban SMS is disabled unless `BAN_SMS_ENABLED=true` is explicitly configured.
