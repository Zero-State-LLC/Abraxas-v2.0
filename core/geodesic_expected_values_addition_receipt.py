from __future__ import annotations

import json
import pathlib
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "GeodesicExpectedValuesAdditionReceipt.v1"
RECEIPT_ID = "geodesic_expected_values_addition_receipt_001"
RECEIPT_STATUS = "GEODESIC_EXPECTED_VALUES_ADDITION_COMPLETE"
ADDITION_STAGE = "EXPECTED_VALUES_ADDITION_ONLY"
OPERATOR_ID = "GEODESIC"

SOURCE_EXPECTED_VALUES_GATE_HASH = (
    "1b234f27f43f7bbddbd53d272b3c84d1f84bd3239a95289db42101b2c1ec88a0"
)

ALLOWED_LANE = ("SHADOW", "PROJECTION", "OBSERVATION_ONLY")

FIXTURE_BASE = pathlib.Path("input/fixtures/geodesic")

VALID_FIXTURE_IDS = (
    "geodesic.valid.valid_001_simple_connected_weighted_graph.v1",
    "geodesic.valid.valid_002_multi_hop_graph.v1",
    "geodesic.valid.valid_003_self_loop.v1",
    "geodesic.valid.valid_004_unweighted_graph.v1",
    "geodesic.valid.valid_005_complete_graph.v1",
)
INVALID_FIXTURE_IDS = (
    "geodesic.invalid.invalid_001_missing_source_node.v1",
    "geodesic.invalid.invalid_002_missing_target_node.v1",
    "geodesic.invalid.invalid_003_missing_edge_list.v1",
    "geodesic.invalid.invalid_004_negative_edge_weight.v1",
)
NC_FIXTURE_IDS = (
    "geodesic.not_computable.nc_001_empty_graph.v1",
    "geodesic.not_computable.nc_002_disconnected_graph.v1",
    "geodesic.not_computable.nc_003_source_not_in_graph.v1",
    "geodesic.not_computable.nc_004_target_not_in_graph.v1",
)

DECLARED_EXPECTED_VALUES: dict[str, float] = {
    "geodesic.valid.valid_001_simple_connected_weighted_graph.v1": 3.0,
    "geodesic.valid.valid_002_multi_hop_graph.v1": 3.0,
    "geodesic.valid.valid_003_self_loop.v1": 0.0,
    "geodesic.valid.valid_004_unweighted_graph.v1": 3.0,
    "geodesic.valid.valid_005_complete_graph.v1": 1.5,
}

FORBIDDEN = (
    "geodesic-distance",
    "dijkstra-execution",
    "shortest-path-computation",
    "metric-value",
    "metric-computation",
    "fixture-file",
    "manifest-file",
    "schema-file",
    "numpy",
    "scipy",
    "gpu-kernel",
)


class GeodesicExpectedValuesAdditionReceiptValidationError(ValueError):
    pass


def _finalize(v: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(v))


def _preimage(v: dict[str, Any]) -> dict[str, Any]:
    out = dict(v)
    out.pop("canonical_hash", None)
    return out


def _check_no_forbidden(v: Any) -> None:
    if isinstance(v, dict):
        for x in v.values():
            _check_no_forbidden(x)
    elif isinstance(v, list):
        for x in v:
            _check_no_forbidden(x)
    elif isinstance(v, str) and any(t in v.lower() for t in FORBIDDEN):
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            "forbidden_token_detected_in_string_value"
        )


def _load_valid_fixture(fixture_id: str) -> dict[str, Any]:
    slug = fixture_id.replace("geodesic.valid.", "").replace(".v1", "") + ".v1.json"
    path = FIXTURE_BASE / "valid" / slug
    return json.loads(path.read_text())


def _load_invalid_fixture(fixture_id: str) -> dict[str, Any]:
    slug = fixture_id.replace("geodesic.invalid.", "").replace(".v1", "") + ".v1.json"
    path = FIXTURE_BASE / "invalid" / slug
    return json.loads(path.read_text())


def _load_nc_fixture(fixture_id: str) -> dict[str, Any]:
    slug = fixture_id.replace("geodesic.not_computable.", "").replace(".v1", "") + ".v1.json"
    path = FIXTURE_BASE / "not_computable" / slug
    return json.loads(path.read_text())


def scan_valid_fixtures() -> list[dict[str, Any]]:
    results = []
    for fid in VALID_FIXTURE_IDS:
        doc = _load_valid_fixture(fid)
        results.append({
            "fixture_id": fid,
            "expected_geodesic_distance_included": doc.get("expected_geodesic_distance_included"),
            "expected_geodesic_distance": doc.get("expected_geodesic_distance"),
            "expected_status": doc.get("expected_status"),
            "source_expected_values_gate_hash": doc.get("source_expected_values_gate_hash"),
            "canonical_hash": doc.get("canonical_hash"),
        })
    return results


