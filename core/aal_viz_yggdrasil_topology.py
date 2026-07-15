"""Deterministic, evidence-backed YGGDRASIL topology projection."""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "AALViz.YggdrasilTopology.v1"
GENERATED_BY = "LIVE_YGGDRASIL_TOPOLOGY_ENRICHMENT_001"
SOURCE_KEYS = (
    "contract_inventory",
    "contract_receipt",
    "graph_render",
    "operator_console",
    "production_slice",
    "surface_receipt",
    "yggdrasil",
)
AUTHORITY = {
    "projection_only": True,
    "runtime_mutation_allowed": False,
    "canon_mutation_allowed": False,
    "execution_authority": False,
    "promotion_allowed": False,
    "production_activation_allowed": False,
    "graph_driven_execution_allowed": False,
    "autonomous_link_creation_allowed": False,
    "alerting_allowed": False,
    "scheduling_allowed": False,
}
NODE_CLASSES = (
    "CONTRACT",
    "INTERFACE",
    "PACKET",
    "RECEIPT",
    "ROUTE",
    "RUNE",
    "SYSTEM",
)
EDGE_CLASSES = (
    "BINDS",
    "CONSUMES",
    "EVIDENCES",
    "EXPOSES",
    "PRODUCES",
    "REFERENCES",
    "RENDER_RELATION",
    "ROUTES_TO",
    "VALIDATES",
)


