from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator


class ReviewContinuityLineagePacket(BaseModel):
    schema_version: Literal["ReviewContinuityLineagePacket.v1"] = "ReviewContinuityLineagePacket.v1"
    lineage_id: str
    continuity_hash: str
    parent_hashes: list[str]
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(continuity_hash: str, parent_hashes: list[str], lineage_cycle_detected: bool) -> str:
        return hashlib.sha256(f"{continuity_hash}|{'|'.join(parent_hashes)}|{lineage_cycle_detected}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        cycle = self.continuity_hash in self.parent_hashes
        if cycle:
            raise ValueError("cyclic lineage invalid")
        if self.lineage_cycle_detected != cycle:
            raise ValueError("lineage cycle mismatch")
        if self.deterministic_lineage_hash != self.compute_hash(self.continuity_hash, self.parent_hashes, self.lineage_cycle_detected):
            raise ValueError("lineage hash mismatch")
        return self
