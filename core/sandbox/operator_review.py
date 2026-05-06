from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OperatorSandboxReviewPacket(BaseModel):
    schema_version: Literal["OperatorSandboxReviewPacket.v1"] = "OperatorSandboxReviewPacket.v1"
    review_id: str
    branch_hash: str
    pending_mutations: list[str]
    stabilization_state: str
    rollback_available: bool
    convergence_score: float
    operator_actions: list[str]
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "OperatorSandboxReviewPacket":
        self.authority.assert_locked()
        if "execute_production" in self.operator_actions:
            raise ValueError("no production execution authority")
        return self
