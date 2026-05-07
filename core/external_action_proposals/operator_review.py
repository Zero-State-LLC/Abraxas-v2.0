from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel


class ExternalActionProposalOperatorReviewPacket(BaseModel):
    schema_version: Literal["ExternalActionProposalOperatorReviewPacket.v1"] = "ExternalActionProposalOperatorReviewPacket.v1"
    proposal_hash: str
    projection_only: bool
    inference_authority: bool
    deterministic_review_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, projection_only: bool, inference_authority: bool) -> str:
        return hashlib.sha256(f"{proposal_hash}|{projection_only}|{inference_authority}".encode()).hexdigest()
