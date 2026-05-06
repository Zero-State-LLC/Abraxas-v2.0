from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class DriftReplayPacket(BaseModel):
    schema_version: Literal["DriftReplayPacket.v1"] = "DriftReplayPacket.v1"
    replay_id: str
    overlay_hash: str
    deterministic_match: bool
    replayed_overlays: list[str]
    mismatched_overlays: list[str]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode='after')
    def _validate(self) -> "DriftReplayPacket":
        self.authority.assert_locked()
        if self.deterministic_match and self.mismatched_overlays:
            raise ValueError("replay mismatch invalidates stabilization")
        return self
