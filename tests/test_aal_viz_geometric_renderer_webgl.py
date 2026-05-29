"""Tests for AAL-Viz Geometric Renderer WebGL Boundary artifact."""

from __future__ import annotations

import copy
import json

import pytest

from core.aal_viz_geometric_renderer_webgl import (
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_FALSE_OUTPUT_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    RENDERER_WEBGL_ID,
    RENDERER_WEBGL_STATUS,
    RENDERER_WEBGL_TYPE,
    REQUIRED_BLOCKED_SCOPES,
    SCHEMA_VERSION,
    SOURCE_CANVAS_RENDERER_BOUNDARY_HASH,
    AALVizGeometricRendererWebGLValidationError,
    build_aal_viz_geometric_renderer_webgl,
    build_webgl_projection,
    compute_aal_viz_geometric_renderer_webgl_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_governance_flags,
    default_renderer_output_declaration,
    default_validation_rules,
    default_webgl_intake_record,
    serialize_aal_viz_geometric_renderer_webgl,
    validate_aal_viz_geometric_renderer_webgl,
)
from core.canonical.json import canonical_dumps

_ARTIFACT_CANONICAL_HASH = (
    "d4ac613bb547b50a2b424124b2b4d26fd4d647f9d039f6a73691ee406cab5393"
)
_CANVAS_BOUNDARY_HASH = (
    "f22a540c6fab6b45fe301339d6b28471489be3725078e4c8942d64afa2550d1d"
)
_GEO_SPEC_SOURCE_HASH = (
    "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080"
)

_EXPECTED_WEBGL_PROJECTION_SNAPSHOT: dict = {
    "advisory_only": True,
    "data_source_hash": _GEO_SPEC_SOURCE_HASH,
    "execution_authority": False,
    "projection_only": True,
    "schema_version": "GeometricProjectionSpec.v1",
    "surface_type": "WEBGL_BOUNDARY",
    "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
    "webgl_generation_status": "BOUNDARY_PROJECTION_ONLY",
}