class YggdrasilTopologyError(ValueError):
    """Raised when topology evidence or output violates the locked contract."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def _repository_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in value
        or (len(value) > 2 and value[1] == ":")
    ):
        raise YggdrasilTopologyError(
            f"published path must be repository-relative POSIX: {value}"
        )
    return value


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return sorted({str(item) for item in value if str(item).strip()})


def _declared_hash(payload: Mapping[str, Any] | None) -> str | None:
    if payload is None:
        return None
    value = payload.get(
        "canonical_hash", payload.get("packet_hash", payload.get("seal"))
    )
    return value if isinstance(value, str) else None


def source_descriptor(
    key: str,
    path: str,
    payload: Mapping[str, Any] | None,
    content_sha256: str | None,
) -> dict[str, Any]:
    _repository_path(path)
    if content_sha256 is not None and (
        len(content_sha256) != 64
        or any(character not in "0123456789abcdef" for character in content_sha256)
    ):
        raise YggdrasilTopologyError(f"invalid content hash for source: {key}")
    return {
        "id": f"source:{key}",
        "source_key": key,
        "path": path,
        "declared_canonical_hash": _declared_hash(payload),
        "content_sha256": content_sha256,
        "integrity_state": "VERIFIED" if payload is not None else "NOT_COMPUTABLE",
    }


def edge_id(edge_class: str, source: str, target: str, relation: str) -> str:
    return f"edge:{sha256_json([edge_class, source, target, relation])}"


def _node(
    node_id: str,
    label: str,
    node_class: str,
    source_ref: str,
    evidence_refs: Sequence[str],
    *,
    roles: Sequence[str] = (),
    status: str = "OBSERVED",
    resolution_state: str = "RESOLVED",
    provenance: str = "OBSERVED",
    confidence: str = "VERIFIED",
) -> dict[str, Any]:
    return {
        "id": node_id,
        "label": label,
        "node_class": node_class,
        "roles": sorted(set(roles)),
        "status": status,
        "resolution_state": resolution_state,
        "source_ref": source_ref,
        "provenance": provenance,
        "confidence": confidence,
        "freshness": "CURRENT",
        "evidence_refs": sorted(set(evidence_refs)),
        "temporal_ref": {"category": "TOPOLOGY_NODE", "entity_id": node_id},
    }


def _edge(
    edge_class: str,
    source: str,
    target: str,
    relation: str,
    evidence_refs: Sequence[str],
    *,
    stable_id: str | None = None,
    status: str = "OBSERVED",
    resolution_state: str = "RESOLVED",
    provenance: str = "OBSERVED",
    confidence: str = "VERIFIED",
) -> dict[str, Any]:
    identity = stable_id or edge_id(edge_class, source, target, relation)
    return {
        "id": identity,
        "source": source,
        "target": target,
        "edge_class": edge_class,
        "relation": relation,
        "status": status,
        "resolution_state": resolution_state,
        "provenance": provenance,
        "confidence": confidence,
        "freshness": "CURRENT",
        "evidence_refs": sorted(set(evidence_refs)),
        "temporal_ref": {"category": "TOPOLOGY_EDGE", "entity_id": identity},
    }


def _merge_node(nodes: dict[str, dict[str, Any]], candidate: dict[str, Any]) -> None:
    existing = nodes.get(candidate["id"])
    if existing is None:
        nodes[candidate["id"]] = candidate
        return
    if existing["node_class"] != candidate["node_class"]:
        raise YggdrasilTopologyError(f"duplicate node id: {candidate['id']}")
    existing["roles"] = sorted(set(existing["roles"] + candidate["roles"]))
    existing["evidence_refs"] = sorted(
        set(existing["evidence_refs"] + candidate["evidence_refs"])
    )


def _add_edge(edges: dict[str, dict[str, Any]], candidate: dict[str, Any]) -> None:
    existing = edges.get(candidate["id"])
    if existing is None:
        edges[candidate["id"]] = candidate
        return
    semantic_keys = ("source", "target", "edge_class", "relation")
    if any(existing[key] != candidate[key] for key in semantic_keys):
        raise YggdrasilTopologyError(f"duplicate edge id: {candidate['id']}")
    existing["evidence_refs"] = sorted(
        set(existing["evidence_refs"] + candidate["evidence_refs"])
    )


def _interface(
    nodes: dict[str, dict[str, Any]], path: str, role: str, evidence_ref: str
) -> str:
    normalized = _repository_path(path)
    identity = f"interface:{normalized}"
    _merge_node(
        nodes,
        _node(
            identity,
            normalized,
            "INTERFACE",
            normalized,
            [evidence_ref],
            roles=[role],
        ),
    )
    return identity


def _map_graph_render(
    payload: Mapping[str, Any],
    nodes: dict[str, dict[str, Any]],
    edges: dict[str, dict[str, Any]],
) -> None:
    evidence_ref = "source:graph_render"
    raw_nodes = payload.get("nodes", [])
    raw_edges = payload.get("edges", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        raise YggdrasilTopologyError("graph_render node and edge arrays are required")
    for raw in raw_nodes:
        if not isinstance(raw, Mapping) or not isinstance(raw.get("node_id"), str):
            raise YggdrasilTopologyError("graph_render contains a malformed node")
        identity = raw["node_id"]
        _merge_node(
            nodes,
            _node(
                identity,
                str(raw.get("label", raw.get("source_ref", identity))),
                "PACKET",
                str(raw.get("source_ref", "")),
                [evidence_ref],
                status=str(raw.get("status", "NOT_COMPUTABLE")),
            ),
        )
    for raw in raw_edges:
        if not isinstance(raw, Mapping):
            raise YggdrasilTopologyError("graph_render contains a malformed edge")
        identity = raw.get("edge_id")
        source = raw.get("source_node_id")
        target = raw.get("target_node_id")
        if not all(isinstance(value, str) and value for value in (identity, source, target)):
            raise YggdrasilTopologyError("graph_render edge identity is malformed")
        _add_edge(
            edges,
            _edge(
                "RENDER_RELATION",
                source,
                target,
                str(raw.get("category", "RELATED")),
                [evidence_ref],
                stable_id=identity,
                status=str(raw.get("status", "NOT_COMPUTABLE")),
            ),
        )


def _map_yggdrasil(
    payload: Mapping[str, Any],
    nodes: dict[str, dict[str, Any]],
    edges: dict[str, dict[str, Any]],
) -> None:
    evidence_ref = "source:yggdrasil"
    rune_map = payload.get("rune_to_pipelines", {})
    route_map = payload.get("pipeline_to_route", {})
    if not isinstance(rune_map, Mapping) or not isinstance(route_map, Mapping):
        raise YggdrasilTopologyError("yggdrasil coupling maps are malformed")
    unbound = set(_string_list(payload.get("unbound_runes", [])))
    for rune, pipelines in sorted(rune_map.items()):
        rune_name = str(rune)
        rune_identity = f"rune:{rune_name}"
        _merge_node(
            nodes,
            _node(
                rune_identity,
                rune_name,
                "RUNE",
                rune_name,
                [evidence_ref],
                status="UNBOUND" if rune_name in unbound else "BOUND",
                resolution_state="UNRESOLVED" if rune_name in unbound else "RESOLVED",
            ),
        )
        for pipeline in _string_list(pipelines):
            system_identity = f"system:{pipeline}"
            _merge_node(
                nodes,
                _node(
                    system_identity,
                    pipeline,
                    "SYSTEM",
                    pipeline,
                    [evidence_ref],
                ),
            )
            _add_edge(
                edges,
                _edge(
                    "BINDS",
                    rune_identity,
                    system_identity,
                    "BINDS",
                    [evidence_ref],
                    stable_id=f"binding:{rune_name}:{pipeline}",
                ),
            )
    for pipeline, route in sorted(route_map.items()):
        system_identity = f"system:{pipeline}"
        route_name = str(route)
        route_identity = f"route:{route_name}"
        _merge_node(
            nodes,
            _node(
                system_identity,
                str(pipeline),
                "SYSTEM",
                str(pipeline),
                [evidence_ref],
            ),
        )
        _merge_node(
            nodes,
            _node(
                route_identity,
                route_name,
                "ROUTE",
                route_name,
                [evidence_ref],
            ),
        )
        _add_edge(
            edges,
            _edge(
                "ROUTES_TO",
                system_identity,
                route_identity,
                "ROUTES_TO",
                [evidence_ref],
                stable_id=f"route-binding:{pipeline}:{route_name}",
            ),
        )


def _map_contracts(
    payload: Mapping[str, Any],
    nodes: dict[str, dict[str, Any]],
    edges: dict[str, dict[str, Any]],
) -> None:
    evidence_ref = "source:contract_inventory"
    contracts = payload.get("contracts", [])
    if not isinstance(contracts, list):
        raise YggdrasilTopologyError("contract inventory contracts must be an array")
    for raw in contracts:
        if not isinstance(raw, Mapping):
            raise YggdrasilTopologyError("contract inventory contains a malformed record")
        contract_id = raw.get("contract_id")
        if not isinstance(contract_id, str) or not contract_id:
            raise YggdrasilTopologyError("contract inventory record lacks contract_id")
        identity = f"contract:{contract_id}"
        resolved = bool(raw.get("owner_resolved", False))
        _merge_node(
            nodes,
            _node(
                identity,
                contract_id,
                "CONTRACT",
                str(raw.get("surface", contract_id)),
                [evidence_ref],
                status=str(raw.get("production_reachability", "NOT_COMPUTABLE")),
                resolution_state="RESOLVED" if resolved else "UNRESOLVED",
            ),
        )
        relations = (
            ("PRODUCER", "PRODUCES", "PRODUCES", raw.get("producers", []), True),
            ("VALIDATOR", "VALIDATES", "VALIDATES", raw.get("validators", []), True),
            ("CONSUMER", "CONSUMES", "CONSUMES", raw.get("consumers", []), False),
        )
        for role, edge_class, relation, paths, interface_first in relations:
            for path in _string_list(paths):
                interface_id = _interface(nodes, path, role, evidence_ref)
                source, target = (
                    (interface_id, identity) if interface_first else (identity, interface_id)
                )
                _add_edge(
                    edges,
                    _edge(
                        edge_class,
                        source,
                        target,
                        relation,
                        [evidence_ref],
                    ),
                )


def _map_production_slice(
    payload: Mapping[str, Any],
    nodes: dict[str, dict[str, Any]],
    edges: dict[str, dict[str, Any]],
) -> None:
    evidence_ref = "source:production_slice"
    entrypoint = payload.get("entrypoint")
    if not isinstance(entrypoint, str) or not entrypoint:
        raise YggdrasilTopologyError("production slice lacks an entrypoint")
    system_id = "system:production_slice"
    _merge_node(
        nodes,
        _node(
            system_id,
            str(payload.get("classification", "production slice")),
            "SYSTEM",
            entrypoint,
            [evidence_ref],
            provenance="INFERRED",
            confidence="SUPPORTED",
        ),
    )
    for path in sorted(set([entrypoint, *_string_list(payload.get("orchestration_path", []))])):
        interface_id = _interface(nodes, path, "OPERATOR", evidence_ref)
        _add_edge(
            edges,
            _edge(
                "EXPOSES",
                interface_id,
                system_id,
                "OPERATOR_ENTRYPOINT",
                [evidence_ref],
                provenance="INFERRED",
                confidence="SUPPORTED",
            ),
        )


def _map_evidence_nodes(
    sources: Mapping[str, Mapping[str, Any] | None],
    nodes: dict[str, dict[str, Any]],
) -> dict[str, str]:
    evidence_nodes: dict[str, str] = {}
    for key in ("contract_receipt", "graph_render", "operator_console", "surface_receipt"):
        payload = sources.get(key)
        if payload is None:
            continue
        record_id = payload.get("packet_id", payload.get("artifact_id", key))
        if not isinstance(record_id, str) or not record_id:
            record_id = key
        schema_name = str(payload.get("schema_version", payload.get("schema", "")))
        node_class = "RECEIPT" if "Receipt" in schema_name or "receipt" in key else "PACKET"
        prefix = node_class.lower()
        identity = f"{prefix}:{record_id}"
        evidence_nodes[key] = identity
        _merge_node(
            nodes,
            _node(
                identity,
                record_id,
                node_class,
                str(record_id),
                [f"source:{key}"],
                status=str(
                    payload.get(
                        "final_status", payload.get("packet_status", payload.get("status", "OBSERVED"))
                    )
                ),
            ),
        )
    return evidence_nodes


def _map_evidence_edges(
    evidence_nodes: Mapping[str, str],
    nodes: Mapping[str, Mapping[str, Any]],
    edges: dict[str, dict[str, Any]],
) -> None:
    source_bindings = {
        "contract_receipt": ("source:contract_inventory",),
        "graph_render": ("source:graph_render",),
        "operator_console": ("source:operator_console",),
        "surface_receipt": ("source:production_slice", "source:surface_receipt"),
    }
    for source_key, evidence_node in sorted(evidence_nodes.items()):
        evidence_refs = source_bindings[source_key]
        for node in sorted(nodes.values(), key=lambda item: item["id"]):
            if node["id"] == evidence_node or not set(evidence_refs).intersection(node["evidence_refs"]):
                continue
            _add_edge(
                edges,
                _edge(
                    "EVIDENCES",
                    evidence_node,
                    str(node["id"]),
                    "EVIDENCES",
                    [f"source:{source_key}"],
                ),
            )


def _summary(
    nodes: Sequence[Mapping[str, Any]],
    edges: Sequence[Mapping[str, Any]],
    evidence: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "evidence_count": len(evidence),
        "unresolved_node_count": sum(
            1 for node in nodes if node["resolution_state"] == "UNRESOLVED"
        ),
        "stale_entity_count": sum(
            1 for item in [*nodes, *edges] if item["freshness"] == "STALE"
        ),
        "inferred_edge_count": sum(
            1 for edge in edges if edge["provenance"] == "INFERRED"
        ),
        "node_class_counts": {
            node_class: sum(1 for node in nodes if node["node_class"] == node_class)
            for node_class in NODE_CLASSES
            if any(node["node_class"] == node_class for node in nodes)
        },
        "edge_class_counts": {
            edge_class: sum(1 for edge in edges if edge["edge_class"] == edge_class)
            for edge_class in EDGE_CLASSES
            if any(edge["edge_class"] == edge_class for edge in edges)
        },
    }


def _topology_generation_id(artifact: Mapping[str, Any]) -> str:
    semantic = copy.deepcopy(dict(artifact))
    semantic.pop("canonical_hash", None)
    semantic.pop("temporal_linkage", None)
    generation = semantic["generation"]
    generation.pop("generated_at", None)
    generation.pop("topology_generation_id", None)
    generation.pop("operator_platform_generation_id", None)
    return sha256_json(semantic)


def _canonical_hash(artifact: Mapping[str, Any]) -> str:
    return sha256_json(
        {key: value for key, value in artifact.items() if key != "canonical_hash"}
    )


def build_yggdrasil_topology(
    sources: Mapping[str, Mapping[str, Any] | None],
    source_paths: Mapping[str, str],
    content_hashes: Mapping[str, str | None],
    *,
    generated_at: str,
) -> dict[str, Any]:
    unknown = set(sources) - set(SOURCE_KEYS)
    if unknown:
        raise YggdrasilTopologyError(f"unsupported topology source keys: {sorted(unknown)}")
    descriptors = [
        source_descriptor(
            key, source_paths[key], sources.get(key), content_hashes.get(key)
        )
        for key in SOURCE_KEYS
    ]
    present = {key for key in SOURCE_KEYS if sources.get(key) is not None}
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[str, dict[str, Any]] = {}
    if payload := sources.get("graph_render"):
        _map_graph_render(payload, nodes, edges)
    if payload := sources.get("yggdrasil"):
        _map_yggdrasil(payload, nodes, edges)
    if payload := sources.get("contract_inventory"):
        _map_contracts(payload, nodes, edges)
    if payload := sources.get("production_slice"):
        _map_production_slice(payload, nodes, edges)
    evidence_nodes = _map_evidence_nodes(sources, nodes)
    _map_evidence_edges(evidence_nodes, nodes, edges)
    dangling = [
        edge["id"]
        for edge in edges.values()
        if edge["source"] not in nodes or edge["target"] not in nodes
    ]
    if dangling:
        raise YggdrasilTopologyError(f"dangling topology edge: {dangling[0]}")
    ordered_nodes = sorted(nodes.values(), key=lambda item: item["id"])
    ordered_edges = sorted(edges.values(), key=lambda item: item["id"])
    findings = [
        f"Optional topology source is unavailable: {key}"
        for key in SOURCE_KEYS
        if key not in present
    ]
    if not present:
        status = "NOT_COMPUTABLE"
        payload: dict[str, Any] | None = None
        reason = "No usable topology evidence was supplied."
        provenance = "INFERRED"
    else:
        status = "AVAILABLE" if len(present) == len(SOURCE_KEYS) else "PARTIAL"
        evidence = descriptors
        payload = {
            "summary": _summary(ordered_nodes, ordered_edges, evidence),
            "nodes": ordered_nodes,
            "edges": ordered_edges,
            "evidence": evidence,
        }
        reason = None
        provenance = (
            "INFERRED"
            if any(edge["provenance"] == "INFERRED" for edge in ordered_edges)
            else "OBSERVED"
        )
    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generation": {
            "generated_at": generated_at,
            "generated_by": GENERATED_BY,
            "topology_generation_id": "0" * 64,
            "operator_platform_generation_id": None,
        },
        "status": status,
        "provenance": provenance,
        "source_artifacts": descriptors,
        "authority": dict(AUTHORITY),
        "payload": payload,
        "not_computable_reason": reason,
        "validation_findings": findings,
        "temporal_linkage": {
            "status": "NOT_COMPUTABLE",
            "source_path": None,
            "content_sha256": None,
            "prior_generation_id": None,
            "current_generation_id": None,
        },
        "canonical_hash": "0" * 64,
    }
    artifact["generation"]["topology_generation_id"] = _topology_generation_id(
        artifact
    )
    artifact["canonical_hash"] = _canonical_hash(artifact)
    return artifact


def bind_yggdrasil_topology(
    artifact: Mapping[str, Any],
    operator_platform_generation_id: str,
    *,
    temporal_diff: Mapping[str, Any] | None,
    temporal_source_path: str,
    temporal_content_sha256: str | None,
) -> dict[str, Any]:
    bound = copy.deepcopy(dict(artifact))
    bound["generation"]["operator_platform_generation_id"] = (
        operator_platform_generation_id
    )
    linkage = {
        "status": "NOT_COMPUTABLE",
        "source_path": None,
        "content_sha256": None,
        "prior_generation_id": None,
        "current_generation_id": None,
    }
    if temporal_diff is not None:
        _repository_path(temporal_source_path)
        prior = temporal_diff.get("prior_generation", {})
        current = temporal_diff.get("current_generation", {})
        prior_id = prior.get("generation_id") if isinstance(prior, Mapping) else None
        current_id = current.get("generation_id") if isinstance(current, Mapping) else None
        linkage = {
            "status": (
                "MATCHED"
                if current_id == operator_platform_generation_id
                else "STALE"
            ),
            "source_path": temporal_source_path,
            "content_sha256": temporal_content_sha256,
            "prior_generation_id": prior_id,
            "current_generation_id": current_id,
        }
    bound["temporal_linkage"] = linkage
    bound["canonical_hash"] = _canonical_hash(bound)
    return bound


def operator_topology_payload(artifact: Mapping[str, Any]) -> dict[str, Any]:
    payload = artifact.get("payload")
    if not isinstance(payload, Mapping):
        return {"source_status": "NOT_COMPUTABLE", "nodes": [], "edges": []}
    entity_types = {
        "CONTRACT": "CONTRACT",
        "INTERFACE": "SYSTEM",
        "PACKET": "PACKET",
        "RECEIPT": "RECEIPT",
        "ROUTE": "ROUTE",
        "RUNE": "RUNE",
        "SYSTEM": "SYSTEM",
    }
    return {
        "source_status": "OBSERVED",
        "nodes": [
            {
                "id": node["id"],
                "label": node["label"],
                "entity_type": entity_types[node["node_class"]],
                "status": node["status"],
                "source_ref": node["source_ref"],
                "provenance": node["provenance"],
            }
            for node in payload["nodes"]
        ],
        "edges": [
            {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "relation": edge["relation"],
                "status": edge["status"],
                "provenance": edge["provenance"],
            }
            for edge in payload["edges"]
        ],
    }


def validate_yggdrasil_topology(
    artifact: Mapping[str, Any], schema_path: Path
) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if errors:
        raise YggdrasilTopologyError(
            f"topology schema violation: {errors[0].message}"
        )
    if artifact.get("authority") != AUTHORITY:
        raise YggdrasilTopologyError("topology authority locks are malformed")
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        raise YggdrasilTopologyError("topology canonical hash mismatch")
    generation = artifact["generation"]
    if generation["topology_generation_id"] != _topology_generation_id(artifact):
        raise YggdrasilTopologyError("topology generation id mismatch")
    sources = artifact["source_artifacts"]
    if sources != sorted(sources, key=lambda item: item["id"]):
        raise YggdrasilTopologyError("source artifacts are not canonically ordered")
    if artifact["validation_findings"] != sorted(artifact["validation_findings"]):
        raise YggdrasilTopologyError("validation findings are not canonically ordered")
    payload = artifact.get("payload")
    if not isinstance(payload, Mapping):
        return
    evidence = payload["evidence"]
    nodes = payload["nodes"]
    edges = payload["edges"]
    for label, records in (("evidence", evidence), ("nodes", nodes), ("edges", edges)):
        identities = [record["id"] for record in records]
        if identities != sorted(identities) or len(identities) != len(set(identities)):
            raise YggdrasilTopologyError(f"{label} identities are invalid")
    evidence_ids = {record["id"] for record in evidence}
    node_ids = {record["id"] for record in nodes}
    for node in nodes:
        if node["temporal_ref"]["entity_id"] != node["id"]:
            raise YggdrasilTopologyError("node temporal reference mismatch")
        if not set(node["evidence_refs"]).issubset(evidence_ids):
            raise YggdrasilTopologyError("dangling node evidence reference")
    for edge in edges:
        if edge["source"] not in node_ids or edge["target"] not in node_ids:
            raise YggdrasilTopologyError("dangling edge endpoint")
        if edge["temporal_ref"]["entity_id"] != edge["id"]:
            raise YggdrasilTopologyError("edge temporal reference mismatch")
        if not set(edge["evidence_refs"]).issubset(evidence_ids):
            raise YggdrasilTopologyError("dangling edge evidence reference")
