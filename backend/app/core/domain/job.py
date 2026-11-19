"""Job entity definition.

A Job groups one or more Cargo records. It may be a bundle (multiple cargo) or a single cargo.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import Verdict, ClaimTag

class Job(BaseModel):
    id: str
    cargo_ids: List[str]
    is_bundle: bool = False
    pickup_cluster_radius_km: Optional[float] = None
    drop_cluster_radius_km: Optional[float] = None

    # No special validators – clustering radii are optional and follow null‑not‑zero via base validator if needed.
