from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class OverlayTelemetryPacket(BaseModel):
    schema_version: Literal["OverlayTelemetryPacket.v1"] = "OverlayTelemetryPacket.v1"
    telemetry_id: str
    overlay_hash: str
    replay_match_count: int
    replay_failure_count: int
    rollback_count: int
    blocked_route_count: int
    pending_review_count: int
    stability_score: float
    deterministic_telemetry_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]
    @staticmethod
    def compute_hash(overlay_hash:str,a:int,b:int,c:int,d:int,e:int,s:float)->str:
        return hashlib.sha256(f"{overlay_hash}|{a}|{b}|{c}|{d}|{e}|{s:.6f}".encode()).hexdigest()
    @model_validator(mode='after')
    def _v(self)->"OverlayTelemetryPacket":
        self.authority.assert_locked()
        if min(self.replay_match_count,self.replay_failure_count,self.rollback_count,self.blocked_route_count,self.pending_review_count)<0:
            raise ValueError('counts nonnegative')
        if not 0<=self.stability_score<=1:
            raise ValueError('stability_score range [0,1]')
        if self.deterministic_telemetry_hash!=self.compute_hash(self.overlay_hash,self.replay_match_count,self.replay_failure_count,self.rollback_count,self.blocked_route_count,self.pending_review_count,self.stability_score):
            raise ValueError('deterministic hash')
        return self
