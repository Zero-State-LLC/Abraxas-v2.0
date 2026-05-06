from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class IntakeReplayPacket(BaseModel):
    schema_version: Literal["IntakeReplayPacket.v1"] = "IntakeReplayPacket.v1"
    replay_id: str
    source_intake_hash: str
    replay_intake_hash: str
    deterministic_match: bool
    mismatched_normalizations: list[str]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "IntakeReplayPacket":
        self.authority.assert_locked()
        if self.deterministic_match and self.mismatched_normalizations:
            raise ValueError("mismatch invalidates stabilization")
        return self
