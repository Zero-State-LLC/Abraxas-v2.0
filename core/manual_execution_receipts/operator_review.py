from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ManualExecutionReceiptOperatorReviewPacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptOperatorReviewPacket.v1"] = "ManualExecutionReceiptOperatorReviewPacket.v1"
    review_id: str
    receipt_ledger_hash: str
    total_receipts: int
    pending_receipts: int
    blocked_receipts: int
    invalid_receipts: int
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "pending", "blocked"]

    @staticmethod
    def compute_hash(ledger_hash: str, total: int, pending: int, blocked: int, invalid: int, unresolved: int) -> str:
        return hashlib.sha256(f"{ledger_hash}|{total}|{pending}|{blocked}|{invalid}|{unresolved}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptOperatorReviewPacket":
        self.authority.assert_locked()
        if self.deterministic_review_hash != self.compute_hash(
            self.receipt_ledger_hash,
            self.total_receipts,
            self.pending_receipts,
            self.blocked_receipts,
            self.invalid_receipts,
            self.unresolved_diagnostics,
        ):
            raise ValueError("review hash")
        return self
