from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OperatorDriftReviewPacket(BaseModel):
    schema_version: Literal["OperatorDriftReviewPacket.v1"] = "OperatorDriftReviewPacket.v1"
    review_id: str
    overlay_hash: str
    calibration_score: float
    drift_confidence: float
    replay_failures: int
    pending_actions: list[str]
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode='after')
    def _validate(self) -> "OperatorDriftReviewPacket":
        self.authority.assert_locked()
        if "autonomous_weight_mutation" in self.pending_actions or "execute_production" in self.pending_actions:
            raise ValueError("no autonomous weight mutation")
        return self
