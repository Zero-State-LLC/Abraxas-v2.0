from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority

ALLOWED_RECEIPT_ACTIONS = {
    "inspect_receipt",
    "document_receipt",
    "compare_receipt",
    "defer_receipt",
    "invalidate_receipt",
}
FORBIDDEN_RECEIPT_ACTIONS = {
    "execute",
    "activate",
    "deploy",
    "route_production",
    "mutate_forecast",
    "mutate_weight",
    "mutate_canon",
    "auto_apply",
}


class ManualExecutionReceiptScopePacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptScopePacket.v1"] = "ManualExecutionReceiptScopePacket.v1"
    receipt_scope_id: str
    receipt_hash: str
    bounded_scope_hash: str
    allowed_receipt_actions: list[str]
    forbidden_receipt_actions: list[str]
    deterministic_scope_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(receipt_hash: str, bounded_scope_hash: str, allowed_actions: list[str], forbidden_actions: list[str]) -> str:
        payload = f"{receipt_hash}|{bounded_scope_hash}|{'|'.join(sorted(allowed_actions))}|{'|'.join(sorted(forbidden_actions))}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptScopePacket":
        self.authority.assert_locked()
        if any(action not in ALLOWED_RECEIPT_ACTIONS for action in self.allowed_receipt_actions):
            raise ValueError("invalid allowed action")
        if any(action in FORBIDDEN_RECEIPT_ACTIONS for action in self.allowed_receipt_actions):
            raise ValueError("forbidden receipt action")
        if set(self.forbidden_receipt_actions) != FORBIDDEN_RECEIPT_ACTIONS:
            raise ValueError("forbidden actions explicit")
        expected = self.compute_hash(
            self.receipt_hash,
            self.bounded_scope_hash,
            self.allowed_receipt_actions,
            self.forbidden_receipt_actions,
        )
        if self.deterministic_scope_hash != expected:
            raise ValueError("scope hash")
        return self
