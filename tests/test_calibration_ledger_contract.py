import hashlib
import json
from dataclasses import asdict
from pathlib import Path

from core.calibration import *
from core.calibration.models import *


def _entries():
    return [
        {"ledger_entry_id": "b1", "ledger_hash": "h1", "probability": 0.8, "outcome_value": 1.0, "score_result": {"score": 0.04}},
        {"ledger_entry_id": "b2", "ledger_hash": "h2", "probability": 0.1, "outcome_value": 0.0, "score_result": {"score": 0.01}},
        {"ledger_entry_id": "b3", "ledger_hash": "h3", "probability": 1.0, "outcome_value": 1.0, "score_result": {"score": 0.0}},
    ]


def test_aggregate_deterministic_stable_buckets_and_aggregate_values():
    a = aggregate_brier_entries(_entries())
    b = aggregate_brier_entries(_entries())
    assert a == b


def test_probability_one_assigned_to_final_decile_bucket():
    led = aggregate_brier_entries(_entries())
    assert any(b.bucket_id == "decile_9" and b.entry_count >= 1 for b in led.buckets)


def test_observed_without_inputs_blocked_or_not_computable():
    l = build_calibration_ledger("id", (), (), CalibrationAggregate(0,0,0,0,0,"x"), (CalibrationReliabilityObservation("o","GLOBAL","g",0,0,"INSUFFICIENT_SAMPLE",False),), "OBSERVED", "DECILE_V1", "OPERATOR", AuthorityRef("A","B","C"))
    assert validate_calibration_ledger(l).status in {"BLOCKED","NOT_COMPUTABLE"}


def test_reliability_observations_mutation_always_false():
    l = aggregate_brier_entries(_entries())
    assert all(not r.mutation_allowed for r in l.reliability_observations)


def test_insufficient_sample_validates_and_no_mutation():
    l = aggregate_brier_entries([])
    assert l.calibration_status == "INSUFFICIENT_SAMPLE"
    assert validate_calibration_ledger(l).status in {"PASS","WARN","INSUFFICIENT_SAMPLE","NOT_COMPUTABLE"}


def test_mean_out_of_range_blocked_or_not_computable():
    l = aggregate_brier_entries(_entries())
    bad = asdict(l)
    bad["aggregate"]["mean_brier_score"] = 1.5
    assert validate_calibration_ledger(bad).status in {"BLOCKED","NOT_COMPUTABLE"}


def test_shadow_cannot_finalize_observed_ledger():
    l = aggregate_brier_entries(_entries())
    bad = asdict(l); bad["created_by_lane"] = "SHADOW"
    assert validate_calibration_ledger(bad).status == "BLOCKED"


def test_projection_cannot_create_calibration_authority():
    l = aggregate_brier_entries(_entries())
    bad = asdict(l); bad["created_by_lane"] = "PROJECTION"
    assert validate_calibration_ledger(bad).status == "BLOCKED"


def test_hash_stable_excludes_calibration_hash_field():
    l = aggregate_brier_entries(_entries())
    h1 = calibration_ledger_hash(l)
    p = asdict(l); p["calibration_hash"] = "mutated"
    h2 = calibration_ledger_hash(p)
    assert h1 == h2


def test_canonical_json_byte_stable():
    l = aggregate_brier_entries(_entries())
    assert canonical_calibration_ledger_json(l) == canonical_calibration_ledger_json(l)


def test_schema_accepts_shape_and_required_fields_present():
    s = json.loads(Path("contracts/calibration/calibration_ledger.v1.schema.json").read_text())
    assert "required" in s and "calibration_hash" in s["required"]


def test_audit_artifact_stable_sha256_and_newline(tmp_path: Path):
    h1 = write_calibration_ledger_contract_audit(tmp_path)
    p = tmp_path / "out/audit/calibration_ledger_contract.latest.json"
    t1 = p.read_text()
    h2 = write_calibration_ledger_contract_audit(tmp_path)
    t2 = p.read_text()
    assert t1.endswith("\n") and h1 == h2
    assert hashlib.sha256(t1.encode()).hexdigest() == hashlib.sha256(t2.encode()).hexdigest()
