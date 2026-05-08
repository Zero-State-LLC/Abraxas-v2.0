from core.proposal_sandbox_routing.validators import validate_proposal_sandbox_routing


def _valid() -> dict[str, object]:
    return validate_proposal_sandbox_routing(
        "simulation",
        "route_proposed",
        "simulation_lane",
        [],
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


def test_forbidden_route_status_fails() -> None:
    out = validate_proposal_sandbox_routing(
        "simulation",
        "routed_live",
        "simulation_lane",
        [],
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
    out = validate_proposal_sandbox_routing(
        "simulation",
        "route_proposed",
        "simulation_lane",
        [],
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


def test_authority_and_auto_execution_fails() -> None:
    out = validate_proposal_sandbox_routing(
        "simulation",
        "route_proposed",
        "simulation_lane",
        [],
        True,
        [],
        False,
        True,
        False,
        False,
        False,
        True,
    )
    assert out["status"] == "failed"


def test_critical_diagnostic_and_lineage_cycle_fail() -> None:
    out = validate_proposal_sandbox_routing(
        "simulation",
        "route_proposed",
        "simulation_lane",
        [],
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


def test_forbidden_action_and_prod_execution_deployment_leaks_fail() -> None:
    out = validate_proposal_sandbox_routing(
        "simulation",
        "route_proposed",
        "simulation_lane",
        ["execute"],
        True,
        [],
        False,
        False,
        True,
        True,
        True,
        False,
    )
    assert out["status"] == "failed"
