# TextBee phone verification setup

The backend sends registration and phone-change OTPs through TextBee. An API `200` means TextBee accepted the message into its queue; it does not prove that the carrier delivered it to the handset. The service stores TextBee's `smsBatchId` (when TextBee returns one) and records delivery as `pending`; the real-SMS script below polls `GET /gateway/messages?smsBatchId=` and shows `sent`/`delivered`/`failed`. TextBee instances that dispatch immediately answer with `successCount`/`failureCount` instead of a batch ID, and both forms are accepted. The batch ID is kept server-side and is not returned to the browser; challenge responses stay generic to reduce account/phone enumeration.

## Configure TextBee

1. Create a TextBee account and verify its email address.
2. Install the Android app from the official TextBee download page, connect a phone with an active SMS-capable SIM, register the device, and grant the requested permissions.
3. Keep the Android device online and allow TextBee to run without battery restrictions.
4. Create an API key in the TextBee dashboard. An optional device ID can pin sends to one registered phone.
5. Paste the key into the existing root `.env` (do not replace the file) and restart the backend:

   ```dotenv
   TEXTBEE_API_KEY=your_key_here
   ```

   **That is the only required setting.** Everything else is automatic or optional:

   | Variable | Default / behaviour |
   |---|---|
   | `SMS_PROVIDER` | Auto-selected as `textbee` when `TEXTBEE_API_KEY` is set. An explicit value (e.g. `twilio`) wins. |
   | `OTP_HMAC_SECRET` | Optional. If blank, a separate 64-char key is derived from `JWT_SECRET_KEY` (needs 32+ chars). Set it explicitly to use an independent secret. Rotating the source secret only invalidates in-flight (5 minute) codes. |
   | `TEXTBEE_DEVICE_ID` | Optional. Blank uses your TextBee default device. |
   | `TEXTBEE_BASE_URL` | `https://api.textbee.dev/api/v1` (other hosts are rejected). |
   | `OTP_*` limits | 300 s expiry (fixed), 60 s resend cooldown, 5 attempts, 3 sends per 15 min. |

   On startup the backend logs `Phone verification (SMS OTP) is ready via textbee.` or a warning naming exactly what is missing. Never add the key to a `VITE_` variable or the frontend.

## Local migration and real-SMS check

Use only a designated local/test PostgreSQL database. Back it up and review the migration before applying it; do not point this step at production.

```powershell
Set-Location backend
alembic upgrade head
python -m scripts.test_textbee_otp +919876543210
```

The standalone script refuses to run without TextBee configuration or in test/demo mode. It displays a real-SMS warning and sends nothing unless the operator types `SEND`. It then prompts for the received code and calls the same production challenge issue/verification service used by the API. It does not print the OTP, verifier, or credentials.

## Security and behavior

- Codes are six cryptographically generated decimal digits, stored only as an HMAC verifier bound to challenge, purpose, E.164 phone, user, and organization.
- The backend enforces a 300-second expiry, resend cooldown, issuance limits, five failed attempts, and row-locked single-use verification.
- Registration codes are never returned to the frontend. The browser only collects the code entered by the user; it does not generate or verify codes.
- Phone changes require an authenticated account and a new verification challenge. The account phone is changed only after successful verification; the existing verified number remains in place if the new challenge fails or expires.
- Registration and phone change do not alter login or server-backed TOTP MFA.
- No request is automatically retried after a provider failure because the send endpoint's idempotency behavior is not established.
- TextBee sends through the registered Android phone's SIM. Check TextBee's message history or its delivery-status facilities for carrier/handset evidence; API acceptance alone remains `pending`.

Official references: [Sending SMS](https://textbee.dev/docs/sending-sms), [API request and response details](https://textbee.dev/docs/sending-sms/sending-sms), and [Setting up TextBee](https://textbee.dev/docs/getting-started/setting-up-textbee).
