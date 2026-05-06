from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class StateRollbackPacket(BaseModel):
    schema_version: Literal["StateRollbackPacket.v1"] = "StateRollbackPacket.v1"
    rollback_id: str
    source_state_hash: str
    target_state_hash: str
    rollback_reason: str
    rollback_possible: bool
    deterministic_rollback_hash: str
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(source: str, target: str, reason: str, possible: bool) -> str:
        return hashlib.sha256(f"{source}|{target}|{reason}|{possible}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "StateRollbackPacket":
        self.authority.assert_locked()
        if self.deterministic_rollback_hash != self.compute_hash(
            self.source_state_hash, self.target_state_hash, self.rollback_reason, self.rollback_possible
        ):
            raise ValueError("rollback hash mismatch")
        return self
