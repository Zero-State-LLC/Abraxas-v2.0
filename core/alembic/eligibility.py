"""Eligibility filters — applied before ranking."""

from __future__ import annotations

from core.alembic.config import RouterPolicy
from core.alembic.constants import DETERMINISM_LEVELS
from core.alembic.models import ArchitectureDescriptor, TaskEnvelope

_DETERMINISM_RANK = {name: index for index, name in enumerate(DETERMINISM_LEVELS)}


def _determinism_ok(required: str, actual: str) -> bool:
    return _DETERMINISM_RANK[actual] <= _DETERMINISM_RANK[required]


def evaluate_eligibility(
    task: TaskEnvelope,
    descriptor: ArchitectureDescriptor,
    *,
    policy: RouterPolicy,
    health_ready: bool,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []

    if descriptor.status in {"UNAVAILABLE", "NOT_IMPLEMENTED"}:
        reasons.append(f"adapter_status:{descriptor.status}")
    if descriptor.status == "SHADOW_ONLY" and task.lane != "SHADOW":
        reasons.append("shadow_only_architecture")
    # stubs are handled via status; non-ready enabled adapters fail closed
    if (
        not health_ready
        and descriptor.status not in {"UNAVAILABLE", "NOT_IMPLEMENTED"}
        and descriptor.status in {"ENABLED", "ELIGIBLE", "REGISTERED"}
    ):
        reasons.append("adapter_not_ready")

    if (
        task.allowed_architecture_families
        and descriptor.architecture_family not in task.allowed_architecture_families
    ):
        reasons.append("family_not_allowlisted")
    if descriptor.architecture_family in task.disallowed_architecture_families:
        reasons.append("family_denylisted")

    modality_ok = any(
        modality in descriptor.supported_modalities for modality in task.input_modalities
    )
    if not modality_ok:
        reasons.append("unsupported_modality")

    if task.task_type not in descriptor.supported_task_types and "advisory_analysis" not in descriptor.supported_task_types:
        reasons.append("unsupported_task_type")

    if descriptor.authority_class == "DENIED":
        reasons.append("authority_denied")
    if task.governance_context.get("require_symbolic_backbone") and descriptor.governance_class != "SYMBOLIC_BACKBONE":
        reasons.append("symbolic_backbone_required")
    if task.lane == "ADVISORY" and descriptor.authority_class not in {
        "ADVISORY_ONLY",
        "OPERATOR_GATED",
        "SHADOW_ONLY",
    }:
        reasons.append("authority_class_incompatible")

    privacy_required = tuple(task.constraints.get("required_privacy", ()))
    for item in privacy_required:
        if item not in descriptor.privacy_constraints:
            reasons.append(f"privacy_constraint_missing:{item}")
            break
    if task.privacy_class == "strict_local" and "local_only" not in descriptor.privacy_constraints:
        reasons.append("privacy_class_violation")

    security_required = tuple(task.constraints.get("required_security", ()))
    for item in security_required:
        if item not in descriptor.security_constraints:
            reasons.append(f"security_constraint_missing:{item}")
            break

    if not _determinism_ok(task.required_determinism, descriptor.determinism_level):
        reasons.append("determinism_requirement_unmet")

    if task.latency_budget_ms is not None and descriptor.latency_profile.expected_ms > task.latency_budget_ms:
        reasons.append("latency_budget_exceeded")
    if task.compute_budget is not None and descriptor.resource_profile.compute_units > task.compute_budget:
        reasons.append("compute_budget_exceeded")
    if task.cost_budget is not None and descriptor.cost_profile.relative_cost > task.cost_budget:
        reasons.append("cost_budget_exceeded")
    if task.energy_budget is not None and descriptor.energy_profile.relative_energy > task.energy_budget:
        reasons.append("energy_budget_exceeded")

    ceilings = policy.resource_ceilings
    if "latency_ms" in ceilings and descriptor.latency_profile.expected_ms > ceilings["latency_ms"]:
        reasons.append("policy_latency_ceiling")
    if "compute" in ceilings and descriptor.resource_profile.compute_units > ceilings["compute"]:
        reasons.append("policy_compute_ceiling")

    context_limit = descriptor.context_limits.get("max_artifacts")
    if context_limit is not None and len(task.input_artifacts) > int(context_limit):
        reasons.append("context_limit_exceeded")

    if (
        task.require_calibration
        and descriptor.calibration_profile_id is None
        and policy.require_calibration_when_flagged
    ):
        reasons.append("calibration_required_missing")

    if task.required_runes:
        # Rune restriction is recorded; adapters do not execute runes directly.
        allowed = set(policy.eligibility.get("allowed_runes", task.required_runes))
        if any(rune not in allowed for rune in task.required_runes):
            reasons.append("rune_restriction")

    # Stubs may be inspected but never enter ranking as executable successes.
    if descriptor.is_stub:
        reasons.append("stub_not_executable")

    return (not reasons, tuple(reasons))
