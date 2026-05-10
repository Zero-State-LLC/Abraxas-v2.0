from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from typing import Any, Mapping

from .models import AuthorityRef, EvidenceConflict, EvidenceObservation, EvidenceStatus, ResolutionEvidenceItem, ResolutionEvidencePacket, ResolutionEvidenceSourceRef, ResolutionEvidenceValidationFinding, ResolutionEvidenceValidationReport

ALLOWED_SOURCE_TYPES = {"OFFICIAL_API", "PUBLIC_WEB", "MANUAL_RECEIPT", "MARKET_SOURCE", "SPORTS_DATA_SOURCE", "REPO_FIXTURE", "OPERATOR_ATTESTATION", "NOT_COMPUTABLE"}


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _to_packet(packet: ResolutionEvidencePacket | Mapping[str, Any]) -> ResolutionEvidencePacket:
    if isinstance(packet, ResolutionEvidencePacket):
        return packet
    data = dict(packet)
    items = []
    for item in data["evidence_items"]:
        obs = EvidenceObservation(source_ref=ResolutionEvidenceSourceRef(**item["observation"]["source_ref"]), **{k: v for k, v in item["observation"].items() if k != "source_ref"})
        items.append(ResolutionEvidenceItem(item_id=item["item_id"], observation=obs))
    return ResolutionEvidencePacket(
        schema_version=data["schema_version"],
        evidence_packet_id=data["evidence_packet_id"],
        binding_id=data["binding_id"],
        forecast_id=data["forecast_id"],
        forecast_hash=data["forecast_hash"],
        binding_hash=data["binding_hash"],
        evidence_items=tuple(items),
        conflicts=tuple(EvidenceConflict(**c) for c in data["conflicts"]),
        evidence_status=EvidenceStatus(data["evidence_status"]),
        created_by_lane=data["created_by_lane"],
        authority_ref=AuthorityRef(**data["authority_ref"]) if data.get("authority_ref") else None,
        void_reason=data.get("void_reason"),
        evidence_hash=data["evidence_hash"],
    )


def validate_resolution_evidence_packet(packet: ResolutionEvidencePacket | Mapping[str, Any]) -> ResolutionEvidenceValidationReport:
    obj = _to_packet(packet)
    findings: list[ResolutionEvidenceValidationFinding] = []
    status = "PASS"

    if obj.schema_version != "ResolutionEvidence.v1":
        findings.append(ResolutionEvidenceValidationFinding("SCHEMA_VERSION_INVALID", "not_computable", "schema_version must be ResolutionEvidence.v1."))
        status = "NOT_COMPUTABLE"

    if not obj.binding_id or not obj.forecast_id or not obj.forecast_hash or not obj.binding_hash:
        findings.append(ResolutionEvidenceValidationFinding("REQUIRED_LINKAGE_MISSING", "not_computable", "binding_id/forecast_id/forecast_hash/binding_hash are required."))
        status = "NOT_COMPUTABLE"

    if obj.evidence_status == EvidenceStatus.DRAFT:
        findings.append(ResolutionEvidenceValidationFinding("DRAFT_NOT_SETTLEMENT_READY", "warning", "DRAFT evidence is not settlement-ready."))
        if status == "PASS":
            status = "WARN"

    if obj.evidence_status == EvidenceStatus.EVIDENCE_COLLECTED and not obj.evidence_items:
        findings.append(ResolutionEvidenceValidationFinding("EVIDENCE_ITEMS_REQUIRED", "error", "EVIDENCE_COLLECTED requires at least one evidence item."))
        status = "BLOCKED"

    if obj.evidence_status == EvidenceStatus.SETTLEMENT_READY:
        if not obj.evidence_items:
            findings.append(ResolutionEvidenceValidationFinding("SETTLEMENT_ITEMS_REQUIRED", "error", "SETTLEMENT_READY requires evidence items."))
            status = "BLOCKED"
        if obj.conflicts:
            findings.append(ResolutionEvidenceValidationFinding("UNRESOLVED_CONFLICTS_BLOCKED", "error", "SETTLEMENT_READY cannot include unresolved conflicts."))
            status = "BLOCKED"
        if obj.authority_ref is None:
            findings.append(ResolutionEvidenceValidationFinding("SETTLEMENT_AUTHORITY_REQUIRED", "not_computable", "SETTLEMENT_READY requires authority_ref."))
            if status != "BLOCKED":
                status = "NOT_COMPUTABLE"

    if obj.evidence_status == EvidenceStatus.CONFLICTING and not obj.conflicts:
        findings.append(ResolutionEvidenceValidationFinding("CONFLICTS_REQUIRED", "error", "CONFLICTING status requires at least one conflict."))
        status = "BLOCKED"

    if obj.evidence_status == EvidenceStatus.VOID and not obj.void_reason:
        findings.append(ResolutionEvidenceValidationFinding("VOID_REASON_REQUIRED", "not_computable", "VOID requires a reason."))
        status = "NOT_COMPUTABLE"

    if obj.created_by_lane == "SHADOW" and obj.evidence_status == EvidenceStatus.SETTLEMENT_READY:
        findings.append(ResolutionEvidenceValidationFinding("SHADOW_SETTLEMENT_READY_BLOCKED", "error", "SHADOW may not mark SETTLEMENT_READY."))
        status = "BLOCKED"
    if obj.created_by_lane == "PROJECTION" and obj.evidence_status != EvidenceStatus.DRAFT:
        findings.append(ResolutionEvidenceValidationFinding("PROJECTION_AUTHORITY_BLOCKED", "error", "PROJECTION may not create authoritative evidence packets."))
        status = "BLOCKED"
    if obj.created_by_lane == "CANON" and obj.evidence_status != EvidenceStatus.DRAFT:
        findings.append(ResolutionEvidenceValidationFinding("CANON_EVIDENCE_BLOCKED", "error", "CANON may define contracts only."))
        status = "BLOCKED"

    for item in obj.evidence_items:
        if item.observation.source_ref.source_type not in ALLOWED_SOURCE_TYPES:
            findings.append(ResolutionEvidenceValidationFinding("SOURCE_TYPE_INVALID", "not_computable", "Unknown evidence source type."))
            if status != "BLOCKED":
                status = "NOT_COMPUTABLE"

    receipt_hash = _sha256_text(_canonical_json({"status": status, "findings": [asdict(f) for f in findings], "evidence_packet_id": obj.evidence_packet_id}))
    return ResolutionEvidenceValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)
