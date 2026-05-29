from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from core.wasserstein_test_vector_fixture_schema_validation_execution import (
    SOURCE_COMPLETE_REVIEW_HASH,
    SOURCE_VALIDATION_PLAN_HASH,
    build_wasserstein_test_vector_fixture_schema_validation_execution,
    compute_wasserstein_test_vector_fixture_schema_validation_execution_hash,
    default_authority_locks,
    default_blocked_scopes,
    serialize_wasserstein_test_vector_fixture_schema_validation_execution,
)

FIXTURE_ROOT = Path("input/fixtures/wasserstein")


def _payload() -> dict:
    return {
        "execution_id": (
            "wasserstein_test_vector_fixture_schema_validation_execution_001"
        ),
        "intended_lane": "SHADOW",
        "execution_stage": "FIXTURE_SCHEMA_VALIDATION_EXECUTION_ONLY",
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "recommended_next_step": (
            "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_COMPLETE_REVIEW"
        ),
        "provenance": {
            "source": (
                "P55_WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTION"
            ),
            "evidence_refs": [
                "WassersteinTestVectorFixtureSchemaValidationPlan.v1:"
                "wasserstein_test_vector_fixture_schema_validation_plan_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_schema_validation_execution"
                ".v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash() -> None:
    a = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    b = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert a["canonical_hash"] == b["canonical_hash"]


def test_deterministic_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    b = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert serialize_wasserstein_test_vector_fixture_schema_validation_execution(
        a
    ) == serialize_wasserstein_test_vector_fixture_schema_validation_execution(b)


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorFixtureSchemaValidationExecution.v1"
    )
    assert (
        packet["execution_type"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTION"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_validation_plan_hash"] == SOURCE_VALIDATION_PLAN_HASH
    assert packet["source_complete_review_hash"] == SOURCE_COMPLETE_REVIEW_HASH
    assert packet["intended_lane"] == "SHADOW"
    assert packet["execution_stage"] == "FIXTURE_SCHEMA_VALIDATION_EXECUTION_ONLY"


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------


def test_fixture_schema_validation_executed_true() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert packet["authority_locks"]["fixture_schema_validation_executed"] is True


def test_wasserstein_computation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is False


def test_execution_only_lock_true() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert packet["authority_locks"]["fixture_schema_validation_execution_only"] is True


def test_executed_false_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["fixture_schema_validation_executed"] = False
    p["authority_locks"] = al
    with pytest.raises(
        ValueError, match="fixture_schema_validation_executed_must_be_true"
    ):
        build_wasserstein_test_vector_fixture_schema_validation_execution(
            p, FIXTURE_ROOT
        )


def test_computation_authorized_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["wasserstein_computation_authorized"] = True
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="wasserstein_computation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_schema_validation_execution(
            p, FIXTURE_ROOT
        )


def test_authority_locks_mutation_raises() -> None:
    p = _payload()
    al = default_authority_locks()
    al["advisory_only"] = False
    p["authority_locks"] = al
    with pytest.raises(ValueError, match="invalid_authority_locks"):
        build_wasserstein_test_vector_fixture_schema_validation_execution(
            p, FIXTURE_ROOT
        )


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    bs = default_blocked_scopes()
    bs["emits_metric_values"] = True
    p["blocked_scopes"] = bs
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_schema_validation_execution(
            p, FIXTURE_ROOT
        )


# ---------------------------------------------------------------------------
# Corpus execution — live fixture files
# ---------------------------------------------------------------------------


def test_all_14_fixtures_parsed() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert packet["fixture_parse_results"]["total_files"] == 14
    assert packet["fixture_parse_results"]["parsed_ok"] == 14
    assert packet["fixture_parse_results"]["parse_failures"] == []


def test_all_14_fixtures_pass() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert packet["validation_summary"]["passed"] == 14
    assert packet["validation_summary"]["failed"] == 0
    assert packet["validation_summary"]["all_checks_passed"] is True


def test_valid_fixture_results_count() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert len(packet["valid_fixture_schema_results"]) == 5
    for r in packet["valid_fixture_schema_results"]:
        assert r["status"] == "PASS", f'{r["file"]} failed: {r["checks_failed"]}'
        assert r["fixture_type"] == "VALID"


def test_invalid_fixture_results_count() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert len(packet["invalid_fixture_schema_results"]) == 5
    for r in packet["invalid_fixture_schema_results"]:
        assert r["status"] == "PASS", f'{r["file"]} failed: {r["checks_failed"]}'
        assert r["fixture_type"] == "INVALID"
        assert r.get("rejection_reason"), f'{r["file"]} missing rejection_reason'


def test_nc_fixture_results_count() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert len(packet["not_computable_fixture_schema_results"]) == 4
    for r in packet["not_computable_fixture_schema_results"]:
        assert r["status"] == "PASS", f'{r["file"]} failed: {r["checks_failed"]}'
        assert r["fixture_type"] == "NOT_COMPUTABLE"
        assert r.get("rejection_reason"), f'{r["file"]} missing rejection_reason'


def test_no_metric_value_violations() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    scan = packet["no_metric_value_scan_results"]
    assert scan["all_false"] is True
    assert scan["violations"] == []
    assert scan["total_checked"] == 14


def test_no_expected_distance_violations() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    scan = packet["no_expected_distance_scan_results"]
    assert scan["all_false"] is True
    assert scan["violations"] == []
    assert scan["total_checked"] == 14


def test_authority_lock_scan_all_pinned() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    auth = packet["authority_lock_scan_results"]
    assert auth["gate_hash_pinned_all"] is True
    assert auth["intended_lane_shadow_all"] is True
    assert auth["creation_authorized_all"] is True
    assert auth["violations"] == []
    assert auth["total_checked"] == 14


def test_execution_status_executed() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert (
        packet["validation_summary"]["execution_status"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_SCHEMA_VALIDATION_EXECUTED"
    )


def test_valid_passed_summary() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    assert packet["validation_summary"]["valid_passed"] == 5
    assert packet["validation_summary"]["invalid_passed"] == 5
    assert packet["validation_summary"]["not_computable_passed"] == 4


# ---------------------------------------------------------------------------
# Failure path — tampered fixture root
# ---------------------------------------------------------------------------


def test_bad_fixture_fails_validation() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "valid").mkdir()
        (root / "invalid").mkdir()
        (root / "not_computable").mkdir()
        bad = {
            "fixture_type": "VALID",
            "fixture_group": "DISTRIBUTION_PAIR_SCHEMA",
            "fixture_id": "valid-001",
            "source_gate_hash": "badhash",
            "metric_value_emitted": False,
            "expected_wasserstein_distance_included": False,
            "intended_lane": "SHADOW",
            "fixture_creation_authorized": True,
            "schema_version": "WassersteinTestVectorFixture.v1",
            "created_at_utc": "2026-05-29T00:00:00Z",
            "input": {},
        }
        (root / "valid" / "valid_001.json").write_text(
            json.dumps(bad, sort_keys=True, indent=2) + "\n"
        )
        for i in range(2, 6):
            (root / "valid" / f"valid_00{i}.json").write_text(
                json.dumps(bad, sort_keys=True, indent=2) + "\n"
            )
        for i in range(1, 6):
            inv = dict(bad)
            inv.update({"fixture_type": "INVALID", "fixture_group": "MISSING_REQUIRED_FIELD", "rejection_reason": "missing_required_field: x"})
            (root / "invalid" / f"invalid_00{i}.json").write_text(
                json.dumps(inv, sort_keys=True, indent=2) + "\n"
            )
        for i in range(1, 5):
            nc = dict(bad)
            nc.update({"fixture_type": "NOT_COMPUTABLE", "fixture_group": "EMPTY_INPUT", "rejection_reason": "not_computable: empty"})
            (root / "not_computable" / f"nc_00{i}.json").write_text(
                json.dumps(nc, sort_keys=True, indent=2) + "\n"
            )
        with pytest.raises(ValueError, match="validation_checks_not_all_passed"):
            build_wasserstein_test_vector_fixture_schema_validation_execution(
                _payload(), root
            )


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert (
        compute_wasserstein_test_vector_fixture_schema_validation_execution_hash(packet)
        == compute_wasserstein_test_vector_fixture_schema_validation_execution_hash(
            altered
        )
    )


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_schema_validation_execution(
        _payload(), FIXTURE_ROOT
    )
    b = build_wasserstein_test_vector_fixture_schema_validation_execution(
        p2, FIXTURE_ROOT
    )
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "scoring metric-value authority-flag"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_schema_validation_execution(
            p, FIXTURE_ROOT
        )


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["execution_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_schema_validation_execution(
            p, FIXTURE_ROOT
        )


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("execution_stage", "ACTIVE", "unknown_execution_stage"),
    ],
)
def test_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_fixture_schema_validation_execution(
            p, FIXTURE_ROOT
        )
