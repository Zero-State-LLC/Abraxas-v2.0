from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class DriftStabilizationPacket(BaseModel):
    schema_version: Literal["DriftStabilizationPacket.v1"] = "DriftStabilizationPacket.v1"
    stabilization_id: str
    overlay_hash: str
    replay_match_count: int
    replay_failure_count: int
    calibration_score: float
    drift_confidence: float
    stabilization_window: int
    stabilization_state: Literal["unstable", "stabilizing", "stable", "conflicted", "failed"]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode='after')
    def _validate(self) -> "DriftStabilizationPacket":
        self.authority.assert_locked()
        if self.stabilization_state == "stable" and self.replay_failure_count > 0:
            raise ValueError("unresolved mismatches block stable state")
        return self
