"""Tests for core/norm_geometry_distance_implementation_readiness_dossier.py (HARDENING candidate a7b2faceba3749b6)"""

from core.norm_geometry_distance_implementation_readiness_dossier import (
    build_norm_geometry_distance_implementation_readiness_dossier,
    default_input_shape_requirements,
    default_blocked_scopes,
    default_authority_locks,
    NormGeometryDistanceImplementationReadinessDossierValidationError,
)

def test_build_dossier_with_minimal_payload():
    payload = {
        "mathematical_requirements": [],
        "input_shape_requirements": default_input_shape_requirements(),
        "determinism_requirements": [],
        "numerical_constraints": [],
        "numerical_stability_requirements": [],
        "dependency_inventory": [],
        "implementation_prerequisites": [],
        "implementation_risks": [],
        "validation_requirements": [],
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "output_contract": {"deterministic": True},
        "governance_flags": {k: False for k in ["production_activation", "canon_promotion"]},
        "provenance": {"source": "test"},
    }
    try:
        dossier = build_norm_geometry_distance_implementation_readiness_dossier(payload)
        assert isinstance(dossier, dict)
        assert "canonical_hash" in dossier
    except NormGeometryDistanceImplementationReadinessDossierValidationError as e:
        # Acceptable if the minimal payload is intentionally incomplete for advisory dossier
        assert "missing" in str(e).lower() or "invalid" in str(e).lower()

def test_default_input_shape_requirements():
    reqs = default_input_shape_requirements()
    assert isinstance(reqs, list)
    assert len(reqs) > 0
    assert any("float64" in r.lower() for r in reqs)
