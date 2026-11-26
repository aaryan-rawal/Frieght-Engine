# Subscription page: demo-only contract

The subscription page is a college-project demonstration. It records a selected plan and billing cycle but does not charge a card, create a paid subscription, grant a verified payment entitlement, or contact a payment provider.

## Server behavior

- `GET /api/billing/subscription` returns the saved demo selection for the signed-in user or organization scope. If none exists, it returns an unsaved demo preview based on the account tier.
- `POST /api/billing/subscription` saves a plan and billing cycle. The server validates allowed values and uses a unique scope key/upsert to avoid duplicate organization selections.
- `POST /api/billing/subscription/cancel` marks an existing demo selection to end. Status remains `demo`; it does not cancel a real recurring payment.
- The request schema accepts no price or payment credentials. The frontend prices are labelled indicative only.
- Mock mode stores demo selections in browser storage, separately per user. HTTP mode uses the server and PostgreSQL.

## Database and release note

Migration `0013_demo_subscriptions` adds the demo-selection table. The migration is the current Alembic head but has **not** been applied to any database in this work. Apply it only through the project's backed-up, owner-approved migration procedure before using the HTTP billing endpoints.

Real payment-provider onboarding, webhooks, reconciliation, refunds, invoices, tax handling, and entitlement activation remain out of scope and are not implemented. Do not treat demo plan selection as payment activation.
