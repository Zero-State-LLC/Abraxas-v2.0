from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import (
    AuthorityRef,
    SettlementConflictSummary,
    SettlementDecision,
    SettlementReason,
    SettlementStatus,
    SettlementValidationReport,
    SettlementVerdict,
)

SCHEMA_VERSION = "SettlementVerdict.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload(verdict: SettlementVerdict | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(verdict, SettlementVerdict):
        return asdict(verdict)
    return dict(verdict)


def canonical_settlement_verdict_json(verdict: SettlementVerdict | Mapping[str, Any]) -> str:
    payload = _payload(verdict)
    payload.pop("settlement_hash", None)
    return _canonical_json(payload)


def settlement_verdict_hash(verdict: SettlementVerdict | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_settlement_verdict_json(verdict))


def build_settlement_verdict(
    settlement_id: str,
    forecast_id: str,
    forecast_hash: str,
    binding_id: str,
    binding_hash: str,
    evidence_packet_id: str,
    evidence_hash: str,
    decision: SettlementDecision,
    reasons: tuple[SettlementReason, ...],
    conflict_summary: SettlementConflictSummary,
    settlement_status: SettlementStatus,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
) -> SettlementVerdict:
    draft = SettlementVerdict(
        schema_version=SCHEMA_VERSION,
        settlement_id=settlement_id,
        forecast_id=forecast_id,
        forecast_hash=forecast_hash,
        binding_id=binding_id,
        binding_hash=binding_hash,
        evidence_packet_id=evidence_packet_id,
        evidence_hash=evidence_hash,
        decision=decision,
        reasons=tuple(reasons),
        conflict_summary=conflict_summary,
        settlement_status=settlement_status,
        created_by_lane=created_by_lane,
        authority_ref=authority_ref,
        settlement_hash="PENDING",
    )
    return replace(draft, settlement_hash=settlement_verdict_hash(draft))


def validate_settlement_verdict(verdict: SettlementVerdict | Mapping[str, Any]) -> SettlementValidationReport:
    from .validator import validate_settlement_verdict

    return validate_settlement_verdict(verdict)


def write_settlement_verdict_contract_audit(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    sample = build_settlement_verdict(
        settlement_id="settlement-verdict-v1",
        forecast_id="forecast-object-contract-v1",
        forecast_hash="fixture-forecast-hash",
        binding_id="outcome-binding-v1",
        binding_hash="fixture-binding-hash",
        evidence_packet_id="resolution-evidence-v1",
        evidence_hash="fixture-evidence-hash",
        decision=SettlementDecision.TRUE,
        reasons=(SettlementReason("r1", "BOOLEAN_EVENT", "Evidence supports TRUE verdict", ("src-1",), "POLICY_BOOLEAN_SETTLEMENT"),),
        conflict_summary=SettlementConflictSummary(False, (), "NO_CONFLICT_POLICY", "CLEAR"),
        settlement_status=SettlementStatus.SETTLED,
        created_by_lane="OPERATOR",
        authority_ref=AuthorityRef("MANUAL_RECEIPT", "receipt://settlement/approval", "Operator settlement receipt"),
    )
    report = validate_settlement_verdict(sample)
    payload = {
        "status": report.status,
        "settlement_hash": sample.settlement_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": sample.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = base / "out/audit/settlement_verdict_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
