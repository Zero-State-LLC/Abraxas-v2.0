from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import AuthorityRef, BrierLedgerEntry, BrierScorePolicy, BrierScoreResult, BrierValidationReport

SCHEMA_VERSION = "BrierLedgerEntry.v1"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
DECOMPOSITION_MODE = "MURPHY_AND_YATES"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _round_value(value: float, rounding_policy: str = "ROUND_10_DP") -> float:
    if rounding_policy == "ROUND_10_DP":
        return round(value, 10)
    if rounding_policy == "ROUND_6_DP":
        return round(value, 6)
    return value


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _variance(values: list[float], mean_val: float | None = None) -> float:
    if not values:
        return 0.0
    mean_value = mean_val if mean_val is not None else _mean(values)
    return sum((value - mean_value) ** 2 for value in values) / len(values)


def _covariance(
    x_values: list[float],
    y_values: list[float],
    mean_x: float | None = None,
    mean_y: float | None = None,
) -> float:
    if not x_values or len(x_values) != len(y_values):
        return 0.0
    mean_x_value = mean_x if mean_x is not None else _mean(x_values)
    mean_y_value = mean_y if mean_y is not None else _mean(y_values)
    return sum(
        (x_value - mean_x_value) * (y_value - mean_y_value)
        for x_value, y_value in zip(x_values, y_values)
    ) / len(x_values)


def _not_computable_murphy() -> dict[str, float | str]:
    return {
        "reliability": NOT_COMPUTABLE,
        "resolution": NOT_COMPUTABLE,
        "uncertainty": NOT_COMPUTABLE,
        "brier_score": NOT_COMPUTABLE,
    }


def _not_computable_yates() -> dict[str, float | str]:
    return {
        "bias_squared": NOT_COMPUTABLE,
        "excess_variance": NOT_COMPUTABLE,
        "covariance_deficit": NOT_COMPUTABLE,
        "brier_score": NOT_COMPUTABLE,
    }


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


def compute_murphy_decomposition(
    predictions: list[float],
    targets: list[float],
    *,
    rounding_policy: str = "ROUND_10_DP",
    n_bins: int = 10,
) -> dict[str, float | str]:
    if not predictions or len(predictions) != len(targets):
        return _not_computable_murphy()
    n = len(predictions)
    mean_target = _mean(targets)
    reliability = 0.0
    resolution = 0.0
    for bin_index in range(n_bins):
        lower = bin_index / n_bins
        upper = (bin_index + 1) / n_bins
        bin_preds = [pred for pred, target in zip(predictions, targets) if lower <= pred < upper]
        bin_targets = [target for pred, target in zip(predictions, targets) if lower <= pred < upper]
        if bin_preds:
            bin_mean_pred = _mean(bin_preds)
            bin_mean_target = _mean(bin_targets)
            reliability += (len(bin_preds) / n) * (bin_mean_pred - bin_mean_target) ** 2
            resolution += (len(bin_preds) / n) * (bin_mean_target - mean_target) ** 2
    uncertainty = mean_target * (1 - mean_target)
    brier_score = reliability - resolution + uncertainty
    return {
        "reliability": _round_value(reliability, rounding_policy),
        "resolution": _round_value(resolution, rounding_policy),
        "uncertainty": _round_value(uncertainty, rounding_policy),
        "brier_score": _round_value(brier_score, rounding_policy),
    }


def compute_yates_decomposition(
    predictions: list[float],
    targets: list[float],
    *,
    rounding_policy: str = "ROUND_10_DP",
) -> dict[str, float | str]:
    if not predictions or len(predictions) != len(targets):
        return _not_computable_yates()
    mean_pred = _mean(predictions)
    mean_target = _mean(targets)
    bias_squared = (mean_pred - mean_target) ** 2
    excess_variance = _variance(predictions, mean_pred)
    outcome_variance = _variance(targets, mean_target)
    covariance_deficit = outcome_variance - 2 * _covariance(
        predictions, targets, mean_pred, mean_target
    )
    brier_score = bias_squared + excess_variance + covariance_deficit
    return {
        "bias_squared": _round_value(bias_squared, rounding_policy),
        "excess_variance": _round_value(excess_variance, rounding_policy),
        "covariance_deficit": _round_value(covariance_deficit, rounding_policy),
        "brier_score": _round_value(brier_score, rounding_policy),
    }


def compute_full_decomposition(
    predictions: list[float],
    targets: list[float],
    *,
    rounding_policy: str = "ROUND_10_DP",
) -> dict[str, Any]:
    return {
        "decomposition_mode": DECOMPOSITION_MODE,
        "murphy": compute_murphy_decomposition(predictions, targets, rounding_policy=rounding_policy),
        "yates": compute_yates_decomposition(predictions, targets, rounding_policy=rounding_policy),
    }


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
