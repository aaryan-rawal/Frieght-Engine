# Hosting and deployment guide

## Current preparation status

Repository configuration is prepared for a Vercel static frontend, a Render FastAPI service, and an external Neon PostgreSQL database. This work has **not** created a provider account, hosted database, service, public deployment, or migration. No real SMS was sent. The existing root `.env` is intentionally untouched.

The project directory currently has no Git metadata. Before provider dashboards can deploy this project, create or connect a private GitHub repository after reviewing the ignore rules. `.env`, private uploads, large datasets, model files, and `HANDOVER_PRIVATE_CONFIG.txt` are excluded from Git/Docker contexts. Do not commit any local credential files.

## Repository audit

| Area | Finding |
|---|---|
| Frontend | React 18, TypeScript, Vite 8; run `npm ci`, `npm run build`, `npm test -- --run` from `frontend`. Static build output is `frontend/dist`. |
| Backend | FastAPI on Python 3.11+; Docker starts `uvicorn app.main:app` and binds Render's `PORT`. |
| API | API routes are under `/api`; liveness is `/health`, database readiness is `/health/ready`. |
| PostgreSQL | SQLAlchemy async uses `asyncpg`; Alembic uses synchronous `psycopg`. `DATABASE_URL` can be a standard PostgreSQL URL. For Neon, the async adapter accepts `sslmode=require` and drops the libpq-only `channel_binding` option for `asyncpg`. Alembic can use a separate direct URL via `MIGRATION_DATABASE_URL`. |
| Migrations | Current Alembic head is `0016_driver_enforcement`, following `0015_textbee_phone_otp`. Application startup does not run migrations. |
| CORS | `CORS_ORIGINS` is a comma-separated exact-origin allowlist. Configure the production Vercel origin; do not use `*`. |
| Uploads | Delivery proofs and other private documents are stored under `backend/uploads` by default. This is local/ephemeral container storage, not a persistent object-storage integration. |
| Authentication | JWTs require a fresh `JWT_SECRET_KEY` of at least 32 characters. MFA requires a stable Fernet `MFA_ENCRYPTION_KEY`. Registration OTP requires `TEXTBEE_API_KEY`; secrets belong only in the backend host's environment. |
| Routing | An HGV Lua profile and local OSRM compose/build files exist, but the India PBF graph and hosted OSRM service are absent. `OSRM_TRUCK_PROFILE_CONFIRMED` remains `false`; hosted routing is not HGV-verified. |

## Recommended providers

**Vercel frontend + Render web service in Singapore + Neon PostgreSQL in Singapore.**

- Render supports Docker web services and currently lists Singapore as a service region. This matches the backend's existing Docker packaging and keeps the database region near the app.
- Neon supports standard PostgreSQL connections and a Singapore region. Its database works with SQLAlchemy/Alembic; the deployed code handles the relevant Neon URL parameters.
- Vercel is appropriate for the static Vite build and provides HTTPS/CDN delivery. The frontend calls the Render API origin directly; exact CORS origins are set in Render.

This is a provider recommendation, **not an authorization to provision resources**. Render Free is a demo/testing tier: services spin down after 15 minutes without inbound traffic, take about a minute to resume, and have ephemeral filesystems. Render explicitly says Free instances are not for production. Neon Free is also for prototypes/small projects: 100 CU-hours per project, 1 GB database storage, 5 GB public network transfer, and compute scales to zero after 5 minutes. The driver rest monitor polls the database once a minute while the backend is running, which can keep Neon compute active and consume its free CU-hours. For production, budget for an always-on Render compute plan and monitor Neon usage; no exact cost can be forecast without workload measurements.

Vercel Hobby is currently listed at $0/month, with usage limits; Pro is listed at $20/month. Check current provider terms, usage, and pricing before enabling a paid plan. Sources (checked 2026-11-23):

