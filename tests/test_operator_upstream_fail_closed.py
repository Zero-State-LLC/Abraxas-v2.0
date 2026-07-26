from __future__ import annotations

import pytest

from core.governance.upstream_evidence import require_upstream_packets
from core.human_decision_continuity.runtime import run_human_decision_continuity
from core.human_decision_ledger.runtime import run_human_decision_ledger
from core.manual_execution.runtime import run_manual_execution_authorization
from core.manual_execution_receipts.runtime import run_manual_execution_receipt_ledger


def _stub(*count: int) -> list[dict]:
    return [{"evidence": f"e{i}"} for i in range(count[0] if count else 1)]


def test_require_upstream_packets_rejects_empty() -> None:
    with pytest.raises(ValueError, match="refuse synthetic passed packet"):
        require_upstream_packets(("upstream", []), surface="test_surface")


def test_require_upstream_packets_rejects_empty_dict() -> None:
    with pytest.raises(ValueError, match="empty/malformed"):
        require_upstream_packets(("upstream", [{}]), surface="test_surface")


def test_human_decision_ledger_empty_fails_closed() -> None:
    with pytest.raises(ValueError, match="human_decision_ledger"):
        run_human_decision_ledger([], [], [], [])


def test_human_decision_continuity_empty_fails_closed() -> None:
    with pytest.raises(ValueError, match="human_decision_continuity"):
        run_human_decision_continuity([], [], [], [])


def test_manual_execution_empty_fails_closed() -> None:
    with pytest.raises(ValueError, match="manual_execution_authorization"):
        run_manual_execution_authorization([], [], [], [], [])


def test_manual_execution_receipts_empty_fails_closed() -> None:
    with pytest.raises(ValueError, match="manual_execution_receipt_ledger"):
        run_manual_execution_receipt_ledger([], [], [], [], [])


def test_nonempty_upstreams_still_emit_packets() -> None:
    ledger = run_human_decision_ledger(_stub(1), _stub(1), _stub(1), _stub(1))
    assert ledger["status"] == "passed"
    continuity = run_human_decision_continuity(_stub(1), _stub(1), _stub(1), _stub(1))
    assert continuity["status"] == "passed"
    manual = run_manual_execution_authorization(
        _stub(1), _stub(1), _stub(1), _stub(1), _stub(1)
    )
    assert manual["status"] == "passed"
    receipts = run_manual_execution_receipt_ledger(
        _stub(1), _stub(1), _stub(1), _stub(1), _stub(1)
    )
    assert receipts["status"] == "passed"


def test_sole_writers_no_longer_hardcode_empty_lists() -> None:
    paths = [
        "scripts/operator/run_human_decision_ledger.py",
        "scripts/operator/run_human_decision_continuity.py",
        "scripts/operator/run_manual_execution_authorization.py",
        "scripts/operator/run_manual_execution_receipt_ledger.py",
        "scripts/operator/run_manual_execution_replay.py",
        "scripts/operator/run_human_decision_continuity_replay.py",
        "scripts/operator/run_manual_execution_receipt_replay.py",
    ]
    for path in paths:
        source = __import__("pathlib").Path(path).read_text(encoding="utf-8")
        assert "([], [], [], [])" not in source
        assert "([], [], [], [], [])" not in source
