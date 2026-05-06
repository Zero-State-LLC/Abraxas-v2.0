from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel

from core.governance.authority import Authority
from core.spine.milestone_registry import MilestoneRegistryPacket


class MilestoneValidationPacket(BaseModel):
    schema_version: Literal["MilestoneValidationPacket.v1"] = "MilestoneValidationPacket.v1"
    validation_id: str
    reported_active_milestone: str
    derived_active_milestone: str
    derived_evidence_status: str
    stale_metadata_detected: bool
    registry_status: str
    partial_milestones: list[str]
    missing_milestones: list[str]
    lineage_valid: bool
    authority: Authority = Authority()
    status: Literal["passed", "failed", "not_computable"]


def _lineage_valid(registry: MilestoneRegistryPacket) -> bool:
    by_id = {n.milestone_id: n for n in registry.milestone_lineage}
    if len(by_id) != len(registry.milestone_lineage):
        return False
    for node in registry.milestone_lineage:
        seen: set[str] = set()
        cur = node
        while cur.parent_milestone:
            if cur.milestone_id in seen or cur.parent_milestone not in by_id:
                return False
            seen.add(cur.milestone_id)
            cur = by_id[cur.parent_milestone]
    return True


def validate_active_milestone(reported_active_milestone: str, registry: MilestoneRegistryPacket) -> MilestoneValidationPacket:
    derived = registry.active_milestone
    stale = reported_active_milestone != derived
    lineage_valid = _lineage_valid(registry)
    evidence_status = next((e.evidence_status for e in registry.evidence_packets if e.milestone_id == derived), "not_computable")

    if derived == "unknown" or registry.status == "not_computable":
        status: Literal["passed", "failed", "not_computable"] = "not_computable"
    elif not lineage_valid or stale or registry.status == "partial":
        status = "failed"
    elif derived == "v2.0.9-governed-weight-drift-simulation" and evidence_status in {"artifact_verified", "code_verified"}:
        status = "passed"
    else:
        status = "failed"

    validation_id = hashlib.sha256(f"{reported_active_milestone}|{derived}|{registry.deterministic_registry_hash}|{evidence_status}".encode()).hexdigest()
    packet = MilestoneValidationPacket(
        validation_id=validation_id,
        reported_active_milestone=reported_active_milestone,
        derived_active_milestone=derived,
        derived_evidence_status=evidence_status,
        stale_metadata_detected=stale,
        registry_status=registry.status,
        partial_milestones=registry.partial_milestones,
        missing_milestones=registry.missing_milestones,
        lineage_valid=lineage_valid,
        status=status,
    )
    packet.authority.assert_locked()
    return packet
