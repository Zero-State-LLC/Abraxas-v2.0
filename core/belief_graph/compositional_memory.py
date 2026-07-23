from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from hashlib import sha256
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from core.belief_graph.evidence_object import EvidenceObject

MemoryModality = Literal["textual", "visual", "mixed"]


def _normalized_refs(values: Iterable[str]) -> tuple[str, ...]:
    refs = {str(value).strip() for value in values}
    refs.discard("")
    return tuple(sorted(refs))


class CompositionalMemoryEntry(BaseModel):
    """Immutable, provenance-bound external-memory descriptor.

    This adapts the useful MemEIC pattern (modality-aware external memory)
    without importing model checkpoints, trainable adapters, or runtime
    authority into Abraxas.
    """

    schema_version: Literal["CompositionalMemoryEntry.v1"] = "CompositionalMemoryEntry.v1"
    memory_id: str = Field(min_length=1)
    modality: MemoryModality
    source_ref: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    observed_at: str = Field(min_length=1)
    provenance: dict[str, Any]
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple)
    semantic_tags: tuple[str, ...] = Field(default_factory=tuple)

    model_config = {"frozen": True}

    @field_validator("memory_id", "source_ref", "content_hash", "observed_at")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("non-empty value required")
        return value

    @field_validator("evidence_refs", "semantic_tags", mode="before")
    @classmethod
    def _normalize_collections(cls, value: object) -> tuple[str, ...]:
        if value is None:
            return ()
        if not isinstance(value, (list, tuple, set, frozenset)):
            raise TypeError("reference collection required")
        return _normalized_refs(str(item) for item in value)


class KnowledgeConnectorLink(BaseModel):
    """Advisory bridge between separated textual and visual memories."""

    schema_version: Literal["KnowledgeConnectorLink.v1"] = "KnowledgeConnectorLink.v1"
    textual_memory_ref: str = Field(min_length=1)
    visual_memory_ref: str = Field(min_length=1)
    shared_evidence_refs: tuple[str, ...] = Field(default_factory=tuple)
    shared_semantic_tags: tuple[str, ...] = Field(default_factory=tuple)
    connector_hash: str = Field(min_length=1)

    model_config = {"frozen": True}


def memory_entry_from_evidence(
    evidence: EvidenceObject | Mapping[str, Any],
    *,
    memory_id: str,
    modality: MemoryModality,
    source_ref: str | None = None,
    semantic_tags: Sequence[str] = (),
) -> CompositionalMemoryEntry:
    evidence_model = evidence if isinstance(evidence, EvidenceObject) else EvidenceObject.model_validate(evidence)
    return CompositionalMemoryEntry(
        memory_id=memory_id,
        modality=modality,
        source_ref=source_ref or evidence_model.source,
        content_hash=evidence_model.hash,
        observed_at=evidence_model.timestamp,
        provenance=evidence_model.provenance,
        evidence_refs=(evidence_model.hash,),
        semantic_tags=tuple(semantic_tags),
    )


def build_compositional_memory_packet(
    entries: Sequence[CompositionalMemoryEntry | Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a deterministic MemEIC-inspired external-memory packet.

    Pairing is explicit and replayable: textual and visual entries are linked
    only when they share at least one evidence reference or semantic tag.
    No embedding search, model mutation, truth assignment, or autonomous write
    is performed.
    """

    models = [
        item if isinstance(item, CompositionalMemoryEntry) else CompositionalMemoryEntry.model_validate(item)
        for item in entries
    ]
    models = sorted(models, key=lambda item: item.memory_id)

    textual = [item for item in models if item.modality in {"textual", "mixed"}]
    visual = [item for item in models if item.modality in {"visual", "mixed"}]

    connectors: list[KnowledgeConnectorLink] = []
    for text_entry in textual:
        for visual_entry in visual:
            if text_entry.memory_id == visual_entry.memory_id:
                continue
            shared_evidence = tuple(sorted(set(text_entry.evidence_refs) & set(visual_entry.evidence_refs)))
            shared_tags = tuple(sorted(set(text_entry.semantic_tags) & set(visual_entry.semantic_tags)))
            if not shared_evidence and not shared_tags:
                continue
            digest_input = "|".join(
                (
                    text_entry.memory_id,
                    visual_entry.memory_id,
                    ",".join(shared_evidence),
                    ",".join(shared_tags),
                )
            )
            connectors.append(
                KnowledgeConnectorLink(
                    textual_memory_ref=text_entry.memory_id,
                    visual_memory_ref=visual_entry.memory_id,
                    shared_evidence_refs=shared_evidence,
                    shared_semantic_tags=shared_tags,
                    connector_hash=sha256(digest_input.encode("utf-8")).hexdigest(),
                )
            )

    connectors = sorted(
        connectors,
        key=lambda link: (link.textual_memory_ref, link.visual_memory_ref, link.connector_hash),
    )

    return {
        "schema_version": "CompositionalMemoryPacket.v1",
        "status": "COMPOSITIONAL_EVIDENCE_MEMORY_EMITTED_ADVISORY_ONLY",
        "entry_count": len(models),
        "textual_memory": [item.model_dump(mode="json") for item in textual],
        "visual_memory": [item.model_dump(mode="json") for item in visual],
        "knowledge_connectors": [item.model_dump(mode="json") for item in connectors],
        "connector_count": len(connectors),
        "retrieval_policy": "EXPLICIT_SHARED_EVIDENCE_OR_TAGS",
        "model_mutation": False,
        "parameter_editing": False,
        "truth_assignment": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "advisory_only": True,
    }
