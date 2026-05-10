from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from .models import AuthorityRef, CalibrationAggregate, CalibrationBucket, CalibrationInputRef, CalibrationLedger, CalibrationReliabilityObservation, CalibrationValidationReport

SCHEMA_VERSION = "CalibrationLedger.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_calibration_ledger_json(ledger: CalibrationLedger | Mapping[str, Any]) -> str:
    payload = asdict(ledger) if isinstance(ledger, CalibrationLedger) else dict(ledger)
    payload.pop("calibration_hash", None)
    return _canonical_json(payload)


def calibration_ledger_hash(ledger: CalibrationLedger | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_calibration_ledger_json(ledger))


def _bucket_index(p: float) -> int:
    if p >= 1.0:
        return 9
    return min(9, max(0, int(p * 10)))


def aggregate_brier_entries(entries: Sequence[Mapping[str, Any]], bucket_policy: str = "DECILE_V1") -> CalibrationLedger:
    buckets_data = [[] for _ in range(10)]
    for e in entries:
        buckets_data[_bucket_index(float(e["probability"]))].append(e)

    buckets = []
    total_gap = 0.0
    for i, group in enumerate(buckets_data):
        lo, hi = i / 10.0, (i + 1) / 10.0 if i < 9 else 1.0
        if group:
            mp = sum(float(x["probability"]) for x in group) / len(group)
            mo = sum(float(x["outcome_value"]) for x in group) / len(group)
            mb = sum(float(x["score_result"]["score"]) for x in group) / len(group)
        else:
            mp = mo = mb = 0.0
        gap = abs(mp - mo) if group else 0.0
        total_gap += gap * len(group)
        buckets.append(CalibrationBucket(f"decile_{i}", lo, hi, len(group), round(mp, 10), round(mo, 10), round(mb, 10), round(gap, 10)))

    n = len(entries)
    mean_brier = round(sum(float(x["score_result"]["score"]) for x in entries) / n, 10) if n else 0.0
    mean_prob = round(sum(float(x["probability"]) for x in entries) / n, 10) if n else 0.0
    mean_out = round(sum(float(x["outcome_value"]) for x in entries) / n, 10) if n else 0.0
    ece = round(total_gap / n, 10) if n else 0.0

    status = "OBSERVED" if n else "INSUFFICIENT_SAMPLE"
    agg = CalibrationAggregate(n, mean_brier, mean_prob, mean_out, ece, "SAMPLE_MEAN_V1")
    rel = CalibrationReliabilityObservation("rel-global", "GLOBAL", "global", n, mean_brier, "INSUFFICIENT_SAMPLE" if n < 3 else "MIXED", False)
    return build_calibration_ledger(
        calibration_ledger_id="calibration-ledger-v1",
        input_entries=tuple(CalibrationInputRef(str(e["ledger_entry_id"]), str(e["ledger_hash"])) for e in entries),
        buckets=tuple(buckets),
        aggregate=agg,
        reliability_observations=(rel,),
        calibration_status=status,
        calibration_policy=bucket_policy,
        created_by_lane="OPERATOR",
        authority_ref=AuthorityRef("MANUAL_RECEIPT", "receipt://calibration/observation", "Operator calibration receipt"),
    )


def build_calibration_ledger(calibration_ledger_id: str, input_entries: tuple[CalibrationInputRef, ...], buckets: tuple[CalibrationBucket, ...], aggregate: CalibrationAggregate, reliability_observations: tuple[CalibrationReliabilityObservation, ...], calibration_status: str, calibration_policy: str, created_by_lane: str, authority_ref: AuthorityRef | None) -> CalibrationLedger:
    draft = CalibrationLedger(SCHEMA_VERSION, calibration_ledger_id, input_entries, buckets, aggregate, reliability_observations, calibration_status, calibration_policy, created_by_lane, authority_ref, "PENDING")
    return replace(draft, calibration_hash=calibration_ledger_hash(draft))


def validate_calibration_ledger(ledger: CalibrationLedger | Mapping[str, Any]) -> CalibrationValidationReport:
    from .validator import validate_calibration_ledger
    return validate_calibration_ledger(ledger)


def write_calibration_ledger_contract_audit(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    entries = [
        {"ledger_entry_id": "b1", "ledger_hash": "h1", "probability": 0.8, "outcome_value": 1.0, "score_result": {"score": 0.04}},
        {"ledger_entry_id": "b2", "ledger_hash": "h2", "probability": 0.2, "outcome_value": 0.0, "score_result": {"score": 0.04}},
    ]
    ledger = aggregate_brier_entries(entries)
    report = validate_calibration_ledger(ledger)
    payload = {"status": report.status, "calibration_hash": ledger.calibration_hash, "receipt_hash": report.receipt_hash, "findings": [asdict(f) for f in report.findings], "schema_version": ledger.schema_version}
    text = _canonical_json(payload) + "\n"
    out = base / "out/audit/calibration_ledger_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
