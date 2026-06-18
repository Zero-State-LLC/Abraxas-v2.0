from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash, write_canonical_json
from core.rune_registry_formalization_plan import build_rune_registry_formalization_plan
from core.sync.notion_patch_queue_terminal_state import build_notion_patch_queue_terminal_state

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/notion_patch_queue_terminal_state.v1.schema.json"


def _load_runner():
    try:
        from scripts import run_notion_patch_queue_terminal_state

        return run_notion_patch_queue_terminal_state
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_notion_patch_queue_terminal_state.py"
        spec = importlib.util.spec_from_file_location("run_notion_patch_queue_terminal_state", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_terminal_state_is_advisory_fail_closed() -> None:
    packet = build_notion_patch_queue_terminal_state(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "NotionPatchQueueTerminalState.v1"
    assert packet["terminal_state_status"] == "QUEUE_TERMINAL_STATE_EMITTED_ADVISORY_ONLY"
    assert packet["queue_is_terminal"] is True
    assert packet["safe_to_auto_continue"] is False
    assert packet["auto_patch_generation_allowed"] is False
    assert packet["notion_writeback_allowed"] is False
    assert packet["github_writeback_allowed"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_terminal_state_records_candidate_holds_and_stop_reason() -> None:
    packet = build_notion_patch_queue_terminal_state(repo_root=REPO_ROOT)

    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"
    assert packet["recommended_next_lane"] == "NOT_COMPUTABLE"
    assert packet["candidate_holds"] == []
    assert "NOT_COMPUTABLE" in packet["terminal_reason"]
    assert "new Notion patch spec" in packet["required_operator_input"]


def test_terminal_state_fails_closed_when_source_plan_is_not_terminal(tmp_path: Path) -> None:
    plan = build_rune_registry_formalization_plan(repo_root=REPO_ROOT)
    altered = dict(plan)
    altered["recommended_next_patch"] = "PATCH-ABX-SHOULD-NOT-AUTO-RUN"
    plan_path = tmp_path / "out/audit/rune_registry_formalization_plan_001.latest.json"
    write_canonical_json(plan_path, altered)

    packet = build_notion_patch_queue_terminal_state(
        repo_root=tmp_path,
        rune_registry_formalization_plan_path="out/audit/rune_registry_formalization_plan_001.latest.json",
    )

    assert packet["terminal_state_status"] == "NOT_COMPUTABLE"
    assert packet["queue_is_terminal"] is False
    assert packet["safe_to_auto_continue"] is False
    assert packet["recommended_next_patch"] == "NOT_COMPUTABLE"


def test_terminal_state_schema_and_hash_are_stable() -> None:
    packet = build_notion_patch_queue_terminal_state(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_terminal_state_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/sync/notion_patch_queue_terminal_state/latest.json"
    out_md = tmp_path / "out/sync/notion_patch_queue_terminal_state/latest.md"
    run_notion_patch_queue_terminal_state = _load_runner()

    first = run_notion_patch_queue_terminal_state.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_notion_patch_queue_terminal_state.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
