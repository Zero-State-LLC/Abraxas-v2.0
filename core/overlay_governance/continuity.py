from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority


class OverlayGovernanceContinuityPacket(BaseModel):
    schema_version: Literal["OverlayGovernanceContinuityPacket.v1"] = "OverlayGovernanceContinuityPacket.v1"
    continuity_id: str
    ledger_hash: str
    expected_event_types: list[str]
    observed_event_types: list[str]
    missing_event_types: list[str]
    continuity_score: float = Field(ge=0.0, le=1.0)
    deterministic_continuity_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(ledger_hash: str, expected_event_types: list[str], observed_event_types: list[str], missing_event_types: list[str], continuity_score: float) -> str:
        return hashlib.sha256(f"{ledger_hash}|{sorted(expected_event_types)}|{sorted(observed_event_types)}|{sorted(missing_event_types)}|{continuity_score:.8f}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayGovernanceContinuityPacket":
        self.authority.assert_locked()
        self.authority
        if self.deterministic_continuity_hash != self.compute_hash(self.ledger_hash, self.expected_event_types, self.observed_event_types, self.missing_event_types, self.continuity_score):
            raise ValueError("continuity hash")
        return self
