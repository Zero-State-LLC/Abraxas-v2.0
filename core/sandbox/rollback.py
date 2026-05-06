from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SandboxRollbackPacket(BaseModel):
    schema_version: Literal["SandboxRollbackPacket.v1"] = "SandboxRollbackPacket.v1"
    rollback_id: str
    branch_hash: str
    rollback_possible: bool
    rollback_target_hash: str
    rollback_reason: str
    deterministic_rollback_hash: str
    authority: Authority = Authority()
    status: str = "ready"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(branch_hash: str, rollback_target_hash: str, rollback_reason: str, rollback_possible: bool) -> str:
        return hashlib.sha256(f"{branch_hash}|{rollback_target_hash}|{rollback_reason}|{rollback_possible}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "SandboxRollbackPacket":
        self.authority.assert_locked()
        if self.compute_hash(self.branch_hash, self.rollback_target_hash, self.rollback_reason, self.rollback_possible) != self.deterministic_rollback_hash:
            raise ValueError("deterministic rollback hash mismatch")
        return self
