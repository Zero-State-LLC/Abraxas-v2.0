from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority
from core.proposal_sandbox_routing.routes import FORBIDDEN_ROUTE_TYPES

ALLOWED_LANE_TYPES = {"simulation_lane","advisory_lane","governance_lane","containment_lane","rollback_lane","continuity_lane"}
FORBIDDEN_LANE_TYPES = {"production_lane","deployment_lane","execution_lane","live_lane"}

class ProposalSandboxLanePacket(BaseModel):
    schema_version: Literal["ProposalSandboxLanePacket.v1"] = "ProposalSandboxLanePacket.v1"
    lane_id: str
    lane_type: str
    lane_constraints: list[str] = Field(default_factory=list)
    allowed_route_types: list[str] = Field(default_factory=list)
    forbidden_route_types: list[str] = Field(default_factory=list)
    deterministic_lane_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(lane_type: str, lane_constraints: list[str], allowed_route_types: list[str], forbidden_route_types: list[str]) -> str:
        return hashlib.sha256(f"{lane_type}|{'/'.join(sorted(lane_constraints))}|{'/'.join(sorted(allowed_route_types))}|{'/'.join(sorted(forbidden_route_types))}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "ProposalSandboxLanePacket":
        self.authority.assert_locked()
        if self.lane_type in FORBIDDEN_LANE_TYPES or self.lane_type not in ALLOWED_LANE_TYPES:
            raise ValueError("invalid lane_type")
        overlap = set(self.allowed_route_types).intersection(set(self.forbidden_route_types))
        if overlap:
            raise ValueError("allowed/forbidden route types overlap")
        if set(self.allowed_route_types).intersection(FORBIDDEN_ROUTE_TYPES):
            raise ValueError("forbidden route type allowed")
        if self.deterministic_lane_hash != self.compute_hash(self.lane_type, self.lane_constraints, self.allowed_route_types, self.forbidden_route_types):
            raise ValueError("lane hash mismatch")
        return self
