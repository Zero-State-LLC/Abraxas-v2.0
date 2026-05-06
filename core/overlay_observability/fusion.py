from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class OverlayObservabilityFusionPacket(BaseModel):
    schema_version: Literal["OverlayObservabilityFusionPacket.v1"] = "OverlayObservabilityFusionPacket.v1"
    fusion_id: str
    canary_hash: str
    drift_hash: str
    forecast_hash: str
    brier_hash: str
    fusion_scope: Literal["diagnostic_only", "replay_only", "projection_only"]
    fused_overlay_hash: str
    deterministic_fusion_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(canary_hash: str, drift_hash: str, forecast_hash: str, brier_hash: str, fusion_scope: str) -> str:
        return hashlib.sha256(f"{canary_hash}|{drift_hash}|{forecast_hash}|{brier_hash}|{fusion_scope}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "OverlayObservabilityFusionPacket":
        self.authority.assert_locked()
        if self.deterministic_fusion_hash != self.compute_hash(self.canary_hash, self.drift_hash, self.forecast_hash, self.brier_hash, self.fusion_scope):
            raise ValueError("deterministic hashing")
        return self
