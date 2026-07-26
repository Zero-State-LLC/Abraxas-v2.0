"""SHADOW comparison — detect divergence without promotion or policy mutation."""

from __future__ import annotations

from core.alembic.models import (
    ArchitectureContribution,
    Provenance,
    ShadowComparison,
    TaskEnvelope,
)
from core.alembic.util import det_timestamp, hash_model, make_id


def compare_active_and_shadow(
    task: TaskEnvelope,
    active: tuple[ArchitectureContribution, ...],
    shadow: tuple[ArchitectureContribution, ...],
) -> ShadowComparison:
    active_ids = tuple(sorted(item.contribution_id for item in active))
    shadow_ids = tuple(sorted(item.contribution_id for item in shadow))
    divergences = []
    anomalies = []

    active_claims = {
        str(claim.get("statement", "")).strip()
        for item in active
        for claim in item.claims
        if str(claim.get("statement", "")).strip()
    }
    shadow_claims = {
        str(claim.get("statement", "")).strip()
        for item in shadow
        for claim in item.claims
        if str(claim.get("statement", "")).strip()
    }
    only_shadow = sorted(shadow_claims - active_claims)
    only_active = sorted(active_claims - shadow_claims)
    if only_shadow:
        divergences.append({"type": "shadow_only_claims", "values": only_shadow})
        anomalies.append("shadow_claims_absent_from_active")
    if only_active:
        divergences.append({"type": "active_only_claims", "values": only_active})

    # Outlier confidence in shadow vs active (informational only).
    active_conf = [
        float(claim.get("confidence"))
        for item in active
        for claim in item.claims
        if isinstance(claim.get("confidence"), (int, float))
    ]
    shadow_conf = [
        float(claim.get("confidence"))
        for item in shadow
        for claim in item.claims
        if isinstance(claim.get("confidence"), (int, float))
    ]
    if active_conf and shadow_conf and max(shadow_conf) - max(active_conf) > 0.25:
        anomalies.append("shadow_candidate_higher_confidence_than_active")
        divergences.append(
            {
                "type": "confidence_divergence",
                "active_max": max(active_conf),
                "shadow_max": max(shadow_conf),
            }
        )

    status = "DIVERGENT" if divergences or anomalies else "ALIGNED"
    comparison = ShadowComparison(
        comparison_id=make_id("shadow", task.task_id, task.run_id, active_ids, shadow_ids),
        task_id=task.task_id,
        run_id=task.run_id,
        active_contribution_ids=active_ids,
        shadow_contribution_ids=shadow_ids,
        divergences=tuple(divergences),
        anomalies=tuple(anomalies),
        status=status,
        provenance=Provenance(classification="OBSERVED", producer="core.alembic.shadow"),
    )
    digest = hash_model(comparison)
    return comparison.model_copy(
        update={
            "provenance": comparison.provenance.model_copy(
                update={"content_hash": digest, "notes": det_timestamp(digest)}
            )
        }
    )
