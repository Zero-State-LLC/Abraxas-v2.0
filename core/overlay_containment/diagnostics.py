from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class OverlayContainmentDiagnosticPacket(BaseModel):
    schema_version: Literal["OverlayContainmentDiagnosticPacket.v1"] = "OverlayContainmentDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal["containment_threshold_exceeded", "rollback_unavailable", "critical_diagnostic_present", "propagation_depth_exceeded", "coupling_threshold_exceeded", "authority_violation"]
    severity: Literal["info", "warning", "critical"]
    diagnostic_message: str
    deterministic_diagnostic_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(diagnostic_type: str, severity: str, diagnostic_message: str) -> str:
        return hashlib.sha256(f"{diagnostic_type}|{severity}|{diagnostic_message}".encode()).hexdigest()
