"""Statistical calibrator adapter — confidence calibration specialist."""

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


def _calibrate(raw_confidence: float) -> float:
    # Simple bounded shrinkage toward 0.5 — explicit, deterministic, not a black box.
    return round(0.5 + 0.5 * (raw_confidence - 0.5), 6)


class StatisticalCalibratorAdapter:
    def descriptor(self) -> ArchitectureDescriptor:
        return ArchitectureDescriptor(
            architecture_id="arch.statistical_calibrator.v1",
            architecture_family="statistical_ml",
            implementation_id="alembic.statistical_calibrator",
            version="1.0.0",
            capabilities=("calibration", "confidence_adjustment"),
            supported_modalities=("structured_json", "text"),
            supported_task_types=("calibrate", "advisory_analysis", "forecast_support"),
            input_contracts=("TaskEnvelope.v1",),
            output_contracts=("ArchitectureContribution.v1",),
            determinism_level="BOUNDED_DETERMINISTIC",
            uncertainty_support=True,
            verification_support=False,
            resource_profile=ResourceProfile(compute_units=0.4, memory_mb=32.0),
            privacy_constraints=("local_only",),
            security_constraints=("no_external_side_effects",),
            governance_class="SPECIALIST",
            authority_class="ADVISORY_ONLY",
            adapter_id="adapter.statistical_calibrator",
            calibration_profile_id="calibration.shrinkage.v1",
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
            expected_latency_ms=4.0,
            expected_cost=0.2,
            expected_energy=0.2,
            expected_compute=0.4,
        )

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult:
        raw_confidence = float(task.constraints.get("raw_confidence", 0.9))
        calibrated = _calibrate(raw_confidence)
        return RawResult(
            adapter_id=self.descriptor().adapter_id,
            architecture_id=self.descriptor().architecture_id,
            status="OK",
            payload={
                "raw_confidence": raw_confidence,
                "calibrated_confidence": calibrated,
                "calibration_model": "shrinkage_v1",
                "claims": [
                    {
                        "claim_id": "calib-claim-0",
                        "statement": f"Calibrated confidence for: {task.goal}",
                        "status": "INFERRED",
                        "confidence": calibrated,
                    }
                ],
            },
            is_stub=False,
            resource_usage={"latency_ms": 4.0, "cost": 0.2, "energy": 0.2, "compute": 0.4},
        )

    def normalize(
        self, raw: RawResult, context: ExecutionContext
    ) -> ArchitectureContribution:
        raise RuntimeError("use normalize_with_task")

    def normalize_with_task(
        self, raw: RawResult, task: TaskEnvelope, context: ExecutionContext
    ) -> ArchitectureContribution:
        contribution = normalize_raw(
            raw,
            task=task,
            context=context,
            output_contract=task.required_output_contract,
            claims=tuple(raw.payload.get("claims", ())),
            confidence=float(raw.payload.get("raw_confidence", 0.0)),
            uncertainty=abs(
                float(raw.payload.get("raw_confidence", 0.0))
                - float(raw.payload.get("calibrated_confidence", 0.0))
            ),
            assumptions=("shrinkage_calibration_applicable",),
            limitations=("not_a_full_reliability_diagram",),
        )
        return contribution.model_copy(
            update={
                "calibrated_confidence": float(raw.payload.get("calibrated_confidence")),
                "calibration_metadata": {
                    "raw_confidence": float(raw.payload.get("raw_confidence")),
                    "calibrated_confidence": float(raw.payload.get("calibrated_confidence")),
                    "calibration_model": "shrinkage_v1",
                    "calibration_model_version": "1.0.0",
                    "sample_count": "NOT_COMPUTABLE",
                    "missing_calibration": False,
                },
            }
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.descriptor().adapter_id,
            status="ENABLED",
            ready=True,
            detail="statistical calibrator ready",
        )
