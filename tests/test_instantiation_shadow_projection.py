"""RDI-4: anomaly-only SHADOW detection and projection-only view."""

import pytest

from core.instantiation import (
    DIMENSIONS,
    build_instantiation_projection,
    build_instantiation_state,
    build_instantiation_transition,
    detect_instantiation_anomalies,
    validate_instantiation_projection,
    validate_instantiation_shadow_report,
)

HASH_A = "a" * 64


def _dimensions(observed: set[str] | None = None):
    observed = observed or set()
    return [
        {
            "name": name,
            "epistemic_status": "OBSERVED" if name in observed else "NOT_COMPUTABLE",
            "claim_refs": [f"claim:{name}"] if name in observed else [],
            "evidence_refs": [f"evidence:{name}"] if name in observed else [],
            "not_computable_reason": None if name in observed else "fixture evidence absent",
        }
        for name in DIMENSIONS
    ]


def _state(state_id="is-t0", observed=None, exposure="UNKNOWN", window="fixture-t0"):
    return build_instantiation_state(
        state_id=state_id,
        construct_id="cfar-fixture",
        construct_hash=HASH_A,
        observation_start=window,
        observation_end=window,
        dimensions=_dimensions(observed),
        causal_exposure=exposure,
    )


def _transition(prior, later, changes, exposure="EXOGENOUS", reasons=()):
    return build_instantiation_transition(
        transition_id="it-1",
        prior_state_id=prior["state_id"],
        prior_state_hash=prior["state_hash"],
        later_state_id=later["state_id"],
        later_state_hash=later["state_hash"],
        dimension_changes=changes,
        causal_exposure=exposure,
        contamination_reasons=reasons,
    )


def _change(dimension, kind, status="OBSERVED"):
    return {
        "dimension": dimension,
        "change_kind": kind,
        "epistemic_status": status,
        "claim_refs": [f"claim:{dimension}"],
        "evidence_refs": [f"evidence:{dimension}"],
        "not_computable_reason": None,
    }


def _codes(report):
    return {f["code"] for f in report["findings"]}


def test_shadow_report_deterministic_and_valid():
    state = _state(observed={"symbolic_persistence"}, exposure="EXOGENOUS")
    r1 = detect_instantiation_anomalies([state], report_id="isr-1")
    r2 = detect_instantiation_anomalies([state], report_id="isr-1")
    assert r1 == r2
    validate_instantiation_shadow_report(r1)
    assert r1["lane"] == "SHADOW"
    assert all(v is False for v in r1["authority"].values())


def test_missing_evidence_and_unknown_exposure_detected_as_observations():
    report = detect_instantiation_anomalies([_state()], report_id="isr-1")
    assert "MISSING_EVIDENCE" in _codes(report)
    assert "EXPOSURE_UNKNOWN" in _codes(report)
    assert report["anomaly_count"] == 0  # observations only; nothing anomalous


def test_reinforcement_without_consequence_evidence_is_anomaly():
    state = _state(observed={"recursive_reinforcement", "symbolic_persistence"})
    report = detect_instantiation_anomalies([state], report_id="isr-1")
    assert "REINFORCEMENT_WITHOUT_CONSEQUENCE_EVIDENCE" in _codes(report)


def test_reinforcement_with_consequence_evidence_not_flagged():
    state = _state(observed={"recursive_reinforcement", "behavioral_consequence"})
    report = detect_instantiation_anomalies([state], report_id="isr-1")
    assert "REINFORCEMENT_WITHOUT_CONSEQUENCE_EVIDENCE" not in _codes(report)


def test_regression_and_unexplained_decay_detected():
    prior = _state("is-t0", observed={"behavioral_consequence", "symbolic_persistence"}, window="fixture-t0")
    later = _state("is-t1", observed={"behavioral_consequence"}, window="fixture-t1")
    transition = _transition(prior, later, [_change("behavioral_consequence", "DECREASED")])
    report = detect_instantiation_anomalies([prior, later], [transition], report_id="isr-1")
    codes = _codes(report)
    assert "DIMENSION_REGRESSION" in codes
    # symbolic_persistence went OBSERVED -> NOT_COMPUTABLE with no declared change
    assert "UNEXPLAINED_EVIDENCE_DECAY" in codes


