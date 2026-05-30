from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.metric_operator_rank3_candidate_audit import (
    LOCKED_FALSE_FLAGS,
    MetricOperatorRank3CandidateAuditValidationError,
    build_metric_operator_rank3_candidate_audit,
    default_candidate_entries,
    default_output_contract,
    serialize_metric_operator_rank3_candidate_audit,
)


def _payload() -> dict:
    return {
        "audit_id": "rank3-audit-test-001",
        "completed_operators": ["CHAMFER_DISTANCE", "WASSERSTEIN"],
        "candidate_entries": default_candidate_entries(),
        "recommended_rank3": "GEODESIC",
        "audit_status": "RANK3_CANDIDATE_SELECTED",
        "output_contract": default_output_contract(),
        "governance_flags": {k: False for k in LOCKED_FALSE_FLAGS},
        "provenance": {
            "source": "METRIC_OPERATOR_RANK3_CANDIDATE_AUDIT_TEST",
            "evidence_refs": ["MetricOperatorRegistryStabilization.v1:stabilization-001"],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/metric_operator_rank3_candidate_audit.v1.schema.json"
            ],
        },
        "created_at_utc": "2026-05-30T00:00:00Z",
    }


def test_hash_deterministic() -> None:
    a = build_metric_operator_rank3_candidate_audit(_payload())
    b = build_metric_operator_rank3_candidate_audit(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]


def test_schema_version_fixed() -> None:
    p = build_metric_operator_rank3_candidate_audit(_payload())
    assert p["schema_version"] == "MetricOperatorRank3CandidateAudit.v1"


def test_audit_type_fixed() -> None:
    p = build_metric_operator_rank3_candidate_audit(_payload())
    assert p["audit_type"] == "METRIC_OPERATOR_RANK3_CANDIDATE_AUDIT"


def test_recommended_rank3_is_geodesic() -> None:
    p = build_metric_operator_rank3_candidate_audit(_payload())
    assert p["recommended_rank3"] == "GEODESIC"


def test_exactly_one_selected_rank3() -> None:
    entries = default_candidate_entries()
    selected = [e for e in entries if e["selection_status"] == "SELECTED_RANK3"]
    assert len(selected) == 1
    assert selected[0]["operator_id"] == "GEODESIC"


def test_all_ten_candidates_present() -> None:
    entries = default_candidate_entries()
    assert len(entries) == 10


def test_candidate_entries_sorted_by_composite_rank() -> None:
    p = build_metric_operator_rank3_candidate_audit(_payload())
    ranks = [e["composite_rank"] for e in p["candidate_entries"]]
    assert ranks == sorted(ranks)


def test_geodesic_is_rank_1_in_audit() -> None:
    entries = default_candidate_entries()
    geodesic = next(e for e in entries if e["operator_id"] == "GEODESIC")
    assert geodesic["composite_rank"] == 1


def test_rejected_candidates_have_rejection_reason() -> None:
    entries = default_candidate_entries()
    for e in entries:
        if e["selection_status"] == "REJECTED":
            assert "rejection_reason" in e
            assert len(e["rejection_reason"]) > 0


def test_output_contract_no_metric_emission() -> None:
    c = default_output_contract()
    assert c["emits_metric_values"] is False
    assert c["emits_scores"] is False
    assert c["emits_forecast_inputs"] is False
    assert c["emits_authority_tokens"] is False
    assert c["emits_candidate_ranking"] is True


def test_all_governance_flags_false() -> None:
    p = build_metric_operator_rank3_candidate_audit(_payload())
    for flag in LOCKED_FALSE_FLAGS:
        assert p["governance_flags"][flag] is False


def test_canonical_hash_64_hex() -> None:
    p = build_metric_operator_rank3_candidate_audit(_payload())
    h = p["canonical_hash"]
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_completed_operators_sorted() -> None:
    payload = _payload()
    payload["completed_operators"] = ["WASSERSTEIN", "CHAMFER_DISTANCE"]
    p = build_metric_operator_rank3_candidate_audit(payload)
    assert p["completed_operators"] == sorted(p["completed_operators"])


def test_serialize_is_valid_json() -> None:
    p = build_metric_operator_rank3_candidate_audit(_payload())
    raw = serialize_metric_operator_rank3_candidate_audit(p)
    parsed = json.loads(raw)
    assert parsed["schema_version"] == "MetricOperatorRank3CandidateAudit.v1"


@pytest.mark.parametrize(
    ("mutator", "err"),
    [
        (
            lambda p: p["governance_flags"].__setitem__("execution_authority", True),
            "authority_lock_must_be_false:execution_authority",
        ),
        (
            lambda p: p.__setitem__("audit_status", "BAD_STATUS"),
            "unknown_audit_status",
        ),
        (
            lambda p: p.__setitem__("completed_operators", []),
            "completed_operators_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__("candidate_entries", []),
            "candidate_entries_must_be_non_empty",
        ),
        (
            lambda p: p.__setitem__(
                "candidate_entries",
                [e for e in default_candidate_entries() if e["operator_id"] != "GEODESIC"],
            ),
            "exactly_one_candidate_must_be_selected_rank3",
        ),
        (
            lambda p: p["provenance"].__setitem__(
                "generated_by", "bad-geodesic-distance-ref"
            ),
            "forbidden_provenance_reference_detected",
        ),
    ],
)
def test_validation_rejects_invalid(mutator, err: str) -> None:
    payload = _payload()
    mutator(payload)
    with pytest.raises(MetricOperatorRank3CandidateAuditValidationError, match=err):
        build_metric_operator_rank3_candidate_audit(payload)


def test_committed_artifact_parseable() -> None:
    path = Path("out/metric_operator/metric_operator_rank3_candidate_audit_001.latest.json")
    if not path.exists():
        pytest.skip("artifact not yet emitted")
    data = json.loads(path.read_text())
    assert data["schema_version"] == "MetricOperatorRank3CandidateAudit.v1"
    assert data["recommended_rank3"] == "GEODESIC"
    assert len(data["canonical_hash"]) == 64
