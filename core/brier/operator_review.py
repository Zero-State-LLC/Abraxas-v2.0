from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OperatorBrierReviewPacket(BaseModel):
    schema_version: Literal["OperatorBrierReviewPacket.v1"] = "OperatorBrierReviewPacket.v1"
    review_id: str
    ledger_hash: str
    reliability_score: float
    replay_failures: int
    pending_actions: list[str]
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode='after')
    def _validate(self) -> "OperatorBrierReviewPacket":
        self.authority.assert_locked()
        if "autonomous_reliability_mutation" in self.pending_actions or "execute_production" in self.pending_actions:
            raise ValueError("no autonomous calibration mutation")
        return self
