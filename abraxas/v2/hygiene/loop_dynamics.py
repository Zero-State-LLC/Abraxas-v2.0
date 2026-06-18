from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class LoopDynamics(BaseModel):
    schema_version: Literal["LoopDynamics.v1"] = "LoopDynamics.v1"
    retrocausal_risk: float = Field(default=0.0, ge=0.0, le=1.0)
    hyperstitional_charge: float = Field(default=0.0, ge=0.0, le=1.0)
    mitigation: str = Field(default="none")
    version: str = Field(default="1.0.0")

    model_config = {"frozen": True}

    @field_validator("mitigation")
    @classmethod
    def _mitigation_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("mitigation required")
        return value.strip()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