def scan_excluded_fixtures() -> dict[str, list[dict[str, Any]]]:
    invalid_results = []
    for fid in INVALID_FIXTURE_IDS:
        doc = _load_invalid_fixture(fid)
        invalid_results.append({
            "fixture_id": fid,
            "expected_geodesic_distance_included": doc.get("expected_geodesic_distance_included"),
            "fixture_type": doc.get("fixture_type"),
        })
    nc_results = []
    for fid in NC_FIXTURE_IDS:
        doc = _load_nc_fixture(fid)
        nc_results.append({
            "fixture_id": fid,
            "expected_geodesic_distance_included": doc.get("expected_geodesic_distance_included"),
            "fixture_type": doc.get("fixture_type"),
        })
    return {"invalid": invalid_results, "not_computable": nc_results}


def build_modified_fixture_manifest(valid_scan: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "modified_fixture_count": len(valid_scan),
        "unmodified_invalid_count": len(INVALID_FIXTURE_IDS),
        "unmodified_not_computable_count": len(NC_FIXTURE_IDS),
        "total_fixture_count": len(VALID_FIXTURE_IDS) + len(INVALID_FIXTURE_IDS) + len(NC_FIXTURE_IDS),
        "modified_fixture_ids": list(VALID_FIXTURE_IDS),
        "addition_field": "expected_geodesic_distance",
        "inclusion_flag_field": "expected_geodesic_distance_included",
        "source_gate_field": "source_expected_values_gate_hash",
        "fixture_files_modified": True,
        "invalid_fixtures_modified": False,
        "not_computable_fixtures_modified": False,
    }


def build_expected_value_summary(valid_scan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "fixture_id": entry["fixture_id"],
            "expected_geodesic_distance": entry["expected_geodesic_distance"],
            "expected_geodesic_distance_included": entry["expected_geodesic_distance_included"],
            "expected_status": entry["expected_status"],
            "source_expected_values_gate_hash_prefix": (
                entry["source_expected_values_gate_hash"][:16] + "…"
                if entry.get("source_expected_values_gate_hash") else None
            ),
            "canonical_hash_prefix": (
                entry["canonical_hash"][:16] + "…"
                if entry.get("canonical_hash") else None
            ),
        }
        for entry in valid_scan
    ]


def build_invalid_fixture_exclusion_review(excluded: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "excluded_fixture_count": len(excluded),
        "excluded_fixture_ids": [e["fixture_id"] for e in excluded],
        "all_excluded_have_no_expected_distance": all(
            e.get("expected_geodesic_distance_included") is False for e in excluded
        ),
        "exclusion_confirmed": True,
        "modification_applied": False,
    }


def build_not_computable_fixture_exclusion_review(excluded: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "excluded_fixture_count": len(excluded),
        "excluded_fixture_ids": [e["fixture_id"] for e in excluded],
        "all_excluded_have_no_expected_distance": all(
            e.get("expected_geodesic_distance_included") is False for e in excluded
        ),
        "exclusion_confirmed": True,
        "modification_applied": False,
    }


def build_no_metric_emission_review() -> dict[str, Any]:
    return {
        "emits_metric_values": False,
        "metric_emission_confirmed_absent": True,
        "review_finding": (
            "No metric values emitted. Static expected-distance field addition only. "
            "All values declared by operator, not computed."
        ),
    }


def build_no_forecast_influence_review() -> dict[str, Any]:
    return {
        "forecast_influence": False,
        "forecast_confirmed_absent": True,
        "review_finding": (
            "No forecast influence. GEODESIC operator remains SHADOW_STUB_ONLY. "
            "Expected-value addition does not open forecast lanes."
        ),
    }


def build_blocked_scopes() -> dict[str, Any]:
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


def build_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "shadow_lane_only": True,
        "expected_values_addition_only": True,
        "expected_geodesic_distances_authorized": True,
        "emits_metric_values": False,
        "forecast_influence": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "canon_promotion": False,
        "runtime_mutation": False,
        "execution_authority": False,
        "inference_authority": False,
    }


