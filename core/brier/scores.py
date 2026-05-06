from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class BrierScorePacket(BaseModel):
    schema_version: Literal["BrierScorePacket.v1"] = "BrierScorePacket.v1"
    score_id: str
    forecast_hash: str
    expected_probability: float
    observed_outcome: int
    brier_score: float
    deterministic_score_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_score(expected_probability: float, observed_outcome: int) -> float:
        return round((expected_probability - observed_outcome) ** 2, 6)

    @staticmethod
    def compute_hash(forecast_hash: str, expected_probability: float, observed_outcome: int, brier_score: float) -> str:
        return hashlib.sha256(f"{forecast_hash}|{expected_probability:.6f}|{observed_outcome}|{brier_score:.6f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "BrierScorePacket":
        self.authority.assert_locked()
        if not 0 <= self.expected_probability <= 1:
            raise ValueError("probability range [0,1]")
        if self.observed_outcome not in {0, 1}:
            raise ValueError("observed_outcome binary {0,1}")
        if self.brier_score != self.compute_score(self.expected_probability, self.observed_outcome):
            raise ValueError("deterministic scoring")
        if self.deterministic_score_hash != self.compute_hash(self.forecast_hash, self.expected_probability, self.observed_outcome, self.brier_score):
            raise ValueError("deterministic hash")
        return self
