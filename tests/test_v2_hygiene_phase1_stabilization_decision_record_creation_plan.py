from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_creation_plan import (
    PLAN_JSON_PATH,
    READY_STATUS,
    build_v2_hygiene_phase1_stabilization_decision_record_creation_plan,
    render_v2_hygiene_phase1_stabilization_decision_record_creation_plan_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_creation_plan,
)
from scripts.hygiene import run_v2_hygiene_phase1_stabilization_decision_record_creation_plan

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_plan.v1.schema.json"
)
SOURCE_GATE_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_creation_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_stabilization_decision_record_creation_plan_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT
    )

    assert first["plan_hash"] == second["plan_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["decision_record_creation_plan_ready"] is True
    assert first["planned_creation"]["field_group_count"] == 5
    assert first["planned_creation"]["record_creation_allowed"] is False
    assert first["planned_creation"]["requires_separate_creation_authorization"] is True
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False
    assert first["valid_for_execution"] is False


def test_stabilization_decision_record_creation_plan_missing_gate_returns_not_computable(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT,
        source_creation_gate_path=tmp_path / "missing_gate.json",
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["decision_record_creation_plan_ready"] is False
    assert "one_or_more_required_source_artifacts_missing" in packet["source_blockers"]


def test_stabilization_decision_record_creation_plan_invalid_gate_blocks(
    tmp_path: Path,
) -> None:
    gate = _read_json(SOURCE_GATE_PATH)
    gate["status"] = "NOT_COMPUTABLE"
    path = _write_source(tmp_path, "invalid_gate.json", gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT,
        source_creation_gate_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_PLAN_BLOCKED"
    )
    assert "source_creation_gate_not_eligible" in packet["source_blockers"]
    assert packet["decision_record_creation_plan_ready"] is False


def test_stabilization_decision_record_creation_plan_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    gate = _read_json(SOURCE_GATE_PATH)
    gate["decision_record_creation_authorized"] = True
    gate["authority_locks"]["decision_record_creation"] = True
    path = _write_source(tmp_path, "authorizing_gate.json", gate)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT,
        source_creation_gate_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_CREATION_PLAN_BLOCKED"
    )
    assert (
        "creation_gate_authority_expanding_field:decision_record_creation_authorized"
        in packet["source_blockers"]
    )
    assert "creation_gate_authority_lock_true:decision_record_creation" in packet[
        "source_blockers"
    ]
    assert packet["decision_record_creation_authorized"] is False


def test_stabilization_decision_record_creation_plan_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
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


def test_stabilization_decision_record_creation_plan_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    plan_hash = packet_without_hash.pop("plan_hash")
    assert plan_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_stabilization_decision_record_creation_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / PLAN_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_creation_plan.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["plan_hash"] == packet["plan_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_stabilization_decision_record_creation_plan_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_creation_plan(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_creation_plan_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Creation Plan"
    )
    assert any("decision_record_creation_plan_ready: True" in line for line in markdown)
    assert any("record_creation_allowed: False" in line for line in markdown)
    assert any("valid_for_execution: False" in line for line in markdown)
    assert any("- none" in line for line in markdown)
