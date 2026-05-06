from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class ReviewRationaleInheritancePacket(BaseModel):
    schema_version: Literal["ReviewRationaleInheritancePacket.v1"] = "ReviewRationaleInheritancePacket.v1"
    inheritance_id: str
    parent_rationale_hash: str
    inherited_constraints: list[str]
    inherited_denials: list[str]
    inherited_deferrals: list[str]
    inherited_governance_flags: list[str]
    deterministic_inheritance_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(parent_rationale_hash: str, inherited_constraints: list[str], inherited_denials: list[str], inherited_deferrals: list[str], inherited_governance_flags: list[str]) -> str:
        return hashlib.sha256(f"{parent_rationale_hash}|{'|'.join(inherited_constraints)}|{'|'.join(inherited_denials)}|{'|'.join(inherited_deferrals)}|{'|'.join(inherited_governance_flags)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_inheritance_hash != self.compute_hash(self.parent_rationale_hash, self.inherited_constraints, self.inherited_denials, self.inherited_deferrals, self.inherited_governance_flags):
            raise ValueError("inheritance hash mismatch")
        return self
