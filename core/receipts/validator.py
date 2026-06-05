"""Receipt validation helpers."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from core.receipts.models import RepoExecutionReceipt


def validate_receipt(receipt: RepoExecutionReceipt) -> dict[str, Any]:
    try:
        rebuilt = RepoExecutionReceipt(**receipt.model_dump())
    except ValidationError as exc:
        return {
            "command_id": receipt.command_id,
            "status": "invalid",
            "reason": str(exc),
        }

    return {
        "command_id": rebuilt.command_id,
        "receipt_id": rebuilt.receipt_id,
        "status": "valid",
        "execution_state": rebuilt.execution_state.value,
    }
