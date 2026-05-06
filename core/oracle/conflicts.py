from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class IntakeConflictPacket(BaseModel):
    schema_version: Literal["IntakeConflictPacket.v1"] = "IntakeConflictPacket.v1"
    conflict_id: str
    conflicting_hashes: list[str]
    conflict_type: Literal["provenance_mismatch", "normalization_mismatch", "replay_mismatch", "lineage_break", "duplicate_source", "authority_violation"]
    severity: Literal["low", "medium", "high", "severe"]
    authority: Authority = Authority()
    resolution_required: bool = True
    status: str = "open"

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _validate(self) -> "IntakeConflictPacket":
        self.authority.assert_locked()
        if self.severity == "severe" and not self.resolution_required:
            raise ValueError("unresolved severe conflicts block approval")
        return self
