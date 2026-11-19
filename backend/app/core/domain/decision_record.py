"""DecisionRecord entity definition.

Captures all rule checks for a single job match and the final eligibility verdict.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import Verdict, ClaimTag
from .check_result import CheckResult

class DecisionRecord(BaseModel):
    id: str
    match_run_id: str
    job_id: str
    route_class: Optional[str] = None
    checks: List[CheckResult] = Field(default_factory=list)
    eligible: Verdict
    rejection_codes: List[str] = Field(default_factory=list)
    pickup_access_km: Optional[float] = None
    excursion_km: Optional[float] = None
    extra_distance_km: Optional[float] = None
    extra_active_minutes: Optional[float] = None
    revenue_inr: Optional[float] = None
    incremental_cost_inr: Optional[float] = None
    net_inr_low: Optional[float] = None
    net_inr_expected: Optional[float] = None
    net_inr_high: Optional[float] = None
    baseline_score: Optional[float] = None
    model_scores: Optional[dict] = None
    explanation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
