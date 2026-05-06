from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class OperatorOverlayResolutionReviewPacket(BaseModel):
    schema_version: Literal["OperatorOverlayResolutionReviewPacket.v1"] = "OperatorOverlayResolutionReviewPacket.v1"
    review_id: str
    pending_reviews: int
    critical_diagnostics: int
    unresolved_events: int
    pending_actions: list[str]
    status: Literal["approved", "pending", "blocked"]
