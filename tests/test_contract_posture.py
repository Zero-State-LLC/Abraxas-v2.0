from scripts.governance.run_doctrine_validator import _build_summary


def test_seal_recommendation_hold_for_legacy_only() -> None:
    summary = _build_summary([{"status": "legacy_contract_posture"}])
    assert summary["seal_recommendation"] == "hold"


def test_seal_recommendation_repair_for_repair_required() -> None:
    summary = _build_summary([{"status": "legacy_contract_posture"}, {"status": "repair_required"}])
    assert summary["seal_recommendation"] == "repair"


def test_seal_recommendation_repair_for_extended_overlay_gate_failure() -> None:
    """Extended overlay gates (beyond the five base governance gates) must block seal."""
    summary = _build_summary(
        [{"status": "doctrine_compliant"}],
        overlay_governance_status={"overlay_risk_replay_gate": "failed"},
    )
    assert summary["overlay_risk_replay_gate"] == "failed"
    assert summary["failed_count"] >= 1
    assert summary["status"] == "failed"
    assert summary["seal_recommendation"] == "repair"


def test_seal_recommendation_repair_for_base_overlay_gate_failure() -> None:
    """Base overlay governance failures must not leave seal_recommendation=seal."""
    summary = _build_summary(
        [{"status": "doctrine_compliant"}],
        overlay_governance_status={"replay_gate": "failed"},
    )
    assert summary["overlay_governance_replay_gate"] == "failed"
    assert summary["failed_count"] >= 1
    assert summary["status"] == "failed"
    assert summary["seal_recommendation"] == "repair"


def test_seal_recommendation_repair_for_external_action_gate_failure() -> None:
    summary = _build_summary(
        [],
        overlay_governance_status={"external_action_replay_gate": "failed"},
    )
    assert summary["external_action_replay_gate"] == "failed"
    assert summary["failed_count"] >= 1
    assert summary["status"] == "failed"
    assert summary["seal_recommendation"] == "repair"
