from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, Field

class ProposalSandboxRationalePacket(BaseModel):
    schema_version: Literal["ProposalSandboxRationalePacket.v1"] = "ProposalSandboxRationalePacket.v1"
    evaluation_hash: str
    rationale: str
    cited_diagnostics: list[str] = Field(default_factory=list)
    deterministic_rationale_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(evaluation_hash: str, rationale: str, cited_diagnostics: list[str]) -> str:
        return hashlib.sha256(f"{evaluation_hash}|{rationale}|{'/'.join(sorted(cited_diagnostics))}".encode()).hexdigest()
