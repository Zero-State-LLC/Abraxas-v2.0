from __future__ import annotations

import hashlib, json
from dataclasses import asdict
from typing import Any, Mapping
from .models import *

def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _to_ledger(ledger: CalibrationLedger | Mapping[str, Any]) -> CalibrationLedger:
    if isinstance(ledger, CalibrationLedger): return ledger
    d=dict(ledger)
    return CalibrationLedger(d["schema_version"], d["calibration_ledger_id"], tuple(CalibrationInputRef(**x) for x in d["input_entries"]), tuple(CalibrationBucket(**x) for x in d["buckets"]), CalibrationAggregate(**d["aggregate"]), tuple(CalibrationReliabilityObservation(**x) for x in d["reliability_observations"]), d["calibration_status"], d["calibration_policy"], d["created_by_lane"], AuthorityRef(**d["authority_ref"]) if d.get("authority_ref") else None, d["calibration_hash"])

def validate_calibration_ledger(ledger: CalibrationLedger | Mapping[str, Any]) -> CalibrationValidationReport:
    o=_to_ledger(ledger); findings=[]; status="PASS"
    if o.schema_version!="CalibrationLedger.v1": findings.append(CalibrationValidationFinding("SCHEMA_VERSION_INVALID","not_computable","schema_version must be CalibrationLedger.v1.")); status="NOT_COMPUTABLE"
    if o.calibration_status=="OBSERVED" and not o.input_entries: findings.append(CalibrationValidationFinding("OBSERVED_INPUT_REQUIRED","error","OBSERVED requires input entries.")); status="BLOCKED"
    if o.calibration_status=="CONFLICTING" and not findings: findings.append(CalibrationValidationFinding("CONFLICTING_REASON_REQUIRED","not_computable","CONFLICTING requires findings/reason context.")); status="NOT_COMPUTABLE"
    if o.calibration_status=="VOID" and not findings: findings.append(CalibrationValidationFinding("VOID_REASON_REQUIRED","not_computable","VOID requires reason/finding.")); status="NOT_COMPUTABLE"
    for r in o.reliability_observations:
        if r.mutation_allowed: findings.append(CalibrationValidationFinding("MUTATION_FORBIDDEN","error","mutation_allowed must be false.")); status="BLOCKED"
    vals=[o.aggregate.mean_brier_score,o.aggregate.mean_probability,o.aggregate.mean_outcome,o.aggregate.expected_calibration_error]
    if any(v<0 or v>1 for v in vals): findings.append(CalibrationValidationFinding("AGGREGATE_RANGE_INVALID","error","Aggregate means must be in [0,1].")); status="BLOCKED"
    for b in o.buckets:
        if b.lower_bound<0 or b.upper_bound>1 or b.lower_bound>b.upper_bound: findings.append(CalibrationValidationFinding("BUCKET_RANGE_INVALID","error","Bucket ranges malformed.")); status="BLOCKED"
    if any(not e.ledger_entry_id or not e.ledger_hash for e in o.input_entries): findings.append(CalibrationValidationFinding("INPUT_REF_MISSING","not_computable","Input refs require id and hash.")); status="NOT_COMPUTABLE" if status!="BLOCKED" else status
    if o.calibration_status=="OBSERVED" and o.created_by_lane not in {"FORECAST","OPERATOR"}: findings.append(CalibrationValidationFinding("OBSERVED_LANE_INVALID","error","OBSERVED must be FORECAST or OPERATOR lane.")); status="BLOCKED"
    if o.created_by_lane=="SHADOW" and o.calibration_status=="OBSERVED": findings.append(CalibrationValidationFinding("SHADOW_OBSERVED_BLOCKED","error","SHADOW may not finalize OBSERVED ledger.")); status="BLOCKED"
    if o.created_by_lane=="PROJECTION" and o.calibration_status!="DRAFT": findings.append(CalibrationValidationFinding("PROJECTION_AUTHORITY_BLOCKED","error","PROJECTION cannot create calibration authority.")); status="BLOCKED"
    if o.created_by_lane=="CANON" and o.calibration_status!="DRAFT": findings.append(CalibrationValidationFinding("CANON_CALIBRATION_BLOCKED","error","CANON may define contracts only.")); status="BLOCKED"
    receipt=_sha256_text(_canonical_json({"status":status,"findings":[asdict(f) for f in findings],"calibration_ledger_id":o.calibration_ledger_id}))
    return CalibrationValidationReport(status, tuple(findings), receipt)
