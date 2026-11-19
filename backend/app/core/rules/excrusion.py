"""Excursion rule.

The 40 km excursion cap (D‑010) limits the round‑trip detour for any off‑route stop.
If the reported excursion distance exceeds 40 km the rule returns ``Verdict.fail``;
exactly 40 km passes; any value ``None`` yields ``Verdict.unknown``.
"""

from __future__ import annotations

from .check_result import CheckResult
from ..domain.enums import Verdict, ClaimTag

MAX_EXCURSION_KM = 40.0

def check_excursion(excursion_km: float | None) -> CheckResult:
    """Validate a single excursion distance.

    Args:
        excursion_km: Detour distance in kilometres, or ``None`` if unknown.
    Returns:
        ``CheckResult`` with rule code ``EXC001``.
    """
    if excursion_km is None:
        verdict = Verdict.unknown
        message = "Excursion distance not provided"
    elif excursion_km <= MAX_EXCURSION_KM:
        verdict = Verdict.pass_
        message = f"Excursion {excursion_km:.2f} km within limit"
    else:
        verdict = Verdict.fail
        message = f"Excursion {excursion_km:.2f} km exceeds 40 km cap"
    return CheckResult(
        rule_code="EXC001",
        verdict=verdict,
        value=excursion_km,
        threshold=MAX_EXCURSION_KM,
        unit="km",
        claim_tag=ClaimTag.calculation,
        message=message,
    )
