"""Canonical contract spine for the Abraxas Moses function.

The models in this module are immutable handoff artifacts over existing
Abraxas surfaces. They intentionally contain no orchestration or execution
engine.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class MeaningStatus(str, Enum):
    resolved = "RESOLVED"
    provisional = "PROVISIONAL"
    contradicted = "CONTRADICTED"
    not_computable = "NOT_COMPUTABLE"


class GroundingDisposition(str, Enum):
    resolved = "RESOLVED"
    provisional = "PROVISIONAL"
    contradicted = "CONTRADICTED"
    not_computable = "NOT_COMPUTABLE"


class _CanonicalSpineArtifact(BaseModel):
    """Shared immutable, authority-locked artifact behavior."""

    canonical_hash: str | None = None
    authority: Authority = Field(default_factory=Authority)

    model_config = {"frozen": True}

    def canonical_payload(self) -> dict[str, Any]:
        payload = self.model_dump(mode="json")
        payload.pop("canonical_hash", None)
        return payload

    def computed_canonical_hash(self) -> str:
        return canonical_hash(self.canonical_payload())

    @model_validator(mode="after")
    def _seal_hash_and_authority(self) -> "_CanonicalSpineArtifact":
        self.authority.assert_locked()
        expected = self.computed_canonical_hash()
        if self.canonical_hash is None:
            object.__setattr__(self, "canonical_hash", expected)
        elif self.canonical_hash != expected:
            raise ValueError("canonical_hash does not match canonical payload")
        return self


class MeaningPacket(_CanonicalSpineArtifact):
    schema_version: Literal["MeaningPacket.v1"] = "MeaningPacket.v1"
    meaning_id: str = Field(min_length=1)
    observations: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    interpretations: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    semantic_invariants: tuple[str, ...] = Field(default_factory=tuple)
    representation_variants: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    contradictions: tuple[str, ...] = Field(default_factory=tuple)
    uncertainty: tuple[str, ...] = Field(default_factory=tuple)
    provenance: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    status: MeaningStatus

    @model_validator(mode="after")
    def _meaning_state_is_honest(self) -> "MeaningPacket":
        if self.status == MeaningStatus.resolved and self.contradictions:
            raise ValueError("RESOLVED MeaningPacket cannot contain unresolved contradictions")
        if self.status == MeaningStatus.not_computable and not self.uncertainty:
            raise ValueError("NOT_COMPUTABLE MeaningPacket requires uncertainty reasons")
        return self


class GroundingReceipt(_CanonicalSpineArtifact):
    schema_version: Literal["GroundingReceipt.v1"] = "GroundingReceipt.v1"
    grounding_receipt_id: str = Field(min_length=1)
    meaning_id: str = Field(min_length=1)
    meaning_packet_hash: str = Field(min_length=64, max_length=64)
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple)
    shadow_findings: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    grounding_disposition: GroundingDisposition
    unresolved: tuple[str, ...] = Field(default_factory=tuple)
    provenance: tuple[dict[str, Any], ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _grounding_state_is_honest(self) -> "GroundingReceipt":
        if self.grounding_disposition == GroundingDisposition.not_computable and not self.unresolved:
            raise ValueError("NOT_COMPUTABLE GroundingReceipt requires unresolved reasons")
        return self


class LoweringStep(BaseModel):
    stage: Literal[
        "DOMAIN",
        "REQUIREMENTS",
        "JOURNEY",
        "WORKFLOW",
        "STATE_TRANSITION",
        "CONTRACT",
        "DATA_GOVERNANCE_ARCHITECTURE",
        "ACCEPTANCE",
        "IMPLEMENTATION",
    ]
    input_refs: tuple[str, ...] = Field(default_factory=tuple)
    output_refs: tuple[str, ...] = Field(default_factory=tuple)
    preserved_invariants: tuple[str, ...] = Field(default_factory=tuple)
    declared_changes: tuple[str, ...] = Field(default_factory=tuple)

    model_config = {"frozen": True}


class ArchitecturePacket(_CanonicalSpineArtifact):
    schema_version: Literal["ArchitecturePacket.v1"] = "ArchitecturePacket.v1"
    architecture_id: str = Field(min_length=1)
    meaning_id: str = Field(min_length=1)
    meaning_packet_hash: str = Field(min_length=64, max_length=64)
    grounding_receipt_id: str = Field(min_length=1)
    grounding_receipt_hash: str = Field(min_length=64, max_length=64)
    grounding_disposition: GroundingDisposition
    semantic_invariants: tuple[str, ...] = Field(default_factory=tuple)
    lowering_trace: tuple[LoweringStep, ...] = Field(default_factory=tuple)
    domain: dict[str, Any] = Field(default_factory=dict)
    requirements: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    journeys: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    workflows: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    state_transitions: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    contracts: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    acceptance_tests: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    implementation_tasks: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    unresolved: tuple[str, ...] = Field(default_factory=tuple)
    provenance: tuple[dict[str, Any], ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _lowering_requires_grounding(self) -> "ArchitecturePacket":
        if self.grounding_disposition in {
            GroundingDisposition.contradicted,
            GroundingDisposition.not_computable,
        }:
            raise ValueError(
                "ArchitecturePacket cannot be emitted from CONTRADICTED or NOT_COMPUTABLE grounding"
            )
        if not self.lowering_trace:
            raise ValueError("ArchitecturePacket requires a lowering trace")
        return self


class OutcomeReceipt(_CanonicalSpineArtifact):
    schema_version: Literal["OutcomeReceipt.v1"] = "OutcomeReceipt.v1"
    outcome_receipt_id: str = Field(min_length=1)
    architecture_id: str = Field(min_length=1)
    architecture_packet_hash: str = Field(min_length=64, max_length=64)
    expected_outcomes: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    observed_outcomes: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    settlements: dict[str, Any] = Field(default_factory=dict)
    deviations: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple)
    provenance: tuple[dict[str, Any], ...] = Field(default_factory=tuple)
    evidence_only: Literal[True] = True
