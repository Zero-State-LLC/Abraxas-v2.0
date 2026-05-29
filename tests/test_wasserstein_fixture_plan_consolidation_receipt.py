from __future__ import annotations

import pytest

from core.wasserstein_fixture_plan_consolidation_receipt import (
    build_wasserstein_fixture_plan_consolidation_receipt,
    compute_wasserstein_fixture_plan_consolidation_receipt_hash,
    default_consolidated_surfaces,
    default_consolidation_findings,
    default_fixture_constraints,
    default_output_contract,
    default_readiness_constraints,
    serialize_wasserstein_fixture_plan_consolidation_receipt,
)
from core.wasserstein_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS


def _payload() -> dict:
    return {
        "receipt_id": "wasserstein_fixture_plan_consolidation_receipt_001",
        "source_valid_fixture_plan_refs": [
            "WassersteinValidFixtureImplementationPlan.v1:"
            "wasserstein_valid_fixture_implementation_plan_001",
        ],
        "source_invalid_fixture_plan_refs": [
            "WassersteinInvalidFixtureImplementationPlan.v1:"
            "wasserstein_invalid_fixture_implementation_plan_001",
        ],
        "source_not_computable_fixture_plan_refs": [
            "WassersteinNotComputableFixtureImplementationPlan.v1:"
            "wasserstein_not_computable_fixture_implementation_plan_001",
        ],
        "source_schema_plan_refs": [
            "WassersteinTestVectorSchemaPlan.v1:wasserstein_test_vector_schema_plan_001",
        ],
        "source_dossier_refs": [
            "WassersteinDistanceImplementationReadinessDossier.v1:"
            "wasserstein_distance_implementation_readiness_dossier_001",
        ],
        "consolidation_scope": {
            "consolidation_family": "VALID_INVALID_NOT_COMPUTABLE_TRIAD",
            "intended_lane": "SHADOW",
            "consolidation_stage": "CONSOLIDATION_RECEIPT_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "P46_WASSERSTEIN_FIXTURE_PLAN_CONSOLIDATION_RECEIPT",
            "evidence_refs": [
                "WassersteinValidFixtureImplementationPlan.v1:"
                "wasserstein_valid_fixture_implementation_plan_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_fixture_plan_consolidation_receipt.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    b = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_fixture_plan_consolidation_receipt(
        a
    ) == serialize_wasserstein_fixture_plan_consolidation_receipt(b)


def test_default_surfaces_and_findings_deterministic() -> None:
    assert default_consolidated_surfaces() == default_consolidated_surfaces()
    assert default_consolidation_findings() == default_consolidation_findings()


def test_constants_enforced() -> None:
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    assert packet["schema_version"] == "WassersteinFixturePlanConsolidationReceipt.v1"
    assert packet["receipt_type"] == "WASSERSTEIN_FIXTURE_PLAN_CONSOLIDATION_RECEIPT"
    assert packet["operator_id"] == "WASSERSTEIN"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["consolidation_scope"].__setitem__(
                "consolidation_family", "BAD"
            ),
            "unknown_consolidation_family",
        ),
        (
            lambda p: p["consolidation_scope"].__setitem__("intended_lane", "BAD"),
            "unknown_intended_lane",
        ),
        (
            lambda p: p["consolidation_scope"].__setitem__("consolidation_stage", "BAD"),
            "unknown_consolidation_stage",
        ),
        (
            lambda p: p["consolidated_surfaces"].append(
                dict(p["consolidated_surfaces"][0])
            ),
            "duplicate_surface_id",
        ),
        (
            lambda p: p["consolidated_surfaces"][0].__setitem__("surface_type", "BAD"),
            "unknown_surface_type",
        ),
        (
            lambda p: p["consolidated_surfaces"][0].__setitem__(
                "consolidation_status", "BAD"
            ),
            "unknown_consolidation_status",
        ),
        (
            lambda p: p["consolidation_findings"].append(
                dict(p["consolidation_findings"][0])
            ),
            "duplicate_finding_id",
        ),
        (
            lambda p: p["consolidation_findings"][0].__setitem__("finding_type", "BAD"),
            "unknown_finding_type",
        ),
        (
            lambda p: p["consolidation_findings"][0].__setitem__("finding_status", "BAD"),
            "unknown_finding_status",
        ),
    ],
)
def test_enum_and_duplicate_failures(mutator, err: str) -> None:
    p = _payload()
    p["consolidated_surfaces"] = default_consolidated_surfaces()
    p["consolidation_findings"] = default_consolidation_findings()
    mutator(p)
    with pytest.raises(ValueError, match=err):
        build_wasserstein_fixture_plan_consolidation_receipt(p)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["readiness_constraints"] = default_readiness_constraints()
    p["readiness_constraints"]["implementation_allowed"] = True
    with pytest.raises(ValueError, match="invalid_readiness_constraints"):
        build_wasserstein_fixture_plan_consolidation_receipt(p)

    p = _payload()
    p["fixture_constraints"] = default_fixture_constraints()
    p["fixture_constraints"]["wasserstein_math_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_constraints"):
        build_wasserstein_fixture_plan_consolidation_receipt(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_wasserstein_outputs"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_wasserstein_fixture_plan_consolidation_receipt(p)

    p = _payload()
    p["governance_flags"]["execution_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_wasserstein_fixture_plan_consolidation_receipt(p)


def test_all_governance_flags_false() -> None:
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert packet["governance_flags"][flag] is False, flag


def test_output_contract_emits_receipt() -> None:
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    assert packet["output_contract"]["emits_consolidation_receipt"] is True
    assert packet["output_contract"]["emits_readiness_summary"] is True
    assert packet["output_contract"]["emits_blocker_summary"] is True
    assert packet["output_contract"]["emits_wasserstein_outputs"] is False


def test_implementation_allowed_is_false() -> None:
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    assert packet["readiness_constraints"]["implementation_allowed"] is False
    assert packet["readiness_constraints"]["operator_review_required"] is True


def test_surfaces_cover_triad() -> None:
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    types = {s["surface_type"] for s in packet["consolidated_surfaces"]}
    assert "VALID_FIXTURE_IMPLEMENTATION_PLAN" in types
    assert "INVALID_FIXTURE_IMPLEMENTATION_PLAN" in types
    assert "NOT_COMPUTABLE_FIXTURE_IMPLEMENTATION_PLAN" in types
    assert "TEST_VECTOR_SCHEMA_PLAN" in types


def test_findings_cover_governance() -> None:
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    ftypes = {f["finding_type"] for f in packet["consolidation_findings"]}
    assert "GOVERNANCE_LOCK_FINDING" in ftypes


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_fixture_plan_consolidation_receipt(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_fixture_plan_consolidation_receipt_hash(
        packet
    ) == compute_wasserstein_fixture_plan_consolidation_receipt_hash(altered)


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler metric-value"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_fixture_plan_consolidation_receipt(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["receipt_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_fixture_plan_consolidation_receipt(p)
