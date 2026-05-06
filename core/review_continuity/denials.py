from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class ReviewDenialPacket(BaseModel):
    schema_version: Literal["ReviewDenialPacket.v1"] = "ReviewDenialPacket.v1"
    denial_id: str
    chain_hash: str
    denial_reason: str
    denial_code: str
    deterministic_denial_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(chain_hash: str, denial_reason: str, denial_code: str) -> str:
        return hashlib.sha256(f"{chain_hash}|{denial_reason}|{denial_code}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if not self.denial_reason.strip():
            raise ValueError("explicit denial reason required")
        if self.deterministic_denial_hash != self.compute_hash(self.chain_hash, self.denial_reason, self.denial_code):
            raise ValueError("denial hash mismatch")
        return self
