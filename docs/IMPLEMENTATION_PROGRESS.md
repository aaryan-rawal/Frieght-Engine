# OptiFreight AI — Implementation Progress

Last updated: 2026-11-22. A code file existing is not the same as a feature being runtime-verified.

## Part 1 — Dataset preparation and inventory

**Status: PARTIALLY COMPLETE — uploaded sources organized; Belgium OBU archive verified and inventoried, semantic/license review pending.**

- Organized uploaded CSVs under `DATASETS/raw/`.
- Retained source ZIPs under `DATASETS/source_archives/` and extracted Olist/AnonNet datasets under `DATASETS/extracted/`.
- Extracted SimMD, supply-chain disruption monitoring and SynDelay research repositories under `DATASETS/repositories/`.
- Created `DATASETS/manifests/dataset_manifest.json` and `DATASETS/README.md`.
- Belgium OBU (Kaggle `giobbu/belgium-obu`) archive integrity, checksum, extraction, and full structural/quality inventory were verified: 29 headerless CSVs, 301,483,881 records, four JSON files, one GIF. Field semantics, units, timezone, privacy, and licensing still need review; license approval is owner-reported, not independently reviewed.
- Previous claims about a separate 34-file traffic parquet collection were not verifiable from the uploaded dataset files in this build and are not marked as re-verified.

## Part 2 — Environment and launch infrastructure

**Status: IMPLEMENTED; local launch dependencies and database connectivity verified.**

- Root `requirements.txt` is the canonical Python dependency list.
- Root `.env` was preserved byte-for-byte from the supplied cleaned archive. No `.env` values are reproduced in documentation.
- Added `.env.example` as a template only; it must not overwrite an existing `.env`.
- Added/updated `setup.bat`, `run.bat`, `run_frontend.bat`, `run_all.bat`, and `migrate.bat`.
- `scripts/check_db.py` uses SQLAlchemy 2.x `text()` and does not print credentials.

## Part 3 — Database models and migrations

**Status: IMPLEMENTED; local database is behind the current code head.**

- Added SQLAlchemy 2.x models for app users, manual cargo, matching runs, shipments, fleet drivers and fleet containers.
- Added Alembic revision `0002_operational_app` while preserving the existing `0001_initial` revision identity.
- New application identities use `app_users` so the older legacy `users` table is not silently repurposed.
- The configured local database was previously verified at revision `0012_server_mfa`.
- The current repository migration graph has one head, `0014_cargo_csv_provenance`; migrations 0013 and 0014 have not been applied locally.
- No migration was applied during the current integration-readiness work.

## Part 4 — Authentication

**Status: IMPLEMENTED IN CODE; SELECTED POSTGRESQL AND LIVE HTTP FLOWS VERIFIED.**

- Added JSON registration and login endpoints.
- Passwords use Argon2 hashing; JWTs use the root `.env` secret.
- Added bearer-token current-user dependency and administrator profile guard.
- Password minimum matches the supplied frontend validation (8 characters).
- Added server-backed TOTP enrollment and login challenges, encrypted authenticator secrets, replay prevention, one-use hashed recovery codes, and protected MFA disable. Requires a persistent `MFA_ENCRYPTION_KEY`.

## Part 5 — Backend API

**Status: IMPLEMENTED IN CODE; PARTIAL DATABASE/HTTP VERIFICATION.**

- Routes catalogue: `GET /api/routes` and `GET /api/routes/{route_id}`.
- Authentication: registration/login/current-user endpoints plus MFA setup, confirmation, challenge, and disable endpoints.
- Manual cargo CRUD: `GET/POST /api/cargo/manual`, `DELETE /api/cargo/manual/{id}`.
- Client CSV cargo import: `POST /api/cargo/import/csv` (requires migration 0014).
- Matching: `POST /api/matching/run`.
- Shipments: create/accept, list, read, assign, advance and cancel under `/api/shipments`.
- Fleet drivers and containers under `/api/fleet`.
- Admin profile: `GET /api/admin/profile`.
- Health/readiness: `/health`, `/health/ready`.

