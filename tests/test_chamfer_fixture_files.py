from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("input/fixtures/chamfer")
FIXTURE_FILES = [
    ROOT / "valid/identical_point_sets.v1.json",
    ROOT / "valid/offset_point_sets.v1.json",
    ROOT / "valid/partial_overlap_point_sets.v1.json",
    ROOT / "valid/duplicate_points.v1.json",
    ROOT / "valid/multidimensional_points.v1.json",
    ROOT / "invalid/missing_point_set.v1.json",
    ROOT / "invalid/empty_point_set.v1.json",
    ROOT / "invalid/dimension_mismatch.v1.json",
    ROOT / "invalid/non_numeric_coordinate.v1.json",
    ROOT / "invalid/malformed_coordinates.v1.json",
    ROOT / "not_computable/unknown_coordinate_space.v1.json",
    ROOT / "not_computable/undeclared_dimensionality.v1.json",
    ROOT / "not_computable/missing_numerical_policy.v1.json",
]
MANIFEST = ROOT / "chamfer_fixture_manifest.v1.json"
FALSE_FLAGS = {
    "production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation",
    "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved",
    "authorization_granted",
}


def _canon(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(obj: dict) -> str:
    pre = dict(obj)
    pre.pop("canonical_hash", None)
    return hashlib.sha256(_canon(pre).encode()).hexdigest()


def test_files_exist_and_parse() -> None:
    assert MANIFEST.exists()
    for path in FIXTURE_FILES:
        assert path.exists()
        json.loads(path.read_text(encoding="utf-8"))


def test_hashes_validate_and_exclude_hash_field() -> None:
    for path in [*FIXTURE_FILES, MANIFEST]:
        packet = json.loads(path.read_text(encoding="utf-8"))
        assert packet["canonical_hash"] == _hash(packet)
        altered = dict(packet)
        altered["canonical_hash"] = "0" * 64
        assert _hash(altered) == _hash(packet)


def test_locks_and_expected_distance() -> None:
    for path in FIXTURE_FILES:
        packet = json.loads(path.read_text(encoding="utf-8"))
        if "/valid/" in path.as_posix():
            assert packet["expected_distance"] is not None
        else:
            assert packet["expected_distance"] is None
        assert set(packet["governance_flags"]) == FALSE_FLAGS
        assert all(packet["governance_flags"][k] is False for k in FALSE_FLAGS)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["expected_distances_added"] is True
    assert manifest["tolerance_values_added"] is False
    assert manifest["chamfer_math_added"] is False
    assert manifest["metric_values_emitted"] is False
    assert manifest["runtime_loading_enabled"] is False
    assert set(manifest["governance_flags"]) == FALSE_FLAGS
    assert all(manifest["governance_flags"][k] is False for k in FALSE_FLAGS)


def test_fixture_group_constraints_and_non_executable_strings() -> None:
    forbidden = ("exec(", "subprocess", "os.system", "runtime_authority:true")
    for path in FIXTURE_FILES:
        packet = json.loads(path.read_text(encoding="utf-8"))
        serialized = _canon(packet).lower()
        assert not any(tok in serialized for tok in forbidden)
        if "/valid/" in path.as_posix():
            ps = packet["point_sets"]
            assert "point_set_a" in ps and "point_set_b" in ps
            assert "declared_dimensionality" in ps and "coordinate_space" in ps and "numerical_policy" in ps
            assert packet["expected_status"] == "VALID_INPUT_WITH_EXPECTED_DISTANCE"
        elif "/invalid/" in path.as_posix():
            assert packet["expected_status"] == "INVALID_INPUT_NO_EXPECTED_DISTANCE"
            assert packet["fixture_type"] == "INVALID"
        else:
            assert packet["expected_status"] == "NOT_COMPUTABLE_NO_EXPECTED_DISTANCE"
            assert packet["fixture_type"] == "NOT_COMPUTABLE"


def test_manifest_deterministic_ordering() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["fixture_ids"] == sorted(manifest["fixture_ids"])
    assert manifest["fixture_paths"] == sorted(manifest["fixture_paths"])
