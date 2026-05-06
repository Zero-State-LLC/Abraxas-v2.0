from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OverlayResolutionLedgerPacket(BaseModel):
    schema_version: Literal["OverlayResolutionLedgerPacket.v1"] = "OverlayResolutionLedgerPacket.v1"
    ledger_id: str
    resolution_events: list[str]
    total_events: int
    unresolved_events: int
    critical_unresolved_events: int
    deterministic_ledger_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(events: list[str], total: int, unresolved: int, critical_unresolved: int) -> str:
        ordered = sorted(events)
        return hashlib.sha256(f"{'|'.join(ordered)}|{total}|{unresolved}|{critical_unresolved}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayResolutionLedgerPacket":
        self.authority.assert_locked()
        if self.deterministic_ledger_hash != self.compute_hash(self.resolution_events, self.total_events, self.unresolved_events, self.critical_unresolved_events):
            raise ValueError("ledger hash")
        return self
