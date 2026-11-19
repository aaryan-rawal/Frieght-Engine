"""CheckResult entity definition.

Represents the outcome of a single deterministic rule check.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from .enums import Verdict, ClaimTag

class CheckResult(BaseModel):
    rule_code: str
    verdict: Verdict
    value: Optional[float] = None
    threshold: Optional[float] = None
    unit: Optional[str] = None
    claim_tag: ClaimTag
    message: str
