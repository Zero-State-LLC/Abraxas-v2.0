from __future__ import annotations

import json
import importlib.util
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.runtime_inventory import build_runtime_inventory

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/runtime_inventory_packet.v1.schema.json"


def _load_runner():
    try:
        from scripts.runtime import run_runtime_inventory

        return run_runtime_inventory
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_runtime_inventory.py"
        spec = importlib.util.spec_from_file_location("run_runtime_inventory", runner_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_runtime_inventory_is_advisory_and_read_only() -> None:
    packet = build_runtime_inventory(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "RuntimeInventoryPacket.v1"
    assert packet["inventory_status"] == "EMITTED_ADVISORY_ONLY"
    assert packet["filesystem_read_only"] is True
    assert packet["repo_mutation"] is False
    assert packet["artifact_regeneration"] is False
    assert packet["runtime_activation"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["valid_for_execution"] is False
    assert packet["recommended_next_patch"] == "PATCH-ABX-REPO-NOTION-DIFF-001"
    assert all(value is False for value in packet["authority_locks"].values())


def test_runtime_inventory_has_deterministic_order_and_counts() -> None:
    packet = build_runtime_inventory(repo_root=REPO_ROOT)
    paths = [record["path"] for record in packet["records"]]

    assert paths == sorted(paths)
    assert packet["total_files"] == len(paths)
    assert packet["surface_counts"]["contract"] > 0
    assert packet["surface_counts"]["core_module"] > 0
    assert packet["surface_counts"]["runner_script"] > 0
    assert packet["surface_counts"]["test"] > 0
    assert packet["surface_categories"]["yggdrasil_routes"]["count"] > 0
    assert packet["surface_categories"]["generated_registry"]["count"] == 1


def test_runtime_inventory_includes_anchor_hashes() -> None:
    packet = build_runtime_inventory(repo_root=REPO_ROOT)
    anchors = {row["path"]: row for row in packet["anchor_hashes"]}

    assert anchors["README.md"]["observed"] is True
    assert anchors["PLANS.md"]["observed"] is True
    assert anchors["core/generated_artifact_registry.py"]["observed"] is True
    assert anchors["docs/status/badges.json"]["sha256"] != "NOT_COMPUTABLE"


def test_runtime_inventory_schema_and_hash_are_stable() -> None:
    packet = build_runtime_inventory(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_runtime_inventory_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/audit/runtime_inventory_001.latest.json"
    out_md = tmp_path / "out/audit/runtime_inventory_001.latest.md"
    run_runtime_inventory = _load_runner()

    first = run_runtime_inventory.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_runtime_inventory.run(repo_root=REPO_ROOT, out_json=out_json, out_md=out_md)

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
