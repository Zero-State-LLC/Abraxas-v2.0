from core.human_decision_ledger.validators import validate_human_decision_ledger


def _valid() -> dict[str, object]:
    return validate_human_decision_ledger(
        "review_only",
        True,
        [],
        False,
        False,
        False,
        False,
        False,
        False,
    )


def test_nominal_passes() -> None:
    assert _valid()["status"] == "passed"


def test_forbidden_decision_state_fails() -> None:
    out = validate_human_decision_ledger(
        "approved_live",
        True,
        [],
        False,
        False,
        False,
        False,
        False,
        False,
    )
    assert out["status"] == "failed"


def test_replay_mismatch_fails() -> None:
    out = validate_human_decision_ledger(
        "review_only",
        False,
        [],
        False,
        False,
        False,
        False,
        False,
        False,
    )
    assert out["status"] == "failed"


def test_authority_mutation_and_privilege_leaks_fail() -> None:
    out = validate_human_decision_ledger(
        "review_only",
        True,
        [],
        False,
        True,
        True,
        True,
        True,
        True,
    )
    assert out["status"] == "failed"


def test_critical_diagnostic_and_lineage_cycle_fail() -> None:
    out = validate_human_decision_ledger(
        "review_only",
        True,
        [{"severity": "critical", "resolved": False}],
        True,
        False,
        False,
        False,
        False,
        False,
    )
    assert out["status"] == "failed"
