from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SandboxStabilizationPacket(BaseModel):
    schema_version: Literal["SandboxStabilizationPacket.v1"] = "SandboxStabilizationPacket.v1"
    stabilization_id: str
    branch_hash: str
    replay_match_count: int
    replay_failure_count: int
    stabilization_window: int
    convergence_score: float
    stabilization_state: Literal["unstable", "stabilizing", "stable", "failed"]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "SandboxStabilizationPacket":
        self.authority.assert_locked()
        if self.replay_failure_count > 0 and self.stabilization_state == "stable":
            raise ValueError("replay mismatch invalidates stabilization")
        return self
