"""Architecture adapter protocol and shared helpers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.alembic.constants import FINAL_STATUS
from core.alembic.models import (
    AdapterHealth,
    ArchitectureContribution,
    ArchitectureDescriptor,
    ExecutionContext,
    ExecutionEstimate,
    Provenance,
    RawResult,
    TaskEnvelope,
    ValidationResult,
)
from core.alembic.util import det_timestamp, hash_model, make_id


@runtime_checkable
class ArchitectureAdapter(Protocol):
    def descriptor(self) -> ArchitectureDescriptor: ...

    def validate_task(self, task: TaskEnvelope) -> ValidationResult: ...

    def estimate(self, task: TaskEnvelope) -> ExecutionEstimate: ...

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult: ...

    def normalize(
        self, raw: RawResult, context: ExecutionContext
    ) -> ArchitectureContribution: ...

    def health(self) -> AdapterHealth: ...


def normalize_raw(
    raw: RawResult,
    *,
    task: TaskEnvelope,
    context: ExecutionContext,
    output_contract: str,
    claims: tuple[dict, ...] = (),
    evidence_refs: tuple[str, ...] = (),
    confidence: float | None = None,
    uncertainty: float | None = None,
    assumptions: tuple[str, ...] = (),
    limitations: tuple[str, ...] = (),
) -> ArchitectureContribution:
    contribution_id = make_id(
        "contribution",
        task.task_id,
        task.run_id,
        raw.architecture_id,
        raw.adapter_id,
        raw.status,
    )
    status = raw.status
    if raw.is_stub and status == "OK":
        status = "STUB"
    payload = {
        "schema_version": "ArchitectureContribution.v1",
        "contribution_id": contribution_id,
        "task_id": task.task_id,
        "run_id": context.run_id,
        "architecture_id": raw.architecture_id,
        "adapter_id": raw.adapter_id,
        "status": status,
        "output_payload": dict(raw.payload),
        "output_contract": output_contract,
        "claims": list(claims),
        "evidence_refs": list(evidence_refs),
        "uncertainty": uncertainty,
        "confidence": confidence,
        "calibrated_confidence": None,
        "calibration_metadata": {
            "raw_confidence": confidence,
            "calibrated_confidence": None,
            "calibration_model": None,
            "missing_calibration": True,
        },
        "assumptions": list(assumptions),
        "limitations": list(limitations),
        "resource_usage": dict(raw.resource_usage),
        "latency_ms": float(raw.resource_usage.get("latency_ms", 0.0)),
        "cost": float(raw.resource_usage.get("cost", 0.0)),
        "energy_usage": float(raw.resource_usage.get("energy", 0.0)),
        "verification_status": "ABSTAIN",
        "policy_status": "ADVISORY_ONLY",
        "artifact_refs": [],
        "error": raw.error,
        "is_stub": raw.is_stub,
        "lane": context.lane,
        "provenance": {
            "classification": "OBSERVED" if status == "OK" else "INFERRED",
            "producer": raw.adapter_id,
            "producer_version": "1.0.0",
            "notes": FINAL_STATUS,
        },
    }
    contribution = ArchitectureContribution.model_validate(payload)
    digest = hash_model(contribution)
    return contribution.model_copy(
        update={
            "provenance": Provenance(
                classification=contribution.provenance.classification,
                producer=raw.adapter_id,
                producer_version="1.0.0",
                content_hash=digest,
                notes=f"{FINAL_STATUS};ts={det_timestamp(digest)}",
            )
        }
    )
