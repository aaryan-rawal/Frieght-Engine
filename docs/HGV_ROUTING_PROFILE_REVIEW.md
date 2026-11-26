# India HGV routing profile review

## Current evidence

- A candidate baseline exists at `routing/profiles/hgv.lua`. It uses OSRM profile API v4 and standard way handlers, prioritizes HGV/goods access tags, and defines one static vehicle envelope: 3.8 m height, 2.6 m width, 16.5 m length and 49,000 kg.
- `routing/Dockerfile.osrm`, `routing/build_osrm_data.sh` and `routing/docker-compose.osrm.yml` provide a local graph-build/serve path.
- The project inventory contains no OSM PBF or preprocessed OSRM graph under `routing/data/`. The profile has not been built or independently reviewed against Indian HGV law or actual corridor restrictions.
- `OSRM_TRUCK_PROFILE_CONFIRMED` defaults to false. A valid OSRM road response is not by itself HGV or legal verification.
- The 40.0 km inclusive combined excursion boundary has unit tests using a fake routing result. This confirms application comparison behavior, not real-road distance accuracy.
- No live routing request was made for this review. External routing fallbacks are disabled by default; enabling one requires explicit configuration because route coordinates leave the local service.

## Review blockers

1. A qualified reviewer must verify the OSM profile handlers, access-tag precedence, conditional restrictions, vehicle dimensions/weight and speed assumptions against the intended Indian vehicle classes and applicable current rules.
2. The owner must select the first supported vehicle classes and approve a profile envelope for each. The single 49,000 kg profile cannot represent every registered truck or axle configuration.
3. Obtain a legally usable, appropriately current OSM PBF, document its coverage/date and licensing, then build the graph locally.
4. Compare route distance, connectivity, HGV access and ETA on representative India corridors against independent/field-verified references, including relevant bridges, road classes, toll roads and restricted urban areas.
5. Test endpoint snapping, multi-leg round-trip excursions, detour-boundary cases and behavior when a road is missing or restricted. Regulatory checks must remain separate and fail closed.
6. Record reviewer, profile/version, map extract date, tested corridors, discrepancies and approval before setting `OSRM_TRUCK_PROFILE_CONFIRMED=true`.

## Decision

**NOT VERIFIED / NOT APPROVED FOR HGV ELIGIBILITY.** Keep route-dependent candidates ineligible when the truck profile or relevant regulatory evidence is unknown. The profile is useful as a local research starting point, not as evidence of safe, legal routing.
