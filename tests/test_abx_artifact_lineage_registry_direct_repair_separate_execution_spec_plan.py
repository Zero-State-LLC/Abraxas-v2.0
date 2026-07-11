from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_operator_decision_record import (
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record,
)
from core.abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan import (
    BLOCKED_ACTIONS,
    build_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan,
    render_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_markdown,
    write_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan.py",
    "local_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_runner",
)


def test_spec_plan_is_deterministic_and_authorized_by_576_decision() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan()
    second = build_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan()

    assert first["spec_plan_hash"] == second["spec_plan_hash"]
    assert first["artifact_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN"
    assert first["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_SEPARATE_EXECUTION_SPEC_PLAN_READY"
    assert first["source_authorization"]["selected_decision"] == "AUTHORIZE_SEPARATE_DIRECT_REPAIR_EXECUTION_SPEC"
    assert first["source_authorization"]["spec_authoring_approved"] is True


def test_spec_plan_is_advisory_and_performs_no_repairs() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan()

    assert packet["advisory_only"] is True
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
    assert packet["downstream_status"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_spec_plan_preserves_every_required_blocked_action() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan()

    for blocked_action in BLOCKED_ACTIONS:
        assert blocked_action in packet["blocked_actions"]
    assert all(phase["execution_allowed"] is False for phase in packet["proposed_phases"])
    assert all(phase["repair_execution_performed"] is False for phase in packet["proposed_phases"])


def test_writer_runner_schema_and_markdown(tmp_path: Path) -> None:
    write_abx_artifact_lineage_registry_direct_repair_operator_decision_record(".", out_root=tmp_path)
    packet = write_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan(
        tmp_path,
        out_root=tmp_path,
    )

    json_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json"
    )
    md_path = (
        tmp_path
        / "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.md"
    )
    assert json_path.exists()
    assert md_path.exists()

    runner_packet = RUNNER.run(repo_root=tmp_path, out_root=tmp_path)
    assert runner_packet["spec_plan_hash"] == packet["spec_plan_hash"]

    schema = json.loads(
        Path(
            "contracts/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_markdown(packet)
    assert markdown[0] == "# ABX Artifact Lineage Registry Direct Repair Separate Execution Spec Plan"
    assert any("DIRECT_REGISTRY_REPAIR_EXECUTION" in line for line in markdown)


def test_registry_includes_spec_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.json"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
    assert (
        "out/operator_review/abx_artifact_lineage_registry_direct_repair_separate_execution_spec_plan_001.latest.md"
        in _DERIVED_OPTIONAL_ARTIFACTS
    )
