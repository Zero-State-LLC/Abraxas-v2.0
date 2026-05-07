from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority

ALLOWED_RECEIPT_STATUS = {
    "receipt_recorded",
    "receipt_pending",
    "receipt_blocked",
    "receipt_deferred",
    "receipt_invalid",
}
FORBIDDEN_RECEIPT_STATUS = {
    "executed",
    "activated",
    "deployed",
    "live",
    "auto_executed",
    "production_ready",
}


class ManualExecutionReceiptPacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptPacket.v1"] = "ManualExecutionReceiptPacket.v1"
    receipt_id: str
    authorization_hash: str
    envelope_hash: str
    acknowledgement_hash: str
    scope_hash: str
    replay_hash: str
    rollback_hash: str
    receipt_status: str
    receipt_reason: str
    deterministic_receipt_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(*parts: str) -> str:
        return hashlib.sha256("|".join(parts).encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptPacket":
        self.authority.assert_locked()
        if self.receipt_status in FORBIDDEN_RECEIPT_STATUS or self.receipt_status not in ALLOWED_RECEIPT_STATUS:
            raise ValueError("forbidden receipt status")
        expected = self.compute_hash(
            self.authorization_hash,
            self.envelope_hash,
            self.acknowledgement_hash,
            self.scope_hash,
            self.replay_hash,
            self.rollback_hash,
            self.receipt_status,
            self.receipt_reason,
        )
        if self.deterministic_receipt_hash != expected:
            raise ValueError("receipt hash")
        return self
