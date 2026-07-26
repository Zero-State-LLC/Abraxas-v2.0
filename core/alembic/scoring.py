"""Explicit, versioned candidate scoring."""

from __future__ import annotations

from core.alembic.config import RouterPolicy
from core.alembic.constants import SCORE_COMPONENTS
from core.alembic.models import ArchitectureDescriptor, CandidateScore, TaskEnvelope


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_components(
    task: TaskEnvelope,
    descriptor: ArchitectureDescriptor,
    *,
    historical: dict[str, float] | None = None,
) -> dict[str, float]:
    hist = historical or {}
    modality_hits = sum(
        1 for modality in task.input_modalities if modality in descriptor.supported_modalities
    )
    modality_fit = modality_hits / max(1, len(task.input_modalities))
    task_type_fit = 1.0 if task.task_type in descriptor.supported_task_types else (
        0.6 if "advisory_analysis" in descriptor.supported_task_types else 0.0
    )
    capability_fit = 1.0 if descriptor.capabilities else 0.2
    if task.task_type == "verify" and "contract_check" in descriptor.capabilities:
        capability_fit = 1.0
    if task.task_type == "calibrate" and "calibration" in descriptor.capabilities:
        capability_fit = 1.0

    determinism_fit = {
        "STRICT_DETERMINISTIC": 1.0,
        "BOUNDED_DETERMINISTIC": 0.8,
        "STOCHASTIC_REPLAYABLE": 0.5,
        "NONDETERMINISTIC": 0.2,
    }[descriptor.determinism_level]
    if task.required_determinism == "STRICT_DETERMINISTIC":
        determinism_fit = 1.0 if descriptor.determinism_level == "STRICT_DETERMINISTIC" else 0.0

    latency_fit = 1.0
    if task.latency_budget_ms is not None and task.latency_budget_ms > 0:
        latency_fit = _clamp(1.0 - (descriptor.latency_profile.expected_ms / task.latency_budget_ms))
    compute_fit = 1.0
    if task.compute_budget is not None and task.compute_budget > 0:
        compute_fit = _clamp(1.0 - (descriptor.resource_profile.compute_units / task.compute_budget))
    cost_fit = 1.0
    if task.cost_budget is not None and task.cost_budget > 0:
        cost_fit = _clamp(1.0 - (descriptor.cost_profile.relative_cost / task.cost_budget))
    energy_fit = 1.0
    if task.energy_budget is not None and task.energy_budget > 0:
        energy_fit = _clamp(1.0 - (descriptor.energy_profile.relative_energy / task.energy_budget))

    privacy_fit = 1.0 if "local_only" in descriptor.privacy_constraints or task.privacy_class != "strict_local" else 0.0
    security_fit = 1.0 if "no_external_side_effects" in descriptor.security_constraints else 0.5
    uncertainty_fit = 1.0 if descriptor.uncertainty_support or task.uncertainty_tolerance >= 1.0 else 0.5
    verification_compatibility = 1.0 if descriptor.verification_support else 0.4

    values = {
        "capability_fit": capability_fit,
        "task_type_fit": task_type_fit,
        "modality_fit": modality_fit,
        "historical_accuracy": float(hist.get("historical_accuracy", 0.5)),
        "calibration_quality": float(hist.get("calibration_quality", 0.5 if descriptor.calibration_profile_id else 0.2)),
        "verification_compatibility": verification_compatibility,
        "determinism_fit": determinism_fit,
        "latency_fit": latency_fit,
        "compute_fit": compute_fit,
        "cost_fit": cost_fit,
        "energy_fit": energy_fit,
        "privacy_fit": privacy_fit,
        "security_fit": security_fit,
        "uncertainty_fit": uncertainty_fit,
        "historical_failure_rate": float(hist.get("historical_failure_rate", 0.1)),
        "drift_penalty": float(hist.get("drift_penalty", 0.0)),
        "staleness_penalty": float(hist.get("staleness_penalty", 0.0)),
        "complexity_penalty": 0.2 if descriptor.architecture_family in {"generative", "agentic", "world_model"} else 0.05,
    }
    # Ensure complete component set.
    for key in SCORE_COMPONENTS:
        values.setdefault(key, 0.0)
        values[key] = _clamp(float(values[key]))
    return values


def score_candidate(
    task: TaskEnvelope,
    descriptor: ArchitectureDescriptor,
    *,
    policy: RouterPolicy,
    historical: dict[str, float] | None = None,
) -> CandidateScore:
    components = score_components(task, descriptor, historical=historical)
    # Penalties subtract; other components add.
    penalty_keys = {
        "historical_failure_rate",
        "drift_penalty",
        "staleness_penalty",
        "complexity_penalty",
    }
    total = 0.0
    for key, weight in policy.score_weights.items():
        value = components[key]
        if key in penalty_keys:
            total += weight * (1.0 - value)
        else:
            total += weight * value
    total = round(_clamp(total), 10)
    rationale = (
        f"selected_components:capability={components['capability_fit']},"
        f"task={components['task_type_fit']},"
        f"modality={components['modality_fit']},"
        f"verify={components['verification_compatibility']},"
        f"determinism={components['determinism_fit']}"
    )
    return CandidateScore(
        architecture_id=descriptor.architecture_id,
        total=total,
        components=components,
        rationale=rationale,
    )
