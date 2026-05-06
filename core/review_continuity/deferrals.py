from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class ReviewDeferralPacket(BaseModel):
    schema_version: Literal["ReviewDeferralPacket.v1"] = "ReviewDeferralPacket.v1"
    deferral_id: str
    chain_hash: str
    deferral_reason: str
    deferral_code: str
    deterministic_deferral_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(chain_hash: str, deferral_reason: str, deferral_code: str) -> str:
        return hashlib.sha256(f"{chain_hash}|{deferral_reason}|{deferral_code}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if not self.deferral_reason.strip():
            raise ValueError("explicit deferral reason required")
        if self.deterministic_deferral_hash != self.compute_hash(self.chain_hash, self.deferral_reason, self.deferral_code):
            raise ValueError("deferral hash mismatch")
        return self
