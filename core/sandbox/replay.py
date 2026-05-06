from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SandboxReplayPacket(BaseModel):
    schema_version: Literal["SandboxReplayPacket.v1"] = "SandboxReplayPacket.v1"
    replay_id: str
    branch_hash: str
    deterministic_match: bool
    replayed_mutations: list[str]
    mismatched_mutations: list[str]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "SandboxReplayPacket":
        self.authority.assert_locked()
        if self.deterministic_match and self.mismatched_mutations:
            raise ValueError("deterministic replay cannot contain mismatches")
        return self
