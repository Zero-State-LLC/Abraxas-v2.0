from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OperatorStateReviewPacket(BaseModel):
    schema_version: Literal["OperatorStateReviewPacket.v1"] = "OperatorStateReviewPacket.v1"
    review_id: str
    state_hash: str
    pending_transitions: list[str]
    rollback_available: bool
    stabilization_state: str
    operator_actions: list[str]
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "OperatorStateReviewPacket":
        self.authority.assert_locked()
        if "approve_execution" in self.operator_actions and self.state_hash.startswith("projection:"):
            raise ValueError("projection-only states cannot approve execution")
        return self
