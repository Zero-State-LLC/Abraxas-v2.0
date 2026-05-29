from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinExpectedValuesGate.v1"
GATE_TYPE = "WASSERSTEIN_EXPECTED_VALUES_GATE"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_COMPUTATION_RECEIPT_HASH = (
    "010da2fdf344cfc32d2e9accc0ef19e96644fdd69974928ca047f87e4daf6188"
)
SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH = (
    "8d37688fb2f4c0337cdfb2cf2ab3fb491138cbd7c1f66eca87b476bd45a60079"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = (
    "EXPECTED_VALUES_GATE_ONLY",
    "BLOCKED_PENDING_GATE",
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

# Canonical-rounded shadow_transport_value per valid fixture_id
SHADOW_TRANSPORT_VALUES: dict[str, float] = {
    "valid-001": 0.4,
    "valid-002": 0.4,
    "valid-003": 0.866025,
    "valid-004": 0.2,
    "valid-005": 0.0,
}

VALID_FIXTURE_GROUPS: dict[str, str] = {
    "valid-001": "DISTRIBUTION_PAIR_SCHEMA",
    "valid-002": "WEIGHTED_HISTOGRAM_SCHEMA",
    "valid-003": "REFERENCE_VECTOR_SCHEMA",
    "valid-004": "GROUND_METRIC_SCHEMA",
    "valid-005": "DEGENERATE_DISTRIBUTION_SCHEMA",
}

INVALID_FIXTURE_IDS = [
    "invalid-001",
    "invalid-002",
    "invalid-003",
    "invalid-004",
    "invalid-005",
]

NC_FIXTURE_IDS = ["nc-001", "nc-002", "nc-003", "nc-004"]


class WassersteinExpectedValuesGateError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Gate sub-structures
# ---------------------------------------------------------------------------


def build_valid_fixture_result_review() -> dict[str, Any]:
    fixture_reviews = []
    for fid in sorted(SHADOW_TRANSPORT_VALUES):
        fixture_reviews.append(
            {
                "fixture_id": fid,
                "fixture_group": VALID_FIXTURE_GROUPS[fid],
                "shadow_transport_value_verified": True,
                "shadow_transport_value": SHADOW_TRANSPORT_VALUES[fid],
                "eligible_for_expected_distance": True,
                "expected_distance_scope": "SHADOW_ONLY",
                "gate_status": "AUTHORIZED",
            }
        )
    return {
        "total_reviewed": 5,
        "all_shadow_transport_values_verified": True,
        "all_eligible_for_expected_distance": True,
        "expected_distance_scope": "SHADOW_ONLY",
        "fixture_reviews": fixture_reviews,
        "gate_status": "VALID_FIXTURES_AUTHORIZED_FOR_EXPECTED_VALUES",
    }


def build_expected_value_authorization_scope() -> dict[str, Any]:
    return {
        "authorized_fixture_ids": sorted(SHADOW_TRANSPORT_VALUES),
        "authorized_action": "ADD_EXPECTED_WASSERSTEIN_DISTANCE",
        "scope": "VALID_FIXTURES_ONLY",
        "fixture_count": 5,
        "shadow_only": True,
        "no_metric_emission": True,
        "no_forecast_influence": True,
        "no_p43_output": True,
        "no_runtime_binding": True,
        "authorization_status": "EXPECTED_WASSERSTEIN_DISTANCES_AUTHORIZED",
    }


def build_rejected_input_exclusion_scope() -> dict[str, Any]:
    return {
        "invalid_fixture_ids": INVALID_FIXTURE_IDS,
        "nc_fixture_ids": NC_FIXTURE_IDS,
        "invalid_count": 5,
        "not_computable_count": 4,
        "exclusion_reason": "REJECTED_INPUT_NOT_ELIGIBLE_FOR_EXPECTED_VALUES",
        "expected_distance_excluded": True,
        "exclusion_status": "REJECTED_INPUT_FIXTURES_EXCLUDED",
    }


def build_metric_emission_block() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "block_status": "BLOCKED",
        "no_runtime_emission": True,
        "no_p43_surface_output": True,
        "block_reason": "expected_values_gate_is_shadow_only_advisory",
    }


def build_forecast_influence_block() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "block_status": "BLOCKED",
        "no_p43_output": True,
        "no_forecast_binding": True,
        "block_reason": "expected_values_gate_does_not_activate_forecast_lane",
    }


