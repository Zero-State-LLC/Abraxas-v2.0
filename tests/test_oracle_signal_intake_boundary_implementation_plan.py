from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.oracle_signal_intake_boundary_alignment_plan import (
    build_oracle_signal_intake_boundary_alignment_plan,
    write_oracle_signal_intake_boundary_alignment_plan,
)
from core.sync.oracle_signal_intake_boundary_implementation_plan import (
    PATCH_ID,
    build_oracle_signal_intake_boundary_implementation_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/oracle_signal_intake_boundary_implementation_plan.v1.schema.json"


def _seed_implementation_repo(tmp_path: Path) -> Path:
    write_canonical_json(
        tmp_path / "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json",
        {
            "artifact_type": "GlobalIngestAdapterSpineAlignmentPlan.v1",
            "plan_status": "ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY",
        },
    )
    for rel_path in (
        "scripts/run_oracle_intake.py",
        "core/oracle/runtime.py",
        "core/oracle/intake.py",
        "contracts/ingest/oracle_intake_queue.v1.schema.json",
        "out/ingest/oracle_intake_queue_001.latest.json",
    ):
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("stub", encoding="utf-8")
    alignment_packet = build_oracle_signal_intake_boundary_alignment_plan(repo_root=tmp_path)
    write_oracle_signal_intake_boundary_alignment_plan(
        tmp_path / "out/sync/oracle_signal_intake_boundary_alignment_plan/latest.json",
        alignment_packet,
    )
    return tmp_path


def _load_runner_module():
    runner_path = REPO_ROOT / "scripts/run_oracle_signal_intake_boundary_implementation_plan.py"
    spec = importlib.util.spec_from_file_location(
        "local_oracle_signal_intake_boundary_implementation_plan_runner",
        runner_path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_implementation_plan_is_advisory_only_and_fail_closed(tmp_path: Path) -> None:
    packet = build_oracle_signal_intake_boundary_implementation_plan(repo_root=_seed_implementation_repo(tmp_path))

    assert packet["artifact_type"] == "OracleSignalIntakeBoundaryImplementationPlan.v1"
    assert packet["plan_status"] == "IMPLEMENTATION_PLAN_EMITTED_ADVISORY_ONLY"
    assert packet["patch_id"] == PATCH_ID
    assert packet["safe_to_prepare_planning_pr"] is True
    assert packet["safe_to_prepare_implementation_pr"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["implementation_allowed"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["queue_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False


def test_implementation_plan_preserves_legacy_surfaces_and_plans_missing_boundary_paths(tmp_path: Path) -> None:
    packet = build_oracle_signal_intake_boundary_implementation_plan(repo_root=_seed_implementation_repo(tmp_path))

    assert packet["preserved_legacy_surfaces"] == [
        "scripts/run_oracle_intake.py",
        "core/oracle/runtime.py",
        "core/oracle/intake.py",
        "contracts/ingest/oracle_intake_queue.v1.schema.json",
        "out/ingest/oracle_intake_queue_001.latest.json",
    ]
    assert packet["planned_contract_paths"] == [
        "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
        "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
        "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
    ]
    assert packet["planned_runner_paths"] == ["scripts/run_oracle_signal_intake_boundary.py"]
    assert packet["missing_boundary_paths"] == [
        "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
        "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
        "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
        "scripts/run_oracle_signal_intake_boundary.py",
    ]
    assert packet["implemented_boundary_paths"] == []
    assert packet["all_boundary_paths_observed"] is False
    assert packet["planning_pr_consumed"] is False
    assert packet["recommended_next_patch"] == PATCH_ID


def test_implementation_plan_marks_planning_pr_consumed_when_boundary_paths_exist(tmp_path: Path) -> None:
    repo_root = _seed_implementation_repo(tmp_path)
    for rel_path in (
        "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
        "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
        "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
        "scripts/run_oracle_signal_intake_boundary.py",
    ):
        path = repo_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("stub", encoding="utf-8")
    alignment_packet = build_oracle_signal_intake_boundary_alignment_plan(repo_root=repo_root)
    write_oracle_signal_intake_boundary_alignment_plan(
        repo_root / "out/sync/oracle_signal_intake_boundary_alignment_plan/latest.json",
        alignment_packet,
    )

    packet = build_oracle_signal_intake_boundary_implementation_plan(repo_root=repo_root)

    assert packet["plan_status"] == "IMPLEMENTATION_PLAN_BOUNDARY_OBSERVED_ADVISORY_ONLY"
    assert packet["missing_boundary_paths"] == []
    assert packet["implemented_boundary_paths"] == [
        "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
        "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
        "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
        "scripts/run_oracle_signal_intake_boundary.py",
    ]
    assert packet["all_boundary_paths_observed"] is True
    assert packet["planning_pr_consumed"] is True
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["safe_to_prepare_implementation_pr"] is False
    assert packet["implementation_allowed"] is False


def test_implementation_plan_requires_planning_only_and_preserve_observed_gates(tmp_path: Path) -> None:
    packet = build_oracle_signal_intake_boundary_implementation_plan(repo_root=_seed_implementation_repo(tmp_path))

    gate_statuses = {gate["gate_id"]: gate["status"] for gate in packet["acceptance_gates"]}
    assert gate_statuses == {
        "ORACLE-IMPL-GATE-001": "PLANNING_ONLY",
        "ORACLE-IMPL-GATE-002": "PRESERVE_AS_OBSERVED",
        "ORACLE-IMPL-GATE-003": "AUTHORITY_DENIED",
    }


def test_implementation_plan_fails_closed_without_alignment_packet(tmp_path: Path) -> None:
    write_canonical_json(
        tmp_path / "out/sync/oracle_signal_intake_boundary_alignment_plan/latest.json",
        {
            "artifact_type": "OracleSignalIntakeBoundaryAlignmentPlan.v1",
            "plan_status": "NOT_COMPUTABLE",
            "recommended_next_patch": "NOT_COMPUTABLE",
            "safe_to_prepare_planning_pr": False,
        },
    )
    for rel_path in (
        "scripts/run_oracle_intake.py",
        "core/oracle/runtime.py",
        "core/oracle/intake.py",
        "contracts/ingest/oracle_intake_queue.v1.schema.json",
        "out/ingest/oracle_intake_queue_001.latest.json",
    ):
        path = tmp_path / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("stub", encoding="utf-8")

    packet = build_oracle_signal_intake_boundary_implementation_plan(repo_root=tmp_path)

    assert packet["plan_status"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_implementation_plan_schema_and_hash_are_stable(tmp_path: Path) -> None:
    packet = build_oracle_signal_intake_boundary_implementation_plan(repo_root=_seed_implementation_repo(tmp_path))
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_implementation_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    runner = _load_runner_module()
    repo_root = _seed_implementation_repo(tmp_path / "repo")
    out_json = tmp_path / "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json"
    out_md = tmp_path / "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.md"

    first = runner.run(
        repo_root=repo_root,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = runner.run(
        repo_root=repo_root,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")


def test_registry_includes_implementation_plan_artifacts() -> None:
    from core.generated_artifact_registry import _DERIVED_OPTIONAL_ARTIFACTS

    assert "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json" in _DERIVED_OPTIONAL_ARTIFACTS
    assert "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.md" in _DERIVED_OPTIONAL_ARTIFACTS
