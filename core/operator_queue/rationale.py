from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OperatorRationalePacket(BaseModel):
    schema_version: Literal["OperatorRationalePacket.v1"] = "OperatorRationalePacket.v1"
    rationale_id: str
    decision_hash: str
    rationale_summary: str
    cited_diagnostics: list[str]
    cited_containment_restrictions: list[str]
    cited_governance_events: list[str]
    deterministic_rationale_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, rationale_summary: str, cited_diagnostics: list[str], cited_containment_restrictions: list[str], cited_governance_events: list[str]) -> str:
        return hashlib.sha256(f"{decision_hash}|{rationale_summary}|{'|'.join(cited_diagnostics)}|{'|'.join(cited_containment_restrictions)}|{'|'.join(cited_governance_events)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_rationale_hash != self.compute_hash(self.decision_hash, self.rationale_summary, self.cited_diagnostics, self.cited_containment_restrictions, self.cited_governance_events):
            raise ValueError("rationale hash mismatch")
        return self
