from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator


class ProposalReadinessPacket(BaseModel):
    schema_version: Literal["ProposalReadinessPacket.v1"] = "ProposalReadinessPacket.v1"
    proposal_hash: str
    readiness_posture: float
    deterministic_readiness_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, readiness_posture: float) -> str:
        return hashlib.sha256(f"{proposal_hash}|{readiness_posture:.6f}".encode()).hexdigest()

    @model_validator(mode="after")
    def validate_packet(self) -> "ProposalReadinessPacket":
        if not 0.0 <= self.readiness_posture <= 1.0:
            raise ValueError("readiness posture out of bounds")
        if self.deterministic_readiness_hash != self.compute_hash(self.proposal_hash, self.readiness_posture):
            raise ValueError("readiness hash mismatch")
        return self
