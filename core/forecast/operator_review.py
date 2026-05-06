from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OperatorForecastReviewPacket(BaseModel):
    schema_version: Literal["OperatorForecastReviewPacket.v1"] = "OperatorForecastReviewPacket.v1"
    review_id: str
    forecast_hash: str
    stabilization_state: str
    calibration_score: float
    unresolved_bindings: int
    pending_actions: list[str]
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "OperatorForecastReviewPacket":
        self.authority.assert_locked()
        if "autonomous_promotion" in self.pending_actions or "execute_production" in self.pending_actions:
            raise ValueError("no autonomous promotion")
        return self
