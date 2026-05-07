from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

FORBIDDEN_EVAL_STATUS = {"executed", "approved", "deployed", "production_ready"}

class ProposalSandboxEvaluationPacket(BaseModel):
    schema_version: Literal["ProposalSandboxEvaluationPacket.v1"] = "ProposalSandboxEvaluationPacket.v1"
    evaluation_id: str
    route_hash: str
    evaluation_status: str
    deterministic_evaluation_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(route_hash: str, evaluation_status: str) -> str:
        return hashlib.sha256(f"{route_hash}|{evaluation_status}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self) -> "ProposalSandboxEvaluationPacket":
        self.authority.assert_locked()
        if self.evaluation_status in FORBIDDEN_EVAL_STATUS:
            raise ValueError("forbidden evaluation status")
        if self.deterministic_evaluation_hash != self.compute_hash(self.route_hash, self.evaluation_status):
            raise ValueError("evaluation hash mismatch")
        return self
