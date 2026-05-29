from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer_contract_spec import (
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_FALSE_OUTPUT_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    REQUIRED_BLOCKED_SCOPES,
    SOURCE_P44_PLAN_HASH,
    SOURCE_VIEWMODEL_ADAPTER_SPEC_HASH,
    SOURCE_WP001_BOUNDARY_HASH,
    build_aal_viz_geometric_renderer_contract_spec,
    default_authority_locks,
    default_blocked_scopes,
    default_deterministic_ordering_contract,
    default_governance_flags,
    default_renderer_input_contract,
    default_renderer_output_contract,
    default_source_ref_preservation_rules,
    default_validation_rules,
    default_viewmodel_acceptance_rules,
    validate_aal_viz_geometric_renderer_contract_spec,
)
from core.canonical.json import canonical_dumps, canonical_hash

_build = build_aal_viz_geometric_renderer_contract_spec


def _valid_payload() -> dict[str, object]:
    return {
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_002",
        "renderer_input_contract": default_renderer_input_contract(),
        "renderer_output_contract": default_renderer_output_contract(),
        "viewmodel_acceptance_rules": default_viewmodel_acceptance_rules(),
        "deterministic_ordering_contract": default_deterministic_ordering_contract(),
        "source_ref_preservation_rules": default_source_ref_preservation_rules(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of RENDERER_CONTRACT_SPEC_DEFINED status, "
            "advance to operator decision for renderer implementation authorization. "
            "Renderer code, metric computation, and P43 surface lanes remain blocked."
        ),
        "provenance": {
            "source": "P44_RENDERER_CONTRACT_SPEC_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-RENDERER-CONTRACT-SPEC-001",
            "evidence_refs": [
                "AALVizGeometricRendererViewmodelAdapterSpec.v1:aal_viz_geometric_renderer_viewmodel_adapter_spec_001",
                "AALVizGeometricRendererWP001ImplementationBoundary.v1:wp001_implementation_boundary_001",
                "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
                "GeometricProjectionSpec.v1:geometric_projection_spec_001",
                "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_002",
            ],
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_contract_spec.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_viewmodel_adapter_spec.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_wp001_implementation_boundary.v1.schema.json",
                "contracts/canon/geometric_projection_spec.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    first = _build(_valid_payload())
    second = _build(_valid_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert canonical_dumps(first) == canonical_dumps(second)


def test_contract_spec_constants() -> None:
    packet = _build(_valid_payload())
    assert packet["schema_version"] == "AALVizGeometricRendererContractSpec.v1"
    assert packet["contract_spec_type"] == "AAL_VIZ_GEOMETRIC_RENDERER_CONTRACT_SPEC"
    assert packet["contract_spec_status"] == "RENDERER_CONTRACT_SPEC_DEFINED"
    assert packet["source_viewmodel_adapter_spec_hash"] == SOURCE_VIEWMODEL_ADAPTER_SPEC_HASH
    assert packet["source_wp001_boundary_hash"] == SOURCE_WP001_BOUNDARY_HASH
    assert packet["source_p44_plan_hash"] == SOURCE_P44_PLAN_HASH


def test_viewmodel_adapter_spec_hash_pin_enforced() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["source_viewmodel_adapter_spec_hash"] = "b" * 64
    with pytest.raises(ValueError, match="source_viewmodel_adapter_spec_hash_mismatch"):
        validate_aal_viz_geometric_renderer_contract_spec(tampered)


def test_wp001_boundary_hash_pin_enforced() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["source_wp001_boundary_hash"] = "c" * 64
    with pytest.raises(ValueError, match="source_wp001_boundary_hash_mismatch"):
        validate_aal_viz_geometric_renderer_contract_spec(tampered)


def test_p44_plan_hash_pin_enforced() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["source_p44_plan_hash"] = "d" * 64
    with pytest.raises(ValueError, match="source_p44_plan_hash_mismatch"):
        validate_aal_viz_geometric_renderer_contract_spec(tampered)


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


@pytest.mark.parametrize("flag", LOCKED_FALSE_GOVERNANCE_FLAGS)
def test_governance_flags_locked_false(flag: str) -> None:
    payload = _valid_payload()
    payload["governance_flags"][flag] = True  # type: ignore[index]
    with pytest.raises(ValueError, match="governance_flag_must_be_false"):
        _build(payload)


@pytest.mark.parametrize("scope", REQUIRED_BLOCKED_SCOPES)
def test_missing_required_blocked_scope(scope: str) -> None:
    payload = _valid_payload()
    payload["blocked_scopes"] = [s for s in default_blocked_scopes() if s != scope]  # type: ignore[assignment]
    with pytest.raises(ValueError, match="missing_required_blocked_scope"):
        _build(payload)


@pytest.mark.parametrize("flag", LOCKED_FALSE_OUTPUT_FLAGS)
def test_output_contract_disallowed_flag_true_rejected(flag: str) -> None:
    payload = _valid_payload()
    payload["renderer_output_contract"][flag] = True  # type: ignore[index]
    with pytest.raises(ValueError, match=f"renderer_output_contract_{flag}_must_be_false"):
        _build(payload)


def test_output_contract_planning_metadata_false_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_contract"]["emits_planning_metadata"] = False  # type: ignore[index]
    with pytest.raises(
        ValueError, match="renderer_output_contract_emits_planning_metadata_must_be_true"
    ):
        _build(payload)


def test_output_contract_execution_authority_true_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_contract"]["execution_authority"] = True  # type: ignore[index]
    with pytest.raises(
        ValueError, match="renderer_output_contract_execution_authority_must_be_false"
    ):
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
            "contracts/canon/aal_viz_geometric_renderer_contract_spec.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = _build(_valid_payload())
    jsonschema.validate(packet, schema)


def test_default_output_contract_all_disallowed_flags_false() -> None:
    oc = default_renderer_output_contract()
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        assert oc[flag] is False
    assert oc["emits_planning_metadata"] is True
    assert oc["execution_authority"] is False


def test_default_blocked_scopes_covers_all_required() -> None:
    scopes = set(default_blocked_scopes())
    for scope in REQUIRED_BLOCKED_SCOPES:
        assert scope in scopes


def test_default_validation_rules_covers_all_allowed() -> None:
    rules = set(default_validation_rules())
    from core.aal_viz_geometric_renderer_contract_spec import ALLOWED_VALIDATION_RULES
    for rule in ALLOWED_VALIDATION_RULES:
        assert rule in rules


def test_source_ref_preservation_rules_contains_all_hashes() -> None:
    rules = default_source_ref_preservation_rules()
    hashes = rules["required_upstream_hashes"]
    assert hashes["source_viewmodel_adapter_spec_hash"] == SOURCE_VIEWMODEL_ADAPTER_SPEC_HASH
    assert hashes["source_wp001_boundary_hash"] == SOURCE_WP001_BOUNDARY_HASH
    assert hashes["source_p44_plan_hash"] == SOURCE_P44_PLAN_HASH


def test_viewmodel_acceptance_rules_contain_required_fields() -> None:
    rules = default_viewmodel_acceptance_rules()
    for field in ("created_at_utc", "governance_flags", "source_hash", "schema_version"):
        assert field in rules["required_viewmodel_ref_fields"]


def test_empty_recommended_next_step_rejected() -> None:
    payload = _valid_payload()
    payload["recommended_next_step"] = "   "  # type: ignore[assignment]
    with pytest.raises(ValueError, match="recommended_next_step_must_be_non_empty_string"):
        _build(payload)
