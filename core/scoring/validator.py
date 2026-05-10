from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .brier import compute_brier_score
from .models import AuthorityRef, BrierLedgerEntry, BrierScorePolicy, BrierScoreResult, BrierValidationFinding, BrierValidationReport

NON_SCORABLE = {"VOID", "CONFLICTING", "NOT_COMPUTABLE"}


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_entry(entry: BrierLedgerEntry | Mapping[str, Any]) -> BrierLedgerEntry:
    if isinstance(entry, BrierLedgerEntry):
        return entry
    data = dict(entry)
    return BrierLedgerEntry(
        schema_version=data["schema_version"],
        ledger_entry_id=data["ledger_entry_id"],
        forecast_id=data["forecast_id"],
        forecast_hash=data["forecast_hash"],
        settlement_id=data["settlement_id"],
        settlement_hash=data["settlement_hash"],
        probability=data["probability"],
        settlement_decision=data["settlement_decision"],
        outcome_value=data["outcome_value"],
        score_result=BrierScoreResult(**data["score_result"]),
        score_policy=BrierScorePolicy(**data["score_policy"]),
        created_by_lane=data["created_by_lane"],
        authority_ref=AuthorityRef(**data["authority_ref"]) if data.get("authority_ref") else None,
        ledger_hash=data["ledger_hash"],
    )


def validate_brier_ledger_entry(entry: BrierLedgerEntry | Mapping[str, Any]) -> BrierValidationReport:
    obj = _to_entry(entry)
    findings: list[BrierValidationFinding] = []
    status = "PASS"

    if obj.schema_version != "BrierLedgerEntry.v1":
        findings.append(BrierValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be BrierLedgerEntry.v1."))
        status = "NOT_COMPUTABLE"

    if not all([obj.forecast_id, obj.forecast_hash, obj.settlement_id, obj.settlement_hash]):
        findings.append(BrierValidationFinding("REQUIRED_HASH_REF_MISSING", "not_computable", "forecast and settlement ids/hashes are required."))
        status = "NOT_COMPUTABLE"

    if not (0.0 <= obj.probability <= 1.0):
        findings.append(BrierValidationFinding("PROBABILITY_RANGE_INVALID", "error", "Probability must be in [0,1]."))
        status = "BLOCKED"
    if not (0.0 <= obj.outcome_value <= 1.0):
        findings.append(BrierValidationFinding("OUTCOME_RANGE_INVALID", "error", "Outcome value must be in [0,1]."))
        status = "BLOCKED"

    if obj.settlement_decision == "TRUE" and obj.outcome_value != 1.0:
        findings.append(BrierValidationFinding("TRUE_OUTCOME_MISMATCH", "error", "TRUE requires outcome_value 1.0."))
        status = "BLOCKED"
    if obj.settlement_decision == "FALSE" and obj.outcome_value != 0.0:
        findings.append(BrierValidationFinding("FALSE_OUTCOME_MISMATCH", "error", "FALSE requires outcome_value 0.0."))
        status = "BLOCKED"
    if obj.settlement_decision == "PARTIAL" and not obj.score_policy.partial_policy:
        findings.append(BrierValidationFinding("PARTIAL_POLICY_REQUIRED", "not_computable", "PARTIAL requires explicit partial policy."))
        if status != "BLOCKED":
            status = "NOT_COMPUTABLE"

    if obj.settlement_decision in NON_SCORABLE:
        findings.append(BrierValidationFinding("DECISION_NOT_SCORE_READY", "not_computable", "VOID/CONFLICTING/NOT_COMPUTABLE are not score-ready."))
        if status != "BLOCKED":
            status = "NOT_COMPUTABLE"

    if obj.created_by_lane == "SHADOW" and obj.authority_ref is not None:
        findings.append(BrierValidationFinding("SHADOW_FINALIZE_BLOCKED", "error", "SHADOW may not finalize ledger entries."))
        status = "BLOCKED"
    if obj.created_by_lane == "PROJECTION":
        findings.append(BrierValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION cannot create scoring authority."))
        status = "BLOCKED"
    if obj.created_by_lane == "CANON" and obj.authority_ref is not None:
        findings.append(BrierValidationFinding("CANON_FINALIZE_BLOCKED", "error", "CANON may define contracts only."))
        status = "BLOCKED"

    finalized = obj.settlement_decision not in NON_SCORABLE
    if finalized:
        if obj.authority_ref is None:
            findings.append(BrierValidationFinding("FINALIZED_AUTHORITY_REQUIRED", "not_computable", "Finalized ledger entry requires authority_ref."))
            if status != "BLOCKED":
                status = "NOT_COMPUTABLE"
        if obj.created_by_lane not in {"FORECAST", "OPERATOR"}:
            findings.append(BrierValidationFinding("FINALIZED_LANE_INVALID", "error", "Finalized entry must be FORECAST or OPERATOR lane."))
            status = "BLOCKED"

    expected = compute_brier_score(obj.probability, obj.outcome_value, obj.score_policy.rounding_policy)
    if abs(obj.score_result.score - expected) > 1e-12:
        findings.append(BrierValidationFinding("SCORE_MISMATCH", "error", "Score result does not match deterministic Brier computation."))
        status = "BLOCKED"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "ledger_entry_id": obj.ledger_entry_id}))
    return BrierValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)
