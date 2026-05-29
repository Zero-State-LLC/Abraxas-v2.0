from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinTestVectorComputationActualPrGate.v1"
GATE_TYPE = "WASSERSTEIN_TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH = (
    "3728f4da6b52d887fedb35c428361c6979ed4cc1654d413259de58277dc6b5d2"
)
SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH = (
    "6efad6ecfbfc4ff186496d4f49871a52adbce5015b7222fa1dbacf6e88d92eea"
)
SOURCE_OPERATOR_DECISION_ID = (
    "WASSERSTEIN_COMPUTATION_OPERATOR_DECISION_2026_05_29_001"
)
SOURCE_OPERATOR_DECISION_HASH = (
    "3fd89a4d9b9e675234205054c62e284a9bf80a004b7d51b5ff96a97ef532974b"
)
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_GATE_STAGE = (
    "TEST_VECTOR_COMPUTATION_ACTUAL_PR_GATE_ONLY",
    "BLOCKED_PENDING_OPERATOR_DECISION",
)

FORBIDDEN = (
    "runtime",
    "scheduler",
    "cache",
    "forecast",
    "scoring",
    "metric-value",
    "wasserstein-distance",
    "expected-wasserstein",
    "earth-mover",
    "ot-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "sinkhorn-kernel",
    "authority-flag",
)


class WassersteinTestVectorComputationActualPrGateError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Default sub-structures
# ---------------------------------------------------------------------------


def default_operator_decision_verification() -> dict[str, Any]:
    return {
        "operator_decision_id": SOURCE_OPERATOR_DECISION_ID,
        "operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "operator_id_verified": "Daniel Meyer",
        "decision_verified": "approve_wasserstein_test_vector_computation",
        "computation_lane_verified": "TEST_VECTOR_COMPUTATION_ONLY",
        "upstream_review_hash_verified": SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH,
        "source_schema_validation_complete_review_hash": (
            SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
        ),
        "verification_status": "VERIFIED",
    }


def default_authorized_computation_scope() -> dict[str, Any]:
    return {
        "scope": "TEST_VECTOR_COMPUTATION_ONLY",
        "authorized_lanes": ["SHADOW"],
        "fixture_count": 14,
        "no_forecast_influence": True,
        "no_runtime_binding": True,
        "no_p43_surface_lane_output": True,
        "no_production_activation": True,
        "computation_scope_status": "AUTHORIZED",
    }


def default_authorized_fixture_manifest() -> dict[str, Any]:
    return {
        "total_authorized_fixtures": 14,
        "valid_fixtures": 5,
        "invalid_fixtures": 5,
        "not_computable_fixtures": 4,
        "source_gate_hash": SOURCE_GATE_HASH,
        "manifest_status": "AUTHORIZED_FOR_BOUNDED_COMPUTATION",
    }


def default_computation_constraints() -> dict[str, Any]:
    return {
        "bounded_to_validated_fixtures_only": True,
        "shadow_lane_only": True,
        "no_metric_value_emission": True,
        "no_expected_distance_addition": True,
        "no_p43_surface_lanes": True,
        "no_production_activation": True,
        "no_canon_promotion": True,
        "no_runtime_mutation": True,
        "no_execution_authority": True,
        "no_inference_authority": True,
        "constraint_status": "ACTIVE",
    }


