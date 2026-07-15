from __future__ import annotations

import copy
from pathlib import Path

import pytest

from core.aal_viz_yggdrasil_topology import (
    YggdrasilTopologyError,
    bind_yggdrasil_topology,
    build_yggdrasil_topology,
    edge_id,
    operator_topology_payload,
    validate_yggdrasil_topology,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "contracts/canon/aal_viz_yggdrasil_topology.v1.schema.json"
SOURCE_PATHS = {
    "contract_inventory": "out/contracts.json",
    "contract_receipt": "out/contract-receipt.json",
    "graph_render": "out/graph.json",
    "operator_console": "out/operator.json",
    "production_slice": "out/production.json",
    "surface_receipt": "out/surface-receipt.json",
    "yggdrasil": "out/yggdrasil.json",
}


def _sources() -> dict[str, dict]:  # type: ignore[type-arg]
    return {
        "contract_inventory": {
            "canonical_hash": "a" * 64,
            "contracts": [
                {
                    "contract_id": "python.example.Contract",
                    "surface": "core/example.py:Contract",
                    "owner_resolved": True,
                    "production_reachability": "PRODUCTION_SLICE_REACHABLE",
                    "producers": ["core/example.py"],
                    "validators": ["core/validator.py"],
                    "consumers": ["apps/console.ts"],
                }
            ],
        },
        "contract_receipt": {
            "schema_version": "ContractInventoryReceipt.v1",
            "packet_id": "CONTRACT_RECEIPT",
            "canonical_hash": "b" * 64,
        },
        "graph_render": {
            "packet_id": "GRAPH_PACKET",
            "canonical_hash": "c" * 64,
            "nodes": [
                {"node_id": "render:one", "label": "Render one", "source_ref": "one", "status": "PRESENT"},
                {"node_id": "render:two", "label": "Render two", "source_ref": "two", "status": "PRESENT"},
            ],
            "edges": [
                {"edge_id": "render-edge", "source_node_id": "render:one", "target_node_id": "render:two", "category": "message_edge", "status": "PRESENT"}
            ],
        },
        "operator_console": {"packet_id": "OPERATOR_PACKET", "status": "ADVISORY_ONLY"},
        "production_slice": {
            "classification": "PARTIALLY_CONNECTED_RUNTIME_PATH",
            "entrypoint": "scripts/run_example.py",
            "orchestration_path": ["scripts/run_example.py"],
        },
        "surface_receipt": {
            "schema_version": "SurfaceResolutionReceipt.v1",
            "packet_id": "SURFACE_RECEIPT",
            "canonical_hash": "d" * 64,
        },
        "yggdrasil": {
            "rune_to_pipelines": {"RUNE.PIPELINE.VALIDATE": ["example"]},
            "pipeline_to_route": {"example": "example.route.json"},
            "unbound_runes": [],
        },
    }


def _build(sources: dict | None = None):  # type: ignore[type-arg, no-untyped-def]
    source_values = sources or _sources()
    return build_yggdrasil_topology(
        source_values,
        SOURCE_PATHS,
        {key: str(index) * 64 for index, key in enumerate(SOURCE_PATHS, start=1)},
        generated_at="2026-07-15T00:00:00Z",
    )


def test_builds_full_evidence_graph_deterministically() -> None:
    first = _build()
    second = _build()
    assert first == second
    validate_yggdrasil_topology(first, SCHEMA)
    payload = first["payload"]
    assert payload["summary"]["node_class_counts"]["CONTRACT"] == 1
    assert payload["summary"]["node_class_counts"]["INTERFACE"] == 4
    assert {edge["edge_class"] for edge in payload["edges"]} >= {
        "BINDS",
        "CONSUMES",
        "EVIDENCES",
        "EXPOSES",
        "PRODUCES",
        "RENDER_RELATION",
        "ROUTES_TO",
        "VALIDATES",
    }
    interface = next(node for node in payload["nodes"] if node["id"] == "interface:core/example.py")
    assert interface["roles"] == ["PRODUCER"]
    assert first["generation"]["topology_generation_id"] != "0" * 64


def test_operator_summary_preserves_stable_ids() -> None:
    artifact = _build()
    summary = operator_topology_payload(artifact)
    assert {node["id"] for node in summary["nodes"]} == {
        node["id"] for node in artifact["payload"]["nodes"]
    }
    assert {edge["id"] for edge in summary["edges"]} == {
        edge["id"] for edge in artifact["payload"]["edges"]
    }


def test_temporal_binding_is_matched_stale_or_not_computable() -> None:
    artifact = _build()
    operator_id = "a" * 64
    no_diff = bind_yggdrasil_topology(
        artifact,
        operator_id,
        temporal_diff=None,
        temporal_source_path="out/diff.json",
        temporal_content_sha256=None,
    )
    assert no_diff["temporal_linkage"]["status"] == "NOT_COMPUTABLE"
    assert no_diff["generation"]["topology_generation_id"] == artifact["generation"]["topology_generation_id"]
    matched = bind_yggdrasil_topology(
        artifact,
        operator_id,
        temporal_diff={
            "prior_generation": {"generation_id": "b" * 64},
            "current_generation": {"generation_id": operator_id},
        },
        temporal_source_path="out/diff.json",
        temporal_content_sha256="c" * 64,
    )
    assert matched["temporal_linkage"]["status"] == "MATCHED"
    stale_diff = copy.deepcopy(matched)
    stale_diff = bind_yggdrasil_topology(
        artifact,
        operator_id,
        temporal_diff={
            "prior_generation": {"generation_id": "b" * 64},
            "current_generation": {"generation_id": "d" * 64},
        },
        temporal_source_path="out/diff.json",
        temporal_content_sha256="c" * 64,
    )
    assert stale_diff["temporal_linkage"]["status"] == "STALE"
    validate_yggdrasil_topology(matched, SCHEMA)


def test_missing_sources_are_partial_or_not_computable() -> None:
    sources = {key: None for key in SOURCE_PATHS}
    empty = build_yggdrasil_topology(
        sources,
        SOURCE_PATHS,
        {key: None for key in SOURCE_PATHS},
        generated_at="2026-07-15T00:00:00Z",
    )
    assert empty["status"] == "NOT_COMPUTABLE"
    assert empty["payload"] is None
    partial_sources = dict(sources)
    partial_sources["yggdrasil"] = _sources()["yggdrasil"]
    partial = build_yggdrasil_topology(
        partial_sources,
        SOURCE_PATHS,
        {key: ("a" * 64 if partial_sources[key] else None) for key in SOURCE_PATHS},
        generated_at="2026-07-15T00:00:00Z",
    )
    assert partial["status"] == "PARTIAL"
    validate_yggdrasil_topology(partial, SCHEMA)


def test_malformed_records_paths_and_authority_fail_closed() -> None:
    malformed = _sources()
    malformed["contract_inventory"]["contracts"].append({"producers": []})
    with pytest.raises(YggdrasilTopologyError, match="contract_id"):
        _build(malformed)
    with pytest.raises(YggdrasilTopologyError, match="repository-relative"):
        build_yggdrasil_topology(
            _sources(),
            {**SOURCE_PATHS, "graph_render": "/tmp/graph.json"},
            {key: "a" * 64 for key in SOURCE_PATHS},
            generated_at="2026-07-15T00:00:00Z",
        )
    artifact = _build()
    artifact["authority"]["runtime_mutation_allowed"] = True
    with pytest.raises(YggdrasilTopologyError, match="schema violation|authority"):
        validate_yggdrasil_topology(artifact, SCHEMA)


def test_new_edge_id_matches_locked_vector() -> None:
    assert edge_id(
        "PRODUCES", "interface:core/x.py", "contract:python.X", "PRODUCES"
    ) == "edge:f340e8bfc6412e43d721c9247897cf502068e8a1787ff5237d863e10c34ccf86"
