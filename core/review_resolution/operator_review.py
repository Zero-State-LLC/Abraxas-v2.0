from __future__ import annotations
from typing import Literal
from pydantic import BaseModel

class ReviewResolutionOperatorReviewPacket(BaseModel):
    schema_version: Literal["ReviewResolutionOperatorReviewPacket.v1"] = "ReviewResolutionOperatorReviewPacket.v1"
    review_id: str
    pending_reviews: int
    unresolved_blockers: int
    critical_diagnostics: int
    pending_actions: list[str]
    status: Literal["approved", "pending", "blocked"]
