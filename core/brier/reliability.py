from __future__ import annotations

import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class ReliabilityAggregatePacket(BaseModel):
    schema_version: Literal["ReliabilityAggregatePacket.v1"] = "ReliabilityAggregatePacket.v1"
    reliability_id: str
    forecast_hashes: list[str]
    average_brier: float
    calibration_average: float
    reliability_score: float
    deterministic_reliability_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(forecast_hashes: list[str], average_brier: float, calibration_average: float, reliability_score: float) -> str:
        return hashlib.sha256(f"{'|'.join(sorted(forecast_hashes))}|{average_brier:.6f}|{calibration_average:.6f}|{reliability_score:.6f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "ReliabilityAggregatePacket":
        self.authority.assert_locked()
        if self.deterministic_reliability_hash != self.compute_hash(self.forecast_hashes, self.average_brier, self.calibration_average, self.reliability_score):
            raise ValueError("deterministic aggregation")
        return self
