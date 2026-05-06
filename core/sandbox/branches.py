from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SandboxBranchPacket(BaseModel):
    schema_version: Literal["SandboxBranchPacket.v1"] = "SandboxBranchPacket.v1"
    branch_id: str
    parent_state_hash: str
    sandbox_state_hash: str
    branch_generation: int
    topology_hash: str
    replay_hash: str | None = None
    authority: Authority = Authority()
    branch_status: Literal["active", "stabilizing", "stable", "failed", "rolled_back", "archived"] = "active"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(parent_state_hash: str, topology_hash: str, branch_generation: int) -> str:
        return hashlib.sha256(f"{parent_state_hash}|{topology_hash}|{branch_generation}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "SandboxBranchPacket":
        self.authority.assert_locked()
        if self.parent_state_hash == self.sandbox_state_hash:
            raise ValueError("sandbox branch must be isolated from parent state")
        return self
