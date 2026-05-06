from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OverlayStabilityPacket(BaseModel):
    schema_version: Literal["OverlayStabilityPacket.v1"] = "OverlayStabilityPacket.v1"
    stability_id: str
    fusion_hash: str
    replay_match_count: int
    replay_failure_count: int
    rollback_count: int
    diagnostic_count: int
    stability_score: float
    stability_state: Literal["stable", "watch", "unstable", "failed"]
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @model_validator(mode="after")
    def _v(self) -> "OverlayStabilityPacket":
        self.authority.assert_locked()
        if not 0 <= self.stability_score <= 1:
            raise ValueError("score")
        return self
