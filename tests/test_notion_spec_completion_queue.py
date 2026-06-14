from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.notion_spec_completion_queue import build_notion_spec_completion_queue

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/notion_spec_completion_queue.v1.schema.json"


def _load_runner():
    try:
        from scripts import run_notion_spec_completion_queue

        return run_notion_spec_completion_queue
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_notion_spec_completion_queue.py"
        spec = importlib.util.spec_from_file_location("run_notion_spec_completion_queue", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_completion_queue_is_advisory_and_fail_closed() -> None:
    packet = build_notion_spec_completion_queue(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "NotionSpecCompletionQueue.v1"
    assert packet["queue_status"] == "COMPLETION_QUEUE_EMITTED_ADVISORY_ONLY"
    assert packet["terminal_queue_observed"] is True
    assert packet["repo_notion_diff_observed"] is True
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["auto_patch_generation_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["runtime_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_completion_queue_ranks_global_ingest_planning_first() -> None:
    packet = build_notion_spec_completion_queue(repo_root=REPO_ROOT)
    first = packet["completion_queue"][0]

    assert first["notion_surface"] == "Global Ingest Adapter Spine"
    assert first["completion_status"] == "BLOCKED"
    assert first["match_strength"] == "PARTIAL"
    assert first["duplicate_risk"] == "HIGH"
    assert first["implementation_blocked"] is True
    assert first["eligible_for_planning"] is False
    assert first["queue_action"] == "SPEC_AUTHORING_APPROVED_IMPLEMENTATION_HELD"
    assert "core/oracle_signal.py" in first["missing_paths"]
    assert (
        packet["recommended_next_action"]
        == "hold; additive shadow contracts, candidate runner, and shadow receipt are already repo-observed as advisory-only evidence"
    )
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"


def test_completion_queue_records_blocked_surfaces() -> None:
    packet = build_notion_spec_completion_queue(repo_root=REPO_ROOT)

    assert packet["blocked_surfaces"] == ["Global Ingest Adapter Spine"]
    assert packet["governed_hold_surfaces"] == [
        "NOTION-PATCH-QUEUE-TERMINAL-STATE-001",
        "Situation Runtime",
    ]
    blocked_items = [item for item in packet["completion_queue"] if item["implementation_blocked"]]
    assert [item["notion_surface"] for item in blocked_items] == ["Global Ingest Adapter Spine"]
    assert blocked_items[0]["queue_action"] == "SPEC_AUTHORING_APPROVED_IMPLEMENTATION_HELD"
    governed_hold_items = [item for item in packet["completion_queue"] if item["governed_hold"]]
    assert [item["notion_surface"] for item in governed_hold_items] == [
        "NOTION-PATCH-QUEUE-TERMINAL-STATE-001",
        "Situation Runtime",
    ]
    assert all(item["completion_status"] == "GOVERNED_HOLD" for item in governed_hold_items)
    assert all(item["implementation_blocked"] is False for item in governed_hold_items)
    assert all(item["queue_action"] == "HOLD_FOR_GOVERNED_OPERATOR_DECISION" for item in governed_hold_items)


def test_completion_queue_fails_closed_when_sources_are_missing(tmp_path: Path) -> None:
    packet = build_notion_spec_completion_queue(repo_root=tmp_path)

    assert packet["queue_status"] == "NOT_COMPUTABLE"
    assert packet["terminal_queue_observed"] is False
    assert packet["repo_notion_diff_observed"] is False
    assert packet["completion_queue"] == []
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["safe_to_prepare_planning_pr"] is False
    assert packet["valid_for_execution"] is False


def test_completion_queue_fails_closed_when_terminal_state_is_not_terminal(tmp_path: Path) -> None:
    terminal_path = tmp_path / "out/sync/notion_patch_queue_terminal_state/latest.json"
    diff_path = tmp_path / "out/audit/repo_notion_diff_001.latest.json"
    write_canonical_json(
        terminal_path,
        {
            "artifact_type": "NotionPatchQueueTerminalState.v1",
            "queue_is_terminal": False,
        },
    )
    write_canonical_json(
        diff_path,
        {
            "artifact_type": "RepoNotionDiffPacket.v1",
            "diff_status": "EMITTED_ADVISORY_ONLY",
            "diff_records": [],
        },
    )

    packet = build_notion_spec_completion_queue(repo_root=tmp_path)

    assert packet["queue_status"] == "NOT_COMPUTABLE"
    assert packet["terminal_queue_observed"] is False
    assert packet["repo_notion_diff_observed"] is True
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_completion_queue_recommends_global_ingest_plan_when_followthrough_artifact_is_missing(
    tmp_path: Path,
) -> None:
    terminal_path = tmp_path / "out/sync/notion_patch_queue_terminal_state/latest.json"
    diff_path = tmp_path / "out/audit/repo_notion_diff_001.latest.json"
    write_canonical_json(
        terminal_path,
        {
            "artifact_type": "NotionPatchQueueTerminalState.v1",
            "queue_is_terminal": True,
        },
    )
    write_canonical_json(
        diff_path,
        {
            "artifact_type": "RepoNotionDiffPacket.v1",
            "diff_status": "EMITTED_ADVISORY_ONLY",
            "diff_records": [
                {
                    "notion_surface": "Global Ingest Adapter Spine",
                    "match_strength": "PARTIAL",
                    "duplicate_risk": "HIGH",
                    "implementation_blocked": False,
                    "governed_hold": False,
                    "hold_reason": "NOT_APPLICABLE",
                    "observed_paths": ["scripts/run_ingest_once.py", "scripts/run_oracle_intake.py"],
                    "missing_paths": ["core/oracle_signal.py"],
                    "recommended_action": "align observed ingest entrypoints before expansion",
                }
            ],
        },
    )

    packet = build_notion_spec_completion_queue(repo_root=tmp_path)

    assert packet["completion_queue"][0]["completion_status"] == "PARTIAL"
    assert packet["completion_queue"][0]["eligible_for_planning"] is True
    assert packet["recommended_next_patch"] == "PATCH-ABX-GLOBAL-INGEST-ADAPTER-SPINE-ALIGNMENT-PLAN-001"
    assert packet["safe_to_prepare_planning_pr"] is True


def test_completion_queue_schema_and_hash_are_stable() -> None:
    packet = build_notion_spec_completion_queue(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_completion_queue_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/notion_spec_completion_queue/latest.json"
    out_md = tmp_path / "out/sync/notion_spec_completion_queue/latest.md"
    run_notion_spec_completion_queue = _load_runner()

    first = run_notion_spec_completion_queue.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_notion_spec_completion_queue.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
