from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel


class OverlayResolutionDiagnosticPacket(BaseModel):
    schema_version: Literal["OverlayResolutionDiagnosticPacket.v1"] = "OverlayResolutionDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal["unresolved_critical_event", "replay_verification_failed", "authority_violation", "rollback_not_ready", "invalid_lineage", "unresolved_diagnostic"]
    severity: Literal["info", "warning", "critical"]
    diagnostic_message: str
    deterministic_diagnostic_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(t: str, s: str, m: str) -> str:
        return hashlib.sha256(f"{t}|{s}|{m}".encode()).hexdigest()
