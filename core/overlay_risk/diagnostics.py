from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel


class OverlayRiskDiagnosticPacket(BaseModel):
    schema_version: Literal["OverlayRiskDiagnosticPacket.v1"] = "OverlayRiskDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal[
        "escalation_pressure_high",
        "rollback_exposure_high",
        "propagation_chain_risk",
        "confidence_cliff_detected",
        "governance_saturation_high",
        "replay_instability",
        "authority_violation",
    ]
    severity: Literal["info", "warning", "critical"]
    diagnostic_message: str
    deterministic_diagnostic_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(diagnostic_type: str, severity: str, diagnostic_message: str) -> str:
        return hashlib.sha256(f"{diagnostic_type}|{severity}|{diagnostic_message}".encode()).hexdigest()
