from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ForecastOutcomeBindingPacket(BaseModel):
    schema_version: Literal["ForecastOutcomeBindingPacket.v1"] = "ForecastOutcomeBindingPacket.v1"
    binding_id: str
    forecast_hash: str
    expected_outcome_hash: str
    observed_outcome_hash: str | None = None
    binding_status: Literal["unresolved", "matched", "mismatched", "expired"] = "unresolved"
    authority: Authority = Authority()
    status: str = "open"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "ForecastOutcomeBindingPacket":
        self.authority.assert_locked()
        return self
