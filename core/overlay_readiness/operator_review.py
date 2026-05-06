from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class OperatorOverlayReadinessReviewPacket(BaseModel):
    schema_version: Literal["OperatorOverlayReadinessReviewPacket.v1"] = "OperatorOverlayReadinessReviewPacket.v1"
    review_id: str
    pending_reviews: int
    critical_diagnostics: int
    readiness_band: str
    pending_actions: list[str]
    status: Literal["approved","pending","blocked"]
