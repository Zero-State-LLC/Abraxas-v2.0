from __future__ import annotations

from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, Field, field_validator

SourcePayload: TypeAlias = dict[str, Any] | list[Any] | str | None


class SourceRecord(BaseModel):
    schema_version: Literal["SourceRecord.v1"] = "SourceRecord.v1"
    adapter_id: str = Field(min_length=1)
    source_uri: str = Field(min_length=1)
    source_type: Literal["filesystem", "json", "audit_artifact"]
    observed_at: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    size_bytes: int = Field(ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    payload: SourcePayload = None
    local_only: Literal[True] = True
    advisory_only: Literal[True] = True

    model_config = {"frozen": True}

    @field_validator("adapter_id", "source_uri", "observed_at", "content_type")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("non-empty value required")
        return value
