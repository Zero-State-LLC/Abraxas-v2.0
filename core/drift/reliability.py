from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class DriftReliabilityPacket(BaseModel):
    schema_version: Literal["DriftReliabilityPacket.v1"] = "DriftReliabilityPacket.v1"
    reliability_id: str
    overlay_hashes: list[str]
    average_reliability: float
    average_brier: float
    drift_confidence: float
    deterministic_reliability_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(overlay_hashes: list[str], average_reliability: float, average_brier: float, drift_confidence: float) -> str:
        return hashlib.sha256(f"{'|'.join(sorted(overlay_hashes))}|{average_reliability:.6f}|{average_brier:.6f}|{drift_confidence:.6f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "DriftReliabilityPacket":
        self.authority.assert_locked()
        if self.deterministic_reliability_hash != self.compute_hash(self.overlay_hashes, self.average_reliability, self.average_brier, self.drift_confidence):
            raise ValueError("deterministic aggregation")
        return self
