from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority

_ALLOWED = {"unstable", "stabilizing", "stable", "failed"}


class StateStabilizationPacket(BaseModel):
    schema_version: Literal["StateStabilizationPacket.v1"] = "StateStabilizationPacket.v1"
    stabilization_id: str
    state_hash: str
    replay_match_count: int
    replay_failure_count: int
    stabilization_window: int
    stabilization_state: str
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "StateStabilizationPacket":
        self.authority.assert_locked()
        if self.stabilization_state not in _ALLOWED:
            raise ValueError("invalid stabilization_state")
        return self
