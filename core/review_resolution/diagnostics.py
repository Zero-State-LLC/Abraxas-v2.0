from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class ReviewResolutionDiagnosticPacket(BaseModel):
    schema_version: Literal["ReviewResolutionDiagnosticPacket.v1"] = "ReviewResolutionDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal["replay_mismatch", "lineage_cycle", "authority_violation", "forbidden_posture_detected", "forbidden_outcome_detected", "unresolved_critical_blocker", "missing_rationale", "continuity_break"]
    severity: Literal["info", "warning", "critical"]
    diagnostic_message: str
    resolved: bool = False
    deterministic_diagnostic_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(t: str, s: str, m: str) -> str:
        return hashlib.sha256(f"{t}|{s}|{m}".encode()).hexdigest()
