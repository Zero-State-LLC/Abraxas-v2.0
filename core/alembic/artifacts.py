"""Alembic receipt and replay artifact builders."""

from __future__ import annotations

from typing import Any

from core.alembic.config import RouterPolicy, policy_hash
from core.alembic.models import (
    AlembicRunReceipt,
    ArchitectureContribution,
    FusionResult,
    Provenance,
    RoutingDecision,
    TaskEnvelope,
    VerificationResult,
)
from core.alembic.util import det_timestamp, hash_model, make_id, to_canonical_dict
from core.canonical.json import canonical_hash


def build_run_receipt(
    *,
    task: TaskEnvelope,
    decision: RoutingDecision,
    verification: VerificationResult | None,
    fusion: FusionResult | None,
    configuration_hash: str,
) -> AlembicRunReceipt:
    status = "ABSTAIN" if decision.abstention_reason else "ADVISORY_COMPLETE"
    if verification is not None and verification.status == "FAIL":
        status = "VERIFICATION_FAIL"
    if fusion is not None:
        status = f"FUSION_{fusion.status}"
    parent_ids = [decision.decision_id]
    if verification is not None:
        parent_ids.append(verification.verification_id)
    if fusion is not None:
        parent_ids.append(fusion.fusion_id)
    receipt = AlembicRunReceipt(
        artifact_id=make_id("receipt", task.run_id, task.task_id, status),
        run_id=task.run_id,
        task_id=task.task_id,
        parent_artifact_ids=tuple(parent_ids),
        timestamp=det_timestamp(f"{task.run_id}:{task.task_id}:{status}"),
        content_hash="",
        configuration_hash=configuration_hash,
        policy_refs=decision.policy_refs,
        provenance=Provenance(classification="OBSERVED", producer="core.alembic"),
        status=status,
        decision_id=decision.decision_id,
        fusion_id=fusion.fusion_id if fusion is not None else None,
        verification_id=verification.verification_id if verification is not None else None,
        abstention_reason=decision.abstention_reason,
        replay_manifest_ref=f"replay:{task.run_id}",
        lane=task.lane,
    )
    digest = hash_model(receipt.model_copy(update={"content_hash": ""}))
    return receipt.model_copy(
        update={
            "content_hash": digest,
            "provenance": receipt.provenance.model_copy(update={"content_hash": digest}),
        }
    )


def build_replay_manifest(
    *,
    task: TaskEnvelope,
    decision: RoutingDecision,
    contributions: tuple[ArchitectureContribution, ...],
    verification: VerificationResult | None,
    fusion: FusionResult | None,
    policy: RouterPolicy,
) -> dict[str, Any]:
    nondeterministic = [
        item.architecture_id
        for item in contributions
        if item.is_stub or item.status in {"UNAVAILABLE", "NOT_IMPLEMENTED"}
    ]
    payload = {
        "schema_version": "AlembicReplayManifest.v1",
        "manifest_id": make_id("replay", task.run_id, decision.decision_id),
        "run_id": task.run_id,
        "task": to_canonical_dict(task),
        "policy_hash": policy_hash(policy),
        "decision_id": decision.decision_id,
        "contribution_ids": [item.contribution_id for item in contributions],
        "verification_id": verification.verification_id if verification else None,
        "fusion_id": fusion.fusion_id if fusion else None,
        "replayable": len(nondeterministic) == 0 or decision.abstention_reason is not None,
        "irreproducible_dependencies": nondeterministic,
        "replay_notes": (
            "Deterministic replay supported for local advisory adapters; "
            "stub/unavailable adapters are typed irreproducible dependencies."
            if nondeterministic
            else "Deterministic replay supported for this advisory run."
        ),
        "FINAL_STATUS": "ALEMBIC_SPINE_ADVISORY_ONLY",
    }
    payload["content_hash"] = canonical_hash(payload)
    return payload
