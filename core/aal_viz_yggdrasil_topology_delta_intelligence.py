"""Deterministic, projection-only YGGDRASIL topology delta intelligence."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter, deque
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from jsonschema import Draft202012Validator


SCHEMA_VERSION = "AALViz.YggdrasilTopologyDeltaIntelligence.v1"
GENERATED_BY = "YGGDRASIL_TOPOLOGY_DELTA_INTELLIGENCE_001"
OPERATIONAL_EDGE_CLASSES = {
    "BINDS",
    "CONSUMES",
    "EXPOSES",
    "PRODUCES",
    "ROUTES_TO",
    "VALIDATES",
}
STRUCTURAL_WEIGHTS = {
    "BROKEN_PRODUCER_CONSUMER_PATH": 30,
    "TOPOLOGY_FRAGMENTATION": 30,
    "ORPHANED_CONTRACT": 25,
    "VALIDATOR_COVERAGE_LOSS": 25,
    "STALE_EVIDENCE_CHAIN": 20,
    "OWNERSHIP_DRIFT": 15,
    "ISOLATED_NODE_EMERGENCE": 10,
    "UNEXPECTED_CLUSTER_FUSION": 10,
}
SEVERITY_WEIGHTS = {"HIGH": 35, "MEDIUM": 25, "LOW": 10, "INFO": 0}
SEVERITY_ORDER = {"HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}
CONFIDENCE_WEIGHTS = {"VERIFIED": 5, "SUPPORTED": 3, "INFERRED": 1}
AUTHORITY = {
    "projection_only": True,
    "execution_authority": False,
    "canon_mutation_allowed": False,
    "runtime_mutation_allowed": False,
    "graph_driven_execution_allowed": False,
    "production_activation_allowed": False,
    "route_receipt_triggering_allowed": False,
    "scheduling_allowed": False,
    "alert_delivery_allowed": False,
    "acknowledgement_state_allowed": False,
    "browser_persistence_allowed": False,
    "automatic_remediation_allowed": False,
    "autonomous_escalation_allowed": False,
}


class YggdrasilTopologyDeltaIntelligenceError(ValueError):
    """Raised when delta intelligence cannot be published safely."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def typed_id(prefix: str, *identity: Any) -> str:
    return f"{prefix}:{sha256_json(list(identity))}"


def _repository_path(value: str) -> str:
    candidate = PurePosixPath(value)
    if (
        not value
        or candidate.is_absolute()
        or ".." in candidate.parts
        or "\\" in value
        or (len(value) > 2 and value[1] == ":")
    ):
        raise YggdrasilTopologyDeltaIntelligenceError(
            f"published source path must be repository-relative POSIX: {value}"
        )
    return value


