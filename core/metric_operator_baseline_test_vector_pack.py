from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "MetricOperatorBaselineTestVectorPack.v1"
PACK_TYPE = "METRIC_OPERATOR_BASELINE_TEST_VECTOR_PACK"

ALLOWED_OPERATOR_IDS = (
    "WASSERSTEIN", "CHAMFER_DISTANCE", "GEODESIC", "NORM_GEOMETRY", "TRANSPORT", "HYPERVECTOR_BINDING",
    "RESERVOIR_STATE_SPACE", "COUNTERFACTUAL_DIFFUSION", "HEAVY_TAIL", "HYSTERESIS", "STOCHASTIC_GEOMETRY", "TOPOLOGICAL_PRIMITIVES",
)
ALLOWED_VECTOR_TYPES = ("VALID_METADATA_VECTOR", "VALID_ABSENT_VECTOR", "VALID_NOT_COMPUTABLE_VECTOR", "VALID_SHADOW_ONLY_VECTOR")
ALLOWED_COMPUTATION_STATUS = ("DECLARED_ONLY", "METADATA_ONLY", "NOT_IMPLEMENTED", "SHADOW_STUB_ONLY", "NOT_COMPUTABLE")
ALLOWED_INVALID_REASONS = (
    "UNKNOWN_OPERATOR_ID", "EXECUTABLE_REFERENCE_PRESENT", "AUTHORITY_FLAG_TRUE", "FORECAST_INFLUENCE_PRESENT",
    "RUNTIME_MUTATION_PRESENT", "MISSING_REQUIRED_FIELD", "DUPLICATE_OPERATOR_ID",
)

LOCKED_FALSE_FLAGS = (
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted",
)

FORBIDDEN_PROVENANCE_TOKENS = ("executable", "callable", "runtime", "scheduler", "cache", "forecast", "scoring", "metric-value")


class MetricOperatorBaselineTestVectorPackValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def default_validation_policy() -> dict[str, bool]:
    return {
        "validates_metadata_only": True,
        "validates_no_computation": True,
        "validates_no_authority": True,
        "validates_no_runtime_mutation": True,
        "validates_no_forecast_influence": True,
        "validates_registry_alignment": True,
    }


def default_output_contract() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "emits_scores": False,
        "emits_forecast_inputs": False,
        "emits_runtime_controls": False,
        "emits_authority_tokens": False,
        "emits_fixture_metadata": True,
        "emits_validation_expectations": True,
    }


def default_governance_flags() -> dict[str, bool]:
    return {flag: False for flag in LOCKED_FALSE_FLAGS}


_WASSERSTEIN_SHADOW_STUB_EVIDENCE_REFS = [
    "contracts/canon/metric_operator_registry.v1.schema.json",
    "WassersteinExpectedValuesCompleteReview.v1:wasserstein_expected_values_complete_review_001",
]


def default_operator_vectors() -> list[dict[str, Any]]:
    vectors: list[dict[str, Any]] = []
    for idx, operator_id in enumerate(ALLOWED_OPERATOR_IDS, start=1):
        if operator_id == "WASSERSTEIN":
            vectors.append({
                "vector_id": f"vector-{idx:03d}-{operator_id.lower()}",
                "operator_id": operator_id,
                "vector_type": "VALID_SHADOW_ONLY_VECTOR",
                "description": (
                    "Shadow-stub baseline vector for WASSERSTEIN. "
                    "Expected values hardened in P61 complete review "
                    "(5 valid fixtures, expected distances authorized)."
                ),
                "input_descriptor": "shadow_stub_fixture_only_no_runtime_execution",
                "expected_metadata_semantics": (
                    "operator_id declared in registry; expected Wasserstein distances "
                    "hardened (SHADOW_STUB_ONLY); all governance flags false; "
                    "metric emission blocked."
                ),
                "expected_computation_status": "SHADOW_STUB_ONLY",
                "expected_authority_state": "ADVISORY_ONLY",
                "evidence_refs": _WASSERSTEIN_SHADOW_STUB_EVIDENCE_REFS,
            })
        else:
            vectors.append({
                "vector_id": f"vector-{idx:03d}-{operator_id.lower()}",
                "operator_id": operator_id,
                "vector_type": "VALID_METADATA_VECTOR",
                "description": f"Metadata-only baseline vector for {operator_id}.",
                "input_descriptor": "metadata_fixture_only_no_runtime_execution",
                "expected_metadata_semantics": "operator_id declared in registry and governance-locked advisory-only.",
                "expected_computation_status": "NOT_IMPLEMENTED",
                "expected_authority_state": "ADVISORY_ONLY",
                "evidence_refs": ["contracts/canon/metric_operator_registry.v1.schema.json"],
            })
    return vectors


def default_invalid_vectors() -> list[dict[str, str]]:
    return [
        {"vector_id": "invalid-001-unknown-operator", "invalid_reason": "UNKNOWN_OPERATOR_ID", "target_field": "operator_id", "expected_failure": "reject_unknown_operator_id"},
        {"vector_id": "invalid-002-authority-flag", "invalid_reason": "AUTHORITY_FLAG_TRUE", "target_field": "governance_flags.execution_authority", "expected_failure": "authority_lock_must_be_false"},
    ]


