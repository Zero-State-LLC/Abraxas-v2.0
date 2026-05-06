from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class OperatorOverlayContainmentReviewPacket(BaseModel):
    schema_version: Literal["OperatorOverlayContainmentReviewPacket.v1"] = "OperatorOverlayContainmentReviewPacket.v1"
    review_id: str
    pending_reviews: int
    critical_diagnostics: int
    recommendation_count: int
    pending_actions: list[str]
    status: Literal["approved", "pending", "blocked"]
