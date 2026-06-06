from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_approval_plan import (
    build_abx_artifact_lineage_registry_direct_repair_approval_plan,
    render_markdown,
    write_abx_artifact_lineage_registry_direct_repair_approval_plan,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_approval_plan.py",
    "local_abx_artifact_lineage_registry_direct_repair_approval_plan_runner",
)


def test_approval_plan_id_and_source_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_approval_plan()
    assert packet["approval_plan_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_PLAN_001"
    assert packet["source_validation_dry_run"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_DRY_RUN_001"
    assert packet["source_validation_dry_run_observed"] is True


def test_approval_plan_is_ready_and_fail_closed() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_approval_plan()
    assert packet["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_PLAN_READY"
    assert packet["recommended_next_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_DRY_RUN_001"
    assert packet["validation_passed"] is True
    assert packet["approval_granted"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_repair"] is False
    assert packet["valid_for_execution"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_requirements_and_constraints_are_present() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_approval_plan()
    assert packet["required_operator_acknowledgements"]
    assert packet["required_operator_approval_fields"]
    assert packet["approval_constraints"]
    assert packet["approval_provenance_requirements"]
    assert packet["approval_hash_requirements"]
    assert len(packet["ready_workstreams"]) == 3


def test_schema_and_markdown_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_approval_plan()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_direct_repair_approval_plan.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_PLAN_001" in markdown
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_APPROVAL_DRY_RUN_001" in markdown


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_approval_plan()
    second = build_abx_artifact_lineage_registry_direct_repair_approval_plan()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.md"
    packet = write_abx_artifact_lineage_registry_direct_repair_approval_plan(json_path, md_path)
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]


def test_registry_includes_approval_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/sync/abx_artifact_lineage_registry_direct_repair_approval_plan/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
