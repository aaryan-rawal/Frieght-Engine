"""Route entity definition.

Original onward route for a truck. All numeric values follow the *null‑not‑zero* rule.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, validator

class Route(BaseModel):
    id: str
    truck_id: str
    origin_lat: float
    origin_lng: float
    destination_lat: float
    destination_lng: float
    polyline: Optional[str] = None
    distance_km: float
    baseline_driving_minutes: float
    verified: bool = False
    version: int

    @validator("distance_km", "baseline_driving_minutes")
    def positive(cls, v):
        if v <= 0:
            raise ValueError("must be positive")
        return v
