from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt import (
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt,
    render_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_markdown,
    write_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt,
)
from scripts.hygiene import run_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt.v1.schema.json"
)
SOURCE_HYGIENE_RECEIPT_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_completion_validation_ci_frontier_hygiene_receipt_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "source_hygiene_receipt.json"
    write_canonical_json(path, payload)
    return path


def _hygiene_source_payload() -> dict:
    return {
        "status": (
            "V2_HYGIENE_PHASE1_COMPLETION_VALIDATION_CI_FRONTIER_HYGIENE_RECEIPT_"
            "BLOCKED_BY_UNQUARANTINED_FRONTIER_DRIFT"
        ),
        "ready_for_subsystem_implementation_authorization_gate": False,
        "recommended_next_lane": "NOT_COMPUTABLE",
        "downstream": "NOT_COMPUTABLE",
        "authority_locks": {"execution_authority": False},
        "hygiene_receipt_hash": "0" * 64,
    }


def test_quarantine_design_receipt_emits_manifest_from_fixture(
    tmp_path: Path,
) -> None:
    paths = [
        ("tests/test_example 2.py", "tests/test_example.py"),
        ("tests/fixtures/codegen/example 2.json", "tests/fixtures/codegen/example.json"),
        ("out/audit/example.latest 2.md", "out/audit/example.latest.md"),
        ("core/example 2.py", "core/example.py"),
    ]
    for duplicate, canonical in paths:
        duplicate_path = tmp_path / duplicate
        canonical_path = tmp_path / canonical
        duplicate_path.parent.mkdir(parents=True, exist_ok=True)
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        duplicate_path.write_text("same\n", encoding="utf-8")
        canonical_path.write_text("same\n", encoding="utf-8")
    source = _write_source(tmp_path, _hygiene_source_payload())

    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        tmp_path,
        source_hygiene_receipt_path=source,
        status_paths_override=[duplicate for duplicate, _canonical in paths],
    )

    assert packet["status"] == READY_STATUS
    assert packet["sources_observed"] is True
    assert packet["source_blockers"] == []
    assert packet["ready_for_subsystem_implementation_authorization_gate"] is False
    summary = packet["duplicate_manifest_summary"]
    assert summary["duplicate_manifest_count"] == 4
    assert summary["pytest_collectable_count"] == 1
    assert summary["fixture_impact_count"] == 1
    assert summary["by_category"]["pytest_candidate"] == 1
    assert summary["by_category"]["codegen_fixture"] == 1
    assert summary["by_classification"]["PYTEST_COLLECTION_BLOCKER"] == 1
    assert summary["by_classification"]["CODEGEN_FIXTURE_BLOCKER"] == 1


def test_quarantine_design_manifest_classifies_path_examples(tmp_path: Path) -> None:
    paths = [
        (
            "tests/test_abx_codegen_intelligence_spine_packet_validation_receipt 2.py",
            "tests/test_abx_codegen_intelligence_spine_packet_validation_receipt.py",
        ),
        (
            "tests/fixtures/codegen/invalid_improvement_proposal_missing_operator_decision.v1 2.json",
            "tests/fixtures/codegen/invalid_improvement_proposal_missing_operator_decision.v1.json",
        ),
        (
            "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest 2.md",
            "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest.md",
        ),
    ]
    for duplicate, canonical in paths:
        duplicate_path = tmp_path / duplicate
        canonical_path = tmp_path / canonical
        duplicate_path.parent.mkdir(parents=True, exist_ok=True)
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        duplicate_path.write_text("same\n", encoding="utf-8")
        canonical_path.write_text("same\n", encoding="utf-8")
    source = _write_source(tmp_path, _hygiene_source_payload())

    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        tmp_path,
        source_hygiene_receipt_path=source,
        status_paths_override=[duplicate for duplicate, _canonical in paths],
    )
    records = {item["path"]: item for item in packet["duplicate_manifest"]}

    test_record = records[
        "tests/test_abx_codegen_intelligence_spine_packet_validation_receipt 2.py"
    ]
    assert test_record["classification"] == "PYTEST_COLLECTION_BLOCKER"
    assert test_record["pytest_collectable"] is True
    assert test_record["risk_level"] == "HIGH"

    fixture_record = records[
        "tests/fixtures/codegen/invalid_improvement_proposal_missing_operator_decision.v1 2.json"
    ]
    assert fixture_record["classification"] == "CODEGEN_FIXTURE_BLOCKER"
    assert fixture_record["fixture_impact"] is True
    assert fixture_record["canonical_counterpart_observed"] is True

    generated_record = records[
        "out/audit/abx_codegen_intelligence_spine_packet_validation_receipt_001.latest 2.md"
    ]
    assert generated_record["classification"] == "GENERATED_OUTPUT_DUPLICATE"


def test_quarantine_design_receipt_source_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    source = _read_json(SOURCE_HYGIENE_RECEIPT_PATH)
    source["safe_to_auto_continue"] = True
    source["authority_locks"]["execution_authority"] = True
    source_path = _write_source(tmp_path, source)

    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        REPO_ROOT,
        source_hygiene_receipt_path=source_path,
        status_paths_override=[
            "tests/test_example 2.py",
        ],
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert "source_authority_expanding_field:safe_to_auto_continue" in packet[
        "source_blockers"
    ]
    assert "source_authority_locks_not_all_false" in packet["source_blockers"]
    assert packet["safe_to_auto_continue"] is False
    assert packet["execution_authority"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_quarantine_design_receipt_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        REPO_ROOT
    )

    assert packet["cleanup_authorized"] is False
    assert packet["deletion_authorized"] is False
    assert packet["file_movement_authorized"] is False
    assert packet["quarantine_execution_authorized"] is False
    assert packet["duplicate_file_mutation_authorized"] is False
    assert packet["gitignore_mutation_authorized"] is False
    assert packet["pytest_configuration_mutation_authorized"] is False
    assert packet["fixture_mutation_authorized"] is False
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["subsystem_implementation_authorized"] is False
    assert packet["completion_validation_execution_authorized"] is False
    assert packet["decision_record_completion_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_quarantine_design_brier_and_rune_contracts_are_non_authoritative() -> None:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        REPO_ROOT
    )
    brier = packet["planned_brier_scoring_contract"]
    runes = packet["planned_rune_governance_mapping"]

    assert brier["telemetry_only"] is True
    assert brier["brier_score_formula"] == "(forecast_probability - binary_outcome)^2"
    assert brier["resolution_allowed"] is False
    assert brier["adaptive_learning_authorized"] is False
    assert brier["forecast_routing_authorized"] is False
    assert {item["rune"] for item in runes} == {
        "Observe",
        "Bind",
        "Hold",
        "Sever",
        "Seal",
    }
    assert all(item["authority_granted"] is False for item in runes)


def test_quarantine_design_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("quarantine_design_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_quarantine_design_runner_writes_stable_outputs(tmp_path: Path) -> None:
    packet = write_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["quarantine_design_receipt_hash"] == packet[
        "quarantine_design_receipt_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_quarantine_design_markdown() -> None:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_duplicate_frontier_quarantine_design_receipt_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Duplicate Frontier Quarantine Design Receipt"
    )
    assert any("## Duplicate Manifest Summary" in line for line in markdown)
    assert any("## Repair Playbook" in line for line in markdown)
    assert any("## Brier Telemetry Contract" in line for line in markdown)
