from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer import (
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_FALSE_OUTPUT_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    REQUIRED_BLOCKED_SCOPES,
    SOURCE_RENDERER_CONTRACT_SPEC_HASH,
    build_aal_viz_geometric_renderer,
    default_authority_locks,
    default_blocked_scopes,
    default_deterministic_ordering_result,
    default_governance_flags,
    default_renderer_intake_boundary,
    default_renderer_output_declaration,
    default_validation_rules,
    default_viewmodel_acceptance_result,
    validate_aal_viz_geometric_renderer,
)
from core.canonical.json import canonical_dumps, canonical_hash

_build = build_aal_viz_geometric_renderer


def _valid_payload() -> dict[str, object]:
    return {
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_003",
        "renderer_intake_boundary": default_renderer_intake_boundary(),
        "viewmodel_acceptance_result": default_viewmodel_acceptance_result(),
        "deterministic_ordering_result": default_deterministic_ordering_result(),
        "renderer_output_declaration": default_renderer_output_declaration(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of RENDERER_BOUNDARY_DEFINED status, advance to "
            "operator decision for SVG/WebGL/Canvas renderer surface authorization."
        ),
        "provenance": {
            "source": "P44_RENDERER_BOUNDARY_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-RENDERER-BOUNDARY-001",
            "evidence_refs": [
                "AALVizGeometricRendererContractSpec.v1:aal_viz_geometric_renderer_contract_spec_001",
                "GeometricProjectionSpec.v1:geometric_projection_spec_001",
                "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_003",
            ],
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_contract_spec.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    first = _build(_valid_payload())
    second = _build(_valid_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert canonical_dumps(first) == canonical_dumps(second)


def test_renderer_boundary_constants() -> None:
    packet = _build(_valid_payload())
    assert packet["schema_version"] == "AALVizGeometricRenderer.v1"
    assert packet["renderer_type"] == "AAL_VIZ_GEOMETRIC_RENDERER_BOUNDARY"
    assert packet["renderer_status"] == "RENDERER_BOUNDARY_DEFINED"
    assert packet["source_renderer_contract_spec_hash"] == SOURCE_RENDERER_CONTRACT_SPEC_HASH


def test_renderer_contract_spec_hash_pin_enforced() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["source_renderer_contract_spec_hash"] = "b" * 64
    with pytest.raises(ValueError, match="source_renderer_contract_spec_hash_mismatch"):
        validate_aal_viz_geometric_renderer(tampered)


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
def test_output_declaration_disallowed_flag_true_rejected(flag: str) -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"][flag] = True  # type: ignore[index]
    with pytest.raises(
        ValueError, match=f"renderer_output_declaration_{flag}_must_be_false"
    ):
        _build(payload)


def test_output_declaration_planning_metadata_false_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"]["emits_planning_metadata"] = False  # type: ignore[index]
    with pytest.raises(
        ValueError,
        match="renderer_output_declaration_emits_planning_metadata_must_be_true",
    ):
        _build(payload)


def test_output_declaration_execution_authority_true_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"]["execution_authority"] = True  # type: ignore[index]
    with pytest.raises(
        ValueError,
        match="renderer_output_declaration_execution_authority_must_be_false",
    ):
        _build(payload)


@pytest.mark.parametrize("token", ["executable", "runtime", "svg", "webgl", "forecast"])
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
        Path("contracts/canon/aal_viz_geometric_renderer.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = _build(_valid_payload())
    jsonschema.validate(packet, schema)


def test_viewmodel_acceptance_result_has_acceptance_status() -> None:
    result = default_viewmodel_acceptance_result()
    assert result["acceptance_status"] == "VIEWMODEL_ACCEPTED_BOUNDARY_ONLY"
    assert result["execution_authority"] is False


def test_deterministic_ordering_result_has_ordering_status() -> None:
    result = default_deterministic_ordering_result()
    assert result["ordering_status"] == "ORDERING_CONTRACT_APPLIED"
    assert result["execution_authority"] is False
    assert result["determinism_guarantee"] == "BYTE_STABLE_ACROSS_RUNS"


def test_renderer_intake_boundary_declares_correct_input_fields() -> None:
    boundary = default_renderer_intake_boundary()
    assert "adapter_status" in boundary["accepted_input_fields"]
    assert "projection_boundary_id" in boundary["accepted_input_fields"]
    assert "viewmodel_ref" in boundary["accepted_input_fields"]
    assert boundary["execution_authority"] is False
    assert boundary["input_source"] == "VIEWMODEL_ADAPTER_SPEC_OUTPUT"


def test_empty_recommended_next_step_rejected() -> None:
    payload = _valid_payload()
    payload["recommended_next_step"] = "   "  # type: ignore[assignment]
    with pytest.raises(
        ValueError, match="recommended_next_step_must_be_non_empty_string"
    ):
        _build(payload)


def test_renderer_boundary_implementation_true_in_authority_locks() -> None:
    locks = default_authority_locks()
    assert locks["renderer_boundary_implementation"] is True
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["work_package_definition_only"] is False


def test_all_svg_webgl_canvas_locks_false() -> None:
    locks = default_authority_locks()
    assert locks["svg_renderer_implementation_authorized"] is False
    assert locks["webgl_renderer_implementation_authorized"] is False
    assert locks["canvas_renderer_implementation_authorized"] is False


def test_default_blocked_scopes_covers_all_required() -> None:
    scopes = set(default_blocked_scopes())
    for scope in REQUIRED_BLOCKED_SCOPES:
        assert scope in scopes


def test_default_validation_rules_covers_all_allowed() -> None:
    from core.aal_viz_geometric_renderer import ALLOWED_VALIDATION_RULES

    rules = set(default_validation_rules())
    for rule in ALLOWED_VALIDATION_RULES:
        assert rule in rules
