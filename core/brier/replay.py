from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class BrierReplayPacket(BaseModel):
    schema_version: Literal["BrierReplayPacket.v1"] = "BrierReplayPacket.v1"
    replay_id: str
    ledger_hash: str
    deterministic_match: bool
    replayed_scores: list[str]
    mismatched_scores: list[str]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode='after')
    def _validate(self) -> "BrierReplayPacket":
        self.authority.assert_locked()
        if self.deterministic_match and self.mismatched_scores:
            raise ValueError("replay mismatch invalidates stabilization")
        return self
