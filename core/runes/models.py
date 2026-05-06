"""ABX-Rune contract models for ABRAXAS v2.0."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

from core.governance.authority import Authority
from core.governance.doctrine import SCHEMA_VERSION_RUNE


class RuneContract(BaseModel):
    """Typed operation contract for an ABX-Rune."""

    schema_version: Literal["RuneContract.v1"] = SCHEMA_VERSION_RUNE
    rune_id: str
    purpose: str
    input_schema: str
    output_schema: str
    lane: str
    authority: Authority
    required_proofs: list[str] = []

    model_config = {"frozen": True}

    @field_validator("rune_id")
    @classmethod
    def _rune_id_prefix(cls, v: str) -> str:
        if not v.startswith("RUNE."):
            raise ValueError(f"rune_id must start with 'RUNE.', got: {v!r}")
        return v

    @field_validator("input_schema", "output_schema")
    @classmethod
    def _schema_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("input_schema and output_schema are required")
        return v

    @model_validator(mode="after")
    def _authority_locked(self) -> "RuneContract":
        self.authority.assert_locked()
        return self
