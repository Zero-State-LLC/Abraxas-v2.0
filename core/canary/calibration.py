from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryCalibrationPacket(BaseModel):
    schema_version: Literal["CanaryCalibrationPacket.v1"] = "CanaryCalibrationPacket.v1"
    calibration_id: str
    overlay_hash: str
    replay_consistency: float
    calibration_score: float
    bounded_influence_score: float
    rollback_readiness: bool
    deterministic_calibration_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, replay_consistency: float, calibration_score: float, bounded_influence_score: float, rollback_readiness: bool) -> str:
        return hashlib.sha256(f"{overlay_hash}|{replay_consistency:.6f}|{calibration_score:.6f}|{bounded_influence_score:.6f}|{rollback_readiness}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryCalibrationPacket":
        self.authority.assert_locked()
        for s in (self.replay_consistency, self.calibration_score, self.bounded_influence_score):
            if not 0.0 <= s <= 1.0:
                raise ValueError("score range [0,1]")
        if self.deterministic_calibration_hash != self.compute_hash(self.overlay_hash, self.replay_consistency, self.calibration_score, self.bounded_influence_score, self.rollback_readiness):
            raise ValueError("calibration hash mismatch")
        return self
