from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator


class ReviewContinuityDiagnosticPacket(BaseModel):
    schema_version: Literal["ReviewContinuityDiagnosticPacket.v1"] = "ReviewContinuityDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal["replay_mismatch", "lineage_cycle", "authority_violation", "missing_review_chain", "orphaned_rationale", "orphaned_deferral", "orphaned_denial", "unresolved_firewall_violation", "unresolved_governance_violation", "continuity_break", "forbidden_status_detected"]
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
