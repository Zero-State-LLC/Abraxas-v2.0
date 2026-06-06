from __future__ import annotations

import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.abx_artifact_lineage_registry_direct_repair_implementation_dry_run import (
    build_abx_artifact_lineage_registry_direct_repair_implementation_dry_run,
)
from tests.script_runner_loader import load_script_runner

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = load_script_runner(
    REPO_ROOT,
    "Scripts/run_abx_artifact_lineage_registry_direct_repair_implementation_dry_run.py",
    "local_abx_artifact_lineage_registry_direct_repair_implementation_dry_run_runner",
)
SCHEMA_PATH = (
    "contracts/canon/abx_artifact_lineage_registry_direct_repair_implementation_dry_run.v1.schema.json"
)


def test_dry_run_is_advisory_only_and_fail_closed() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_dry_run(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "AbxArtifactLineageRegistryDirectRepairImplementationDryRun.v1"
    assert (
        packet["dry_run_status"]
        == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_IMPLEMENTATION_DRY_RUN_READY"
    )
    assert packet["recommended_next_plan"] == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_VALIDATION_PLAN_001"
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["safe_to_prepare_implementation_pr"] is False
    assert packet["repair_execution_performed"] is False
    assert packet["implementation_authorized"] is False
    assert packet["execution_authority"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["valid_for_repair"] is False
    assert packet["valid_for_execution"] is False


def test_dry_run_simulates_three_workstream_runs() -> None:
    packet = build_abx_artifact_lineage_registry_direct_repair_implementation_dry_run(repo_root=REPO_ROOT)

    assert packet["source_implementation_plan_observed"] is True
    assert packet["source_batch_observed"] is True
    assert packet["simulated_workstream_count"] == 3
    assert [run["phase_id"] for run in packet["simulated_workstream_runs"]] == [
        "DIRECT-IMPL-001",
        "DIRECT-IMPL-002",
        "DIRECT-IMPL-003",
    ]
    assert all(run["simulated_only"] is True for run in packet["simulated_workstream_runs"])
    assert all(run["repo_mutation_performed"] is False for run in packet["simulated_workstream_runs"])


def test_dry_run_schema_and_hash_are_stable() -> None:
    first = build_abx_artifact_lineage_registry_direct_repair_implementation_dry_run(repo_root=REPO_ROOT)
    second = build_abx_artifact_lineage_registry_direct_repair_implementation_dry_run(repo_root=REPO_ROOT)

    assert first == second
    packet_without_hash = dict(first)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(first, schema)


def test_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.json"
    out_md = tmp_path / "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.md"

    first = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = RUNNER.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert out_json.read_text(encoding="utf-8") == first_json
    assert out_md.read_text(encoding="utf-8") == first_md


def test_registry_includes_dry_run_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/sync/abx_artifact_lineage_registry_direct_repair_implementation_dry_run/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
