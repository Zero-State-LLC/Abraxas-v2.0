from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_fixture_plan_consolidation_receipt import (
    build_chamfer_fixture_plan_consolidation_receipt,
    compute_chamfer_fixture_plan_consolidation_receipt_hash,
    default_consolidated_surfaces,
    default_consolidation_findings,
    default_fixture_constraints,
    default_output_contract,
    default_readiness_constraints,
    serialize_chamfer_fixture_plan_consolidation_receipt,
)
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS


def _payload() -> dict[str, object]:
    return {
        "receipt_id": "chamfer-fixture-plan-consolidation-receipt-001",
        "source_valid_fixture_plan_refs": ["ChamferValidFixtureImplementationPlan.v1:plan-001"],
        "source_invalid_fixture_plan_refs": ["ChamferInvalidFixtureImplementationPlan.v1:plan-001"],
        "source_not_computable_fixture_plan_refs": ["ChamferNotComputableFixtureImplementationPlan.v1:plan-001"],
        "source_schema_plan_refs": ["ChamferTestVectorSchemaPlan.v1:plan-001"],
        "source_baseline_implementation_plan_refs": ["ChamferBaselineImplementationPlan.v1:plan-001"],
        "consolidation_scope": {
            "consolidation_family": "VALID_INVALID_NOT_COMPUTABLE_TRIAD",
            "intended_lane": "SHADOW",
            "consolidation_stage": "CONSOLIDATION_RECEIPT_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "CHAMFER_FIXTURE_PLAN_CONSOLIDATION_RECEIPT_v0.1",
            "evidence_refs": ["ChamferNotComputableFixtureImplementationPlan.v1:plan-001"],
            "generated_by": "unit-test",
            "upstream_schema_refs": ["contracts/canon/chamfer_fixture_plan_consolidation_receipt.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_fixture_plan_consolidation_receipt(_payload())
    b = build_chamfer_fixture_plan_consolidation_receipt(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_fixture_plan_consolidation_receipt(a) == serialize_chamfer_fixture_plan_consolidation_receipt(b)


def test_default_sections_deterministic() -> None:
    assert default_consolidated_surfaces() == default_consolidated_surfaces()
    assert default_consolidation_findings() == default_consolidation_findings()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["consolidation_scope"].__setitem__("consolidation_family", "BAD"), "unknown_consolidation_family"),
        (lambda p: p["consolidation_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["consolidation_scope"].__setitem__("consolidation_stage", "BAD"), "unknown_consolidation_stage"),
        (lambda p: p["consolidated_surfaces"].append(dict(p["consolidated_surfaces"][0])), "duplicate_surface_id"),
        (lambda p: p["consolidation_findings"].append(dict(p["consolidation_findings"][0])), "duplicate_finding_id"),
        (lambda p: p["consolidated_surfaces"][0].__setitem__("surface_type", "BAD"), "unknown_surface_type"),
        (lambda p: p["consolidated_surfaces"][0].__setitem__("consolidation_status", "BAD"), "unknown_consolidation_status"),
        (lambda p: p["consolidation_findings"][0].__setitem__("finding_type", "BAD"), "unknown_finding_type"),
        (lambda p: p["consolidation_findings"][0].__setitem__("finding_status", "BAD"), "unknown_finding_status"),
        (lambda p: p["consolidated_surfaces"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
    ],
)
def test_scope_surface_and_finding_failures(mutator, err: str) -> None:
    payload = _payload()
    payload["consolidated_surfaces"] = default_consolidated_surfaces()
    payload["consolidation_findings"] = default_consolidation_findings()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_chamfer_fixture_plan_consolidation_receipt(payload)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["readiness_constraints"] = default_readiness_constraints()
    p["readiness_constraints"]["implementation_allowed"] = True
    with pytest.raises(ValueError, match="invalid_readiness_constraints"):
        build_chamfer_fixture_plan_consolidation_receipt(p)

    p = _payload()
    p["fixture_constraints"] = default_fixture_constraints()
    p["fixture_constraints"]["metric_values_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_constraints"):
        build_chamfer_fixture_plan_consolidation_receipt(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_fixture_files"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_chamfer_fixture_plan_consolidation_receipt(p)

    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_chamfer_fixture_plan_consolidation_receipt(p)


def test_provenance_hash_change_and_schema() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime fixture-file expected-distance authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_chamfer_fixture_plan_consolidation_receipt(p)

    packet = build_chamfer_fixture_plan_consolidation_receipt(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_fixture_plan_consolidation_receipt_hash(packet) == compute_chamfer_fixture_plan_consolidation_receipt_hash(altered)

    changed_payload = _payload()
    changed_payload["consolidation_scope"]["consolidation_stage"] = "READINESS_SUMMARY_ONLY"
    changed = build_chamfer_fixture_plan_consolidation_receipt(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_fixture_plan_consolidation_receipt.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
    assert all(isinstance(x, str) and x for x in packet["provenance"]["evidence_refs"])
