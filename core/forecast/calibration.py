from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ForecastCalibrationPacket(BaseModel):
    schema_version: Literal["ForecastCalibrationPacket.v1"] = "ForecastCalibrationPacket.v1"
    calibration_id: str
    forecast_hash: str
    calibration_method: Literal["replay_consistency", "stabilization_consistency", "sandbox_consistency", "lineage_consistency"]
    calibration_score: float
    deterministic_calibration_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(forecast_hash: str, method: str, score: float) -> str:
        return hashlib.sha256(f"{forecast_hash}|{method}|{score:.6f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ForecastCalibrationPacket":
        self.authority.assert_locked()
        if not 0 <= self.calibration_score <= 1:
            raise ValueError("score range [0,1]")
        if self.deterministic_calibration_hash != self.compute_hash(self.forecast_hash, self.calibration_method, self.calibration_score):
            raise ValueError("deterministic calibration")
        return self
