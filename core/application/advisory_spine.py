"""Golden-path advisory orchestration.

Assimilates existing canonical surfaces:
- activation_policy (lane gate)
- validation_service (schema validation)
- alembic (optional architecture routing)
- oracle_bridge (read-only Alembic intake from Oracle candidates)
- canonical hashing for result envelopes

Does not write to disk. Runners/API adapters persist via canonical writers.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from core.alembic.config import default_router_policy
from core.alembic.models import TaskEnvelope
from core.alembic.oracle_bridge import (
    architecture_aware_intake_from_oracle_candidate,
    task_envelope_from_oracle_candidate,
)
from core.alembic.pipeline import execute_advisory
from core.alembic.registry import default_registry
from core.canonical.json import canonical_hash
from core.governance.activation_policy import (
    ActivationLane,
    ActivationRequest,
    evaluate_activation,
)
from core.services.validation_service import validate as validation_validate


class AdvisorySpineRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str
    activation_lane: ActivationLane = ActivationLane.LOCAL_DEV
    input_payload: dict[str, Any] = Field(default_factory=dict)
    schema_ref: str | None = None
    oracle_candidate: dict[str, Any] | None = None
    alembic_task: dict[str, Any] | None = None
    enable_alembic: bool = True
    alembic_mode: Literal["advisory", "shadow"] = "advisory"


def _lane_request(lane: ActivationLane) -> ActivationRequest:
    if lane == ActivationLane.LOCAL_DEV:
        return ActivationRequest(
            lane=lane,
            deterministic_config_present=True,
            test_evidence_present=True,
        )
    if lane == ActivationLane.SANDBOX:
        return ActivationRequest(
            lane=lane,
            isolation_present=True,
            reversibility_present=True,
            bounded_credentials_present=True,
        )
    if lane == ActivationLane.INTERNAL_CANARY:
        return ActivationRequest(
            lane=lane,
            deployment_manifest_present=True,
            observability_present=True,
            rollback_present=True,
            credential_boundary_present=True,
            operator_review_present=True,
        )
    return ActivationRequest(lane=lane)


def run_advisory_spine(request: AdvisorySpineRequest | Mapping[str, Any]) -> dict[str, Any]:
    """Execute the supported advisory golden-path slice (pure)."""
    req = (
        request
        if isinstance(request, AdvisorySpineRequest)
        else AdvisorySpineRequest.model_validate(dict(request))
    )

    activation = evaluate_activation(_lane_request(req.activation_lane))
    if not activation.permitted and req.activation_lane != ActivationLane.EXTERNAL_PRODUCTION:
        return {
            "status": "DENIED",
            "error_class": "ACTIVATION_DENIED",
            "activation": activation.model_dump(mode="python"),
            "run_id": req.run_id,
        }
    if req.activation_lane == ActivationLane.EXTERNAL_PRODUCTION:
        return {
            "status": "OPERATOR_GATE",
            "error_class": "EXTERNAL_PRODUCTION_OPERATOR_GATED",
            "activation": activation.model_dump(mode="python"),
            "run_id": req.run_id,
            "notes": [
                "EXTERNAL_PRODUCTION remains operator-gated; spine does not authorize deploy."
            ],
        }

    validation_result: dict[str, Any] | None = None
    if req.schema_ref is not None:
        validation_result = validation_validate(
            {
                "schema_version": "ValidationServiceRequest.v1",
                "service_id": "validation_service",
                "execution_id": f"advisory-spine:{req.run_id}",
                "schema_ref": req.schema_ref,
                "payload": req.input_payload,
            }
        )
        if validation_result.get("status") == "ERROR" or validation_result.get("valid") is False:
            return {
                "status": "INVALID_INPUT",
                "error_class": "VALIDATION_FAILED",
                "activation": activation.model_dump(mode="python"),
                "validation": validation_result,
                "run_id": req.run_id,
            }

    alembic_result: dict[str, Any] | None = None
    alembic_intake: dict[str, Any] | None = None
    if req.enable_alembic:
        registry = default_registry()
        policy = default_router_policy()
        task: TaskEnvelope | None = None
        if req.alembic_task is not None:
            task = TaskEnvelope.model_validate(req.alembic_task)
        elif req.oracle_candidate is not None:
            alembic_intake = architecture_aware_intake_from_oracle_candidate(
                req.oracle_candidate
            )
            task = task_envelope_from_oracle_candidate(
                req.oracle_candidate,
                run_id=req.run_id,
            )
        if task is not None:
            alembic_result = execute_advisory(
                task,
                registry,
                policy,
                mode=req.alembic_mode,
            )

    advisory = {
        "lane": "SHADOW",
        "forecast_influence": False,
        "authority_mutation": False,
        "summary": "Advisory spine result; not production authority.",
        "input_keys": sorted(req.input_payload.keys()),
        "alembic_invoked": alembic_result is not None,
        "oracle_candidate_present": req.oracle_candidate is not None,
    }

    result = {
        "status": "OK",
        "run_id": req.run_id,
        "activation": activation.model_dump(mode="python"),
        "validation": validation_result,
        "alembic_intake": alembic_intake,
        "alembic": alembic_result,
        "advisory_result": advisory,
        "artifact_class": "AUDIT_EVIDENCE",
        "influences_current_state": False,
        "producer_system": "MIXED",
    }
    result["result_hash"] = canonical_hash(
        {k: v for k, v in result.items() if k != "result_hash"}
    )
    return result
