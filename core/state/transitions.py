from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority

_ALLOWED = {
    "stabilization_update",
    "replay_update",
    "topology_update",
    "validation_update",
    "observability_update",
    "projection_update",
}


class StateTransitionPacket(BaseModel):
    schema_version: Literal["StateTransitionPacket.v1"] = "StateTransitionPacket.v1"
    transition_id: str
    source_state_hash: str
    target_state_hash: str
    triggering_execution_hash: str
    transition_type: str
    deterministic_transition_hash: str
    authority: Authority = Authority()
    operator_review_required: bool = True
    status: str = "pending"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(source: str, target: str, execution: str, ttype: str) -> str:
        return hashlib.sha256(f"{source}|{target}|{execution}|{ttype}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "StateTransitionPacket":
        self.authority.assert_locked()
        if self.transition_type not in _ALLOWED:
            raise ValueError("invalid transition_type")
        if self.source_state_hash == self.target_state_hash:
            raise ValueError("source != target required")
        expected = self.compute_hash(
            self.source_state_hash, self.target_state_hash, self.triggering_execution_hash, self.transition_type
        )
        if self.deterministic_transition_hash != expected:
            raise ValueError("deterministic transition hash mismatch")
        return self
