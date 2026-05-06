from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority


class OverlayRiskEnvelopePacket(BaseModel):
    schema_version: Literal["OverlayRiskEnvelopePacket.v1"] = "OverlayRiskEnvelopePacket.v1"
    risk_envelope_id: str
    overlay_hash: str
    governance_scope: Literal["projection_only", "audit_only", "replay_only"]
    escalation_pressure_score: float = Field(ge=0, le=1)
    rollback_exposure_score: float = Field(ge=0, le=1)
    propagation_risk_score: float = Field(ge=0, le=1)
    saturation_score: float = Field(ge=0, le=1)
    cliff_risk_score: float = Field(ge=0, le=1)
    aggregate_risk_score: float = Field(ge=0, le=1)
    deterministic_risk_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, governance_scope: str, escalation: float, rollback: float, propagation: float, saturation: float, cliff: float, aggregate: float) -> str:
        return hashlib.sha256(f"{overlay_hash}|{governance_scope}|{escalation:.8f}|{rollback:.8f}|{propagation:.8f}|{saturation:.8f}|{cliff:.8f}|{aggregate:.8f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayRiskEnvelopePacket":
        self.authority.assert_locked()
        if self.deterministic_risk_hash != self.compute_hash(self.overlay_hash, self.governance_scope, self.escalation_pressure_score, self.rollback_exposure_score, self.propagation_risk_score, self.saturation_score, self.cliff_risk_score, self.aggregate_risk_score):
            raise ValueError("risk hash")
        return self
