from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class CalibrationHistoryPacket(BaseModel):
    schema_version: Literal["CalibrationHistoryPacket.v1"] = "CalibrationHistoryPacket.v1"
    calibration_history_id: str
    forecast_hash: str
    calibration_scores: list[float]
    moving_average: float
    deterministic_history_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_average(scores: list[float]) -> float:
        return round(sum(scores) / len(scores), 6) if scores else 0.0

    @staticmethod
    def compute_hash(forecast_hash: str, scores: list[float], moving_average: float) -> str:
        return hashlib.sha256(f"{forecast_hash}|{'|'.join(f'{s:.6f}' for s in scores)}|{moving_average:.6f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "CalibrationHistoryPacket":
        self.authority.assert_locked()
        if self.moving_average != self.compute_average(self.calibration_scores):
            raise ValueError("deterministic averaging")
        if self.deterministic_history_hash != self.compute_hash(self.forecast_hash, self.calibration_scores, self.moving_average):
            raise ValueError("replay-safe history generation")
        return self
