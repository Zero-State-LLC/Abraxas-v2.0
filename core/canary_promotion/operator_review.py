from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.governance.authority import Authority


class OperatorCanaryPromotionReviewPacket(BaseModel):
    schema_version: Literal["OperatorCanaryPromotionReviewPacket.v1"] = "OperatorCanaryPromotionReviewPacket.v1"
    review_id: str
    candidate_hash: str
    eligibility_status: bool
    denial_reasons: list[str]
    replay_failures: int
    critical_diagnostics: int
    pending_actions: list[str]
    authority: Authority = Authority()
    status: Literal["pending", "approved", "rejected", "not_computable"]
