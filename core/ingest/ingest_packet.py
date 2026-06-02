from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from core.belief_graph.belief_graph_builder import build_belief_graph_packet
from core.belief_graph.belief_graph_packet import BeliefGraphPacket
from core.belief_graph.claim_object import ClaimObject
from core.belief_graph.evidence_object import EvidenceObject
from core.belief_graph.signal_graph import SignalGraphRelationship
from core.belief_graph.theory_object import TheoryObject
from core.ingest.source_record import SourceRecord

PATCH_ID = "GLOBAL_INGEST_ADAPTER_SPINE_001"
FINAL_STATUS = "GLOBAL_INGEST_SPINE_ADVISORY_ONLY"


class IngestPacket(BaseModel):
    schema_version: Literal["IngestPacket.v1"] = "IngestPacket.v1"
    patch_id: Literal["GLOBAL_INGEST_ADAPTER_SPINE_001"] = PATCH_ID
    adapter_id: str = Field(min_length=1)
    source_record: SourceRecord
    claims: tuple[ClaimObject, ...] = Field(default_factory=tuple)
    evidence: tuple[EvidenceObject, ...] = Field(default_factory=tuple)
    theories: tuple[TheoryObject, ...] = Field(default_factory=tuple)
    relationships: tuple[SignalGraphRelationship, ...] = Field(default_factory=tuple)
    provenance: dict[str, Any] = Field(default_factory=dict)
    confidence_behavior: Literal["PRESERVE_INPUT"] = "PRESERVE_INPUT"
    not_computable_behavior: Literal["PRESERVE"] = "PRESERVE"
    FORECAST_ROUTING: Literal[False] = False
    CANON_MUTATION: Literal[False] = False
    RUNTIME_MUTATION: Literal[False] = False
    EXECUTION_AUTHORITY: Literal[False] = False
    TRUTH_ASSIGNMENT: Literal[False] = False
    FINAL_STATUS: Literal["GLOBAL_INGEST_SPINE_ADVISORY_ONLY"] = FINAL_STATUS

    model_config = {"frozen": True}

    def to_belief_graph_packet(self) -> BeliefGraphPacket:
        packet_provenance = {
            **self.provenance,
            "patch_id": self.patch_id,
            "final_status": self.FINAL_STATUS,
            "adapter_id": self.adapter_id,
            "source_record": self.source_record.model_dump(mode="json"),
        }
        return build_belief_graph_packet(
            claims=self.claims,
            evidence=self.evidence,
            theories=self.theories,
            relationships=self.relationships,
            provenance=packet_provenance,
        )
