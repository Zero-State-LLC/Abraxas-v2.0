from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.notion_operator_decision_backlog import build_notion_operator_decision_backlog

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/notion_operator_decision_backlog.v1.schema.json"


def _load_runner():
    try:
        from scripts.notion import run_notion_operator_decision_backlog

        return run_notion_operator_decision_backlog
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_notion_operator_decision_backlog.py"
        spec = importlib.util.spec_from_file_location("run_notion_operator_decision_backlog", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_operator_decision_backlog_is_advisory_and_fail_closed() -> None:
    packet = build_notion_operator_decision_backlog(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "NotionOperatorDecisionBacklog.v1"
    assert packet["backlog_status"] == "OPERATOR_DECISION_BACKLOG_EMITTED_ADVISORY_ONLY"
    assert packet["queue_observed"] is True
    assert packet["queue_terminal"] is True
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


def test_operator_decision_backlog_ranks_global_ingest_first() -> None:
    packet = build_notion_operator_decision_backlog(repo_root=REPO_ROOT)
    first = packet["decision_backlog"][0]

    assert packet["blocked_surface_count"] == 2
    assert packet["top_priority_surface"] == "NOTION-PATCH-QUEUE-TERMINAL-STATE-001"
    assert first["notion_surface"] == "NOTION-PATCH-QUEUE-TERMINAL-STATE-001"
    assert first["decision_scope"] == "NOTION_SPEC_REFRESH_REQUIRED"
    assert first["source_completion_status"] == "GOVERNED_HOLD"
    assert first["queue_action"] == "HOLD_FOR_GOVERNED_OPERATOR_DECISION"
    assert first["hold_reason"] == "fresh Notion patch spec or explicit governed operator decision required"
    assert "core/oracle_signal.py" not in first["missing_paths"]


def test_operator_decision_backlog_fails_closed_when_queue_is_not_terminal(tmp_path: Path) -> None:
    queue_path = tmp_path / "out/sync/notion_spec_completion_queue/latest.json"
    write_canonical_json(
        queue_path,
        {
            "artifact_type": "NotionSpecCompletionQueue.v1",
            "queue_status": "COMPLETION_QUEUE_EMITTED_ADVISORY_ONLY",
            "recommended_next_patch": "PATCH-ABX-SHOULD-NOT-AUTO-RUN",
            "safe_to_prepare_planning_pr": True,
            "safe_to_auto_continue": False,
            "valid_for_execution": False,
            "completion_queue": [],
        },
    )

    packet = build_notion_operator_decision_backlog(repo_root=tmp_path)

    assert packet["backlog_status"] == "NOT_COMPUTABLE"
    assert packet["queue_terminal"] is False
    assert packet["decision_backlog"] == []
    assert packet["top_priority_surface"] == "NOT_COMPUTABLE"


def test_operator_decision_backlog_schema_and_hash_are_stable() -> None:
    packet = build_notion_operator_decision_backlog(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_operator_decision_backlog_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/notion_operator_decision_backlog/latest.json"
    out_md = tmp_path / "out/sync/notion_operator_decision_backlog/latest.md"
    run_notion_operator_decision_backlog = _load_runner()

    first = run_notion_operator_decision_backlog.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_notion_operator_decision_backlog.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