def _hash(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or len(value) != 64:
        raise YggdrasilTopologyDeltaIntelligenceError(f"{label} is malformed")
    try:
        int(value, 16)
    except ValueError as exc:
        raise YggdrasilTopologyDeltaIntelligenceError(f"{label} is malformed") from exc
    return value


def _canonical_hash(artifact: Mapping[str, Any]) -> str:
    return sha256_json(
        {key: value for key, value in artifact.items() if key != "canonical_hash"}
    )


def _generation_id(artifact: Mapping[str, Any]) -> str:
    semantic = copy.deepcopy(dict(artifact))
    semantic.pop("canonical_hash", None)
    generation = semantic["generation"]
    generation.pop("generated_at", None)
    generation.pop("delta_generation_id", None)
    return sha256_json(semantic)


def _source(
    key: str,
    path: str,
    artifact: Mapping[str, Any] | None,
    content_hash: str | None,
) -> dict[str, Any]:
    _repository_path(path)
    declared = artifact.get("canonical_hash") if artifact is not None else None
    return {
        "id": f"source:{key}",
        "source_key": key,
        "path": path,
        "declared_canonical_hash": _hash(
            declared, f"{key} canonical hash", nullable=True
        ),
        "content_sha256": _hash(content_hash, f"{key} content hash", nullable=True),
        "integrity_state": "VERIFIED" if artifact is not None else "NOT_COMPUTABLE",
    }


def _payload(artifact: Mapping[str, Any]) -> Mapping[str, Any]:
    value = artifact.get("payload")
    if not isinstance(value, Mapping):
        raise YggdrasilTopologyDeltaIntelligenceError(
            "topology payload is required for comparison"
        )
    return value


def _index(records: Any, label: str) -> dict[str, Mapping[str, Any]]:
    if not isinstance(records, Sequence) or isinstance(records, (str, bytes)):
        raise YggdrasilTopologyDeltaIntelligenceError(f"{label} is malformed")
    result: dict[str, Mapping[str, Any]] = {}
    for record in records:
        if not isinstance(record, Mapping) or not isinstance(record.get("id"), str):
            raise YggdrasilTopologyDeltaIntelligenceError(
                f"{label} contains a malformed record"
            )
        identifier = record["id"]
        if identifier in result:
            raise YggdrasilTopologyDeltaIntelligenceError(
                f"{label} contains duplicate id: {identifier}"
            )
        result[identifier] = record
    return result


def _graph(
    topology: Mapping[str, Any],
) -> tuple[
    dict[str, Mapping[str, Any]],
    dict[str, Mapping[str, Any]],
    dict[str, list[tuple[str, str]]],
]:
    payload = _payload(topology)
    nodes = _index(payload.get("nodes"), "topology nodes")
    edges = _index(payload.get("edges"), "topology edges")
    adjacency: dict[str, list[tuple[str, str]]] = {
        identifier: [] for identifier in nodes
    }
    for edge in edges.values():
        source = edge.get("source")
        target = edge.get("target")
        if source not in nodes or target not in nodes:
            raise YggdrasilTopologyDeltaIntelligenceError(
                f"topology edge has dangling endpoint: {edge['id']}"
            )
        if edge.get("edge_class") not in OPERATIONAL_EDGE_CLASSES:
            continue
        adjacency[source].append((target, edge["id"]))
        adjacency[target].append((source, edge["id"]))
    for identifier in adjacency:
        adjacency[identifier].sort()
    return nodes, edges, adjacency


def _components(adjacency: Mapping[str, Sequence[tuple[str, str]]]) -> list[list[str]]:
    seen: set[str] = set()
    result: list[list[str]] = []
    for start in sorted(adjacency):
        if start in seen:
            continue
        pending = deque([start])
        seen.add(start)
        component: list[str] = []
        while pending:
            node = pending.popleft()
            component.append(node)
            for neighbor, _ in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    pending.append(neighbor)
        result.append(sorted(component))
    return sorted(result, key=lambda component: (component[0], len(component)))


def _shortest_path(
    adjacency: Mapping[str, Sequence[tuple[str, str]]], source: str, target: str
) -> tuple[list[str], list[str]] | None:
    if source not in adjacency or target not in adjacency:
        return None
    pending = deque([source])
    prior: dict[str, tuple[str, str] | None] = {source: None}
    while pending:
        node = pending.popleft()
        if node == target:
            break
        for neighbor, edge_id in adjacency[node]:
            if neighbor not in prior:
                prior[neighbor] = (node, edge_id)
                pending.append(neighbor)
    if target not in prior:
        return None
    nodes = [target]
    edges: list[str] = []
    cursor = target
    while prior[cursor] is not None:
        parent, edge_id = prior[cursor]
        edges.append(edge_id)
        nodes.append(parent)
        cursor = parent
    return list(reversed(nodes)), list(reversed(edges))


def _finding_key(finding: Mapping[str, Any]) -> str:
    entity = finding.get("entity_ref")
    entity_map = entity if isinstance(entity, Mapping) else {}
    return typed_id(
        "correlation",
        finding.get("finding_type"),
        entity_map.get("category"),
        entity_map.get("entity_id"),
        finding.get("subject_key"),
    )


def _finding_map(integrity: Mapping[str, Any] | None) -> dict[str, Mapping[str, Any]]:
    if integrity is None:
        return {}
    payload = integrity.get("payload")
    if not isinstance(payload, Mapping):
        return {}
    findings = _index(payload.get("findings", []), "integrity findings")
    result: dict[str, Mapping[str, Any]] = {}
    for finding in findings.values():
        key = _finding_key(finding)
        if key in result:
            raise YggdrasilTopologyDeltaIntelligenceError(
                f"integrity findings contain duplicate correlation key: {key}"
            )
        result[key] = finding
    return result


def _elapsed_seconds(
    prior_topology: Mapping[str, Any], current_topology: Mapping[str, Any]
) -> int | None:
    try:
        prior = datetime.fromisoformat(
            str(prior_topology["generation"]["generated_at"]).replace("Z", "+00:00")
        )
        current = datetime.fromisoformat(
            str(current_topology["generation"]["generated_at"]).replace("Z", "+00:00")
        )
    except (KeyError, TypeError, ValueError):
        return None
    return max(0, int((current - prior).total_seconds()))


def _evidence_domain_complete(
    integrity: Mapping[str, Any] | None, finding_type: str
) -> bool:
    if integrity is None or not isinstance(integrity.get("payload"), Mapping):
        return False
    sources = {
        source.get("source_key"): source
        for source in integrity.get("source_artifacts", [])
        if isinstance(source, Mapping)
    }
    if finding_type in {"TEMPORAL_REMOVAL", "TEMPORAL_WEAKENING"}:
        return sources.get("temporal_diff", {}).get("integrity_state") == "VERIFIED"
    return sources.get("topology", {}).get("integrity_state") == "VERIFIED"


def _correlations(
    prior_integrity: Mapping[str, Any] | None,
    current_integrity: Mapping[str, Any] | None,
    changed_entity_ids: set[str],
    temporal_entry_ids: Mapping[str, list[str]],
    elapsed_seconds: int | None,
) -> tuple[list[dict[str, Any]], list[str]]:
    if prior_integrity is None or current_integrity is None:
        return [], [
            "Prior and current integrity evidence are required for correlation."
        ]
    prior = _finding_map(prior_integrity)
    current = _finding_map(current_integrity)
    result: list[dict[str, Any]] = []
    findings: list[str] = []
    for key in sorted(set(prior) | set(current)):
        before = prior.get(key)
        after = current.get(key)
        exemplar = after or before
        assert exemplar is not None
        finding_type = str(exemplar["finding_type"])
        if before is None:
            state = "NEW"
        elif after is None:
            if not (
                _evidence_domain_complete(prior_integrity, finding_type)
                and _evidence_domain_complete(current_integrity, finding_type)
            ):
                state = "NOT_COMPUTABLE"
                findings.append(
                    f"Resolution suppressed for {key}: evidence domain is incomplete."
                )
            else:
                state = "RESOLVED"
        else:
            state = "PERSISTENT"
        raw_entity = exemplar.get("entity_ref")
        entity = (
            raw_entity
            if isinstance(raw_entity, Mapping)
            and raw_entity.get("category") in {"TOPOLOGY_NODE", "TOPOLOGY_EDGE"}
            else None
        )
        entity_id = (
            str(entity.get("entity_id")) if isinstance(entity, Mapping) else None
        )
        correlated = entity_id is not None and entity_id in changed_entity_ids
        temporal_ids = sorted(temporal_entry_ids.get(entity_id or "", []))
        supporting_entities = (
            [entity_id] if correlated and entity_id is not None else []
        )
        prior_severity = before.get("severity") if before is not None else None
        current_severity = after.get("severity") if after is not None else None
        if before is not None and after is not None:
            prior_weight = SEVERITY_ORDER.get(str(prior_severity), 0)
            current_weight = SEVERITY_ORDER.get(str(current_severity), 0)
            severity_change = (
                "INCREASED"
                if current_weight > prior_weight
                else "DECREASED"
                if current_weight < prior_weight
                else "UNCHANGED"
            )
        else:
            severity_change = "NOT_COMPUTABLE"
        evidence_refs = ["source:current_integrity", "source:prior_integrity"]
        result.append(
            {
                "id": key,
                "correlation_key": key,
                "state": state,
                "correlation_state": (
                    "CHANGE_CORRELATED"
                    if correlated or temporal_ids
                    else "NOT_COMPUTABLE"
                    if state == "NOT_COMPUTABLE"
                    else "UNCORRELATED"
                ),
                "prior_finding_id": before.get("id") if before is not None else None,
                "current_finding_id": after.get("id") if after is not None else None,
                "entity_ref": copy.deepcopy(entity)
                if isinstance(entity, Mapping)
                else None,
                "subject_key": str(exemplar["subject_key"]),
                "prior_severity": prior_severity,
                "current_severity": current_severity,
                "severity_change": severity_change,
                "provenance": "INFERRED",
                "confidence": (
                    str(after.get("confidence", "SUPPORTED"))
                    if after is not None and state != "NOT_COMPUTABLE"
                    else "NOT_COMPUTABLE"
                ),
                "supporting_entity_ids": supporting_entities,
                "supporting_temporal_entry_ids": temporal_ids,
                "observed_generation_count": 2 if state == "PERSISTENT" else 1,
                "persistence_seconds_lower_bound": (
                    elapsed_seconds if state == "PERSISTENT" else None
                ),
                "true_age_status": "NOT_COMPUTABLE",
                "evidence_refs": evidence_refs,
            }
        )
    return sorted(result, key=lambda entry: entry["id"]), sorted(findings)


def _entity_ref(entity_id: str, edges: Mapping[str, Any]) -> dict[str, str]:
    return {
        "category": "TOPOLOGY_EDGE" if entity_id in edges else "TOPOLOGY_NODE",
        "entity_id": entity_id,
    }


def _structural_record(
    structural_class: str,
    entity_ids: Iterable[str],
    edges: Mapping[str, Any],
    prior_value: Any,
    current_value: Any,
    reason: str,
    *,
    provenance: str = "OBSERVED",
    confidence: str = "VERIFIED",
    evidence_refs: Iterable[str] = (
        "source:current_topology",
        "source:prior_topology",
    ),
) -> dict[str, Any]:
    identifiers = sorted(set(entity_ids))
    return {
        "id": typed_id("structural", structural_class, identifiers),
        "structural_class": structural_class,
        "entity_refs": [_entity_ref(identifier, edges) for identifier in identifiers],
        "prior_value": prior_value,
        "current_value": current_value,
        "provenance": provenance,
        "confidence": confidence,
        "reason": reason,
        "evidence_refs": sorted(set(evidence_refs)),
        "computability": "COMPUTABLE",
    }


def _contract_coverage(
    contract_id: str, edges: Mapping[str, Mapping[str, Any]]
) -> tuple[set[str], set[str], set[str]]:
    producers: set[str] = set()
    consumers: set[str] = set()
    validators: set[str] = set()
    for edge in edges.values():
        edge_class = edge.get("edge_class")
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        if edge_class == "PRODUCES" and target == contract_id:
            producers.add(source)
        elif edge_class == "CONSUMES" and source == contract_id:
            consumers.add(target)
        elif edge_class == "VALIDATES" and target == contract_id:
            validators.add(source)
    return producers, consumers, validators


def _structural_deltas(
    prior_topology: Mapping[str, Any],
    current_topology: Mapping[str, Any],
    temporal_diff: Mapping[str, Any] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str], list[str]]:
    prior_nodes, prior_edges, prior_adjacency = _graph(prior_topology)
    current_nodes, current_edges, current_adjacency = _graph(current_topology)
    complete = (
        prior_topology.get("status") == "AVAILABLE"
        and current_topology.get("status") == "AVAILABLE"
    )
    if not complete:
        return (
            [],
            [],
            set(),
            [
                "Absence-dependent structural conclusions require AVAILABLE topology evidence in both generations."
            ],
        )
    changed = (set(prior_nodes) ^ set(current_nodes)) | (
        set(prior_edges) ^ set(current_edges)
    )
    records: list[dict[str, Any]] = []
    paths: list[dict[str, Any]] = []
    for node_id in sorted(set(current_nodes) - set(prior_nodes)):
        if not current_adjacency[node_id]:
            records.append(
                _structural_record(
                    "ISOLATED_NODE_EMERGENCE",
                    [node_id],
                    current_edges,
                    None,
                    0,
                    "A newly observed node has no operational edge.",
                )
            )
    contract_ids = sorted(
        identifier
        for identifier, node in current_nodes.items()
        if node.get("node_class") == "CONTRACT"
    )
    for contract_id in contract_ids:
        prior_coverage = _contract_coverage(contract_id, prior_edges)
        current_coverage = _contract_coverage(contract_id, current_edges)
        if (
            contract_id in prior_nodes
            and all(prior_coverage[:2])
            and not all(current_coverage[:2])
        ):
            records.append(
                _structural_record(
                    "ORPHANED_CONTRACT",
                    [contract_id],
                    current_edges,
                    {
                        "producer_count": len(prior_coverage[0]),
                        "consumer_count": len(prior_coverage[1]),
                    },
                    {
                        "producer_count": len(current_coverage[0]),
                        "consumer_count": len(current_coverage[1]),
                    },
                    "A contract lost all producer or consumer coverage.",
                )
            )
        if len(current_coverage[2]) < len(prior_coverage[2]):
            records.append(
                _structural_record(
                    "VALIDATOR_COVERAGE_LOSS",
                    [contract_id],
                    current_edges,
                    len(prior_coverage[2]),
                    len(current_coverage[2]),
                    "A contract has fewer validating interfaces than in the prior generation.",
                )
            )
        for producer in sorted(prior_coverage[0]):
            for consumer in sorted(prior_coverage[1]):
                before = _shortest_path(prior_adjacency, producer, consumer)
                after = _shortest_path(current_adjacency, producer, consumer)
                if (
                    before is not None
                    and after is None
                    and producer in current_nodes
                    and consumer in current_nodes
                ):
                    path_id = typed_id("path", producer, consumer, "REMOVED")
                    paths.append(
                        {
                            "id": path_id,
                            "source_id": producer,
                            "target_id": consumer,
                            "change": "REMOVED",
                            "prior_node_ids": sorted(before[0]),
                            "prior_edge_ids": sorted(before[1]),
                            "current_node_ids": [],
                            "current_edge_ids": [],
                            "evidence_refs": [
                                "source:current_topology",
                                "source:prior_topology",
                            ],
                        }
                    )
                    records.append(
                        _structural_record(
                            "BROKEN_PRODUCER_CONSUMER_PATH",
                            [contract_id, producer, consumer],
                            current_edges,
                            before[0],
                            None,
                            "A previously observed producer-to-consumer path is absent.",
                        )
                    )
    prior_evidence = _index(
        _payload(prior_topology).get("evidence", []), "prior evidence"
    )
    current_evidence = _index(
        _payload(current_topology).get("evidence", []), "current evidence"
    )
    for entity_id in sorted(set(prior_nodes) & set(current_nodes)):
        prior_refs = set(prior_nodes[entity_id].get("evidence_refs", []))
        current_refs = set(current_nodes[entity_id].get("evidence_refs", []))
        prior_valid = all(
            prior_evidence.get(ref, {}).get("integrity_state") == "VERIFIED"
            for ref in prior_refs
        )
        current_valid = bool(current_refs) and all(
            current_evidence.get(ref, {}).get("integrity_state") == "VERIFIED"
            for ref in current_refs
        )
        if prior_valid and not current_valid:
            records.append(
                _structural_record(
                    "STALE_EVIDENCE_CHAIN",
                    [entity_id],
                    current_edges,
                    True,
                    False,
                    "An entity lost complete integrity-verified evidence.",
                )
            )
    prior_components = _components(prior_adjacency)
    current_components = _components(current_adjacency)
    if len(current_components) > len(prior_components):
        records.append(
            _structural_record(
                "TOPOLOGY_FRAGMENTATION",
                sorted(changed),
                current_edges,
                len(prior_components),
                len(current_components),
                "The operational topology contains more connected components.",
            )
        )
    prior_component_by_node = {
        node: index
        for index, component in enumerate(prior_components)
        for node in component
    }
    for edge_id in sorted(set(current_edges) - set(prior_edges)):
        edge = current_edges[edge_id]
        source = str(edge.get("source"))
        target = str(edge.get("target"))
        if (
            edge.get("edge_class") in OPERATIONAL_EDGE_CLASSES
            and source in prior_component_by_node
            and target in prior_component_by_node
            and prior_component_by_node[source] != prior_component_by_node[target]
            and (
                edge.get("provenance") == "INFERRED"
                or edge.get("confidence") != "VERIFIED"
            )
        ):
            records.append(
                _structural_record(
                    "UNEXPECTED_CLUSTER_FUSION",
                    [edge_id, source, target],
                    current_edges,
                    prior_component_by_node[source],
                    prior_component_by_node[target],
                    "An inferred or non-verified bridge joins prior operational components.",
                    provenance="INFERRED",
                    confidence=str(edge.get("confidence", "INFERRED")),
                )
            )
    if (
        temporal_diff is not None
        and temporal_diff.get("comparison_status") == "AVAILABLE"
    ):
        for entry in temporal_diff.get("entries", []):
            if (
                entry.get("category") == "OWNERSHIP"
                and entry.get("operation") == "CHANGED"
            ):
                records.append(
                    _structural_record(
                        "OWNERSHIP_DRIFT",
                        [str(entry["entity_id"])],
                        current_edges,
                        entry.get("prior_value"),
                        entry.get("current_value"),
                        "Temporal Diff records an ownership field change.",
                        evidence_refs=["source:temporal_diff"],
                    )
                )
                changed.add(str(entry["entity_id"]))
    return (
        sorted(records, key=lambda entry: entry["id"]),
        sorted(paths, key=lambda entry: entry["id"]),
        changed,
        [],
    )


