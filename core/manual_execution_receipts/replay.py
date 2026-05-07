from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator


class ManualExecutionReceiptReplayPacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptReplayPacket.v1"] = "ManualExecutionReceiptReplayPacket.v1"
    replay_id: str
    source_ledger_hash: str
    replay_ledger_hash: str
    deterministic_match: bool
    mismatch_reasons: list[str]
    deterministic_replay_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(source: str, replay: str, matches: bool, reasons: list[str]) -> str:
        return hashlib.sha256(f"{source}|{replay}|{int(matches)}|{'|'.join(sorted(reasons))}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptReplayPacket":
        if self.deterministic_replay_hash != self.compute_hash(
            self.source_ledger_hash,
            self.replay_ledger_hash,
            self.deterministic_match,
            self.mismatch_reasons,
        ):
            raise ValueError("replay hash")
        return self
