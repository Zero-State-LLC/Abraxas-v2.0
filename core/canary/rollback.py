from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryRollbackPacket(BaseModel):
    schema_version: Literal["CanaryRollbackPacket.v1"] = "CanaryRollbackPacket.v1"
    rollback_id: str
    overlay_hash: str
    rollback_reason: str
    rollback_generation: int
    rollback_complete: bool
    deterministic_rollback_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(overlay_hash: str, rollback_reason: str, rollback_generation: int, rollback_complete: bool) -> str:
        return hashlib.sha256(f"{overlay_hash}|{rollback_reason}|{rollback_generation}|{rollback_complete}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "CanaryRollbackPacket":
        self.authority.assert_locked()
        if self.deterministic_rollback_hash != self.compute_hash(self.overlay_hash, self.rollback_reason, self.rollback_generation, self.rollback_complete):
            raise ValueError("rollback deterministic")
        return self
