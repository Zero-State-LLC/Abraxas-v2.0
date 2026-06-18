from __future__ import annotations

from pathlib import Path

from core.abx_codegen_shadow_replay_harness_operator_attestation_intake_gate import (
    DEFAULT_PAYLOAD_PATH,
    build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_payload_observed_at_canonical_path() -> None:
    assert (REPO_ROOT / DEFAULT_PAYLOAD_PATH).is_file()


def test_intake_gate_validated_with_operator_clearance() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        REPO_ROOT
    )
    assert (
        packet["status"]
        == "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_VALIDATED"
    )
    assert packet["attestation_payload_observed"] is True
    assert packet["intake_validated_for_operator_decision_record"] is True
    assert packet["intake_gate_clearance_authorized"] is True
    assert packet["downstream"] == "INTAKE_CLEARED_ONLY"
    assert packet["recommended_next_lane"] == (
        "ABX_CODEGEN_INTELLIGENCE_SPINE_SHADOW_REPLAY_HARNESS_OPERATOR_DECISION_RECORD_REVIEW"
    )
    assert packet["authority_granted"] is False
    assert packet["harness_implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["validation_blockers"] == []


def test_intake_gate_deterministic() -> None:
    first = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        REPO_ROOT
    )
    second = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        REPO_ROOT
    )
    assert first["gate_hash"] == second["gate_hash"]
    assert first == second
