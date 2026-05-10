from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import AuthorityRef, BrierLedgerEntry, BrierScorePolicy, BrierScoreResult, BrierValidationReport

SCHEMA_VERSION = "BrierLedgerEntry.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload(entry: BrierLedgerEntry | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(entry, BrierLedgerEntry):
        return asdict(entry)
    return dict(entry)


def canonical_brier_ledger_json(entry: BrierLedgerEntry | Mapping[str, Any]) -> str:
    payload = _payload(entry)
    payload.pop("ledger_hash", None)
    return _canonical_json(payload)


def brier_ledger_hash(entry: BrierLedgerEntry | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_brier_ledger_json(entry))


def compute_brier_score(probability: float, outcome_value: float, rounding_policy: str = "ROUND_10_DP") -> float:
    score = (probability - outcome_value) ** 2
    if rounding_policy == "ROUND_10_DP":
        return round(score, 10)
    if rounding_policy == "ROUND_6_DP":
        return round(score, 6)
    return score


def build_brier_ledger_entry(
    ledger_entry_id: str,
    forecast_id: str,
    forecast_hash: str,
    settlement_id: str,
    settlement_hash: str,
    probability: float,
    settlement_decision: str,
    outcome_value: float,
    score_policy: BrierScorePolicy,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> BrierLedgerEntry:
    score = compute_brier_score(probability, outcome_value, score_policy.rounding_policy)
    draft = BrierLedgerEntry(
        schema_version=SCHEMA_VERSION,
        ledger_entry_id=ledger_entry_id,
        forecast_id=forecast_id,
        forecast_hash=forecast_hash,
        settlement_id=settlement_id,
        settlement_hash=settlement_hash,
        probability=probability,
        settlement_decision=settlement_decision,
        outcome_value=outcome_value,
        score_result=BrierScoreResult(score=score, rounding_policy=score_policy.rounding_policy),
        score_policy=score_policy,
        created_by_lane=created_by_lane,
        authority_ref=authority_ref,
        ledger_hash="PENDING",
    )
    return replace(draft, ledger_hash=brier_ledger_hash(draft))


def validate_brier_ledger_entry(entry: BrierLedgerEntry | Mapping[str, Any]) -> BrierValidationReport:
    from .validator import validate_brier_ledger_entry

    return validate_brier_ledger_entry(entry)


def write_brier_ledger_contract_audit(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    policy = BrierScorePolicy("BRIER_BINARY_V1", "ROUND_10_DP", "PARTIAL_LINEAR", "VOID_NOT_SCORABLE", "CONFLICT_NOT_SCORABLE")
    sample = build_brier_ledger_entry(
        ledger_entry_id="brier-ledger-v1",
        forecast_id="forecast-object-contract-v1",
        forecast_hash="fixture-forecast-hash",
        settlement_id="settlement-verdict-v1",
        settlement_hash="fixture-settlement-hash",
        probability=0.8,
        settlement_decision="TRUE",
        outcome_value=1.0,
        score_policy=policy,
        created_by_lane="OPERATOR",
        authority_ref=AuthorityRef("MANUAL_RECEIPT", "receipt://brier/approval", "Operator brier receipt"),
    )
    report = validate_brier_ledger_entry(sample)
    payload = {
        "status": report.status,
        "ledger_hash": sample.ledger_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": sample.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = base / "out/audit/brier_ledger_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
