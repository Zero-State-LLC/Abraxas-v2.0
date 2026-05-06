from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class OverlayReadinessDiagnosticPacket(BaseModel):
    schema_version: Literal["OverlayReadinessDiagnosticPacket.v1"] = "OverlayReadinessDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal["readiness_score_out_of_bounds","threshold_order_invalid","unresolved_critical_diagnostics","replay_verification_failed","rollback_not_ready","authority_violation","auto_approval_attempted"]
    severity: Literal["info","warning","critical"]
    diagnostic_message: str
    deterministic_diagnostic_hash: str
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(t:str,s:str,m:str)->str:
        return hashlib.sha256(f"{t}|{s}|{m}".encode()).hexdigest()
