from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class SourceEvidencePacket(BaseModel):
    schema_version: Literal["SourceEvidencePacket.v1"] = "SourceEvidencePacket.v1"
    evidence_id: str
    intake_hash: str
    provenance_chain: list[str]
    evidence_type: Literal["structural", "runtime", "replay", "observability", "sandbox", "state", "projection"]
    deterministic_evidence_hash: str
    authority: Authority = Authority()
    status: str = "ok"

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(intake_hash: str, provenance_chain: list[str], evidence_type: str) -> str:
        return hashlib.sha256(f"{intake_hash}|{'|'.join(provenance_chain)}|{evidence_type}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "SourceEvidencePacket":
        self.authority.assert_locked()
        if not self.provenance_chain:
            raise ValueError("missing provenance fail closed")
        if self.deterministic_evidence_hash != self.compute_hash(self.intake_hash, self.provenance_chain, self.evidence_type):
            raise ValueError("provenance deterministic")
        return self
