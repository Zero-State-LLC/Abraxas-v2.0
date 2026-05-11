from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import *
from .validator import validate_temporal_governance_topology_index

SCHEMA_VERSION = "TemporalGovernanceTopologyIndex.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_temporal_governance_topology_index_json(index: TemporalGovernanceTopologyIndex | Mapping[str, Any]) -> str:
    payload = asdict(index) if isinstance(index, TemporalGovernanceTopologyIndex) else dict(index)
    payload.pop("topology_hash", None)
    return _canonical_json(payload)


def temporal_governance_topology_index_hash(index: TemporalGovernanceTopologyIndex | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_temporal_governance_topology_index_json(index))


def compute_topology_posture(nodes: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]], pressure_hotspots: Sequence[Mapping[str, Any]], fracture_zones: Sequence[Mapping[str, Any]]) -> str:
    if not nodes:
        return "INSUFFICIENT_GRAPH"
    if fracture_zones:
        return "UNSTABLE" if len(fracture_zones) > 1 or any(float(z.get("fracture_score", 0.0)) >= 0.85 for z in fracture_zones) else "FRACTURED"
    if pressure_hotspots:
        if any(str(h.get("severity", "")) == "BLOCKED" for h in pressure_hotspots):
            return "UNSTABLE"
        return "HOTSPOT_PRESSURE" if any(float(h.get("pressure_score", 0.0)) >= 0.55 for h in pressure_hotspots) else "WATCH"
    if all(str(n.get("node_posture", "")) == "STABLE" for n in nodes):
        return "STABLE"
    return "WATCH" if edges else "INSUFFICIENT_GRAPH"


def build_temporal_governance_topology_index(topology_id: str, input_refs: tuple[TemporalTopologyInputRef, ...], nodes: tuple[TemporalTopologyNode, ...], edges: tuple[TemporalTopologyEdge, ...], pressure_hotspots: tuple[TemporalPressureHotspot, ...], fracture_zones: tuple[TemporalFractureZone, ...], metrics: tuple[TemporalTopologyMetric, ...], recommendations: tuple[TemporalTopologyRecommendation, ...], topology_status: str, topology_posture: str, topology_policy: str, created_by_lane: str, authority_ref: dict | None) -> TemporalGovernanceTopologyIndex:
    draft = TemporalGovernanceTopologyIndex(SCHEMA_VERSION, topology_id, input_refs, nodes, edges, pressure_hotspots, fracture_zones, metrics, recommendations, topology_status, topology_posture, topology_policy, created_by_lane, authority_ref, False, False, False, False, False, False, "PENDING")
    return replace(draft, topology_hash=temporal_governance_topology_index_hash(draft))


