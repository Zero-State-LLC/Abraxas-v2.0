from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

FORBIDDEN_ACTIONS = {"approve", "execute", "deploy", "route_production", "mutate_canon", "mutate_forecast", "mutate_weight", "auto_apply"}

class ProposalDecisionRestrictionPacket(BaseModel):
    schema_version: Literal["ProposalDecisionRestrictionPacket.v1"] = "ProposalDecisionRestrictionPacket.v1"
    bridge_hash: str
    governance_restricted: bool
    restricted_actions: list[str] = Field(default_factory=list)
    deterministic_restriction_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(bridge_hash: str, governance_restricted: bool, restricted_actions: list[str]) -> str:
        return hashlib.sha256(f"{bridge_hash}|{governance_restricted}|{'/'.join(sorted(restricted_actions))}".encode()).hexdigest()
