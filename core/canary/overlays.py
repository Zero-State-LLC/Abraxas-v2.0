from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryOverlayPacket(BaseModel):
    schema_version: Literal["CanaryOverlayPacket.v1"] = "CanaryOverlayPacket.v1"
    overlay_id: str
    source_drift_hash: str
    source_forecast_hash: str
    overlay_scope: Literal["shadow_only", "replay_only", "simulation_only"]
    overlay_weight: float
    overlay_duration: int
    overlay_generation: int
    bounded_influence: bool
    deterministic_overlay_hash: str
    authority: Authority = Authority()
    status: Literal["pending", "active", "stabilized", "rolled_back", "rejected", "archived", "not_computable"]

    @staticmethod
    def compute_hash(overlay_id: str, source_drift_hash: str, source_forecast_hash: str, overlay_scope: str, overlay_weight: float, overlay_duration: int, overlay_generation: int, bounded_influence: bool) -> str:
        return hashlib.sha256(f"{overlay_id}|{source_drift_hash}|{source_forecast_hash}|{overlay_scope}|{overlay_weight:.6f}|{overlay_duration}|{overlay_generation}|{bounded_influence}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryOverlayPacket":
        self.authority.assert_locked()
        if not 0.0 <= self.overlay_weight <= 1.0:
            raise ValueError("overlay_weight bounded [0,1]")
        if not self.bounded_influence:
            raise ValueError("bounded_influence required")
        if self.deterministic_overlay_hash != self.compute_hash(self.overlay_id, self.source_drift_hash, self.source_forecast_hash, self.overlay_scope, self.overlay_weight, self.overlay_duration, self.overlay_generation, self.bounded_influence):
            raise ValueError("deterministic hashing")
        return self
