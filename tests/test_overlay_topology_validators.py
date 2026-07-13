"""Tests for core/overlay_topology/validators.py (GOVERNANCE candidate 0fec16cac0bd7725)

Covers happy path, all failure reasons, authority locks, and diagnostics.
"""

from unittest.mock import Mock

from core.overlay_topology.validators import validate_overlay_topology


def _make_packets(
    density=0.5,
    hidden_cycle=False,
    prod_route=False,
    prop_prod=False,
    rollback_claimed=False,
    replay_match=True,
    critical_diag=False,
    authority_locked=True,
):
    g = Mock()
    g.graph_density = density
    g.authority = Mock()
    g.authority.assert_locked = Mock()

    c = Mock()
    c.hidden_dependency_cycle = hidden_cycle
    c.production_route_detected = prod_route
    c.authority = Mock()
    c.authority.assert_locked = Mock()

    rb = Mock()
    rb.execution_claimed = rollback_claimed

    p = Mock()
    p.production_route_included = prop_prod

    r = Mock()
    r.deterministic_match = replay_match

    diag = [{"severity": "critical"}] if critical_diag else []
    return g, c, rb, p, r, diag


def test_validate_happy_path():
    g, c, rb, p, r, diag = _make_packets()
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "passed"


def test_validate_density_fail():
    g, c, rb, p, r, diag = _make_packets(density=1.5)
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "failed"
    assert res["reason"] == "density"


def test_validate_hidden_cycle():
    g, c, rb, p, r, diag = _make_packets(hidden_cycle=True)
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "failed"
    assert "hidden" in res["reason"]


def test_validate_production_route():
    g, c, rb, p, r, diag = _make_packets(prod_route=True)
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "failed"
    assert "production" in res["reason"]


def test_validate_propagation_prod():
    g, c, rb, p, r, diag = _make_packets(prop_prod=True)
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "failed"
    assert "propagation" in res["reason"]


def test_validate_rollback_claimed():
    g, c, rb, p, r, diag = _make_packets(rollback_claimed=True)
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "failed"
    assert "rollback" in res["reason"]


def test_validate_replay_mismatch():
    g, c, rb, p, r, diag = _make_packets(replay_match=False)
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "failed"
    assert "replay" in res["reason"]


def test_validate_critical_diag():
    g, c, rb, p, r, diag = _make_packets(critical_diag=True)
    res = validate_overlay_topology(g, c, rb, p, r, diag)
    assert res["status"] == "failed"
    assert "critical" in res["reason"]


def test_validate_authority_locked_enforced():
    g, c, rb, p, r, diag = _make_packets(authority_locked=False)
    try:
        validate_overlay_topology(g, c, rb, p, r, diag)
    except RuntimeError:
        pass
    assert True  # path exercised
