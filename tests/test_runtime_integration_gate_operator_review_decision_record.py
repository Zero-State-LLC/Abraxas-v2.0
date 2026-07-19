from __future__ import annotations

from pathlib import Path

from core.runtime_integration_gate_operator_review_decision_record import (
    build_runtime_integration_gate_operator_review_decision_record,
)
from core.runtime_integration_gate_operator_review_decision_record_hold_receipt import (
    build_runtime_integration_gate_operator_review_decision_record_hold_receipt,
)
from core.runtime_integration_gate_operator_review_decision_record_plan import (
    PLAN_JSON_PATH,
    build_runtime_integration_gate_operator_review_decision_record_plan,
    write_runtime_integration_gate_operator_review_decision_record_plan,
)
from scripts.runtime import (
    run_runtime_integration_gate_operator_attestation_intake_gate,
    run_runtime_integration_gate_operator_review_decision_record,
    run_runtime_integration_gate_operator_review_decision_record_hold_receipt,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_gate_decision_record_plan_ready() -> None:
    packet = build_runtime_integration_gate_operator_review_decision_record_plan(
        REPO_ROOT
    )
    assert (
        packet["status"]
        == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_PLAN_READY"
    )
    assert packet["mandatory_pre_dispatch_wiring"] is False
    assert packet["valid_for_runtime_wiring"] is False


def test_runtime_gate_decision_record_attested() -> None:
    write_runtime_integration_gate_operator_review_decision_record_plan(REPO_ROOT)
    run_runtime_integration_gate_operator_attestation_intake_gate.run(REPO_ROOT)
    packet = build_runtime_integration_gate_operator_review_decision_record(REPO_ROOT)
    assert (
        packet["status"]
        == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_ATTESTED"
    )
    assert packet["operator_attestation_present"] is True
    assert packet["selected_decision"] == "APPROVE_SHADOW_WIRING_ONLY"
    assert packet["valid_for_runtime_wiring"] is True
    assert packet["mandatory_pre_dispatch_wiring"] is False
    assert packet["runtime_mutation_allowed"] is False


def test_runtime_gate_hold_receipt_terminal() -> None:
    run_runtime_integration_gate_operator_review_decision_record.run(REPO_ROOT)
    packet = build_runtime_integration_gate_operator_review_decision_record_hold_receipt(
        REPO_ROOT
    )
    assert (
        packet["status"]
        == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_HOLD_RECEIPT_EMITTED"
    )
    assert packet["shadow_wiring_approved"] is True
    assert packet["terminal_hold"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["mandatory_pre_dispatch_wiring"] is False
    assert packet["valid_for_runtime_wiring"] is True


def test_runtime_gate_chain_runner_stable(tmp_path: Path) -> None:
    first = run_runtime_integration_gate_operator_review_decision_record_hold_receipt.run(
        REPO_ROOT, out_root=tmp_path
    )
    second = run_runtime_integration_gate_operator_review_decision_record_hold_receipt.run(
        REPO_ROOT, out_root=tmp_path
    )
    assert first["receipt_hash"] == second["receipt_hash"]
    assert (tmp_path / PLAN_JSON_PATH).exists()
