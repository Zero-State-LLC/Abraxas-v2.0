"""Explicit non-executing specialist stubs — never scored as successful executions."""

from __future__ import annotations

from core.alembic.adapters.base import normalize_raw
from core.alembic.models import (
    AdapterHealth,
    ArchitectureContribution,
    ArchitectureDescriptor,
    ExecutionContext,
    ExecutionEstimate,
    Provenance,
    RawResult,
    ResourceProfile,
    TaskEnvelope,
    ValidationResult,
)


class _StubAdapter:
    architecture_id: str
    architecture_family: str
    adapter_id: str
    implementation_id: str
    capabilities: tuple[str, ...]
    supported_task_types: tuple[str, ...]
    status: str
    detail: str

    def descriptor(self) -> ArchitectureDescriptor:
        return ArchitectureDescriptor(
            architecture_id=self.architecture_id,
            architecture_family=self.architecture_family,
            implementation_id=self.implementation_id,
            version="0.0.0-stub",
            capabilities=self.capabilities,
            supported_modalities=("structured_json", "text", "sequence"),
            supported_task_types=self.supported_task_types,
            input_contracts=("TaskEnvelope.v1",),
            output_contracts=("ArchitectureContribution.v1",),
            determinism_level="NONDETERMINISTIC",
            uncertainty_support=True,
            verification_support=False,
            resource_profile=ResourceProfile(compute_units=10.0, memory_mb=1024.0),
            privacy_constraints=("local_only",),
            security_constraints=("no_external_side_effects",),
            governance_class="EXPERIMENTAL",
            authority_class="SHADOW_ONLY",
            adapter_id=self.adapter_id,
            status=self.status,
            is_stub=True,
            provenance=Provenance(
                classification="SPECULATIVE",
                producer="core.alembic",
                notes="explicit stub; not an operational integration",
            ),
        )

    def validate_task(self, task: TaskEnvelope) -> ValidationResult:
        return ValidationResult(ok=True, reasons=())

    def estimate(self, task: TaskEnvelope) -> ExecutionEstimate:
        return ExecutionEstimate(
            feasible=False,
            reasons=(self.status,),
        )

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult:
        return RawResult(
            adapter_id=self.adapter_id,
            architecture_id=self.architecture_id,
            status=self.status,
            payload={
                "stub": True,
                "detail": self.detail,
                "claims": [],
            },
            error=self.detail,
            is_stub=True,
            resource_usage={"latency_ms": 0.0, "cost": 0.0, "energy": 0.0, "compute": 0.0},
        )

    def normalize(
        self, raw: RawResult, context: ExecutionContext
    ) -> ArchitectureContribution:
        raise RuntimeError("use normalize_with_task")

    def normalize_with_task(
        self, raw: RawResult, task: TaskEnvelope, context: ExecutionContext
    ) -> ArchitectureContribution:
        return normalize_raw(
            raw,
            task=task,
            context=context,
            output_contract=task.required_output_contract,
            claims=(),
            confidence=None,
            uncertainty=None,
            assumptions=("stub_adapter",),
            limitations=(self.detail,),
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.adapter_id,
            status=self.status,
            ready=False,
            detail=self.detail,
        )


class StateSpaceStubAdapter(_StubAdapter):
    architecture_id = "arch.ssm_sequence.v1"
    architecture_family = "state_space_sequence"
    adapter_id = "adapter.ssm_sequence.stub"
    implementation_id = "alembic.ssm_stub"
    capabilities = ("long_sequence_analysis",)
    supported_task_types = ("sequence_analysis", "advisory_analysis")
    status = "NOT_IMPLEMENTED"
    detail = "SSM/Mamba specialist stub — NOT_IMPLEMENTED"


class GenerativeStubAdapter(_StubAdapter):
    architecture_id = "arch.generative.v1"
    architecture_family = "generative"
    adapter_id = "adapter.generative.stub"
    implementation_id = "alembic.generative_stub"
    capabilities = ("generation", "diffusion_vae_hint")
    supported_task_types = ("generate", "advisory_analysis")
    status = "NOT_IMPLEMENTED"
    detail = "Generative specialist stub — NOT_IMPLEMENTED"


class SpikingNeuromorphicStubAdapter(_StubAdapter):
    architecture_id = "arch.snn_neuromorphic.v1"
    architecture_family = "spiking_neuromorphic"
    adapter_id = "adapter.snn_neuromorphic.stub"
    implementation_id = "alembic.snn_stub"
    capabilities = ("temporal_spike_detection",)
    supported_task_types = ("temporal_detection", "advisory_analysis")
    status = "UNAVAILABLE"
    detail = "SNN/neuromorphic simulator stub — UNAVAILABLE (experimental shadow path)"


class OperatorReviewAdapter:
    def descriptor(self) -> ArchitectureDescriptor:
        return ArchitectureDescriptor(
            architecture_id="arch.human_operator_review.v1",
            architecture_family="human_operator_review",
            implementation_id="alembic.operator_review",
            version="1.0.0",
            capabilities=("human_review", "authority_gate"),
            supported_modalities=("structured_json", "text"),
            supported_task_types=("operator_review", "advisory_analysis", "clarification"),
            input_contracts=("TaskEnvelope.v1",),
            output_contracts=("ArchitectureContribution.v1",),
            determinism_level="NONDETERMINISTIC",
            uncertainty_support=True,
            verification_support=True,
            resource_profile=ResourceProfile(compute_units=0.0, memory_mb=0.0),
            privacy_constraints=("operator_controlled",),
            security_constraints=("no_external_side_effects",),
            governance_class="OPERATOR",
            authority_class="OPERATOR_GATED",
            adapter_id="adapter.operator_review",
            status="ENABLED",
            is_stub=False,
            provenance=Provenance(classification="OBSERVED", producer="core.alembic"),
        )

    def validate_task(self, task: TaskEnvelope) -> ValidationResult:
        return ValidationResult(ok=True, reasons=())

    def estimate(self, task: TaskEnvelope) -> ExecutionEstimate:
        return ExecutionEstimate(
            feasible=True,
            expected_latency_ms=0.0,
            expected_cost=0.0,
            expected_energy=0.0,
            expected_compute=0.0,
            reasons=("requires_operator",),
        )

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult:
        return RawResult(
            adapter_id=self.descriptor().adapter_id,
            architecture_id=self.descriptor().architecture_id,
            status="ABSTAIN",
            payload={
                "requires_operator": True,
                "claims": [
                    {
                        "claim_id": "operator-claim-0",
                        "statement": f"Operator review required for: {task.goal}",
                        "status": "NOT_COMPUTABLE",
                        "confidence": "NOT_COMPUTABLE",
                    }
                ],
            },
            error="operator_review_required",
            is_stub=False,
            resource_usage={"latency_ms": 0.0, "cost": 0.0, "energy": 0.0, "compute": 0.0},
        )

    def normalize(
        self, raw: RawResult, context: ExecutionContext
    ) -> ArchitectureContribution:
        raise RuntimeError("use normalize_with_task")

    def normalize_with_task(
        self, raw: RawResult, task: TaskEnvelope, context: ExecutionContext
    ) -> ArchitectureContribution:
        return normalize_raw(
            raw,
            task=task,
            context=context,
            output_contract=task.required_output_contract,
            claims=tuple(raw.payload.get("claims", ())),
            confidence=None,
            uncertainty=None,
            assumptions=("human_sovereignty",),
            limitations=("no_automatic_resolution",),
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.descriptor().adapter_id,
            status="ENABLED",
            ready=True,
            detail="operator review adapter ready (always abstains pending operator)",
        )
