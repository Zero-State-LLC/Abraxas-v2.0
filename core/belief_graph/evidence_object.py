from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class EvidenceObject(BaseModel):
    schema_version: Literal["EvidenceObject.v1"] = "EvidenceObject.v1"
    source: str = Field(min_length=1)
    provenance: dict[str, Any]
    timestamp: str = Field(min_length=1)
    evidence_type: str = Field(min_length=1)
    hash: str = Field(min_length=1)

    model_config = {"frozen": True}

    @field_validator("source", "timestamp", "evidence_type", "hash")
    @classmethod
    def _value_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("non-empty value required")
        return value
