from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceStatus(str, Enum):
    DRAFT = "DRAFT"
    EVIDENCE_COLLECTED = "EVIDENCE_COLLECTED"
    CONFLICTING = "CONFLICTING"
    INSUFFICIENT = "INSUFFICIENT"
    SETTLEMENT_READY = "SETTLEMENT_READY"
    VOID = "VOID"


@dataclass(frozen=True)
class ResolutionEvidenceSourceRef:
    source_type: str
    source_id: str
    label: str


@dataclass(frozen=True)
class EvidenceObservation:
    observation_id: str
    observed_value: str
    observation_type: str
    source_ref: ResolutionEvidenceSourceRef
    collection_policy: str
    confidence_policy: str


@dataclass(frozen=True)
class ResolutionEvidenceItem:
    item_id: str
    observation: EvidenceObservation


@dataclass(frozen=True)
class EvidenceConflict:
    conflict_id: str
    source_ids: tuple[str, ...]
    conflict_type: str
    severity: str
    resolution_policy: str


@dataclass(frozen=True)
class AuthorityRef:
    authority_type: str
    authority_id: str
    label: str


@dataclass(frozen=True)
class ResolutionEvidencePacket:
    schema_version: str
    evidence_packet_id: str
    binding_id: str
    forecast_id: str
    forecast_hash: str
    binding_hash: str
    evidence_items: tuple[ResolutionEvidenceItem, ...]
    conflicts: tuple[EvidenceConflict, ...]
    evidence_status: EvidenceStatus
    created_by_lane: str
    authority_ref: AuthorityRef | None
    void_reason: str | None
    evidence_hash: str


@dataclass(frozen=True)
class ResolutionEvidenceValidationFinding:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ResolutionEvidenceValidationReport:
    status: str
    findings: tuple[ResolutionEvidenceValidationFinding, ...]
    receipt_hash: str
