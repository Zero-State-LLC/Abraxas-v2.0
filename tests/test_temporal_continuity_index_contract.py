import hashlib
import json
from dataclasses import asdict, replace

from core.temporal_continuity.index import canonical_temporal_continuity_index_json, compute_temporal_continuity_score, derive_temporal_continuity_index, temporal_continuity_index_hash, write_temporal_continuity_index_contract_audit
from core.temporal_continuity.validator import validate_temporal_continuity_index


def _review(status="CONSENSUS_PRESENT", blocked=False, nondet=False):
    findings = []
    if blocked:
        findings.append({"finding_type": "BLOCKED_HISTORY_PRESENT", "severity": "BLOCKED"})
    if nondet:
        findings.append({"finding_type": "NONDETERMINISM_PRESSURE", "severity": "BLOCKED"})
    return {"review_status": status, "consensus_findings": tuple(findings)}


def test_temporal_continuity_derivation_rules():
    assert derive_temporal_continuity_index([]).index_status == "NOT_COMPUTABLE"
    one = derive_temporal_continuity_index([_review()])
    assert one.index_status == "INSUFFICIENT_HISTORY"
    strong = derive_temporal_continuity_index([_review(), _review()])
    assert strong.index_status == "CONTINUITY_STABLE"
    mixed = derive_temporal_continuity_index([_review(), _review("PARTIAL_CONSENSUS")])
    assert mixed.index_status == "CONTINUITY_MIXED"
    unstable = derive_temporal_continuity_index([_review("CONSENSUS_CONFLICT"), _review("CONSENSUS_PRESENT", blocked=True)])
    assert unstable.index_status in {"CONTINUITY_UNSTABLE", "OPERATOR_REVIEW_REQUIRED"}
    assert any(f.finding_type == "BLOCKED_HISTORY_PRESSURE" for f in unstable.findings)
    nd = derive_temporal_continuity_index([_review(nondet=True), _review()])
    assert any(f.finding_type == "NONDETERMINISM_PRESSURE" for f in nd.findings)


def test_score_and_validation_hash_schema_audit(tmp_path):
    assert compute_temporal_continuity_score([{"normalized_score": 0.9, "weight": 1.0}])[1] == "STABLE"
    assert compute_temporal_continuity_score([{"normalized_score": 0.7, "weight": 1.0}])[1] == "MIXED"
    assert compute_temporal_continuity_score([{"normalized_score": 0.2, "weight": 1.0}])[1] == "UNSTABLE"
    assert compute_temporal_continuity_score([{"normalized_score": 0.8, "weight": 0.0}])[1] == "NOT_COMPUTABLE"

    base = derive_temporal_continuity_index([_review(), _review()])
    assert validate_temporal_continuity_index(replace(base, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_continuity_index(replace(base, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_continuity_index(replace(base, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_continuity_index(replace(base, canonical_selection_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_continuity_index(replace(base, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_continuity_index(replace(base, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_comp = replace(base, component_scores=(replace(base.component_scores[0], mutation_allowed=True),) + base.component_scores[1:])
    assert validate_temporal_continuity_index(bad_comp).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_find = replace(base, findings=(replace(base.findings[0], normalization_allowed=True),))
    assert validate_temporal_continuity_index(bad_find).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bad_rec = replace(base, recommendations=(replace(base.recommendations[0], canonical_selection_allowed=True),))
    assert validate_temporal_continuity_index(bad_rec).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_continuity_index(replace(base, created_by_lane="SHADOW", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_temporal_continuity_index(replace(base, created_by_lane="PROJECTION", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}

    alt = dict(asdict(base))
    alt["index_hash"] = "x"
    assert temporal_continuity_index_hash(base) == temporal_continuity_index_hash(alt)
    assert canonical_temporal_continuity_index_json(base) == canonical_temporal_continuity_index_json(base)

    s = json.loads(open("contracts/temporal_continuity/temporal_continuity_index.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(base).keys()))
    s2 = dict(asdict(base))
    s2.pop("index_id")
    assert "index_id" in s["required"] and "index_id" not in s2

    h = write_temporal_continuity_index_contract_audit(tmp_path)
    t = open(tmp_path / "out/audit/temporal_continuity_index_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
