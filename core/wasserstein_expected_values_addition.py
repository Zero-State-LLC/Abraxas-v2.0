from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "WassersteinExpectedValuesAdditionReceipt.v1"
RECEIPT_TYPE = "WASSERSTEIN_EXPECTED_VALUES_ADDITION_RECEIPT"
OPERATOR_ID = "WASSERSTEIN"

SOURCE_EXPECTED_VALUES_GATE_HASH = (
    "21baf9d688ba3ec0590e14355e26d043b48693ac71ecdb0d69da0afcf3b09bb2"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")
ALLOWED_STAGE = ("EXPECTED_VALUES_ADDITION_ONLY", "BLOCKED_PENDING_GATE")

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

VALID_FIXTURE_FILES = {
    "valid-001": "input/fixtures/wasserstein/valid/valid_001_distribution_pair.json",
    "valid-002": "input/fixtures/wasserstein/valid/valid_002_weighted_histogram.json",
    "valid-003": "input/fixtures/wasserstein/valid/valid_003_reference_vector.json",
    "valid-004": "input/fixtures/wasserstein/valid/valid_004_ground_metric.json",
    "valid-005": "input/fixtures/wasserstein/valid/valid_005_degenerate_distribution.json",
}

EXPECTED_WASSERSTEIN_DISTANCES: dict[str, float] = {
    "valid-001": 0.4,
    "valid-002": 0.4,
    "valid-003": 0.866025,
    "valid-004": 0.2,
    "valid-005": 0.0,
}

INVALID_FIXTURE_IDS = [
    "invalid-001",
    "invalid-002",
    "invalid-003",
    "invalid-004",
    "invalid-005",
]

NC_FIXTURE_IDS = ["nc-001", "nc-002", "nc-003", "nc-004"]


class WassersteinExpectedValuesAdditionError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


# ---------------------------------------------------------------------------
# Receipt sub-structures
# ---------------------------------------------------------------------------


def build_modified_fixture_manifest() -> list[dict[str, Any]]:
    entries = []
    for fid in sorted(EXPECTED_WASSERSTEIN_DISTANCES):
        entries.append(
            {
                "fixture_id": fid,
                "fixture_path": VALID_FIXTURE_FILES[fid],
                "expected_wasserstein_distance": EXPECTED_WASSERSTEIN_DISTANCES[fid],
                "source_expected_values_gate_hash": SOURCE_EXPECTED_VALUES_GATE_HASH,
                "addition_status": "ADDED",
                "metric_value_emitted": False,
                "shadow_only": True,
            }
        )
    return entries


def build_expected_value_summary() -> dict[str, Any]:
    return {
        "total_fixtures_updated": 5,
        "all_additions_shadow_only": True,
        "no_metric_emission": True,
        "values": {fid: v for fid, v in sorted(EXPECTED_WASSERSTEIN_DISTANCES.items())},
        "summary_status": "EXPECTED_VALUES_ADDITION_COMPLETE",
    }


def build_invalid_fixture_exclusion_review() -> dict[str, Any]:
    return {
        "invalid_fixture_ids": INVALID_FIXTURE_IDS,
        "invalid_count": 5,
        "expected_wasserstein_distance_added": False,
        "fixtures_unchanged": True,
        "exclusion_status": "INVALID_FIXTURES_EXCLUDED_UNCHANGED",
    }


def build_not_computable_fixture_exclusion_review() -> dict[str, Any]:
    return {
        "nc_fixture_ids": NC_FIXTURE_IDS,
        "not_computable_count": 4,
        "expected_wasserstein_distance_added": False,
        "fixtures_unchanged": True,
        "exclusion_status": "NOT_COMPUTABLE_FIXTURES_EXCLUDED_UNCHANGED",
    }


def build_no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "no_runtime_emission": True,
        "no_p43_surface_output": True,
        "review_status": "NO_METRIC_EMISSION_CONFIRMED",
    }


