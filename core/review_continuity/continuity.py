from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field, model_validator
from core.governance.authority import Authority


class ReviewContinuityPacket(BaseModel):
    schema_version: Literal["ReviewContinuityPacket.v1"] = "ReviewContinuityPacket.v1"
    continuity_id: str
    chain_hash: str
    continuity_score: float = Field(ge=0, le=1)
    continuity_integrity: bool
    unresolved_breaks: list[str]
    deterministic_continuity_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(chain_hash: str, continuity_score: float, continuity_integrity: bool, unresolved_breaks: list[str]) -> str:
        return hashlib.sha256(f"{chain_hash}|{continuity_score:.8f}|{continuity_integrity}|{'|'.join(unresolved_breaks)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.continuity_integrity != (len(self.unresolved_breaks) == 0):
            raise ValueError("continuity integrity mismatch")
        if self.deterministic_continuity_hash != self.compute_hash(self.chain_hash, self.continuity_score, self.continuity_integrity, self.unresolved_breaks):
            raise ValueError("continuity hash mismatch")
        return self
