from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.governance.authority import Authority


class OperatorCanaryReviewPacket(BaseModel):
    schema_version: Literal["OperatorCanaryReviewPacket.v1"] = "OperatorCanaryReviewPacket.v1"
    review_id: str
    overlay_hash: str
    calibration_score: float
    replay_failures: int
    rollback_readiness: bool
    pending_actions: list[str]
    authority: Authority = Authority()
    status: Literal["pending", "approved", "rejected", "not_computable"]
