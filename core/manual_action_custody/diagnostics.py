from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel

class ManualActionCustodyDiagnosticPacket(BaseModel):
    schema_version: Literal["ManualActionCustodyDiagnosticPacket.v1"]="ManualActionCustodyDiagnosticPacket.v1"
    diagnostic_id:str
    diagnostic_type: Literal["forbidden_custody_status","forbidden_escalation_type","replay_mismatch","missing_receipt","missing_handoff","missing_acknowledgement","authority_violation","auto_execution_attempted","custody_lineage_cycle","custody_continuity_break"]
    severity: Literal["info","warning","critical"]
    diagnostic_message:str
    resolved: bool=False
    deterministic_diagnostic_hash:str
    status: Literal["passed","failed","not_computable"]
    @staticmethod
    def compute_hash(a:str,b:str,c:str)->str:
        return hashlib.sha256(f"{a}|{b}|{c}".encode()).hexdigest()
