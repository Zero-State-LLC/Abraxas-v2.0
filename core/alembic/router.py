"""Deterministic explainable paradigm router."""

from __future__ import annotations

from typing import Any

from core.alembic.config import RouterPolicy
from core.alembic.eligibility import evaluate_eligibility
from core.alembic.hybrid import build_hybrid_plan
from core.alembic.models import (
    ArchitectureDescriptor,
    CandidateScore,
    Provenance,
    RoutingDecision,
    TaskEnvelope,
)
from core.alembic.registry import ArchitectureRegistry
from core.alembic.runes import rune_bindings_for_operation
from core.alembic.scoring import score_candidate
from core.alembic.util import det_timestamp, hash_model, make_id


def _task_is_underspecified(task: TaskEnvelope) -> str | None:
    if not task.goal.strip():
        return "empty_goal"
    if not task.task_type.strip():
        return "empty_task_type"
    if not task.input_modalities:
        return "missing_input_modalities"
    if not task.required_output_contract.strip():
        return "missing_output_contract"
    return None


def route_task(
    task: TaskEnvelope,
    registry: ArchitectureRegistry,
    policy: RouterPolicy,
    *,
    historical_metrics: dict[str, dict[str, float]] | None = None,
) -> RoutingDecision:
    underspec = _task_is_underspecified(task)
    health_by_adapter = {item.adapter_id: item for item in registry.health()}
    rejected: list[dict[str, Any]] = []
    rejection_reasons: dict[str, tuple[str, ...]] = {}
    eligible: list[ArchitectureDescriptor] = []

    if underspec:
        decision = RoutingDecision(
            decision_id=make_id("decision", task.task_id, task.run_id, underspec),
            task_id=task.task_id,
            run_id=task.run_id,
            abstention_reason=f"underspecified_task:{underspec}",
            fallback_plan=("operator_review", "clarification"),
            policy_refs=(policy.policy_id, *policy.operator_gate_refs),
            rune_bindings=rune_bindings_for_operation("ROUTER_ABSTAIN"),
            score_weights=dict(policy.score_weights),
            score_weight_version=policy.score_weight_version,
            timestamp=det_timestamp(f"{task.task_id}:{task.run_id}:{underspec}"),
            provenance=Provenance(classification="OBSERVED", producer="core.alembic.router"),
        )
        return decision.model_copy(
            update={"provenance": decision.provenance.model_copy(update={"content_hash": hash_model(decision)})}
        )

    for descriptor in registry.list_descriptors():
        health = health_by_adapter.get(descriptor.adapter_id)
        ready = bool(health.ready) if health is not None else False
        ok, reasons = evaluate_eligibility(
            task, descriptor, policy=policy, health_ready=ready
        )
        # Also ask adapter validate_task when present.
        adapter = registry.get_adapter(descriptor.architecture_id)
        validate = getattr(adapter, "validate_task", None)
        if callable(validate):
            validation = validate(task)
            if not validation.ok:
                ok = False
                reasons = tuple(dict.fromkeys((*reasons, *validation.reasons)))
        if ok:
            eligible.append(descriptor)
        else:
            rejected.append(
                {
                    "architecture_id": descriptor.architecture_id,
                    "reasons": list(reasons),
                }
            )
            rejection_reasons[descriptor.architecture_id] = reasons

    scores: list[CandidateScore] = []
    for descriptor in eligible:
        hist = (historical_metrics or {}).get(descriptor.architecture_id)
        scores.append(score_candidate(task, descriptor, policy=policy, historical=hist))
    scores.sort(key=lambda item: (-item.total, item.architecture_id))

    abstention_reason: str | None = None
    selected: list[str] = []
    hybrid_plan = None
    verification_plan: list[str] = []
    fallback_plan: list[str] = ["abstain"]

    if not eligible:
        abstention_reason = "no_eligible_candidates"
        fallback_plan = ["operator_review", "clarification"]
    else:
        top = scores[0]
        # Tie detection among top scores.
        tied = [
            score
            for score in scores
            if abs(score.total - top.total) <= policy.tie_epsilon
        ]
        if len(tied) > 1 and policy.eligibility.get("tie_break") is None:
            # Deterministic secondary tie-break by architecture_id for selection stability,
            # but if policy forbids implicit tie-break, abstain.
            if policy.eligibility.get("require_explicit_tie_break", True):
                abstention_reason = "candidate_tie_without_tie_break_policy"
            else:
                selected = [tied[0].architecture_id]
        else:
            selected = [top.architecture_id]

        if abstention_reason is None:
            # Optionally include a verifier for hybrid plans.
            if policy.allow_hybrid:
                verifier = next(
                    (
                        descriptor.architecture_id
                        for descriptor in eligible
                        if descriptor.architecture_family == "symbolic_expert"
                        and descriptor.architecture_id not in selected
                    ),
                    None,
                )
                if verifier and task.verification_requirements:
                    selected.append(verifier)
                # statistical + graph hybrid hint
                if task.task_type in {"memetic_analysis", "graph_analysis"}:
                    calib = next(
                        (
                            d.architecture_id
                            for d in eligible
                            if d.architecture_family == "statistical_ml"
                            and d.architecture_id not in selected
                        ),
                        None,
                    )
                    if calib:
                        selected.append(calib)
            selected = selected[: policy.max_selected_candidates]
            if len(selected) > 1:
                family_by_id = {
                    d.architecture_id: d.architecture_family for d in registry.list_descriptors()
                }
                hybrid_plan = build_hybrid_plan(
                    tuple(selected),
                    family_by_id=family_by_id,
                    fusion_method=policy.default_fusion_method,
                )
            verification_plan = [
                arch_id
                for arch_id in selected
                if registry.get(arch_id).verification_support
            ]
            if task.require_calibration:
                missing_cal = [
                    arch_id
                    for arch_id in selected
                    if registry.get(arch_id).calibration_profile_id is None
                ]
                if missing_cal and policy.require_calibration_when_flagged:
                    abstention_reason = "calibration_data_missing_where_required"
                    selected = []
                    hybrid_plan = None

    if task.governance_context.get("attempted_authority_escalation"):
        abstention_reason = "unsupported_authority_request"
        selected = []
        hybrid_plan = None
        fallback_plan = ["deny", "operator_review"]

    operation = "PARADIGM_ROUTE" if selected else "ROUTER_ABSTAIN"
    decision = RoutingDecision(
        decision_id=make_id("decision", task.task_id, task.run_id, tuple(selected), abstention_reason),
        task_id=task.task_id,
        run_id=task.run_id,
        eligible_candidates=tuple(d.architecture_id for d in eligible),
        rejected_candidates=tuple(sorted(rejected, key=lambda row: row["architecture_id"])),
        rejection_reasons={key: rejection_reasons[key] for key in sorted(rejection_reasons)},
        candidate_scores=tuple(scores),
        score_components={score.architecture_id: score.components for score in scores},
        selected_candidates=tuple(selected),
        hybrid_plan=hybrid_plan,
        verification_plan=tuple(verification_plan),
        fusion_policy=policy.default_fusion_method,
        fallback_plan=tuple(fallback_plan),
        abstention_reason=abstention_reason,
        policy_refs=(policy.policy_id, *policy.operator_gate_refs),
        rune_bindings=rune_bindings_for_operation(operation),
        score_weights=dict(policy.score_weights),
        score_weight_version=policy.score_weight_version,
        timestamp=det_timestamp(f"{task.task_id}:{task.run_id}:{selected}:{abstention_reason}"),
        provenance=Provenance(classification="OBSERVED", producer="core.alembic.router"),
    )
    digest = hash_model(decision)
    return decision.model_copy(
        update={"provenance": decision.provenance.model_copy(update={"content_hash": digest})}
    )