## Part 6 — Deterministic matching engine

**Status: PARTIALLY IMPLEMENTED; IMPORTANT HARD RULES ARE FAIL-CLOSED.**

- Added WGS84 Haversine and route-polyline nearest-point helpers.
- Added route-distance job caps and piecewise trip budget multiplier.
- Added vehicle-body compatibility checks based on the frontend's documented matrix.
- Added route verification gating, pickup-before-drop ordering, pickup-window ETA check, per-stop road excursion checks and total/daily job-cap checks.
- Added conservative bundle alternatives from individually eligible same-category cargo. Bundles recheck smallest-enclosing-circle pickup/drop radii, combined payload, route-order load profile, aggregate trip distance and active-time budgets. Bundle generation remains unavailable until all member regulatory and other hard checks pass.
- Added a fail-closed regulatory assessment gate for e-way bill, heavy-vehicle access, hazardous-goods requirements, over-dimensional permits, driver-hours/rest, vehicle documents, route permits and registered GVW/axle-load limits. No legal thresholds are guessed; a current trusted jurisdiction adapter is still required.
- OSRM road geometry is used only when the routing call succeeds. Seed/demo route geometry remains unverified otherwise.
- Off-route excursion is measured by OSRM round trip from the nearest point on the route polyline to each stop and back. The two excursions combined must be at most 40 km; exactly 40 km is accepted.
- Whole-trip distance and active-time budgets are checked separately. Active time uses truck-supplied baseline active minutes plus OSRM off-route driving durations and explicit per-cargo loading/unloading/waiting minutes; missing values remain unknown.
- Net contribution is calculated only when revenue, extra distance, active time, diesel, loaded mileage, toll, driver rate and handling fee are all explicitly available.
- A transparent provisional baseline score ranks only candidates whose every hard check passes and whose net contribution and payload utilization are known. No ML model score is fabricated.
- Bundle candidate generation and aggregate checks are implemented, but additional cargo-specific volume/handling/segregation constraints and multi-stop sequencing need expansion before production.
- Regulatory assessment framework is implemented. Live e-way bill, local heavy-vehicle access, hazardous-goods, ODC, driver-hours/rest, vehicle-document, transport-permit and axle-load verification remain blocked on trusted data adapters and approved jurisdiction policy.
- Driver-hours/rest policy values and authoritative financial assumptions remain unimplemented; no unverified legal limits or cost assumptions are invented.
- No trained ML score is returned. A provisional deterministic baseline score is separate from ML. Unknown checks are never eligible.

## Part 7 — Routing and mapping

**Status: PARTIALLY IMPLEMENTED; LIVE ROAD ROUTE RESPONDS, HGV PROFILE UNVERIFIED.**

- Added OSRM HTTP adapter using configurable root `.env` `OSRM_URL` and fallback URL.
- Added response-code, geometry-coordinate, positive metric, endpoint-snap and endpoint-geometry checks before marking a road route verified.
- Added `POST /api/routes/{route_id}/verify`; matching uses the same verification function.
- Per-stop round-trip road excursion is implemented through OSRM as route-departure -> stop -> route-re-entry.
- Automated mock-response tests cover successful verification, bad response code, invalid coordinates and excessive endpoint snapping.
- A live OSRM road-network route returned geometry; the endpoint does not confirm a reviewed HGV profile. Local OSRM deployment, caching/rate-limit policy and real-map end-to-end verification remain pending.

## Part 8 — Cargo ingestion

**Status: PARTIALLY IMPLEMENTED; client-provided CSV ingestion is available.**

- Manual cargo persistence/API is implemented.
- Uploaded datasets are inventoried and stored as research inputs.
- DataCo/Olist/AnonNet/SimMD/SynDelay/disruption-monitoring datasets are not automatically treated as live freight listings.
- Client CSV upload validates UTF-8 headers and rows, enforces 5 MiB / 1,000-row limits, rejects duplicate client source IDs, records source-file SHA-256 provenance, and reports row-level validation errors. It is not a connector to a public marketplace or research dataset.
- A CSV template and import contract are documented in `docs/CARGO_CSV_TEMPLATE.md`.
- Authorized public cargo APIs, source-specific external field mapping, and real freight-source approval remain pending.
- UNCTAD transport-cost indicators are not cargo listings; the old placeholder UNCTAD endpoints were disabled rather than retained as false integrations.

