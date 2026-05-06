from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryPromotionEligibilityPacket(BaseModel):
    schema_version: Literal["CanaryPromotionEligibilityPacket.v1"] = "CanaryPromotionEligibilityPacket.v1"
    eligibility_id: str
    candidate_hash: str
    stability_score: float
    replay_failures: int
    critical_diagnostics: int
    rollback_ready: bool
    eligible_for_review: bool
    denial_reasons: list[str]
    deterministic_eligibility_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(
        candidate_hash: str,
        stability_score: float,
        replay_failures: int,
        critical_diagnostics: int,
        rollback_ready: bool,
        eligible_for_review: bool,
        denial_reasons: list[str],
    ) -> str:
        raw = (
            f"{candidate_hash}|{stability_score:.6f}|{replay_failures}|{critical_diagnostics}|"
            f"{rollback_ready}|{eligible_for_review}|{'|'.join(denial_reasons)}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryPromotionEligibilityPacket":
        self.authority.assert_locked()
        if self.deterministic_eligibility_hash != self.compute_hash(
            self.candidate_hash,
            self.stability_score,
            self.replay_failures,
            self.critical_diagnostics,
            self.rollback_ready,
            self.eligible_for_review,
            self.denial_reasons,
        ):
            raise ValueError("hash")
        return self
