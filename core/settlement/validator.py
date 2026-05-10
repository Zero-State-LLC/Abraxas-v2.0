from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import AuthorityRef, SettlementConflictSummary, SettlementDecision, SettlementReason, SettlementStatus, SettlementValidationFinding, SettlementValidationReport, SettlementVerdict


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_verdict(verdict: SettlementVerdict | Mapping[str, Any]) -> SettlementVerdict:
    if isinstance(verdict, SettlementVerdict):
        return verdict
    data = dict(verdict)
    return SettlementVerdict(
        schema_version=data["schema_version"],
        settlement_id=data["settlement_id"],
        forecast_id=data["forecast_id"],
        forecast_hash=data["forecast_hash"],
        binding_id=data["binding_id"],
        binding_hash=data["binding_hash"],
        evidence_packet_id=data["evidence_packet_id"],
        evidence_hash=data["evidence_hash"],
        decision=SettlementDecision(data["decision"]),
        reasons=tuple(SettlementReason(**r) for r in data["reasons"]),
        conflict_summary=SettlementConflictSummary(**data["conflict_summary"]),
        settlement_status=SettlementStatus(data["settlement_status"]),
        created_by_lane=data["created_by_lane"],
        authority_ref=AuthorityRef(**data["authority_ref"]) if data.get("authority_ref") else None,
        settlement_hash=data["settlement_hash"],
    )


def validate_settlement_verdict(verdict: SettlementVerdict | Mapping[str, Any]) -> SettlementValidationReport:
    obj = _to_verdict(verdict)
    findings: list[SettlementValidationFinding] = []
    status = "PASS"

    if obj.schema_version != "SettlementVerdict.v1":
        findings.append(SettlementValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be SettlementVerdict.v1."))
        status = "NOT_COMPUTABLE"

    if not all([obj.forecast_id, obj.forecast_hash, obj.binding_id, obj.binding_hash, obj.evidence_packet_id, obj.evidence_hash]):
        findings.append(SettlementValidationFinding("SETTLEMENT_LINKAGE_MISSING", "not_computable", "Forecast/binding/evidence refs and hashes are required."))
        status = "NOT_COMPUTABLE"

    if obj.settlement_status == SettlementStatus.DRAFT:
        findings.append(SettlementValidationFinding("DRAFT_NOT_SCORE_READY", "warning", "DRAFT settlement is not score-ready."))
        if status == "PASS":
            status = "WARN"

    if obj.settlement_status == SettlementStatus.SETTLED:
        if obj.decision not in {SettlementDecision.TRUE, SettlementDecision.FALSE, SettlementDecision.PARTIAL}:
            findings.append(SettlementValidationFinding("SETTLED_DECISION_INVALID", "error", "SETTLED requires TRUE/FALSE/PARTIAL decision."))
            status = "BLOCKED"
        if not obj.reasons:
            findings.append(SettlementValidationFinding("SETTLED_REASON_REQUIRED", "error", "SETTLED requires at least one reason."))
            status = "BLOCKED"
        if obj.authority_ref is None:
            findings.append(SettlementValidationFinding("SETTLED_AUTHORITY_REQUIRED", "not_computable", "SETTLED requires authority_ref."))
            if status != "BLOCKED":
                status = "NOT_COMPUTABLE"
        if obj.conflict_summary.has_conflicts:
            findings.append(SettlementValidationFinding("UNRESOLVED_CONFLICTS_BLOCKED", "error", "SETTLED must not have unresolved conflicts."))
            status = "BLOCKED"

    if obj.settlement_status == SettlementStatus.CONFLICTING and not obj.conflict_summary.has_conflicts:
        findings.append(SettlementValidationFinding("CONFLICT_SUMMARY_REQUIRED", "error", "CONFLICTING requires has_conflicts=true."))
        status = "BLOCKED"

    if obj.settlement_status == SettlementStatus.VOID:
        if obj.decision != SettlementDecision.VOID:
            findings.append(SettlementValidationFinding("VOID_DECISION_REQUIRED", "error", "VOID status requires VOID decision."))
            status = "BLOCKED"
        if not obj.reasons:
            findings.append(SettlementValidationFinding("VOID_REASON_REQUIRED", "not_computable", "VOID requires at least one reason."))
            if status != "BLOCKED":
                status = "NOT_COMPUTABLE"

    if obj.settlement_status == SettlementStatus.NOT_COMPUTABLE or obj.decision == SettlementDecision.NOT_COMPUTABLE:
        findings.append(SettlementValidationFinding("NOT_SCORE_READY", "warning", "NOT_COMPUTABLE decision/status is not score-ready."))
        if status == "PASS":
            status = "WARN"

    if obj.created_by_lane == "SHADOW" and obj.settlement_status == SettlementStatus.SETTLED:
        findings.append(SettlementValidationFinding("SHADOW_SETTLED_BLOCKED", "error", "SHADOW may not mark SETTLED."))
        status = "BLOCKED"
    if obj.created_by_lane == "PROJECTION" and obj.settlement_status != SettlementStatus.DRAFT:
        findings.append(SettlementValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION may not create authoritative settlement verdicts."))
        status = "BLOCKED"
    if obj.created_by_lane == "CANON" and obj.settlement_status != SettlementStatus.DRAFT:
        findings.append(SettlementValidationFinding("CANON_SETTLEMENT_BLOCKED", "error", "CANON may define schema/contracts only."))
        status = "BLOCKED"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "settlement_id": obj.settlement_id}))
    return SettlementValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)
