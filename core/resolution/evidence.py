from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Mapping

from .models import (
    AuthorityRef,
    EvidenceConflict,
    EvidenceObservation,
    EvidenceStatus,
    ResolutionEvidenceItem,
    ResolutionEvidencePacket,
    ResolutionEvidenceSourceRef,
    ResolutionEvidenceValidationReport,
)

SCHEMA_VERSION = "ResolutionEvidence.v1"


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload(packet: ResolutionEvidencePacket | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(packet, ResolutionEvidencePacket):
        return asdict(packet)
    return dict(packet)


def canonical_resolution_evidence_json(packet: ResolutionEvidencePacket | Mapping[str, Any]) -> str:
    payload = _payload(packet)
    payload.pop("evidence_hash", None)
    return _canonical_json(payload)


def resolution_evidence_hash(packet: ResolutionEvidencePacket | Mapping[str, Any]) -> str:
    return _sha256_text(canonical_resolution_evidence_json(packet))


def build_resolution_evidence_packet(
    evidence_packet_id: str,
    binding_id: str,
    forecast_id: str,
    forecast_hash: str,
    binding_hash: str,
    evidence_items: tuple[ResolutionEvidenceItem, ...],
    conflicts: tuple[EvidenceConflict, ...],
    evidence_status: EvidenceStatus,
    created_by_lane: str,
    authority_ref: AuthorityRef | None,
    void_reason: str | None = None,
) -> ResolutionEvidencePacket:
    draft = ResolutionEvidencePacket(
        schema_version=SCHEMA_VERSION,
        evidence_packet_id=evidence_packet_id,
        binding_id=binding_id,
        forecast_id=forecast_id,
        forecast_hash=forecast_hash,
        binding_hash=binding_hash,
        evidence_items=tuple(evidence_items),
        conflicts=tuple(conflicts),
        evidence_status=evidence_status,
        created_by_lane=created_by_lane,
        authority_ref=authority_ref,
        void_reason=void_reason,
        evidence_hash="PENDING",
    )
    return replace(draft, evidence_hash=resolution_evidence_hash(draft))


def validate_resolution_evidence_packet(packet: ResolutionEvidencePacket | Mapping[str, Any]) -> ResolutionEvidenceValidationReport:
    from .validator import validate_resolution_evidence_packet

    return validate_resolution_evidence_packet(packet)


def write_resolution_evidence_contract_audit(base_dir: Path | str = ".") -> str:
    base = Path(base_dir)
    sample = build_resolution_evidence_packet(
        evidence_packet_id="resolution-evidence-v1",
        binding_id="outcome-binding-v1",
        forecast_id="forecast-object-contract-v1",
        forecast_hash="fixture-forecast-hash",
        binding_hash="fixture-binding-hash",
        evidence_items=(
            ResolutionEvidenceItem(
                item_id="item-1",
                observation=EvidenceObservation(
                    observation_id="obs-1",
                    observed_value="true",
                    observation_type="BOOLEAN_EVENT",
                    source_ref=ResolutionEvidenceSourceRef("REPO_FIXTURE", "fixtures/resolution/evidence.json", "Local evidence fixture"),
                    collection_policy="COLLECT_POLICY_STATIC",
                    confidence_policy="CONFIDENCE_POLICY_MEDIUM",
                ),
            ),
        ),
        conflicts=(),
        evidence_status=EvidenceStatus.EVIDENCE_COLLECTED,
        created_by_lane="FORECAST",
        authority_ref=AuthorityRef("MANUAL_RECEIPT", "receipt://resolution/evidence", "Operator evidence receipt"),
    )
    report = validate_resolution_evidence_packet(sample)
    payload = {
        "status": report.status,
        "evidence_hash": sample.evidence_hash,
        "receipt_hash": report.receipt_hash,
        "findings": [asdict(f) for f in report.findings],
        "schema_version": sample.schema_version,
    }
    text = _canonical_json(payload) + "\n"
    out = base / "out/audit/resolution_evidence_contract.latest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return _sha256_text(text)
