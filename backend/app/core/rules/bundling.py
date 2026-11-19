"""Bundling rule (D‑015, D‑016).

Checks if a set of cargos can be bundled: all pickups must be within a 5 km radius and all drops within a 5 km radius (straight‑line distance).
If the condition holds, the rule returns ``Verdict.pass_``; otherwise ``Verdict.fail``. If any coordinates are missing it returns ``Verdict.unknown``.
"""

from __future__ import annotations

from math import radians, cos, sin, asin, sqrt
from typing import List, Tuple

from .check_result import CheckResult
from ..domain.enums import Verdict, ClaimTag

EARTH_RADIUS_KM = 6371.0

def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return great‑circle distance in kilometres between two lat/lng points."""
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = (sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2)
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))

def _max_pairwise_distance(points: List[Tuple[float, float]]) -> float:
    max_dist = 0.0
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = haversine(points[i][0], points[i][1], points[j][0], points[j][1])
            if d > max_dist:
                max_dist = d
    return max_dist

def check_bundling(pickup_coords: List[Tuple[float, float]], drop_coords: List[Tuple[float, float]]) -> CheckResult:
    """Validate bundling eligibility for a collection of cargos.

    Args:
        pickup_coords: List of ``(lat, lng)`` for each cargo’s pickup.
        drop_coords:   List of ``(lat, lng)`` for each cargo’s drop.
    Returns:
        ``CheckResult`` with rule code ``BND001``.
    """
    if not pickup_coords or not drop_coords:
        verdict = Verdict.unknown
        message = "Missing pickup or drop coordinates"
        return CheckResult(
            rule_code="BND001",
            verdict=verdict,
            claim_tag=ClaimTag.calculation,
            message=message,
        )

    max_pickup = _max_pairwise_distance(pickup_coords)
    max_drop = _max_pairwise_distance(drop_coords)
    radius = 5.0
    if max_pickup <= radius and max_drop <= radius:
        verdict = Verdict.pass_
        message = f"All pickups ({max_pickup:.2f} km) and drops ({max_drop:.2f} km) within {radius} km radius"
    else:
        verdict = Verdict.fail
        message = f"Bundling radius exceeded: pickups {max_pickup:.2f} km, drops {max_drop:.2f} km"
    return CheckResult(
        rule_code="BND001",
        verdict=verdict,
        value=None,
        threshold=radius,
        unit="km",
        claim_tag=ClaimTag.calculation,
        message=message,
    )
