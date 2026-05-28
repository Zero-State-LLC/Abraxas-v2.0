from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "OracleGeometricAttachmentStabilizationWindow.v1"
WINDOW_TYPE = "ORACLE_GEOMETRIC_ATTACHMENT_STABILIZATION_WINDOW"

ALLOWED_SURFACE_TYPES = (
    "ORACLE_GEOMETRIC_SIGNAL_ATTACHMENT",
    "ORACLE_GEOMETRIC_ATTACHMENT_REPLAY_RECEIPT",
    "ORACLE_SHADOW_ATTACHMENT_CONTEXT",
    "ORACLE_REPLAY_CONTEXT",
)
ALLOWED_WINDOW_MODES = (
    "STABILIZATION_DECLARED_ONLY",
    "HASH_STABILITY_WINDOW",
    "BYTE_STABILITY_WINDOW",
    "REPLAY_OBSERVATION_WINDOW",
    "NOT_COMPUTABLE_WINDOW",
)
ALLOWED_INTENDED_LANES = ("SHADOW", "REPLAY", "OBSERVATION_ONLY")
ALLOWED_REQUIREMENT_TYPES = (
    "HASH_STABILITY_REQUIREMENT",
    "BYTE_STABILITY_REQUIREMENT",
    "ID_REFERENCE_REQUIREMENT",
    "GOVERNANCE_LOCK_REQUIREMENT",
    "NO_ORACLE_MUTATION_REQUIREMENT",
    "NO_FORECAST_INFLUENCE_REQUIREMENT",
    "NOT_COMPUTABLE_REQUIREMENT",
)
ALLOWED_EVIDENCE_REQUIRED = (
    "SOURCE_ATTACHMENT_REF_REQUIRED",
    "SOURCE_REPLAY_RECEIPT_REF_REQUIRED",
    "TEST_VECTOR_REF_REQUIRED",
    "PROVENANCE_REF_REQUIRED",
    "STABILITY_OBSERVATION_REQUIRED",
    "NO_RUNTIME_EFFECT_REQUIRED",
)
ALLOWED_IMPLEMENTATION_STATUS = (
    "DECLARED_ONLY",
    "METADATA_ONLY",
    "NOT_IMPLEMENTED",
    "SHADOW_STUB_ONLY",
)
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)
FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast", "scoring", "oracle-score", "replay-execution", "stabilization-execution", "route-selection",
)


class OracleGeometricAttachmentStabilizationWindowValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_observation_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "req-001-hash-stability",
            "requirement_type": "HASH_STABILITY_REQUIREMENT",
            "description": "Window is declaration-only and must keep attachment/receipt hash stability under deterministic canonical serialization.",
            "evidence_required": "STABILITY_OBSERVATION_REQUIRED",
            "pass_condition": "canonical_hash_replay_match_required",
            "implementation_status": "DECLARED_ONLY",
        }
    ]


def default_stability_expectations() -> dict[str, bool]:
    return {
        "hash_stability_required": True,
        "byte_stability_required": True,
        "deterministic_ordering_required": True,
        "governance_lock_stability_required": True,
        "replay_receipt_consistency_required": True,
        "oracle_score_stability_required": False,
        "forecast_probability_stability_required": False,
    }


def default_window_constraints() -> dict[str, bool]:
    return {
        "stabilization_executed": False,
        "replay_executed": False,
        "oracle_packet_mutated": False,
        "oracle_score_recomputed": False,
        "forecast_probability_updated": False,
        "runtime_mutated": False,
        "scheduler_mutated": False,
        "canon_mutated": False,
    }


def default_oracle_effects() -> dict[str, bool]:
    return {
        "affects_oracle_scores": False,
        "affects_forecast_probability": False,
        "affects_forecast_routing": False,
        "affects_outcome_binding": False,
        "affects_pse_outputs": False,
        "affects_runtime_routing": False,
        "affects_scheduler": False,
        "affects_canon": False,
        "affects_operator_authority": False,
    }


def default_replay_effects() -> dict[str, bool]:
    return {
        "executes_replay": False,
        "mutates_replay_state": False,
        "mutates_oracle_packet": False,
        "mutates_source_attachment": False,
        "mutates_runtime": False,
        "mutates_scheduler": False,
        "mutates_routes": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_stability_scores": False,
        "emits_oracle_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_window_metadata": True,
        "emits_observation_requirements": True,
    }


def _assert_provenance_safe(value: Any) -> None:
    if isinstance(value, dict):
        for v in value.values():
            _assert_provenance_safe(v)
    elif isinstance(value, list):
        for v in value:
            _assert_provenance_safe(v)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise OracleGeometricAttachmentStabilizationWindowValidationError("forbidden_provenance_reference_detected")