def test_change_without_later_evidence_detected():
    prior = _state("is-t0", observed={"symbolic_persistence"}, window="fixture-t0")
    later = _state("is-t1", observed={"symbolic_persistence"}, window="fixture-t1")
    transition = _transition(prior, later, [_change("behavioral_consequence", "INCREASED")])
    report = detect_instantiation_anomalies([prior, later], [transition], report_id="isr-1")
    assert "CHANGE_WITHOUT_LATER_EVIDENCE" in _codes(report)


def test_contamination_and_exposure_conflict_detected():
    prior = _state("is-t0", observed={"symbolic_persistence"}, window="fixture-t0")
    later = _state("is-t1", observed={"symbolic_persistence"}, window="fixture-t1")
    transition = _transition(
        prior,
        later,
        [_change("symbolic_persistence", "UNCHANGED")],
        exposure="EXOGENOUS",
        reasons=("abx recommendation preceded observation",),
    )
    report = detect_instantiation_anomalies([prior, later], [transition], report_id="isr-1")
    codes = _codes(report)
    assert "CONTAMINATION_PRESENT" in codes
    assert "EXPOSURE_CONTAMINATION_CONFLICT" in codes


def test_unresolved_state_ref_detected():
    prior = _state("is-t0", observed={"symbolic_persistence"}, window="fixture-t0")
    later = _state("is-t1", observed={"symbolic_persistence"}, window="fixture-t1")
    transition = _transition(prior, later, [_change("symbolic_persistence", "UNCHANGED")])
    report = detect_instantiation_anomalies([prior], [transition], report_id="isr-1")
    assert "STATE_REF_UNRESOLVED" in _codes(report)


def test_tampered_report_fails_validation():
    report = detect_instantiation_anomalies([_state()], report_id="isr-1")
    tampered = dict(report)
    tampered["finding_count"] = 0
    with pytest.raises(ValueError):
        validate_instantiation_shadow_report(tampered)


def test_projection_view_deterministic_valid_and_projection_only():
    prior = _state("is-t0", observed={"symbolic_persistence"}, window="fixture-t0")
    later = _state("is-t1", observed={"symbolic_persistence"}, window="fixture-t1")
    transition = _transition(prior, later, [_change("symbolic_persistence", "UNCHANGED")])
    shadow = detect_instantiation_anomalies([prior, later], [transition], report_id="isr-1")
    v1 = build_instantiation_projection([prior, later], [transition], view_id="ipv-1", shadow_report=shadow)
    v2 = build_instantiation_projection([prior, later], [transition], view_id="ipv-1", shadow_report=shadow)
    assert v1 == v2
    validate_instantiation_projection(v1)
    assert v1["lane"] == "PROJECTION"
    assert v1["authority"]["projection_only"] is True
    assert v1["authority"]["execution_authority"] is False


def test_projection_timeline_ordered_and_lineage_linked():
    prior = _state("is-t0", observed={"symbolic_persistence"}, window="fixture-t0")
    later = _state("is-t1", observed={"symbolic_persistence"}, window="fixture-t1")
    transition = _transition(prior, later, [_change("symbolic_persistence", "UNCHANGED")])
    view = build_instantiation_projection([later, prior], [transition], view_id="ipv-1")
    timeline = view["construct_timelines"][0]
    assert [s["state_id"] for s in timeline["states"]] == ["is-t0", "is-t1"]
    edge = view["lineage_edges"][0]
    assert edge["from_state_id"] == "is-t0"
    assert edge["to_state_id"] == "is-t1"
    assert view["unresolved_state_ids"] == []
    assert view["shadow_overlay"] is None


def test_projection_reports_unresolved_states_without_failing():
    prior = _state("is-t0", observed={"symbolic_persistence"}, window="fixture-t0")
    later = _state("is-t1", observed={"symbolic_persistence"}, window="fixture-t1")
    transition = _transition(prior, later, [_change("symbolic_persistence", "UNCHANGED")])
    view = build_instantiation_projection([prior], [transition], view_id="ipv-1")
    assert view["unresolved_state_ids"] == ["is-t1"]


def test_projection_never_invents_depth_or_scores():
    view = build_instantiation_projection([_state()], view_id="ipv-1")
    tile = view["construct_timelines"][0]["states"][0]
    assert tile["aggregate_instantiation_depth"] == "NOT_COMPUTABLE"
    assert "score" not in str(sorted(tile)).lower()


def test_tampered_projection_fails_validation():
    view = build_instantiation_projection([_state()], view_id="ipv-1")
    tampered = dict(view)
    tampered["lane"] = "FORECAST"
    with pytest.raises(ValueError):
        validate_instantiation_projection(tampered)