def build_addition_receipt(
    receipt_id: str = RECEIPT_ID,
    created_at_utc: str = "2026-05-30T00:00:00Z",
    intended_lane: str = "SHADOW",
) -> dict[str, Any]:
    if intended_lane not in ALLOWED_LANE:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )

    valid_scan = scan_valid_fixtures()
    excluded = scan_excluded_fixtures()

    _validate_valid_scan(valid_scan)
    _validate_excluded_scan(excluded)

    preimage: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": receipt_id,
        "receipt_status": RECEIPT_STATUS,
        "addition_stage": ADDITION_STAGE,
        "created_at_utc": created_at_utc,
        "intended_lane": intended_lane,
        "source_expected_values_gate_hash": SOURCE_EXPECTED_VALUES_GATE_HASH,
        "modified_fixture_manifest": build_modified_fixture_manifest(valid_scan),
        "expected_value_summary": build_expected_value_summary(valid_scan),
        "invalid_fixture_exclusion_review": build_invalid_fixture_exclusion_review(
            excluded["invalid"]
        ),
        "not_computable_fixture_exclusion_review": build_not_computable_fixture_exclusion_review(
            excluded["not_computable"]
        ),
        "no_metric_emission_review": build_no_metric_emission_review(),
        "no_forecast_influence_review": build_no_forecast_influence_review(),
        "blocked_scopes": build_blocked_scopes(),
        "authority_locks": build_authority_locks(),
        "recommended_next_step": "GEODESIC_EXPECTED_VALUES_COMPLETE_REVIEW",
    }

    result = json.loads(canonical_dumps(preimage))
    _check_no_forbidden(result)
    result["canonical_hash"] = canonical_hash(result)
    return _finalize(result)


def _validate_valid_scan(scan: list[dict[str, Any]]) -> None:
    if len(scan) != 5:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            f"Expected 5 valid fixtures in scan, got {len(scan)}"
        )
    for entry in scan:
        fid = entry["fixture_id"]
        if entry.get("expected_geodesic_distance_included") is not True:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"Fixture {fid}: expected_geodesic_distance_included must be True"
            )
        ev = entry.get("expected_geodesic_distance")
        if ev is None:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"Fixture {fid}: expected_geodesic_distance must be declared"
            )
        declared = DECLARED_EXPECTED_VALUES.get(fid)
        if ev != declared:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"Fixture {fid}: expected_geodesic_distance={ev} but declared={declared}"
            )
        if entry.get("source_expected_values_gate_hash") != SOURCE_EXPECTED_VALUES_GATE_HASH:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"Fixture {fid}: source_expected_values_gate_hash mismatch"
            )


def _validate_excluded_scan(excluded: dict[str, list[dict[str, Any]]]) -> None:
    for entry in excluded["invalid"]:
        if entry.get("expected_geodesic_distance_included") is not False:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"Invalid fixture {entry['fixture_id']} must have "
                "expected_geodesic_distance_included=False"
            )
    for entry in excluded["not_computable"]:
        if entry.get("expected_geodesic_distance_included") is not False:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"NC fixture {entry['fixture_id']} must have "
                "expected_geodesic_distance_included=False"
            )


def validate_addition_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema_version") != SCHEMA_VERSION:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            f"schema_version must be {SCHEMA_VERSION!r}"
        )
    if receipt.get("receipt_status") != RECEIPT_STATUS:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            f"receipt_status must be {RECEIPT_STATUS!r}"
        )
    if receipt.get("addition_stage") != ADDITION_STAGE:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            f"addition_stage must be {ADDITION_STAGE!r}"
        )
    if receipt.get("intended_lane") not in ALLOWED_LANE:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            f"intended_lane must be one of {ALLOWED_LANE}"
        )
    if receipt.get("source_expected_values_gate_hash") != SOURCE_EXPECTED_VALUES_GATE_HASH:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            "source_expected_values_gate_hash mismatch"
        )
    locks = receipt.get("authority_locks", {})
    for flag in ("advisory_only", "shadow_lane_only", "expected_values_addition_only",
                 "expected_geodesic_distances_authorized"):
        if locks.get(flag) is not True:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"authority_locks.{flag} must be True"
            )
    for flag in ("emits_metric_values", "forecast_influence", "p43_surface_lanes_authorized",
                 "production_activation", "canon_promotion", "runtime_mutation",
                 "execution_authority", "inference_authority"):
        if locks.get(flag) is not False:
            raise GeodesicExpectedValuesAdditionReceiptValidationError(
                f"authority_locks.{flag} must be False"
            )
    mfm = receipt.get("modified_fixture_manifest", {})
    if mfm.get("modified_fixture_count") != 5:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            "modified_fixture_manifest.modified_fixture_count must be 5"
        )
    if mfm.get("invalid_fixtures_modified") is not False:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            "modified_fixture_manifest.invalid_fixtures_modified must be False"
        )
    if mfm.get("not_computable_fixtures_modified") is not False:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            "modified_fixture_manifest.not_computable_fixtures_modified must be False"
        )
    evs = receipt.get("expected_value_summary", [])
    if len(evs) != 5:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            "expected_value_summary must contain exactly 5 entries"
        )
    h = receipt.get("canonical_hash", "")
    if not isinstance(h, str) or len(h) != 64:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            "canonical_hash must be a 64-char hex string"
        )
    recomputed = canonical_hash(_preimage(receipt))
    if recomputed != h:
        raise GeodesicExpectedValuesAdditionReceiptValidationError(
            f"canonical_hash mismatch: stored={h!r} recomputed={recomputed!r}"
        )
