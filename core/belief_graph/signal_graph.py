from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, Field, model_validator

NodeType: TypeAlias = Literal["claim", "evidence", "theory"]
_ALLOWED_RELATIONSHIPS = {
    frozenset({"claim"}),
    frozenset({"claim", "evidence"}),
    frozenset({"claim", "theory"}),
    frozenset({"evidence", "theory"}),
}


class SignalGraphRelationship(BaseModel):
    source_ref: str = Field(min_length=1)
    source_type: NodeType
    target_ref: str = Field(min_length=1)
    target_type: NodeType
    relationship: str = Field(min_length=1)

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate_pair(self) -> "SignalGraphRelationship":
        pair = frozenset({self.source_type, self.target_type})
        if pair not in _ALLOWED_RELATIONSHIPS:
            raise ValueError("signal graph only stores claim/evidence/theory relationships")
        return self


class SignalGraph(BaseModel):
    schema_version: Literal["SignalGraph.v1"] = "SignalGraph.v1"
    relationship_count: int = Field(ge=0)
    relationships: tuple[SignalGraphRelationship, ...] = Field(default_factory=tuple)

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate_relationships(self) -> "SignalGraph":
        if self.relationship_count != len(self.relationships):
            raise ValueError("relationship_count mismatch")
        seen: set[tuple[str, str, str, str, str]] = set()
        for relationship in self.relationships:
            key = (
                relationship.source_ref,
                relationship.source_type,
                relationship.target_ref,
                relationship.target_type,
                relationship.relationship,
            )
            if key in seen:
                raise ValueError("duplicate signal graph relationship")
            seen.add(key)
        return self
