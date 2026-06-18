from __future__ import annotations

from pathlib import Path

from core.abx_codegen_shadow_replay_harness_operator_attestation_intake_gate import (
    DEFAULT_PAYLOAD_PATH,
    build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_payload_observed_at_canonical_path() -> None:
    assert (REPO_ROOT / DEFAULT_PAYLOAD_PATH).is_file()


def test_intake_gate_blocked_with_draft_payload() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        REPO_ROOT
    )
    assert (
        packet["status"]
        == "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_BLOCKED"
    )
    assert packet["attestation_payload_observed"] is True
    assert packet["intake_validated_for_operator_decision_record"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["authority_granted"] is False
    assert packet["harness_implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_implementation"] is False
    assert "external_attestation_not_received" in packet["validation_blockers"]
    assert "operator_acceptance_pending" in packet["validation_blockers"]
    assert "operator_review_incomplete" in packet["validation_blockers"]


def test_intake_gate_deterministic() -> None:
    first = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        REPO_ROOT
    )
    second = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        REPO_ROOT
    )
    assert first["gate_hash"] == second["gate_hash"]
    assert first == second
