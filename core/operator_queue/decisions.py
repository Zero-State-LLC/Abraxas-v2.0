from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority

ALLOWED_DECISIONS = {"deny", "defer", "review_only_approval"}
FORBIDDEN_DECISIONS = {"execute", "activate", "deploy", "promote_live"}


class OperatorDecisionPacket(BaseModel):
    schema_version: Literal["OperatorDecisionPacket.v1"] = "OperatorDecisionPacket.v1"
    decision_id: str
    request_hash: str
    operator_id_hash: str
    decision: str
    decision_reason: str
    requires_additional_review: bool
    deterministic_decision_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def hash_operator_id(operator_id: str) -> str:
        return hashlib.sha256(operator_id.encode()).hexdigest()

    @staticmethod
    def compute_hash(request_hash: str, operator_id_hash: str, decision: str, decision_reason: str, requires_additional_review: bool) -> str:
        return hashlib.sha256(f"{request_hash}|{operator_id_hash}|{decision}|{decision_reason}|{requires_additional_review}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.decision in FORBIDDEN_DECISIONS or self.decision not in ALLOWED_DECISIONS:
            raise ValueError("invalid decision")
        if self.deterministic_decision_hash != self.compute_hash(self.request_hash, self.operator_id_hash, self.decision, self.decision_reason, self.requires_additional_review):
            raise ValueError("decision hash mismatch")
        return self
