from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryPromotionRollbackPacket(BaseModel):
    schema_version: Literal["CanaryPromotionRollbackPacket.v1"] = "CanaryPromotionRollbackPacket.v1"
    rollback_id: str
    candidate_hash: str
    rollback_reason: str
    rollback_complete: bool
    deterministic_rollback_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(candidate_hash: str, rollback_reason: str, rollback_complete: bool) -> str:
        return hashlib.sha256(f"{candidate_hash}|{rollback_reason}|{rollback_complete}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryPromotionRollbackPacket":
        self.authority.assert_locked()
        if self.deterministic_rollback_hash != self.compute_hash(self.candidate_hash, self.rollback_reason, self.rollback_complete):
            raise ValueError("hash")
        return self
