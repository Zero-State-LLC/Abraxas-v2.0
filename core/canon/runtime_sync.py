from __future__ import annotations

import json
from dataclasses import asdict

from core.governance_runtime.models import ValidationFinding, ValidationReport

from .doctrine_hash import canonical_doctrine_hash
from .models import CanonAttestation, CanonDoctrineRef, CanonSource, CanonSyncPacket


def build_canon_sync_packet(
    notion_page_id: str | None,
    repo_file_ref: str,
    repo_execution_hash: str,
    sync_posture: str = "CANON_SYNCED",
) -> CanonSyncPacket:
    status = "PASS" if notion_page_id else "NOT_COMPUTABLE"
    canon_ref = CanonDoctrineRef(
        source_type=CanonSource.NOTION_PAGE,
        source_id=notion_page_id or "NOT_COMPUTABLE",
        label="notion_canon",
    )
    repo_ref = CanonDoctrineRef(
        source_type=CanonSource.REPO_FILE,
        source_id=repo_file_ref,
        label="repo_execution",
    )
    attestation = CanonAttestation(
        doctrine_hash="PENDING",
        repo_execution_hash=repo_execution_hash,
        sync_posture=sync_posture,
    )
    packet = CanonSyncPacket(canon_ref=canon_ref, repo_ref=repo_ref, attestation=attestation, status=status)
    doctrine_hash = canonical_doctrine_hash(packet)
    packet = CanonSyncPacket(
        canon_ref=canon_ref,
        repo_ref=repo_ref,
        attestation=CanonAttestation(doctrine_hash=doctrine_hash, repo_execution_hash=repo_execution_hash, sync_posture=sync_posture),
        status=status,
    )
    return packet


def validate_canon_sync_packet(packet: CanonSyncPacket) -> ValidationReport:
    findings: list[ValidationFinding] = []

    if packet.canon_ref.source_type == CanonSource.NOTION_PAGE and packet.canon_ref.source_id == "NOT_COMPUTABLE":
        findings.append(ValidationFinding(code="CANON_SOURCE_NOT_COMPUTABLE", severity="not_computable", message="Missing Notion page ID prevents canon sync computation."))

    if packet.canon_ref.source_type == CanonSource.REPO_FILE:
        findings.append(ValidationFinding(code="REPO_ONLY_AUTHORITY_DRIFT", severity="warning", message="Repo-only authority is a canon drift risk."))

    recomputed = canonical_doctrine_hash(packet)
    if packet.attestation.doctrine_hash != recomputed:
        findings.append(ValidationFinding(code="DOCTRINE_HASH_MISMATCH", severity="error", message="Doctrine hash does not match canonical packet hash."))

    status = "PASS" if not findings else "FAIL"
    if any(f.severity == "not_computable" for f in findings):
        status = "NOT_COMPUTABLE"

    receipt_hash = canonical_doctrine_hash(packet)
    return ValidationReport(status=status, findings=tuple(findings), receipt_hash=receipt_hash)


def canon_sync_packet_json(packet: CanonSyncPacket) -> str:
    return json.dumps(asdict(packet), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

from core.audit.status import build_audit_status_envelope


def build_canon_audit_payload(packet: CanonSyncPacket) -> dict:
    report = validate_canon_sync_packet(packet)
    envelope = build_audit_status_envelope(
        artifact_id="canon_authority_stub",
        artifact_type="canon_authority",
        status=report.status,
        findings=[{"code": f.code, "severity": f.severity, "message": f.message} for f in report.findings],
        source_artifacts=[],
        artifact_hash=report.receipt_hash,
        generated_at_policy="INPUT_DERIVED",
    )
    return {"packet": asdict(packet), "receipt_hash": report.receipt_hash, "status": report.status, "posture": report.status, "validation_status": report.status, "audit_envelope": envelope}
