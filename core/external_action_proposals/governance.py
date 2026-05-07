from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator


class ProposalGovernancePacket(BaseModel):
    schema_version: Literal["ProposalGovernancePacket.v1"] = "ProposalGovernancePacket.v1"
    proposal_hash: str
    governance_restricted: bool
    authority_locked: bool
    deterministic_governance_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, governance_restricted: bool, authority_locked: bool) -> str:
        return hashlib.sha256(f"{proposal_hash}|{governance_restricted}|{authority_locked}".encode()).hexdigest()

    @model_validator(mode="after")
    def validate_packet(self) -> "ProposalGovernancePacket":
        if self.deterministic_governance_hash != self.compute_hash(self.proposal_hash, self.governance_restricted, self.authority_locked):
            raise ValueError("governance hash mismatch")
        return self
