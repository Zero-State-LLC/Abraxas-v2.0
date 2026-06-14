from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.global_ingest_adapter_spine_alignment_plan import (
    PATCH_ID,
    build_global_ingest_adapter_spine_alignment_plan,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/global_ingest_adapter_spine_alignment_plan.v1.schema.json"


def _load_runner():
    try:
        from scripts import run_global_ingest_adapter_spine_alignment_plan

        return run_global_ingest_adapter_spine_alignment_plan
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_global_ingest_adapter_spine_alignment_plan.py"
        spec = importlib.util.spec_from_file_location(
            "run_global_ingest_adapter_spine_alignment_plan",
            runner_path,
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_alignment_plan_is_advisory_only_and_fail_closed() -> None:
    packet = build_global_ingest_adapter_spine_alignment_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "GlobalIngestAdapterSpineAlignmentPlan.v1"
    assert packet["plan_status"] == "ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY"
    assert packet["patch_id"] == PATCH_ID
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["downstream_spec_chain_observed"] is True
    assert packet["safe_to_auto_continue"] is False
    assert packet["auto_patch_generation_allowed"] is False
    assert packet["implementation_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["scheduler_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_alignment_plan_preserves_observed_entrypoints_and_missing_core_boundary() -> None:
    packet = build_global_ingest_adapter_spine_alignment_plan(repo_root=REPO_ROOT)

    assert packet["target_surface"] == "Global Ingest Adapter Spine"
    assert packet["target_paths"] == [
        "scripts/run_ingest_once.py",
        "scripts/run_oracle_intake.py",
        "core/oracle_signal.py",
    ]
    assert packet["observed_entrypoints"] == [
        {
            "path": "scripts/run_ingest_once.py",
            "role": "single-run ingest entrypoint",
            "preserve_as_observed": True,
        },
        {
            "path": "scripts/run_oracle_intake.py",
            "role": "oracle intake entrypoint",
            "preserve_as_observed": True,
        },
    ]
    assert packet["missing_paths"] == ["core/oracle_signal.py"]
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert "CORE_ORACLE_SIGNAL_IMPLEMENTATION" in packet["blocked_actions"]
    assert packet["downstream_spec_chain"]["operator_decision_record"]["observed"] is True
    assert packet["downstream_spec_chain"]["separate_implementation_spec_plan"]["observed"] is True
    assert packet["downstream_spec_chain"]["implementation_spec"]["observed"] is True


def test_alignment_plan_requires_operator_decision_before_implementation() -> None:
    packet = build_global_ingest_adapter_spine_alignment_plan(repo_root=REPO_ROOT)

    gate_statuses = {gate["gate_id"]: gate["status"] for gate in packet["acceptance_gates"]}
    assert gate_statuses == {
        "INGEST-GATE-001": "OPERATOR_DECISION_REQUIRED",
        "INGEST-GATE-002": "SEPARATE_IMPLEMENTATION_PR_REQUIRED",
        "INGEST-GATE-003": "AUTHORITY_DENIED",
    }
    assert "no additional planning PR" in packet["required_operator_input"]


def test_alignment_plan_fails_closed_when_queue_does_not_recommend_patch(tmp_path: Path) -> None:
    write_canonical_json(
        tmp_path / "out/sync/notion_patch_queue_terminal_state/latest.json",
        {
            "artifact_type": "NotionPatchQueueTerminalState.v1",
            "queue_is_terminal": False,
            "valid_for_execution": False,
        },
    )
    write_canonical_json(
        tmp_path / "out/audit/repo_notion_diff_001.latest.json",
        {
            "artifact_type": "RepoNotionDiffPacket.v1",
            "diff_records": [
                {
                    "notion_surface": "Global Ingest Adapter Spine",
                    "match_strength": "PARTIAL",
                    "implementation_blocked": False,
                    "observed_paths": ["scripts/run_ingest_once.py", "scripts/run_oracle_intake.py"],
                    "missing_paths": ["core/oracle_signal.py"],
                }
            ],
        },
    )

    packet = build_global_ingest_adapter_spine_alignment_plan(repo_root=tmp_path)

    assert packet["plan_status"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["valid_for_execution"] is False


def test_alignment_plan_schema_and_hash_are_stable() -> None:
    packet = build_global_ingest_adapter_spine_alignment_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_alignment_plan_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json"
    out_md = tmp_path / "out/sync/global_ingest_adapter_spine_alignment_plan/latest.md"
    run_global_ingest_adapter_spine_alignment_plan = _load_runner()

    first = run_global_ingest_adapter_spine_alignment_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_global_ingest_adapter_spine_alignment_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