- [Render free instance limitations](https://render.com/docs/free)
- [Render regions](https://render.com/docs/regions)
- [Render Docker deployment](https://render.com/docs/docker)
- [Render Blueprint specification](https://render.com/docs/blueprint-spec)
- [Neon pricing and limits](https://neon.com/pricing)
- [Neon regions](https://neon.com/docs/introduction/regions)
- [Neon connection strings](https://neon.com/docs/connect/connect-from-any-app)
- [Vercel pricing](https://vercel.com/pricing)
- [Vite on Vercel](https://vercel.com/docs/frameworks/frontend/vite)

## Environment variables

Set these in the provider dashboards. Never place backend secrets in Vercel variables or `VITE_` variables.

### Vercel frontend

| Variable | Value |
|---|---|
| `VITE_API_BASE_URL` | Required hosted backend HTTPS origin, e.g. `https://optifreight-api.onrender.com` (origin only; no `/api` suffix). This is public and compiled into the frontend at build time. |
| `VITE_API_MODE` | `http` |
| `VITE_GOOGLE_MAPS_EMBED_KEY` | Optional browser-visible key; restrict it to the Vercel site and the required Maps API. |

The Vercel project root is `frontend`. `frontend/vercel.json` configures the Vite build/output and SPA fallback. Local development keeps using Vite's `/api` proxy when `VITE_API_BASE_URL` is empty.

### Render backend

| Variable | Required/setup |
|---|---|
| `APP_ENV` | Set to `production`. |
| `DATABASE_URL` | Neon pooled PostgreSQL connection URL for the running API. Keep the connection string secret. |
| `MIGRATION_DATABASE_URL` | Neon **direct** PostgreSQL URL for manual Alembic operations; do not use the pooler for migrations. |
| `JWT_SECRET_KEY` | Fresh random secret, at least 32 characters. Do not reuse the local development key. |
| `MFA_ENCRYPTION_KEY` | Fresh Fernet key; keep stable and securely backed up. Losing/rotating it breaks access to existing MFA secrets. |
| `IDENTITY_FINGERPRINT_SECRET` | Stable, fresh secret of at least 32 characters; keep it stable for lifetime identity-fingerprint matching. |
| `PLATFORM_OWNER_EMAIL`, `PLATFORM_OWNER_PASSWORD` | Production bootstrap credentials; use a unique strong password. |
| `CORS_ORIGINS` | Exact production Vercel origin, e.g. `https://your-project.vercel.app`, with no trailing slash. Add an exact preview origin only if needed. |
| `TEXTBEE_API_KEY` | Required for OTP registration/phone verification. Enter only in Render. Do not test by sending SMS without approval. |
| `BAN_SMS_ENABLED` | Keep `false` unless outbound permanent-ban SMS is separately approved. |
| `OSRM_TRUCK_PROFILE_CONFIRMED` | Keep `false` until a reviewed HGV graph is hosted and routes have been independently validated. |
| `DRIVER_AUTO_BLACKLIST` | Keep `true` to preserve the existing background rest monitor. |

The blueprint sets non-secret safe values and marks secrets for dashboard entry. No `.env` values are copied into the image or printed by this guide.

## Local checks and commands

Run these from a trusted local clone before pushing:

```powershell
cd frontend
npm ci
npm run typecheck
npm test -- --run
npm run build

cd ..\backend
python -m pytest tests -q
alembic heads
```

Optional local container build (does not deploy or create hosted resources), from the repository root:

```powershell
docker build -f backend/Dockerfile -t optifreight-api:local .
```

After you approve a hosted database and deployment, the manual migration command is:

```powershell
cd backend
alembic upgrade head
```

Run it only with `MIGRATION_DATABASE_URL` set to the approved target database's **direct** connection URL. This applies the migration to the database selected by that secret. Do not run it before taking a backup and confirming the target. The configured Render health check is `/health/ready`; `/health` only verifies that the API process responds.

## Manual setup sequence (no resources created yet)

1. **Prepare GitHub.** Review `.gitignore` and `.dockerignore`; create a private repository and push the source without `.env`, `HANDOVER_PRIVATE_CONFIG.txt`, uploads, datasets, or model data. This working directory currently has no `.git` metadata, so initialize/connect it locally before the provider dashboards can select it.
2. **Create Neon only after explicit approval.** Choose AWS Asia Pacific Singapore (`aws-ap-southeast-1`). Create a database and obtain both pooled (runtime) and direct (migration) PostgreSQL URLs. Keep these out of chat. The application uses TLS (`sslmode=require`).
3. **Create the Render Blueprint/service only after explicit approval.** Select the repository and root-level `render.yaml`; review the free-plan limitations and set all required Render variables securely before deploying. The blueprint does not define or provision a database and disables automatic deploys. Do not add a migration pre-deploy command.
4. **Apply the database migration only after explicit approval.** Back up the target database, set `MIGRATION_DATABASE_URL` to its direct URL in Render, open the service shell, and run `cd /app/backend && alembic upgrade head`. Confirm the target database and resulting Alembic head before proceeding.
5. **Create the Vercel project and publish only after explicit approval.** Import the same GitHub repository, set the project root to `frontend`, add the frontend variables above, and deploy. Then update Render's `CORS_ORIGINS` with the exact production URL and redeploy the backend if needed.
6. **Verify from another network/device.** Open the Vercel URL over HTTPS; test login/OTP only with an authorized TextBee key and approval to send an actual SMS. Check `/health` and `/health/ready`, then test sign-in, one representative API flow, upload/download behavior, and browser network errors. Do not treat HTTP acceptance as proof of SMS handset delivery.

## Known limitations and external checks

- **Persistence:** uploads in `backend/uploads` disappear on container restart/redeploy. Do not rely on delivery evidence or identity documents in this configuration for production. An approved private object-storage adapter and migration plan are still needed; none is created here.
- **TextBee:** the Render container can make outbound HTTPS requests, but outbound network reachability and TextBee delivery have not been tested. The Android gateway phone must remain powered, online, and running the TextBee gateway app. Provider API acceptance does not confirm handset delivery.
- **HGV routing:** no hosted OSRM instance or India graph is configured. Keep safety-dependent route results unconfirmed.
- **Free tiers:** expect sleeping/cold starts, limited storage/compute/egress, quotas, and provider terms that may change. The backend's periodic database monitor can increase Neon compute usage.
- **Not verified:** no GitHub push, provider account, hosted service/database, public deployment, production migration, live database connection, TextBee call, or HGV route test has occurred.
