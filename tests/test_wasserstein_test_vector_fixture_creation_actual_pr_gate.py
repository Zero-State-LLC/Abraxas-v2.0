from __future__ import annotations

import pytest

from core.wasserstein_test_vector_fixture_creation_actual_pr_gate import (
    SOURCE_AUTHORIZATION_REVIEW_HASH,
    SOURCE_OPERATOR_DECISION_HASH,
    SOURCE_OPERATOR_DECISION_ID,
    build_wasserstein_test_vector_fixture_creation_actual_pr_gate,
    compute_wasserstein_test_vector_fixture_creation_actual_pr_gate_hash,
    default_authority_locks,
    default_authorized_batches,
    default_authorized_fixture_manifest,
    default_blocked_scopes,
    default_fixture_creation_constraints,
    serialize_wasserstein_test_vector_fixture_creation_actual_pr_gate,
)


def _payload() -> dict:
    return {
        "gate_id": "wasserstein_test_vector_fixture_creation_actual_pr_gate_001",
        "intended_lane": "SHADOW",
        "gate_stage": "FIXTURE_CREATION_ACTUAL_PR_GATE_ONLY",
        "recommended_next_step": "WASSERSTEIN_TEST_VECTOR_FIXTURE_FILE_CREATION_PR",
        "provenance": {
            "source": "P51_WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_ACTUAL_PR_GATE",
            "evidence_refs": [
                "WassersteinFixtureCreationOperatorDecision:"
                "WASSERSTEIN_FIXTURE_CREATION_OPERATOR_DECISION_2026_05_29_001",
            ],
            "generated_by": "unit_test",
            "upstream_schema_refs": [
                "contracts/canon/"
                "wasserstein_test_vector_fixture_creation_actual_pr_gate.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_deterministic_hash_and_serialization() -> None:
    a = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    b = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    assert a["canonical_hash"] == b["canonical_hash"]
    assert serialize_wasserstein_test_vector_fixture_creation_actual_pr_gate(
        a
    ) == serialize_wasserstein_test_vector_fixture_creation_actual_pr_gate(b)


def test_default_sub_structures_deterministic() -> None:
    assert default_authorized_fixture_manifest() == default_authorized_fixture_manifest()
    assert default_authorized_batches() == default_authorized_batches()
    assert default_fixture_creation_constraints() == default_fixture_creation_constraints()


# ---------------------------------------------------------------------------
# Constants enforced
# ---------------------------------------------------------------------------


def test_constants_enforced() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    assert (
        packet["schema_version"]
        == "WassersteinTestVectorFixtureCreationActualPRGate.v1"
    )
    assert (
        packet["gate_type"]
        == "WASSERSTEIN_TEST_VECTOR_FIXTURE_CREATION_ACTUAL_PR_GATE"
    )
    assert packet["operator_id"] == "WASSERSTEIN"
    assert packet["source_operator_decision_id"] == SOURCE_OPERATOR_DECISION_ID
    assert packet["source_operator_decision_hash"] == SOURCE_OPERATOR_DECISION_HASH
    assert (
        packet["source_authorization_review_hash"] == SOURCE_AUTHORIZATION_REVIEW_HASH
    )
    assert packet["intended_lane"] == "SHADOW"
    assert packet["gate_stage"] == "FIXTURE_CREATION_ACTUAL_PR_GATE_ONLY"


# ---------------------------------------------------------------------------
# Key authority flag flip: fixture_file_creation_authorized = true
# ---------------------------------------------------------------------------


def test_fixture_file_creation_authorized_true() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    assert packet["authority_locks"]["fixture_file_creation_authorized"] is True


def test_fixture_files_created_still_false() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    assert packet["authority_locks"]["fixture_files_created"] is False


def test_wasserstein_computation_unauthorized() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    assert packet["authority_locks"]["wasserstein_computation_authorized"] is False


def test_fixture_file_creation_authorized_false_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["fixture_file_creation_authorized"] = False
    with pytest.raises(ValueError, match="fixture_file_creation_authorized_must_be_true"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


def test_wasserstein_computation_authorized_true_raises() -> None:
    p = _payload()
    p["authority_locks"] = default_authority_locks()
    p["authority_locks"]["wasserstein_computation_authorized"] = True
    with pytest.raises(ValueError, match="wasserstein_computation_must_be_unauthorized"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Authorized manifest
# ---------------------------------------------------------------------------


def test_manifest_has_14_entries() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    assert len(packet["authorized_fixture_manifest"]) == 14


def test_manifest_type_distribution() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    manifest = packet["authorized_fixture_manifest"]
    assert len([e for e in manifest if e["fixture_type"] == "VALID"]) == 5
    assert len([e for e in manifest if e["fixture_type"] == "INVALID"]) == 5
    assert len([e for e in manifest if e["fixture_type"] == "NOT_COMPUTABLE"]) == 4


def test_manifest_all_creation_authorized() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    for entry in packet["authorized_fixture_manifest"]:
        assert entry["creation_authorized"] is True
        assert entry["status"] == "AUTHORIZED"


def test_manifest_unique_ids_and_paths() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    manifest = packet["authorized_fixture_manifest"]
    ids = [e["fixture_id"] for e in manifest]
    paths = [e["target_path"] for e in manifest]
    assert len(ids) == len(set(ids))
    assert len(paths) == len(set(paths))


def test_manifest_unauthorized_entry_raises() -> None:
    p = _payload()
    m = default_authorized_fixture_manifest()
    m[0]["creation_authorized"] = False
    p["authorized_fixture_manifest"] = m
    with pytest.raises(ValueError, match="fixture_creation_must_be_authorized"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


def test_manifest_wrong_count_raises() -> None:
    p = _payload()
    p["authorized_fixture_manifest"] = default_authorized_fixture_manifest()[:5]
    with pytest.raises(ValueError, match="manifest_entry_count_mismatch"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


def test_manifest_mutation_raises() -> None:
    p = _payload()
    m = default_authorized_fixture_manifest()
    m[0]["fixture_group"] = "TAMPERED"
    p["authorized_fixture_manifest"] = m
    with pytest.raises(ValueError, match="invalid_authorized_fixture_manifest"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Authorized batches
# ---------------------------------------------------------------------------


def test_authorized_batches_all_authorized() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    for batch in packet["authorized_batches"]:
        assert batch["creation_authorized"] is True
        assert batch["batch_status"] == "AUTHORIZED"


def test_batches_unauthorized_raises() -> None:
    p = _payload()
    batches = default_authorized_batches()
    batches[0]["creation_authorized"] = False
    p["authorized_batches"] = batches
    with pytest.raises(ValueError, match="batch_creation_must_be_authorized"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


def test_batches_mutation_raises() -> None:
    p = _payload()
    batches = default_authorized_batches()
    batches[0]["fixture_count"] = 99
    p["authorized_batches"] = batches
    with pytest.raises(ValueError, match="invalid_authorized_batches"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Fixture creation constraints
# ---------------------------------------------------------------------------


def test_constraints_all_safe() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    cc = packet["fixture_creation_constraints"]
    assert cc["expected_wasserstein_distances_included"] is False
    assert cc["computed_metric_outputs_included"] is False
    assert cc["fixture_execution_outputs_included"] is False
    assert cc["shadow_lane_only"] is True
    assert cc["fixture_file_creation_only"] is True
    assert cc["authorized_fixture_count"] == 14
    assert cc["authorized_batch_count"] == 3


def test_constraints_expected_distances_raises() -> None:
    p = _payload()
    cc = default_fixture_creation_constraints()
    cc["expected_wasserstein_distances_included"] = True
    p["fixture_creation_constraints"] = cc
    with pytest.raises(ValueError, match="expected_distances_must_be_excluded"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


def test_constraints_metric_outputs_raises() -> None:
    p = _payload()
    cc = default_fixture_creation_constraints()
    cc["computed_metric_outputs_included"] = True
    p["fixture_creation_constraints"] = cc
    with pytest.raises(ValueError, match="computed_metric_outputs_must_be_excluded"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


def test_constraints_mutation_raises() -> None:
    p = _payload()
    cc = default_fixture_creation_constraints()
    cc["authorized_fixture_count"] = 10
    p["fixture_creation_constraints"] = cc
    with pytest.raises(ValueError, match="invalid_fixture_creation_constraints"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------


def test_blocked_scopes_all_false() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    for k, v in packet["blocked_scopes"].items():
        assert v is False, f"blocked_scopes[{k!r}] must be False"


def test_blocked_scopes_mutation_raises() -> None:
    p = _payload()
    p["blocked_scopes"] = default_blocked_scopes()
    p["blocked_scopes"]["wasserstein_computation"] = True
    with pytest.raises(ValueError, match="invalid_blocked_scopes"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("field", "value", "err"),
    [
        ("intended_lane", "LIVE", "unknown_intended_lane"),
        ("gate_stage", "ACTIVE", "unknown_gate_stage"),
    ],
)
def test_top_level_enum_failures(field: str, value: str, err: str) -> None:
    p = _payload()
    p[field] = value
    with pytest.raises(ValueError, match=err):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


# ---------------------------------------------------------------------------
# Hash / provenance
# ---------------------------------------------------------------------------


def test_hash_excludes_itself() -> None:
    packet = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    altered = dict(packet)
    altered["canonical_hash"] = "0" * 64
    assert compute_wasserstein_test_vector_fixture_creation_actual_pr_gate_hash(
        packet
    ) == compute_wasserstein_test_vector_fixture_creation_actual_pr_gate_hash(altered)


def test_lane_change_changes_hash() -> None:
    p2 = _payload()
    p2["intended_lane"] = "PROJECTION"
    a = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(_payload())
    b = build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p2)
    assert a["canonical_hash"] != b["canonical_hash"]


def test_provenance_forbidden_reference() -> None:
    p = _payload()
    p["provenance"]["source"] = "runtime scheduler cache"
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)


def test_missing_required_field_raises() -> None:
    p = _payload()
    del p["gate_id"]
    with pytest.raises(ValueError, match="missing_required_fields"):
        build_wasserstein_test_vector_fixture_creation_actual_pr_gate(p)