def build_no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "no_forecast_binding": True,
        "no_p43_output": True,
        "review_status": "NO_FORECAST_INFLUENCE_CONFIRMED",
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
        "expected_values_addition_only": True,
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
        raise WassersteinExpectedValuesAdditionError(
            "forbidden_provenance_reference_detected"
        )


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_wasserstein_expected_values_addition_receipt(
    packet: dict[str, Any],
) -> None:
    required = {
        "schema_version",
        "receipt_id",
        "receipt_type",
        "operator_id",
        "source_expected_values_gate_hash",
        "intended_lane",
        "addition_stage",
        "modified_fixture_manifest",
        "expected_value_summary",
        "invalid_fixture_exclusion_review",
        "not_computable_fixture_exclusion_review",
        "no_metric_emission_review",
        "no_forecast_influence_review",
        "blocked_scopes",
        "authority_locks",
        "recommended_next_step",
        "provenance",
        "created_at_utc",
        "canonical_hash",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise WassersteinExpectedValuesAdditionError(
            f"missing_required_fields:{missing}"
        )

    if packet["schema_version"] != SCHEMA_VERSION:
        raise WassersteinExpectedValuesAdditionError("invalid_schema_version")
    if packet["receipt_type"] != RECEIPT_TYPE:
        raise WassersteinExpectedValuesAdditionError("invalid_receipt_type")
    if packet["operator_id"] != OPERATOR_ID:
        raise WassersteinExpectedValuesAdditionError("unknown_operator_id")
    if packet["source_expected_values_gate_hash"] != SOURCE_EXPECTED_VALUES_GATE_HASH:
        raise WassersteinExpectedValuesAdditionError(
            "invalid_source_expected_values_gate_hash"
        )
    if packet["intended_lane"] not in ALLOWED_LANE:
        raise WassersteinExpectedValuesAdditionError("unknown_intended_lane")
    if packet["addition_stage"] not in ALLOWED_STAGE:
        raise WassersteinExpectedValuesAdditionError("unknown_addition_stage")

    mfm = packet["modified_fixture_manifest"]
    if len(mfm) != 5:
        raise WassersteinExpectedValuesAdditionError(
            "modified_fixture_manifest_must_have_5_entries"
        )
    for entry in mfm:
        if entry.get("addition_status") != "ADDED":
            raise WassersteinExpectedValuesAdditionError(
                f"fixture_addition_status_not_added:{entry.get('fixture_id')}"
            )
        if entry.get("metric_value_emitted") is not False:
            raise WassersteinExpectedValuesAdditionError(
                f"fixture_metric_value_emitted_must_be_false:{entry.get('fixture_id')}"
            )
        if entry.get("shadow_only") is not True:
            raise WassersteinExpectedValuesAdditionError(
                f"fixture_shadow_only_must_be_true:{entry.get('fixture_id')}"
            )

    evs = packet["expected_value_summary"]
    if evs.get("summary_status") != "EXPECTED_VALUES_ADDITION_COMPLETE":
        raise WassersteinExpectedValuesAdditionError(
            "expected_value_summary_not_complete"
        )
    if evs.get("total_fixtures_updated") != 5:
        raise WassersteinExpectedValuesAdditionError(
            "expected_value_summary_count_mismatch"
        )
    if not evs.get("no_metric_emission"):
        raise WassersteinExpectedValuesAdditionError(
            "expected_value_summary_allows_metric_emission"
        )

    ifer = packet["invalid_fixture_exclusion_review"]
    if ifer.get("exclusion_status") != "INVALID_FIXTURES_EXCLUDED_UNCHANGED":
        raise WassersteinExpectedValuesAdditionError(
            "invalid_fixture_exclusion_review_not_excluded"
        )
    if ifer.get("expected_wasserstein_distance_added") is not False:
        raise WassersteinExpectedValuesAdditionError(
            "invalid_fixtures_must_not_have_expected_distance_added"
        )

    ncfer = packet["not_computable_fixture_exclusion_review"]
    if ncfer.get("exclusion_status") != "NOT_COMPUTABLE_FIXTURES_EXCLUDED_UNCHANGED":
        raise WassersteinExpectedValuesAdditionError(
            "not_computable_fixture_exclusion_review_not_excluded"
        )
    if ncfer.get("expected_wasserstein_distance_added") is not False:
        raise WassersteinExpectedValuesAdditionError(
            "nc_fixtures_must_not_have_expected_distance_added"
        )

    nmer = packet["no_metric_emission_review"]
    if nmer.get("review_status") != "NO_METRIC_EMISSION_CONFIRMED":
        raise WassersteinExpectedValuesAdditionError(
            "no_metric_emission_review_not_confirmed"
        )
    if nmer.get("emits_metric_values") is not False:
        raise WassersteinExpectedValuesAdditionError(
            "no_metric_emission_review_emits_metric_values_not_false"
        )

    nfir = packet["no_forecast_influence_review"]
    if nfir.get("review_status") != "NO_FORECAST_INFLUENCE_CONFIRMED":
        raise WassersteinExpectedValuesAdditionError(
            "no_forecast_influence_review_not_confirmed"
        )
    if nfir.get("forecast_influence") is not False:
        raise WassersteinExpectedValuesAdditionError(
            "no_forecast_influence_review_forecast_influence_not_false"
        )

    al = packet["authority_locks"]
    if al.get("expected_values_addition_only") is not True:
        raise WassersteinExpectedValuesAdditionError(
            "expected_values_addition_only_must_be_true"
        )
    if al.get("expected_wasserstein_distances_authorized") is not True:
        raise WassersteinExpectedValuesAdditionError(
            "expected_wasserstein_distances_authorized_must_be_true"
        )
    if al.get("emits_metric_values") is not False:
        raise WassersteinExpectedValuesAdditionError(
            "emits_metric_values_must_be_false"
        )
    if al.get("execution_authority") is not False:
        raise WassersteinExpectedValuesAdditionError(
            "execution_authority_must_be_false"
        )

    if packet["authority_locks"] != default_authority_locks():
        raise WassersteinExpectedValuesAdditionError("invalid_authority_locks")
    if packet["blocked_scopes"] != default_blocked_scopes():
        raise WassersteinExpectedValuesAdditionError("invalid_blocked_scopes")
    if packet["modified_fixture_manifest"] != build_modified_fixture_manifest():
        raise WassersteinExpectedValuesAdditionError("invalid_modified_fixture_manifest")
    if packet["expected_value_summary"] != build_expected_value_summary():
        raise WassersteinExpectedValuesAdditionError("invalid_expected_value_summary")
    if (
        packet["invalid_fixture_exclusion_review"]
        != build_invalid_fixture_exclusion_review()
    ):
        raise WassersteinExpectedValuesAdditionError(
            "invalid_invalid_fixture_exclusion_review"
        )
    if (
        packet["not_computable_fixture_exclusion_review"]
        != build_not_computable_fixture_exclusion_review()
    ):
        raise WassersteinExpectedValuesAdditionError(
            "invalid_not_computable_fixture_exclusion_review"
        )
    if packet["no_metric_emission_review"] != build_no_metric_emission_review():
        raise WassersteinExpectedValuesAdditionError(
            "invalid_no_metric_emission_review"
        )
    if packet["no_forecast_influence_review"] != build_no_forecast_influence_review():
        raise WassersteinExpectedValuesAdditionError(
            "invalid_no_forecast_influence_review"
        )

    _assert_safe(packet["provenance"])


# ---------------------------------------------------------------------------
# Hash / serialization / build
# ---------------------------------------------------------------------------


def compute_wasserstein_expected_values_addition_receipt_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_wasserstein_expected_values_addition_receipt(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_wasserstein_expected_values_addition_receipt(
    payload: dict[str, Any],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "receipt_type": RECEIPT_TYPE,
        "operator_id": OPERATOR_ID,
        "source_expected_values_gate_hash": SOURCE_EXPECTED_VALUES_GATE_HASH,
        "modified_fixture_manifest": payload.get(
            "modified_fixture_manifest", build_modified_fixture_manifest()
        ),
        "expected_value_summary": payload.get(
            "expected_value_summary", build_expected_value_summary()
        ),
        "invalid_fixture_exclusion_review": payload.get(
            "invalid_fixture_exclusion_review",
            build_invalid_fixture_exclusion_review(),
        ),
        "not_computable_fixture_exclusion_review": payload.get(
            "not_computable_fixture_exclusion_review",
            build_not_computable_fixture_exclusion_review(),
        ),
        "no_metric_emission_review": payload.get(
            "no_metric_emission_review", build_no_metric_emission_review()
        ),
        "no_forecast_influence_review": payload.get(
            "no_forecast_influence_review", build_no_forecast_influence_review()
        ),
        "authority_locks": payload.get("authority_locks", default_authority_locks()),
        "blocked_scopes": payload.get("blocked_scopes", default_blocked_scopes()),
    }
    base["canonical_hash"] = compute_wasserstein_expected_values_addition_receipt_hash(
        base
    )
    validate_wasserstein_expected_values_addition_receipt(base)
    return _finalize(base)
