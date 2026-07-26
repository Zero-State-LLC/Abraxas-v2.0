"""Graph / memetic-analysis specialist adapter (local heuristic)."""

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


class GraphMemeticAdapter:
    def descriptor(self) -> ArchitectureDescriptor:
        return ArchitectureDescriptor(
            architecture_id="arch.graph_memetic.v1",
            architecture_family="graph_neural",
            implementation_id="alembic.graph_memetic_heuristic",
            version="1.0.0",
            capabilities=("graph_relation_extract", "memetic_cluster_hint"),
            supported_modalities=("structured_json", "text"),
            supported_task_types=("memetic_analysis", "graph_analysis", "advisory_analysis"),
            input_contracts=("TaskEnvelope.v1",),
            output_contracts=("ArchitectureContribution.v1",),
            determinism_level="BOUNDED_DETERMINISTIC",
            uncertainty_support=True,
            verification_support=False,
            resource_profile=ResourceProfile(compute_units=1.0, memory_mb=64.0),
            privacy_constraints=("local_only",),
            security_constraints=("no_external_side_effects",),
            governance_class="SPECIALIST",
            authority_class="ADVISORY_ONLY",
            adapter_id="adapter.graph_memetic",
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
            expected_latency_ms=8.0,
            expected_cost=0.4,
            expected_energy=0.4,
            expected_compute=1.0,
        )

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult:
        nodes = sorted({task.goal, *(str(a.get("statement", "")) for a in task.input_artifacts)})
        edges = [
            {"source": nodes[i], "target": nodes[i + 1], "relation": "co_mentioned"}
            for i in range(max(0, len(nodes) - 1))
        ]
        return RawResult(
            adapter_id=self.descriptor().adapter_id,
            architecture_id=self.descriptor().architecture_id,
            status="OK",
            payload={
                "graph": {"nodes": nodes, "edges": edges},
                "claims": [
                    {
                        "claim_id": "graph-claim-0",
                        "statement": f"Graph heuristic over {len(nodes)} nodes for: {task.goal}",
                        "status": "INFERRED",
                        "confidence": 0.55,
                    }
                ],
            },
            is_stub=False,
            resource_usage={"latency_ms": 8.0, "cost": 0.4, "energy": 0.4, "compute": 1.0},
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
            confidence=0.55,
            uncertainty=0.45,
            assumptions=("co_mention_implies_weak_relation",),
            limitations=("not_a_trained_gnn",),
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.descriptor().adapter_id,
            status="ENABLED",
            ready=True,
            detail="graph memetic heuristic ready",
        )
