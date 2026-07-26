"""Canonical Alembic domain models (frozen, schema-aligned)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from core.alembic.constants import (
    ADAPTER_STATES,
    ARCHITECTURE_FAMILIES,
    AUTHORITY_CLASSES,
    AUTHORITY_LOCKS,
    CONFLICT_TYPES,
    CONTRIBUTION_STATUSES,
    DETERMINISM_LEVELS,
    FINAL_STATUS,
    GOVERNANCE_CLASSES,
    PROPOSAL_STATUSES,
    ROUTER_VERSION,
    SCORE_COMPONENTS,
    VERIFICATION_STATUSES,
)


class _Frozen(BaseModel):
    model_config = {"frozen": True, "extra": "forbid"}


class Provenance(_Frozen):
    classification: Literal["OBSERVED", "INFERRED", "SPECULATIVE", "NOT_COMPUTABLE"] = (
        "OBSERVED"
    )
    producer: str = "core.alembic"
    producer_version: str = "1.0.0"
    content_hash: str | None = None
    notes: str | None = None


class ResourceProfile(_Frozen):
    compute_units: float = Field(default=1.0, ge=0.0)
    memory_mb: float = Field(default=64.0, ge=0.0)
    notes: str | None = None


class LatencyProfile(_Frozen):
    expected_ms: float = Field(default=10.0, ge=0.0)
    p95_ms: float = Field(default=50.0, ge=0.0)


class CostProfile(_Frozen):
    relative_cost: float = Field(default=1.0, ge=0.0)
    currency: str = "relative"


class EnergyProfile(_Frozen):
    relative_energy: float = Field(default=1.0, ge=0.0)


class ArchitectureDescriptor(_Frozen):
    schema_version: Literal["ArchitectureDescriptor.v1"] = "ArchitectureDescriptor.v1"
    architecture_id: str = Field(min_length=1)
    architecture_family: str
    implementation_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    capabilities: tuple[str, ...] = ()
    supported_modalities: tuple[str, ...] = ()
    supported_task_types: tuple[str, ...] = ()
    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()
    determinism_level: str
    uncertainty_support: bool = False
    verification_support: bool = False
    resource_profile: ResourceProfile = Field(default_factory=ResourceProfile)
    latency_profile: LatencyProfile = Field(default_factory=LatencyProfile)
    energy_profile: EnergyProfile = Field(default_factory=EnergyProfile)
    cost_profile: CostProfile = Field(default_factory=CostProfile)
    context_limits: dict[str, Any] = Field(default_factory=dict)
    privacy_constraints: tuple[str, ...] = ()
    security_constraints: tuple[str, ...] = ()
    governance_class: str
    authority_class: str
    deployment_environment: str = "local_advisory"
    adapter_id: str = Field(min_length=1)
    calibration_profile_id: str | None = None
    historical_metrics_ref: str | None = None
    status: str
    is_stub: bool = False
    provenance: Provenance = Field(default_factory=Provenance)

    @field_validator("architecture_family")
    @classmethod
    def _family(cls, value: str) -> str:
        if value not in ARCHITECTURE_FAMILIES:
            raise ValueError(f"unknown architecture_family: {value}")
        return value

    @field_validator("determinism_level")
    @classmethod
    def _det(cls, value: str) -> str:
        if value not in DETERMINISM_LEVELS:
            raise ValueError(f"unknown determinism_level: {value}")
        return value

    @field_validator("governance_class")
    @classmethod
    def _gov(cls, value: str) -> str:
        if value not in GOVERNANCE_CLASSES:
            raise ValueError(f"unknown governance_class: {value}")
        return value

    @field_validator("authority_class")
    @classmethod
    def _auth(cls, value: str) -> str:
        if value not in AUTHORITY_CLASSES:
            raise ValueError(f"unknown authority_class: {value}")
        return value

    @field_validator("status")
    @classmethod
    def _status(cls, value: str) -> str:
        if value not in ADAPTER_STATES:
            raise ValueError(f"unknown status: {value}")
        return value


class TaskEnvelope(_Frozen):
    schema_version: Literal["TaskEnvelope.v1"] = "TaskEnvelope.v1"
    task_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    task_type: str = Field(min_length=1)
    input_modalities: tuple[str, ...] = Field(min_length=1)
    input_artifacts: tuple[dict[str, Any], ...] = ()
    required_output_contract: str = Field(min_length=1)
    constraints: dict[str, Any] = Field(default_factory=dict)
    latency_budget_ms: float | None = Field(default=None, ge=0.0)
    compute_budget: float | None = Field(default=None, ge=0.0)
    cost_budget: float | None = Field(default=None, ge=0.0)
    energy_budget: float | None = Field(default=None, ge=0.0)
    privacy_class: str = "internal"
    security_class: str = "standard"
    required_determinism: str = "BOUNDED_DETERMINISTIC"
    uncertainty_tolerance: float = Field(default=1.0, ge=0.0, le=1.0)
    verification_requirements: tuple[str, ...] = ()
    allowed_architecture_families: tuple[str, ...] = ()
    disallowed_architecture_families: tuple[str, ...] = ()
    required_runes: tuple[str, ...] = ()
    operator_policy_ref: str | None = None
    governance_context: dict[str, Any] = Field(default_factory=dict)
    historical_context_refs: tuple[str, ...] = ()
    lane: Literal["ADVISORY", "SHADOW", "FORECAST"] = "ADVISORY"
    require_calibration: bool = False
    provenance: Provenance = Field(default_factory=Provenance)

    @field_validator("required_determinism")
    @classmethod
    def _det(cls, value: str) -> str:
        if value not in DETERMINISM_LEVELS:
            raise ValueError(f"unknown required_determinism: {value}")
        return value

    @field_validator("allowed_architecture_families", "disallowed_architecture_families")
    @classmethod
    def _families(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            if item not in ARCHITECTURE_FAMILIES:
                raise ValueError(f"unknown architecture_family: {item}")
        return value


class ValidationResult(_Frozen):
    ok: bool
    reasons: tuple[str, ...] = ()


class ExecutionEstimate(_Frozen):
    feasible: bool
    expected_latency_ms: float = 0.0
    expected_cost: float = 0.0
    expected_energy: float = 0.0
    expected_compute: float = 0.0
    reasons: tuple[str, ...] = ()


class AdapterHealth(_Frozen):
    adapter_id: str
    status: str
    ready: bool
    detail: str = ""

    @field_validator("status")
    @classmethod
    def _status(cls, value: str) -> str:
        if value not in ADAPTER_STATES:
            raise ValueError(f"unknown status: {value}")
        return value


class RawResult(_Frozen):
    adapter_id: str
    architecture_id: str
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    is_stub: bool = False
    resource_usage: dict[str, float] = Field(default_factory=dict)

    @field_validator("status")
    @classmethod
    def _status(cls, value: str) -> str:
        if value not in CONTRIBUTION_STATUSES:
            raise ValueError(f"unknown status: {value}")
        return value


class ArchitectureContribution(_Frozen):
    schema_version: Literal["ArchitectureContribution.v1"] = "ArchitectureContribution.v1"
    contribution_id: str
    task_id: str
    run_id: str
    architecture_id: str
    adapter_id: str
    status: str
    output_payload: dict[str, Any] = Field(default_factory=dict)
    output_contract: str
    claims: tuple[dict[str, Any], ...] = ()
    evidence_refs: tuple[str, ...] = ()
    uncertainty: float | None = None
    confidence: float | None = None
    calibrated_confidence: float | None = None
    calibration_metadata: dict[str, Any] = Field(default_factory=dict)
    assumptions: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    resource_usage: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0.0
    cost: float = 0.0
    energy_usage: float = 0.0
    verification_status: str = "ABSTAIN"
    policy_status: str = "ADVISORY_ONLY"
    provenance: Provenance = Field(default_factory=Provenance)
    artifact_refs: tuple[str, ...] = ()
    error: str | None = None
    is_stub: bool = False
    lane: Literal["ADVISORY", "SHADOW", "FORECAST"] = "ADVISORY"

    @field_validator("status")
    @classmethod
    def _status(cls, value: str) -> str:
        if value not in CONTRIBUTION_STATUSES:
            raise ValueError(f"unknown status: {value}")
        return value


class ScoreComponents(_Frozen):
    values: dict[str, float]

    @model_validator(mode="after")
    def _validate_keys(self) -> ScoreComponents:
        unknown = sorted(set(self.values) - set(SCORE_COMPONENTS))
        if unknown:
            raise ValueError(f"unknown score components: {unknown}")
        return self


class CandidateScore(_Frozen):
    architecture_id: str
    total: float
    components: dict[str, float]
    rationale: str


class HybridNode(_Frozen):
    node_id: str
    architecture_id: str
    role: str
    depends_on: tuple[str, ...] = ()


class HybridPlan(_Frozen):
    schema_version: Literal["HybridPlan.v1"] = "HybridPlan.v1"
    plan_id: str
    nodes: tuple[HybridNode, ...]
    execution_order: tuple[str, ...]
    parallelizable_stages: tuple[tuple[str, ...], ...] = ()
    input_output_contracts: dict[str, str] = Field(default_factory=dict)
    verification_points: tuple[str, ...] = ()
    stop_conditions: tuple[str, ...] = ()
    fallbacks: tuple[str, ...] = ()
    resource_ceilings: dict[str, float] = Field(default_factory=dict)
    fusion_method: str = "deterministic_evidence_union"
    iterative_loop_bound: int | None = None


class RoutingDecision(_Frozen):
    schema_version: Literal["RoutingDecision.v1"] = "RoutingDecision.v1"
    decision_id: str
    task_id: str
    run_id: str
    eligible_candidates: tuple[str, ...] = ()
    rejected_candidates: tuple[dict[str, Any], ...] = ()
    rejection_reasons: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    candidate_scores: tuple[CandidateScore, ...] = ()
    score_components: dict[str, dict[str, float]] = Field(default_factory=dict)
    selected_candidates: tuple[str, ...] = ()
    hybrid_plan: HybridPlan | None = None
    verification_plan: tuple[str, ...] = ()
    fusion_policy: str = "deterministic_evidence_union"
    fallback_plan: tuple[str, ...] = ()
    abstention_reason: str | None = None
    policy_refs: tuple[str, ...] = ()
    rune_bindings: tuple[str, ...] = ()
    router_version: str = ROUTER_VERSION
    score_weight_version: str = "alembic.weights.v1"
    score_weights: dict[str, float] = Field(default_factory=dict)
    timestamp: str
    provenance: Provenance = Field(default_factory=Provenance)
    authority_locks: dict[str, bool] = Field(
        default_factory=lambda: dict(AUTHORITY_LOCKS)
    )
    FINAL_STATUS: Literal["ALEMBIC_SPINE_ADVISORY_ONLY"] = FINAL_STATUS


class ConflictRecord(_Frozen):
    conflict_id: str
    conflict_type: str
    contribution_ids: tuple[str, ...]
    detail: str
    resolved: bool = False
    resolution: str | None = None

    @field_validator("conflict_type")
    @classmethod
    def _ctype(cls, value: str) -> str:
        if value not in CONFLICT_TYPES:
            raise ValueError(f"unknown conflict_type: {value}")
        return value


class VerificationResult(_Frozen):
    schema_version: Literal["VerificationResult.v1"] = "VerificationResult.v1"
    verification_id: str
    task_id: str
    run_id: str
    status: str
    checks: tuple[dict[str, Any], ...] = ()
    residuals: tuple[str, ...] = ()
    conflicts: tuple[ConflictRecord, ...] = ()
    contribution_ids: tuple[str, ...] = ()
    provenance: Provenance = Field(default_factory=Provenance)
    FINAL_STATUS: Literal["ALEMBIC_SPINE_ADVISORY_ONLY"] = FINAL_STATUS

    @field_validator("status")
    @classmethod
    def _status(cls, value: str) -> str:
        if value not in VERIFICATION_STATUSES:
            raise ValueError(f"unknown status: {value}")
        return value


class FusionResult(_Frozen):
    schema_version: Literal["FusionResult.v1"] = "FusionResult.v1"
    fusion_id: str
    task_id: str
    run_id: str
    input_contribution_ids: tuple[str, ...] = ()
    accepted_contribution_ids: tuple[str, ...] = ()
    rejected_contribution_ids: tuple[str, ...] = ()
    conflicts: tuple[ConflictRecord, ...] = ()
    conflict_resolution: str | None = None
    fusion_method: str
    fused_output: dict[str, Any] = Field(default_factory=dict)
    uncertainty: float | None = None
    confidence: float | None = None
    calibrated_confidence: float | None = None
    verification_summary: dict[str, Any] = Field(default_factory=dict)
    calibration_summary: dict[str, Any] = Field(default_factory=dict)
    policy_summary: dict[str, Any] = Field(default_factory=dict)
    lineage: tuple[str, ...] = ()
    residuals: tuple[str, ...] = ()
    status: str
    provenance: Provenance = Field(default_factory=Provenance)
    authority_locks: dict[str, bool] = Field(
        default_factory=lambda: dict(AUTHORITY_LOCKS)
    )
    FINAL_STATUS: Literal["ALEMBIC_SPINE_ADVISORY_ONLY"] = FINAL_STATUS


class ShadowComparison(_Frozen):
    schema_version: Literal["ShadowComparison.v1"] = "ShadowComparison.v1"
    comparison_id: str
    task_id: str
    run_id: str
    active_contribution_ids: tuple[str, ...] = ()
    shadow_contribution_ids: tuple[str, ...] = ()
    divergences: tuple[dict[str, Any], ...] = ()
    anomalies: tuple[str, ...] = ()
    promotion_allowed: Literal[False] = False
    policy_mutation_allowed: Literal[False] = False
    status: str
    provenance: Provenance = Field(default_factory=Provenance)


class RouterChangeProposal(_Frozen):
    schema_version: Literal["RouterChangeProposal.v1"] = "RouterChangeProposal.v1"
    proposal_id: str
    current_configuration: dict[str, Any]
    proposed_configuration: dict[str, Any]
    evidence: tuple[str, ...] = ()
    expected_benefit: str
    uncertainty: float = Field(ge=0.0, le=1.0)
    risk: str
    affected_tasks: tuple[str, ...] = ()
    affected_architectures: tuple[str, ...] = ()
    backtest_result: dict[str, Any] = Field(default_factory=dict)
    shadow_result: dict[str, Any] = Field(default_factory=dict)
    rollback_plan: str
    operator_gate_required: Literal[True] = True
    status: str
    provenance: Provenance = Field(default_factory=Provenance)

    @field_validator("status")
    @classmethod
    def _status(cls, value: str) -> str:
        if value not in PROPOSAL_STATUSES:
            raise ValueError(f"unknown status: {value}")
        return value


class EvaluationCaseResult(_Frozen):
    case_id: str
    passed: bool
    detail: str
    artifacts: dict[str, Any] = Field(default_factory=dict)


class EvaluationResult(_Frozen):
    schema_version: Literal["EvaluationResult.v1"] = "EvaluationResult.v1"
    evaluation_id: str
    cases: tuple[EvaluationCaseResult, ...]
    passed_count: int
    failed_count: int
    status: str
    provenance: Provenance = Field(default_factory=Provenance)
    FINAL_STATUS: Literal["ALEMBIC_SPINE_ADVISORY_ONLY"] = FINAL_STATUS


class AlembicRunReceipt(_Frozen):
    schema_version: Literal["AlembicRunReceipt.v1"] = "AlembicRunReceipt.v1"
    artifact_type: Literal["alembic_run_receipt"] = "alembic_run_receipt"
    artifact_id: str
    run_id: str
    task_id: str
    parent_artifact_ids: tuple[str, ...] = ()
    producer: str = "core.alembic"
    producer_version: str = "1.0.0"
    timestamp: str
    content_hash: str
    configuration_hash: str
    policy_refs: tuple[str, ...] = ()
    provenance: Provenance
    authority: dict[str, bool] = Field(default_factory=lambda: dict(AUTHORITY_LOCKS))
    status: str
    decision_id: str | None = None
    fusion_id: str | None = None
    verification_id: str | None = None
    abstention_reason: str | None = None
    replay_manifest_ref: str | None = None
    lane: Literal["ADVISORY", "SHADOW", "FORECAST"] = "ADVISORY"
    FINAL_STATUS: Literal["ALEMBIC_SPINE_ADVISORY_ONLY"] = FINAL_STATUS


class ExecutionContext(_Frozen):
    run_id: str
    lane: Literal["ADVISORY", "SHADOW", "FORECAST"] = "ADVISORY"
    policy_refs: tuple[str, ...] = ()
    allow_stubs: bool = True
    dry_run: bool = False
