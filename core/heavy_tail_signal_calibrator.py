from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

INTENDED_LANES = {"SHADOW", "REPLAY", "PROJECTION", "OBSERVATION_ONLY"}
MODEL_FAMILIES = {"POWER_LAW", "PARETO_LIKE", "STABLE_DISTRIBUTION", "SUBEXPONENTIAL", "EXTREME_VALUE", "NON_GAUSSIAN_RESIDUAL", "UNKNOWN_HEAVY_TAIL"}
DECLARED_USES = {"ANOMALY_CONTEXT", "VOLATILITY_CONTEXT", "RARE_EVENT_CONTEXT", "PERTURBATION_CONTEXT", "BASELINE_COMPARISON_CONTEXT", "NOT_COMPUTABLE_CONTEXT"}
EVIDENCE_REQUIRED = {"BASELINE_COMPARATOR_REQUIRED", "SAMPLE_SIZE_DECLARATION_REQUIRED", "REPLAY_VALIDATION_REQUIRED", "PROVENANCE_REF_REQUIRED", "SHADOW_OBSERVATION_REQUIRED", "NO_RUNTIME_EFFECT_REQUIRED"}
IMPLEMENTATION_STATUSES = {"DECLARED_ONLY", "METADATA_ONLY", "NOT_IMPLEMENTED", "SHADOW_STUB_ONLY"}
COMPUTATION_STATUSES = IMPLEMENTATION_STATUSES
_GOV_FALSE = ("production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted")
_POLICY_TRUE = ("observation_only", "no_score_emission", "no_threshold_execution", "no_forecast_influence", "no_runtime_mutation", "no_scheduler_mutation", "no_route_mutation", "no_operator_authority")
_THRESHOLDS = {"thresholds_declared": True, "thresholds_executable": False, "thresholds_affect_routing": False, "thresholds_affect_forecast": False, "thresholds_affect_scheduler": False, "thresholds_affect_runtime": False}
_OUTPUT = {"emits_scores": False, "emits_context_labels": True, "emits_observation_notes": True, "emits_forecast_inputs": False, "emits_runtime_controls": False, "emits_authority_tokens": False}
_FORBIDDEN_TEXT = ("callable", "execute", "runtime", "scheduler", "cache", "forecast", "scoring", "threshold-execution", "route-selection")


def default_tail_model_declarations() -> list[dict[str, Any]]:
    return [
        {
            "model_id": "HTM-POWER-LAW",
            "model_family": "POWER_LAW",
            "description": "Declared heavy-tail context model; metadata-only.",
            "declared_use": "ANOMALY_CONTEXT",
            "evidence_required": ["SHADOW_OBSERVATION_REQUIRED", "NO_RUNTIME_EFFECT_REQUIRED"],
            "implementation_status": "DECLARED_ONLY",
        }
    ]


def default_anomaly_observation_policy() -> dict[str, bool]:
    return {k: True for k in _POLICY_TRUE}


def default_threshold_declarations() -> dict[str, bool]:
    return dict(_THRESHOLDS)


def default_output_contract() -> dict[str, bool]:
    return dict(_OUTPUT)


