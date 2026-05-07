from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalSandboxContinuityPacket(BaseModel):
    schema_version: Literal["ProposalSandboxContinuityPacket.v1"] = "ProposalSandboxContinuityPacket.v1"
    route_hash: str
    prior_route_hashes: list[str] = Field(default_factory=list)
    append_only: bool
    deterministic_continuity_hash: str
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, prior_route_hashes: list[str], append_only: bool) -> str:
        return hashlib.sha256(f"{route_hash}|{'/'.join(sorted(prior_route_hashes))}|{append_only}".encode()).hexdigest()
