from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class StateReplayPacket(BaseModel):
    schema_version: Literal["StateReplayPacket.v1"] = "StateReplayPacket.v1"
    replay_id: str
    source_state_hash: str
    replayed_state_hash: str
    deterministic_match: bool
    mismatched_transitions: list[str]
    authority: Authority = Authority()
    status: str = "pending"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "StateReplayPacket":
        self.authority.assert_locked()
        if self.mismatched_transitions and self.deterministic_match:
            raise ValueError("mismatched transitions invalidate replay")
        return self
