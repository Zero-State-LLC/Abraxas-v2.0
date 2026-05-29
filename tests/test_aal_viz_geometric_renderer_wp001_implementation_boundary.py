from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer_wp001_implementation_boundary import (
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    REQUIRED_BLOCKED_SCOPES,
    build_aal_viz_geometric_renderer_wp001_implementation_boundary,
    default_adapter_interface_plan,
    default_authority_locks,
    default_blocked_scopes,
    default_deterministic_ordering_contract,
    default_governance_flags,
    default_source_reference_matrix,
)
from core.canonical.json import canonical_dumps, canonical_hash


def _valid_payload() -> dict[str, object]:
    return {
        "source_p44_plan_hash": "e747808d3a94586fd682ece6a0824b666ac0aa326c0368799d736d85c11864f1",
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_002",
        "adapter_interface_plan": default_adapter_interface_plan(),
        "deterministic_ordering_contract": default_deterministic_ordering_contract(),
        "source_reference_matrix": default_source_reference_matrix(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of WP001_IMPLEMENTATION_BOUNDARY_DEFINED status, "
            "author the viewmodel adapter specification document for wp-001-implementation-boundary. "
            "Renderer code, metric computation, and P43 surface lanes remain blocked."
        ),
        "provenance": {
            "source": "P44_WP001_IMPLEMENTATION_BOUNDARY_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-WP001-IMPLEMENTATION-BOUNDARY-001",
            "evidence_refs": [
                "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
                "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_002",
            ],
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_wp001_implementation_boundary.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_implementation_plan.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


_build = build_aal_viz_geometric_renderer_wp001_implementation_boundary


def test_hash_deterministic_and_byte_stable() -> None:
    first = _build(_valid_payload())
    second = _build(_valid_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert canonical_dumps(first) == canonical_dumps(second)


def test_work_package_constants() -> None:
    packet = _build(_valid_payload())
    assert packet["work_package_id"] == "wp-001-implementation-boundary"
    assert packet["work_package_type"] == "AAL_VIZ_GEOMETRIC_RENDERER_WP001_IMPLEMENTATION_BOUNDARY"
    assert packet["wp_status"] == "WP001_IMPLEMENTATION_BOUNDARY_DEFINED"
    assert packet["implementation_stage"] == "WORK_PACKAGE_DEFINITION_ONLY"
    assert packet["schema_version"] == "AALVizGeometricRendererWP001ImplementationBoundary.v1"


@pytest.mark.parametrize("key", LOCKED_FALSE_AUTHORITY_KEYS)
def test_locked_false_authority_keys_rejected(key: str) -> None:
    payload = _valid_payload()
    payload["authority_locks"][key] = True  # type: ignore[index]
    with pytest.raises(ValueError, match="authority_lock_must_be_false"):
        _build(payload)


@pytest.mark.parametrize("key", LOCKED_TRUE_AUTHORITY_KEYS)
def test_locked_true_authority_keys_rejected(key: str) -> None:
    payload = _valid_payload()
    payload["authority_locks"][key] = False  # type: ignore[index]
    with pytest.raises(ValueError, match="authority_lock_must_be_true"):
        _build(payload)


@pytest.mark.parametrize("scope", REQUIRED_BLOCKED_SCOPES)
def test_missing_required_blocked_scope(scope: str) -> None:
    payload = _valid_payload()
    payload["blocked_scopes"] = [s for s in default_blocked_scopes() if s != scope]  # type: ignore[assignment]
    with pytest.raises(ValueError, match="missing_required_blocked_scope"):
        _build(payload)


@pytest.mark.parametrize("flag", LOCKED_FALSE_GOVERNANCE_FLAGS)
def test_governance_flags_locked_false(flag: str) -> None:
    payload = _valid_payload()
    payload["governance_flags"][flag] = True  # type: ignore[index]
    with pytest.raises(ValueError, match="governance_flag_must_be_false"):
        _build(payload)


def test_empty_adapter_interface_plan_rejected() -> None:
    payload = _valid_payload()
    payload["adapter_interface_plan"] = {}  # type: ignore[assignment]
    with pytest.raises(ValueError, match="adapter_interface_plan_must_be_non_empty_dict"):
        _build(payload)


def test_empty_source_reference_matrix_rejected() -> None:
    payload = _valid_payload()
    payload["source_reference_matrix"] = []  # type: ignore[assignment]
    with pytest.raises(ValueError, match="source_reference_matrix_must_be_non_empty_list"):
        _build(payload)


def test_empty_recommended_next_step_rejected() -> None:
    payload = _valid_payload()
    payload["recommended_next_step"] = "   "  # type: ignore[assignment]
    with pytest.raises(ValueError, match="recommended_next_step_must_be_non_empty_string"):
        _build(payload)


@pytest.mark.parametrize("token", ["executable", "runtime", "svg", "inference", "forecast"])
def test_forbidden_provenance_token_rejected(token: str) -> None:
    payload = _valid_payload()
    payload["provenance"]["source"] = f"test_{token}_source"  # type: ignore[index]
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        _build(payload)


def test_hash_excludes_canonical_hash_from_preimage_and_changes_on_change() -> None:
    packet = _build(_valid_payload())
    preimage = {k: v for k, v in packet.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == packet["canonical_hash"]
    payload2 = _valid_payload()
    payload2["source_operator_decision_ref"] = "P44_OPERATOR_DECISION_DIFFERENT"  # type: ignore[assignment]
    packet2 = _build(payload2)
    assert packet2["canonical_hash"] != packet["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path(
            "contracts/canon/aal_viz_geometric_renderer_wp001_implementation_boundary.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = _build(_valid_payload())
    jsonschema.validate(packet, schema)


def test_source_reference_matrix_sorted_by_ref_id() -> None:
    packet = _build(_valid_payload())
    ids = [entry["ref_id"] for entry in packet["source_reference_matrix"]]
    assert ids == sorted(ids)


def test_default_blocked_scopes_covers_all_required() -> None:
    scopes = set(default_blocked_scopes())
    for scope in REQUIRED_BLOCKED_SCOPES:
        assert scope in scopes
