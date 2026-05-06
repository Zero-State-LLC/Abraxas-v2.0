from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class ProjectionStateSnapshot(BaseModel):
    schema_version: Literal["ProjectionStateSnapshot.v1"] = "ProjectionStateSnapshot.v1"
    snapshot_id: str
    projection_hash: str
    queue_hash: str
    validation_hash: str
    telemetry_hash: str
    topology_hash: str
    authority: Authority
    projection_only: bool
    inference_authority: bool
    status: Literal["valid", "failed"]


def build_projection_state_snapshot(projection: dict, queue: dict, validation: dict, telemetry: dict, runtime_run: dict) -> ProjectionStateSnapshot:
    body = {
        "projection_hash": canonical_hash(projection),
        "queue_hash": canonical_hash(queue),
        "validation_hash": canonical_hash(validation),
        "telemetry_hash": canonical_hash(telemetry),
        "topology_hash": runtime_run.get("graph", {}).get("topology_hash", ""),
        "projection_only": True,
        "inference_authority": False,
        "status": "valid",
    }
    sid = canonical_hash(body)
    return ProjectionStateSnapshot(snapshot_id=sid, authority=Authority(), **body)
