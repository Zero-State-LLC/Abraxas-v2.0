"""RDI-5: synthetic fixture experiment harness."""

import copy
import json
from pathlib import Path

import pytest

from core.instantiation import run_fixture_experiment, validate_experiment_record

FIXTURES = Path("input/fixtures/instantiation/experiments")


def _spec(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.v1.json").read_text(encoding="utf-8"))


def test_experiment_fixture_specs_present():
    scenarios = {
        json.loads(path.read_text(encoding="utf-8"))["scenario"]
        for path in sorted(FIXTURES.glob("*.json"))
    }
    assert scenarios == {
        "no_intervention_matched",
        "intervention_abx_mediated",
        "unresolved_not_computable",
    }


def test_no_intervention_matched_full_loop_scores():
    record = run_fixture_experiment(_spec("no_intervention_matched"))
    validate_experiment_record(record)
    assert record["intervention"] is None
    assert record["settlement"]["verdict"]["decision"] == "TRUE"
    assert record["settlement"]["validation_status"] == "PASS"
    cal = record["calibration"]
    assert cal["status"] == "SCORED"
    assert cal["score_packet"]["observed_outcome"] == 1
    assert cal["score_packet"]["brier_score"] == pytest.approx((0.7 - 1) ** 2, abs=1e-6)
    assert cal["telemetry_only"] is True
    assert cal["feedback_contaminated"] is False
    # transition binds forecast and settlement by hash
    assert record["transition"]["forecast_ref"]["object_id"] == "forecast-exp001"
    assert record["transition"]["settlement_ref"]["canonical_hash"] == (
        record["settlement"]["verdict"]["settlement_hash"]
    )


def test_abx_mediated_intervention_scores_but_never_independent():
    record = run_fixture_experiment(_spec("intervention_abx_mediated"))
    validate_experiment_record(record)
    assert record["intervention"]["intervention_id"] == "iv-exp002"
    assert all(v is False for v in record["intervention"]["authority"].values())
    assert record["transition"]["causal_exposure"] == "ABX_MEDIATED"
    assert record["transition"]["contamination"]["feedback_contaminated"] is True
    cal = record["calibration"]
    assert cal["status"] == "SCORED"  # contaminated outcomes may settle and score
    assert cal["feedback_contaminated"] is True
    assert cal["independent_confirmation_eligible"] is False
    # SHADOW pass must surface the contamination without judging it
    codes = {f["code"] for f in record["shadow_report"]["findings"]}
    assert "CONTAMINATION_PRESENT" in codes


def test_unresolved_binding_yields_not_computable_calibration():
    record = run_fixture_experiment(_spec("unresolved_not_computable"))
    validate_experiment_record(record)
    verdict = record["settlement"]["verdict"]
    assert verdict["decision"] == "NOT_COMPUTABLE"
    assert verdict["settlement_status"] == "DRAFT"
    cal = record["calibration"]
    assert cal["status"] == "NOT_COMPUTABLE"
    assert cal["score_packet"] is None
    assert "not score-ready" in cal["not_computable_reason"]


def test_experiment_record_deterministic():
    spec = _spec("no_intervention_matched")
    assert run_fixture_experiment(spec) == run_fixture_experiment(spec)


def test_experiment_record_is_lab_shadow_and_authority_free():
    record = run_fixture_experiment(_spec("no_intervention_matched"))
    assert record["evidence_environment"] == "LAB"
    assert record["lane"] == "SHADOW"
    assert record["synthetic_fixture_only"] is True
    assert all(v is False for v in record["authority"].values())


def test_missing_spec_keys_fail_closed():
    spec = _spec("no_intervention_matched")
    del spec["binding"]
    with pytest.raises(ValueError, match="missing required keys"):
        run_fixture_experiment(spec)


def test_unknown_dimension_fails_closed():
    spec = _spec("no_intervention_matched")
    spec["baseline"]["observed_dimensions"] = ["vibes"]
    with pytest.raises(ValueError, match="unknown dimensions"):
        run_fixture_experiment(spec)


def test_tampered_record_fails_validation():
    record = run_fixture_experiment(_spec("no_intervention_matched"))

    tampered = copy.deepcopy(record)
    tampered["calibration"]["telemetry_only"] = False
    with pytest.raises(ValueError, match="telemetry_only"):
        validate_experiment_record(tampered)

    tampered = copy.deepcopy(record)
    tampered["calibration"]["independent_confirmation_eligible"] = True
    tampered["calibration"]["feedback_contaminated"] = True
    with pytest.raises(ValueError, match="independent-confirmation"):
        validate_experiment_record(tampered)

    tampered = copy.deepcopy(record)
    tampered["experiment_id"] = "spoofed"
    with pytest.raises(ValueError, match="record_hash"):
        validate_experiment_record(tampered)
