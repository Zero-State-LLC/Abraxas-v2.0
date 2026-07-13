"""Tests for core/norm_geometry_computation_implementation_gate.py (HARDENING candidate 9de38ad964c167b8)"""

from core.norm_geometry_computation_implementation_gate import (
    _check_no_forbidden,
    build_authorized_implementation_scope,
    build_valid_fixture_scope,
    build_rejection_fixture_scope,
    build_no_metric_emission_block,
    NormGeometryComputationImplementationGateValidationError,
)

def test_build_authorized_implementation_scope():
    locked = {"float64_precision_declaration": "IEEE-754"}
    scope = build_authorized_implementation_scope(locked)
    assert scope["authorized_lane"] == "SHADOW"
    assert scope["bounded_scope_only"] is True
    assert "locked_constants_binding" in scope

def test_build_valid_and_rejection_scopes():
    valid = build_valid_fixture_scope()
    assert valid["fixture_count"] == 6
    assert "ng.valid.v001_l1_norm" in valid["fixture_ids"]

    rej = build_rejection_fixture_scope()
    assert rej["invalid_fixture_count"] == 4
    assert rej["not_computable_fixture_count"] == 4

def test_no_metric_emission_block():
    block = build_no_metric_emission_block()
    assert block["emits_metric_values"] is False
    assert block["metric_emission_blocked"] is True

def test_forbidden_token_checker():
    _check_no_forbidden({"key": "safe value"})
    try:
        _check_no_forbidden({"bad": "this contains numpy call"})
        assert False, "should have raised"
    except NormGeometryComputationImplementationGateValidationError:
        pass
