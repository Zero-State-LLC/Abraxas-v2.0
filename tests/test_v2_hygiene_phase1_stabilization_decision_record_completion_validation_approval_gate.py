from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate import (
    GATE_JSON_PATH,
    READY_STATUS,
    build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate,
    render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_markdown,
    write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate,
)
from scripts import (
    run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    "contracts/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate.v1.schema.json"
)
SOURCE_PLAN_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_plan_001.latest.json"
)
SOURCE_AUTHORIZATION_GATE_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_authorization_gate_001.latest.json"
)
SOURCE_APPROVAL_INTAKE_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.json"
)


def _read_json(path: str | Path) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _write_source(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    write_canonical_json(path, payload)
    return path


def test_completion_validation_approval_gate_ready_path_is_stable() -> None:
    first = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT
    )
    second = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT
    )

    assert first["gate_hash"] == second["gate_hash"]
    assert first["status"] == READY_STATUS
    assert first["source_readiness"] == "SOURCE_ARTIFACTS_READY"
    assert first["source_blockers"] == []
    assert first["completion_validation_approval_gate_ready"] is True
    assert first["selected_follow_on_action"] == (
        "PLAN_SEPARATE_GOVERNED_RECORD_COMPLETION_VALIDATION"
    )
    planned = first["planned_record_completion_validation"]
    assert planned["record_completion_validation_allowed"] is False
    assert planned["record_completion_validation_authorized"] is False
    assert planned["record_completion_validation_performed"] is False
    assert planned["record_completed"] is False
    assert planned["record_finalized"] is False
    assert first["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert first["safe_to_auto_continue"] is False
    assert first["valid_for_execution"] is False


def test_completion_validation_approval_gate_missing_intake_returns_not_computable(
    tmp_path: Path,
) -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT,
        source_completion_validation_approval_intake_gate_path=tmp_path / "missing.json",
    )

    assert packet["status"] == "NOT_COMPUTABLE"
    assert packet["completion_validation_approval_gate_ready"] is False
    assert "required_completion_validation_approval_intake_missing" in packet[
        "source_blockers"
    ]
    assert packet["decision_record_completion_validation_performed"] is False


def test_completion_validation_approval_gate_invalid_intake_blocks(
    tmp_path: Path,
) -> None:
    intake = _read_json(SOURCE_APPROVAL_INTAKE_PATH)
    intake["status"] = "NOT_COMPUTABLE"
    path = _write_source(tmp_path, "invalid_intake.json", intake)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT,
        source_completion_validation_approval_intake_gate_path=path,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "APPROVAL_GATE_BLOCKED"
    )
    assert "source_completion_validation_approval_intake_not_validated" in packet[
        "source_blockers"
    ]
    assert packet["completion_validation_approval_gate_ready"] is False


def test_completion_validation_approval_gate_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    intake = _read_json(SOURCE_APPROVAL_INTAKE_PATH)
    intake["decision_record_completion_validation_authorized"] = True
    intake["authority_locks"]["decision_record_completion_validation"] = True
    path = _write_source(tmp_path, "authorizing_intake.json", intake)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT,
        source_completion_validation_approval_intake_gate_path=path,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "APPROVAL_GATE_BLOCKED"
    )
    assert (
        "completion_validation_approval_intake_authority_expanding_field:"
        "decision_record_completion_validation_authorized"
    ) in packet["source_blockers"]
    assert (
        "completion_validation_approval_intake_authority_lock_true:"
        "decision_record_completion_validation"
    ) in packet["source_blockers"]
    assert packet["decision_record_completion_validation_authorized"] is False
    assert packet["decision_record_completion_validation_performed"] is False


def test_completion_validation_approval_gate_plan_authority_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    plan = _read_json(SOURCE_PLAN_PATH)
    plan["valid_for_decision_record_completion_validation"] = True
    plan["authority_locks"]["decision_record_completion_validation"] = True
    path = _write_source(tmp_path, "authorizing_plan.json", plan)

    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT,
        source_completion_validation_plan_path=path,
    )

    assert packet["status"] == (
        "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_"
        "APPROVAL_GATE_BLOCKED"
    )
    assert "completion_validation_plan_authority_expanding_field:valid_for_decision_record_completion_validation" in packet[
        "source_blockers"
    ]
    assert (
        "completion_validation_plan_authority_lock_true:"
        "decision_record_completion_validation"
    ) in packet["source_blockers"]
    assert packet["valid_for_decision_record_completion_validation"] is False


def test_completion_validation_approval_gate_preserves_authority_denials() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
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
    assert all(value is False for value in packet["authority_locks"].values())


def test_completion_validation_approval_gate_schema_and_hash_are_stable() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT
    )
    packet_without_hash = dict(packet)
    gate_hash = packet_without_hash.pop("gate_hash")
    assert gate_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_completion_validation_approval_gate_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    packet = write_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT,
        out_root=tmp_path,
    )
    out_json = tmp_path / GATE_JSON_PATH
    out_md = out_json.with_suffix(".md")
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate.run(
        repo_root=REPO_ROOT,
        out_root=tmp_path,
    )

    assert second["gate_hash"] == packet["gate_hash"]
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_completion_validation_approval_gate_markdown() -> None:
    packet = build_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate(
        REPO_ROOT
    )
    markdown = render_v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_markdown(
        packet
    )

    assert markdown[0] == (
        "# v2.0 Hygiene Phase 1 Stabilization Decision-Record Completion Validation Approval Gate"
    )
    assert any("completion_validation_approval_gate_ready: True" in line for line in markdown)
    assert any("record_completion_validation_allowed: False" in line for line in markdown)
    assert any(
        "record_completion_validation_authorized: False" in line for line in markdown
    )
    assert any("record_completion_validation_performed: False" in line for line in markdown)
    assert any("record_completed: False" in line for line in markdown)
    assert any("record_finalized: False" in line for line in markdown)
    assert any("valid_for_execution: False" in line for line in markdown)
    assert any("- none" in line for line in markdown)
