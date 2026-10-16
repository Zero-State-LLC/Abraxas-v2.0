"""Adapters from existing Belief Graph output into the Moses contract spine."""

from __future__ import annotations

from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.moses.contracts import MeaningPacket, MeaningStatus


def meaning_packet_from_belief_graph(
    packet: BeliefGraphPacket,
    *,
    meaning_id: str,
    semantic_invariants: tuple[str, ...] = (),
    representation_variants: tuple[dict, ...] = (),
) -> MeaningPacket:
    """Project a BeliefGraphPacket into a MeaningPacket without new inference.

    This adapter is deliberately lossy only in representation, not semantics:
    it copies existing claims/theories/evidence and derives status solely from
    explicit upstream classifications. It does not call a model, resolve
    contradictions, assign truth, or grant authority.
    """
    observed = tuple(
        {
            "claim_id": claim.id,
            "statement": claim.statement,
            "status": claim.status,
            "confidence": claim.confidence,
            "evidence_refs": list(claim.evidence_refs),
        }
        for claim in packet.claims
        if claim.status == "OBSERVED"
    )
    interpretations = tuple(
        {
            "claim_id": claim.id,
            "statement": claim.statement,
            "status": claim.status,
            "confidence": claim.confidence,
            "evidence_refs": list(claim.evidence_refs),
        }
        for claim in packet.claims
        if claim.status in {"INFERRED", "SPECULATIVE"}
    )

    not_computable = [claim for claim in packet.claims if claim.status == "NOT_COMPUTABLE"]
    theory_conflicts = [
        theory
        for theory in packet.theories
        if theory.conflicting_claims
    ]
    contradictions = tuple(
        f"theory:{theory.id}:conflicts:{','.join(theory.conflicting_claims)}"
        for theory in theory_conflicts
    )
    uncertainty = tuple(
        f"claim:{claim.id}:NOT_COMPUTABLE"
        for claim in not_computable
    )

    if contradictions:
        status = MeaningStatus.contradicted
    elif uncertainty:
        status = MeaningStatus.not_computable
    else:
        # BeliefGraph does not itself prove resolution. Absence of an explicit
        # blocker therefore remains PROVISIONAL until the grounding gate acts.
        status = MeaningStatus.provisional

    provenance = (
        {
            "source": "BeliefGraphPacket.v1",
            "patch_id": packet.patch_id,
            "final_status": packet.FINAL_STATUS,
            "belief_graph_provenance": packet.provenance,
        },
    )

    return MeaningPacket(
        meaning_id=meaning_id,
        observations=observed,
        interpretations=interpretations,
        semantic_invariants=semantic_invariants,
        representation_variants=representation_variants,
        contradictions=contradictions,
        uncertainty=uncertainty,
        provenance=provenance,
        status=status,
    )
