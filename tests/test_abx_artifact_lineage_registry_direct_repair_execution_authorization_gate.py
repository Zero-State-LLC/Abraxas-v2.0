from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_execution_authorization_gate import (
    BLOCKED_ACTIONS,
    build_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate,
    render_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_markdown,
    write_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate,
)
from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record import (
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record,
)
from core.abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan import (
    write_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate.py",
    "local_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_runner",
)


def test_authorization_gate_is_deterministic_and_held_for_operator() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate()
    second = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate()

    assert first["authorization_gate_hash"] == second["authorization_gate_hash"]
    assert first["artifact_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE"
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
    assert first["source_spec_plan"]["source_spec_plan_ready"] is True
    assert first["operator_authorization_required"] is True
    assert first["operator_authorization_observed"] is False


def test_authorization_gate_denies_execution_and_repair_authority() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate()

    assert packet["advisory_only"] is True
    assert packet["authorization_gate_only"] is True
    assert packet["authorization_granted"] is False
    assert packet["execution_authority"] is False
    assert packet["execution_allowed"] is False
    assert packet["repair_execution_performed"] is False
    assert packet["implementation_authorized"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["notion_completeness_claim_allowed"] is False
    assert packet["runner_casing_policy_override_allowed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_repair"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["safe_to_prepare_execution_pr"] is False
    assert packet["downstream_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_authorization_gate_preserves_blocked_actions_and_required_fields() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate()

    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]
    assert "authorization_scope_acknowledged" in packet["required_operator_authorization_fields"]
    assert "runner_casing_policy_decision" in packet["required_operator_authorization_fields"]
    assert "notion_mapping_evidence_disposition" in packet["required_operator_authorization_fields"]


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record(".", out_root=tmp_path)
    write_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan(tmp_path, out_root=tmp_path)
    packet = write_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate(
        tmp_path,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["authorization_gate_hash"] == packet["authorization_gate_hash"]

    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Execution Authorization Gate"
    assert any("EXECUTION_AUTHORITY_GRANT_WITHOUT_OPERATOR_RECORD" in line for line in markdown)


def test_registry_includes_authorization_gate_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_gate_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
