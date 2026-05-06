from core.brier.ledger import BrierLedgerEntry


def test_ledger_hash_deterministic() -> None:
    assert BrierLedgerEntry.compute_hash("f", "s", "c", 1) == BrierLedgerEntry.compute_hash("f", "s", "c", 1)
