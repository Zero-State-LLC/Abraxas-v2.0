from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "YggdrasilGeometricRouteReplayReceipt.v1"
RECEIPT_TYPE = "YGGDRASIL_GEOMETRIC_ROUTE_REPLAY_RECEIPT"

ALLOWED_SURFACE_TYPES = (
    "YGGDRASIL_GEOMETRIC_ROUTE_METADATA",
    "ROUTE_GRAPH_METADATA",
    "ROUTE_NODE_METADATA",
    "ROUTE_EDGE_METADATA",
    "SHADOW_ROUTE_ANALYSIS_PACKET",
)
ALLOWED_REPLAY_MODES = (
    "METADATA_REPLAY",
    "HASH_STABILITY_REPLAY",
    "ID_REFERENCE_REPLAY",
    "ROUTE_EFFECT_LOCK_REPLAY",
    "NOT_COMPUTABLE_REPLAY",
)
ALLOWED_INTENDED_LANES = ("SHADOW", "REPLAY", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_OBSERVATION_TYPES = (
    "HASH_STABILITY_OBSERVATION",
    "ID_REFERENCE_OBSERVATION",
    "ROUTE_EFFECT_LOCK_OBSERVATION",
    "METADATA_SHAPE_OBSERVATION",
    "GOVERNANCE_LOCK_OBSERVATION",
    "NOT_COMPUTABLE_OBSERVATION",
)
ALLOWED_EVIDENCE_REQUIRED = (
    "SOURCE_ROUTE_METADATA_REF_REQUIRED",
    "SOURCE_SIGNAL_PACKET_REF_REQUIRED",
    "TEST_VECTOR_REF_REQUIRED",
    "PROVENANCE_REF_REQUIRED",
    "REPLAY_VALIDATION_REQUIRED",
    "NO_RUNTIME_EFFECT_REQUIRED",
)
ALLOWED_IMPLEMENTATION_STATUS = ("DECLARED_ONLY", "METADATA_ONLY", "NOT_IMPLEMENTED", "SHADOW_STUB_ONLY")
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)
FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast", "scoring", "route-selection", "route-scoring", "graph-replay", "replay-execution",
)


class YggdrasilGeometricRouteReplayReceiptValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_replay_observations() -> list[dict[str, str]]:
    return [
        {"observation_id": "obs-001-metadata-shape", "observation_type": "METADATA_SHAPE_OBSERVATION", "description": "Route metadata shape remains advisory metadata only.", "source_ref": "YggdrasilGeometricRouteMetadata.v1", "expected_replay_semantics": "metadata_shape_stable", "evidence_required": "SOURCE_ROUTE_METADATA_REF_REQUIRED", "implementation_status": "METADATA_ONLY"},
        {"observation_id": "obs-002-hash-stability", "observation_type": "HASH_STABILITY_OBSERVATION", "description": "Canonical hash is deterministic with canonical_hash excluded from preimage.", "source_ref": "GeometricSignalPacket.v1", "expected_replay_semantics": "stable_hash_for_identical_metadata", "evidence_required": "REPLAY_VALIDATION_REQUIRED", "implementation_status": "DECLARED_ONLY"},
        {"observation_id": "obs-003-route-lock", "observation_type": "ROUTE_EFFECT_LOCK_OBSERVATION", "description": "Route effects remain false-locked and non-authoritative.", "source_ref": "MetricOperatorBaselineTestVectorPack.v1", "expected_replay_semantics": "route_effects_remain_locked_false", "evidence_required": "NO_RUNTIME_EFFECT_REQUIRED", "implementation_status": "METADATA_ONLY"},
    ]


def default_stability_policy() -> dict[str, bool]:
    return {
        "replay_declared": True,
        "hash_stability_required": True,
        "byte_stability_required": True,
        "deterministic_ordering_required": True,
        "replay_execution_enabled": False,
        "route_graph_recomputed": False,
    }


def default_route_effects() -> dict[str, bool]:
    return {
        "affects_route_selection": False,
        "affects_route_scoring": False,
        "affects_scheduler": False,
        "affects_cache": False,
        "affects_runtime_dispatch": False,
        "affects_forecast": False,
        "affects_operator_authority": False,
    }


