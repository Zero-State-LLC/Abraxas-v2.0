from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.repo_notion_diff import build_repo_notion_diff

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/repo_notion_diff_packet.v1.schema.json"


def _load_runner():
    try:
        from scripts import run_repo_notion_diff

        return run_repo_notion_diff
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_repo_notion_diff.py"
        spec = importlib.util.spec_from_file_location("run_repo_notion_diff", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_repo_notion_diff_is_advisory_only() -> None:
    packet = build_repo_notion_diff(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "RepoNotionDiffPacket.v1"
    assert packet["diff_status"] == "EMITTED_ADVISORY_ONLY"
    assert packet["match_strength_recorded"] is True
    assert packet["duplicate_risk_recorded"] is True
    assert packet["repo_mutation"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_repo_notion_diff_records_match_strength_and_duplicate_risk() -> None:
    packet = build_repo_notion_diff(repo_root=REPO_ROOT)
    records = {record["notion_surface"]: record for record in packet["diff_records"]}

    assert records["PATCH-ABX-RUNTIME-INVENTORY-001"]["match_strength"] == "EXACT"
    assert records["PATCH-ABX-REPO-NOTION-DIFF-001"]["match_strength"] == "EXACT"
    assert records["PATCH-ABX-BELIEF-GRAPH-GAP-VERIFICATION-001"]["implementation_blocked"] is False
    assert records["PATCH-ABX-RUNE-REGISTRY-FORMALIZATION-PLAN-001"]["implementation_blocked"] is False
    assert records["NOTION-PATCH-QUEUE-TERMINAL-STATE-001"]["implementation_blocked"] is True
    assert records["Situation Runtime"]["implementation_blocked"] is True
    assert records["Global Ingest Adapter Spine"]["duplicate_risk"] in {"MEDIUM", "HIGH"}
    assert packet["summary"]["total_targets"] == len(packet["diff_records"])


def test_repo_notion_diff_schema_and_hash_are_stable() -> None:
    packet = build_repo_notion_diff(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_repo_notion_diff_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/repo_notion_diff_001.latest.json"
    out_md = tmp_path / "out/audit/repo_notion_diff_001.latest.md"
    run_repo_notion_diff = _load_runner()

    first = run_repo_notion_diff.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_repo_notion_diff.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