## Part 9 — Machine learning

**Status: DEVELOPMENT SCAFFOLD IMPLEMENTED; NOT TRAINED OR EVALUATED.**

- Added one versioned serving/training feature contract. Missing feature values are not imputed as zero.
- Model A loads a versioned LightGBM ranking artifact only when its metadata matches the feature schema.
- Model B loads p10/p50/p90 LightGBM quantile artifacts for delay and incremental-cost estimates.
- Matching calls ML only after all deterministic checks pass. ML can never override eligibility.
- Added reproducible training CLI scaffolding; no training was run and no model artifacts were created.
- SynDelay's three-class target has not been mapped to a project label. Dataset suitability, owner-approved labels, final leakage-safe split design, training, calibration and locked test evaluation remain for the dedicated ML phase.

## Frontend integration

**Status: FRONTEND TYPECHECK, UNIT TESTS, AND PRODUCTION BUILD PASS ON WINDOWS.**

- `npm ci` completed on Windows using the supplied lockfile.
- `npm run typecheck` passed.
- `npm test` passed (58 tests in the latest verification).
- `npm run build` passed. Vite emitted a non-blocking chunk-size advisory.
- The authenticated app now shares the ZIP-inspired dark navy/teal visual language, focus states, and form-control styling across the shared design tokens and components; light theme remains supported.
- Vite 8.3.8, Vitest 5.1.1, React Router DOM 7.18.6, and the Vite React plugin 6.3.0 are installed.
- `npm audit --audit-level=low` reports 0 vulnerabilities.
- Updated Playwright demonstration smoke test passed after installing Chromium.
- Eight mock-mode Playwright tests pass, including public role selection and all five role portals. Two opt-in live PostgreSQL browser flows cover Client cargo/MFA and Owner company approval plus Company, Company Admin, and Driver registration/sign-in; they were skipped in the latest local E2E run because live mode was not enabled.
- `npm audit --audit-level=low` reports 0 vulnerabilities after the frontend tooling/router upgrades.
- Five role-specific portal home experiences use the shared design system; mock mode explicitly labels server-only operations.
- Driver registration now loads approved companies and submits the selected organization ID.
- The backend creates or reuses the matching company fleet-driver profile when driver registration is verified.
- Drivers can review/cancel pending cargo requests and view rest-event history.

## Verification performed in this build environment

- Latest local backend regression: `python -m pytest backend\tests -q` — 111 passed, 6 skipped. The opt-in PostgreSQL tests were not run during this pass.
- FastAPI health and database readiness: passed against local PostgreSQL.
- The configured local database was previously verified at `0012_server_mfa`; repository code now has one migration head, `0014_cargo_csv_provenance`. No migrations were applied during this pass.
- Live OSRM road routing returned geometry; the endpoint does not have confirmed HGV-profile verification.

## Next implementation priorities

1. Configure a reviewed HGV routing profile and keep route-dependent matching blocked until verified.
2. Configure authorized regulatory, identity, and SMS providers; retain fail-closed behavior until each integration is verified.
3. Expand browser coverage for provider-backed integrations and actual proof-file upload/review; live role registration, sign-in, and Owner company approval are covered.
4. Review the completed Belgium OBU inventory alongside its source documentation; verify license, privacy, field semantics, units, timezone/coverage, and suitability before any ingestion.
5. Approve ML label definitions and leakage-safe splits, then train/evaluate Model A and Model B. Model C remains optional.
6. Configure production-grade private object storage, malware scanning, retention, and a deployment-specific managed MFA key.

## Follow-up implementation — 21 November 2026

