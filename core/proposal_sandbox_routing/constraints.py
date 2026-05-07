from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority

FORBIDDEN_RESTRICTED_ACTIONS = {"execute","activate","deploy","route_production","mutate_forecast","mutate_weight","mutate_canon","auto_apply"}

class ProposalSandboxConstraintPacket(BaseModel):
    schema_version: Literal["ProposalSandboxConstraintPacket.v1"] = "ProposalSandboxConstraintPacket.v1"
    constraint_id: str
    route_hash: str
    hard_constraints: list[str] = Field(default_factory=list)
    soft_constraints: list[str] = Field(default_factory=list)
    restricted_actions: list[str]
    deterministic_constraint_hash: str
    authority: Authority = Authority()
    status: Literal["passed","failed","not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, hard_constraints: list[str], soft_constraints: list[str], restricted_actions: list[str]) -> str:
        value = f"{route_hash}|{'/'.join(sorted(hard_constraints))}|{'/'.join(sorted(soft_constraints))}|{'/'.join(sorted(restricted_actions))}"
        return hashlib.sha256(value.encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "ProposalSandboxConstraintPacket":
        self.authority.assert_locked()
        if not self.restricted_actions:
            raise ValueError("restricted_actions required")
        if not FORBIDDEN_RESTRICTED_ACTIONS.issubset(set(self.restricted_actions)):
            raise ValueError("restricted actions incomplete")
        if self.deterministic_constraint_hash != self.compute_hash(self.route_hash, self.hard_constraints, self.soft_constraints, self.restricted_actions):
            raise ValueError("constraint hash mismatch")
        return self
