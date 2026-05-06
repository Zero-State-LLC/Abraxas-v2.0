from __future__ import annotations
import hashlib
from pydantic import BaseModel


class OverlayResolutionClosurePacket(BaseModel):
    schema_version: str = "OverlayResolutionClosurePacket.v1"
    closure_id: str
    unresolved_count: int
    critical_unresolved_count: int
    replay_failures: int
    closure_ready: bool
    deterministic_closure_hash: str

    @staticmethod
    def compute_hash(unresolved: int, critical: int, replay_failures: int, closure_ready: bool) -> str:
        return hashlib.sha256(f"{unresolved}|{critical}|{replay_failures}|{int(closure_ready)}".encode()).hexdigest()
