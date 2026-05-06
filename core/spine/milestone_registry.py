from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, model_validator

from core.governance.authority import Authority


class MilestoneLineageNode(BaseModel):
    milestone_id: str
    parent_milestone: str | None = None
    stabilization_hash: str
    generation: int


class MilestoneRegistryPacket(BaseModel):
    schema_version: Literal["MilestoneRegistryPacket.v1"] = "MilestoneRegistryPacket.v1"
    active_milestone: str
    stabilized_milestones: list[str]
    latest_stable_hash: str
    milestone_lineage: list[MilestoneLineageNode]
    deterministic_registry_hash: str
    authority: Authority = Authority()
    status: str

    model_config = {"frozen": True}

    @staticmethod
    def compute_hash(active_milestone: str, stabilized_milestones: list[str], latest_stable_hash: str, lineage: list[MilestoneLineageNode]) -> str:
        lineage_blob = "|".join(f"{n.milestone_id}:{n.parent_milestone}:{n.stabilization_hash}:{n.generation}" for n in lineage)
        return hashlib.sha256(f"{active_milestone}|{'|'.join(stabilized_milestones)}|{latest_stable_hash}|{lineage_blob}".encode()).hexdigest()

    @model_validator(mode="after")
    def _validate(self) -> "MilestoneRegistryPacket":
        self.authority.assert_locked()
        if self.stabilized_milestones != sorted(self.stabilized_milestones):
            raise ValueError("deterministic ordering")
        seen: set[str] = set()
        for n in self.milestone_lineage:
            if n.milestone_id in seen:
                raise ValueError("cyclic lineage fail closed")
            seen.add(n.milestone_id)
        if self.active_milestone != self.stabilized_milestones[-1]:
            raise ValueError("stale milestone mismatch fail closed")
        if self.deterministic_registry_hash != self.compute_hash(self.active_milestone, self.stabilized_milestones, self.latest_stable_hash, self.milestone_lineage):
            raise ValueError("replay-safe deterministic registry hash mismatch")
        return self


def derive_registry_from_artifacts() -> MilestoneRegistryPacket:
    candidates: list[tuple[str, str]] = [
        ("v2.0.5-governed-adaptive-sandbox", "out/sandbox/latest.json"),
        ("v2.0.6-governed-oracle-intake", "out/oracle/latest.json"),
        ("v2.0.7-governed-forecast-candidate-layer", "out/forecast/latest.json"),
        ("v2.0.8-governed-brier-ledger-layer", "out/brier/latest.json"),
        ("v2.0.9-governed-weight-drift-simulation", "out/drift/latest.json"),
    ]
    stabilized = [m for m, p in candidates if Path(p).exists()]
    if not stabilized:
        stabilized = ["v2.0.4-governed-state-engine"]
        latest_hash = "missing-artifacts"
        lineage = [MilestoneLineageNode(milestone_id=stabilized[0], stabilization_hash=latest_hash, generation=0)]
        active = stabilized[-1]
        det = MilestoneRegistryPacket.compute_hash(active, stabilized, latest_hash, lineage)
        return MilestoneRegistryPacket(active_milestone=active, stabilized_milestones=stabilized, latest_stable_hash=latest_hash, milestone_lineage=lineage, deterministic_registry_hash=det, status="not_computable")

    latest_path = next(p for m, p in reversed(candidates) if m == stabilized[-1])
    latest_hash = hashlib.sha256(Path(latest_path).read_bytes()).hexdigest()
    lineage: list[MilestoneLineageNode] = []
    parent = None
    for idx, milestone in enumerate(stabilized):
        mpath = next(p for m, p in candidates if m == milestone)
        shash = hashlib.sha256(Path(mpath).read_bytes()).hexdigest()
        lineage.append(MilestoneLineageNode(milestone_id=milestone, parent_milestone=parent, stabilization_hash=shash, generation=idx))
        parent = milestone
    stabilized_sorted = sorted(stabilized)
    active = stabilized_sorted[-1]
    det = MilestoneRegistryPacket.compute_hash(active, stabilized_sorted, latest_hash, lineage)
    return MilestoneRegistryPacket(active_milestone=active, stabilized_milestones=stabilized_sorted, latest_stable_hash=latest_hash, milestone_lineage=lineage, deterministic_registry_hash=det, status="ok")
