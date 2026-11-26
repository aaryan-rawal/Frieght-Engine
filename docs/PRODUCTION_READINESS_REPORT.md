# Production readiness report: TextBee phone OTP

**Updated:** 2026-11-23  
**Status:** Implementation and mocked verification are complete. Live TextBee delivery and PostgreSQL migration remain unverified and require owner setup.

## Implemented

- Added the TextBee `POST /gateway/send-sms` adapter using the documented `x-api-key` header and request fields. It validates `data.success` and `data.smsBatchId`, does not follow redirects, uses a 15-second timeout, and performs no automatic retries.
- Added six-digit cryptographic OTP generation, a dedicated HMAC verifier, E.164 normalization with `phonenumbers`, fixed 300-second expiry, cooldown and rate limits, five-attempt lockout, and row-locked single-use verification.
- Reworked registration to avoid returning any OTP and added authenticated phone-change start/verify endpoints bound to the exact user and organization. The existing verified phone remains unchanged until the replacement number is verified.
- Stored TextBee's batch ID and pending delivery state in PostgreSQL. TextBee acceptance is not represented as carrier or handset delivery. Public challenge responses do not expose batch IDs or account-existence details.
- Added resend/countdown/expired/error states to registration and a phone-change panel in server-mode settings. Browser-only mock registration no longer uses a fixed demonstration OTP; mock mode reports that server-backed SMS is required.
- Added an interactive real-SMS utility that calls the production OTP service, refuses test/demo mode and missing TextBee configuration, and requires the operator to type `SEND`. It was not executed.

## Files changed

- Backend: `backend/app/api/auth.py`, `backend/app/config.py`, `backend/app/models.py`, `backend/app/schemas.py`, `backend/app/services/otp_verification.py`, `backend/app/services/integrations/sms.py`
- Migration: `backend/alembic/versions/0015_textbee_phone_otp.py`
- Manual check: `backend/scripts/test_textbee_otp.py`
- Tests: `backend/tests/test_otp_verification.py`, `backend/tests/test_otp_postgres.py`, `backend/tests/test_sms_integration.py`, `backend/tests/test_registration_otp_schemas.py`, `backend/tests/test_mfa_postgres.py`
- Frontend: `frontend/src/api/client.ts`, `frontend/src/api/httpApi.ts`, `frontend/src/api/mock/mockApi.ts`, `frontend/src/api/types.ts`, `frontend/src/auth/AuthProvider.tsx`, `frontend/src/components/PhoneVerificationPanel.tsx`, `frontend/src/pages/RegisterPage.tsx`, `frontend/src/pages/SettingsPage.tsx`, `frontend/src/__tests__/PhoneVerificationPanel.test.tsx`, `frontend/src/__tests__/RegisterPage.test.tsx`
- Configuration/docs: `.env.example`, `backend/requirements.txt`, `backend/pyproject.toml`, `docs/TEXTBEE_OTP_SETUP.md`, `docs/STATUS.md`

## Verification performed

- `python -m pytest backend\tests -q` — **134 passed, 12 skipped**. All provider HTTP calls in enabled tests are mocked. PostgreSQL OTP integration tests are opt-in and were skipped.
- In `frontend/`: `npm.cmd run typecheck` — passed; `npm.cmd test` — **60 passed**; `npm.cmd run build` — passed with the existing non-blocking large-chunk advisory.
- In `backend/`: `python -m alembic heads` — single head `0015_textbee_phone_otp`.
- In `backend/`: `python -m alembic upgrade head --sql` — offline SQL generation passed. This did not connect to or alter any database.
- Official TextBee docs were checked for the endpoint, body, response envelope, batch identifier, acceptance semantics, and device setup.

## Not verified / owner actions

1. The existing root `.env` was left untouched. Add the variable names and values documented in [TEXTBEE_OTP_SETUP.md](./TEXTBEE_OTP_SETUP.md), keeping the TextBee API key and `OTP_HMAC_SECRET` server-side and distinct. The project is not yet confirmed to have TextBee credentials or an online registered Android device.
2. Review migration `0015_textbee_phone_otp` and apply it only to a backed-up, designated local/test PostgreSQL database. No migration was run and no database was accessed in this pass.
3. After configuration and migration, run `python -m scripts.test_textbee_otp +91...` from `backend/`. It sends one real SMS only after interactive `SEND` confirmation. No SMS was sent during implementation.
4. Confirm receipt and successful verification on a real handset. Until delivery status is independently confirmed, the server records the TextBee request as `pending`; no claim of carrier/handset delivery is made.

Setup, commands, rate-limit defaults, and TextBee's Android/SIM requirements are documented in [TEXTBEE_OTP_SETUP.md](./TEXTBEE_OTP_SETUP.md).
