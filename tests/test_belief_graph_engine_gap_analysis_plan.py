from __future__ import annotations

import json
import importlib.util
from pathlib import Path

from jsonschema import validate

from core.belief_graph_engine_gap_analysis_plan import (
    build_belief_graph_engine_gap_analysis_plan,
)
from core.canonical.json import canonical_hash

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/belief_graph_engine_gap_analysis_plan.v1.schema.json"


def _load_runner():
    try:
        from scripts import run_belief_graph_engine_gap_analysis_plan

        return run_belief_graph_engine_gap_analysis_plan
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_belief_graph_engine_gap_analysis_plan.py"
        spec = importlib.util.spec_from_file_location(
            "run_belief_graph_engine_gap_analysis_plan",
            runner_path,
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_belief_graph_engine_gap_analysis_plan_is_advisory_only() -> None:
    packet = build_belief_graph_engine_gap_analysis_plan(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "BeliefGraphEngineGapAnalysisPlan.v1"
    assert packet["plan_status"] == "BELIEF_GRAPH_ENGINE_GAP_CLOSED"
    assert packet["target_surface"] == "BELIEF_GRAPH_ENGINE_001"
    assert packet["belief_graph_engine_implementation_performed"] is True
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert packet["valid_for_implementation"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_belief_graph_engine_gap_analysis_plan_separates_primitives_from_engine() -> None:
    packet = build_belief_graph_engine_gap_analysis_plan(repo_root=REPO_ROOT)

    assert packet["primitive_scaffold_evidence"]["belief_graph_equivalent_observed"] is True
    assert packet["primitive_scaffold_evidence"]["primitive_paths_observed"] == packet[
        "primitive_scaffold_evidence"
    ]["primitive_paths_total"]
    assert packet["gap_summary"]["engine_missing_paths"] == 0
    assert packet["notion_gap_evidence"]["implementation_status"] == "OBSERVED"
    assert "belief_graph_engine_implementation" not in packet["blocked_actions"]


def test_belief_graph_engine_gap_analysis_plan_schema_and_hash_are_stable() -> None:
    packet = build_belief_graph_engine_gap_analysis_plan(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_belief_graph_engine_gap_analysis_plan_runner_writes_stable_outputs(
    tmp_path: Path,
) -> None:
    out_json = tmp_path / "out/audit/belief_graph_engine_gap_analysis_plan_001.latest.json"
    out_md = tmp_path / "out/audit/belief_graph_engine_gap_analysis_plan_001.latest.md"
    run_belief_graph_engine_gap_analysis_plan = _load_runner()

    first = run_belief_graph_engine_gap_analysis_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_belief_graph_engine_gap_analysis_plan.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
