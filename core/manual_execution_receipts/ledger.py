from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ManualExecutionReceiptLedgerPacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptLedgerPacket.v1"] = "ManualExecutionReceiptLedgerPacket.v1"
    ledger_id: str
    receipt_hashes: list[str]
    total_receipts: int
    pending_receipts: int
    blocked_receipts: int
    invalid_receipts: int
    deterministic_ledger_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(receipt_hashes: list[str], total: int, pending: int, blocked: int, invalid: int) -> str:
        payload = f"{'|'.join(sorted(receipt_hashes))}|{total}|{pending}|{blocked}|{invalid}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptLedgerPacket":
        self.authority.assert_locked()
        if self.receipt_hashes != sorted(self.receipt_hashes):
            raise ValueError("append ordering invalid")
        expected = self.compute_hash(
            self.receipt_hashes,
            self.total_receipts,
            self.pending_receipts,
            self.blocked_receipts,
            self.invalid_receipts,
        )
        if self.deterministic_ledger_hash != expected:
            raise ValueError("ledger hash")
        return self
