"""Cargo entity definition.

Represents a freight listing. All optional numeric fields follow the *null‑not‑zero* rule.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from .enums import SourceType, ListingStatus, Verdict, ClaimTag, ShipmentStatus, RouteClass

class Cargo(BaseModel):
    id: str
    source_type: SourceType
    source_id: Optional[str] = None
    category: str
    description: Optional[str] = None
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    length_m: Optional[float] = None
    width_m: Optional[float] = None
    height_m: Optional[float] = None
    pickup_lat: float
    pickup_lng: float
    drop_lat: float
    drop_lng: float
    pickup_window_start: Optional[datetime] = None
    pickup_window_end: Optional[datetime] = None
    delivery_deadline: Optional[datetime] = None
    rate_inr: Optional[float] = None
    hazardous: Optional[bool] = None
    temperature_controlled: Optional[bool] = None
    over_dimensional: Optional[bool] = None
    required_body_types: List[str] = Field(default_factory=list)
    status: ListingStatus
    created_at: datetime
    updated_at: datetime
    verification_status: str
    completeness_flags: List[str] = Field(default_factory=list)
    reliability_score: Optional[float] = None

    @validator(
        "weight_kg",
        "volume_m3",
        "length_m",
        "width_m",
        "height_m",
        "rate_inr",
        "reliability_score",
    )
    def not_zero_if_present(cls, v):
        if v is not None and v == 0:
            raise ValueError("Numeric fields must be either None or non‑zero")
        return v
