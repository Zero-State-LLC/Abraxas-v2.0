from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class IntakeNormalizationPacket(BaseModel):
    schema_version: Literal["IntakeNormalizationPacket.v1"] = "IntakeNormalizationPacket.v1"
    normalization_id: str
    source_hash: str
    normalized_hash: str
    normalization_steps: list[str]
    deterministic_normalization_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(source_hash: str, normalized_hash: str, steps: list[str]) -> str:
        return hashlib.sha256(f"{source_hash}|{normalized_hash}|{'|'.join(steps)}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "IntakeNormalizationPacket":
        self.authority.assert_locked()
        if self.deterministic_normalization_hash != self.compute_hash(self.source_hash, self.normalized_hash, self.normalization_steps):
            raise ValueError("normalization deterministic")
        return self
