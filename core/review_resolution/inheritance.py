from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

class ReviewResolutionInheritancePacket(BaseModel):
    schema_version: Literal["ReviewResolutionInheritancePacket.v1"] = "ReviewResolutionInheritancePacket.v1"
    inheritance_id: str
    continuity_hash: str
    inherited_denials: list[str]
    inherited_deferrals: list[str]
    inherited_rationale_hashes: list[str]
    inherited_blockers: list[str]
    deterministic_inheritance_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(continuity_hash: str, inherited_denials: list[str], inherited_deferrals: list[str], inherited_rationale_hashes: list[str], inherited_blockers: list[str]) -> str:
        return hashlib.sha256(f"{continuity_hash}|{'|'.join(sorted(inherited_denials))}|{'|'.join(sorted(inherited_deferrals))}|{'|'.join(sorted(inherited_rationale_hashes))}|{'|'.join(sorted(inherited_blockers))}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> 'ReviewResolutionInheritancePacket':
        self.authority.assert_locked()
        if self.deterministic_inheritance_hash != self.compute_hash(self.continuity_hash, self.inherited_denials, self.inherited_deferrals, self.inherited_rationale_hashes, self.inherited_blockers):
            raise ValueError('inheritance hash')
        return self
