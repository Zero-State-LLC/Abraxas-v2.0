from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ProposalConstraintPacket(BaseModel):
    schema_version: Literal["ProposalConstraintPacket.v1"] = "ProposalConstraintPacket.v1"
    proposal_hash: str
    blocked_actions: list[str] = Field(default_factory=list)
    deterministic_constraint_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, blocked_actions: list[str]) -> str:
        return hashlib.sha256(f"{proposal_hash}|{'/'.join(sorted(blocked_actions))}".encode()).hexdigest()

    @model_validator(mode="after")
    def validate_packet(self) -> "ProposalConstraintPacket":
        expected = self.compute_hash(self.proposal_hash, self.blocked_actions)
        if self.deterministic_constraint_hash != expected:
            raise ValueError("constraint hash mismatch")
        return self
