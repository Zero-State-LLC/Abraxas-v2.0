from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority
class CanaryScheduleReplayPacket(BaseModel):
    schema_version: Literal['CanaryScheduleReplayPacket.v1']='CanaryScheduleReplayPacket.v1'
    replay_id:str
    schedule_hash:str
    deterministic_match:bool
    replayed_windows:list[str]
    mismatched_windows:list[str]
    authority: Authority=Authority()
    status: Literal['passed','failed','not_computable']
