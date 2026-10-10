import hashlib
import json
from dataclasses import asdict, replace

from core.replay_arbitration.arbitration import canonical_replay_temporal_arbitration_json, derive_replay_temporal_arbitration, replay_temporal_arbitration_hash, write_replay_temporal_arbitration_contract_audit
from core.replay_arbitration.validator import validate_replay_temporal_arbitration


def _cand(i, sp="STABLE", d=0, b=0, n=0, lr="ledger"):
    return {"candidate_id": f"c{i}", "lineage_id": f"l{i}", "ledger_ref_id": f"{lr}-{i}" if lr else "", "diff_ref_ids": (f"d{i}",), "replay_ref_ids": (f"r{i}",), "stability_posture": sp, "divergence_count": d, "blocked_count": b, "nondeterminism_count": n, "lineage_preserved": True}


def test_arbitration_core_rules_and_validation():
    assert derive_replay_temporal_arbitration([]).arbitration_status == "NOT_COMPUTABLE"
    one = derive_replay_temporal_arbitration([_cand(1)])
    assert one.arbitration_status == "NO_CONFLICT"
    same = derive_replay_temporal_arbitration([_cand(1), _cand(2)])
    assert same.arbitration_status == "NO_CONFLICT" and all(c.lineage_preserved for c in same.lineage_candidates)
    assert derive_replay_temporal_arbitration([_cand(1, "STABLE"), _cand(2, "UNSTABLE")]).arbitration_status == "CONFLICT_DETECTED"
    assert any(f.finding_type == "ROLLBACK_CONFLICT" for f in derive_replay_temporal_arbitration([_cand(1, d=1), _cand(2)]).arbitration_findings)
    assert all(s.authority_posture != "PRIMARY" for s in derive_replay_temporal_arbitration([_cand(1, n=1)]).authority_scores)
    assert all(s.authority_posture != "PRIMARY" for s in derive_replay_temporal_arbitration([_cand(1, b=1)]).authority_scores)

    assert validate_replay_temporal_arbitration(replace(one, history_rewrite_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_temporal_arbitration(replace(one, ledger_mutation_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_temporal_arbitration(replace(one, live_execution_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_temporal_arbitration(replace(one, routing_change_allowed=True)).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badc = replace(one, lineage_candidates=(replace(one.lineage_candidates[0], lineage_preserved=False),))
    assert validate_replay_temporal_arbitration(badc).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badf = replace(one, arbitration_findings=(replace(one.arbitration_findings[0], normalization_allowed=True),))
    assert validate_replay_temporal_arbitration(badf).status in {"BLOCKED", "NOT_COMPUTABLE"}
    bads = replace(one, authority_scores=(replace(one.authority_scores[0], auto_select_allowed=True),))
    assert validate_replay_temporal_arbitration(bads).status in {"BLOCKED", "NOT_COMPUTABLE"}
    badr = replace(one, recommendations=(replace(one.recommendations[0], history_rewrite_allowed=True),))
    assert validate_replay_temporal_arbitration(badr).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_temporal_arbitration(replace(one, created_by_lane="SHADOW")).status in {"BLOCKED", "NOT_COMPUTABLE"}
    assert validate_replay_temporal_arbitration(replace(one, created_by_lane="PROJECTION", authority_ref={"a": 1})).status in {"BLOCKED", "NOT_COMPUTABLE"}


def test_hash_schema_json_and_audit(tmp_path):
    a = derive_replay_temporal_arbitration([_cand(1)], [{"source_type": "REPLAY_LEDGER", "source_id": "l", "source_hash": "h"}])
    alt = dict(asdict(a))
    alt["arbitration_hash"] = "x"
    assert replay_temporal_arbitration_hash(a) == replay_temporal_arbitration_hash(alt)
    assert canonical_replay_temporal_arbitration_json(a) == canonical_replay_temporal_arbitration_json(a)

    s = json.loads(open("contracts/replay_arbitration/replay_temporal_arbitration.v1.schema.json").read())
    assert set(s["required"]).issubset(set(asdict(a).keys()))

    h = write_replay_temporal_arbitration_contract_audit(tmp_path)
    t = open(tmp_path / "out/audit/replay_temporal_arbitration_contract.latest.json").read()
    assert t.endswith("\n") and h == hashlib.sha256(t.encode()).hexdigest()
