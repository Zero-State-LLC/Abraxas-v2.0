import hashlib
import json
from dataclasses import asdict, replace

from core.replay_consensus.review import canonical_replay_consensus_review_json, derive_replay_consensus_review, replay_consensus_review_hash, write_replay_consensus_review_contract_audit
from core.replay_consensus.validator import validate_replay_consensus_review


def _arb(i, st="NO_CONFLICT", blocked=False):
    fs = ({"finding_type": "BLOCKED_HISTORY_PRESENT"},) if blocked else tuple()
    return {"arbitration_id": f"a{i}", "arbitration_status": st, "lineage_candidates": ({"candidate_id": f"c{i}", "lineage_id": f"l{i}"},), "arbitration_findings": fs}


def test_consensus_derivation_and_validation_rules():
    assert derive_replay_consensus_review([]).review_status == "NOT_COMPUTABLE"
    one = derive_replay_consensus_review([_arb(1)])
    assert one.review_status == "INSUFFICIENT_ARBITRATION_HISTORY"
    strong = derive_replay_consensus_review([_arb(1), _arb(2)])
    assert strong.review_status == "CONSENSUS_PRESENT" and strong.consensus_posture.consensus_state == "STRONG_CONSENSUS"
    mixed = derive_replay_consensus_review([_arb(1), _arb(2, "CONFLICT_DETECTED")])
    assert mixed.review_status in {"PARTIAL_CONSENSUS", "OPERATOR_REVIEW_REQUIRED", "CONSENSUS_CONFLICT"}
    conflict = derive_replay_consensus_review([_arb(1, "CONFLICT_DETECTED"), _arb(2, "CONFLICT_DETECTED")])
    assert conflict.review_status == "CONSENSUS_CONFLICT"
    assert any(f.finding_type == "BLOCKED_HISTORY_PRESENT" for f in derive_replay_consensus_review([_arb(1, blocked=True), _arb(2)]).consensus_findings)

    assert validate_replay_consensus_review(replace(one, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_consensus_review(replace(one, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_consensus_review(replace(one, timeline_collapse_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_consensus_review(replace(one, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_consensus_review(replace(one, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badc = replace(one, consensus_clusters=(replace(one.consensus_clusters[0], lineages_preserved=False),))
    assert validate_replay_consensus_review(badc).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badn = replace(one, consensus_clusters=(replace(one.consensus_clusters[0], normalization_allowed=True),))
    assert validate_replay_consensus_review(badn).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badp = replace(one, consensus_posture=replace(one.consensus_posture, canonical_selection_allowed=True))
    assert validate_replay_consensus_review(badp).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badp2 = replace(one, consensus_posture=replace(one.consensus_posture, auto_promotion_allowed=True))
    assert validate_replay_consensus_review(badp2).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badr = replace(one, recommendations=(replace(one.recommendations[0], timeline_collapse_allowed=True),))
    assert validate_replay_consensus_review(badr).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_consensus_review(replace(strong, created_by_lane="SHADOW")).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_consensus_review(replace(one, created_by_lane="PROJECTION", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_hash_schema_json_and_audit():
    r = derive_replay_consensus_review([_arb(1), _arb(2)], [{"source_type": "REPLAY_TEMPORAL_ARBITRATION", "source_id": "a1", "source_hash": "h1"}])
    alt = dict(asdict(r))
    alt["review_hash"] = "x"
    assert replay_consensus_review_hash(r) == replay_consensus_review_hash(alt)
    assert canonical_replay_consensus_review_json(r) == canonical_replay_consensus_review_json(r)
    s = json.loads(open("contracts/replay_consensus/replay_consensus_review.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(r).keys()))
    h = write_replay_consensus_review_contract_audit(".")
    t = open("out/audit/replay_consensus_review_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
