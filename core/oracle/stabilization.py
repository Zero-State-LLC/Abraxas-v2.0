from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class IntakeStabilizationPacket(BaseModel):
    schema_version: Literal["IntakeStabilizationPacket.v1"] = "IntakeStabilizationPacket.v1"
    stabilization_id: str
    intake_hash: str
    replay_match_count: int
    replay_failure_count: int
    conflict_count: int
    stabilization_window: int
    stabilization_state: Literal["unstable", "stabilizing", "stable", "conflicted", "failed"]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "IntakeStabilizationPacket":
        self.authority.assert_locked()
        if self.stabilization_state == "stable" and (self.replay_failure_count > 0 or self.conflict_count > 0):
            raise ValueError("unresolved conflicts block stable state")
        return self