_BASE_VIEWMODEL_REF: dict = {
    "schema_version": "GeometricProjectionSpec.v1",
    "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
    "source_hash": _GEO_SPEC_SOURCE_HASH,
    "observed_summary": "Advisory-only projection.",
    "governance_flags": {},
    "provenance": {},
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def _base_payload() -> dict:
    return {
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_006",
        "viewmodel_ref": copy.deepcopy(_BASE_VIEWMODEL_REF),
        "webgl_intake_record": default_webgl_intake_record(_BASE_VIEWMODEL_REF),
        "renderer_output_declaration": default_renderer_output_declaration(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of RENDERER_WEBGL_BOUNDARY_DEFINED status, the "
            "three-surface renderer boundary chain (SVG, Canvas, WebGL) is complete. "
            "Advance to cross-surface parity hardening audit or operator decision for "
            "metric computation authorization. All other blocked scopes remain unchanged."
        ),
        "provenance": {
            "source": "P44_WEBGL_RENDERER_BOUNDARY_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-RENDERER-WEBGL-BOUNDARY-001",
            "evidence_refs": [
                "AALVizGeometricRendererCanvas.v1:aal_viz_geometric_renderer_canvas_001",
                "GeometricProjectionSpec.v1:geometric_projection_spec_001",
                "P44OperatorWebGLDecision.v1:P44_OPERATOR_DECISION_2026_05_29_006",
            ],
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_webgl.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_canvas.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def _build() -> dict:
    return build_aal_viz_geometric_renderer_webgl(_base_payload())


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_schema_version_constant() -> None:
    assert SCHEMA_VERSION == "AALVizGeometricRendererWebGL.v1"


def test_renderer_webgl_type_constant() -> None:
    assert RENDERER_WEBGL_TYPE == "AAL_VIZ_GEOMETRIC_RENDERER_WEBGL_BOUNDARY"


def test_renderer_webgl_status_constant() -> None:
    assert RENDERER_WEBGL_STATUS == "RENDERER_WEBGL_BOUNDARY_DEFINED"


def test_renderer_webgl_id_constant() -> None:
    assert RENDERER_WEBGL_ID == "aal_viz_geometric_renderer_webgl_001"


def test_source_canvas_renderer_boundary_hash_constant() -> None:
    assert SOURCE_CANVAS_RENDERER_BOUNDARY_HASH == _CANVAS_BOUNDARY_HASH


# ---------------------------------------------------------------------------
# Default factories
# ---------------------------------------------------------------------------


def test_default_authority_locks_webgl_authorized() -> None:
    locks = default_authority_locks()
    assert locks["webgl_renderer_implementation_authorized"] is True


def test_default_authority_locks_canvas_svg_preserved() -> None:
    locks = default_authority_locks()
    assert locks["canvas_renderer_implementation_authorized"] is True
    assert locks["svg_renderer_implementation_authorized"] is True


def test_default_authority_locks_false_keys() -> None:
    locks = default_authority_locks()
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        assert locks[key] is False, key


def test_default_authority_locks_true_keys() -> None:
    locks = default_authority_locks()
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        assert locks[key] is True, key


def test_default_blocked_scopes_sorted() -> None:
    scopes = default_blocked_scopes()
    assert scopes == sorted(scopes)


def test_default_blocked_scopes_required_present() -> None:
    scopes = set(default_blocked_scopes())
    for scope in REQUIRED_BLOCKED_SCOPES:
        assert scope in scopes, scope


def test_default_blocked_scopes_webgl_not_in() -> None:
    assert "webgl_renderer_implementation" not in default_blocked_scopes()


def test_default_renderer_output_declaration_emits_webgl() -> None:
    od = default_renderer_output_declaration()
    assert od["emits_webgl"] is True


def test_default_renderer_output_declaration_false_flags() -> None:
    od = default_renderer_output_declaration()
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        assert od[flag] is False, flag


def test_default_renderer_output_declaration_no_execution_authority() -> None:
    od = default_renderer_output_declaration()
    assert od["execution_authority"] is False


def test_default_governance_flags_all_false() -> None:
    gf = default_governance_flags()
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        assert gf[flag] is False, flag


def test_default_validation_rules_sorted() -> None:
    rules = default_validation_rules()
    assert rules == sorted(rules)


def test_default_validation_rules_contains_webgl_compliance() -> None:
    assert "WEBGL_PROJECTION_COMPLIANCE" in default_validation_rules()


def test_default_validation_rules_contains_chain_check() -> None:
    assert "RENDERER_BOUNDARY_CHAIN_CHECK" in default_validation_rules()


def test_default_webgl_intake_record_defaults() -> None:
    record = default_webgl_intake_record()
    assert record["execution_authority"] is False
    assert record["projection_only"] is True
    assert record["webgl_generation_status"] == "BOUNDARY_PROJECTION_ONLY"
    assert record["ordering_applied"] == "CANONICAL_JSON_SORT"
    assert record["input_fields_accepted"] == [
        "adapter_status",
        "projection_boundary_id",
        "viewmodel_ref",
    ]


# ---------------------------------------------------------------------------
# webgl_projection builder
# ---------------------------------------------------------------------------


def test_webgl_projection_snapshot() -> None:
    projection = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert projection == _EXPECTED_WEBGL_PROJECTION_SNAPSHOT


def test_webgl_projection_advisory_only() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["advisory_only"] is True


def test_webgl_projection_execution_authority_false() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["execution_authority"] is False


def test_webgl_projection_projection_only() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["projection_only"] is True


def test_webgl_projection_surface_type() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["surface_type"] == "WEBGL_BOUNDARY"


def test_webgl_projection_webgl_generation_status() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["webgl_generation_status"] == "BOUNDARY_PROJECTION_ONLY"


def test_webgl_projection_schema_version() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["schema_version"] == "GeometricProjectionSpec.v1"


def test_webgl_projection_data_source_hash_pinned() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["data_source_hash"] == _GEO_SPEC_SOURCE_HASH


def test_webgl_projection_title_preserved() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert proj["title"] == "Geometric Projection Spec \u2014 advisory-only scaffold"


def test_webgl_projection_is_deterministic() -> None:
    a = build_webgl_projection(_BASE_VIEWMODEL_REF)
    b = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert a == b


def test_webgl_projection_canonical_dumps_stable() -> None:
    proj = build_webgl_projection(_BASE_VIEWMODEL_REF)
    assert canonical_dumps(proj) == canonical_dumps(proj)
    assert canonical_dumps(proj) == canonical_dumps(
        build_webgl_projection(_BASE_VIEWMODEL_REF)
    )


def test_webgl_projection_special_char_passthrough() -> None:
    special_chars = ['<', '>', '&', '"']
    vr = {**_BASE_VIEWMODEL_REF, "title": "Test <>&\""}
    proj = build_webgl_projection(vr)
    for ch in special_chars:
        assert ch in proj["title"], f"special char {ch!r} should pass through"
    raw_json = canonical_dumps(proj)
    assert "<" not in raw_json or "&lt;" not in raw_json


# ---------------------------------------------------------------------------
# build_aal_viz_geometric_renderer_webgl
# ---------------------------------------------------------------------------


def test_build_sets_schema_version() -> None:
    art = _build()
    assert art["schema_version"] == SCHEMA_VERSION


def test_build_sets_renderer_webgl_type() -> None:
    art = _build()
    assert art["renderer_webgl_type"] == RENDERER_WEBGL_TYPE


def test_build_sets_renderer_webgl_status() -> None:
    art = _build()
    assert art["renderer_webgl_status"] == RENDERER_WEBGL_STATUS


def test_build_sets_renderer_webgl_id() -> None:
    art = _build()
    assert art["renderer_webgl_id"] == RENDERER_WEBGL_ID


def test_build_pins_canvas_boundary_hash() -> None:
    art = _build()
    assert art["source_canvas_renderer_boundary_hash"] == _CANVAS_BOUNDARY_HASH


def test_build_emits_webgl_true() -> None:
    art = _build()
    assert art["renderer_output_declaration"]["emits_webgl"] is True


def test_build_emits_rendered_output_false() -> None:
    art = _build()
    assert art["renderer_output_declaration"]["emits_rendered_output"] is False


def test_build_emits_canvas_false() -> None:
    art = _build()
    assert art["renderer_output_declaration"]["emits_canvas"] is False


def test_build_emits_svg_false() -> None:
    art = _build()
    assert art["renderer_output_declaration"]["emits_svg"] is False


def test_build_webgl_renderer_implementation_authorized_true() -> None:
    art = _build()
    assert art["authority_locks"]["webgl_renderer_implementation_authorized"] is True


def test_build_canvas_renderer_implementation_authorized_preserved() -> None:
    art = _build()
    assert art["authority_locks"]["canvas_renderer_implementation_authorized"] is True


def test_build_svg_renderer_implementation_authorized_preserved() -> None:
    art = _build()
    assert art["authority_locks"]["svg_renderer_implementation_authorized"] is True


def test_build_metric_computation_still_false() -> None:
    art = _build()
    assert art["authority_locks"]["metric_computation_authorized"] is False


def test_build_production_activation_still_false() -> None:
    art = _build()
    assert art["authority_locks"]["production_activation"] is False


def test_build_webgl_projection_embedded() -> None:
    art = _build()
    assert art["webgl_projection"] == _EXPECTED_WEBGL_PROJECTION_SNAPSHOT


def test_build_blocked_scopes_sorted() -> None:
    art = _build()
    assert art["blocked_scopes"] == sorted(art["blocked_scopes"])


def test_build_webgl_not_in_blocked_scopes() -> None:
    art = _build()
    assert "webgl_renderer_implementation" not in art["blocked_scopes"]


def test_build_all_required_blocked_scopes_present() -> None:
    art = _build()
    scopes = set(art["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        assert scope in scopes, scope


def test_build_canonical_hash_present() -> None:
    art = _build()
    assert "canonical_hash" in art
    assert len(art["canonical_hash"]) == 64


def test_build_canonical_hash_pinned() -> None:
    art = _build()
    assert art["canonical_hash"] == _ARTIFACT_CANONICAL_HASH


def test_build_canonical_hash_stable_across_calls() -> None:
    a = _build()
    b = _build()
    assert a["canonical_hash"] == b["canonical_hash"]


# ---------------------------------------------------------------------------
# RENDERER_BOUNDARY_CHAIN_CHECK — canvas hash pin enforcement
# ---------------------------------------------------------------------------


def test_canvas_boundary_hash_pin_enforced() -> None:
    art = _build()
    tampered = dict(art)
    tampered["source_canvas_renderer_boundary_hash"] = "a" * 64
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="source_canvas_renderer_boundary_hash_mismatch",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


# ---------------------------------------------------------------------------
# WEBGL_PROJECTION_COMPLIANCE — rejection tests
# ---------------------------------------------------------------------------


def test_webgl_projection_advisory_only_false_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["webgl_projection"] = {**art["webgl_projection"], "advisory_only": False}
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="webgl_projection_advisory_only_must_be_true",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


def test_webgl_projection_execution_authority_true_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["webgl_projection"] = {
        **art["webgl_projection"],
        "execution_authority": True,
    }
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="webgl_projection_execution_authority_must_be_false",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


def test_webgl_projection_wrong_generation_status_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["webgl_projection"] = {
        **art["webgl_projection"],
        "webgl_generation_status": "ACTIVE",
    }
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="webgl_generation_status_must_be_BOUNDARY_PROJECTION_ONLY",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


def test_webgl_projection_wrong_surface_type_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["webgl_projection"] = {
        **art["webgl_projection"],
        "surface_type": "CANVAS_BOUNDARY",
    }
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="webgl_projection_surface_type_must_be_WEBGL_BOUNDARY",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


def test_webgl_projection_projection_only_false_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["webgl_projection"] = {
        **art["webgl_projection"],
        "projection_only": False,
    }
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="webgl_projection_projection_only_must_be_true",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


# ---------------------------------------------------------------------------
# AUTHORITY_LOCK_SCAN
# ---------------------------------------------------------------------------


def test_authority_lock_false_keys_enforced() -> None:
    art = _build()
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        tampered = dict(art)
        tampered["authority_locks"] = {**art["authority_locks"], key: True}
        with pytest.raises(
            AALVizGeometricRendererWebGLValidationError,
            match=f"authority_lock_must_be_false:{key}",
        ):
            validate_aal_viz_geometric_renderer_webgl(tampered)


def test_authority_lock_true_keys_enforced() -> None:
    art = _build()
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        tampered = dict(art)
        tampered["authority_locks"] = {**art["authority_locks"], key: False}
        with pytest.raises(
            AALVizGeometricRendererWebGLValidationError,
            match=f"authority_lock_must_be_true:{key}",
        ):
            validate_aal_viz_geometric_renderer_webgl(tampered)


# ---------------------------------------------------------------------------
# OUTPUT_DECLARATION_COMPLIANCE
# ---------------------------------------------------------------------------


def test_output_declaration_false_flags_enforced() -> None:
    art = _build()
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        tampered = dict(art)
        tampered["renderer_output_declaration"] = {
            **art["renderer_output_declaration"],
            flag: True,
        }
        with pytest.raises(
            AALVizGeometricRendererWebGLValidationError,
            match=f"renderer_output_declaration_{flag}_must_be_false",
        ):
            validate_aal_viz_geometric_renderer_webgl(tampered)


def test_output_declaration_emits_webgl_false_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["renderer_output_declaration"] = {
        **art["renderer_output_declaration"],
        "emits_webgl": False,
    }
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="renderer_output_declaration_emits_webgl_must_be_true",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


# ---------------------------------------------------------------------------
# SOURCE_REF_PRESERVATION_CHECK — blocked scopes
# ---------------------------------------------------------------------------


def test_missing_required_blocked_scope_rejected() -> None:
    art = _build()
    for scope in REQUIRED_BLOCKED_SCOPES:
        tampered = dict(art)
        tampered["blocked_scopes"] = [s for s in art["blocked_scopes"] if s != scope]
        with pytest.raises(
            AALVizGeometricRendererWebGLValidationError,
            match=f"missing_required_blocked_scope:{scope}",
        ):
            validate_aal_viz_geometric_renderer_webgl(tampered)


# ---------------------------------------------------------------------------
# GOVERNANCE_FALSE_FLAG_SCAN
# ---------------------------------------------------------------------------


def test_governance_false_flags_enforced() -> None:
    art = _build()
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        tampered = dict(art)
        tampered["governance_flags"] = {**art["governance_flags"], flag: True}
        with pytest.raises(
            AALVizGeometricRendererWebGLValidationError,
            match=f"governance_flag_must_be_false:{flag}",
        ):
            validate_aal_viz_geometric_renderer_webgl(tampered)


# ---------------------------------------------------------------------------
# NO_RUNTIME_MUTATION_SCAN — provenance token check
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "token",
    [
        "runtime",
        "scheduler",
        "forecast",
        "inference",
        "cache",
        "callable",
        "executable",
        "metric-computation",
        "route-control",
        "ui",
    ],
)
def test_forbidden_provenance_token_rejected(token: str) -> None:
    art = _build()
    tampered = dict(art)
    tampered["provenance"] = {**art["provenance"], "source": f"FORBIDDEN_{token}_NODE"}
    with pytest.raises(
        AALVizGeometricRendererWebGLValidationError,
        match="forbidden_provenance_reference_detected",
    ):
        validate_aal_viz_geometric_renderer_webgl(tampered)


# ---------------------------------------------------------------------------
# compute_hash
# ---------------------------------------------------------------------------


def test_compute_hash_excludes_canonical_hash_field() -> None:
    art = _build()
    computed = compute_aal_viz_geometric_renderer_webgl_hash(art)
    assert computed == _ARTIFACT_CANONICAL_HASH


# ---------------------------------------------------------------------------
# serialize
# ---------------------------------------------------------------------------


def test_serialize_is_valid_json() -> None:
    art = _build()
    raw = serialize_aal_viz_geometric_renderer_webgl(art)
    parsed = json.loads(raw)
    assert parsed["canonical_hash"] == _ARTIFACT_CANONICAL_HASH


def test_serialize_ends_with_newline() -> None:
    art = _build()
    raw = serialize_aal_viz_geometric_renderer_webgl(art)
    assert raw.endswith("\n")


def test_serialize_is_byte_stable() -> None:
    art = _build()
    a = serialize_aal_viz_geometric_renderer_webgl(art)
    b = serialize_aal_viz_geometric_renderer_webgl(art)
    assert a == b
