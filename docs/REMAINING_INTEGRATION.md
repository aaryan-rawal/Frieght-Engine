# Remaining Integration Gates

Updated: 2026-11-22

This register intentionally distinguishes code-level tests from checks that require the owner's Windows machine, PostgreSQL service, network access, authoritative credentials, or external dataset/provider review.

## Current verification

Use [the current status report](STATUS.md) for latest backend, PostgreSQL, frontend, browser, migration and build results. The older 36-test / migration-0004 statements from the first integration pass are historical and are not current project status.

## Not verified here, and why

### Frontend unit tests and production build

The latest recorded Windows verification is in `docs/STATUS.md`. Provider-backed workflows and expanded live browser coverage remain incomplete; do not infer those results from the mock browser suite.

### PostgreSQL integration

The latest ordinary backend regression run is recorded in `docs/STATUS.md`; the opt-in PostgreSQL tests were not run during that pass. The configured local database remains at revision 0012, while the repository head is 0014. Migrations 0013 and 0014 are pending. Do not apply migrations, restore backups, or modify the local/production database without an approved backup and explicit authorization. The GitHub Actions workflow is configured to exercise migrations and PostgreSQL tests only against its disposable CI service; it has not yet run remotely.

### Cargo sources and billing

Client cargo can be imported from a validated CSV in server-backed mode. This is a user-provided import, not a public freight marketplace/API integration, and does not prove that the source is authorized or that its records are true. See [the CSV import contract](CARGO_CSV_TEMPLATE.md). Public cargo-source connectors remain pending approved sources, contracts, and source-specific field mapping.

Subscription plan selection is persisted by the server in demo state only. It does not collect payment or activate paid entitlements; a real payment provider contract and credentials are still required for production billing.

### Live OSRM and truck suitability

A candidate baseline profile exists at `routing/profiles/hgv.lua`, with local build scripts, but no India PBF or graph is present and the profile has not been legally or empirically reviewed. Road geometry from an unverified profile is not HGV evidence. See [the HGV profile review](HGV_ROUTING_PROFILE_REVIEW.md). External fallbacks are disabled by default; do not send route coordinates to an external service without explicit approval.

### Regulatory authority integrations

The engine intentionally fails closed. India-wide official sources do not provide one unauthenticated API that can answer every route/date-specific check for E-way bills, state permits, municipal/CAQM entry restrictions, hazardous cargo, driver duty records, vehicle documents, and axle limits. The E-way bill portal's distance arithmetic is implemented only as a planning helper; it does not validate a real bill. The other checks require authorized records, jurisdiction-specific policy sources, credentials/agreements where applicable, and a legal review. Do not add a trusted source ID or mark these checks `pass` without a real adapter and evidence. Until then, the engine must keep those checks `unknown` and must not accept the candidate.

See [the regulatory compliance contract](REGULATORY_COMPLIANCE.md) and [the regulatory source register](REGULATORY_SOURCE_REGISTER.md) for recorded sources, code behavior and outstanding approvals.

### Belgium OBU dataset

The archive is now present at `DATASETS/Belgium_OBU/archive (2).zip`, passed ZIP integrity validation, and was extracted with matching byte totals. The full structural/quality inventory is complete and recorded in `DATASETS/manifests/belgium_obu_archive_2_inventory.json`. The CSVs are headerless; position 0 is timezone-naive timestamp-like, while field meanings, units, timezone, and a road-segment join key remain unknown. Do not declare privacy, suitability, or independent license review complete. The owner reports licensing approval, but the terms have not been independently reviewed. This archive does not provide project matching outcomes, same-event delivery delay labels, or INR trip-cost labels.

### Private document storage

Uploads are validated by extension, size, and file signature, stored outside static serving, and fetched through authenticated/tenant-scoped routes. Local file persistence is suitable only for the college/demo environment. No malware scanning, production object storage, retention/deletion policy, or encrypted production backup is configured. Uploaded content is still unverified evidence, not identity or legal verification.

## Windows verification procedure

1. Extract the current `OAI_build.zip` to a stable path.
2. Confirm the owner's root `.env` is present; this project never overwrites it.
3. Run `setup.bat`.
4. Start PostgreSQL and verify the database backup.
5. Start the backend with `run.bat` in one terminal.
6. In another PowerShell terminal, run `scripts/verify_windows.ps1`.
7. If migrations are approved, run `scripts/verify_windows.ps1 -ApplyMigrations` and type `APPLY` at the confirmation prompt.
8. Configure and verify a real HGV OSRM endpoint before enabling `OSRM_TRUCK_PROFILE_CONFIRMED`.
9. Only after OBU dataset intake and schema review should model training begin.

## Release readiness

The project is **not yet at a truthful “only training/testing remains” state**. The code-level matching/bundling and fail-closed frameworks are present, but the external integration gates above are still open. This is deliberate: a fabricated live route, database pass, or legal compliance pass would make the product unsafe and the project report inaccurate.
