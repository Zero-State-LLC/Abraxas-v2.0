from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import (
    AuthorityRef,
    BindingStatus,
    OutcomeBinding,
    OutcomeCriterion,
    OutcomeBindingValidationReport,
    ResolutionSourceRef,
    ResolutionWindow,
    VerdictRule,
)

SCHEMA_VERSION = "OutcomeBinding.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload(binding: OutcomeBinding | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(binding, OutcomeBinding):
        return asdict(binding)
    return dict(binding)


def canonical_outcome_binding_json(binding: OutcomeBinding | Mapping[str, Any]) -> str:
    payload = _payload(binding)
    payload.pop("binding_hash", None)
    return _canonical_json(payload)


def outcome_binding_hash(binding: OutcomeBinding | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_outcome_binding_json(binding))


def build_outcome_binding(
    binding_id: str,
    forecast_id: str,
    forecast_hash: str,
    criteria: tuple[OutcomeCriterion, ...],
    resolution_sources: tuple[ResolutionSourceRef, ...],
    resolution_window: ResolutionWindow,
    verdict_rule: VerdictRule,
    binding_status: BindingStatus,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
    void_reason: str | None = None,
) -> OutcomeBinding:
    draft = OutcomeBinding(
        schema_version=SCHEMA_VERSION,
        binding_id=binding_id,
        forecast_id=forecast_id,
        forecast_hash=forecast_hash,
        criteria=tuple(criteria),
        resolution_sources=tuple(resolution_sources),
        resolution_window=resolution_window,
        verdict_rule=verdict_rule,
        binding_status=binding_status,
        created_by_lane=created_by_lane,
        authority_ref=authority_ref,
        void_reason=void_reason,
        binding_hash="PENDING",
    )
    return replace(draft, binding_hash=outcome_binding_hash(draft))


def validate_outcome_binding(binding: OutcomeBinding | Mapping[str, Any]) -> OutcomeBindingValidationReport:
    from .validator import validate_outcome_binding

    return validate_outcome_binding(binding)


def write_outcome_binding_contract_audit(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    sample = build_outcome_binding(
        binding_id="outcome-binding-v1",
        forecast_id="forecast-object-contract-v1",
        forecast_hash="fixture-forecast-hash",
        criteria=(OutcomeCriterion("c1", "Event resolves true in window"),),
        resolution_sources=(ResolutionSourceRef("REPO_FIXTURE", "fixtures/outcomes/local.json", "Local fixture"),),
        resolution_window=ResolutionWindow("POLICY_OPEN_ON_FORECAST_HORIZON", "POLICY_CLOSE_PLUS_7D", "UTC_STATIC"),
        verdict_rule=VerdictRule("BOOLEAN_EVENT", "true_if_event_occurs"),
        binding_status=BindingStatus.BOUND,
        created_by_lane="FORECAST",
        authority_ref=AuthorityRef("OPERATOR_RECEIPT", "receipt://outcomes/approval", "Operator approval"),
    )
    report = validate_outcome_binding(sample)
    payload = {
        "status": report.status,
        "binding_hash": sample.binding_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": sample.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = base / "out/audit/outcome_binding_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
