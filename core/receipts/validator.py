"""Receipt validator stub."""

from __future__ import annotations

from core.receipts.models import RepoExecutionReceipt


def validate_receipt(receipt: RepoExecutionReceipt) -> dict[str, object]:
    """Validate a receipt; returns status dict."""
    try:
        receipt.authority.assert_locked()
        return {"command_id": receipt.command_id, "status": "valid"}
    except ValueError as exc:
        return {"command_id": receipt.command_id, "status": "invalid", "reason": str(exc)}
