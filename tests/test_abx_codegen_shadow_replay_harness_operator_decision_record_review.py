from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_codegen_shadow_replay_harness_operator_attestation_intake_gate import (
    build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate,
)
from core.abx_codegen_shadow_replay_harness_operator_decision_record_review import (
    REVIEW_INTAKE_CLEARED_STATUS,
    build_abx_codegen_shadow_replay_harness_operator_decision_record_review,
    render_abx_codegen_shadow_replay_harness_operator_decision_record_review_markdown,
)
from core.canonical.json import canonical_hash
from scripts.codegen import run_abx_codegen_shadow_replay_harness_operator_decision_record_review

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/canon/"
    "abx_codegen_shadow_replay_harness_operator_decision_record_review.v1.schema.json"
)


def test_codegen_operator_decision_record_review_observes_intake_cleared() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_review(
        repo_root=REPO_ROOT
    )

    assert packet["operator_decision_record_review_status"] == REVIEW_INTAKE_CLEARED_STATUS
    assert packet["source_operator_decision_record_dry_run"]["source_ready"] is True
    assert packet["source_attestation_intake_gate"]["intake_cleared_observed"] is True
    assert packet["selected_operator_decision"] == "MAINTAIN_HOLD"
    assert packet["operator_attestations_present"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_codegen_operator_decision_record_review_denies_creation_and_authority() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_review(
        repo_root=REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["implementation_authorization_granted"] is False
    assert packet["meta_gate_authorization_granted"] is False
    assert packet["operator_approved"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_codegen_operator_decision_record_review_fails_closed_without_source(
    tmp_path: Path,
) -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_review(
        repo_root=tmp_path
    )

    assert packet["operator_decision_record_review_status"] == "NOT_COMPUTABLE"
    assert packet["selected_operator_decision"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["source_operator_decision_record_dry_run"]["source_ready"] is False
    assert packet["source_attestation_intake_gate"]["intake_cleared_observed"] is False


def test_codegen_operator_decision_record_review_schema_and_hash_are_stable() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_review(
        repo_root=REPO_ROOT
    )
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_codegen_operator_decision_record_review_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = (
        tmp_path
        / "out/audit/"
        "abx_codegen_intelligence_spine_shadow_replay_harness_operator_decision_"
        "record_review_001.latest.json"
    )
    out_md = out_json.with_suffix(".md")

    first = run_abx_codegen_shadow_replay_harness_operator_decision_record_review.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_abx_codegen_shadow_replay_harness_operator_decision_record_review.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_codegen_operator_decision_record_review_markdown() -> None:
    packet = build_abx_codegen_shadow_replay_harness_operator_decision_record_review(
        repo_root=REPO_ROOT
    )
    markdown = render_abx_codegen_shadow_replay_harness_operator_decision_record_review_markdown(
        packet
    )

    assert markdown[0] == "# ABX Codegen Shadow Replay Harness Operator Decision Record Review"
    assert any("operator_attestations_present: False" in line for line in markdown)
    assert any("intake_cleared_observed: True" in line for line in markdown)
    assert any("recommended_next_lane: NOT_COMPUTABLE" in line for line in markdown)


def test_intake_gate_remains_validated_after_odr_intake_bridge_observation() -> None:
    review = build_abx_codegen_shadow_replay_harness_operator_decision_record_review(
        repo_root=REPO_ROOT
    )
    assert review["operator_decision_record_review_status"] == REVIEW_INTAKE_CLEARED_STATUS

    intake = build_abx_codegen_shadow_replay_harness_operator_attestation_intake_gate(
        REPO_ROOT
    )
    assert (
        intake["status"]
        == "ABX_CODEGEN_SHADOW_REPLAY_HARNESS_OPERATOR_ATTESTATION_INTAKE_VALIDATED"
    )
    assert intake["downstream"] == "INTAKE_CLEARED_ONLY"
    assert intake["intake_validated_for_operator_decision_record"] is True
