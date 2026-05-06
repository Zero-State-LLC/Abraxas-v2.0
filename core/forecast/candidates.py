from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class ForecastCandidatePacket(BaseModel):
    schema_version: Literal["ForecastCandidatePacket.v1"] = "ForecastCandidatePacket.v1"
    forecast_id: str
    source_intake_hash: str
    sandbox_branch_hash: str
    candidate_type: Literal["structural", "replay", "stabilization", "sandbox", "topology", "observability"]
    candidate_hash: str
    deterministic_candidate_hash: str
    authority: Authority = Authority()
    forecast_status: Literal["pending", "candidate", "calibrated", "stabilized", "rejected", "archived", "not_computable"] = "candidate"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(source_intake_hash: str, sandbox_branch_hash: str, candidate_type: str, candidate_hash: str) -> str:
        return hashlib.sha256(f"{source_intake_hash}|{sandbox_branch_hash}|{candidate_type}|{candidate_hash}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ForecastCandidatePacket":
        self.authority.assert_locked()
        if self.deterministic_candidate_hash != self.compute_hash(self.source_intake_hash, self.sandbox_branch_hash, self.candidate_type, self.candidate_hash):
            raise ValueError("candidate-only deterministic hash required")
        return self
