from scripts.run_doctrine_validator import _build_summary


def test_seal_recommendation_hold_for_legacy_only() -> None:
    summary = _build_summary([{"status": "legacy_contract_posture"}])
    assert summary["seal_recommendation"] == "hold"


def test_seal_recommendation_repair_for_repair_required() -> None:
    summary = _build_summary([{"status": "legacy_contract_posture"}, {"status": "repair_required"}])
    assert summary["seal_recommendation"] == "repair"
