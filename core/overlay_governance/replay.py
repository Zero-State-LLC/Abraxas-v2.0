from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OverlayGovernanceReplayPacket(BaseModel):
    schema_version: Literal["OverlayGovernanceReplayPacket.v1"] = "OverlayGovernanceReplayPacket.v1"
    replay_id: str
    source_ledger_hash: str
    replay_ledger_hash: str
    deterministic_match: bool
    mismatched_events: list[str]
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @model_validator(mode="after")
    def _validate(self) -> "OverlayGovernanceReplayPacket":
        self.authority.assert_locked()
        self.authority
        if self.deterministic_match != (self.source_ledger_hash == self.replay_ledger_hash and not self.mismatched_events):
            raise ValueError("replay mismatch")
        return self
