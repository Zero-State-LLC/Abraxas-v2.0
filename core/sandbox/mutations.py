from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SandboxMutationProposal(BaseModel):
    schema_version: Literal["SandboxMutationProposal.v1"] = "SandboxMutationProposal.v1"
    proposal_id: str
    branch_hash: str
    mutation_type: Literal[
        "scheduler_adjustment",
        "topology_adjustment",
        "stabilization_adjustment",
        "replay_policy_adjustment",
        "observability_adjustment",
    ]
    mutation_payload_hash: str
    deterministic_mutation_hash: str
    operator_review_required: bool = True
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(branch_hash: str, mutation_type: str, mutation_payload_hash: str) -> str:
        return hashlib.sha256(f"{branch_hash}|{mutation_type}|{mutation_payload_hash}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "SandboxMutationProposal":
        self.authority.assert_locked()
        if not self.operator_review_required:
            raise ValueError("operator review required always")
        if self.deterministic_mutation_hash != self.compute_hash(self.branch_hash, self.mutation_type, self.mutation_payload_hash):
            raise ValueError("deterministic mutation hash mismatch")
        return self
