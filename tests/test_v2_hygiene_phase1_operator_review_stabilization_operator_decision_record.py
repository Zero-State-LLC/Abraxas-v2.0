from __future__ import annotations

from pathlib import Path

import pytest

from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt import (
    build_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt,
)
from core.sync.v2_hygiene_phase1_operator_review_stabilization_operator_decision_record import (
    build_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record,
    write_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record,
)
from scripts.hygiene import (
    run_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt,
)

from tests._repo_mirror import make_repo_mirror

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def mirror_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Working-tree mirror: these writers read and write the same root, so they
    run here instead of rewriting the tracked out/ receipts."""
    return make_repo_mirror(tmp_path_factory.mktemp("v2_hygiene_stabilization_record"))


def test_stabilization_operator_decision_record_attested(mirror_root: Path) -> None:
    write_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
        mirror_root
    )
    packet = build_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
        mirror_root
    )
    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_OPERATOR_DECISION_RECORD_ATTESTED"
    )
    assert packet["operator_attestations_present"] is True
    assert packet["hygiene_code_creation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["v2_module_registration_authorized"] is False


def test_stabilization_hold_receipt_terminal(mirror_root: Path) -> None:
    run_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt.run(
        mirror_root
    )
    packet = (
        build_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt(
            mirror_root
        )
    )
    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_HOLD_RECEIPT_EMITTED"
    )
    assert packet["terminal_hold"] is True
    assert packet["downstream"] == "NOT_COMPUTABLE"
