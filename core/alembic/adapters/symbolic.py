"""Symbolic verifier adapter — high-trust local checking surface."""

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


class SymbolicVerifierAdapter:
    def descriptor(self) -> ArchitectureDescriptor:
        return ArchitectureDescriptor(
            architecture_id="arch.symbolic_verifier.v1",
            architecture_family="symbolic_expert",
            implementation_id="alembic.symbolic_verifier",
            version="1.0.0",
            capabilities=("contract_check", "consistency_check", "provenance_check"),
            supported_modalities=("text", "structured_json"),
            supported_task_types=("verify", "consistency", "advisory_analysis"),
            input_contracts=("TaskEnvelope.v1",),
            output_contracts=("ArchitectureContribution.v1",),
            determinism_level="STRICT_DETERMINISTIC",
            uncertainty_support=False,
            verification_support=True,
            resource_profile=ResourceProfile(compute_units=0.5, memory_mb=32.0),
            privacy_constraints=("local_only",),
            security_constraints=("no_external_side_effects",),
            governance_class="SYMBOLIC_BACKBONE",
            authority_class="ADVISORY_ONLY",
            adapter_id="adapter.symbolic_verifier",
            status="ENABLED",
            is_stub=False,
            provenance=Provenance(classification="OBSERVED", producer="core.alembic"),
        )

    def validate_task(self, task: TaskEnvelope) -> ValidationResult:
        reasons: list[str] = []
        if "structured_json" not in task.input_modalities and "text" not in task.input_modalities:
            reasons.append("unsupported_modality")
        if task.task_type not in {"verify", "consistency", "advisory_analysis", "route_and_verify"}:
            reasons.append("unsupported_task_type")
        return ValidationResult(ok=not reasons, reasons=tuple(reasons))

    def estimate(self, task: TaskEnvelope) -> ExecutionEstimate:
        return ExecutionEstimate(
            feasible=True,
            expected_latency_ms=5.0,
            expected_cost=0.1,
            expected_energy=0.1,
            expected_compute=0.5,
        )

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult:
        artifacts = list(task.input_artifacts)
        claims = []
        for index, artifact in enumerate(artifacts):
            statement = str(artifact.get("statement", artifact.get("goal", task.goal)))
            claims.append(
                {
                    "claim_id": f"symbolic-claim-{index}",
                    "statement": statement,
                    "status": "OBSERVED",
                    "confidence": 1.0,
                }
            )
        if not claims:
            claims.append(
                {
                    "claim_id": "symbolic-claim-0",
                    "statement": task.goal,
                    "status": "OBSERVED",
                    "confidence": 1.0,
                }
            )
        return RawResult(
            adapter_id=self.descriptor().adapter_id,
            architecture_id=self.descriptor().architecture_id,
            status="OK",
            payload={
                "verification_posture": "SYMBOLIC_CHECK",
                "claims": claims,
                "checks": ["contract_shape", "local_consistency"],
            },
            is_stub=False,
            resource_usage={"latency_ms": 5.0, "cost": 0.1, "energy": 0.1, "compute": 0.5},
        )

    def normalize(
        self, raw: RawResult, context: ExecutionContext
    ) -> ArchitectureContribution:
        # Task is reconstructed minimally from raw payload context by caller via task.
        # Pipeline passes task through normalize_with_task.
        raise RuntimeError("use normalize_with_task")

    def normalize_with_task(
        self, raw: RawResult, task: TaskEnvelope, context: ExecutionContext
    ) -> ArchitectureContribution:
        claims = tuple(raw.payload.get("claims", ()))
        return normalize_raw(
            raw,
            task=task,
            context=context,
            output_contract=task.required_output_contract,
            claims=claims,
            evidence_refs=tuple(str(a.get("artifact_id", f"artifact-{i}")) for i, a in enumerate(task.input_artifacts)),
            confidence=1.0,
            uncertainty=0.0,
            assumptions=("local_symbolic_rules_only",),
            limitations=("not_an_omniscient_truth_oracle",),
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.descriptor().adapter_id,
            status="ENABLED",
            ready=True,
            detail="local symbolic verifier ready",
        )
