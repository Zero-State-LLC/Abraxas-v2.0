import pytest

from core.overlay_governance.ledger import OverlayGovernanceLedgerEntry, OverlayGovernanceLedgerPacket


def test_ledger_append_only_ordering() -> None:
    e1 = OverlayGovernanceLedgerEntry(event_hash="a", generation=1, event_type="overlay_created")
    e2 = OverlayGovernanceLedgerEntry(event_hash="b", parent_event_hash="a", generation=2, event_type="overlay_observed")
    h = OverlayGovernanceLedgerPacket.compute_hash([e1, e2])
    p = OverlayGovernanceLedgerPacket(ledger_id="1", entries=[e1, e2], ledger_depth=2, deterministic_ledger_hash=h, status="passed")
    assert p.ledger_depth == 2


def test_cyclic_parent_fails_closed() -> None:
    e1 = OverlayGovernanceLedgerEntry(event_hash="a", parent_event_hash="a", generation=1, event_type="overlay_created")
    with pytest.raises(ValueError):
        OverlayGovernanceLedgerPacket(ledger_id="1", entries=[e1], ledger_depth=1, deterministic_ledger_hash=OverlayGovernanceLedgerPacket.compute_hash([e1]), status="passed")
