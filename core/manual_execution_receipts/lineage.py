from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator


class ManualExecutionReceiptLineagePacket(BaseModel):
    schema_version: Literal["ManualExecutionReceiptLineagePacket.v1"] = "ManualExecutionReceiptLineagePacket.v1"
    lineage_id: str
    continuity_hash: str
    parent_hashes: list[str]
    lineage_cycle_detected: bool
    deterministic_lineage_hash: str
    status: Literal["passed", "failed", "not_computable"]

    @staticmethod
    def compute_hash(continuity_hash: str, parent_hashes: list[str], cycle: bool) -> str:
        return hashlib.sha256(f"{continuity_hash}|{'|'.join(sorted(parent_hashes))}|{int(cycle)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "ManualExecutionReceiptLineagePacket":
        if self.deterministic_lineage_hash != self.compute_hash(self.continuity_hash, self.parent_hashes, self.lineage_cycle_detected):
            raise ValueError("lineage hash")
        return self
