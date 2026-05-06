from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OperatorIntakeReviewPacket(BaseModel):
    schema_version: Literal["OperatorIntakeReviewPacket.v1"] = "OperatorIntakeReviewPacket.v1"
    review_id: str
    intake_hash: str
    pending_conflicts: list[str]
    stabilization_state: str
    replay_status: str
    operator_actions: list[str]
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "OperatorIntakeReviewPacket":
        self.authority.assert_locked()
        if "execute_production" in self.operator_actions:
            raise ValueError("no execution authority")
        return self
