from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field
from core.governance.authority import Authority

class ProposalSandboxGovernancePacket(BaseModel):
    schema_version: Literal["ProposalSandboxGovernancePacket.v1"] = "ProposalSandboxGovernancePacket.v1"
    governance_id: str
    route_hash: str
    governance_constraints: list[str] = Field(default_factory=list)
    governance_restrictions: list[str] = Field(default_factory=list)
    operator_review_required: bool = True
    deterministic_governance_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, governance_constraints: list[str], governance_restrictions: list[str], operator_review_required: bool) -> str:
        return hashlib.sha256(f"{route_hash}|{'/'.join(sorted(governance_constraints))}|{'/'.join(sorted(governance_restrictions))}|{operator_review_required}".encode()).hexdigest()
