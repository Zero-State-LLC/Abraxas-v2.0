from __future__ import annotations

import json
from pathlib import Path

from core.canonical.json import canonical_hash
from core.hyperstition_evaluator_deepening import (
    BRIER_SCORE,
    DEFAULT_OUT_PATH,
    STATUS,
    WEIGHT_POLICY,
    HyperstitionEvaluator,
    build_hyperstition_evaluator_deepening_receipt,
)
from scripts.belief.run_hyperstition_evaluator_deepening_receipt import run


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_hyperstition_evaluator_deepening_preserves_authority_locks() -> None:
    packet = build_hyperstition_evaluator_deepening_receipt(repo_root=REPO_ROOT)

    assert packet["status"] == STATUS
    assert packet["brier_score"] == BRIER_SCORE
    assert packet["advisory_only"] is True
    assert packet["projection_only"] is True
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["boundary"]["sandbox_gate_issued"] is False
    assert packet["boundary"]["forecast_execution"] is False
    assert packet["boundary"]["brier_resolution"] is False


def test_hyperstition_evaluator_deepening_hash_is_canonical() -> None:
    packet = build_hyperstition_evaluator_deepening_receipt(repo_root=REPO_ROOT)
    without_hash = {
        key: value for key, value in packet.items() if key != "canonical_hash"
    }

    assert packet["canonical_hash"] == canonical_hash(without_hash)


def test_hyperstition_evaluator_uses_expected_weight_policy() -> None:
    evaluation = HyperstitionEvaluator(REPO_ROOT).evaluate()

    assert evaluation["weight_policy"] == WEIGHT_POLICY
    assert sum(evaluation["weight_policy"].values()) == 1.0
    assert 0.0 <= evaluation["source_confidence"] <= 1.0
    assert 0.0 <= evaluation["loop_dynamics"]["hyperstitional_charge"] <= 1.0
    assert 0.0 <= evaluation["loop_dynamics"]["retrocausal_risk"] <= 1.0


def test_hyperstition_evaluator_records_required_signals() -> None:
    packet = build_hyperstition_evaluator_deepening_receipt(repo_root=REPO_ROOT)
    signals = packet["evaluation"]["signals"]

    assert set(signals) == {
        "temporal_coherence_contribution",
        "geometric_binding_strength",
        "cross_aal_resonance_weight",
        "decision_provenance_weight",
    }
    assert signals["temporal_coherence_contribution"]["authority_granted"] is False
    assert signals["geometric_binding_strength"]["authority_granted"] is False
    assert signals["cross_aal_resonance_weight"]["authority_granted"] is False
    assert signals["decision_provenance_weight"]["sandbox_gate_issued"] is False


def test_hyperstition_evaluator_missing_sources_fail_closed(tmp_path: Path) -> None:
    packet = build_hyperstition_evaluator_deepening_receipt(repo_root=tmp_path)

    assert packet["source_status"] == "NOT_COMPUTABLE"
    assert packet["observed_signal_count"] == 0
    assert packet["evaluation"]["source_confidence"] == 0.0
    assert all(value is False for value in packet["authority_locks"].values())
    assert packet["canonical_hash"] == canonical_hash(
        {key: value for key, value in packet.items() if key != "canonical_hash"}
    )


def test_hyperstition_evaluator_fixture_suite_is_advisory() -> None:
    packet = build_hyperstition_evaluator_deepening_receipt(repo_root=REPO_ROOT)
    suite = packet["evaluator_fixture_suite"]

    assert suite["fixture_count"] == 4
    assert 0.0 <= suite["mean_shadow_brier"] <= 1.0
    assert suite["forecast_execution_allowed"] is False
    assert suite["outcome_binding_allowed"] is False
    assert suite["resolution_allowed"] is False
    for row in suite["fixture_rows"]:
        assert 0.0 <= row["probability"] <= 1.0
        assert 0.0 <= row["shadow_brier_component"] <= 1.0
        assert row["forecast_execution_allowed"] is False
        assert row["outcome_binding_allowed"] is False
        assert row["brier_resolution_allowed"] is False


def test_hyperstition_evaluator_runner_writes_receipt(tmp_path: Path) -> None:
    out_path = tmp_path / "receipt.latest.json"
    packet = run(repo_root=REPO_ROOT, out_path=out_path)
    written = json.loads(out_path.read_text(encoding="utf-8"))

    assert out_path.exists()
    assert written == packet
    assert written["status"] == STATUS
    assert written["canonical_hash"] == packet["canonical_hash"]
    assert DEFAULT_OUT_PATH.endswith(".latest.json")
