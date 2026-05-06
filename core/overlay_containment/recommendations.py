from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OverlayContainmentRecommendationPacket(BaseModel):
    schema_version: Literal["OverlayContainmentRecommendationPacket.v1"] = "OverlayContainmentRecommendationPacket.v1"
    recommendation_id: str
    policy_hash: str
    overlay_hash: str
    recommendation_type: Literal["hold_observation", "require_operator_review", "deny_promotion_review", "require_rollback_readiness", "reduce_overlay_scope", "flag_authority_violation"]
    recommendation_reason: str
    advisory_severity: Literal["info", "warning", "critical"]
    deterministic_recommendation_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(policy_hash: str, overlay_hash: str, recommendation_type: str, recommendation_reason: str, advisory_severity: str) -> str:
        return hashlib.sha256(f"{policy_hash}|{overlay_hash}|{recommendation_type}|{recommendation_reason}|{advisory_severity}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayContainmentRecommendationPacket":
        self.authority.assert_locked()
        if any(word in self.recommendation_reason.lower() for word in ["enforce", "execute", "disable", "route traffic"]):
            raise ValueError("advisory only")
        if self.deterministic_recommendation_hash != self.compute_hash(self.policy_hash, self.overlay_hash, self.recommendation_type, self.recommendation_reason, self.advisory_severity):
            raise ValueError("recommendation hash")
        return self
