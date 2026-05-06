from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class OverlayDiagnosticPacket(BaseModel):
    schema_version: Literal['OverlayDiagnosticPacket.v1']='OverlayDiagnosticPacket.v1'
    diagnostic_id:str
    overlay_hash:str
    diagnostic_type: Literal['replay_instability','rollback_frequency','route_blocking','calibration_decay','review_backlog','lineage_break','authority_violation']
    severity: Literal['info','warning','critical']
    diagnostic_message:str
    deterministic_diagnostic_hash:str
    authority: Authority=Authority()
    status: Literal['passed','failed','not_computable']
    @staticmethod
    def compute_hash(overlay_hash:str,dt:str,severity:str,msg:str)->str:
        return hashlib.sha256(f"{overlay_hash}|{dt}|{severity}|{msg}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self)->"OverlayDiagnosticPacket":
        self.authority.assert_locked()
        if self.deterministic_diagnostic_hash!=self.compute_hash(self.overlay_hash,self.diagnostic_type,self.severity,self.diagnostic_message):
            raise ValueError('deterministic hash')
        return self
