from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class DriftCalibrationPacket(BaseModel):
    schema_version: Literal["DriftCalibrationPacket.v1"] = "DriftCalibrationPacket.v1"
    calibration_id: str
    overlay_hash: str
    replay_consistency: float
    reliability_consistency: float
    stabilization_consistency: float
    calibration_score: float
    deterministic_calibration_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(overlay_hash: str, replay_consistency: float, reliability_consistency: float, stabilization_consistency: float, calibration_score: float) -> str:
        return hashlib.sha256(f"{overlay_hash}|{replay_consistency:.6f}|{reliability_consistency:.6f}|{stabilization_consistency:.6f}|{calibration_score:.6f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "DriftCalibrationPacket":
        self.authority.assert_locked()
        if not 0 <= self.calibration_score <= 1:
            raise ValueError("score range [0,1]")
        if self.deterministic_calibration_hash != self.compute_hash(self.overlay_hash, self.replay_consistency, self.reliability_consistency, self.stabilization_consistency, self.calibration_score):
            raise ValueError("deterministic calibration")
        return self
