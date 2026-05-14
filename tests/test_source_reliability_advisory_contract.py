import json
import hashlib
from dataclasses import asdict, replace
from core.reliability import *


def _ledger(n=40,b=0.09,e=0.04):
    return {"calibration_ledger_id":"cal-1","calibration_hash":"hash-1","aggregate":{"entry_count":n,"mean_brier_score":b,"expected_calibration_error":e,"mean_probability":0.5,"mean_outcome":0.5,"sample_policy":"SAMPLE_MEAN_V1"}}


def test_deterministic_derivation_stable():
    a1=derive_reliability_advisory_from_calibration(_ledger()); a2=derive_reliability_advisory_from_calibration(_ledger())
    assert a1.advisory_hash==a2.advisory_hash

def test_threshold_postures():
    assert derive_reliability_advisory_from_calibration(_ledger(10,0.09,0.04)).advisory_status=="INSUFFICIENT_SAMPLE"
    assert derive_reliability_advisory_from_calibration(_ledger(40,0.10,0.05)).metric_snapshot.reliability_posture=="STRONG"
    assert derive_reliability_advisory_from_calibration(_ledger(40,0.25,0.15)).metric_snapshot.reliability_posture=="MIXED"
    assert derive_reliability_advisory_from_calibration(_ledger(40,0.4,0.2)).metric_snapshot.reliability_posture=="WEAK"

def test_validation_blocks_mutation_actionability_routing():
    a=derive_reliability_advisory_from_calibration(_ledger())
    assert validate_source_reliability_advisory(replace(a, mutation_allowed=True)).status in {"BLOCKED","NOT_COMPUTABLE"}
    rec=replace(a.recommendations[0], actionability="MUTATE")
    assert validate_source_reliability_advisory(replace(a, recommendations=(rec,))).status in {"BLOCKED","NOT_COMPUTABLE"}
    pol=replace(a.advisory_policy, routing_policy="ALLOW_ROUTING_CHANGE")
    assert validate_source_reliability_advisory(replace(a, advisory_policy=pol)).status in {"BLOCKED","NOT_COMPUTABLE"}

def test_lane_authority_constraints():
    a=derive_reliability_advisory_from_calibration(_ledger())
    assert validate_source_reliability_advisory(replace(a, created_by_lane="SHADOW")).status in {"BLOCKED","NOT_COMPUTABLE"}
    assert validate_source_reliability_advisory(replace(a, created_by_lane="PROJECTION")).status in {"BLOCKED","NOT_COMPUTABLE"}

def test_hash_excludes_advisory_hash_and_canonical_stable():
    a=derive_reliability_advisory_from_calibration(_ledger())
    b=dict(asdict(a)); b["advisory_hash"]="different"
    assert source_reliability_advisory_hash(a)==source_reliability_advisory_hash(b)
    assert canonical_source_reliability_advisory_json(a)==canonical_source_reliability_advisory_json(a)

def test_schema_accepts_and_rejects_required():
    schema=json.loads(open("contracts/reliability/source_reliability_advisory.v1.schema.json",encoding="utf-8").read())
    obj=asdict(derive_reliability_advisory_from_calibration(_ledger()))
    required=set(schema["required"])
    assert required.issubset(set(obj.keys()))
    bad=dict(obj); bad.pop("advisory_id")
    assert not required.issubset(set(bad.keys()))

def test_audit_hash_and_newline(tmp_path):
    h1=write_source_reliability_advisory_contract_audit(tmp_path)
    p=tmp_path/"out/audit/source_reliability_advisory_contract.latest.json"
    text=p.read_text(encoding="utf-8")
    assert text.endswith("\n")
    assert h1==hashlib.sha256(text.encode("utf-8")).hexdigest()
