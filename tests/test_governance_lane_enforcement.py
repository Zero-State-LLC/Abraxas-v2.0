from core.governance_runtime.authority import validate_lane_metadata
from core.governance_runtime.lanes import (
    canon_only,
    forecast_only,
    operator_only,
    projection_only,
    shadow_only,
)
from core.governance_runtime.models import AuthorityScope, GovernanceLane
from core.governance_runtime.receipt import canonical_json, sha256_text


@shadow_only
def shadow_fixture(value: int) -> int:
    return value + 1


@forecast_only
def forecast_fixture() -> str:
    return "forecast"


@projection_only
def projection_fixture() -> str:
    return "render"


@canon_only
def canon_fixture() -> str:
    return "canon"


@operator_only
def operator_fixture() -> str:
    return "operator"


def test_decorators_preserve_name_and_behavior() -> None:
    assert shadow_fixture.__name__ == "shadow_fixture"
    assert shadow_fixture(4) == 5


def test_metadata_is_deterministic() -> None:
    assert forecast_fixture.__abx_lane__ == GovernanceLane.FORECAST.value
    assert forecast_fixture.__abx_authority_scope__ == AuthorityScope.FORECAST.value


def test_projection_only_non_authoritative() -> None:
    report = validate_lane_metadata(projection_fixture)
    assert report.status == "PASS"
    assert projection_fixture.__abx_projection_only__ is True
    assert projection_fixture.__abx_authority_scope__ != AuthorityScope.INFERENCE.value


def test_shadow_cannot_satisfy_forecast_validation() -> None:
    shadow_fixture.__abx_authority_scope__ = AuthorityScope.FORECAST.value
    report = validate_lane_metadata(shadow_fixture)
    assert report.status == "FAIL"


def test_unknown_lane_returns_not_computable() -> None:
    def unknown() -> None:
        return None

    unknown.__abx_lane__ = "UNKNOWN"
    unknown.__abx_authority_scope__ = AuthorityScope.OBSERVATION.value
    report = validate_lane_metadata(unknown)
    assert report.findings[0].severity == "not_computable"


def test_artifact_hash_is_stable() -> None:
    payload = {"a": 1, "z": [1, 2, 3]}
    one = sha256_text(canonical_json(payload))
    two = sha256_text(canonical_json(payload))
    assert one == two
