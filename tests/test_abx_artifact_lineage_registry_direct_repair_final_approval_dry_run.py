from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.abx_artifact_lineage_registry_direct_repair_final_approval_dry_run import (
    build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run,
    render_markdown,
    write_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "scripts/run_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run.py",
    "local_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run_runner",
)


def test_dry_run_id_and_source_are_exact() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run()
    assert packet["dry_run_id"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_DRY_RUN_001"
    assert packet["source_final_approval_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_PLAN_001"
    assert packet["source_final_approval_plan_observed"] is True


def test_final_approval_dry_run_is_ready_and_fail_closed() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run()
    assert packet["status"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_DRY_RUN_READY"
    assert packet["recommended_next_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_VALIDATION_PLAN_001"
    assert packet["final_approval_ready"] is True
    assert packet["approval_granted"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_repair"] is False
    assert packet["valid_for_execution"] is False
    assert packet["downstream"] == "NOT_COMPUTABLE"


def test_simulated_final_approval_execution_stays_non_authoritative() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run()
    execution = packet["simulated_final_approval_execution"]
    assert execution["simulated_only"] is True
    assert execution["operator_input_required"] is True
    assert execution["final_approval_ready"] is True
    assert execution["approval_authority_granted"] is False
    assert execution["repair_authority_granted"] is False
    assert execution["execution_authority_granted"] is False
    assert execution["final_approval_blockers"] == []


def test_schema_and_markdown_validation_pass() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run()
    schema = json.loads(
        Path(
            "contracts/canon/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    validate(packet, schema)
    markdown = render_markdown(packet)
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_DRY_RUN_001" in markdown
    assert "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_FINAL_APPROVAL_VALIDATION_PLAN_001" in markdown


def test_output_is_deterministic() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run()
    second = build_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run()
    assert first == second


def test_writer_and_runner_emit_outputs(tmp_path: Path) -> None:
    json_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.json"
    md_path = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.md"
    packet = write_abx_artifact_lineage_registry_direct_repair_final_approval_dry_run(json_path, md_path)
    assert json_path.exists()
    assert md_path.exists()
    runner_packet = RUNNER.run(repo_root=REPO_ROOT, out_json=json_path, out_md=md_path)
    assert runner_packet["packet_hash"] == packet["packet_hash"]


def test_registry_includes_final_approval_dry_run_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/sync/abx_artifact_lineage_registry_direct_repair_final_approval_dry_run/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
