from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.research_canary_final_activation_operator_decision_record import (
    build_research_canary_final_activation_operator_decision_record,
    write_research_canary_final_activation_operator_decision_record,
)
from core.runtime_integration_gate_operator_attestation_intake_gate import (
    build_runtime_integration_gate_operator_attestation_intake_gate,
)
from core.oracle_signal_physical_implementation_authorization_intake_gate import (
    build_oracle_signal_physical_implementation_authorization_intake_gate,
)
from core.oracle_signal_physical_implementation_authorization_record import (
    build_oracle_signal_physical_implementation_authorization_record,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_gate_attestation_intake_validated() -> None:
    packet = build_runtime_integration_gate_operator_attestation_intake_gate(REPO_ROOT)
    assert packet["status"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_ATTESTATION_INTAKE_VALIDATED"
    assert packet["operator_selected_decision"] == "APPROVE_SHADOW_WIRING_ONLY"
    assert packet["intake_validated_for_decision_record"] is True


def test_runtime_gate_decision_record_shadow_wiring() -> None:
    from core.runtime_integration_gate_operator_review_decision_record import (
        build_runtime_integration_gate_operator_review_decision_record,
    )

    packet = build_runtime_integration_gate_operator_review_decision_record(REPO_ROOT)
    assert packet["status"] == "RUNTIME_INTEGRATION_GATE_OPERATOR_REVIEW_DECISION_RECORD_ATTESTED"
    assert packet["selected_decision"] == "APPROVE_SHADOW_WIRING_ONLY"
    assert packet["valid_for_runtime_wiring"] is True
    assert packet["mandatory_pre_dispatch_wiring"] is False
    assert packet["execution_authority"] is False
    assert packet["operator_id"] == "daniel_meyer"


def test_oracle_physical_implementation_authorization_record_emitted() -> None:
    intake = build_oracle_signal_physical_implementation_authorization_intake_gate(REPO_ROOT)
    assert intake["status"] == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_INTAKE_VALIDATED"
    record = build_oracle_signal_physical_implementation_authorization_record(REPO_ROOT)
    assert record["status"] == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_EMITTED"
    assert record["implementation_authorized"] is True
    assert record["execution_authority"] is False
    assert record["operator_id"] == "daniel_meyer"


def test_p131_operator_decision_record_emitted_with_pilot_shadow() -> None:
    packet = build_research_canary_final_activation_operator_decision_record(REPO_ROOT)
    assert packet["status"] == "OPERATOR_DECISION_RECORD_EMITTED"
    assert packet["lane_status"] == "OPERATOR_DECISION_RECORD_EMITTED_ADVISORY_ONLY"
    assert packet["operator_id"] == "daniel_meyer"
    assert packet["operator_selected_decision"] == "APPROVE_ADVISORY_SHADOW_ACTIVATION_PILOT"
    assert packet["recommended_next_lane"] == "P132_RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD"
    assert len(packet["candidate_decision_records"]) == 6
    drop006a = next(
        rec
        for rec in packet["candidate_decision_records"]
        if rec["candidate_id"] == "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER"
    )
    assert drop006a["activation_approved"] is True
    assert drop006a["advisory_shadow_activation_approved"] is True
    drop006b = next(
        rec
        for rec in packet["candidate_decision_records"]
        if rec["candidate_id"] == "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER"
    )
    assert drop006b["activation_approved"] is True
    assert drop006b["advisory_shadow_activation_approved"] is True
    drop006c = next(
        rec
        for rec in packet["candidate_decision_records"]
        if rec["candidate_id"] == "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER"
    )
    assert drop006c["activation_approved"] is True
    assert drop006c["advisory_shadow_activation_approved"] is True
    drop007a = next(
        rec
        for rec in packet["candidate_decision_records"]
        if rec["candidate_id"] == "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER"
    )
    assert drop007a["activation_approved"] is True
    assert drop007a["advisory_shadow_activation_approved"] is True
    approved_ids = {
        "DROP006A_INTENT_GRAPH_BEHAVIORAL_LOGIC_LAYER",
        "DROP006B_ACTIVE_INFERENCE_RECURSIVE_PLANNING_LAYER",
        "DROP006C_SURVIVAL_CALIBRATION_GOVERNANCE_LAYER",
        "DROP007A_SITUATION_RUNTIME_PROACTIVE_COORDINATION_LAYER",
    }
    assert all(
        not rec["activation_approved"]
        for rec in packet["candidate_decision_records"]
        if rec["candidate_id"] not in approved_ids
    )
    schema = json.loads(
        Path(
            "contracts/canon/research_canary_final_activation_operator_decision_record.v1.schema.json"
        ).read_text()
    )
    validate(packet, schema)


def test_p131_deterministic() -> None:
    first = build_research_canary_final_activation_operator_decision_record(REPO_ROOT)
    second = build_research_canary_final_activation_operator_decision_record(REPO_ROOT)
    assert first == second


def test_p131_writer(tmp_path: Path) -> None:
    out = tmp_path / "latest.json"
    packet = write_research_canary_final_activation_operator_decision_record(
        REPO_ROOT, out_path=out
    )
    assert out.exists()
    assert json.loads(out.read_text()) == packet