def derive_temporal_governance_topology_index(continuity_indexes: Sequence[Mapping[str, Any]], input_refs: Sequence[Mapping[str, Any]] | None = None) -> TemporalGovernanceTopologyIndex:
    refs = tuple(TemporalTopologyInputRef(str(r.get("source_type", "NOT_COMPUTABLE")), str(r.get("source_id", "")), str(r.get("source_hash", ""))) for r in (input_refs or []))
    if not continuity_indexes:
        rec = (TemporalTopologyRecommendation("rec-1", "NOT_COMPUTABLE", "Topology not computable without continuity indexes.", True, False, False, False, False, False),)
        m = (TemporalTopologyMetric("m-pressure", "NOT_COMPUTABLE", 0.0, "PRESERVE_ALL_LINEAGES", "NOT_COMPUTABLE"),)
        return build_temporal_governance_topology_index("topology-1", refs, tuple(), tuple(), tuple(), tuple(), m, rec, "NOT_COMPUTABLE", "NOT_COMPUTABLE", "PRESERVE_ALL_LINEAGES", "FORECAST", None)

    nodes = []
    edges = []
    hotspots = []
    fractures = []
    for i, idx in enumerate(continuity_indexes, start=1):
        posture = str(idx.get("continuity_posture", "NOT_COMPUTABLE"))
        status = str(idx.get("index_status", "NOT_COMPUTABLE"))
        blocked = 1.0 if any(f.get("finding_type") == "BLOCKED_HISTORY_PRESSURE" for f in idx.get("findings", ())) else 0.0
        nondet = 1.0 if any(f.get("finding_type") == "NONDETERMINISM_PRESSURE" for f in idx.get("findings", ())) else 0.0
        fracture_pressure = 1.0 if status in {"CONTINUITY_UNSTABLE", "OPERATOR_REVIEW_REQUIRED"} else 0.0
        node_posture = "STABLE" if posture == "STABLE" and blocked == 0 and nondet == 0 else ("UNSTABLE" if fracture_pressure > 0 else "WATCH")
        nodes.append(TemporalTopologyNode(f"n-{i}", "CONTINUITY_INDEX", str(idx.get("index_id", f"idx-{i}")), posture, float(idx.get("continuity_score", 0.0)), blocked, nondet, fracture_pressure, node_posture, False))
        if blocked > 0:
            hotspots.append(TemporalPressureHotspot(f"h-b-{i}", (f"n-{i}",), "BLOCKED_PRESSURE", blocked, "BLOCKED", True))
        if nondet > 0:
            hotspots.append(TemporalPressureHotspot(f"h-n-{i}", (f"n-{i}",), "NONDETERMINISM_PRESSURE", nondet, "BLOCKED", True))
        if fracture_pressure > 0:
            hotspots.append(TemporalPressureHotspot(f"h-f-{i}", (f"n-{i}",), "FRACTURE_PRESSURE", fracture_pressure, "WARN", True))

    for i in range(1, len(nodes)):
        s = nodes[i - 1]
        t = nodes[i]
        p = round(max(s.fracture_pressure, t.fracture_pressure, s.blocked_pressure, t.blocked_pressure, s.nondeterminism_pressure, t.nondeterminism_pressure), 10)
        epost = "FRACTURED" if p >= 0.85 else ("AMPLIFYING" if p >= 0.55 else "STABLE")
        edges.append(TemporalTopologyEdge(f"e-{i}", s.node_id, t.node_id, "PRESSURE_PROPAGATION", 1.0, p, epost, False))

    if any(n.fracture_pressure > 0 for n in nodes):
        f_edges = tuple(e.edge_id for e in edges if e.edge_posture in {"FRACTURED", "AMPLIFYING"})
        fractures.append(TemporalFractureZone("fz-1", tuple(n.node_id for n in nodes if n.fracture_pressure > 0 or n.blocked_pressure > 0 or n.nondeterminism_pressure > 0), f_edges, "REPLAY_DETERMINISM_FRACTURE", max((n.fracture_pressure for n in nodes), default=0.0), True, False))

    posture = compute_topology_posture([asdict(n) for n in nodes], [asdict(e) for e in edges], [asdict(h) for h in hotspots], [asdict(f) for f in fractures])

    if len(nodes) < 2 or len(edges) < 1:
        status = "INSUFFICIENT_GRAPH"
    elif fractures:
        status = "FRACTURE_ZONES_PRESENT" if posture == "FRACTURED" else "TOPOLOGY_UNSTABLE"
    elif hotspots:
        status = "OPERATOR_REVIEW_REQUIRED" if any(h.severity == "BLOCKED" for h in hotspots) else "PRESSURE_HOTSPOTS_PRESENT"
    elif posture == "STABLE":
        status = "TOPOLOGY_STABLE"
    else:
        status = "TOPOLOGY_READY"

    metrics = (
        TemporalTopologyMetric("m-pressure", "TOPOLOGY_PRESSURE", round(sum(n.pressure_score for n in nodes) / max(1, len(nodes)), 10), "PRESERVE_ALL_LINEAGES", "PASS" if posture == "STABLE" else ("BLOCKED" if posture in {"UNSTABLE", "FRACTURED"} else "WARN")),
        TemporalTopologyMetric("m-hotspots", "HOTSPOT_COUNT", float(len(hotspots)), "PRESERVE_ALL_LINEAGES", "WARN" if hotspots else "PASS"),
        TemporalTopologyMetric("m-fractures", "FRACTURE_ZONE_COUNT", float(len(fractures)), "PRESERVE_ALL_LINEAGES", "BLOCKED" if fractures else "PASS"),
    )
    rec = (TemporalTopologyRecommendation("rec-1", "RECOMMEND_OPERATOR_REVIEW" if status in {"OPERATOR_REVIEW_REQUIRED", "FRACTURE_ZONES_PRESENT", "TOPOLOGY_UNSTABLE", "PRESSURE_HOTSPOTS_PRESENT", "INSUFFICIENT_GRAPH"} else "RECOMMEND_TOPOLOGY_MONITORING", "Deterministic temporal topology recommendation.", True, False, False, False, False, False),)
    return build_temporal_governance_topology_index("topology-1", refs, tuple(nodes), tuple(edges), tuple(hotspots), tuple(fractures), metrics, rec, status, posture, "PRESERVE_ALL_LINEAGES", "FORECAST", None)


def write_temporal_governance_topology_index_contract_audit(base_dir: Path | str = ".") -> str:
    topology = derive_temporal_governance_topology_index([
        {"index_id": "idx-1", "index_status": "CONTINUITY_STABLE", "continuity_posture": "STABLE", "continuity_score": 0.92, "findings": ()},
        {"index_id": "idx-2", "index_status": "CONTINUITY_STABLE", "continuity_posture": "STABLE", "continuity_score": 0.91, "findings": ()},
    ], [{"source_type": "TEMPORAL_CONTINUITY_INDEX", "source_id": "idx-1", "source_hash": "h1"}, {"source_type": "TEMPORAL_CONTINUITY_INDEX", "source_id": "idx-2", "source_hash": "h2"}])
    report = validate_temporal_governance_topology_index(topology)
    payload = {"status": report.status, "topology_hash": topology.topology_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": topology.schema_version}
    text = _canonical_json(payload) + "\n"
    out = Path(base_dir) / "out/audit/temporal_governance_topology_index_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
