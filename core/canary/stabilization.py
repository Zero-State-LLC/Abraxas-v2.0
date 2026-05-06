from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryStabilizationPacket(BaseModel):
    schema_version: Literal["CanaryStabilizationPacket.v1"] = "CanaryStabilizationPacket.v1"
    stabilization_id: str
    overlay_hash: str
    replay_match_count: int
    replay_failure_count: int
    calibration_score: float
    rollback_readiness: bool
    stabilization_window: int
    stabilization_state: Literal["unstable", "stabilizing", "stable", "conflicted", "failed"]
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @model_validator(mode="after")
    def _validate(self) -> "CanaryStabilizationPacket":
        self.authority.assert_locked()
        if self.replay_failure_count > 0 and self.stabilization_state == "stable":
            raise ValueError("unresolved mismatch blocks stable")
        if not self.rollback_readiness:
            raise ValueError("rollback readiness required")
        return self
