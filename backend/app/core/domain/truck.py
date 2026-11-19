"""Truck entity definition.

Represents a vehicle owned by a user. All numeric fields are optional and follow the
*null‑not‑zero* rule: if a value is unknown it must be `None`, never `0`.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from .enums import (
    SourceType,
    ListingStatus,
    Verdict,
    ClaimTag,
    ShipmentStatus,
    RouteClass,
)

class Truck(BaseModel):
    id: str
    owner_id: str
    vehicle_class: str
    body_type: str
    max_payload_kg: float
    available_payload_kg: Optional[float] = None
    available_volume_m3: Optional[float] = None
    loaded_mileage_km_per_l: Optional[float] = None
    handling_equipment: List[str] = Field(default_factory=list)
    cargo_restrictions: List[str] = Field(default_factory=list)
    available_from: Optional[datetime] = None
    location_lat: float
    location_lng: float

    @validator(
        "available_payload_kg",
        "available_volume_m3",
        "loaded_mileage_km_per_l",
    )
    def not_zero_if_present(cls, v):
        if v is not None and v == 0:
            raise ValueError("Numeric fields must be either None or non‑zero")
        return v
