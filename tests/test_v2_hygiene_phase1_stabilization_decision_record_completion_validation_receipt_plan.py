from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan import (
    PLAN_JSON_PATH,
    READY_STATUS,
    build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan,
    render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan,
)
from scripts.hygiene import (
    run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan.v1.schema.json"
)
SOURCE_APPROVAL_GATE_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "approval_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_completion_validation_receipt_plan_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT
    )

    assert first["receipt_plan_hash"] == second["receipt_plan_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["receipt_plan_ready"] is True
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["downstream"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False
    assert first["valid_for_decision_record_completion_validation"] is False
    assert first["valid_for_implementation"] is False
    assert first["valid_for_execution"] is False


def test_completion_validation_receipt_plan_missing_gate_returns_not_computable(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT,
        source_completion_validation_approval_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["receipt_plan_ready"] is False
    assert "required_completion_validation_approval_gate_missing" in packet[
        "source_blockers"
    ]
    assert packet["decision_record_completion_validation_performed"] is False


def test_completion_validation_receipt_plan_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    approval_gate = _read_json(SOURCE_APPROVAL_GATE_PATH)
    approval_gate["valid_for_decision_record_completion_validation"] = True
    approval_gate["authority_locks"]["decision_record_completion_validation"] = True
    path = _write_source(tmp_path, "authorizing_approval_gate.json", approval_gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT,
        source_completion_validation_approval_gate_path=path,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "RECEIPT_PLAN_BLOCKED"
    )
    assert "completion_validation_approval_gate_authority_expanding_field:valid_for_decision_record_completion_validation" in packet[
        "source_blockers"
    ]
    assert (
        "completion_validation_approval_gate_authority_lock_true:"
        "decision_record_completion_validation"
    ) in packet["source_blockers"]
    assert packet["valid_for_decision_record_completion_validation"] is False
    assert packet["decision_record_completion_validation_authorized"] is False
    assert packet["decision_record_completion_validation_performed"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_completion_validation_receipt_plan_contracts_are_non_authoritative() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT
    )
    validation_contract = packet["planned_validation_packet_contract"]
    brier_contract = packet["planned_brier_scoring_contract"]
    rune_mapping = packet["planned_rune_governance_mapping"]

    assert validation_contract["completion_validation_authorized"] is False
    assert validation_contract["completion_validation_performed"] is False
    assert validation_contract["receipt_plan_only"] is True
    assert all(
        value is False for value in validation_contract["authority_denials"].values()
    )
    assert brier_contract["telemetry_only"] is True
    assert brier_contract["brier_score_formula"] == (
        "(forecast_probability - binary_outcome)^2"
    )
    assert brier_contract["resolution_allowed"] is False
    assert brier_contract["adaptive_learning_authorized"] is False
    assert brier_contract["forecast_routing_authorized"] is False
    assert brier_contract["promotion_authorized"] is False
    assert {item["rune"] for item in rune_mapping} == {
        "Observe",
        "Bind",
        "Hold",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in rune_mapping)


def test_completion_validation_receipt_plan_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["decision_record_creation_authorized"] is False
    assert packet["decision_record_completed"] is False
    assert packet["decision_record_completion_authorized"] is False
    assert packet["decision_record_completion_validation_authorized"] is False
    assert packet["decision_record_completion_validation_performed"] is False
    assert packet["decision_record_emitted"] is False
    assert packet["decision_record_emission_authorized"] is False
    assert packet["decision_record_finalized"] is False
    assert packet["decision_record_finalization_authorized"] is False
    assert packet["decision_record_materialized"] is False
    assert packet["decision_record_materialization_authorized"] is False
    assert packet["authorization_record_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert packet["forecast_routing_authorized"] is False
    assert packet["adaptive_learning_authorized"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_completion_validation_receipt_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_plan_hash = packet_without_hash.pop("receipt_plan_hash")
    assert receipt_plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_completion_validation_receipt_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["receipt_plan_hash"] == packet["receipt_plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_completion_validation_receipt_plan_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_receipt_plan_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion "
        "Validation Receipt Plan"
    )
    assert any("telemetry_only: True" in line for line in markdown)
    assert any("adaptive_learning_authorized: False" in line for line in markdown)