def compute_heavy_tail_signal_calibrator_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def validate_heavy_tail_signal_calibrator(packet: dict[str, Any]) -> None:
    if packet.get("calibrator_type") != "HEAVY_TAIL_SIGNAL_CALIBRATOR":
        raise ValueError("calibrator_type must be HEAVY_TAIL_SIGNAL_CALIBRATOR")
    scope = packet.get("calibration_scope", {})
    if scope.get("intended_lane") not in INTENDED_LANES:
        raise ValueError("unknown intended_lane")

    declarations = packet.get("tail_model_declarations", [])
    if not declarations:
        raise ValueError("tail_model_declarations must be non-empty")
    model_ids = [d.get("model_id") for d in declarations]
    if len(model_ids) != len(set(model_ids)):
        raise ValueError("duplicate model_id")
    for declaration in declarations:
        if declaration.get("model_family") not in MODEL_FAMILIES:
            raise ValueError("unknown model_family")
        if declaration.get("declared_use") not in DECLARED_USES:
            raise ValueError("unknown declared_use")
        if declaration.get("implementation_status") not in IMPLEMENTATION_STATUSES:
            raise ValueError("unknown implementation_status")
        for evidence in declaration.get("evidence_required", []):
            if evidence not in EVIDENCE_REQUIRED:
                raise ValueError("unknown evidence_required")

    policy = packet.get("anomaly_observation_policy", {})
    for key in _POLICY_TRUE:
        if policy.get(key) is not True:
            raise ValueError(f"anomaly_observation_policy.{key} must be true")

    thresholds = packet.get("threshold_declarations", {})
    for key, expected in _THRESHOLDS.items():
        if thresholds.get(key) is not expected:
            raise ValueError(f"threshold_declarations.{key} must be {str(expected).lower()}")

    output_contract = packet.get("output_contract", {})
    for key, expected in _OUTPUT.items():
        if output_contract.get(key) is not expected:
            raise ValueError(f"output_contract.{key} must be {str(expected).lower()}")

    if packet.get("computation_status") not in COMPUTATION_STATUSES:
        raise ValueError("unknown computation_status")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")

    prov = packet.get("provenance", {})
    blob_parts: list[str] = []
    for key in ("source", "generated_by"):
        value = prov.get(key)
        if isinstance(value, str):
            blob_parts.append(value.lower())
    for item in prov.get("evidence_refs", []):
        if isinstance(item, str):
            blob_parts.append(item.lower())
    blob = " ".join(blob_parts)
    if any(term in blob for term in _FORBIDDEN_TEXT):
        raise ValueError("forbidden executable/runtime/scheduler/forecast/scoring/threshold-execution/route-selection references")

    expected_hash = compute_heavy_tail_signal_calibrator_hash(packet)
    if packet.get("canonical_hash") != expected_hash:
        raise ValueError("canonical_hash mismatch")


def build_heavy_tail_signal_calibrator(*, calibrator_id: str, source_attachment_refs: list[str], source_signal_packet_refs: list[str], source_metric_registry_refs: list[str], calibration_scope: dict[str, str], tail_model_declarations: list[dict[str, Any]], computation_status: str, provenance: dict[str, Any], created_at_utc: str, schema_version: str = "HeavyTailSignalCalibrator.v1") -> dict[str, Any]:
    normalized_models = []
    for model in tail_model_declarations:
        normalized_models.append({**model, "evidence_required": sorted(model.get("evidence_required", []))})
    packet_no_hash = {
        "schema_version": schema_version,
        "calibrator_id": calibrator_id,
        "calibrator_type": "HEAVY_TAIL_SIGNAL_CALIBRATOR",
        "source_attachment_refs": sorted(source_attachment_refs),
        "source_signal_packet_refs": sorted(source_signal_packet_refs),
        "source_metric_registry_refs": sorted(source_metric_registry_refs),
        "calibration_scope": calibration_scope,
        "tail_model_declarations": sorted(normalized_models, key=lambda item: str(item.get("model_id", ""))),
        "anomaly_observation_policy": default_anomaly_observation_policy(),
        "threshold_declarations": default_threshold_declarations(),
        "output_contract": default_output_contract(),
        "computation_status": computation_status,
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    packet = {**packet_no_hash, "canonical_hash": compute_heavy_tail_signal_calibrator_hash(packet_no_hash)}
    validate_heavy_tail_signal_calibrator(packet)
    return json.loads(canonical_dumps(packet))


def serialize_heavy_tail_signal_calibrator(packet: dict[str, Any]) -> str:
    validate_heavy_tail_signal_calibrator(packet)
    return canonical_dumps(packet) + "\n"
