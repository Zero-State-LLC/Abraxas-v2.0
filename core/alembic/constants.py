"""Alembic Spine constants — advisory-only multi-architecture orchestration."""

from __future__ import annotations

FINAL_STATUS = "ALEMBIC_SPINE_ADVISORY_ONLY"
SPINE_VERSION = "1.0.0"
ROUTER_VERSION = "alembic.router.v1"
PRODUCER = "core.alembic"
PRODUCER_VERSION = SPINE_VERSION

AUTHORITY_LOCKS: dict[str, bool] = {
    "execution_authority": False,
    "canon_mutation": False,
    "runtime_mutation": False,
    "forecast_routing": False,
    "policy_self_modification": False,
    "shadow_to_active_promotion": False,
    "auto_apply_router_proposals": False,
}

ARCHITECTURE_FAMILIES: tuple[str, ...] = (
    "symbolic_expert",
    "statistical_ml",
    "transformer",
    "state_space_sequence",
    "graph_neural",
    "convolutional_vision",
    "generative",
    "world_model",
    "agentic",
    "neuro_symbolic",
    "spiking_neuromorphic",
    "deterministic_tool",
    "human_operator_review",
    "composite_hybrid",
)

DETERMINISM_LEVELS: tuple[str, ...] = (
    "STRICT_DETERMINISTIC",
    "BOUNDED_DETERMINISTIC",
    "STOCHASTIC_REPLAYABLE",
    "NONDETERMINISTIC",
)

AUTHORITY_CLASSES: tuple[str, ...] = (
    "ADVISORY_ONLY",
    "SHADOW_ONLY",
    "OPERATOR_GATED",
    "DENIED",
)

GOVERNANCE_CLASSES: tuple[str, ...] = (
    "SYMBOLIC_BACKBONE",
    "SPECIALIST",
    "EXPERIMENTAL",
    "OPERATOR",
)

ADAPTER_STATES: tuple[str, ...] = (
    "REGISTERED",
    "ELIGIBLE",
    "ENABLED",
    "SHADOW_ONLY",
    "UNAVAILABLE",
    "NOT_IMPLEMENTED",
)

CONTRIBUTION_STATUSES: tuple[str, ...] = (
    "OK",
    "PARTIAL",
    "FAILED",
    "UNAVAILABLE",
    "NOT_IMPLEMENTED",
    "STUB",
    "ABSTAIN",
)

VERIFICATION_STATUSES: tuple[str, ...] = (
    "PASS",
    "PASS_WITH_RESIDUALS",
    "FAIL",
    "ABSTAIN",
    "NOT_COMPUTABLE",
)

CONFLICT_TYPES: tuple[str, ...] = (
    "CLAIM_CONFLICT",
    "EVIDENCE_CONFLICT",
    "CONTRACT_CONFLICT",
    "POLICY_CONFLICT",
    "UNCERTAINTY_CONFLICT",
    "TEMPORAL_CONFLICT",
    "PROVENANCE_CONFLICT",
)

PROPOSAL_STATUSES: tuple[str, ...] = (
    "DRAFT",
    "SHADOW_TESTED",
    "READY_FOR_REVIEW",
    "APPROVED",
    "REJECTED",
    "EXPIRED",
)

SCORE_COMPONENTS: tuple[str, ...] = (
    "capability_fit",
    "task_type_fit",
    "modality_fit",
    "historical_accuracy",
    "calibration_quality",
    "verification_compatibility",
    "determinism_fit",
    "latency_fit",
    "compute_fit",
    "cost_fit",
    "energy_fit",
    "privacy_fit",
    "security_fit",
    "uncertainty_fit",
    "historical_failure_rate",
    "drift_penalty",
    "staleness_penalty",
    "complexity_penalty",
)

DEFAULT_SCORE_WEIGHTS: dict[str, float] = {
    "capability_fit": 0.14,
    "task_type_fit": 0.12,
    "modality_fit": 0.10,
    "historical_accuracy": 0.08,
    "calibration_quality": 0.08,
    "verification_compatibility": 0.10,
    "determinism_fit": 0.08,
    "latency_fit": 0.04,
    "compute_fit": 0.03,
    "cost_fit": 0.03,
    "energy_fit": 0.02,
    "privacy_fit": 0.05,
    "security_fit": 0.05,
    "uncertainty_fit": 0.04,
    "historical_failure_rate": 0.02,
    "drift_penalty": 0.01,
    "staleness_penalty": 0.005,
    "complexity_penalty": 0.005,
}
