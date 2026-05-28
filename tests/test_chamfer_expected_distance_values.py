from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path("input/fixtures/chamfer")
MANIFEST = ROOT / "chamfer_fixture_manifest.v1.json"
VALID_EXPECTED = {
    "chamfer.valid.duplicate_points.v1": 0.0,
    "chamfer.valid.identical_point_sets.v1": 0.0,
    "chamfer.valid.multidimensional_points.v1": 3.0,
    "chamfer.valid.offset_point_sets.v1": 1.0,
    "chamfer.valid.partial_overlap_point_sets.v1": 0.5,
}
FALSE_FLAGS = {
    "production_activation",
    "canon_promotion",
    "scheduler_mutation",
    "runtime_authority",
    "runtime_mutation",
    "forecast_influence",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "activation_approved",
    "authorization_granted",
}
RUNTIME_IMPLEMENTATION_MODULES = {
    Path("core/chamfer_distance.py"),
    Path("core/chamfer_distance_implementation.py"),
    Path("core/chamfer_metric.py"),
    Path("core/metrics/chamfer_distance.py"),
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canon(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(obj: dict[str, Any]) -> str:
    preimage = dict(obj)
    preimage.pop("canonical_hash", None)
    return hashlib.sha256(_canon(preimage).encode()).hexdigest()


def _assert_hash_valid(path: Path) -> None:
    packet = _load(path)
    assert packet["canonical_hash"] == _hash(packet)
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert _hash(altered) == _hash(packet)


def _fixture_files(group: str) -> list[Path]:
    return sorted((ROOT / group).glob("*.v1.json"))


def _squared_distance(left: list[int | float], right: list[int | float]) -> float:
    return float(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def _nearest_mean(source: list[list[int | float]], target: list[list[int | float]]) -> float:
    return sum(min(_squared_distance(src, dst) for dst in target) for src in source) / len(source)


def _static_chamfer_expected_distance(packet: dict[str, Any]) -> float:
    point_sets = packet["point_sets"]
    point_set_a = point_sets["point_set_a"]
    point_set_b = point_sets["point_set_b"]
    a_to_b = _nearest_mean(point_set_a, point_set_b)
    b_to_a = _nearest_mean(point_set_b, point_set_a)
    return (a_to_b + b_to_a) / 2


def _assert_false_flags(packet: dict[str, Any]) -> None:
    assert set(packet["governance_flags"]) == FALSE_FLAGS
    assert all(packet["governance_flags"][flag] is False for flag in FALSE_FLAGS)


def _assert_no_numeric_tolerance(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if "tolerance" in key:
                assert isinstance(nested, bool) or not isinstance(nested, int | float)
            _assert_no_numeric_tolerance(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_no_numeric_tolerance(nested)


def test_valid_fixtures_have_only_static_expected_distances() -> None:
    seen: dict[str, float] = {}
    for path in _fixture_files("valid"):
        packet = _load(path)
        fixture_id = packet["fixture_id"]
        seen[fixture_id] = packet["expected_distance"]
        assert packet["expected_distance"] is not None
        assert packet["expected_distance"] == VALID_EXPECTED[fixture_id]
        assert packet["expected_status"] == "VALID_INPUT_WITH_EXPECTED_DISTANCE"
        assert _static_chamfer_expected_distance(packet) == VALID_EXPECTED[fixture_id]
        _assert_false_flags(packet)
        _assert_hash_valid(path)
        _assert_no_numeric_tolerance(packet)

    assert seen == VALID_EXPECTED


def test_invalid_and_not_computable_fixtures_remain_null_locked() -> None:
    for path in _fixture_files("invalid"):
        packet = _load(path)
        assert packet["expected_distance"] is None
        assert packet["expected_status"] == "INVALID_INPUT_NO_EXPECTED_DISTANCE"
        _assert_false_flags(packet)
        _assert_no_numeric_tolerance(packet)

    for path in _fixture_files("not_computable"):
        packet = _load(path)
        assert packet["expected_distance"] is None
        assert packet["expected_status"] == "NOT_COMPUTABLE_NO_EXPECTED_DISTANCE"
        _assert_false_flags(packet)
        _assert_no_numeric_tolerance(packet)


def test_manifest_records_expected_distance_presence_without_runtime_enabling() -> None:
    manifest = _load(MANIFEST)
    assert manifest["expected_distances_added"] is True
    assert manifest["tolerance_values_added"] is False
    assert manifest["chamfer_math_added"] is False
    assert manifest["metric_values_emitted"] is False
    assert manifest["runtime_loading_enabled"] is False
    assert manifest["expected_distance_fixture_ids"] == sorted(VALID_EXPECTED)
    assert manifest["null_locked_fixture_ids"] == sorted(
        _load(path)["fixture_id"] for path in [*_fixture_files("invalid"), *_fixture_files("not_computable")]
    )
    assert manifest["fixture_ids"] == sorted(manifest["fixture_ids"])
    assert manifest["fixture_paths"] == sorted(manifest["fixture_paths"])
    assert manifest["expected_distance_policy"] == {
        "policy_id": "CHAMFER_SYMMETRIC_MEAN_SQUARED_NEAREST_NEIGHBOR_STATIC_FIXTURE_VALUES_V1",
        "scope": "valid_fixtures_only",
        "distance_convention": "symmetric_chamfer_mean_of_squared_euclidean_nearest_neighbor_means",
        "runtime_math_added": False,
        "tolerance_values_added": False,
        "metric_values_emitted": False,
    }
    _assert_false_flags(manifest)
    _assert_hash_valid(MANIFEST)
    _assert_no_numeric_tolerance(manifest)


def test_no_runtime_loading_or_chamfer_implementation_module_added() -> None:
    manifest = _load(MANIFEST)
    assert manifest["runtime_loading_enabled"] is False
    assert not any(path.exists() for path in RUNTIME_IMPLEMENTATION_MODULES)
