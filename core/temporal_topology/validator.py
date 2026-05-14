from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import TemporalGovernanceTopologyIndex, TemporalTopologyValidationFinding, TemporalTopologyValidationReport


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_temporal_governance_topology_index(index: TemporalGovernanceTopologyIndex | Mapping[str, Any]) -> TemporalTopologyValidationReport:
    i = index if isinstance(index, TemporalGovernanceTopologyIndex) else TemporalGovernanceTopologyIndex(**dict(index))
    findings = []
    status = "PASS"
    if i.history_rewrite_allowed or i.ledger_mutation_allowed or i.timeline_collapse_allowed or i.canonical_selection_allowed or i.live_execution_allowed or i.routing_change_allowed:
        findings.append(TemporalTopologyValidationFinding("FLAGS_FORBIDDEN", "error", "rewrite/mutation/collapse/selection/execution/routing must be false."))
        status = "BLOCKED"
    if any(n.mutation_allowed for n in i.nodes):
        findings.append(TemporalTopologyValidationFinding("NODE_MUTATION_FORBIDDEN", "error", "nodes[*].mutation_allowed must be false."))
        status = "BLOCKED"
    if any(e.routing_change_allowed for e in i.edges):
        findings.append(TemporalTopologyValidationFinding("EDGE_ROUTING_FORBIDDEN", "error", "edges[*].routing_change_allowed must be false."))
        status = "BLOCKED"
    if any((not f.lineages_preserved) or f.normalization_allowed for f in i.fracture_zones):
        findings.append(TemporalTopologyValidationFinding("FRACTURE_INTEGRITY_FORBIDDEN", "error", "fracture_zones must preserve lineages and disallow normalization."))
        status = "BLOCKED"
    if any(r.history_rewrite_allowed or r.ledger_mutation_allowed or r.timeline_collapse_allowed or r.canonical_selection_allowed or r.routing_change_allowed for r in i.recommendations):
        findings.append(TemporalTopologyValidationFinding("RECOMMENDATION_FLAGS_FORBIDDEN", "error", "recommendation flags must be false."))
        status = "BLOCKED"
    if i.topology_status == "TOPOLOGY_STABLE" and not (i.topology_posture == "STABLE" and len(i.pressure_hotspots) == 0 and len(i.fracture_zones) == 0):
        findings.append(TemporalTopologyValidationFinding("STABLE_CONSTRAINT", "error", "TOPOLOGY_STABLE requires STABLE posture and no hotspots/fracture zones."))
        status = "BLOCKED"
    if i.topology_status == "PRESSURE_HOTSPOTS_PRESENT" and len(i.pressure_hotspots) < 1:
        findings.append(TemporalTopologyValidationFinding("HOTSPOT_CONSTRAINT", "error", "PRESSURE_HOTSPOTS_PRESENT requires at least one pressure hotspot."))
        status = "BLOCKED"
    if i.topology_status == "FRACTURE_ZONES_PRESENT" and len(i.fracture_zones) < 1:
        findings.append(TemporalTopologyValidationFinding("FRACTURE_CONSTRAINT", "error", "FRACTURE_ZONES_PRESENT requires at least one fracture zone."))
        status = "BLOCKED"
    if i.topology_status == "TOPOLOGY_UNSTABLE" and not (i.topology_posture == "UNSTABLE" or any(h.severity == "BLOCKED" for h in i.pressure_hotspots) or len(i.fracture_zones) > 0):
        findings.append(TemporalTopologyValidationFinding("UNSTABLE_CONSTRAINT", "error", "TOPOLOGY_UNSTABLE requires UNSTABLE posture or blocked/fracture findings."))
        status = "BLOCKED"
    if i.topology_status == "INSUFFICIENT_GRAPH" and not (len(i.nodes) < 2 or len(i.edges) < 1 or len(i.input_refs) == 0):
        findings.append(TemporalTopologyValidationFinding("INSUFFICIENT_GRAPH_CONSTRAINT", "error", "INSUFFICIENT_GRAPH requires insufficient graph condition."))
        status = "BLOCKED"
    if i.topology_status == "OPERATOR_REVIEW_REQUIRED" and not any(r.operator_review_required for r in i.recommendations):
        findings.append(TemporalTopologyValidationFinding("REVIEW_REQUIRED_MISSING", "error", "OPERATOR_REVIEW_REQUIRED requires operator_review_required recommendation."))
        status = "BLOCKED"
    if i.created_by_lane == "SHADOW" and i.topology_status == "TOPOLOGY_STABLE" and i.authority_ref is not None:
        findings.append(TemporalTopologyValidationFinding("SHADOW_STABLE_AUTH_BLOCKED", "error", "SHADOW cannot mark TOPOLOGY_STABLE authoritative."))
        status = "BLOCKED"
    if i.created_by_lane == "FORECAST" and i.topology_status == "TOPOLOGY_STABLE" and i.authority_ref is not None:
        findings.append(TemporalTopologyValidationFinding("FORECAST_STABLE_AUTH_BLOCKED", "error", "FORECAST cannot mark STABLE authoritative."))
        status = "BLOCKED"
    if i.created_by_lane == "PROJECTION" and i.authority_ref is not None:
        findings.append(TemporalTopologyValidationFinding("PROJECTION_AUTH_BLOCKED", "error", "PROJECTION cannot create topology authority."))
        status = "BLOCKED"
    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "topology_id": i.topology_id}))
    return TemporalTopologyValidationReport(status, tuple(findings), receipt_hash)