def default_replay_effects() -> dict[str, bool]:
    return {
        "executes_replay": False,
        "mutates_replay_state": False,
        "mutates_route_metadata": False,
        "mutates_route_graph": False,
        "mutates_runtime": False,
        "mutates_scheduler": False,
        "mutates_cache": False,
        "mutates_oracle_packet": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_replay_scores": False,
        "emits_route_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_receipt_metadata": True,
        "emits_observation_notes": True,
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
            raise YggdrasilGeometricRouteReplayReceiptValidationError("forbidden_provenance_reference_detected")


def validate_yggdrasil_geometric_route_replay_receipt(receipt: dict[str, Any]) -> None:
    required = {"schema_version", "receipt_id", "receipt_type", "source_route_metadata_refs", "source_signal_packet_refs", "source_metric_registry_refs", "source_test_vector_pack_refs", "replay_scope", "replay_observations", "stability_policy", "route_effects", "replay_effects", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash"}
    missing = sorted(required - receipt.keys())
    if missing:
        raise YggdrasilGeometricRouteReplayReceiptValidationError(f"missing_required_fields:{missing}")
    if receipt["schema_version"] != SCHEMA_VERSION:
        raise YggdrasilGeometricRouteReplayReceiptValidationError("invalid_schema_version")
    if receipt["receipt_type"] != RECEIPT_TYPE:
        raise YggdrasilGeometricRouteReplayReceiptValidationError("invalid_receipt_type")

    scope = receipt["replay_scope"]
    if scope.get("surface_type") not in ALLOWED_SURFACE_TYPES:
        raise YggdrasilGeometricRouteReplayReceiptValidationError("unknown_surface_type")
    if scope.get("replay_mode") not in ALLOWED_REPLAY_MODES:
        raise YggdrasilGeometricRouteReplayReceiptValidationError("unknown_replay_mode")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANES:
        raise YggdrasilGeometricRouteReplayReceiptValidationError("unknown_intended_lane")

    observations = receipt["replay_observations"]
    if not observations:
        raise YggdrasilGeometricRouteReplayReceiptValidationError("replay_observations_must_be_non_empty")
    ids: set[str] = set()
    for o in sorted(observations, key=lambda x: x["observation_id"]):
        oid = o["observation_id"]
        if oid in ids:
            raise YggdrasilGeometricRouteReplayReceiptValidationError("duplicate_observation_id")
        ids.add(oid)
        if o["observation_type"] not in ALLOWED_OBSERVATION_TYPES:
            raise YggdrasilGeometricRouteReplayReceiptValidationError("unknown_observation_type")
        if o["evidence_required"] not in ALLOWED_EVIDENCE_REQUIRED:
            raise YggdrasilGeometricRouteReplayReceiptValidationError("unknown_evidence_required")
        if o["implementation_status"] not in ALLOWED_IMPLEMENTATION_STATUS:
            raise YggdrasilGeometricRouteReplayReceiptValidationError("unknown_implementation_status")

    if receipt["stability_policy"] != default_stability_policy():
        raise YggdrasilGeometricRouteReplayReceiptValidationError("invalid_stability_policy")
    if receipt["route_effects"] != default_route_effects():
        raise YggdrasilGeometricRouteReplayReceiptValidationError("invalid_route_effects")
    if receipt["replay_effects"] != default_replay_effects():
        raise YggdrasilGeometricRouteReplayReceiptValidationError("invalid_replay_effects")
    if receipt["output_contract"] != default_output_contract():
        raise YggdrasilGeometricRouteReplayReceiptValidationError("invalid_output_contract")
    for flag in LOCKED_FALSE_FLAGS:
        if receipt["governance_flags"].get(flag) is not False:
            raise YggdrasilGeometricRouteReplayReceiptValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(receipt["provenance"])


def compute_yggdrasil_geometric_route_replay_receipt_hash(receipt: dict[str, Any]) -> str:
    return canonical_hash(_preimage(receipt))


def serialize_yggdrasil_geometric_route_replay_receipt(receipt: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(receipt)) + "\n"


def build_yggdrasil_geometric_route_replay_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    observations = sorted(payload.get("replay_observations", default_replay_observations()), key=lambda x: x["observation_id"])
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "source_route_metadata_refs": sorted(payload.get("source_route_metadata_refs", [])),
        "source_signal_packet_refs": sorted(payload.get("source_signal_packet_refs", [])),
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "source_test_vector_pack_refs": sorted(payload.get("source_test_vector_pack_refs", [])),
        "replay_observations": observations,
        "stability_policy": payload.get("stability_policy", default_stability_policy()),
        "route_effects": payload.get("route_effects", default_route_effects()),
        "replay_effects": payload.get("replay_effects", default_replay_effects()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_yggdrasil_geometric_route_replay_receipt_hash(base)
    validate_yggdrasil_geometric_route_replay_receipt(base)
    return _finalize(base)
