from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_execution_authorization_gate import (
    write_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate,
)
from core.abx_artifact_lineage_registry_direct_repair_execution_authorization_record import (
    BLOCKED_ACTIONS,
    SCOPED_REPAIR_ACTIONS,
    build_abx_artifact_lineage_registry_direct_repair_execution_authorization_record,
    render_abx_artifact_lineage_registry_direct_repair_execution_authorization_record_markdown,
    write_abx_artifact_lineage_registry_direct_repair_execution_authorization_record,
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
    "scripts/run_abx_artifact_lineage_registry_direct_repair_execution_authorization_record.py",
    "local_abx_artifact_lineage_registry_direct_repair_execution_authorization_record_runner",
)


def test_authorization_record_is_deterministic_and_granted_for_scoped_pr() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_record()
    second = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_record()

    assert first["authorization_record_hash"] == second["authorization_record_hash"]
    assert first["artifact_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD"
    assert (
        first["status"]
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_EXECUTION_AUTHORIZATION_RECORD_CONSUMED_BY_SCOPED_EXECUTION_RECEIPT"
    )
    assert first["source_authorization_gate"]["source_gate_ready"] is True
    assert first["operator_authorization"]["operator_instruction_observed"] == "authorize"
    assert first["authorization_granted"] is True
    assert first["scoped_execution_receipt"]["observed"] is True
    assert first["safe_to_prepare_execution_pr"] is False


def test_authorization_record_does_not_perform_repairs_or_expand_scope() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_record()

    assert packet["authorization_record_only"] is True
    assert packet["execution_authority"] is True
    assert packet["execution_allowed"] is False
    assert packet["repair_execution_performed"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_repair"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["safe_to_prepare_execution_pr"] is False
    assert packet["runtime_mutation_allowed"] is False
    assert packet["canon_mutation_allowed"] is False
    assert packet["queue_mutation_allowed"] is False
    assert packet["notion_completeness_claim_allowed"] is False
    assert packet["runner_casing_policy_override_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["downstream_status"] == "SCOPED_EXECUTION_RECEIPT_OBSERVED"
    assert packet["recommended_next_lane"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REGENERATION"


def test_authorization_record_preserves_scope_boundaries() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_execution_authorization_record()

    for action in SCOPED_REPAIR_ACTIONS:
        assert action in packet["scoped_repair_actions"]
    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]
    assert packet["operator_authorization"]["runner_casing_policy_decision"] == "NO_RUNNER_CASING_POLICY_OVERRIDE_AUTHORIZED"
    assert (
        packet["operator_authorization"]["notion_mapping_evidence_disposition"]
        == "NO_NOTION_MAPPING_COMPLETENESS_CLAIM_AUTHORIZED"
    )


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record(".", out_root=tmp_path)
    write_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan(tmp_path, out_root=tmp_path)
    write_abx_artifact_lineage_registry_direct_repair_execution_authorization_gate(tmp_path, out_root=tmp_path)
    packet = write_abx_artifact_lineage_registry_direct_repair_execution_authorization_record(
        tmp_path,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["authorization_record_hash"] == packet["authorization_record_hash"]

    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_execution_authorization_record_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Execution Authorization Record"
    assert any("DIRECT_REGISTRY_REPAIR_EXECUTION_PR_PREPARATION" in line for line in markdown)


def test_registry_includes_authorization_record_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_execution_authorization_record_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
