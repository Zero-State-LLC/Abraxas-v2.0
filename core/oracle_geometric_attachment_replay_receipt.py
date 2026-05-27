from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "OracleGeometricAttachmentReplayReceipt.v1"
RECEIPT_TYPE = "ORACLE_GEOMETRIC_ATTACHMENT_REPLAY_RECEIPT"

ALLOWED_SURFACE_TYPES = ("ORACLE_GEOMETRIC_SIGNAL_ATTACHMENT", "ORACLE_SIGNAL_PACKET", "ORACLE_SHADOW_PACKET", "ORACLE_REPLAY_PACKET")
ALLOWED_REPLAY_MODES = ("METADATA_REPLAY", "HASH_STABILITY_REPLAY", "ID_REFERENCE_REPLAY", "NOT_COMPUTABLE_REPLAY")
ALLOWED_INTENDED_LANES = ("SHADOW", "REPLAY", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_OBSERVATION_TYPES = (
    "HASH_STABILITY_OBSERVATION", "ID_REFERENCE_OBSERVATION", "ATTACHMENT_SHAPE_OBSERVATION", "GOVERNANCE_LOCK_OBSERVATION", "NOT_COMPUTABLE_OBSERVATION",
)
ALLOWED_EVIDENCE_REQUIRED = (
    "SOURCE_ATTACHMENT_REF_REQUIRED", "SOURCE_SIGNAL_PACKET_REF_REQUIRED", "TEST_VECTOR_REF_REQUIRED",
    "PROVENANCE_REF_REQUIRED", "REPLAY_VALIDATION_REQUIRED", "NO_RUNTIME_EFFECT_REQUIRED",
)
ALLOWED_IMPLEMENTATION_STATUS = ("DECLARED_ONLY", "METADATA_ONLY", "NOT_IMPLEMENTED", "SHADOW_STUB_ONLY")
LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)
FORBIDDEN_PROVENANCE_TOKENS = (
    "executable", "callable", "runtime", "scheduler", "cache", "forecast", "scoring", "oracle-score", "replay-execution", "route-selection",
)


class OracleGeometricAttachmentReplayReceiptValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_replay_observations() -> list[dict[str, str]]:
    return [
        {"observation_id": "obs-001-attachment-shape", "observation_type": "ATTACHMENT_SHAPE_OBSERVATION", "description": "Attachment metadata shape remains replay-declarative only.", "source_ref": "OracleGeometricSignalAttachment.v1", "expected_replay_semantics": "metadata_schema_shape_stable", "evidence_required": "SOURCE_ATTACHMENT_REF_REQUIRED", "implementation_status": "METADATA_ONLY"},
        {"observation_id": "obs-002-hash-stability", "observation_type": "HASH_STABILITY_OBSERVATION", "description": "Canonical hash is deterministic and excludes canonical_hash field.", "source_ref": "GeometricSignalPacket.v1", "expected_replay_semantics": "canonical_hash_stable_for_same_metadata", "evidence_required": "REPLAY_VALIDATION_REQUIRED", "implementation_status": "DECLARED_ONLY"},
        {"observation_id": "obs-003-governance-lock", "observation_type": "GOVERNANCE_LOCK_OBSERVATION", "description": "Governance locks remain advisory-only and non-authoritative.", "source_ref": "MetricOperatorBaselineTestVectorPack.v1", "expected_replay_semantics": "authority_flags_stay_false", "evidence_required": "NO_RUNTIME_EFFECT_REQUIRED", "implementation_status": "METADATA_ONLY"},
    ]


def default_stability_policy() -> dict[str, bool]:
    return {
        "replay_declared": True,
        "hash_stability_required": True,
        "byte_stability_required": True,
        "deterministic_ordering_required": True,
        "replay_execution_enabled": False,
        "oracle_score_recomputed": False,
    }


def default_oracle_effects() -> dict[str, bool]:
    return {
        "affects_oracle_scores": False, "affects_forecast_probability": False, "affects_forecast_routing": False,
        "affects_outcome_binding": False, "affects_pse_outputs": False, "affects_runtime_routing": False,
        "affects_scheduler": False, "affects_canon": False, "affects_operator_authority": False,
    }


