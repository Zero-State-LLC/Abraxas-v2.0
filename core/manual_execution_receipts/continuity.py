from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator


class ManualExecutionReceiptContinuityPacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptContinuityPacket.v1"] = "ManualExecutionReceiptContinuityPacket.v1"
    continuity_id: str
    receipt_hash: str
    envelope_hash: str
    append_only: bool
    deterministic_continuity_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(receipt_hash: str, envelope_hash: str, append_only: bool) -> str:
        return hashlib.sha256(f"{receipt_hash}|{envelope_hash}|{int(append_only)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptContinuityPacket":
        if self.deterministic_continuity_hash != self.compute_hash(self.receipt_hash, self.envelope_hash, self.append_only):
            raise ValueError("continuity hash")
        return self
