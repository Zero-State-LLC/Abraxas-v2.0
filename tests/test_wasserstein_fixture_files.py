from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURE_ROOT = Path("input/fixtures/wasserstein")
SOURCE_GATE_HASH = (
    "28587def52742f1176de841318ffc830e4c2efc7b00239d8dcab2582ec65c761"
)

VALID_DIR = FIXTURE_ROOT / "valid"
INVALID_DIR = FIXTURE_ROOT / "invalid"
NC_DIR = FIXTURE_ROOT / "not_computable"

VALID_FIXTURE_IDS = {
    "valid-001",
    "valid-002",
    "valid-003",
    "valid-004",
    "valid-005",
}
INVALID_FIXTURE_IDS = {
    "invalid-001",
    "invalid-002",
    "invalid-003",
    "invalid-004",
    "invalid-005",
}
NC_FIXTURE_IDS = {"nc-001", "nc-002", "nc-003", "nc-004"}

REQUIRED_FIELDS = {
    "created_at_utc",
    "expected_wasserstein_distance_included",
    "fixture_creation_authorized",
    "fixture_group",
    "fixture_id",
    "fixture_type",
    "input",
    "intended_lane",
    "metric_value_emitted",
    "schema_version",
    "source_gate_hash",
}


def _load_dir(directory: Path) -> list[dict]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.json"))]


def _all_fixtures() -> list[dict]:
    return _load_dir(VALID_DIR) + _load_dir(INVALID_DIR) + _load_dir(NC_DIR)


# ---------------------------------------------------------------------------
# Directory / file presence
# ---------------------------------------------------------------------------


def test_valid_dir_has_five_files() -> None:
    files = sorted(VALID_DIR.glob("*.json"))
    assert len(files) == 5, f"expected 5 valid fixtures, got {len(files)}"


def test_invalid_dir_has_five_files() -> None:
    files = sorted(INVALID_DIR.glob("*.json"))
    assert len(files) == 5, f"expected 5 invalid fixtures, got {len(files)}"


def test_nc_dir_has_four_files() -> None:
    files = sorted(NC_DIR.glob("*.json"))
    assert len(files) == 4, f"expected 4 not-computable fixtures, got {len(files)}"


def test_total_fixture_count() -> None:
    assert len(_all_fixtures()) == 14


# ---------------------------------------------------------------------------
# Required fields on every fixture
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_required_fields_present(fixture: dict) -> None:
    missing = sorted(REQUIRED_FIELDS - fixture.keys())
    assert not missing, f"fixture {fixture.get('fixture_id')} missing: {missing}"


# ---------------------------------------------------------------------------
# Schema version
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_schema_version(fixture: dict) -> None:
    assert fixture["schema_version"] == "WassersteinTestVectorFixture.v1"


# ---------------------------------------------------------------------------
# Source gate hash — provenance anchor
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_source_gate_hash(fixture: dict) -> None:
    assert fixture["source_gate_hash"] == SOURCE_GATE_HASH, (
        f"fixture {fixture.get('fixture_id')} has wrong source_gate_hash"
    )


# ---------------------------------------------------------------------------
# Shadow lane
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_intended_lane_shadow(fixture: dict) -> None:
    assert fixture["intended_lane"] == "SHADOW"


# ---------------------------------------------------------------------------
# Authority: creation authorized / no metric / no distance
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_fixture_creation_authorized(fixture: dict) -> None:
    assert fixture["fixture_creation_authorized"] is True


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_no_metric_value_emitted(fixture: dict) -> None:
    assert fixture["metric_value_emitted"] is False


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_no_expected_distance_included(fixture: dict) -> None:
    assert fixture["expected_wasserstein_distance_included"] is False


# ---------------------------------------------------------------------------
# fixture_type matches directory group
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture", _load_dir(VALID_DIR), ids=lambda f: f.get("fixture_id"))
def test_valid_fixtures_have_valid_type(fixture: dict) -> None:
    assert fixture["fixture_type"] == "VALID"


@pytest.mark.parametrize("fixture", _load_dir(INVALID_DIR), ids=lambda f: f.get("fixture_id"))
def test_invalid_fixtures_have_invalid_type(fixture: dict) -> None:
    assert fixture["fixture_type"] == "INVALID"


@pytest.mark.parametrize("fixture", _load_dir(NC_DIR), ids=lambda f: f.get("fixture_id"))
def test_nc_fixtures_have_nc_type(fixture: dict) -> None:
    assert fixture["fixture_type"] == "NOT_COMPUTABLE"


# ---------------------------------------------------------------------------
# fixture_id membership
# ---------------------------------------------------------------------------


def test_valid_fixture_ids() -> None:
    ids = {f["fixture_id"] for f in _load_dir(VALID_DIR)}
    assert ids == VALID_FIXTURE_IDS


def test_invalid_fixture_ids() -> None:
    ids = {f["fixture_id"] for f in _load_dir(INVALID_DIR)}
    assert ids == INVALID_FIXTURE_IDS


def test_nc_fixture_ids() -> None:
    ids = {f["fixture_id"] for f in _load_dir(NC_DIR)}
    assert ids == NC_FIXTURE_IDS


# ---------------------------------------------------------------------------
# All fixture_ids unique across entire corpus
# ---------------------------------------------------------------------------


def test_all_fixture_ids_unique() -> None:
    ids = [f["fixture_id"] for f in _all_fixtures()]
    assert len(ids) == len(set(ids))


# ---------------------------------------------------------------------------
# Invalid / not-computable fixtures carry rejection_reason
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _load_dir(INVALID_DIR) + _load_dir(NC_DIR),
    ids=lambda f: f.get("fixture_id"),
)
def test_rejection_reason_present(fixture: dict) -> None:
    assert "rejection_reason" in fixture
    assert isinstance(fixture["rejection_reason"], str)
    assert len(fixture["rejection_reason"]) > 0


# ---------------------------------------------------------------------------
# Valid fixtures have no rejection_reason
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _load_dir(VALID_DIR),
    ids=lambda f: f.get("fixture_id"),
)
def test_valid_fixtures_no_rejection_reason(fixture: dict) -> None:
    assert "rejection_reason" not in fixture


# ---------------------------------------------------------------------------
# Input field is present and is a dict
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture",
    _all_fixtures(),
    ids=lambda f: f.get("fixture_id", "unknown"),
)
def test_input_is_dict(fixture: dict) -> None:
    assert isinstance(fixture["input"], dict)


# ---------------------------------------------------------------------------
# JSON is stable (sorted keys, newline-terminated)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    sorted(FIXTURE_ROOT.rglob("*.json")),
    ids=lambda p: p.name,
)
def test_json_stable_sorted_keys(path: Path) -> None:
    raw = path.read_text(encoding="utf-8")
    assert raw.endswith("\n"), f"{path.name} must be newline-terminated"
    parsed = json.loads(raw)
    re_serialized = json.dumps(parsed, sort_keys=True, indent=2) + "\n"
    assert raw == re_serialized, (
        f"{path.name} is not stable sorted-key JSON"
    )
