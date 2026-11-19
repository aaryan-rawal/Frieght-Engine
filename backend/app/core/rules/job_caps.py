"""Job caps rule implementation (D-010, D-011‑D-014).

Enforces the maximum number of jobs allowed for a given original route length and
per‑day limits. The function expects the total route distance (km) and a list of
already‑scheduled jobs with their pickup dates (ISO‑format strings).
"""

from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict
from typing import List, Tuple

from .check_result import CheckResult
from ..domain.enums import Verdict, ClaimTag

# Mapping from distance band (upper bound) to (total_jobs, max_per_day)
JOB_BANDS = [
    (500.0, (3, None)),               # no daily cap for <=500 km
    (1250.0, (5, 3)),                # max 5 total, <=3 per day
    (2000.0, (8, 4)),                # max 8 total, <=4 per day
    (float('inf'), (10, 4)),         # >2000 km
]

def _band_for_distance(dist_km: float) -> Tuple[int, int | None]:
    for upper, caps in JOB_BANDS:
        if dist_km <= upper:
            return caps
    raise AssertionError("No band found – unreachable")

def check_job_caps(
    route_distance_km: float,
    existing_jobs: List[Tuple[str, str]],  # (job_id, pickup_date_iso)
    new_job_pickup_date_iso: str,
) -> CheckResult:
    """Validate job‑count constraints.

    Args:
        route_distance_km: Length of the original route.
        existing_jobs: List of tuples ``(job_id, pickup_date_iso)`` for jobs that
            are already part of the current plan.
        new_job_pickup_date_iso: ISO‑8601 date string of the candidate job's pickup.
    Returns:
        ``CheckResult`` with rule code ``JOB001``.
    """
    total_allowed, per_day_allowed = _band_for_distance(route_distance_km)

    total_jobs = len(existing_jobs) + 1  # include the candidate
    if total_jobs > total_allowed:
        verdict = Verdict.fail
        message = f"Total jobs {total_jobs} exceed allowed {total_allowed} for {route_distance_km:.1f} km"
    else:
        verdict = Verdict.pass_
        message = f"Total jobs {total_jobs} within allowed {total_allowed}"

    # Daily cap check (if applicable)
    if per_day_allowed is not None:
        # Indian calendar day – convert to timezone-aware datetime in Asia/Kolkata
        # (tzdata is a dependency); we will treat the string as UTC for simplicity
        # because the backend stores UTC and the UI will convert.
        def to_date(iso: str) -> datetime:
            return datetime.fromisoformat(iso).replace(tzinfo=timezone.utc).astimezone(tz=None).date()
        new_day = to_date(new_job_pickup_date_iso)
        day_counts = defaultdict(int)
        for _, iso in existing_jobs:
            day_counts[to_date(iso)] += 1
        day_counts[new_day] += 1
        if any(cnt > per_day_allowed for cnt in day_counts.values()):
            verdict = Verdict.fail
            message = f"Day‑wise job count exceeds {per_day_allowed} per day"

    return CheckResult(
        rule_code="JOB001",
        verdict=verdict,
        value=total_jobs,
        threshold=total_allowed,
        unit="jobs",
        claim_tag=ClaimTag.calculation,
        message=message,
    )
