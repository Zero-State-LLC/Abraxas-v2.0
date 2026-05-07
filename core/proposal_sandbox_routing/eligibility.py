from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field
from core.governance.authority import Authority

class ProposalSandboxEligibilityPacket(BaseModel):
    schema_version: Literal["ProposalSandboxEligibilityPacket.v1"] = "ProposalSandboxEligibilityPacket.v1"
    eligibility_id: str
    route_hash: str
    proposal_hash: str
    lane_hash: str
    eligible_for_sandbox: bool
    denial_reasons: list[str] = Field(default_factory=list)
    deterministic_eligibility_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, proposal_hash: str, lane_hash: str, eligible_for_sandbox: bool, denial_reasons: list[str]) -> str:
        return hashlib.sha256(f"{route_hash}|{proposal_hash}|{lane_hash}|{eligible_for_sandbox}|{'/'.join(sorted(denial_reasons))}".encode()).hexdigest()
