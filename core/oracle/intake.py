from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class OracleIntakeEnvelope(BaseModel):
    schema_version: Literal["OracleIntakeEnvelope.v1"] = "OracleIntakeEnvelope.v1"
    intake_id: str
    source_id: str
    source_type: Literal["document", "receipt", "replay", "telemetry", "projection", "topology", "sandbox", "state_snapshot"]
    source_hash: str
    raw_payload_hash: str
    normalized_payload_hash: str | None = None
    replay_hash: str | None = None
    authority: Authority = Authority()
    intake_status: Literal["pending", "normalized", "stabilized", "conflict_detected", "approved", "rejected", "not_computable"] = "pending"

    model_config = {"frozen": True}

    @staticmethod
    def hash_payload(payload: str) -> str:
        return hashlib.sha256(payload.encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "OracleIntakeEnvelope":
        self.authority.assert_locked()
        if len(self.source_hash) != 64 or len(self.raw_payload_hash) != 64:
            raise ValueError("deterministic hashes required")
        return self
