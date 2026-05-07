from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class ManualExecutionDiagnosticPacket(BaseModel):
    schema_version: Literal["ManualExecutionDiagnosticPacket.v1"] = "ManualExecutionDiagnosticPacket.v1"
    diagnostic_id: str
    diagnostic_type: Literal["forbidden_authorization_status","forbidden_envelope_status","forbidden_action_detected","missing_acknowledgement","rollback_not_ready","replay_mismatch","closure_not_ready","critical_blocker_unresolved","authority_violation","auto_execution_attempted"]
    severity: Literal["info","warning","critical"]
    diagnostic_message: str
    resolved: bool = False
    deterministic_diagnostic_hash: str
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:str)->str:
        return hashlib.sha256(f"{a}|{b}|{c}".encode()).hexdigest()
