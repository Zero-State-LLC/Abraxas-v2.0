from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority


class OverlayContainmentPolicyPacket(BaseModel):
    schema_version: Literal["OverlayContainmentPolicyPacket.v1"] = "OverlayContainmentPolicyPacket.v1"
    policy_id: str
    policy_scope: Literal["advisory_only", "replay_only", "projection_only"]
    max_aggregate_risk: float = Field(ge=0, le=1)
    max_propagation_depth: float = Field(ge=0, le=1)
    max_coupling_score: float = Field(ge=0, le=1)
    require_rollback_ready: bool
    block_critical_diagnostics: bool
    deterministic_policy_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(scope: str, aggregate: float, propagation: float, coupling: float, require_rollback_ready: bool, block_critical_diagnostics: bool) -> str:
        payload = f"{scope}|{aggregate:.8f}|{propagation:.8f}|{coupling:.8f}|{int(require_rollback_ready)}|{int(block_critical_diagnostics)}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayContainmentPolicyPacket":
        self.authority.assert_locked()
        if "production" in self.policy_scope:
            raise ValueError("production scope forbidden")
        if self.deterministic_policy_hash != self.compute_hash(self.policy_scope, self.max_aggregate_risk, self.max_propagation_depth, self.max_coupling_score, self.require_rollback_ready, self.block_critical_diagnostics):
            raise ValueError("policy hash")
        return self
