from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ForecastReplayPacket(BaseModel):
    schema_version: Literal["ForecastReplayPacket.v1"] = "ForecastReplayPacket.v1"
    replay_id: str
    forecast_hash: str
    deterministic_match: bool
    replayed_probabilities: list[str]
    mismatched_probabilities: list[str]
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "ForecastReplayPacket":
        self.authority.assert_locked()
        if self.deterministic_match and self.mismatched_probabilities:
            raise ValueError("mismatch invalidates stabilization")
        return self
