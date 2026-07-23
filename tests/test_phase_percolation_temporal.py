"""Phase 4 harness: temporal formula checker + phase percolation stubs."""

from __future__ import annotations

from core.phase_percolation_engine_stub import PhasePercolationEngine
from core.temporal_formula_checker_stub import TemporalFormulaChecker


def test_always_stable_atomic_leaf_true() -> None:
    checker = TemporalFormulaChecker()
    formula = {
        "schema_version": "TemporalFormula.v1",
        "operator": "ALWAYS",
        "operands": [{"atomic": "STABLE"}],
    }
    receipt = checker.evaluate(formula, ["STABLE", "STABLE", "STABLE"])
    assert receipt["execution_authority"] is False
    assert receipt["result"] == "TRUE"
    assert receipt["status"] == "SHADOW_EVALUATED_SUCCESS"


def test_always_stable_atomic_leaf_false_on_transition() -> None:
    checker = TemporalFormulaChecker()
    formula = {
        "schema_version": "TemporalFormula.v1",
        "operator": "ALWAYS",
        "operands": [{"atomic": "STABLE"}],
    }
    receipt = checker.evaluate(formula, ["STABLE", "TRANSITIONING", "STABLE"])
    assert receipt["result"] == "FALSE"
    assert receipt["execution_authority"] is False


def test_percolate_phase_includes_formula_evaluation() -> None:
    engine = PhasePercolationEngine()
    formula = {
        "schema_version": "TemporalFormula.v1",
        "operator": "ALWAYS",
        "operands": [{"atomic": "STABLE"}],
    }
    receipt = engine.percolate_phase(
        {"current": "P27"},
        {"input": "temporal_signal"},
        temporal_context={
            "regime_id": "P27-stable",
            "resonance_score": 0.87,
            "temporal_status": "STABLE",
        },
        temporal_formula=formula,
        regime_sequence=["STABLE", "STABLE"],
    )
    assert receipt["execution_authority"] is False
    assert receipt["status"] == "SHADOW_PERCOLATED"
    assert receipt["temporal_formula_present"] is True
    assert receipt["temporal_formula_evaluation"]["result"] == "TRUE"


def test_emit_phase_regime_packet_advisory() -> None:
    engine = PhasePercolationEngine()
    packet = engine.emit_phase_regime_packet(
        regime_id="P27-stable",
        supporting_claims=["claim-001"],
        evidence_refs=["ev-001"],
        coherence_field_hash="hash-001",
        resonance_score=0.5,
    )
    assert packet["schema_version"] == "PhaseRegimeObject.v1"
    assert packet["execution_authority"] is False
    assert packet["status"] == "OBSERVED"
