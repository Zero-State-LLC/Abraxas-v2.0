from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate import (
    GATE_JSON_PATH,
    HELD_STATUS,
    build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate,
    render_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate,
)
from scripts import (
    run_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate.v1.schema.json"
)
SOURCE_PLAN_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_stabilization_decision_record_emission_authorization_gate_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT
    )

    assert first["gate_hash"] == second["gate_hash"]
    assert first["status"] == HELD_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["operator_review_required"] is True
    assert first["selected_operator_decision"] == "HOLD_FOR_OPERATOR_DECISION_RECORD_EMISSION"
    assert first["selected_follow_on_action"] == "MAINTAIN_STABILIZATION_DECISION_RECORD_EMISSION_HOLD"
    assert first["planned_emission_authorization"]["record_emission_authorized"] is False
    assert first["planned_emission_authorization"]["record_emitted"] is False
    assert first["planned_emission_authorization"]["record_materialized"] is False
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False
    assert first["valid_for_execution"] is False


def test_stabilization_decision_record_emission_authorization_gate_missing_plan_returns_not_computable(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT,
        source_emission_plan_path=tmp_path / "missing_plan.json",
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert "required_emission_plan_missing" in packet["source_blockers"]
    assert packet["planned_emission_authorization"]["record_emission_authorized"] is False


def test_stabilization_decision_record_emission_authorization_gate_invalid_plan_blocks(
    tmp_path: Path,
) -> None:
    plan = _read_json(SOURCE_PLAN_PATH)
    plan["status"] = "NOT_COMPUTABLE"
    path = _write_source(tmp_path, "invalid_plan.json", plan)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT,
        source_emission_plan_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_AUTHORIZATION_GATE_BLOCKED"
    )
    assert "source_emission_plan_not_ready" in packet["source_blockers"]


def test_stabilization_decision_record_emission_authorization_gate_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    plan = _read_json(SOURCE_PLAN_PATH)
    plan["decision_record_emission_authorized"] = True
    plan["authority_locks"]["decision_record_emission"] = True
    path = _write_source(tmp_path, "authorizing_plan.json", plan)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT,
        source_emission_plan_path=path,
    )

    assert (
        packet["status"]
        == "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_EMISSION_AUTHORIZATION_GATE_BLOCKED"
    )
    assert (
        "emission_plan_authority_expanding_field:decision_record_emission_authorized"
        in packet["source_blockers"]
    )
    assert "emission_plan_authority_lock_true:decision_record_emission" in packet[
        "source_blockers"
    ]
    assert packet["decision_record_emission_authorized"] is False


def test_stabilization_decision_record_emission_authorization_gate_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT
    )

    assert packet["decision_record_created"] is False
    assert packet["decision_record_creation_authorized"] is False
    assert packet["decision_record_emitted"] is False
    assert packet["decision_record_emission_authorized"] is False
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
    assert all(value is False for value in packet["authority_locks"].values())


def test_stabilization_decision_record_emission_authorization_gate_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_stabilization_decision_record_emission_authorization_gate_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / GATE_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["gate_hash"] == packet["gate_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_stabilization_decision_record_emission_authorization_gate_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Emission Authorization Gate"
    )
    assert any("operator_review_required: True" in line for line in markdown)
    assert any("record_emission_authorized: False" in line for line in markdown)
    assert any("record_emitted: False" in line for line in markdown)
    assert any("valid_for_execution: False" in line for line in markdown)
    assert any("- none" in line for line in markdown)
