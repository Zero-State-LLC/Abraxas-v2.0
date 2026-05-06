from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority


class OverlayGovernanceLedgerEntry(BaseModel):
    event_hash: str
    parent_event_hash: str | None = None
    generation: int = Field(ge=1)
    event_type: str


class OverlayGovernanceLedgerPacket(BaseModel):
    schema_version: Literal["OverlayGovernanceLedgerPacket.v1"] = "OverlayGovernanceLedgerPacket.v1"
    ledger_id: str
    entries: list[OverlayGovernanceLedgerEntry]
    ledger_depth: int = Field(ge=0)
    deterministic_ledger_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(entries: list[OverlayGovernanceLedgerEntry]) -> str:
        ordered = sorted(entries, key=lambda e: (e.generation, e.event_hash))
        payload = "|".join(f"{e.event_hash}:{e.parent_event_hash or '-'}:{e.generation}:{e.event_type}" for e in ordered)
        return hashlib.sha256(payload.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OverlayGovernanceLedgerPacket":
        self.authority.assert_locked()
        self.authority
        if self.ledger_depth != len(self.entries):
            raise ValueError("depth")
        if self.deterministic_ledger_hash != self.compute_hash(self.entries):
            raise ValueError("ledger hash")
        seen: set[str] = set()
        by_hash = {e.event_hash: e for e in self.entries}
        for e in self.entries:
            if e.parent_event_hash and e.parent_event_hash not in by_hash:
                raise ValueError("unknown parent")
            if e.parent_event_hash == e.event_hash:
                raise ValueError("cyclic parent")
            if e.event_hash in seen:
                raise ValueError("append-only violation")
            seen.add(e.event_hash)
        return self
