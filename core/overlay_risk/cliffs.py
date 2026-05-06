from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class OverlayConfidenceCliffPacket(BaseModel):
    schema_version: Literal["OverlayConfidenceCliffPacket.v1"] = "OverlayConfidenceCliffPacket.v1"
    cliff_id: str
    confidence_drop_rate: float = Field(ge=0, le=1)
    replay_instability_score: float = Field(ge=0, le=1)
    governance_inconsistency_score: float = Field(ge=0, le=1)
    continuity_drop_score: float = Field(ge=0, le=1)
    cliff_risk_score: float = Field(ge=0, le=1)
    deterministic_cliff_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(confidence_drop_rate: float, replay_instability_score: float, governance_inconsistency_score: float, continuity_drop_score: float, cliff_risk_score: float) -> str:
        return hashlib.sha256(f"{confidence_drop_rate:.8f}|{replay_instability_score:.8f}|{governance_inconsistency_score:.8f}|{continuity_drop_score:.8f}|{cliff_risk_score:.8f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "OverlayConfidenceCliffPacket":
        if self.deterministic_cliff_hash != self.compute_hash(self.confidence_drop_rate, self.replay_instability_score, self.governance_inconsistency_score, self.continuity_drop_score, self.cliff_risk_score):
            raise ValueError('cliff hash')
        return self
