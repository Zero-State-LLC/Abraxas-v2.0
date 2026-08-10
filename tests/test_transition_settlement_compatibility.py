import json
from pathlib import Path

from core.instantiation import validate_transition_settlement_compatibility


ROOT_DIR = Path(__file__).resolve().parent.parent
FIXTURE_DIR = ROOT_DIR / "input/fixtures/instantiation"


def _fixture(path: str) -> dict:
    return json.loads(
        (FIXTURE_DIR / path).read_text(
            encoding="utf-8"
        )
    )


def test_no_intervention_transition_is_not_computable_without_refs():
    fixture = _fixture("no_intervention_transition.v1.json")
    assert fixture["scenario"] == "no_intervention_transition"
    report = validate_transition_settlement_compatibility(
        {
            "transition_id": "it-no-ref",
            "forecast_ref": None,
            "settlement_ref": None,
        }
    )
    assert report.status == "NOT_COMPUTABLE"
    assert report.findings == ()


def test_fixture_settlement_requires_matching_settlement_artifact_refs():
    fixture = _fixture("abx_mediated_settlement.v1.json")

    transition = {
        "transition_id": "it-mediation",
        "forecast_ref": {
            "object_id": "forecast-rdi-3",
            "canonical_hash": "f" * 64,
        },
        "settlement_ref": {
            "object_id": fixture["settlement_ref"]["object_id"],
            "canonical_hash": fixture["settlement_ref"]["canonical_hash"],
        },
    }

    settlement = {
        "forecast_id": "forecast-rdi-3",
        "forecast_hash": "f" * 64,
    }
    forecast = {
        "forecast_id": "forecast-rdi-3",
        "forecast_hash": "f" * 64,
    }

    report = validate_transition_settlement_compatibility(
        transition,
        settlement=settlement,
        forecast=forecast,
    )

    assert report.status == "PASS"
    assert report.findings == ()


def test_forecast_only_transition_is_not_computable():
    report = validate_transition_settlement_compatibility(
        {
            "transition_id": "it-forecast-only",
            "forecast_ref": {"object_id": "f", "canonical_hash": "a" * 64},
            "settlement_ref": None,
        }
    )
    assert report.status == "NOT_COMPUTABLE"
    assert report.findings
    assert all(item.code == "INVALID_NOT_COMPUTABLE" for item in report.findings)


def test_settlement_ref_without_artifact_is_not_computable():
    report = validate_transition_settlement_compatibility(
        {
            "transition_id": "it-missing-settlement-artifact",
            "forecast_ref": None,
            "settlement_ref": {"object_id": "s", "canonical_hash": "b" * 64},
        }
    )
    assert report.status == "NOT_COMPUTABLE"
    assert report.findings
    assert report.findings[0].code == "INVALID_NOT_COMPUTABLE"


def test_transition_and_settlement_forecast_mismatch_is_not_computable():
    report = validate_transition_settlement_compatibility(
        {
            "transition_id": "it-mismatch",
            "forecast_ref": {"object_id": "forecast-a", "canonical_hash": "a" * 64},
            "settlement_ref": {"object_id": "s", "canonical_hash": "b" * 64},
        },
        settlement={"forecast_id": "forecast-b", "forecast_hash": "b" * 64},
    )
    assert report.status == "NOT_COMPUTABLE"
    assert any(item.code == "INVALID_NOT_COMPUTABLE" for item in report.findings)


def test_settlement_and_provided_forecast_must_match():
    report = validate_transition_settlement_compatibility(
        {
            "transition_id": "it-cross-check",
            "forecast_ref": {"object_id": "forecast-a", "canonical_hash": "a" * 64},
            "settlement_ref": {"object_id": "s", "canonical_hash": "b" * 64},
        },
        settlement={"forecast_id": "forecast-a", "forecast_hash": "a" * 64},
        forecast={"forecast_id": "forecast-a", "forecast_hash": "b" * 64},
    )
    assert report.status == "NOT_COMPUTABLE"
    assert any(item.code == "INVALID_NOT_COMPUTABLE" for item in report.findings)
