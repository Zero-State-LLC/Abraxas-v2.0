from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from abraxas.v2.hygiene.loop_dynamics import LoopDynamics


class RegisterTier(str, Enum):
    OBSERVED = "observed"
    INFERRED = "inferred"
    SPECULATIVE = "speculative"


class V2Output(BaseModel):
    schema_version: Literal["V2Output.v1"] = "V2Output.v1"
    observed: dict[str, Any] = Field(default_factory=dict)
    inferred: dict[str, Any] = Field(default_factory=dict)
    speculative: dict[str, Any] = Field(default_factory=dict)
    loop_dynamics: LoopDynamics | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="1.0.0")

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate_registers(self) -> "V2Output":
        if not any((self.observed, self.inferred, self.speculative)):
            raise ValueError("at least one register tier must be populated")
        return self

    def is_valid(self) -> bool:
        try:
            self.model_validate(self.model_dump())
            return True
        except ValueError:
            return False

    def tier(self, register: RegisterTier) -> dict[str, Any]:
        return getattr(self, register.value)
