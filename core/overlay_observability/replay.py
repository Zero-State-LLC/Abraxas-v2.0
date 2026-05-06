from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority

class OverlayObservabilityReplayPacket(BaseModel):
    schema_version: Literal['OverlayObservabilityReplayPacket.v1']='OverlayObservabilityReplayPacket.v1'
    replay_id:str
    source_fusion_hash:str
    replay_fusion_hash:str
    deterministic_match:bool
    mismatched_packets:list[str]
    authority: Authority=Authority()
    status: Literal['passed','failed','not_computable']
