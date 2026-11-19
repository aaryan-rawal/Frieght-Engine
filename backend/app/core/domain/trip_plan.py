"""TripPlan entity definition.

Aggregates ordered jobs for a route and tracks distance / time usage.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

class TripPlan(BaseModel):
    id: str
    route_id: str
    route_version: int
    config_version: int
    jobs: List[str]  # list of Job IDs in order
    distance_km: float
    active_minutes: float
    jobs_used_total: int
    jobs_used_by_day: Dict[str, int]  # date string -> count
    budget_distance_used_fraction: float
    budget_time_used_fraction: float
    plan_status: str  # could be Verdict enum, keep as str for now
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("distance_km", "active_minutes")
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("must be non‑negative")
        return v
