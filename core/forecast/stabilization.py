from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ForecastStabilizationPacket(BaseModel):
    schema_version: Literal["ForecastStabilizationPacket.v1"] = "ForecastStabilizationPacket.v1"
    stabilization_id: str
    forecast_hash: str
    replay_match_count: int
    replay_failure_count: int
    calibration_score: float
    unresolved_bindings: int
    stabilization_window: int
    stabilization_state: Literal["unstable", "stabilizing", "stable", "conflicted", "failed"]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "ForecastStabilizationPacket":
        self.authority.assert_locked()
        if self.stabilization_state == "stable" and (self.unresolved_bindings > 0 or self.replay_failure_count > 0):
            raise ValueError("unresolved bindings prevent stable promotion")
        return self
