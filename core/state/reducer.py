from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority
from core.state.transitions import StateTransitionPacket


class DeterministicStateReducer(BaseModel):
    schema_version: Literal["DeterministicStateReducer.v1"] = "DeterministicStateReducer.v1"
    reducer_id: str
    input_state_hash: str
    output_state_hash: str
    applied_transition_hashes: list[str]
    deterministic_reduction_hash: str
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "DeterministicStateReducer":
        self.authority.assert_locked()
        expected = hashlib.sha256(
            f"{self.input_state_hash}|{self.output_state_hash}|{'|'.join(self.applied_transition_hashes)}".encode()
        ).hexdigest()
        if self.deterministic_reduction_hash != expected:
            raise ValueError("deterministic reduction hash mismatch")
        return self


def reduce_state(previous_state: str, transition_packets: list[StateTransitionPacket]) -> DeterministicStateReducer:
    ordered = sorted(transition_packets, key=lambda x: x.deterministic_transition_hash)
    applied = [p.deterministic_transition_hash for p in ordered]
    output = hashlib.sha256(f"{previous_state}|{'|'.join(applied)}".encode()).hexdigest()
    drh = hashlib.sha256(f"{previous_state}|{output}|{'|'.join(applied)}".encode()).hexdigest()
    return DeterministicStateReducer(
        reducer_id=f"reducer:{output[:12]}",
        input_state_hash=previous_state,
        output_state_hash=output,
        applied_transition_hashes=applied,
        deterministic_reduction_hash=drh,
        status="reduced",
    )
