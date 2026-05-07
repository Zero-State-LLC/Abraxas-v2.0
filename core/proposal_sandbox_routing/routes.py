from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority

ALLOWED_ROUTE_TYPES = {"simulation","advisory_review","governance_review","containment_review","rollback_review","continuity_review"}
FORBIDDEN_ROUTE_TYPES = {"production","deployment","execution","activation","live_routing"}
ALLOWED_ROUTE_STATUSES = {"route_proposed","route_deferred","route_blocked","route_review_required","not_computable"}
FORBIDDEN_ROUTE_STATUSES = {"routed_live","executing","deployed","activated","production_ready"}

class ProposalSandboxRoutePacket(BaseModel):
    schema_version: Literal["ProposalSandboxRoutePacket.v1"] = "ProposalSandboxRoutePacket.v1"
    route_id: str
    proposal_hash: str
    route_type: str
    route_scope: Literal["sandbox_only", "advisory_only"] = "sandbox_only"
    sandbox_lane_hash: str
    route_constraints: list[str] = Field(default_factory=list)
    route_status: str
    deterministic_route_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, route_type: str, route_scope: str, sandbox_lane_hash: str, route_constraints: list[str], route_status: str) -> str:
        v = f"{proposal_hash}|{route_type}|{route_scope}|{sandbox_lane_hash}|{'/'.join(sorted(route_constraints))}|{route_status}"
        return hashlib.sha256(v.encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "ProposalSandboxRoutePacket":
        self.authority.assert_locked()
        if self.route_type in FORBIDDEN_ROUTE_TYPES or self.route_type not in ALLOWED_ROUTE_TYPES:
            raise ValueError("invalid route_type")
        if self.route_status in FORBIDDEN_ROUTE_STATUSES or self.route_status not in ALLOWED_ROUTE_STATUSES:
            raise ValueError("invalid route_status")
        if self.deterministic_route_hash != self.compute_hash(self.proposal_hash, self.route_type, self.route_scope, self.sandbox_lane_hash, self.route_constraints, self.route_status):
            raise ValueError("route hash mismatch")
        return self
