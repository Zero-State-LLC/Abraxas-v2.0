from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.governance.authority import Authority


class OperatorOverlayGovernanceReviewPacket(BaseModel):
    schema_version: Literal["OperatorOverlayGovernanceReviewPacket.v1"] = "OperatorOverlayGovernanceReviewPacket.v1"
    review_id: str
    ledger_hash: str
    continuity_score: float = Field(ge=0.0, le=1.0)
    critical_diagnostics: int = Field(ge=0)
    missing_event_types: list[str]
    pending_actions: list[str]
    authority: Authority = Authority()
    status: Literal["approved", "pending", "blocked"]

    @model_validator(mode="after")
    def _validate(self) -> "OperatorOverlayGovernanceReviewPacket":
        self.authority.assert_locked()
        self.authority
        return self