def default_blocked_scopes() -> dict[str, bool]:
    return {
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "test_vector_computation_actual_pr_gate_only": True,
        "wasserstein_computation_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


# ---------------------------------------------------------------------------
# Safety scanner
# ---------------------------------------------------------------------------


def _assert_safe(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _assert_safe(x)
    elif isinstance(v, list):
        for x in v:
            _assert_safe(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise WassersteinTestVectorComputationActualPrGateError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_test_vector_computation_actual_pr_gate(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "gate_id",
        "gate_type",
        "operator_id",
        "source_operator_decision_id",
        "source_operator_decision_hash",
        "source_computation_authorization_review_hash",
        "source_fixture_schema_validation_complete_review_hash",
        "intended_lane",
        "gate_stage",
        "operator_decision_verification",
        "authorized_computation_scope",
        "authorized_fixture_manifest",
        "computation_constraints",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinTestVectorComputationActualPrGateError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_schema_version"
        )
    if packet["gate_type"] != GATE_TYPE:
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_gate_type"
        )
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinTestVectorComputationActualPrGateError(
            "unknown_operator_id"
        )
    if packet["source_operator_decision_id"] != SOURCE_OPERATOR_DECISION_ID:
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_source_operator_decision_id"
        )
    if packet["source_operator_decision_hash"] != SOURCE_OPERATOR_DECISION_HASH:
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_source_operator_decision_hash"
        )
    if (
        packet["source_computation_authorization_review_hash"]
        != SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH
    ):
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_source_computation_authorization_review_hash"
        )
    if (
        packet["source_fixture_schema_validation_complete_review_hash"]
        != SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
    ):
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_source_fixture_schema_validation_complete_review_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinTestVectorComputationActualPrGateError(
            "unknown_intended_lane"
        )
    if packet["gate_stage"] not in ALLOWED_GATE_STAGE:
        raise WassersteinTestVectorComputationActualPrGateError(
            "unknown_gate_stage"
        )

    odv = packet["operator_decision_verification"]
    if odv.get("operator_decision_id") != SOURCE_OPERATOR_DECISION_ID:
        raise WassersteinTestVectorComputationActualPrGateError(
            "operator_decision_id_mismatch"
        )
    if odv.get("operator_decision_hash") != SOURCE_OPERATOR_DECISION_HASH:
        raise WassersteinTestVectorComputationActualPrGateError(
            "operator_decision_hash_mismatch"
        )
    if odv.get("verification_status") != "VERIFIED":
        raise WassersteinTestVectorComputationActualPrGateError(
            "operator_decision_not_verified"
        )
    if (
        odv.get("upstream_review_hash_verified")
        != SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH
    ):
        raise WassersteinTestVectorComputationActualPrGateError(
            "upstream_review_hash_mismatch"
        )

    acs = packet["authorized_computation_scope"]
    if acs.get("computation_scope_status") != "AUTHORIZED":
        raise WassersteinTestVectorComputationActualPrGateError(
            "computation_scope_not_authorized"
        )
    if acs.get("fixture_count") != 14:
        raise WassersteinTestVectorComputationActualPrGateError(
            "computation_scope_fixture_count_mismatch"
        )
    if "SHADOW" not in acs.get("authorized_lanes", []):
        raise WassersteinTestVectorComputationActualPrGateError(
            "shadow_lane_not_in_authorized_lanes"
        )

    afm = packet["authorized_fixture_manifest"]
    if afm.get("total_authorized_fixtures") != 14:
        raise WassersteinTestVectorComputationActualPrGateError(
            "authorized_fixture_count_mismatch"
        )
    if afm.get("source_gate_hash") != SOURCE_GATE_HASH:
        raise WassersteinTestVectorComputationActualPrGateError(
            "authorized_fixture_gate_hash_mismatch"
        )
    if afm.get("manifest_status") != "AUTHORIZED_FOR_BOUNDED_COMPUTATION":
        raise WassersteinTestVectorComputationActualPrGateError(
            "authorized_fixture_manifest_not_ready"
        )

    cc = packet["computation_constraints"]
    if not cc.get("bounded_to_validated_fixtures_only"):
        raise WassersteinTestVectorComputationActualPrGateError(
            "computation_not_bounded_to_fixtures"
        )
    if not cc.get("no_metric_value_emission"):
        raise WassersteinTestVectorComputationActualPrGateError(
            "metric_value_emission_not_blocked"
        )
    if not cc.get("shadow_lane_only"):
        raise WassersteinTestVectorComputationActualPrGateError(
            "shadow_lane_only_not_set"
        )

    al = packet["authority_locks"]
    if al.get("wasserstein_computation_authorized") is not True:
        raise WassersteinTestVectorComputationActualPrGateError(
            "wasserstein_computation_authorized_must_be_true"
        )
    if al.get("test_vector_computation_actual_pr_gate_only") is not True:
        raise WassersteinTestVectorComputationActualPrGateError(
            "test_vector_computation_actual_pr_gate_only_must_be_true"
        )
    if al.get("emits_metric_values") is not False:
        raise WassersteinTestVectorComputationActualPrGateError(
            "emits_metric_values_must_be_false"
        )
    if al.get("execution_authority") is not False:
        raise WassersteinTestVectorComputationActualPrGateError(
            "execution_authority_must_be_false"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_authority_locks"
        )
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_blocked_scopes"
        )
    if (
        packet["operator_decision_verification"]
        != default_operator_decision_verification()
    ):
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_operator_decision_verification"
        )
    if (
        packet["authorized_computation_scope"]
        != default_authorized_computation_scope()
    ):
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_authorized_computation_scope"
        )
    if (
        packet["authorized_fixture_manifest"]
        != default_authorized_fixture_manifest()
    ):
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_authorized_fixture_manifest"
        )
    if packet["computation_constraints"] != default_computation_constraints():
        raise WassersteinTestVectorComputationActualPrGateError(
            "invalid_computation_constraints"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_test_vector_computation_actual_pr_gate_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_test_vector_computation_actual_pr_gate(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_test_vector_computation_actual_pr_gate(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "gate_type": GATE_TYPE,
        "operator_id": OPERATOR_ID,
        "source_operator_decision_id": SOURCE_OPERATOR_DECISION_ID,
        "source_operator_decision_hash": SOURCE_OPERATOR_DECISION_HASH,
        "source_computation_authorization_review_hash": (
            SOURCE_COMPUTATION_AUTHORIZATION_REVIEW_HASH
        ),
        "source_fixture_schema_validation_complete_review_hash": (
            SOURCE_SCHEMA_VALIDATION_COMPLETE_REVIEW_HASH
        ),
        "operator_decision_verification": payload.get(
            "operator_decision_verification",
            default_operator_decision_verification(),
        ),
        "authorized_computation_scope": payload.get(
            "authorized_computation_scope",
            default_authorized_computation_scope(),
        ),
        "authorized_fixture_manifest": payload.get(
            "authorized_fixture_manifest",
            default_authorized_fixture_manifest(),
        ),
        "computation_constraints": payload.get(
            "computation_constraints",
            default_computation_constraints(),
        ),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = (
        compute_wasserstein_test_vector_computation_actual_pr_gate_hash(base)
    )
    validate_wasserstein_test_vector_computation_actual_pr_gate(base)
    return _finalize(base)
