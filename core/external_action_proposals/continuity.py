from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field


class ExternalActionProposalContinuityPacket(BaseModel):
    schema_version: Literal["ExternalActionProposalContinuityPacket.v1"] = "ExternalActionProposalContinuityPacket.v1"
    proposal_hash: str
    unresolved_dependencies: list[str] = Field(default_factory=list)
    continuity_safe: bool
    deterministic_continuity_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, unresolved_dependencies: list[str], continuity_safe: bool) -> str:
        return hashlib.sha256(f"{proposal_hash}|{'/'.join(sorted(unresolved_dependencies))}|{continuity_safe}".encode()).hexdigest()
