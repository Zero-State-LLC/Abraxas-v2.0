from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.chamfer_fixture_implementation_readiness_review import (
    build_chamfer_fixture_implementation_readiness_review,
    compute_chamfer_fixture_implementation_readiness_review_hash,
    default_blocker_findings,
    default_fixture_constraints,
    default_output_contract,
    default_readiness_decision,
    default_readiness_findings,
    serialize_chamfer_fixture_implementation_readiness_review,
)
from core.chamfer_invalid_fixture_implementation_plan import LOCKED_FALSE_FLAGS


def _payload() -> dict[str, object]:
    return {
        "review_id": "chamfer-fixture-implementation-readiness-review-001",
        "source_fixture_consolidation_receipt_refs": ["ChamferFixturePlanConsolidationReceipt.v1:receipt-001"],
        "source_valid_fixture_plan_refs": ["ChamferValidFixtureImplementationPlan.v1:plan-001"],
        "source_invalid_fixture_plan_refs": ["ChamferInvalidFixtureImplementationPlan.v1:plan-001"],
        "source_not_computable_fixture_plan_refs": ["ChamferNotComputableFixtureImplementationPlan.v1:plan-001"],
        "source_schema_plan_refs": ["ChamferTestVectorSchemaPlan.v1:plan-001"],
        "source_baseline_implementation_plan_refs": ["ChamferBaselineImplementationPlan.v1:plan-001"],
        "review_scope": {
            "review_family": "FIXTURE_IMPLEMENTATION_READINESS",
            "intended_lane": "SHADOW",
            "review_stage": "READINESS_REVIEW_ONLY",
        },
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "CHAMFER_FIXTURE_IMPLEMENTATION_READINESS_REVIEW_v0.1",
            "evidence_refs": ["ChamferFixturePlanConsolidationReceipt.v1:receipt-001"],
            "generated_by": "unit-test",
            "upstream_schema_refs": ["contracts/canon/chamfer_fixture_implementation_readiness_review.v1.schema.json"],
        },
        "created_at_utc": "2026-05-28T00:00:00Z",
    }


def test_deterministic_hash_and_serialization() -> None:
    a = build_chamfer_fixture_implementation_readiness_review(_payload())
    b = build_chamfer_fixture_implementation_readiness_review(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_chamfer_fixture_implementation_readiness_review(a) == serialize_chamfer_fixture_implementation_readiness_review(b)


def test_default_sections_deterministic() -> None:
    assert default_readiness_findings() == default_readiness_findings()
    assert default_blocker_findings() == default_blocker_findings()


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (lambda p: p["review_scope"].__setitem__("review_family", "BAD"), "unknown_review_family"),
        (lambda p: p["review_scope"].__setitem__("intended_lane", "BAD"), "unknown_intended_lane"),
        (lambda p: p["review_scope"].__setitem__("review_stage", "BAD"), "unknown_review_stage"),
        (lambda p: p["readiness_findings"].append(dict(p["readiness_findings"][0])), "duplicate_finding_id"),
        (lambda p: p["blocker_findings"].append(dict(p["blocker_findings"][0])), "duplicate_blocker_id"),
        (lambda p: p["readiness_findings"][0].__setitem__("finding_type", "BAD"), "unknown_finding_type"),
        (lambda p: p["readiness_findings"][0].__setitem__("readiness_status", "BAD"), "unknown_readiness_status"),
        (lambda p: p["blocker_findings"][0].__setitem__("blocker_type", "BAD"), "unknown_blocker_type"),
        (lambda p: p["blocker_findings"][0].__setitem__("blocker_status", "BAD"), "unknown_blocker_status"),
        (lambda p: p["readiness_findings"][0].__setitem__("implementation_status", "BAD"), "unknown_implementation_status"),
    ],
)
def test_scope_and_findings_failures(mutator, err: str) -> None:
    payload = _payload()
    payload["readiness_findings"] = default_readiness_findings()
    payload["blocker_findings"] = default_blocker_findings()
    mutator(payload)
    with pytest.raises(ValueError, match=err):
        build_chamfer_fixture_implementation_readiness_review(payload)


def test_locked_maps_and_flags() -> None:
    p = _payload()
    p["readiness_decision"] = default_readiness_decision()
    p["readiness_decision"]["fixture_implementation_allowed"] = True
    with pytest.raises(ValueError, match="invalid_readiness_decision"):
        build_chamfer_fixture_implementation_readiness_review(p)

    p = _payload()
    p["fixture_constraints"] = default_fixture_constraints()
    p["fixture_constraints"]["metric_values_added"] = True
    with pytest.raises(ValueError, match="invalid_fixture_constraints"):
        build_chamfer_fixture_implementation_readiness_review(p)

    p = _payload()
    p["output_contract"] = default_output_contract()
    p["output_contract"]["emits_fixture_files"] = True
    with pytest.raises(ValueError, match="invalid_output_contract"):
        build_chamfer_fixture_implementation_readiness_review(p)

    p = _payload()
    p["governance_flags"]["runtime_authority"] = True
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        build_chamfer_fixture_implementation_readiness_review(p)


def test_provenance_hash_change_and_schema() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime fixture-file expected-distance authority-flag implementation-allowed"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_chamfer_fixture_implementation_readiness_review(p)

    packet = build_chamfer_fixture_implementation_readiness_review(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_chamfer_fixture_implementation_readiness_review_hash(packet) == compute_chamfer_fixture_implementation_readiness_review_hash(altered)

    changed_payload = _payload()
    changed_payload["review_scope"]["review_stage"] = "IMPLEMENTATION_HELD"
    changed = build_chamfer_fixture_implementation_readiness_review(changed_payload)
    assert packet["canonical_hash"] != changed["canonical_hash"]

    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(Path("contracts/canon/chamfer_fixture_implementation_readiness_review.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(packet, schema)
    assert all(isinstance(x, str) and x for x in packet["provenance"]["evidence_refs"])
