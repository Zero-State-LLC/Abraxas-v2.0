from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator


DIAGNOSTIC_TYPES = (
    "forbidden_decision_detected",
    "auto_approval_attempt",
    "replay_mismatch",
    "authority_violation",
    "unresolved_critical_firewall_diagnostic",
    "unresolved_containment_restriction",
    "unresolved_governance_violation",
    "continuity_break",
    "lineage_cycle",
)


class OperatorQueueDiagnosticPacket(BaseModel):
    schema_version: Literal["OperatorQueueDiagnosticPacket.v1"] = "OperatorQueueDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal[
        "forbidden_decision_detected", "auto_approval_attempt", "replay_mismatch", "authority_violation", "unresolved_critical_firewall_diagnostic", "unresolved_containment_restriction", "unresolved_governance_violation", "continuity_break", "lineage_cycle"
    ]
    severity: Literal["critical", "warning"]
    message: str
    resolved: bool = False
    deterministic_diagnostic_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(diagnostic_type: str, severity: str, message: str, resolved: bool) -> str:
        return hashlib.sha256(f"{diagnostic_type}|{severity}|{message}|{resolved}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        if self.deterministic_diagnostic_hash != self.compute_hash(self.diagnostic_type, self.severity, self.message, self.resolved):
            raise ValueError("diagnostic hash mismatch")
        return self
