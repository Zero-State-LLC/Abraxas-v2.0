from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class OperatorQueueReviewPacket(BaseModel):
    schema_version: Literal["OperatorQueueReviewPacket.v1"] = "OperatorQueueReviewPacket.v1"
    review_id: str
    queue_hash: str
    pending_requests: int
    deferred_requests: int
    denied_requests: int
    review_only_approved_requests: int
    unresolved_diagnostics: int
    deterministic_review_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(queue_hash: str, pending_requests: int, deferred_requests: int, denied_requests: int, review_only_approved_requests: int, unresolved_diagnostics: int) -> str:
        return hashlib.sha256(f"{queue_hash}|{pending_requests}|{deferred_requests}|{denied_requests}|{review_only_approved_requests}|{unresolved_diagnostics}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        if self.deterministic_review_hash != self.compute_hash(self.queue_hash, self.pending_requests, self.deferred_requests, self.denied_requests, self.review_only_approved_requests, self.unresolved_diagnostics):
            raise ValueError("review hash mismatch")
        return self
