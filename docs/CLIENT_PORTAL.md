# Client Portal

The Client Portal is the fifth OptiFreight role portal. Client accounts publish and manage their own cargo listings; the existing `client` account role is used rather than introducing a duplicate role.

## Role hierarchy

The Client Portal is on the **same hierarchy tier as the Company Portal**. Both are independent Tier 2 account portals, directly below the Owner tier. Neither portal is subordinate to the other, and neither inherits the other's permissions or data access:

1. **Tier 1 — Owner Portal** (one environment-configured account)
2. **Tier 2 — Company Portal and Client Portal** (equal peers)
3. **Tier 3 — Company Admin Portal**
4. **Tier 4 — Driver Portal**

A client account remains a separate `client` role. It manages only cargo listings it owns; it does not gain company-owner permissions, company administration access, or access to another client's listings. A company owner does not gain access to client accounts or their private listings merely by being on the same tier. Backend role checks and ownership checks remain authoritative.

## Frontend entry points

- `/client` — Client Portal
- `/client/portal` — Client Portal alias
- `/client/jobs` — Client cargo listing workspace (canonical navigation target)

Only a signed-in `client` role is allowed to use this page. The application navigation labels this destination **Client Portal**.

## Cargo listing information

A client can provide:

- Cargo description and category
- Weight, payment/rate and package count
- Pickup and delivery places, including map coordinates
- Pickup time window
- Cargo food-storage classification
- Dimensions and volume
- Required vehicle type and special handling requirements
- Loading, unloading and waiting time
- Hazardous-cargo flag, handling description and supporting safety evidence

## Listing validity

The backend is authoritative and sets `expires_at` at creation time:

| Cargo classification | Listing validity |
| --- | ---: |
| Food item — non-refrigerated | 12 hours |
| Food item — refrigerated | 24 hours |
| Non-food cargo | 24 hours |

The frontend displays the applicable validity and expiry timestamp. The API returns `listing_status: "expired"` after expiry and persists the expired state for open listings when the client's listings are retrieved. Expiry is based on UTC server time, not the browser clock.

Existing cargo rows are backfilled to expire 24 hours after their original `created_at` timestamp.

## Backend changes

- `POST /api/cargo/manual` creates a client-owned cargo listing and computes its expiry.
- `GET /api/cargo/manual` returns only the signed-in client's listings, including expiry metadata.
- Matching includes only unexpired, open client-published listings.
- Shipment acceptance rechecks the source listing expiry and availability on the server, so an old matching result cannot accept an expired listing.
- `DELETE /api/cargo/manual/{cargo_id}` deletes only a listing owned by that client.
- Non-client roles receive HTTP 403 from these client listing endpoints.
- Alembic migration `0010_client_cargo_expiry` adds cargo-detail fields and `expires_at`.

Apply the migration locally after backing up the database:

```bash
cd backend
alembic upgrade head
```

Do not run this migration against a production database without the normal backup and approval process.
