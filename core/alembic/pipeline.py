"""Alembic advisory execution pipeline (pure; runners write artifacts)."""

from __future__ import annotations

from typing import Any, Literal

from core.alembic.artifacts import build_replay_manifest, build_run_receipt
from core.alembic.config import RouterPolicy, policy_hash
from core.alembic.fusion import fuse_contributions
from core.alembic.metrics import score_levels
from core.alembic.models import (
    ArchitectureContribution,
    ExecutionContext,
    FusionResult,
    RoutingDecision,
    ShadowComparison,
    TaskEnvelope,
)
from core.alembic.registry import ArchitectureRegistry
from core.alembic.router import route_task
from core.alembic.shadow import compare_active_and_shadow
from core.alembic.util import to_canonical_dict
from core.alembic.verify import verify_contributions


def _normalize_adapter_result(
    adapter: object,
    raw: Any,
    task: TaskEnvelope,
    context: ExecutionContext,
) -> ArchitectureContribution:
    normalize_with_task = getattr(adapter, "normalize_with_task", None)
    if callable(normalize_with_task):
        return normalize_with_task(raw, task, context)
    return adapter.normalize(raw, context)  # type: ignore[attr-defined]


def execute_advisory(
    task: TaskEnvelope,
    registry: ArchitectureRegistry,
    policy: RouterPolicy,
    *,
    mode: Literal["advisory", "shadow"] = "advisory",
    historical_metrics: dict[str, dict[str, float]] | None = None,
    shadow_architecture_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    if mode == "shadow":
        task = task.model_copy(update={"lane": "SHADOW"})
    context = ExecutionContext(
        run_id=task.run_id,
        lane=task.lane if mode != "shadow" else "SHADOW",
        policy_refs=(policy.policy_id,),
        allow_stubs=True,
        dry_run=False,
    )

    decision = route_task(
        task, registry, policy, historical_metrics=historical_metrics
    )
    contributions: list[ArchitectureContribution] = []
    invocation_receipts: list[dict[str, Any]] = []

    for architecture_id in decision.selected_candidates:
        adapter = registry.get_adapter(architecture_id)
        raw = adapter.invoke(task, context)  # type: ignore[attr-defined]
        contribution = _normalize_adapter_result(adapter, raw, task, context)
        if mode == "shadow":
            contribution = contribution.model_copy(update={"lane": "SHADOW"})
        contributions.append(contribution)
        invocation_receipts.append(
            {
                "architecture_id": architecture_id,
                "adapter_id": contribution.adapter_id,
                "raw_status": raw.status,
                "contribution_id": contribution.contribution_id,
                "is_stub": contribution.is_stub,
            }
        )

    verification = verify_contributions(task, tuple(contributions))
    fusion: FusionResult | None = None
    if decision.selected_candidates and decision.abstention_reason is None:
        fusion = fuse_contributions(
            task,
            tuple(contributions),
            verification,
            fusion_method=decision.fusion_policy,
        )

    shadow_comparison: ShadowComparison | None = None
    shadow_contributions: list[ArchitectureContribution] = []
    if shadow_architecture_ids:
        shadow_context = ExecutionContext(
            run_id=task.run_id,
            lane="SHADOW",
            policy_refs=(policy.policy_id,),
            allow_stubs=True,
        )
        for architecture_id in shadow_architecture_ids:
            if architecture_id not in {d.architecture_id for d in registry.list_descriptors()}:
                continue
            adapter = registry.get_adapter(architecture_id)
            raw = adapter.invoke(task, shadow_context)  # type: ignore[attr-defined]
            contribution = _normalize_adapter_result(adapter, raw, task, shadow_context)
            contribution = contribution.model_copy(update={"lane": "SHADOW"})
            shadow_contributions.append(contribution)
        shadow_comparison = compare_active_and_shadow(
            task, tuple(contributions), tuple(shadow_contributions)
        )

    metrics = score_levels(
        decision=decision,
        contributions=tuple(contributions),
        fusion=fusion,
    )
    receipt = build_run_receipt(
        task=task,
        decision=decision,
        verification=verification,
        fusion=fusion,
        configuration_hash=policy_hash(policy),
    )
    replay = build_replay_manifest(
        task=task,
        decision=decision,
        contributions=tuple(contributions),
        verification=verification,
        fusion=fusion,
        policy=policy,
    )

    return {
        "task": to_canonical_dict(task),
        "registry_snapshot": registry.snapshot(),
        "routing_decision": to_canonical_dict(decision),
        "invocation_receipts": invocation_receipts,
        "contributions": [to_canonical_dict(item) for item in contributions],
        "verification": to_canonical_dict(verification),
        "fusion": to_canonical_dict(fusion) if fusion is not None else None,
        "shadow_comparison": to_canonical_dict(shadow_comparison) if shadow_comparison else None,
        "shadow_contributions": [to_canonical_dict(item) for item in shadow_contributions],
        "metrics": metrics,
        "receipt": to_canonical_dict(receipt),
        "replay_manifest": replay,
        "FINAL_STATUS": "ALEMBIC_SPINE_ADVISORY_ONLY",
        "authority_locks": dict(receipt.authority),
    }


def route_only(
    task: TaskEnvelope,
    registry: ArchitectureRegistry,
    policy: RouterPolicy,
) -> RoutingDecision:
    return route_task(task, registry, policy)
