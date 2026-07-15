"""Deterministic contracts for the stabilization-readiness skill."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from core.canonical.json import canonical_hash
from core.campaign_director.stabilization_campaign import (
    CampaignClass,
    StabilizationEntryDecision,
    StabilizationPhase,
)


class ContractClassification(StrEnum):
    FROZEN = "CONTRACT.FROZEN"
    VERSIONED = "CONTRACT.VERSIONED"
    CONTROLLED = "CONTRACT.CONTROLLED"
    EXPERIMENTAL = "CONTRACT.EXPERIMENTAL"
    INTERNAL = "CONTRACT.INTERNAL"
    ORPHANED = "CONTRACT.ORPHANED"
    NOT_COMPUTABLE = "CONTRACT.NOT_COMPUTABLE"


class ReproducibilityOutcome(StrEnum):
    REPRODUCIBLE = "REPRODUCIBLE"
    REPRODUCIBLE_WITH_DECLARED_VARIANCE = (
        "REPRODUCIBLE_WITH_DECLARED_VARIANCE"
    )
    NON_REPRODUCIBLE = "NON_REPRODUCIBLE"
    NOT_COMPUTABLE = "NOT_COMPUTABLE"


class ComparisonMode(StrEnum):
    BYTE_EXACT = "BYTE_EXACT"
    HASH_EXACT = "HASH_EXACT"
    SEMANTIC_EXACT = "SEMANTIC_EXACT"
    SCHEMA_EXACT = "SCHEMA_EXACT"
    SET_EQUIVALENT = "SET_EQUIVALENT"
    ORDERED_EQUIVALENT = "ORDERED_EQUIVALENT"
    BOUNDED_NUMERIC_VARIANCE = "BOUNDED_NUMERIC_VARIANCE"


@dataclass(frozen=True, slots=True)
class AuthorityLocks:
    advisory_only: bool = True
    contract_freeze: bool = False
    production_activation: bool = False
    canon_mutation: bool = False
    runtime_promotion: bool = False
    external_writeback: bool = False

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)

    def is_locked(self) -> bool:
        values = self.to_dict()
        return values.pop("advisory_only") and not any(values.values())


@dataclass(frozen=True, slots=True)
class StabilizationScope:
    python: bool = True
    typescript: bool = True
    schemas: bool = True
    artifacts: bool = True
    cli: bool = True
    runtime_activation: bool = False

    def to_dict(self) -> dict[str, bool]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StabilizationState:
    baseline_commit: str
    campaign_id: str = "ABRAXAS_STABILIZATION_READINESS_CAMPAIGN_001"
    campaign_class: str = CampaignClass.STABILIZATION_READINESS.value
    phase: str = StabilizationPhase.BASELINE_DISCOVERY.value
    scope: StabilizationScope = field(default_factory=StabilizationScope)
    feature_expansion_allowed: bool = False
    authority: AuthorityLocks = field(default_factory=AuthorityLocks)
    evidence_refs: tuple[str, ...] = ()
    blocking_findings: tuple[str, ...] = ()
    bounded_exceptions: tuple[str, ...] = ()
    recommended_next_packet: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "campaign_class": self.campaign_class,
            "phase": self.phase,
            "baseline_commit": self.baseline_commit,
            "scope": self.scope.to_dict(),
            "feature_expansion_allowed": self.feature_expansion_allowed,
            "authority": self.authority.to_dict(),
            "evidence_refs": sorted(self.evidence_refs),
            "blocking_findings": sorted(self.blocking_findings),
            "bounded_exceptions": sorted(self.bounded_exceptions),
            "recommended_next_packet": self.recommended_next_packet,
        }

    def deterministic_hash(self) -> str:
        return canonical_hash(self.to_dict())


@dataclass(frozen=True, slots=True)
class ContractRecord:
    contract_id: str
    language: str
    surface: str
    classification: str = ContractClassification.CONTROLLED.value
    consumers: tuple[str, ...] = ()
    validators: tuple[str, ...] = ()
    schemas: tuple[str, ...] = ()
    compatibility_policy: str = "NOT_COMPUTABLE"
    evidence_complete: bool = False
    provenance: str = "OBSERVED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "language": self.language,
            "surface": self.surface,
            "classification": self.classification,
            "consumers": sorted(self.consumers),
            "validators": sorted(self.validators),
            "schemas": sorted(self.schemas),
            "compatibility_policy": self.compatibility_policy,
            "evidence_complete": self.evidence_complete,
            "provenance": self.provenance,
        }


@dataclass(frozen=True, slots=True)
class ConformanceCase:
    case_id: str
    description: str
    input: dict[str, Any]
    expected: dict[str, Any]
    comparison_mode: str = ComparisonMode.SEMANTIC_EXACT.value
    implementations: tuple[str, ...] = ("python",)
    allowed_variance: float | None = None
    provenance: str = "OBSERVED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "input": self.input,
            "expected": self.expected,
            "comparison_mode": self.comparison_mode,
            "implementations": list(self.implementations),
            "allowed_variance": self.allowed_variance,
            "provenance": self.provenance,
        }


@dataclass(frozen=True, slots=True)
class StabilizationGateDecision:
    decision: str = StabilizationEntryDecision.HELD.value
    python_ready: bool = False
    typescript_ready: bool = False
    contract_inventory_complete: bool = False
    conformance_corpus_ready: bool = False
    reproducibility_ready: bool = False
    canonical_artifact_safety_ready: bool = False
    full_suite_confidence: str = "NOT_COMPUTABLE"
    blocking_findings: tuple[str, ...] = ()
    bounded_exceptions: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    operator_action_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("blocking_findings", "bounded_exceptions", "evidence_refs"):
            payload[key] = sorted(payload[key])
        return payload
