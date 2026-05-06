from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryPolicyPacket(BaseModel):
    schema_version: Literal["CanaryPolicyPacket.v1"] = "CanaryPolicyPacket.v1"
    policy_id: str
    policy_scope: Literal["shadow_only", "replay_only", "diagnostic_only"]
    max_overlay_weight: float
    min_stability_score: float
    max_replay_failures: int
    require_rollback_ready: bool = True
    allow_critical_diagnostics: bool = False
    deterministic_policy_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(scope: str, weight: float, stability: float, replay_max: int, require_ready: bool, allow_critical: bool) -> str:
        return hashlib.sha256(f"{scope}|{weight:.6f}|{stability:.6f}|{replay_max}|{require_ready}|{allow_critical}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "CanaryPolicyPacket":
        self.authority.assert_locked()
        if not 0 <= self.max_overlay_weight <= 1:
            raise ValueError("bounds")
        if not 0 <= self.min_stability_score <= 1:
            raise ValueError("bounds")
        if self.deterministic_policy_hash != self.compute_hash(
            self.policy_scope,
            self.max_overlay_weight,
            self.min_stability_score,
            self.max_replay_failures,
            self.require_rollback_ready,
            self.allow_critical_diagnostics,
        ):
            raise ValueError("hash")
        return self
