from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class CanaryScheduleRollbackPacket(BaseModel):
    schema_version: Literal["CanaryScheduleRollbackPacket.v1"] = "CanaryScheduleRollbackPacket.v1"
    rollback_id: str
    schedule_hash: str
    rollback_reason: str
    rollback_complete: bool
    deterministic_rollback_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(schedule_hash: str, reason: str, complete: bool) -> str:
        return hashlib.sha256(f"{schedule_hash}|{reason}|{complete}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "CanaryScheduleRollbackPacket":
        self.authority.assert_locked()
        if self.deterministic_rollback_hash != self.compute_hash(self.schedule_hash, self.rollback_reason, self.rollback_complete):
            raise ValueError("deterministic")
        return self
