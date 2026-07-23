"""Minimal advisory checklist for Soft Facade / hygiene receipts."""

from __future__ import annotations

REQUIRED_HYGIENE_FIELDS = {
    "schema_version",
    "execution_authority",
    "net_catalog_delta",
    "producer_system",
    "provenance",
    "recommended_next",
}


def assert_hygiene_receipt(receipt: dict, *, allow_execution: bool = False) -> None:
    """Assert that a receipt-like dict carries the uniform hygiene field set.

    Raises AssertionError on missing fields or when execution_authority is
    True unless allow_execution is explicitly set.
    """
    missing = REQUIRED_HYGIENE_FIELDS - set(receipt.keys())
    assert not missing, f"Missing hygiene fields: {sorted(missing)}"
    assert receipt.get("execution_authority") is False or allow_execution, (
        "execution_authority must be False for Soft Facade / hygiene receipts"
    )
    assert receipt.get("net_catalog_delta", 1) <= 0, (
        "net_catalog_delta must be <= 0 under compression posture"
    )
