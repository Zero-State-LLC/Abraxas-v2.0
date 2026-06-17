from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt import (
    READY_STATUS,
    RECEIPT_JSON_PATH,
    build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt,
    render_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_markdown,
    write_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt,
)
from scripts import run_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt.v1.schema.json"
)


def _source_payload(duplicate_path: str, counterpart_path: str, digest: str) -> dict:
    return {
        "status": "V2_HYGIENE_PHASE1_DUPLICATE_FRONTIER_QUARANTINE_DESIGN_RECEIPT_READY",
        "ready_for_subsystem_implementation_authorization_gate": False,
        "recommended_next_lane": "NOT_COMPUTABLE",
        "downstream": "NOT_COMPUTABLE",
        "authority_locks": {"execution_authority": False},
        "quarantine_design_receipt_hash": "0" * 64,
        "duplicate_manifest": [
            {
                "path": duplicate_path,
                "canonical_counterpart": counterpart_path,
                "classification": "SAFE_DUPLICATE_CANDIDATE",
                "duplicate_hash": digest,
                "canonical_counterpart_hash": digest,
            }
        ],
    }


def _write_source(root: Path, payload: dict) -> Path:
    path = root / "source_design_receipt.json"
    write_canonical_json(path, payload)
    return path


def test_repair_execution_deletes_only_eligible_duplicate(tmp_path: Path) -> None:
    canonical = tmp_path / "tests/example.py"
    duplicate = tmp_path / "tests/example 2.py"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("print('same')\n", encoding="utf-8")
    duplicate.write_text("print('same')\n", encoding="utf-8")
    digest = "not-used-by-builder"
    source = _write_source(
        tmp_path,
        _source_payload("tests/example 2.py", "tests/example.py", digest),
    )

    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        tmp_path,
        source_design_receipt_path=source,
        execute_repair=True,
    )

    assert packet["status"] == READY_STATUS
    assert duplicate.exists() is False
    assert canonical.exists() is True
    assert packet["repair_performed"] is True
    assert packet["repair_summary"]["deleted_path_count"] == 1
    assert packet["ready_for_subsystem_implementation_authorization_gate"] is False


def test_repair_execution_is_stable_after_duplicate_already_absent(tmp_path: Path) -> None:
    canonical = tmp_path / "tests/example.py"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("print('same')\n", encoding="utf-8")
    source = _write_source(
        tmp_path,
        _source_payload("tests/example 2.py", "tests/example.py", "ignored"),
    )

    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        tmp_path,
        source_design_receipt_path=source,
        execute_repair=True,
    )

    assert packet["status"] == READY_STATUS
    assert packet["repair_already_complete_before_run"] is False
    assert packet["repair_performed"] is True
    assert packet["repair_summary"]["deleted_path_count"] == 1
    assert packet["held_paths"] == []


def test_repair_execution_aborts_on_non_equal_duplicate(tmp_path: Path) -> None:
    canonical = tmp_path / "tests/example.py"
    duplicate = tmp_path / "tests/example 2.py"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("print('canonical')\n", encoding="utf-8")
    duplicate.write_text("print('duplicate')\n", encoding="utf-8")
    source = _write_source(
        tmp_path,
        _source_payload("tests/example 2.py", "tests/example.py", "ignored"),
    )

    with pytest.raises(ValueError, match="preflight failed"):
        build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
            tmp_path,
            source_design_receipt_path=source,
            execute_repair=True,
        )
    assert duplicate.exists() is True


def test_repair_execution_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        REPO_ROOT,
        execute_repair=False,
    )

    assert packet["canonical_file_mutation_authorized"] is False
    assert packet["tracked_file_deletion_authorized"] is False
    assert packet["non_manifest_file_deletion_authorized"] is False
    assert packet["package_lock_mutation_authorized"] is False
    assert packet["gitignore_mutation_authorized"] is False
    assert packet["pytest_configuration_mutation_authorized"] is False
    assert packet["dependency_file_mutation_authorized"] is False
    assert packet["subsystem_implementation_authorized"] is False
    assert packet["completion_validation_execution_authorized"] is False
    assert packet["decision_record_completion_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["valid_for_execution"] is False


def test_repair_execution_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        REPO_ROOT,
        execute_repair=False,
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("repair_execution_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_repair_execution_runner_writes_stable_outputs(tmp_path: Path) -> None:
    canonical = tmp_path / "tests/example.py"
    duplicate = tmp_path / "tests/example 2.py"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("print('same')\n", encoding="utf-8")
    duplicate.write_text("print('same')\n", encoding="utf-8")
    source = _write_source(
        tmp_path,
        _source_payload("tests/example 2.py", "tests/example.py", "ignored"),
    )

    packet = write_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        tmp_path,
        out_root=tmp_path,
        source_design_receipt_path=source,
        execute_repair=True,
    )
    out_json = tmp_path / RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt.run(
        repo_root=tmp_path,
        out_root=tmp_path,
        source_design_receipt_path=source,
        execute_repair=True,
    )

    assert second["repair_execution_receipt_hash"] == packet[
        "repair_execution_receipt_hash"
    ]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_repair_execution_markdown() -> None:
    packet = build_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt(
        REPO_ROOT,
        execute_repair=False,
    )
    markdown = render_v2_hygiene_phase1_duplicate_frontier_quarantine_repair_execution_receipt_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Duplicate Frontier Quarantine Repair Execution Receipt"
    )
    assert any("## Repair Summary" in line for line in markdown)
    assert any("## Validation Plan" in line for line in markdown)
