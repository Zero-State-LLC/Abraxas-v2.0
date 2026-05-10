import hashlib, json
from dataclasses import asdict, replace
from core.replay_ledger import *

def _entry(i,h="h1",s="REPLAY_READY",rb="rb1",a="a1",nd=False):
    return {"entry_id":f"e{i}","replay_id":f"r{i}","replay_hash":h,"replay_status":s,"authorization_id":"auth","authorization_hash":a,"determinism_report_hash":"d1","rollback_plan_hash":rb,"entry_index":i,"entry_policy":"P" ,"nondeterminism_detected":nd}

def test_diff_and_stability_rules():
    d=derive_replay_temporal_diff(_entry(1),_entry(2))
    assert d.diff_status=="NO_DIVERGENCE"
    assert derive_replay_temporal_diff(_entry(1,"h1"),_entry(2,"h2")).diff_status in {"DIVERGENCE_DETECTED","ROLLBACK_DIVERGENCE","AUTHORIZATION_DIVERGENCE","NONDETERMINISM_DETECTED"}
    assert any(f.divergence_type=="STATUS_CHANGE" for f in derive_replay_temporal_diff(_entry(1,s="A"),_entry(2,s="B")).divergence_findings)
    assert any(f.divergence_type=="ROLLBACK_CHANGE" for f in derive_replay_temporal_diff(_entry(1,rb="a"),_entry(2,rb="b")).divergence_findings)
    assert any(f.divergence_type=="AUTHORIZATION_CHANGE" for f in derive_replay_temporal_diff(_entry(1,a="a"),_entry(2,a="b")).divergence_findings)
    assert derive_replay_temporal_diff({},_entry(2)).diff_status in {"NOT_COMPUTABLE","BLOCKED_BY_INPUTS"}
    assert compute_temporal_stability_score((_entry(1),)).stability_posture=="INSUFFICIENT_HISTORY"
    assert compute_temporal_stability_score((_entry(1),_entry(2),_entry(3))).stability_posture=="STABLE"
    assert compute_temporal_stability_score((_entry(1),_entry(2),_entry(3,"h2"),_entry(4,"h2"))).stability_posture=="MIXED"
    assert compute_temporal_stability_score((_entry(1),_entry(2,"h2"),_entry(3,"h3"))).stability_posture=="UNSTABLE"

def test_validation_hash_schema_and_audit():
    e1=ReplayLedgerEntry("e1","r1","h1","REPLAY_READY","auth","a1","d1","rb1",1,"P")
    l=build_replay_ledger("l1",(e1,),tuple(),"LEDGER_READY","P","FORECAST",None)
    assert validate_replay_ledger(replace(l,live_execution_allowed=True)).status in {"BLOCKED","NOT_COMPUTABLE"}
    assert validate_replay_ledger(replace(l,mutation_allowed=True)).status in {"BLOCKED","NOT_COMPUTABLE"}
    assert validate_replay_ledger(replace(l,routing_change_allowed=True)).status in {"BLOCKED","NOT_COMPUTABLE"}
    d=derive_replay_temporal_diff(_entry(1),_entry(2))
    assert validate_replay_temporal_diff(replace(d,stability_score=replace(d.stability_score, mutation_allowed=True))).status in {"BLOCKED","NOT_COMPUTABLE"}
    assert validate_replay_temporal_diff(replace(d,created_by_lane="SHADOW")).status in {"BLOCKED","NOT_COMPUTABLE"}
    assert validate_replay_temporal_diff(replace(d,created_by_lane="PROJECTION",authority_ref={"a":1})).status in {"BLOCKED","NOT_COMPUTABLE"}
    alt=dict(asdict(l)); alt["ledger_hash"]="x"; assert replay_ledger_hash(l)==replay_ledger_hash(alt)
    ad=dict(asdict(d)); ad["diff_hash"]="x"; assert replay_temporal_diff_hash(d)==replay_temporal_diff_hash(ad)
    assert canonical_replay_ledger_json(l)==canonical_replay_ledger_json(l)
    assert canonical_replay_temporal_diff_json(d)==canonical_replay_temporal_diff_json(d)
    ls=json.loads(open('contracts/replay_ledger/replay_ledger.v1.schema.json').read()); assert set(ls['required']).issubset(set(asdict(l).keys()))
    ds=json.loads(open('contracts/replay_ledger/replay_temporal_diff.v1.schema.json').read()); assert set(ds['required']).issubset(set(asdict(d).keys()))
    h=write_replay_ledger_temporal_diff_contract_audit('.')
    t=open('out/audit/replay_ledger_temporal_diff_contract.latest.json').read()
    assert t.endswith('\n') and h==hashlib.sha256(t.encode()).hexdigest()
