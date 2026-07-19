from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from jsonschema import validate

from core.canonical.json import canonical_hash
from core.yggdrasil_route_namespace_mapping import build_yggdrasil_route_namespace_mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = "contracts/canon/yggdrasil_route_namespace_mapping.v1.schema.json"


def _load_runner():
    try:
        from scripts.operator import run_yggdrasil_route_namespace_mapping

        return run_yggdrasil_route_namespace_mapping
    except ImportError:
        runner_path = REPO_ROOT / "Scripts" / "run_yggdrasil_route_namespace_mapping.py"
        spec = importlib.util.spec_from_file_location(
            "run_yggdrasil_route_namespace_mapping",
            runner_path,
        )
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def test_yggdrasil_route_namespace_mapping_is_mapping_only() -> None:
    packet = build_yggdrasil_route_namespace_mapping(repo_root=REPO_ROOT)

    assert packet["artifact_type"] == "YggdrasilRouteNamespaceMapping.v1"
    assert packet["mapping_status"] == "EMITTED_ADVISORY_ONLY"
    assert packet["existing_routes_preserved"] is True
    assert packet["new_route_authority_created"] is False
    assert packet["runtime_dispatch_mutation"] is False
    assert packet["forecast_routing"] is False
    assert packet["canon_mutation"] is False
    assert packet["execution_authority"] is False
    assert packet["valid_for_execution"] is False
    assert all(value is False for value in packet["authority_locks"].values())


def test_yggdrasil_route_namespace_mapping_covers_existing_routes() -> None:
    packet = build_yggdrasil_route_namespace_mapping(repo_root=REPO_ROOT)

    assert packet["route_count"] == 11
    assert packet["pipeline_count"] == 11
    assert packet["mapped_count"] == 11
    assert packet["unmapped_routes"] == []
    assert packet["missing_routes_for_pipelines"] == []

    records = {record["pipeline_id"]: record for record in packet["namespace_records"]}
    assert records["research_intake"]["notion_namespace"] == "Research Intake"
    assert records["research_intake"]["route_node_namespace"] == "research.intake"
    assert records["drift_scan"]["route_node_namespace"] == "drift"
    assert records["universal_ingest"]["notion_namespace"] == "Global Ingest Adapter Spine"
    assert records["operator_review_queue"]["route_node_namespace"] == "operator_review"
    assert all(record["route_authority_locked"] for record in records.values())
    assert all(record["pipeline_authority_locked"] for record in records.values())


def test_yggdrasil_route_namespace_mapping_schema_and_hash_are_stable() -> None:
    packet = build_yggdrasil_route_namespace_mapping(repo_root=REPO_ROOT)
    packet_without_hash = dict(packet)
    packet_hash = packet_without_hash.pop("packet_hash")
    assert packet_hash == canonical_hash(packet_without_hash)

    schema = json.loads((REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8"))
    validate(packet, schema)


def test_yggdrasil_route_namespace_mapping_runner_writes_stable_outputs(tmp_path: Path) -> None:
    out_json = tmp_path / "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.json"
    out_md = tmp_path / "out/yggdrasil/yggdrasil_route_namespace_mapping_001.latest.md"
    run_yggdrasil_route_namespace_mapping = _load_runner()

    first = run_yggdrasil_route_namespace_mapping.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )
    first_json = out_json.read_text(encoding="utf-8")
    first_md = out_md.read_text(encoding="utf-8")
    second = run_yggdrasil_route_namespace_mapping.run(
        repo_root=REPO_ROOT,
        out_json=out_json,
        out_md=out_md,
    )

    assert first == second
    assert first_json == out_json.read_text(encoding="utf-8")
    assert first_md == out_md.read_text(encoding="utf-8")
