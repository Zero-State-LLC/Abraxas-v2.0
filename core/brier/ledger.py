from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class BrierLedgerEntry(BaseModel):
    schema_version: Literal["BrierLedgerEntry.v1"] = "BrierLedgerEntry.v1"
    ledger_entry_id: str
    forecast_hash: str
    score_hash: str
    calibration_hash: str
    replay_hash: str | None = None
    ledger_generation: int
    deterministic_ledger_hash: str
    authority: Authority = Authority()
    status: str = "recorded"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(forecast_hash: str, score_hash: str, calibration_hash: str, ledger_generation: int) -> str:
        return hashlib.sha256(f"{forecast_hash}|{score_hash}|{calibration_hash}|{ledger_generation}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "BrierLedgerEntry":
        self.authority.assert_locked()
        if self.deterministic_ledger_hash != self.compute_hash(self.forecast_hash, self.score_hash, self.calibration_hash, self.ledger_generation):
            raise ValueError("deterministic ordering")
        return self
