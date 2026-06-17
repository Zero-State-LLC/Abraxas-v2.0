from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt import (
    BLOCKED_STATUS,
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt,
    render_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_markdown,
    write_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt,
)
from scripts import run_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt.v1.schema.json"
)
SOURCE_RECEIPT_PLAN_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_"
    "receipt_plan_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "source_receipt_plan.json"
    write_canonical_json(path, payload)
    return path


def test_ci_frontier_hygiene_receipt_blocks_duplicate_frontier_fixture() -> None:
    packet = build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        REPO_ROOT,
        status_paths_override=[
            "tests/test_example 2.py",
            "tests/fixtures/codegen/example 2.json",
        ],
        codegen_fixture_paths_override=[
            "tests/fixtures/codegen/example.json",
            "tests/fixtures/codegen/example 2.json",
        ],
    )

    assert packet["status"] == BLOCKED_STATUS
    assert packet["sources_observed"] is True
    assert packet["ready_for_subsystem_implementation_authorization_gate"] is False
    assert "duplicate_pytest_collection_candidates_unquarantined" in packet[
        "source_blockers"
    ]
    assert "codegen_duplicate_fixture_unquarantined" in packet["source_blockers"]
    duplicate_inventory = packet["duplicate_frontier_inventory"]
    assert duplicate_inventory["duplicate_frontier_count"] == 2
    assert duplicate_inventory["duplicate_pytest_collection_candidate_count"] == 1
    assert all(
        item["collected_by_pytest_pattern"] is True
        for item in duplicate_inventory["duplicate_pytest_collection_candidates"]
    )
    fixture_inventory = packet["codegen_fixture_drift_inventory"]
    assert fixture_inventory["duplicate_fixture_count"] == 1
    assert fixture_inventory["extra_fixture_decision"] == "DUPLICATE_DERIVED_NOT_CANONICAL"
    assert fixture_inventory["duplicate_fixture_assessments"][0]["classification"] == (
        "DUPLICATE_DERIVED_FRONTIER_CONTAMINANT"
    )
    assert packet["package_lock_hygiene_finding"]["classification"] == (
        "SEPARATE_DEPENDENCY_HYGIENE_FINDING"
    )


def test_ci_frontier_hygiene_receipt_clean_inventory_can_be_ready() -> None:
    packet = build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        REPO_ROOT,
        status_paths_override=[
            "core/generated_artifact_registry.py",
            "tests/test_generated_artifact_registry.py",
        ],
        codegen_fixture_paths_override=[
            "tests/fixtures/codegen/gap_diagnosis_golden.v1.json",
            "tests/fixtures/codegen/improvement_proposal_golden.v1.json",
        ],
        package_lock_path="missing/package-lock.json",
    )

    assert packet["status"] == READY_STATUS
    assert packet["source_blockers"] == []
    assert packet["ready_for_subsystem_implementation_authorization_gate"] is True
    assert packet["duplicate_frontier_inventory"]["duplicate_frontier_count"] == 0
    assert packet["codegen_fixture_drift_inventory"]["duplicate_fixture_count"] == 0
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_ci_frontier_hygiene_receipt_source_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    source = _read_json(SOURCE_RECEIPT_PLAN_PATH)
    source["valid_for_execution"] = True
    source["authority_locks"]["execution_authority"] = True
    source_path = _write_source(tmp_path, source)

    packet = build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        REPO_ROOT,
        source_receipt_plan_path=source_path,
        status_paths_override=[],
        codegen_fixture_paths_override=[],
        package_lock_path="missing/package-lock.json",
    )

    assert packet["status"] == BLOCKED_STATUS
    assert "source_completion_validation_receipt_plan_execution_not_false" in packet[
        "source_blockers"
    ]
    assert "source_completion_validation_receipt_plan_locks_not_all_false" in packet[
        "source_blockers"
    ]
    assert "source_authority_expanding_field:valid_for_execution" in packet[
        "source_blockers"
    ]
    assert packet["valid_for_execution"] is False
    assert packet["execution_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_ci_frontier_hygiene_receipt_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        REPO_ROOT
    )

    assert packet["cleanup_authorized"] is False
    assert packet["deletion_authorized"] is False
    assert packet["duplicate_file_mutation_authorized"] is False
    assert packet["fixture_mutation_authorized"] is False
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["subsystem_implementation_authorized"] is False
    assert packet["decision_record_completion_validation_authorized"] is False
    assert packet["decision_record_completion_validation_performed"] is False
    assert packet["registry_mutation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["v2_module_registration_authorized"] is False
    assert packet["rune_registration_authorized"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_ci_frontier_hygiene_receipt_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    hygiene_receipt_hash = packet_without_hash.pop("hygiene_receipt_hash")
    assert hygiene_receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_ci_frontier_hygiene_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["hygiene_receipt_hash"] == packet["hygiene_receipt_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_ci_frontier_hygiene_receipt_markdown() -> None:
    packet = build_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Completion-Validation CI Frontier Hygiene Receipt"
    )
    assert any("## Duplicate Frontier Inventory" in line for line in markdown)
    assert any("## Codegen Fixture Drift" in line for line in markdown)
    assert any("## Package-Lock Hygiene Finding" in line for line in markdown)
