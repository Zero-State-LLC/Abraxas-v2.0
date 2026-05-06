from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class OperatorOverlayRiskReviewPacket(BaseModel):
    schema_version: Literal["OperatorOverlayRiskReviewPacket.v1"] = "OperatorOverlayRiskReviewPacket.v1"
    review_id: str
    aggregate_risk_score: float = Field(ge=0, le=1)
    critical_diagnostics: int = Field(ge=0)
    pending_actions: list[str]
    status: Literal["approved", "pending", "blocked"]
