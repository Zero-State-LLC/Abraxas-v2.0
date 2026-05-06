from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority


class OverlayPropagationRiskPacket(BaseModel):
    schema_version: Literal["OverlayPropagationRiskPacket.v1"] = "OverlayPropagationRiskPacket.v1"
    propagation_id: str
    overlay_hashes: list[str]
    shared_dependencies: int = Field(ge=0)
    governance_coupling_score: float = Field(ge=0, le=1)
    replay_overlap_score: float = Field(ge=0, le=1)
    correlated_rollback_exposure: float = Field(ge=0, le=1)
    propagation_depth: int = Field(ge=1)
    cycles_detected: bool
    autonomous_escalation_detected: bool = False
    deterministic_propagation_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hashes: list[str], shared_dependencies: int, governance_coupling_score: float, replay_overlap_score: float, correlated_rollback_exposure: float, propagation_depth: int, cycles_detected: bool, autonomous_escalation_detected: bool) -> str:
        return hashlib.sha256(f"{sorted(overlay_hashes)}|{shared_dependencies}|{governance_coupling_score:.8f}|{replay_overlap_score:.8f}|{correlated_rollback_exposure:.8f}|{propagation_depth}|{cycles_detected}|{autonomous_escalation_detected}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "OverlayPropagationRiskPacket":
        self.authority.assert_locked()
        if self.deterministic_propagation_hash != self.compute_hash(self.overlay_hashes, self.shared_dependencies, self.governance_coupling_score, self.replay_overlap_score, self.correlated_rollback_exposure, self.propagation_depth, self.cycles_detected, self.autonomous_escalation_detected):
            raise ValueError('propagation hash')
        return self
