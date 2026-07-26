from __future__ import annotations

import pytest

from core.external_action_proposals.runtime import run_external_action_proposals
from core.governance.upstream_evidence import require_upstream_packets
from core.human_decision_continuity.runtime import run_human_decision_continuity
from core.human_decision_ledger.runtime import run_human_decision_ledger
from core.manual_execution.runtime import run_manual_execution_authorization
from core.manual_execution_receipts.runtime import run_manual_execution_receipt_ledger
from core.operator_queue.runtime import run_operator_approval_queue
from core.review_resolution.runtime import run_review_resolution_spine


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


def test_operator_approval_queue_empty_fails_closed() -> None:
    with pytest.raises(ValueError, match="operator_approval_queue"):
        run_operator_approval_queue([], [], [], [], [])


def test_review_resolution_spine_empty_fails_closed() -> None:
    with pytest.raises(ValueError, match="review_resolution_spine"):
        run_review_resolution_spine([], [], [], [], [])


def test_external_action_proposals_empty_fails_closed() -> None:
    with pytest.raises(ValueError, match="external_action_proposals"):
        run_external_action_proposals([], [], [], [], [])


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
    queue = run_operator_approval_queue(
        _stub(1), _stub(1), _stub(1), _stub(1), _stub(1)
    )
    assert queue["status"] == "passed"
    resolution = run_review_resolution_spine(
        _stub(1), _stub(1), _stub(1), _stub(1), _stub(1)
    )
    assert resolution["status"] == "passed"
    proposals = run_external_action_proposals(
        _stub(1), _stub(1), _stub(1), _stub(1), _stub(1)
    )
    assert proposals["status"] == "passed"


def test_sole_writers_no_longer_hardcode_empty_lists() -> None:
    paths = [
        "scripts/operator/run_human_decision_ledger.py",
        "scripts/operator/run_human_decision_continuity.py",
        "scripts/operator/run_manual_execution_authorization.py",
        "scripts/operator/run_manual_execution_receipt_ledger.py",
        "scripts/operator/run_manual_execution_replay.py",
        "scripts/operator/run_human_decision_continuity_replay.py",
        "scripts/operator/run_manual_execution_receipt_replay.py",
        "scripts/operator/run_operator_approval_queue.py",
        "scripts/operator/run_operator_queue_replay.py",
        "scripts/governance/run_review_resolution_spine.py",
        "scripts/governance/run_review_resolution_replay.py",
        "scripts/campaign/run_external_action_proposals.py",
        "scripts/campaign/run_external_action_proposal_replay.py",
    ]
    for path in paths:
        source = __import__("pathlib").Path(path).read_text(encoding="utf-8")
        assert "([], [], [], [])" not in source
        assert "([], [], [], [], [])" not in source