def build_p43_surface_lane_block() -> dict[str, Any]:
    return {
        "p43_surface_lanes_authorized": False,
        "block_status": "BLOCKED",
        "no_runtime_binding": True,
        "no_p43_lanes_opened": True,
        "block_reason": "expected_values_gate_does_not_open_p43_surface_lanes",
    }


# ---------------------------------------------------------------------------
# Default sub-structures
# ---------------------------------------------------------------------------


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
        "expected_values_gate_only": True,
        "expected_wasserstein_distances_authorized": True,
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
        raise WassersteinExpectedValuesGateError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_expected_values_gate(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "gate_id",
        "gate_type",
        "operator_id",
        "source_computation_receipt_hash",
        "source_computation_complete_review_hash",
        "intended_lane",
        "gate_stage",
        "valid_fixture_result_review",
        "expected_value_authorization_scope",
        "rejected_input_exclusion_scope",
        "metric_emission_block",
        "forecast_influence_block",
        "p43_surface_lane_block",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinExpectedValuesGateError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinExpectedValuesGateError("invalid_schema_version")
    if packet["gate_type"] != GATE_TYPE:
        raise WassersteinExpectedValuesGateError("invalid_gate_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinExpectedValuesGateError("unknown_operator_id")
    if packet["source_computation_receipt_hash"] != SOURCE_COMPUTATION_RECEIPT_HASH:
        raise WassersteinExpectedValuesGateError(
            "invalid_source_computation_receipt_hash"
        )
    if (
        packet["source_computation_complete_review_hash"]
        != SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH
    ):
        raise WassersteinExpectedValuesGateError(
            "invalid_source_computation_complete_review_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinExpectedValuesGateError("unknown_intended_lane")
    if packet["gate_stage"] not in ALLOWED_STAGE:
        raise WassersteinExpectedValuesGateError("unknown_gate_stage")

    vfr = packet["valid_fixture_result_review"]
    if vfr.get("gate_status") != "VALID_FIXTURES_AUTHORIZED_FOR_EXPECTED_VALUES":
        raise WassersteinExpectedValuesGateError(
            "valid_fixture_result_review_not_authorized"
        )
    if vfr.get("total_reviewed") != 5:
        raise WassersteinExpectedValuesGateError(
            "valid_fixture_result_review_count_mismatch"
        )
    if not vfr.get("all_eligible_for_expected_distance"):
        raise WassersteinExpectedValuesGateError(
            "not_all_valid_fixtures_eligible_for_expected_distance"
        )

    evas = packet["expected_value_authorization_scope"]
    if evas.get("authorization_status") != "EXPECTED_WASSERSTEIN_DISTANCES_AUTHORIZED":
        raise WassersteinExpectedValuesGateError(
            "expected_value_authorization_scope_not_authorized"
        )
    if evas.get("scope") != "VALID_FIXTURES_ONLY":
        raise WassersteinExpectedValuesGateError(
            "expected_value_authorization_scope_not_valid_fixtures_only"
        )
    if not evas.get("shadow_only"):
        raise WassersteinExpectedValuesGateError(
            "expected_value_authorization_not_shadow_only"
        )
    if not evas.get("no_metric_emission"):
        raise WassersteinExpectedValuesGateError(
            "expected_value_authorization_allows_metric_emission"
        )

    ries = packet["rejected_input_exclusion_scope"]
    if ries.get("exclusion_status") != "REJECTED_INPUT_FIXTURES_EXCLUDED":
        raise WassersteinExpectedValuesGateError(
            "rejected_input_exclusion_scope_not_excluded"
        )
    if not ries.get("expected_distance_excluded"):
        raise WassersteinExpectedValuesGateError(
            "rejected_input_fixtures_expected_distance_not_excluded"
        )

    meb = packet["metric_emission_block"]
    if meb.get("block_status") != "BLOCKED":
        raise WassersteinExpectedValuesGateError("metric_emission_not_blocked")
    if meb.get("emits_metric_values") is not False:
        raise WassersteinExpectedValuesGateError(
            "metric_emission_block_emits_metric_values_not_false"
        )

    fib = packet["forecast_influence_block"]
    if fib.get("block_status") != "BLOCKED":
        raise WassersteinExpectedValuesGateError("forecast_influence_not_blocked")
    if fib.get("forecast_influence") is not False:
        raise WassersteinExpectedValuesGateError(
            "forecast_influence_block_forecast_influence_not_false"
        )

    p43b = packet["p43_surface_lane_block"]
    if p43b.get("block_status") != "BLOCKED":
        raise WassersteinExpectedValuesGateError("p43_surface_lane_not_blocked")
    if p43b.get("p43_surface_lanes_authorized") is not False:
        raise WassersteinExpectedValuesGateError(
            "p43_surface_lane_block_not_false"
        )

    al = packet["authority_locks"]
    if al.get("expected_values_gate_only") is not True:
        raise WassersteinExpectedValuesGateError(
            "expected_values_gate_only_must_be_true"
        )
    if al.get("expected_wasserstein_distances_authorized") is not True:
        raise WassersteinExpectedValuesGateError(
            "expected_wasserstein_distances_authorized_must_be_true"
        )
    if al.get("emits_metric_values") is not False:
        raise WassersteinExpectedValuesGateError(
            "emits_metric_values_must_be_false"
        )
    if al.get("execution_authority") is not False:
        raise WassersteinExpectedValuesGateError(
            "execution_authority_must_be_false"
        )
    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinExpectedValuesGateError("invalid_authority_locks")
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinExpectedValuesGateError("invalid_blocked_scopes")
    if packet["valid_fixture_result_review"] != build_valid_fixture_result_review():
        raise WassersteinExpectedValuesGateError("invalid_valid_fixture_result_review")
    if (
        packet["expected_value_authorization_scope"]
        != build_expected_value_authorization_scope()
    ):
        raise WassersteinExpectedValuesGateError(
            "invalid_expected_value_authorization_scope"
        )
    if (
        packet["rejected_input_exclusion_scope"]
        != build_rejected_input_exclusion_scope()
    ):
        raise WassersteinExpectedValuesGateError(
            "invalid_rejected_input_exclusion_scope"
        )
    if packet["metric_emission_block"] != build_metric_emission_block():
        raise WassersteinExpectedValuesGateError("invalid_metric_emission_block")
    if packet["forecast_influence_block"] != build_forecast_influence_block():
        raise WassersteinExpectedValuesGateError("invalid_forecast_influence_block")
    if packet["p43_surface_lane_block"] != build_p43_surface_lane_block():
        raise WassersteinExpectedValuesGateError("invalid_p43_surface_lane_block")

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_expected_values_gate_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_expected_values_gate(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_expected_values_gate(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "gate_type": GATE_TYPE,
        "operator_id": OPERATOR_ID,
        "source_computation_receipt_hash": SOURCE_COMPUTATION_RECEIPT_HASH,
        "source_computation_complete_review_hash": (
            SOURCE_COMPUTATION_COMPLETE_REVIEW_HASH
        ),
        "valid_fixture_result_review": payload.get(
            "valid_fixture_result_review", build_valid_fixture_result_review()
        ),
        "expected_value_authorization_scope": payload.get(
            "expected_value_authorization_scope",
            build_expected_value_authorization_scope(),
        ),
        "rejected_input_exclusion_scope": payload.get(
            "rejected_input_exclusion_scope", build_rejected_input_exclusion_scope()
        ),
        "metric_emission_block": payload.get(
            "metric_emission_block", build_metric_emission_block()
        ),
        "forecast_influence_block": payload.get(
            "forecast_influence_block", build_forecast_influence_block()
        ),
        "p43_surface_lane_block": payload.get(
            "p43_surface_lane_block", build_p43_surface_lane_block()
        ),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = compute_wasserstein_expected_values_gate_hash(base)
    validate_wasserstein_expected_values_gate(base)
    return _finalize(base)
