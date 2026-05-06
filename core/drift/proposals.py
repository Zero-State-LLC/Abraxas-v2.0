from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class WeightDriftProposalPacket(BaseModel):
    schema_version: Literal["WeightDriftProposalPacket.v1"] = "WeightDriftProposalPacket.v1"
    proposal_id: str
    source_reliability_hash: str
    source_brier_hash: str
    proposed_weight_delta: float
    bounded_weight: float
    deterministic_proposal_hash: str
    authority: Authority = Authority()
    proposal_status: Literal["pending", "simulated", "stabilized", "rejected", "archived", "not_computable"] = "simulated"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(source_reliability_hash: str, source_brier_hash: str, proposed_weight_delta: float, bounded_weight: float) -> str:
        return hashlib.sha256(f"{source_reliability_hash}|{source_brier_hash}|{proposed_weight_delta:.6f}|{bounded_weight:.6f}".encode()).hexdigest()

    @model_validator(mode='after')
    def _validate(self) -> "WeightDriftProposalPacket":
        self.authority.assert_locked()
        if not 0 <= self.bounded_weight <= 1:
            raise ValueError("bounded_weight range [0,1]")
        if self.deterministic_proposal_hash != self.compute_hash(self.source_reliability_hash, self.source_brier_hash, self.proposed_weight_delta, self.bounded_weight):
            raise ValueError("simulated only deterministic hash")
        return self
