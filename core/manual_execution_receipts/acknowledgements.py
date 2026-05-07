from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator


class ManualExecutionReceiptAcknowledgementPacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptAcknowledgementPacket.v1"] = "ManualExecutionReceiptAcknowledgementPacket.v1"
    acknowledgement_id: str
    receipt_hash: str
    acknowledgement_hash: str
    deterministic_acknowledgement_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(receipt_hash: str, acknowledgement_hash: str) -> str:
        return hashlib.sha256(f"{receipt_hash}|{acknowledgement_hash}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptAcknowledgementPacket":
        if self.deterministic_acknowledgement_hash != self.compute_hash(self.receipt_hash, self.acknowledgement_hash):
            raise ValueError("ack hash")
        return self