def _surface_ids(
    entity_ids: Iterable[str],
    nodes: Mapping[str, Mapping[str, Any]],
    adjacency: Mapping[str, Sequence[tuple[str, str]]],
) -> list[str]:
    surfaces = {
        identifier
        for identifier, node in nodes.items()
        if node.get("node_class") in {"SYSTEM", "ROUTE"}
        or (
            node.get("node_class") == "INTERFACE"
            and "OPERATOR" in node.get("roles", [])
        )
    }
    found: set[str] = set()
    for start in sorted(set(entity_ids) & set(nodes)):
        pending = deque([(start, 0)])
        seen = {start}
        while pending:
            node, depth = pending.popleft()
            if node in surfaces:
                found.add(node)
            if depth == 3:
                continue
            for neighbor, _ in adjacency[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    pending.append((neighbor, depth + 1))
    return sorted(found)


def _surface_score(count: int) -> int:
    if count == 0:
        return 0
    if count == 1:
        return 8
    if count <= 4:
        return 14
    return 20


def _priorities(
    correlations: Sequence[Mapping[str, Any]],
    structural: Sequence[Mapping[str, Any]],
    current_topology: Mapping[str, Any],
) -> list[dict[str, Any]]:
    nodes, _, adjacency = _graph(current_topology)
    structural_by_entity: dict[str, list[Mapping[str, Any]]] = {}
    for record in structural:
        for reference in record["entity_refs"]:
            structural_by_entity.setdefault(reference["entity_id"], []).append(record)
    candidates: list[dict[str, Any]] = []
    for correlation in correlations:
        if correlation["state"] not in {"NEW", "PERSISTENT"}:
            continue
        entity = correlation.get("entity_ref")
        entity_id = entity.get("entity_id") if isinstance(entity, Mapping) else None
        related = structural_by_entity.get(str(entity_id), [])
        classes = sorted({record["structural_class"] for record in related})
        surfaces = _surface_ids([str(entity_id)] if entity_id else [], nodes, adjacency)
        severity = str(correlation.get("current_severity") or "INFO")
        confidence = str(correlation.get("confidence", "INFERRED"))
        breakdown = {
            "severity": SEVERITY_WEIGHTS.get(severity, 0),
            "structural": max(
                (STRUCTURAL_WEIGHTS[value] for value in classes), default=0
            ),
            "operational_surfaces": _surface_score(len(surfaces)),
            "persistence": 10 if correlation["state"] == "PERSISTENT" else 5,
            "confidence": CONFIDENCE_WEIGHTS.get(confidence, 0),
        }
        evidence_refs = sorted(set(correlation.get("evidence_refs", [])))
        candidates.append(
            {
                "id": typed_id("priority", correlation["id"]),
                "rank": 0,
                "source_ref": {
                    "category": "INTEGRITY_FINDING",
                    "entity_id": correlation["id"],
                },
                "score": min(100, sum(breakdown.values())),
                "score_breakdown": breakdown,
                "severity": severity,
                "structural_classes": classes,
                "confidence": confidence,
                "evidence_count": len(evidence_refs),
                "affected_surface_ids": surfaces,
                "why_this_matters": (
                    f"{correlation['state'].title()} {severity.lower()} integrity finding"
                    + (
                        f" with {', '.join(value.lower() for value in classes)}."
                        if classes
                        else "."
                    )
                ),
                "evidence_refs": evidence_refs,
            }
        )
    covered_structural = {
        value for candidate in candidates for value in candidate["structural_classes"]
    }
    for record in structural:
        if record["structural_class"] in covered_structural:
            continue
        entity_ids = [reference["entity_id"] for reference in record["entity_refs"]]
        surfaces = _surface_ids(entity_ids, nodes, adjacency)
        confidence = str(record["confidence"])
        breakdown = {
            "severity": 25,
            "structural": STRUCTURAL_WEIGHTS[record["structural_class"]],
            "operational_surfaces": _surface_score(len(surfaces)),
            "persistence": 5,
            "confidence": CONFIDENCE_WEIGHTS.get(confidence, 0),
        }
        candidates.append(
            {
                "id": typed_id("priority", record["id"]),
                "rank": 0,
                "source_ref": {
                    "category": "STRUCTURAL_DELTA",
                    "entity_id": record["id"],
                },
                "score": min(100, sum(breakdown.values())),
                "score_breakdown": breakdown,
                "severity": "MEDIUM",
                "structural_classes": [record["structural_class"]],
                "confidence": confidence,
                "evidence_count": len(record["evidence_refs"]),
                "affected_surface_ids": surfaces,
                "why_this_matters": record["reason"],
                "evidence_refs": record["evidence_refs"],
            }
        )
    ordered = sorted(
        candidates,
        key=lambda item: (
            -item["score"],
            -SEVERITY_ORDER[item["severity"]],
            -item["evidence_count"],
            item["id"],
        ),
    )
    for rank, item in enumerate(ordered, start=1):
        item["rank"] = rank
    return ordered


def _section(
    entries: list[dict[str, Any]] | None,
    *,
    findings: Iterable[str] = (),
    provenance: str = "INFERRED",
) -> dict[str, Any]:
    warnings = sorted(set(findings))
    if entries is None:
        return {
            "status": "NOT_COMPUTABLE",
            "provenance": provenance,
            "not_computable_reason": warnings[0]
            if warnings
            else "Required evidence is unavailable.",
            "validation_findings": warnings,
            "entries": None,
        }
    return {
        "status": "PARTIAL" if warnings else "AVAILABLE",
        "provenance": provenance,
        "not_computable_reason": None,
        "validation_findings": warnings,
        "entries": entries,
    }


def _summary(sections: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    correlations = sections["finding_correlation"].get("entries") or []
    structural = sections["structural_deltas"].get("entries") or []
    paths = sections["changed_paths"].get("entries") or []
    priorities = sections["review_priorities"].get("entries") or []
    return {
        "finding_state_counts": dict(
            sorted(Counter(entry["state"] for entry in correlations).items())
        ),
        "structural_class_counts": dict(
            sorted(Counter(entry["structural_class"] for entry in structural).items())
        ),
        "changed_path_count": len(paths),
        "active_priority_count": len(priorities),
        "not_computable_count": sum(
            section["status"] == "NOT_COMPUTABLE" for section in sections.values()
        ),
        "highest_score": max((entry["score"] for entry in priorities), default=None),
    }


def evaluate_yggdrasil_topology_delta_intelligence(
    prior_topology: Mapping[str, Any],
    current_topology: Mapping[str, Any],
    *,
    prior_integrity: Mapping[str, Any] | None = None,
    current_integrity: Mapping[str, Any] | None = None,
    temporal_diff: Mapping[str, Any] | None = None,
    source_paths: Mapping[str, str],
    content_hashes: Mapping[str, str | None],
    generated_at: str,
) -> dict[str, Any]:
    """Interpret an explicit prior/current pair without discovery or retention."""
    prior_generation = prior_topology["generation"]
    current_generation = current_topology["generation"]
    prior_topology_id = str(prior_generation["topology_generation_id"])
    current_topology_id = str(current_generation["topology_generation_id"])
    prior_operator_id = str(prior_generation["operator_platform_generation_id"])
    current_operator_id = str(current_generation["operator_platform_generation_id"])
    sources = sorted(
        [
            _source(key, source_paths[key], artifact, content_hashes.get(key))
            for key, artifact in (
                ("prior_topology", prior_topology),
                ("current_topology", current_topology),
                ("prior_integrity", prior_integrity),
                ("current_integrity", current_integrity),
                ("temporal_diff", temporal_diff),
            )
        ],
        key=lambda item: item["id"],
    )
    validation_findings: list[str] = []
    usable_prior_integrity = prior_integrity
    usable_current_integrity = current_integrity
    usable_temporal = temporal_diff
    if (
        prior_integrity is not None
        and prior_integrity["generation"]["topology_generation_id"] != prior_topology_id
    ):
        usable_prior_integrity = None
        validation_findings.append(
            "Prior integrity generation binding mismatch; evidence was suppressed."
        )
    if (
        current_integrity is not None
        and current_integrity["generation"]["topology_generation_id"]
        != current_topology_id
    ):
        usable_current_integrity = None
        validation_findings.append(
            "Current integrity generation binding mismatch; evidence was suppressed."
        )
    if temporal_diff is not None and (
        temporal_diff["prior_generation"]["generation_id"] != prior_operator_id
        or temporal_diff["current_generation"]["generation_id"] != current_operator_id
    ):
        usable_temporal = None
        validation_findings.append(
            "Temporal Diff generation binding mismatch; evidence was suppressed."
        )
    temporal_by_entity: dict[str, list[str]] = {}
    if usable_temporal is not None:
        for entry in usable_temporal.get("entries", []):
            temporal_by_entity.setdefault(str(entry.get("entity_id")), []).append(
                str(entry["id"])
            )
    structural, paths, changed_ids, structural_findings = _structural_deltas(
        prior_topology, current_topology, usable_temporal
    )
    path_findings = list(structural_findings)
    if temporal_diff is None:
        message = (
            "Temporal Diff evidence was unavailable; ownership drift is not computable."
        )
        validation_findings.append(message)
        structural_findings.append(message)
    elif usable_temporal is None:
        structural_findings.append(
            "Temporal Diff generation mismatch suppressed ownership drift conclusions."
        )
    correlations, correlation_findings = _correlations(
        usable_prior_integrity,
        usable_current_integrity,
        changed_ids,
        temporal_by_entity,
        _elapsed_seconds(prior_topology, current_topology),
    )
    priorities = _priorities(correlations, structural, current_topology)
    topology_complete = (
        prior_topology.get("status") == "AVAILABLE"
        and current_topology.get("status") == "AVAILABLE"
    )
    sections = {
        "finding_correlation": _section(
            correlations
            if usable_prior_integrity is not None
            and usable_current_integrity is not None
            else None,
            findings=correlation_findings,
        ),
        "structural_deltas": _section(
            structural if topology_complete else None, findings=structural_findings
        ),
        "changed_paths": _section(
            paths if topology_complete else None, findings=path_findings
        ),
        "review_priorities": _section(priorities),
    }
    generation = {
        "generated_at": generated_at,
        "generated_by": GENERATED_BY,
        "delta_generation_id": "0" * 64,
        "prior_topology_generation_id": prior_topology_id,
        "current_topology_generation_id": current_topology_id,
        "prior_operator_platform_generation_id": prior_operator_id,
        "current_operator_platform_generation_id": current_operator_id,
        "prior_integrity_generation_id": usable_prior_integrity["generation"][
            "integrity_generation_id"
        ]
        if usable_prior_integrity is not None
        else None,
        "current_integrity_generation_id": usable_current_integrity["generation"][
            "integrity_generation_id"
        ]
        if usable_current_integrity is not None
        else None,
        "temporal_diff_generation_id": current_operator_id
        if usable_temporal is not None
        else None,
    }
    artifact: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generation": generation,
        "status": "PARTIAL"
        if validation_findings
        or any(section["status"] != "AVAILABLE" for section in sections.values())
        else "AVAILABLE",
        "provenance": "INFERRED",
        "source_artifacts": sources,
        "sections": sections,
        "summary": _summary(sections),
        "authority": dict(AUTHORITY),
        "validation_findings": sorted(validation_findings),
        "canonical_hash": "0" * 64,
    }
    artifact["generation"]["delta_generation_id"] = _generation_id(artifact)
    artifact["canonical_hash"] = _canonical_hash(artifact)
    return artifact


def validate_yggdrasil_topology_delta_intelligence(
    artifact: Mapping[str, Any], schema_path: Path
) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema).iter_errors(artifact),
        key=lambda error: list(error.path),
    )
    if errors:
        raise YggdrasilTopologyDeltaIntelligenceError(
            f"delta intelligence schema violation: {errors[0].message}"
        )
    if artifact.get("authority") != AUTHORITY:
        raise YggdrasilTopologyDeltaIntelligenceError(
            "delta intelligence authority locks are malformed"
        )
    if artifact.get("canonical_hash") != _canonical_hash(artifact):
        raise YggdrasilTopologyDeltaIntelligenceError(
            "delta intelligence canonical hash mismatch"
        )
    if artifact["generation"]["delta_generation_id"] != _generation_id(artifact):
        raise YggdrasilTopologyDeltaIntelligenceError(
            "delta intelligence generation id mismatch"
        )
    if artifact["source_artifacts"] != sorted(
        artifact["source_artifacts"], key=lambda item: item["id"]
    ):
        raise YggdrasilTopologyDeltaIntelligenceError(
            "delta intelligence sources are not canonically ordered"
        )
    if artifact["validation_findings"] != sorted(artifact["validation_findings"]):
        raise YggdrasilTopologyDeltaIntelligenceError(
            "delta intelligence findings are not canonically ordered"
        )
    all_ids: set[str] = set()
    for name, section in artifact["sections"].items():
        entries = section["entries"]
        if section["status"] == "NOT_COMPUTABLE":
            if entries is not None or not section["not_computable_reason"]:
                raise YggdrasilTopologyDeltaIntelligenceError(
                    f"{name} NOT_COMPUTABLE envelope mismatch"
                )
            continue
        if entries is None or section["not_computable_reason"] is not None:
            raise YggdrasilTopologyDeltaIntelligenceError(
                f"{name} available envelope mismatch"
            )
        identifiers = [entry["id"] for entry in entries]
        if len(identifiers) != len(set(identifiers)):
            raise YggdrasilTopologyDeltaIntelligenceError(f"duplicate {name} id")
        if name != "review_priorities" and identifiers != sorted(identifiers):
            raise YggdrasilTopologyDeltaIntelligenceError(
                f"{name} is not canonically ordered"
            )
        all_ids.update(identifiers)
    priorities = artifact["sections"]["review_priorities"]["entries"] or []
    expected = sorted(
        priorities,
        key=lambda item: (
            -item["score"],
            -SEVERITY_ORDER[item["severity"]],
            -item["evidence_count"],
            item["id"],
        ),
    )
    if priorities != expected or [item["rank"] for item in priorities] != list(
        range(1, len(priorities) + 1)
    ):
        raise YggdrasilTopologyDeltaIntelligenceError(
            "review priorities are not canonically ordered"
        )
    for item in priorities:
        if item["score"] != min(100, sum(item["score_breakdown"].values())):
            raise YggdrasilTopologyDeltaIntelligenceError(
                "priority score arithmetic mismatch"
            )
        if item["source_ref"]["entity_id"] not in all_ids:
            raise YggdrasilTopologyDeltaIntelligenceError(
                "priority has a dangling source reference"
            )
    if artifact["summary"] != _summary(artifact["sections"]):
        raise YggdrasilTopologyDeltaIntelligenceError(
            "delta intelligence summary mismatch"
        )
