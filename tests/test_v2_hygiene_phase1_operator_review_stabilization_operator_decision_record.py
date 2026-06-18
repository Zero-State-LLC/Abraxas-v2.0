from __future__ import annotations

from pathlib import Path

from core.sync.v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt import (
    build_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt,
)
from core.sync.v2_hygiene_phase1_operator_review_stabilization_operator_decision_record import (
    build_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record,
    write_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record,
)
from scripts import (
    run_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stabilization_operator_decision_record_attested() -> None:
    write_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
        REPO_ROOT
    )
    packet = build_v2_hygiene_phase1_operator_review_stabilization_operator_decision_record(
        REPO_ROOT
    )
    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_OPERATOR_DECISION_RECORD_ATTESTED"
    )
    assert packet["operator_attestations_present"] is True
    assert packet["hygiene_code_creation_authorized"] is False
    assert packet["schema_mutation_authorized"] is False
    assert packet["v2_module_registration_authorized"] is False


def test_stabilization_hold_receipt_terminal() -> None:
    run_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt.run(
        REPO_ROOT
    )
    packet = (
        build_v2_hygiene_phase1_operator_review_stabilization_decision_record_hold_receipt(
            REPO_ROOT
        )
    )
    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_HOLD_RECEIPT_EMITTED"
    )
    assert packet["terminal_hold"] is True
    assert packet["downstream"] == "NOT_COMPUTABLE"
