from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator
from core.governance.authority import Authority


class ReviewContinuityChainPacket(BaseModel):
    schema_version: Literal["ReviewContinuityChainPacket.v1"] = "ReviewContinuityChainPacket.v1"
    chain_id: str
    originating_request_hash: str
    linked_review_hashes: list[str]
    linked_rationale_hashes: list[str]
    linked_governance_hashes: list[str]
    linked_firewall_hashes: list[str]
    chain_status: str
    deterministic_chain_hash: str
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(originating_request_hash: str, linked_review_hashes: list[str], linked_rationale_hashes: list[str], linked_governance_hashes: list[str], linked_firewall_hashes: list[str], chain_status: str) -> str:
        return hashlib.sha256(f"{originating_request_hash}|{'|'.join(linked_review_hashes)}|{'|'.join(linked_rationale_hashes)}|{'|'.join(linked_governance_hashes)}|{'|'.join(linked_firewall_hashes)}|{chain_status}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        self.authority.assert_locked()
        allowed = {"pending_continuity", "deferred_continuity", "denied_continuity", "review_only_continuity"}
        forbidden = {"executing", "activated", "deployed", "production_live"}
        if self.chain_status in forbidden or self.chain_status not in allowed:
            raise ValueError("forbidden_status_detected")
        if self.deterministic_chain_hash != self.compute_hash(self.originating_request_hash, self.linked_review_hashes, self.linked_rationale_hashes, self.linked_governance_hashes, self.linked_firewall_hashes, self.chain_status):
            raise ValueError("chain hash mismatch")
        return self
