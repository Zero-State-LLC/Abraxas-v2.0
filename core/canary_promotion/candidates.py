from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryPromotionCandidatePacket(BaseModel):
    schema_version: Literal["CanaryPromotionCandidatePacket.v1"] = "CanaryPromotionCandidatePacket.v1"
    candidate_id: str
    overlay_hash: str
    scheduler_hash: str
    observability_hash: str
    stability_score: float
    replay_consistency: float
    rollback_ready: bool
    bounded_influence: bool
    candidate_scope: Literal["review_only", "replay_only", "diagnostic_only"]
    deterministic_candidate_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(
        overlay_hash: str,
        scheduler_hash: str,
        observability_hash: str,
        stability_score: float,
        replay_consistency: float,
        rollback_ready: bool,
        bounded_influence: bool,
        candidate_scope: str,
    ) -> str:
        raw = (
            f"{overlay_hash}|{scheduler_hash}|{observability_hash}|{stability_score:.6f}|"
            f"{replay_consistency:.6f}|{rollback_ready}|{bounded_influence}|{candidate_scope}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryPromotionCandidatePacket":
        self.authority.assert_locked()
        if self.replay_consistency <= 0.0 or not self.rollback_ready or not self.bounded_influence:
            raise ValueError("requirements")
        if self.deterministic_candidate_hash != self.compute_hash(
            self.overlay_hash,
            self.scheduler_hash,
            self.observability_hash,
            self.stability_score,
            self.replay_consistency,
            self.rollback_ready,
            self.bounded_influence,
            self.candidate_scope,
        ):
            raise ValueError("hash")
        return self
