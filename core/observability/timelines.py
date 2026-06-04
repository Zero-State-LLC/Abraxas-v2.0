from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class RuntimeTimelineEvent(BaseModel):
    sequence: int
    event_type: str
    source_hash: str
    status: str


class RuntimeTimelinePacket(BaseModel):
    schema_version: Literal["RuntimeTimelinePacket.v1"] = "RuntimeTimelinePacket.v1"
    timeline_id: str
    execution_hash: str
    events: list[RuntimeTimelineEvent]
    timeline_hash: str
    authority: Authority
    status: Literal["valid", "failed"]


def build_runtime_timeline_packet(runtime_run: dict) -> RuntimeTimelinePacket:
    seq = runtime_run.get("scheduler", {}).get("execution_sequence", [])
    events = [RuntimeTimelineEvent(sequence=i, event_type="node_executed", source_hash=canonical_hash({"node": n, "i": i}), status="completed") for i, n in enumerate(seq)]
    events = sorted(events, key=lambda e: e.sequence)
    t_hash = canonical_hash([e.model_dump(mode="json") for e in events])
    tid = canonical_hash({"execution": runtime_run.get("run_id", ""), "timeline": t_hash})
    return RuntimeTimelinePacket(timeline_id=tid, execution_hash=runtime_run.get("run_id", ""), events=events, timeline_hash=t_hash, authority=Authority(), status="valid")
