from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

FORBIDDEN_CATEGORIES = {"deployment", "execution", "activation", "production_routing"}


class ProposalCategoryPacket(BaseModel):
    schema_version: Literal["ProposalCategoryPacket.v1"] = "ProposalCategoryPacket.v1"
    proposal_hash: str
    category: str
    deterministic_category_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, category: str) -> str:
        return hashlib.sha256(f"{proposal_hash}|{category}".encode()).hexdigest()

    @model_validator(mode="after")
    def validate_packet(self) -> "ProposalCategoryPacket":
        if self.category in FORBIDDEN_CATEGORIES:
            raise ValueError("forbidden category")
        if self.deterministic_category_hash != self.compute_hash(self.proposal_hash, self.category):
            raise ValueError("category hash mismatch")
        return self
