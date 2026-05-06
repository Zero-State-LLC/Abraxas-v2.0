from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority
class OperatorCanaryScheduleReviewPacket(BaseModel):
    schema_version: Literal['OperatorCanaryScheduleReviewPacket.v1']='OperatorCanaryScheduleReviewPacket.v1'
    review_id:str
    schedule_hash:str
    eligibility_status: bool
    blocked_reasons:list[str]
    replay_failures:int
    pending_actions:list[str]
    authority: Authority=Authority()
    status: Literal['pending','approved','rejected','not_computable']
