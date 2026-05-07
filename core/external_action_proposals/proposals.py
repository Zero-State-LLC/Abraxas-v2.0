from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority

FORBIDDEN_STATUSES = {
    "executed",
    "activated",
    "deployed",
    "live",
    "auto_approved",
    "auto_executed",
    "production_ready",
}


class ExternalActionProposalPacket(BaseModel):
    schema_version: Literal["ExternalActionProposalPacket.v1"] = (
        "ExternalActionProposalPacket.v1"
    )
    proposal_id: str
    proposal_status: str
    proposed_action: str
    proposal_reason: str
    deterministic_proposal_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_status: str, proposed_action: str, proposal_reason: str) -> str:
        value = f"{proposal_status}|{proposed_action}|{proposal_reason}"
        return hashlib.sha256(value.encode()).hexdigest()

    @model_validator(mode="after")
    def validate_packet(self) -> "ExternalActionProposalPacket":
        self.authority.assert_locked()
        if self.proposal_status in FORBIDDEN_STATUSES:
            raise ValueError("forbidden proposal_status")
        expected = self.compute_hash(
            self.proposal_status,
            self.proposed_action,
            self.proposal_reason,
        )
        if self.deterministic_proposal_hash != expected:
            raise ValueError("proposal hash mismatch")
        return self
