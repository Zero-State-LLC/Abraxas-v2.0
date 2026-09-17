"""SHADOW Alembic adapter for Sigil-Forge.

Not registered in DEFAULT_ADAPTERS or architecture_registry.json.
Invoke is advisory: forge ingest envelope + inspect chips. No forecast.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.alembic.adapters.base import normalize_raw
from core.alembic.models import (
    AdapterHealth,
    ArchitectureContribution,
    ArchitectureDescriptor,
    ExecutionContext,
    ExecutionEstimate,
    RawResult,
    TaskEnvelope,
    ValidationResult,
)

import forge_ingest

_DESCRIPTOR_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "sigil_forge"
    / "architecture_descriptor.v1.json"
)


def _intent_from_task(task: TaskEnvelope) -> str:
    for art in task.input_artifacts:
        if isinstance(art, dict) and art.get("intent"):
            return str(art["intent"])
    return task.goal


class SigilForgeShadowAdapter:
    def descriptor(self) -> ArchitectureDescriptor:
        raw = json.loads(_DESCRIPTOR_PATH.read_text(encoding="utf-8"))
        return ArchitectureDescriptor.model_validate(raw)

    def validate_task(self, task: TaskEnvelope) -> ValidationResult:
        reasons: list[str] = []
        if task.lane == "FORECAST":
            reasons.append("forecast_lane_denied")
        if "text" not in task.input_modalities and "structured_json" not in task.input_modalities:
            reasons.append("unsupported_modality")
        if not _intent_from_task(task).strip():
            reasons.append("empty_intent")
        return ValidationResult(ok=not reasons, reasons=tuple(reasons))

    def estimate(self, task: TaskEnvelope) -> ExecutionEstimate:
        return ExecutionEstimate(
            feasible=self.validate_task(task).ok,
            expected_latency_ms=15.0,
            expected_cost=0.1,
            expected_energy=0.1,
            expected_compute=0.4,
            reasons=self.validate_task(task).reasons,
        )

    def invoke(self, task: TaskEnvelope, context: ExecutionContext) -> RawResult:
        desc = self.descriptor()
        if context.lane == "FORECAST" or task.lane == "FORECAST":
            return RawResult(
                adapter_id=desc.adapter_id,
                architecture_id=desc.architecture_id,
                status="ABSTAIN",
                payload={"detail": "forecast_lane_denied"},
                error="forecast_lane_denied",
                is_stub=False,
            )
        intent = _intent_from_task(task)
        envelope = forge_ingest.from_intent(intent, request_id=task.task_id)
        projection = forge_ingest.inspect_projection(envelope)
        envelope = {**envelope, "inspect_projection": projection}
        status = "OK" if envelope.get("claim_class") != "NOT_COMPUTABLE" else "PARTIAL"
        return RawResult(
            adapter_id=desc.adapter_id,
            architecture_id=desc.architecture_id,
            status=status,
            payload=envelope,
            is_stub=False,
            resource_usage={
                "latency_ms": 15.0,
                "cost": 0.1,
                "energy": 0.1,
                "compute": 0.4,
            },
        )

    def normalize(
        self, raw: RawResult, context: ExecutionContext
    ) -> ArchitectureContribution:
        raise RuntimeError("use normalize_with_task")

    def normalize_with_task(
        self, raw: RawResult, task: TaskEnvelope, context: ExecutionContext
    ) -> ArchitectureContribution:
        payload = dict(raw.payload)
        claims = (
            {
                "claim_id": "sf-digest",
                "statement": f"intent_digest={payload.get('intent_digest')}",
                "status": "INFERRED",
                "confidence": 1.0,
            },
        )
        return normalize_raw(
            raw,
            task=task,
            context=context,
            output_contract="ForgeIngestEnvelope.v1",
            claims=claims,
            confidence=1.0 if raw.status == "OK" else 0.4,
            uncertainty=0.0,
            assumptions=("public_leaves_only", "nonce_never_serialized"),
            limitations=("not_full_forge_run_root", "not_efficacy", "shadow_only"),
        )

    def health(self) -> AdapterHealth:
        return AdapterHealth(
            adapter_id=self.descriptor().adapter_id,
            status="SHADOW_ONLY",
            ready=True,
            detail="sigil-forge shadow adapter; not on live registry",
        )
