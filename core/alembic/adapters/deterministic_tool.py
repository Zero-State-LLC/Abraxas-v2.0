"""Deterministic tool/solver adapter."""

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


class DeterministicToolAdapter:
    def descriptor(self) -> ArchitectureDescriptor:
        return ArchitectureDescriptor(
            architecture_id="arch.deterministic_solver.v1",
            architecture_family="deterministic_tool",
            implementation_id="alembic.deterministic_solver",
            version="1.0.0",
            capabilities=("constraint_solve", "deterministic_transform"),
            supported_modalities=("structured_json", "text"),
            supported_task_types=("solve", "transform", "advisory_analysis"),
            input_contracts=("TaskEnvelope.v1",),
            output_contracts=("ArchitectureContribution.v1",),
            determinism_level="STRICT_DETERMINISTIC",
            uncertainty_support=False,
            verification_support=True,
            resource_profile=ResourceProfile(compute_units=0.25, memory_mb=16.0),
            privacy_constraints=("local_only",),
            security_constraints=("no_external_side_effects",),
            governance_class="SPECIALIST",
            authority_class="ADVISORY_ONLY",
            adapter_id="adapter.deterministic_solver",
            status="ENABLED",
            is_stub=False,
            provenance=Provenance(classification="OBSERVED", producer="core.alembic"),
        )

    def validate_task(self, task: TaskEnvelope) -> ValidationResult:
        reasons: list[str] = []
        if "structured_json" not in task.input_modalities and "text" not in task.input_modalities:
            reasons.append("unsupported_modality")
        return ValidationResult(ok=not reasons, reasons=tuple(reasons))

    def estimate(self, task: TaskEnvelope) -> ExecutionEstimate:
        return ExecutionEstimate(
            feasible=True,
            expected_latency_ms=2.0,
            expected_cost=0.05,
            expected_energy=0.05,
            expected_compute=0.25,
        )

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult:
        constraints = dict(task.constraints)
        solved = sorted(constraints.items())
        return RawResult(
            adapter_id=self.descriptor().adapter_id,
            architecture_id=self.descriptor().architecture_id,
            status="OK",
            payload={
                "solver": "deterministic_key_sort",
                "solved_constraints": solved,
                "claims": [
                    {
                        "claim_id": "solver-claim-0",
                        "statement": f"Deterministic transform of goal: {task.goal}",
                        "status": "OBSERVED",
                        "confidence": 1.0,
                    }
                ],
            },
            is_stub=False,
            resource_usage={"latency_ms": 2.0, "cost": 0.05, "energy": 0.05, "compute": 0.25},
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
            confidence=1.0,
            uncertainty=0.0,
            assumptions=("constraints_are_explicit",),
            limitations=("no_search_beyond_provided_constraints",),
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.descriptor().adapter_id,
            status="ENABLED",
            ready=True,
            detail="deterministic solver ready",
        )
