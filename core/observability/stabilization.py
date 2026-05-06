from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

from core.canonical.json import canonical_hash
from core.governance.authority import Authority


class StabilizationTelemetry(BaseModel):
    schema_version: Literal["StabilizationTelemetry.v1"] = "StabilizationTelemetry.v1"
    stabilization_id: str
    execution_hash: str
    replay_count: int
    deterministic_replay_matches: int
    replay_failures: int
    route_failures: int
    authority: Authority
    stabilization_state: Literal["not_started", "active", "stable", "unstable", "failed"]

    @model_validator(mode="after")
    def _valid(self) -> "StabilizationTelemetry":
        if self.replay_failures > self.replay_count:
            raise ValueError("replay_failures cannot exceed replay_count")
        return self


def build_stabilization_telemetry(runtime_run: dict, replay_packet: dict | None) -> StabilizationTelemetry:
    replay_count = 1 if replay_packet else 0
    replay_failures = 0 if (replay_packet and replay_packet.get("status") == "passed") or replay_packet is None else 1
    route_failures = len(runtime_run.get("failures", []))
    state: Literal["not_started", "active", "stable", "unstable", "failed"] = "stable" if replay_count and replay_failures == 0 and route_failures == 0 else "unstable"
    body = {"execution_hash": runtime_run.get("run_id", ""), "replay_count": replay_count, "deterministic_replay_matches": replay_count - replay_failures, "replay_failures": replay_failures, "route_failures": route_failures, "stabilization_state": state}
    sid = canonical_hash(body)
    return StabilizationTelemetry(stabilization_id=sid, authority=Authority(), **body)