def default_replay_effects() -> dict[str, bool]:
    return {
        "executes_replay": False, "mutates_replay_state": False, "mutates_oracle_packet": False,
        "mutates_source_attachment": False, "mutates_runtime": False, "mutates_scheduler": False, "mutates_routes": False,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_replay_scores": False, "emits_oracle_scores": False, "emits_forecast_inputs": False,
        "emits_runtime_controls": False, "emits_authority_tokens": False, "emits_receipt_metadata": True, "emits_observation_notes": True,
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
            raise OracleGeometricAttachmentReplayReceiptValidationError("forbidden_provenance_reference_detected")


def validate_oracle_geometric_attachment_replay_receipt(receipt: dict[str, Any]) -> None:
    required = {"schema_version","receipt_id","receipt_type","source_attachment_refs","source_signal_packet_refs","source_metric_registry_refs","source_test_vector_pack_refs","replay_scope","replay_observations","stability_policy","oracle_effects","replay_effects","output_contract","governance_flags","provenance","created_at_utc","canonical_hash"}
    missing = sorted(required - receipt.keys())
    if missing:
        raise OracleGeometricAttachmentReplayReceiptValidationError(f"missing_required_fields:{missing}")
    if receipt["schema_version"] != SCHEMA_VERSION:
        raise OracleGeometricAttachmentReplayReceiptValidationError("invalid_schema_version")
    if receipt["receipt_type"] != RECEIPT_TYPE:
        raise OracleGeometricAttachmentReplayReceiptValidationError("invalid_receipt_type")
    scope = receipt["replay_scope"]
    if scope.get("surface_type") not in ALLOWED_SURFACE_TYPES:
        raise OracleGeometricAttachmentReplayReceiptValidationError("unknown_surface_type")
    if scope.get("replay_mode") not in ALLOWED_REPLAY_MODES:
        raise OracleGeometricAttachmentReplayReceiptValidationError("unknown_replay_mode")
    if scope.get("intended_lane") not in ALLOWED_INTENDED_LANES:
        raise OracleGeometricAttachmentReplayReceiptValidationError("unknown_intended_lane")
    observations = receipt["replay_observations"]
    if not observations:
        raise OracleGeometricAttachmentReplayReceiptValidationError("replay_observations_must_be_non_empty")
    ids: set[str] = set()
    for o in sorted(observations, key=lambda x: x["observation_id"]):
        oid = o["observation_id"]
        if oid in ids:
            raise OracleGeometricAttachmentReplayReceiptValidationError("duplicate_observation_id")
        ids.add(oid)
        if o["observation_type"] not in ALLOWED_OBSERVATION_TYPES:
            raise OracleGeometricAttachmentReplayReceiptValidationError("unknown_observation_type")
        if o["evidence_required"] not in ALLOWED_EVIDENCE_REQUIRED:
            raise OracleGeometricAttachmentReplayReceiptValidationError("unknown_evidence_required")
        if o["implementation_status"] not in ALLOWED_IMPLEMENTATION_STATUS:
            raise OracleGeometricAttachmentReplayReceiptValidationError("unknown_implementation_status")

    if receipt["stability_policy"] != default_stability_policy():
        raise OracleGeometricAttachmentReplayReceiptValidationError("invalid_stability_policy")
    if receipt["oracle_effects"] != default_oracle_effects():
        raise OracleGeometricAttachmentReplayReceiptValidationError("invalid_oracle_effects")
    if receipt["replay_effects"] != default_replay_effects():
        raise OracleGeometricAttachmentReplayReceiptValidationError("invalid_replay_effects")
    if receipt["output_contract"] != default_output_contract():
        raise OracleGeometricAttachmentReplayReceiptValidationError("invalid_output_contract")
    for flag in LOCKED_FALSE_FLAGS:
        if receipt["governance_flags"].get(flag) is not False:
            raise OracleGeometricAttachmentReplayReceiptValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(receipt["provenance"])


def compute_oracle_geometric_attachment_replay_receipt_hash(receipt: dict[str, Any]) -> str:
    return canonical_hash(_preimage(receipt))


def serialize_oracle_geometric_attachment_replay_receipt(receipt: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(receipt)) + "\n"


def build_oracle_geometric_attachment_replay_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    observations = sorted(payload.get("replay_observations", default_replay_observations()), key=lambda x: x["observation_id"])
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "source_attachment_refs": sorted(payload.get("source_attachment_refs", [])),
        "source_signal_packet_refs": sorted(payload.get("source_signal_packet_refs", [])),
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "source_test_vector_pack_refs": sorted(payload.get("source_test_vector_pack_refs", [])),
        "replay_observations": observations,
        "stability_policy": payload.get("stability_policy", default_stability_policy()),
        "oracle_effects": payload.get("oracle_effects", default_oracle_effects()),
        "replay_effects": payload.get("replay_effects", default_replay_effects()),
        "output_contract": payload.get("output_contract", default_output_contract()),
    }
    base["canonical_hash"] = compute_oracle_geometric_attachment_replay_receipt_hash(base)
    validate_oracle_geometric_attachment_replay_receipt(base)
    return _finalize(base)
