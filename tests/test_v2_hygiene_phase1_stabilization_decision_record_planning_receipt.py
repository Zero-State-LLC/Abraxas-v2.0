from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_planning_receipt import (
    PLANNING_RECEIPT_JSON_PATH,
    READY_STATUS,
    build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt,
    render_v2_hygiene_phase1_stabilization_decision_record_planning_receipt_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_planning_receipt,
)
from scripts import run_v2_hygiene_phase1_stabilization_decision_record_planning_receipt

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_planning_receipt.v1.schema.json"
)
SOURCE_GATE_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_stabilization_decision_record_planning_receipt_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT
    )

    assert first["planning_receipt_hash"] == second["planning_receipt_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["decision_record_planning_ready"] is True
    assert first["planned_decision_record"]["record_creation_allowed"] is False
    assert first["planned_decision_record"]["field_group_count"] == 5
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False
    assert first["valid_for_execution"] is False


def test_stabilization_decision_record_planning_receipt_missing_gate_returns_not_computable(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT,
        source_decision_record_gate_path=tmp_path / "missing_gate.json",
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["decision_record_planning_ready"] is False
    assert "one_or_more_required_source_artifacts_missing" in packet["source_blockers"]


def test_stabilization_decision_record_planning_receipt_invalid_gate_blocks(
    tmp_path: Path,
) -> None:
    gate = _read_json(SOURCE_GATE_PATH)
    gate["status"] = "NOT_COMPUTABLE"
    path = _write_source(tmp_path, "invalid_gate.json", gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT,
        source_decision_record_gate_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_PLANNING_RECEIPT_BLOCKED"
    )
    assert "source_decision_record_gate_not_ready" in packet["source_blockers"]
    assert packet["decision_record_planning_ready"] is False


def test_stabilization_decision_record_planning_receipt_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    gate = _read_json(SOURCE_GATE_PATH)
    gate["decision_record_creation_authorized"] = True
    gate["authority_locks"]["decision_record_creation"] = True
    path = _write_source(tmp_path, "authorizing_gate.json", gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT,
        source_decision_record_gate_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_PLANNING_RECEIPT_BLOCKED"
    )
    assert (
        "decision_record_gate_authority_expanding_field:decision_record_creation_authorized"
        in packet["source_blockers"]
    )
    assert (
        "decision_record_gate_authority_lock_true:decision_record_creation"
        in packet["source_blockers"]
    )
    assert packet["decision_record_creation_authorized"] is False


def test_stabilization_decision_record_planning_receipt_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["decision_record_creation_authorized"] is False
    assert packet["authorization_record_created"] is False
    assert packet["evidence_bundle_created"] is False
    assert packet["operator_attestation_created"] is False
    assert packet["implementation_authorized"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["runtime_mutation"] is False
    assert packet["canon_mutation"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_stabilization_decision_record_planning_receipt_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    receipt_hash = packet_without_hash.pop("planning_receipt_hash")
    assert receipt_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_stabilization_decision_record_planning_receipt_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLANNING_RECEIPT_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_planning_receipt.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["planning_receipt_hash"] == packet["planning_receipt_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_stabilization_decision_record_planning_receipt_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_planning_receipt(
        REPO_ROOT
    )
    markdown = (
        render_v2_hygiene_phase1_stabilization_decision_record_planning_receipt_markdown(
            packet
        )
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Planning Receipt"
    )
    assert any("decision_record_planning_ready: True" in line for line in markdown)
    assert any("record_creation_allowed: False" in line for line in markdown)
    assert any("valid_for_execution: False" in line for line in markdown)
    assert any("- none" in line for line in markdown)
