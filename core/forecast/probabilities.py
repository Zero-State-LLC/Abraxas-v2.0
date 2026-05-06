from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ForecastProbabilityPacket(BaseModel):
    schema_version: Literal["ForecastProbabilityPacket.v1"] = "ForecastProbabilityPacket.v1"
    probability_id: str
    forecast_hash: str
    probability: float
    calibration_score: float
    deterministic_probability_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(forecast_hash: str, probability: float, calibration_score: float) -> str:
        return hashlib.sha256(f"{forecast_hash}|{probability:.6f}|{calibration_score:.6f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ForecastProbabilityPacket":
        self.authority.assert_locked()
        if not 0 <= self.probability <= 1:
            raise ValueError("probability range [0,1]")
        if not 0 <= self.calibration_score <= 1:
            raise ValueError("calibration required")
        if self.deterministic_probability_hash != self.compute_hash(self.forecast_hash, self.probability, self.calibration_score):
            raise ValueError("deterministic hashing")
        return self