- Client listing management now includes search across cargo/category/pickup/drop, active-versus-expired filtering, and newest/A–Z/Z–A ordering. Delete requires confirmation and surfaces API errors.
- In-portal notifications now have a bulk mark-as-read endpoint scoped to the authenticated recipient, plus a matching portal action.
- Driver registration now requires selection of an approved company; backend registration creates or reuses its fleet-driver profile.
- Drivers can list and cancel their own pending cargo requests. Driver rest history includes duration and associated shipment.
- These are implemented code paths; full live-API browser flows for every role and provider-backed document verification remain outstanding.

## Follow-up implementation — delivery proof review

- Added private PDF/JPG/PNG upload and authenticated download endpoints for assigned drivers.
- Proof records are scoped to the driver's organization; company staff can only review shipments within their tenant, while platform administrators can review across tenants.
- Approval marks the shipment delivered and records review history, an in-portal notification, and an audit event. Rejection requires a reason and allows a later resubmission.
- The frontend now loads, submits, downloads, and reviews proofs through the HTTP API. Mock mode is clearly labeled as browser-only metadata and does not retain files.
- The configured local database is at migration `0011_delivery_proofs`; a custom-format backup was verified immediately before applying it.
- Backend tests: 82 passed with opt-in PostgreSQL integration enabled; frontend typecheck, 49 unit tests, and production build passed.
- Manual review is not document-authenticity verification. Public production requires private object storage, malware scanning, retention policy, and tenant-isolation browser testing.

## Follow-up implementation — matching and assignment safety

- Pickup ETA now includes verified OSRM outbound stop-leg time. Early arrival wait is included in active time and net-cost calculations; missing durations remain unknown.
- Match-run snapshots now retain route fractions, explicit stop durations, and bundle scheduling inputs so bounded bundle generation can use real matched candidates.
- Bundle identifiers fit the shipment schema; accepting a manual bundle reserves every member listing in one transaction. Synthetic and mixed-source offers cannot be accepted as real shipments.
- Shipment acceptance locks the requesting user and cargo rows to enforce trip caps and prevent concurrent duplicate reservation.
- Company-assigned drivers can see and advance their assigned shipments. The backend requires delivery-proof review to complete an in-transit shipment.
- Added PostgreSQL tests for tenant-isolated proof access, private upload/download, approve/reject/resubmit flow, and concurrent acceptance of the same cargo.
- The default matching gates remain fail-closed: no reviewed HGV profile or trusted current regulatory assessments are configured in this workspace.

## Follow-up implementation — 22 November 2026

- Added distinct home dashboards for the Platform Owner, Company Owner, Client, Company Administrator, and Driver roles. Existing server-side permission and tenant checks remain authoritative.
- Replaced the combined role operations screen's inline styling with the shared cards, forms, buttons, and theme tokens; company owners now manage onboarding details from the organization page.
- Implemented server-backed TOTP enrollment, encrypted secret storage, authenticator sign-in challenges, replay protection, one-use hashed recovery codes, and password-plus-code MFA disable. The frontend displays setup QR codes and explicitly reports when the encryption key is unavailable.
- Applied migration `0012_server_mfa` after verifying a pre-migration custom-format PostgreSQL backup. Do not rotate or lose `MFA_ENCRYPTION_KEY` after users enroll.
- Added PostgreSQL MFA lifecycle coverage and live HTTP browser coverage for account registration, client cargo creation, MFA enrollment, and MFA sign-in. Test accounts and registration challenges are removed after the browser run.
- Public registration now presents Client, Company, Company Admin, and Driver; Company Admin and Driver must select an active company. The Owner account is excluded from public registration and bootstrapped from the one server-configured email/password pair.
- Added live PostgreSQL browser coverage for Owner company approval and Company, Company Admin, and Driver onboarding/sign-in, with narrowly scoped cleanup of generated test records. Mock-mode browser checks cover all five portals and the public role selector.
- Replaced the weak local JWT placeholder with a random 64-character signing key after live verification exposed that authentication could not issue tokens. The existing `.env` remains local; deployments must provision separate secrets.
- Remaining code-side verification is broader provider-backed and proof-file browser coverage. External regulatory/provider credentials, a reviewed HGV routing profile, production storage controls, and approved/licensed ML data remain external blockers.

