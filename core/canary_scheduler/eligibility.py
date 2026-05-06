from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryEligibilityPacket(BaseModel):
    schema_version: Literal["CanaryEligibilityPacket.v1"] = "CanaryEligibilityPacket.v1"
    eligibility_id: str
    overlay_hash: str
    policy_hash: str
    stability_score: float
    replay_failures: int
    rollback_ready: bool
    critical_diagnostics: int
    eligible: bool
    blocked_reasons: list[str]
    deterministic_eligibility_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, policy_hash: str, stability: float, replay_failures: int, rollback_ready: bool, critical_diagnostics: int, eligible: bool, blocked_reasons: list[str]) -> str:
        return hashlib.sha256(f"{overlay_hash}|{policy_hash}|{stability:.6f}|{replay_failures}|{rollback_ready}|{critical_diagnostics}|{eligible}|{'|'.join(blocked_reasons)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "CanaryEligibilityPacket":
        self.authority.assert_locked()
        if self.deterministic_eligibility_hash != self.compute_hash(
            self.overlay_hash,
            self.policy_hash,
            self.stability_score,
            self.replay_failures,
            self.rollback_ready,
            self.critical_diagnostics,
            self.eligible,
            self.blocked_reasons,
        ):
            raise ValueError("hash")
        return self
