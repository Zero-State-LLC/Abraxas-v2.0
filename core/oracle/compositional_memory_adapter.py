from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from core.belief_graph.compositional_memory import (
    CompositionalMemoryEntry,
    MemoryModality,
    build_compositional_memory_packet,
    memory_entry_from_evidence,
)
from core.belief_graph.evidence_object import EvidenceObject

OracleSignalLane = Literal["OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"]


class NormalizedOracleEvidence(BaseModel):
    """Bounded adapter input for already-normalized Oracle evidence.

    This contract performs no extraction, classification, embedding search, or
    model inference. The caller must supply normalized evidence and an explicit
    modality before the adapter can emit a compositional-memory packet.
    """

    schema_version: Literal["NormalizedOracleEvidence.v1"] = "NormalizedOracleEvidence.v1"
    signal_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    evidence_type: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    modality: MemoryModality
    lane: OracleSignalLane
    provenance: dict[str, Any]
    semantic_tags: tuple[str, ...] = Field(default_factory=tuple)

    model_config = {"frozen": True}

    @field_validator("signal_id", "source", "timestamp", "evidence_type", "content_hash")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("non-empty value required")
        return value

    @field_validator("semantic_tags", mode="before")
    @classmethod
    def _normalize_tags(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        if not isinstance(value, (list, tuple, set, frozenset)):
            raise TypeError("semantic tag collection required")
        return tuple(sorted({str(item).strip() for item in value if str(item).strip()}))


def _evidence_object(item: NormalizedOracleEvidence) -> EvidenceObject:
    provenance = dict(item.provenance)
    provenance.update(
        {
            "oracle_signal_id": item.signal_id,
            "oracle_lane": item.lane,
            "adapter": "core.oracle.compositional_memory_adapter",
        }
    )
    return EvidenceObject(
        source=item.source,
        provenance=provenance,
        timestamp=item.timestamp,
        evidence_type=item.evidence_type,
        hash=item.content_hash,
    )


def adapt_oracle_evidence_to_compositional_memory(
    items: Sequence[NormalizedOracleEvidence | Mapping[str, Any]],
) -> dict[str, Any]:
    """Convert normalized Oracle evidence into one advisory memory packet.

    The transform is deterministic and fail-closed. Empty input returns a
    NOT_COMPUTABLE receipt rather than an empty authoritative memory surface.
    """

    models = [
        item if isinstance(item, NormalizedOracleEvidence) else NormalizedOracleEvidence.model_validate(item)
        for item in items
    ]
    models = sorted(models, key=lambda item: item.signal_id)

    if not models:
        return {
            "schema_version": "OracleCompositionalMemoryAdapterReceipt.v1",
            "status": "NOT_COMPUTABLE",
            "reason": "NO_NORMALIZED_ORACLE_EVIDENCE",
            "input_count": 0,
            "memory_packet": None,
            "model_inference": False,
            "embedding_search": False,
            "truth_assignment": False,
            "forecast_routing": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "advisory_only": True,
        }

    entries: list[CompositionalMemoryEntry] = []
    for item in models:
        evidence = _evidence_object(item)
        entries.append(
            memory_entry_from_evidence(
                evidence,
                memory_id=f"oracle:{item.signal_id}",
                modality=item.modality,
                source_ref=item.signal_id,
                semantic_tags=item.semantic_tags,
            )
        )

    packet = build_compositional_memory_packet(entries)
    return {
        "schema_version": "OracleCompositionalMemoryAdapterReceipt.v1",
        "status": "ORACLE_COMPOSITIONAL_MEMORY_ADAPTED_ADVISORY_ONLY",
        "input_count": len(models),
        "lanes": sorted({item.lane for item in models}),
        "memory_packet": packet,
        "model_inference": False,
        "embedding_search": False,
        "truth_assignment": False,
        "forecast_routing": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "advisory_only": True,
    }