## Follow-up implementation — integration readiness

- Added client-only CSV import to the Client Cargo Portal and documented the required schema, limits, validation, provenance, and source-rights responsibility. It does not import public/research datasets or claim that imported records are verified.
- Added server-backed demo subscription selections. They do not process payments or activate paid entitlements; migration `0013_demo_subscriptions` is pending on the configured local database.
- Added the CSV provenance migration `0014_cargo_csv_provenance`; the code graph has one head, but this migration is not applied locally.
- Private local uploads now use exclusive file creation with restrictive POSIX file permissions and remove uploaded files when document metadata persistence fails. Files remain local and unscanned; this does not replace production object storage, malware scanning, retention, or backup controls.
- Expanded GitHub Actions configuration to run backend tests against an ephemeral PostgreSQL service after applying migrations, plus frontend typecheck, unit tests, production build, and mock-mode Playwright coverage. The workflow has not yet run on GitHub.
- Latest local checks: 111 backend tests passed and 6 were skipped; 58 frontend tests passed; typecheck/build passed; 8 mock Playwright tests passed and 2 live tests were skipped. No database or external provider was used in this verification pass.

## Platform Owner portal rework — 24 November 2026

- Added an Owner-only dashboard shell, server-derived company/client totals, a four-plan active-subscription matrix, and four notification categories.
- Added searchable company/client queues and terminal registration decisions. Client decisions are persisted by migration `0017_client_approval`; existing client rows remain approved, while new client registrations await approval. Company decisions are separately persisted by `0019_company_approval_status`; existing companies retain their existing operational eligibility, while new registrations await approval. Rejected clients and companies are blocked by authenticated backend access checks.
- Added migration `0018_company_owner_requests` for persisted branding and company-detail-change requests; request submissions also create owner notifications. Owner controls for reviewing those requests and the later-stage account/profile features remain out of scope.
- Company operations are denied unless the organization is active, its required profile fields are complete, and a persisted subscription is active. The current billing API only creates explicitly demo subscriptions, so it cannot activate a company in this workspace.
- At implementation time, `docs/portal_requirements_audio.webm` and `reference/Placement_Portal_reference.zip` were absent from the supplied source tree. The user later supplied a 42-minute audio file outside the project tree, but local transcription attempts were not reliable enough to extract requirements. No reference-specific styling or audio-derived requirements are claimed. `docs/PORTAL_REWORK_AUDIO_NOTES.md` records the blocker; JSON-only implementation is scoped to prompt 1.
- Migrations `0017_client_approval`, `0018_company_owner_requests`, and `0019_company_approval_status` are additive. Alembic reports one head at `0019_company_approval_status`; offline SQL generation succeeded. No database was upgraded.
- Verification: frontend typecheck, 63 unit tests, and production build passed. The focused Owner browser flow passed. The full mock-mode Playwright run had 5 passed, 3 failed (existing OTP-mock, Company Admin fixture, and fleet-driver fixture cases), and 2 live tests skipped. Focused Owner backend acceptance tests passed (5 tests). The full backend run is not green: collection fails on the existing Belgium inventory import, and excluding that module leaves an unrelated SMS-provider boundary failure under the current local configuration; the other 165 collected tests passed and 12 were skipped. See `docs/STATUS.md` for exact commands and limitations.

## Audio follow-up — 24 November 2026

- The user supplied `ChatGPT dictation 2026-11-23T14-27-47.883Z.webm` from Downloads; its audio was decoded locally, without sending it to a third party.
- The offline Whisper model was not cached and could not be fetched in this environment. The available Windows offline recognizer produced incoherent, very-low-confidence text on a sample, so it was rejected rather than used as a transcript.
- The recording remains untranscribed and no new requirements were implemented. The current OAI workspace has no distinct `reference` directory or `Placement_Portal_reference.zip`; the intended reference material is not identifiable from the workspace contents.