def _assert_provenance_safe(value: Any) -> None:
    if isinstance(value, dict):
        for v in value.values():
            _assert_provenance_safe(v)
        return
    if isinstance(value, list):
        for v in value:
            _assert_provenance_safe(v)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if any(token in lowered for token in FORBIDDEN_PROVENANCE_TOKENS):
            raise MetricOperatorBaselineTestVectorPackValidationError("forbidden_provenance_reference_detected")


def validate_metric_operator_baseline_test_vector_pack(pack: dict[str, Any]) -> None:
    required = {
        "schema_version", "pack_id", "pack_type", "source_metric_registry_refs", "operator_vectors", "invalid_vectors",
        "validation_policy", "output_contract", "governance_flags", "provenance", "created_at_utc", "canonical_hash",
    }
    missing = sorted(required - pack.keys())
    if missing:
        raise MetricOperatorBaselineTestVectorPackValidationError(f"missing_required_fields:{missing}")
    if pack["schema_version"] != SCHEMA_VERSION:
        raise MetricOperatorBaselineTestVectorPackValidationError("invalid_schema_version")
    if pack["pack_type"] != PACK_TYPE:
        raise MetricOperatorBaselineTestVectorPackValidationError("invalid_pack_type")
    if not pack["operator_vectors"]:
        raise MetricOperatorBaselineTestVectorPackValidationError("operator_vectors_must_be_non_empty")
    if not pack["invalid_vectors"]:
        raise MetricOperatorBaselineTestVectorPackValidationError("invalid_vectors_must_be_non_empty")

    vector_ids = set()
    for vector in sorted(pack["operator_vectors"], key=lambda v: v["vector_id"]):
        vid = vector["vector_id"]
        if vid in vector_ids:
            raise MetricOperatorBaselineTestVectorPackValidationError("duplicate_vector_id")
        vector_ids.add(vid)
        if vector["operator_id"] not in ALLOWED_OPERATOR_IDS:
            raise MetricOperatorBaselineTestVectorPackValidationError("unknown_operator_id")
        if vector["vector_type"] not in ALLOWED_VECTOR_TYPES:
            raise MetricOperatorBaselineTestVectorPackValidationError("unknown_vector_type")
        if vector["expected_computation_status"] not in ALLOWED_COMPUTATION_STATUS:
            raise MetricOperatorBaselineTestVectorPackValidationError("unknown_expected_computation_status")
        if vector["expected_authority_state"] != "ADVISORY_ONLY":
            raise MetricOperatorBaselineTestVectorPackValidationError("invalid_expected_authority_state")

    for vector in sorted(pack["invalid_vectors"], key=lambda v: v["vector_id"]):
        vid = vector["vector_id"]
        if vid in vector_ids:
            raise MetricOperatorBaselineTestVectorPackValidationError("duplicate_vector_id")
        vector_ids.add(vid)
        if vector["invalid_reason"] not in ALLOWED_INVALID_REASONS:
            raise MetricOperatorBaselineTestVectorPackValidationError("unknown_invalid_reason")

    if pack["validation_policy"] != default_validation_policy():
        raise MetricOperatorBaselineTestVectorPackValidationError("invalid_validation_policy")
    if pack["output_contract"] != default_output_contract():
        raise MetricOperatorBaselineTestVectorPackValidationError("invalid_output_contract")
    for flag in LOCKED_FALSE_FLAGS:
        if pack["governance_flags"].get(flag) is not False:
            raise MetricOperatorBaselineTestVectorPackValidationError(f"authority_lock_must_be_false:{flag}")

    _assert_provenance_safe(pack["provenance"])


def compute_metric_operator_baseline_test_vector_pack_hash(pack: dict[str, Any]) -> str:
    return canonical_hash(_preimage(pack))


def serialize_metric_operator_baseline_test_vector_pack(pack: dict[str, Any]) -> str:
    return canonical_dumps(_finalize(pack)) + "\n"


def build_metric_operator_baseline_test_vector_pack(payload: dict[str, Any]) -> dict[str, Any]:
    ordered_vectors = sorted(payload.get("operator_vectors", []), key=lambda v: v["vector_id"])
    for vector in ordered_vectors:
        vector["evidence_refs"] = sorted(vector.get("evidence_refs", []))
    ordered_invalid = sorted(payload.get("invalid_vectors", []), key=lambda v: v["vector_id"])
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "pack_type": PACK_TYPE,
        "source_metric_registry_refs": sorted(payload.get("source_metric_registry_refs", [])),
        "operator_vectors": ordered_vectors,
        "invalid_vectors": ordered_invalid,
    }
    base["canonical_hash"] = compute_metric_operator_baseline_test_vector_pack_hash(base)
    validate_metric_operator_baseline_test_vector_pack(base)
    return _finalize(base)
