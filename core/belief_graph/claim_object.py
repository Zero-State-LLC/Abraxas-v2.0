from __future__ import annotations

from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, Field, field_validator, model_validator

ClaimStatus: TypeAlias = Literal[
    "OBSERVED",
    "INFERRED",
    "SPECULATIVE",
    "NOT_COMPUTABLE",
]
ClaimConfidence: TypeAlias = float | Literal["NOT_COMPUTABLE"]


def _normalize_refs(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple, set, frozenset)):
        raise TypeError("reference collection required")
    refs = {str(item).strip() for item in value}
    refs.discard("")
    return tuple(sorted(refs))


class ClaimObject(BaseModel):
    schema_version: Literal["ClaimObject.v1"] = "ClaimObject.v1"
    id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    provenance: dict[str, Any]
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple)
    confidence: ClaimConfidence
    status: ClaimStatus

    model_config = {"frozen": True}

    @field_validator("statement")
    @classmethod
    def _statement_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("statement required")
        return value

    @field_validator("evidence_refs", mode="before")
    @classmethod
    def _normalize_evidence_refs(cls, value: object) -> tuple[str, ...]:
        return _normalize_refs(value)

    @model_validator(mode="after")
    def _validate_confidence(self) -> "ClaimObject":
        if self.status == "NOT_COMPUTABLE" and self.confidence != "NOT_COMPUTABLE":
            raise ValueError("not computable claims must preserve NOT_COMPUTABLE confidence")
        if self.status != "NOT_COMPUTABLE" and self.confidence == "NOT_COMPUTABLE":
            raise ValueError("NOT_COMPUTABLE confidence requires NOT_COMPUTABLE status")
        if isinstance(self.confidence, float) and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        return self
