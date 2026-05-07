from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class HumanDecisionRationalePacket(BaseModel):
    schema_version: Literal["HumanDecisionRationalePacket.v1"] = "HumanDecisionRationalePacket.v1"
    decision_hash: str
    rationale_summary: str
    cited_review_notes: list[str] = Field(default_factory=list)
    deterministic_rationale_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(decision_hash: str, rationale_summary: str, cited_review_notes: list[str]) -> str:
        return hashlib.sha256(f"{decision_hash}|{rationale_summary}|{'/'.join(sorted(cited_review_notes))}".encode()).hexdigest()
