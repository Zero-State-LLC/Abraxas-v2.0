from __future__ import annotations
import hashlib
from typing import Literal
from pydantic import BaseModel, model_validator


class OperatorQueueLineagePacket(BaseModel):
    schema_version: Literal["OperatorQueueLineagePacket.v1"] = "OperatorQueueLineagePacket.v1"
    lineage_id: str
    queue_hash: str
    parent_hashes: list[str]
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(queue_hash: str, parent_hashes: list[str], lineage_cycle_detected: bool) -> str:
        return hashlib.sha256(f"{queue_hash}|{'|'.join(parent_hashes)}|{lineage_cycle_detected}".encode()).hexdigest()

    @model_validator(mode="after")
    def _v(self):
        if self.queue_hash in self.parent_hashes:
            raise ValueError("cyclic lineage invalid")
        if self.lineage_cycle_detected != (self.queue_hash in self.parent_hashes):
            # fail-closed: explicit cycle truth required
            if self.lineage_cycle_detected:
                raise ValueError("lineage cycle mismatch")
        if self.deterministic_lineage_hash != self.compute_hash(self.queue_hash, self.parent_hashes, self.lineage_cycle_detected):
            raise ValueError("lineage hash mismatch")
        return self
