from __future__ import annotations
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority

class OperatorOverlayReviewPacket(BaseModel):
    schema_version: Literal['OperatorOverlayReviewPacket.v1']='OperatorOverlayReviewPacket.v1'
    review_id:str
    fusion_hash:str
    diagnostic_count:int
    critical_diagnostics:int
    stability_state: str
    pending_actions:list[str]
    authority: Authority=Authority()
    status: Literal['pending','approved','rejected','not_computable']
