from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class BrierStabilizationPacket(BaseModel):
    schema_version: Literal["BrierStabilizationPacket.v1"] = "BrierStabilizationPacket.v1"
    stabilization_id: str
    ledger_hash: str
    replay_match_count: int
    replay_failure_count: int
    reliability_score: float
    stabilization_window: int
    stabilization_state: Literal["unstable", "stabilizing", "stable", "conflicted", "failed"]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode='after')
    def _validate(self) -> "BrierStabilizationPacket":
        self.authority.assert_locked()
        if self.stabilization_state == "stable" and self.replay_failure_count > 0:
            raise ValueError("unresolved score mismatches block stable state")
        return self
