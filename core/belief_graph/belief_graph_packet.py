from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from core.belief_graph.claim_object import ClaimObject
from core.belief_graph.evidence_object import EvidenceObject
from core.belief_graph.signal_graph import SignalGraph
from core.belief_graph.theory_object import TheoryObject

PATCH_ID = "PATCH-ABX-BELIEF-GRAPH-001"
FINAL_STATUS = "BELIEF_GRAPH_SCAFFOLD_ADVISORY_ONLY"


class ShadowForecastSeparation(BaseModel):
    SHADOW_SURFACE: Literal["SHADOW"] = "SHADOW"
    FORECAST_SURFACE: Literal["FORECAST"] = "FORECAST"
    FORECAST_ROUTING: Literal[False] = False

    model_config = {"frozen": True}


class BeliefGraphAuthorityLocks(BaseModel):
    FORECAST_ROUTING: Literal[False] = False
    CANON_MUTATION: Literal[False] = False
    RUNTIME_MUTATION: Literal[False] = False
    EXECUTION_AUTHORITY: Literal[False] = False
    TRUTH_ASSIGNMENT: Literal[False] = False
    BELIEF_PROMOTION: Literal[False] = False

    model_config = {"frozen": True}


class BeliefGraphPacket(BaseModel):
    schema_version: Literal["BeliefGraphPacket.v1"] = "BeliefGraphPacket.v1"
    patch_id: Literal[PATCH_ID] = PATCH_ID
    claims: tuple[ClaimObject, ...] = Field(default_factory=tuple)
    evidence: tuple[EvidenceObject, ...] = Field(default_factory=tuple)
    theories: tuple[TheoryObject, ...] = Field(default_factory=tuple)
    signal_graph: SignalGraph
    provenance: dict[str, Any]
    shadow_forecast_separation: ShadowForecastSeparation = Field(
        default_factory=ShadowForecastSeparation
    )
    authority_locks: BeliefGraphAuthorityLocks = Field(
        default_factory=BeliefGraphAuthorityLocks
    )
    confidence_behavior: Literal["PRESERVE_INPUT"] = "PRESERVE_INPUT"
    not_computable_behavior: Literal["PRESERVE"] = "PRESERVE"
    FORECAST_ROUTING: Literal[False] = False
    CANON_MUTATION: Literal[False] = False
    RUNTIME_MUTATION: Literal[False] = False
    EXECUTION_AUTHORITY: Literal[False] = False
    TRUTH_ASSIGNMENT: Literal[False] = False
    BELIEF_PROMOTION: Literal[False] = False
    FINAL_STATUS: Literal[FINAL_STATUS] = FINAL_STATUS

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate_graph_integrity(self) -> "BeliefGraphPacket":
        claim_ids = {claim.id for claim in self.claims}
        evidence_ids = {item.hash for item in self.evidence}
        theory_ids = {theory.id for theory in self.theories}

        if len(claim_ids) != len(self.claims):
            raise ValueError("duplicate claim id")
        if len(evidence_ids) != len(self.evidence):
            raise ValueError("duplicate evidence hash")
        if len(theory_ids) != len(self.theories):
            raise ValueError("duplicate theory id")

        for claim in self.claims:
            missing_evidence = set(claim.evidence_refs) - evidence_ids
            if missing_evidence:
                raise ValueError("claim references missing evidence")

        for theory in self.theories:
            missing_claims = (
                set(theory.supporting_claims) | set(theory.conflicting_claims)
            ) - claim_ids
            if missing_claims:
                raise ValueError("theory references missing claims")
            missing_evidence = set(theory.evidence_refs) - evidence_ids
            if missing_evidence:
                raise ValueError("theory references missing evidence")

        for relationship in self.signal_graph.relationships:
            if relationship.source_type == "claim" and relationship.source_ref not in claim_ids:
                raise ValueError("signal graph references missing claim")
            if relationship.target_type == "claim" and relationship.target_ref not in claim_ids:
                raise ValueError("signal graph references missing claim")
            if (
                relationship.source_type == "evidence"
                and relationship.source_ref not in evidence_ids
            ):
                raise ValueError("signal graph references missing evidence")
            if (
                relationship.target_type == "evidence"
                and relationship.target_ref not in evidence_ids
            ):
                raise ValueError("signal graph references missing evidence")
            if relationship.source_type == "theory" and relationship.source_ref not in theory_ids:
                raise ValueError("signal graph references missing theory")
            if relationship.target_type == "theory" and relationship.target_ref not in theory_ids:
                raise ValueError("signal graph references missing theory")

        if self.authority_locks.model_dump() != {
            "FORECAST_ROUTING": self.FORECAST_ROUTING,
            "CANON_MUTATION": self.CANON_MUTATION,
            "RUNTIME_MUTATION": self.RUNTIME_MUTATION,
            "EXECUTION_AUTHORITY": self.EXECUTION_AUTHORITY,
            "TRUTH_ASSIGNMENT": self.TRUTH_ASSIGNMENT,
            "BELIEF_PROMOTION": self.BELIEF_PROMOTION,
        }:
            raise ValueError("authority locks must match belief graph seal")
        return self