def validate_oracle_geometric_attachment_stabilization_window(packet: dict[str, Any]) -> None:
    required = {
        "schema_version", "window_id", "window_type", "source_attachment_refs", "source_replay_receipt_refs",
        "source_signal_packet_refs", "source_metric_registry_refs", "stabilization_scope", "observation_requirements",
        "stability_expectations", "window_constraints", "oracle_effects", "replay_effects", "output_contract",
        "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise OracleGeometricAttachmentStabilizationWindowValidationError(f"missing_required_fields:{missing}")
    if packet["schema_version"] != SCHEMA_VERSION:
        raise OracleGeometricAttachmentStabilizationWindowValidationError("invalid_schema_version")
    if packet["window_type"] != WINDOW_TYPE:
        raise OracleGeometricAttachmentStabilizationWindowValidationError("invalid_window_type")

    scope = packet["stabilization_scope"]
    if scope.get("surface_type") not in ALLOWED_SURFACE_TYPES:
        raise OracleGeometricAttachmentStabilizationWindowValidationError("unknown_surface_type")
    if scope.get("window_mode") not in ALLOWED_WINDOW_MODES:
        raise OracleGeometricAttachmentStabilizationWindowValidationError("unknown_window_mode")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANES:
        raise OracleGeometricAttachmentStabilizationWindowValidationError("unknown_intended_lane")

    requirements = packet["observation_requirements"]
    if not requirements:
        raise OracleGeometricAttachmentStabilizationWindowValidationError("observation_requirements_must_be_non_empty")

    seen: set[str] = set()
    for req in sorted(requirements, key=lambda x: x["requirement_id"]):
        rid = req["requirement_id"]
        if rid in seen:
            raise OracleGeometricAttachmentStabilizationWindowValidationError("duplicate_requirement_id")
        seen.add(rid)
        if req["requirement_type"] not in ALLOWED_REQUIREMENT_TYPES:
            raise OracleGeometricAttachmentStabilizationWindowValidationError("unknown_requirement_type")
        if req["evidence_required"] not in ALLOWED_EVIDENCE_REQUIRED:
            raise OracleGeometricAttachmentStabilizationWindowValidationError("unknown_evidence_required")
        if req["implementation_status"] not in ALLOWED_IMPLEMENTATION_STATUS:
            raise OracleGeometricAttachmentStabilizationWindowValidationError("unknown_implementation_status")

    if packet["stability_expectations"] != default_stability_expectations():
        raise OracleGeometricAttachmentStabilizationWindowValidationError("invalid_stability_expectations")
    if packet["window_constraints"] != default_window_constraints():
        raise OracleGeometricAttachmentStabilizationWindowValidationError("invalid_window_constraints")
    if packet["oracle_effects"] != default_oracle_effects():
        raise OracleGeometricAttachmentStabilizationWindowValidationError("invalid_oracle_effects")
    if packet["replay_effects"] != default_replay_effects():
        raise OracleGeometricAttachmentStabilizationWindowValidationError("invalid_replay_effects")
    if packet["output_contract"] != default_output_contract():
        raise OracleGeometricAttachmentStabilizationWindowValidationError("invalid_output_contract")

    for flag in LOCKED_FALSE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise OracleGeometricAttachmentStabilizationWindowValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(packet["provenance"])


def compute_oracle_geometric_attachment_stabilization_window_hash(packet: dict[str, Any]) -> str:
    return canonical_hash(_preimage(packet))


def serialize_oracle_geometric_attachment_stabilization_window(packet: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_oracle_geometric_attachment_stabilization_window(payload: dict[str, Any]) -> dict[str, Any]:
    requirements = sorted(payload.get("observation_requirements", default_observation_requirements()), key=lambda x: x["requirement_id"])
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "window_type": WINDOW_TYPE,
        "source_attachment_refs": sorted(payload.get("source_attachment_refs", [])),
        "source_replay_receipt_refs": sorted(payload.get("source_replay_receipt_refs", [])),
        "source_signal_packet_refs": sorted(payload.get("source_signal_packet_refs", [])),
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "observation_requirements": requirements,
        "stability_expectations": payload.get("stability_expectations", default_stability_expectations()),
        "window_constraints": payload.get("window_constraints", default_window_constraints()),
        "oracle_effects": payload.get("oracle_effects", default_oracle_effects()),
        "replay_effects": payload.get("replay_effects", default_replay_effects()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_oracle_geometric_attachment_stabilization_window_hash(base)
    validate_oracle_geometric_attachment_stabilization_window(base)
    return _finalize(base)
