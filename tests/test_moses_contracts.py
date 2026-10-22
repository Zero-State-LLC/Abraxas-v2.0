from __future__ import annotations

import pytest
from pydantic import ValidationError

from core.moses.contracts import (
    ArchitecturePacket,
    GroundingDisposition,
    GroundingReceipt,
    LoweringStep,
    MeaningPacket,
    MeaningStatus,
    OutcomeReceipt,
)


def test_meaning_packet_hash_is_deterministic() -> None:
    payload = dict(
        meaning_id="meaning-001",
        observations=({"id": "obs-1", "value": "signal"},),
        interpretations=({"id": "int-1", "value": "meaning"},),
        semantic_invariants=("intent-preserved",),
        provenance=({"source": "oracle"},),
        status=MeaningStatus.resolved,
    )
    first = MeaningPacket(**payload)
    second = MeaningPacket(**payload)
    assert first.canonical_hash == second.canonical_hash


def test_resolved_meaning_rejects_contradictions() -> None:
    with pytest.raises(ValidationError):
        MeaningPacket(
            meaning_id="meaning-001",
            contradictions=("claim conflict",),
            status=MeaningStatus.resolved,
        )


def test_not_computable_requires_reason() -> None:
    with pytest.raises(ValidationError):
        MeaningPacket(
            meaning_id="meaning-001",
            status=MeaningStatus.not_computable,
        )


@pytest.mark.parametrize(
    "disposition",
    [GroundingDisposition.contradicted, GroundingDisposition.not_computable],
)
def test_architecture_fails_closed_on_ungrounded_meaning(disposition: GroundingDisposition) -> None:
    with pytest.raises(ValidationError):
        ArchitecturePacket(
            architecture_id="architecture-001",
            meaning_id="meaning-001",
            meaning_packet_hash="a" * 64,
            grounding_receipt_id="grounding-001",
            grounding_receipt_hash="b" * 64,
            grounding_disposition=disposition,
            lowering_trace=(
                LoweringStep(stage="DOMAIN", input_refs=("meaning-001",), output_refs=("domain-001",)),
            ),
        )


def test_architecture_requires_lowering_trace() -> None:
    with pytest.raises(ValidationError):
        ArchitecturePacket(
            architecture_id="architecture-001",
            meaning_id="meaning-001",
            meaning_packet_hash="a" * 64,
            grounding_receipt_id="grounding-001",
            grounding_receipt_hash="b" * 64,
            grounding_disposition=GroundingDisposition.resolved,
        )


def test_grounding_not_computable_requires_unresolved_reason() -> None:
    with pytest.raises(ValidationError):
        GroundingReceipt(
            grounding_receipt_id="grounding-001",
            meaning_id="meaning-001",
            meaning_packet_hash="a" * 64,
            grounding_disposition=GroundingDisposition.not_computable,
        )


def test_outcome_receipt_is_evidence_only_and_hash_sealed() -> None:
    receipt = OutcomeReceipt(
        outcome_receipt_id="outcome-001",
        architecture_id="architecture-001",
        architecture_packet_hash="c" * 64,
        expected_outcomes=({"id": "expected-1"},),
        observed_outcomes=({"id": "observed-1"},),
        evidence_refs=("evidence-001",),
    )
    assert receipt.evidence_only is True
    assert receipt.canonical_hash == receipt.computed_canonical_hash()


def test_supplied_bad_hash_fails_closed() -> None:
    with pytest.raises(ValidationError):
        MeaningPacket(
            meaning_id="meaning-001",
            status=MeaningStatus.provisional,
            canonical_hash="0" * 64,
        )
