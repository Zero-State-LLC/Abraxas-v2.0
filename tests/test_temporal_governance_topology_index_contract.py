import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_topology import *


def _continuity(posture="STABLE", status="CONTINUITY_STABLE", blocked=False, nondet=False, score=0.9):
    findings = []
    if blocked:
        findings.append({"finding_type": "BLOCKED_HISTORY_PRESSURE"})
    if nondet:
        findings.append({"finding_type": "NONDETERMINISM_PRESSURE"})
    return {"index_id": "idx", "continuity_posture": posture, "index_status": status, "continuity_score": score, "findings": tuple(findings)}


def test_topology_derivation_rules():
    assert derive_temporal_governance_topology_index([]).topology_status == "NOT_COMPUTABLE"
    one = derive_temporal_governance_topology_index([_continuity()])
    assert one.topology_status == "INSUFFICIENT_GRAPH"
    stable = derive_temporal_governance_topology_index([_continuity(), dict(_continuity(), index_id="idx2")])
    assert stable.topology_status == "TOPOLOGY_STABLE"
    mixed = derive_temporal_governance_topology_index([_continuity(), _continuity(posture="MIXED", status="CONTINUITY_MIXED", score=0.7)])
    assert mixed.topology_status in {"PRESSURE_HOTSPOTS_PRESENT", "OPERATOR_REVIEW_REQUIRED", "TOPOLOGY_READY"}
    unstable = derive_temporal_governance_topology_index([_continuity(posture="UNSTABLE", status="CONTINUITY_UNSTABLE", blocked=True), _continuity(nondet=True, status="OPERATOR_REVIEW_REQUIRED", posture="UNSTABLE")])
    assert unstable.topology_status in {"FRACTURE_ZONES_PRESENT", "TOPOLOGY_UNSTABLE", "OPERATOR_REVIEW_REQUIRED"}
    assert any(h.hotspot_type == "BLOCKED_PRESSURE" for h in unstable.pressure_hotspots) or len(unstable.fracture_zones) > 0
    assert any(h.hotspot_type == "NONDETERMINISM_PRESSURE" for h in unstable.pressure_hotspots) or len(unstable.fracture_zones) > 0


def test_validation_hash_schema_and_audit():
    base = derive_temporal_governance_topology_index([_continuity(), dict(_continuity(), index_id="idx2")])
    assert validate_temporal_governance_topology_index(replace(base, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_governance_topology_index(replace(base, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_governance_topology_index(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_governance_topology_index(replace(base, canonical_selection_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_governance_topology_index(replace(base, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_governance_topology_index(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badn = replace(base, nodes=(replace(base.nodes[0], mutation_allowed=True),) + base.nodes[1:])
    assert validate_temporal_governance_topology_index(badn).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bade = replace(base, edges=(replace(base.edges[0], routing_change_allowed=True),))
    assert validate_temporal_governance_topology_index(bade).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badf1 = replace(base, fracture_zones=(TemporalFractureZone("fz", ("n-1",), ("e-1",), "LINEAGE_FRACTURE", 0.9, False, False),))
    assert validate_temporal_governance_topology_index(badf1).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badf2 = replace(base, fracture_zones=(TemporalFractureZone("fz", ("n-1",), ("e-1",), "LINEAGE_FRACTURE", 0.9, True, True),))
    assert validate_temporal_governance_topology_index(badf2).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badr = replace(base, recommendations=(replace(base.recommendations[0], routing_change_allowed=True),))
    assert validate_temporal_governance_topology_index(badr).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_governance_topology_index(replace(base, created_by_lane="SHADOW", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_governance_topology_index(replace(base, created_by_lane="PROJECTION", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base)); alt["topology_hash"] = "x"
    assert temporal_governance_topology_index_hash(base) == temporal_governance_topology_index_hash(alt)
    assert canonical_temporal_governance_topology_index_json(base) == canonical_temporal_governance_topology_index_json(base)

    s = json.loads(open("contracts/temporal_topology/temporal_governance_topology_index.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))
    d = dict(asdict(base)); d.pop("topology_id")
    assert "topology_id" in s["required"] and "topology_id" not in d

    h = write_temporal_governance_topology_index_contract_audit(".")
    t = open("out/audit/temporal_governance_topology_index_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
