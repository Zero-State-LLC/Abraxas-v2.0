from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field


class ExternalActionProposalLineagePacket(BaseModel):
    schema_version: Literal["ExternalActionProposalLineagePacket.v1"] = "ExternalActionProposalLineagePacket.v1"
    proposal_hash: str
    parent_hashes: list[str] = Field(default_factory=list)
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(proposal_hash: str, parent_hashes: list[str], lineage_cycle_detected: bool) -> str:
        return hashlib.sha256(f"{proposal_hash}|{'/'.join(sorted(parent_hashes))}|{lineage_cycle_detected}".encode()).hexdigest()
