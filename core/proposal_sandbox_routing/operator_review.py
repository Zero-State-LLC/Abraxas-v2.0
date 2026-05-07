from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel
from core.governance.authority import Authority

class ProposalSandboxOperatorReviewPacket(BaseModel):
    schema_version: Literal["ProposalSandboxOperatorReviewPacket.v1"] = "ProposalSandboxOperatorReviewPacket.v1"
    review_id: str
    route_hash: str
    route_count: int
    blocked_routes: int
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, route_count: int, blocked_routes: int, unresolved_diagnostics: int) -> str:
        return hashlib.sha256(f"{route_hash}|{route_count}|{blocked_routes}|{unresolved_diagnostics}".encode()).hexdigest()
