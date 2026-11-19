"""Budget rule (D‑017, D‑018).

Applies the detour‑budget multiplier based on total trip distance.
The multiplier is 1.25× up to 1000 km, rises linearly to 1.35× at 1500 km, then caps at 1.35×.
If the effective distance (baseline + extra) exceeds the allowed budget, the rule returns ``Verdict.fail``.
"""

from __future__ import annotations

from .check_result import CheckResult
from ..domain.enums import Verdict, ClaimTag

def budget_multiplier(total_distance_km: float) -> float:
    """Return the allowed multiplier for the given total distance.

    Implements the piecewise linear function described in D‑018.
    """
    if total_distance_km <= 1000:
        return 1.25
    if total_distance_km >= 1500:
        return 1.35
    # Linear interpolation between (1000,1.25) and (1500,1.35)
    slope = (1.35 - 1.25) / (1500 - 1000)
    return 1.25 + slope * (total_distance_km - 1000)

def check_budget(baseline_distance_km: float, extra_distance_km: float) -> CheckResult:
    """Validate that the total distance stays within the allowed budget.

    Args:
        baseline_distance_km: Original route distance.
        extra_distance_km: Detour distance added by off‑route stops.
    Returns:
        ``CheckResult`` with rule code ``BGT001``.
    """
    total = baseline_distance_km + extra_distance_km
    allowed_multiplier = budget_multiplier(baseline_distance_km)
    allowed_distance = baseline_distance_km * allowed_multiplier
    if total <= allowed_distance:
        verdict = Verdict.pass_
        message = f"Total {total:.2f} km within budget {allowed_distance:.2f} km (multiplier {allowed_multiplier:.2f})"
    else:
        verdict = Verdict.fail
        message = f"Total {total:.2f} km exceeds budget {allowed_distance:.2f} km (multiplier {allowed_multiplier:.2f})"
    return CheckResult(
        rule_code="BGT001",
        verdict=verdict,
        value=total,
        threshold=allowed_distance,
        unit="km",
        claim_tag=ClaimTag.calculation,
        message=message,
    )
