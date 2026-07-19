from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate import (
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate,
    render_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_markdown,
    write_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate,
)
from scripts.hygiene import run_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate.v1.schema.json"
)
SOURCE_PHASE7_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase2_next_stabilization_subsystem_selection_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_operator_review_gate_ready_path_records_package_lock_hold() -> None:
    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT
    )

    assert packet["status"] == READY_STATUS
    assert packet["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert packet["source_blockers"] == []
    assert packet["operator_review_gate_ready"] is True
    assert packet["phase7_selection_receipt_hash_verified"] is True
    assert packet["recommended_next_lane"] == (
        "V2_HYGIENE_PHASE1_DEPENDENCY_HYGIENE_PACKAGE_LOCK_RECEIPT_001"
    )
    assert packet["downstream"] == "NOT_COMPUTABLE"
    assert packet["valid_for_package_lock_tracking"] is False
    assert packet["valid_for_execution"] is False
    package_lock = packet["package_lock_resolution_contract"]
    assert package_lock["preferred_disposition"] == "COMMIT_AND_TRACK_IF_VALIDATED"
    assert package_lock["actual_disposition"] == "HOLD_VALIDATION_FAILED"
    assert package_lock["package_lock_resolution_status"] == (
        "PACKAGE_LOCK_RESOLUTION_HELD_VALIDATION_FAILED"
    )
    assert package_lock["package_lock_tracking_authorized"] is False
    assert package_lock["metadata_consistent_with_package_json"] is True
    assert package_lock["fail_closed_blocker"] == "npm_ci_failed_invalid_version"


def test_operator_review_gate_missing_source_fails_closed(tmp_path: Path) -> None:
    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT,
        source_phase7_selection_receipt_path=tmp_path / "missing.json",
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE2_STABILIZATION_SUBSYSTEM_SELECTION_OPERATOR_REVIEW_GATE_BLOCKED"
    )
    assert packet["operator_review_gate_ready"] is False
    assert "required_phase7_selection_receipt_missing" in packet["source_blockers"]
    assert packet["phase7_selection_receipt_hash_verified"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_operator_review_gate_source_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    phase7 = _read_json(SOURCE_PHASE7_PATH)
    phase7["promotion_authorized"] = True
    phase7["authority_locks"]["promotion"] = True
    source = _write_source(tmp_path, "authorizing_phase7.json", phase7)

    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT,
        source_phase7_selection_receipt_path=source,
    )

    assert packet["operator_review_gate_ready"] is False
    assert "phase7_selection_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert (
        "phase7_selection_receipt_authority_expanding_field:promotion_authorized"
        in packet["source_blockers"]
    )
    assert "phase7_selection_receipt_authority_lock_true:promotion" in packet[
        "source_blockers"
    ]
    assert packet["promotion_authorized"] is False


def test_operator_review_gate_candidate_matrix_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    phase7 = _read_json(SOURCE_PHASE7_PATH)
    phase7["candidate_next_lane_matrix"] = phase7["candidate_next_lane_matrix"][:-1]
    phase7["candidate_next_lane_count"] = 4
    source = _write_source(tmp_path, "missing_candidate_phase7.json", phase7)

    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT,
        source_phase7_selection_receipt_path=source,
    )

    assert "phase7_selection_receipt_self_hash_mismatch" in packet["source_blockers"]
    assert "phase7_candidate_count_not_five" in packet["source_blockers"]
    assert "phase7_candidate_matrix_unexpected" in packet["source_blockers"]
    assert packet["operator_review_gate_ready"] is False


def test_operator_review_gate_contracts_preserve_authority_denials() -> None:
    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT
    )
    disposition = packet["operator_disposition_contract"]
    brier = packet["brier_scoring_contract"]
    runes = packet["rune_governance_mapping"]

    assert disposition["recommended_operator_decision"] == (
        "HOLD_FOR_PACKAGE_LOCK_RESOLUTION_REPAIR"
    )
    assert disposition["package_lock_resolution_selected"] is True
    assert all(value is False for value in disposition["authority_denials"].values())
    assert brier["telemetry_only"] is True
    assert brier["resolution_allowed"] is False
    assert brier["promotion_authorized"] is False
    assert brier["brier_resolution_authorized"] is False
    assert {item["rune"] for item in runes} == {
        "Observe",
        "Bind",
        "Hold",
        "Weigh",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in runes)
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["canon_promotion_authorized"] is False
    assert packet["runtime_activation_authorized"] is False
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["execution_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_operator_review_gate_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("operator_review_gate_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_operator_review_gate_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["operator_review_gate_hash"] == packet["operator_review_gate_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_operator_review_gate_markdown() -> None:
    packet = build_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate(
        REPO_ROOT
    )
    markdown = (
        render_v2_hygiene_phase2_stabilization_subsystem_selection_operator_review_gate_markdown(
            packet
        )
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 2 Stabilization Subsystem Selection Operator Review Gate"
    )
    assert any("## Package-Lock Resolution Contract" in line for line in markdown)
    assert any("HOLD_VALIDATION_FAILED" in line for line in markdown)
    assert any("brier_resolution_authorized: False" in line for line in markdown)
