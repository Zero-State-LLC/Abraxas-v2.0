from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


def _normalize_refs(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple, set, frozenset)):
        raise TypeError("reference collection required")
    refs = {str(item).strip() for item in value}
    refs.discard("")
    return tuple(sorted(refs))


class TheoryObject(BaseModel):
    schema_version: Literal["TheoryObject.v1"] = "TheoryObject.v1"
    id: str = Field(min_length=1)
    supporting_claims: tuple[str, ...] = Field(default_factory=tuple)
    conflicting_claims: tuple[str, ...] = Field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple)

    model_config = {"frozen": True}

    @field_validator("supporting_claims", "conflicting_claims", "evidence_refs", mode="before")
    @classmethod
    def _normalize_reference_fields(cls, value: object) -> tuple[str, ...]:
        return _normalize_refs(value)

    @model_validator(mode="after")
    def _validate_claim_overlap(self) -> "TheoryObject":
        overlap = set(self.supporting_claims) & set(self.conflicting_claims)
        if overlap:
            raise ValueError("theory claims cannot be both supporting and conflicting")
        return self
