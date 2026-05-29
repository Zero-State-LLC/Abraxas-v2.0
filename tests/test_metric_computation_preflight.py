"""Tests for Metric Computation Preflight boundary artifact."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from core.metric_computation_preflight import (
    ALLOWED_VALIDATION_RULES,
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_FALSE_OUTPUT_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    PREFLIGHT_ID,
    PREFLIGHT_STATUS,
    PREFLIGHT_TYPE,
    REGISTERED_OPERATOR_COUNT,
    REQUIRED_BLOCKED_SCOPES,
    REQUIRED_PREFLIGHT_ACKNOWLEDGEMENT_KEYS,
    SCHEMA_VERSION,
    SOURCE_BASELINE_VECTOR_PACK_HASH,
    SOURCE_METRIC_REGISTRY_HASH,
    SOURCE_WEBGL_RENDERER_BOUNDARY_HASH,
    MetricComputationPreflightValidationError,
    build_metric_computation_preflight,
    build_preflight_projection,
    compute_metric_computation_preflight_hash,
    default_authority_locks,
    default_blocked_scopes,
    default_governance_flags,
    default_metric_intake_record,
    default_preflight_governance_acknowledgements,
    default_renderer_output_declaration,
    default_validation_rules,
    serialize_metric_computation_preflight,
    validate_metric_computation_preflight,
)
from core.canonical.json import canonical_dumps, canonical_hash

_ARTIFACT_CANONICAL_HASH = (
    "e1e3f8a0bd2999aebecf0dcbc5c94ce87d967c056f2ed18261b33e6de2b20238"
)
_WEBGL_BOUNDARY_HASH = (
    "d4ac613bb547b50a2b424124b2b4d26fd4d647f9d039f6a73691ee406cab5393"
)
_METRIC_REGISTRY_HASH = (
    "0493c034f1f270d31f23c211c0a938d75e0634299f1123db872b503ccb4bd0e3"
)
_BASELINE_VECTOR_PACK_HASH = (
    "053988aac083e06cf727a42675ae6e3f025e884d521f584d5b631ff813c2f0db"
)
_GEO_SPEC_SOURCE_HASH = (
    "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080"
)

_EXPECTED_PREFLIGHT_PROJECTION_SNAPSHOT: dict = {
    "advisory_only": True,
    "data_source_hash": _GEO_SPEC_SOURCE_HASH,
    "emits_metric_values": False,
    "execution_authority": False,
    "forecast_influence": False,
    "metric_computation_status": "PREFLIGHT_BOUNDARY_ONLY",
    "preflight_only": True,
    "projection_only": True,
    "registered_operator_count": 12,
    "schema_version": "GeometricProjectionSpec.v1",
    "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
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
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_007",
        "viewmodel_ref": copy.deepcopy(_BASE_VIEWMODEL_REF),
        "metric_intake_record": default_metric_intake_record(_BASE_VIEWMODEL_REF),
        "renderer_output_declaration": default_renderer_output_declaration(),
        "preflight_governance_acknowledgements": default_preflight_governance_acknowledgements(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of METRIC_COMPUTATION_PREFLIGHT_DEFINED status, "
            "advance to metric operator implementation selection \u2014 select the first operator "
            "(WASSERSTEIN, rank 1) for shadow-lane preflight implementation planning. "
            "All other blocked scopes remain unchanged. "
            "Forecast authority, inference authority, and P43 surface lanes remain blocked."
        ),
        "provenance": {
            "source": "P44_METRIC_COMPUTATION_PREFLIGHT_GATE",
            "advisory_only": True,
            "generated_by": "PATCH_P44_METRIC_COMPUTATION_PREFLIGHT_001",
            "evidence_refs": [
                "AALVizGeometricRendererWebGL.v1:aal_viz_geometric_renderer_webgl_001",
                "MetricOperatorRegistry.v1:metric_operator_registry_001",
                "MetricOperatorBaselineTestVectorPack.v1:metric_operator_baseline_test_vector_pack_001",
                "P44OperatorMetricPreflightDecision.v1:P44_OPERATOR_DECISION_2026_05_29_007",
            ],
            "upstream_schema_refs": [
                "contracts/canon/metric_computation_preflight.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer_webgl.v1.schema.json",
                "contracts/canon/metric_operator_registry.v1.schema.json",
                "contracts/canon/metric_operator_baseline_test_vector_pack.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def _build() -> dict:
    return build_metric_computation_preflight(_base_payload())


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_schema_version_constant() -> None:
    assert SCHEMA_VERSION == "MetricComputationPreflight.v1"


def test_preflight_type_constant() -> None:
    assert PREFLIGHT_TYPE == "METRIC_COMPUTATION_PREFLIGHT_BOUNDARY"


def test_preflight_status_constant() -> None:
    assert PREFLIGHT_STATUS == "METRIC_COMPUTATION_PREFLIGHT_DEFINED"


def test_preflight_id_constant() -> None:
    assert PREFLIGHT_ID == "metric_computation_preflight_001"


def test_source_webgl_renderer_boundary_hash_constant() -> None:
    assert SOURCE_WEBGL_RENDERER_BOUNDARY_HASH == _WEBGL_BOUNDARY_HASH


def test_source_metric_registry_hash_constant() -> None:
    assert SOURCE_METRIC_REGISTRY_HASH == _METRIC_REGISTRY_HASH


def test_source_baseline_vector_pack_hash_constant() -> None:
    assert SOURCE_BASELINE_VECTOR_PACK_HASH == _BASELINE_VECTOR_PACK_HASH


def test_registered_operator_count_constant() -> None:
    assert REGISTERED_OPERATOR_COUNT == 12


# ---------------------------------------------------------------------------
# Default factories
# ---------------------------------------------------------------------------


def test_default_authority_locks_metric_computation_authorized() -> None:
    locks = default_authority_locks()
    assert locks["metric_computation_authorized"] is True


def test_default_authority_locks_renderer_surfaces_preserved() -> None:
    locks = default_authority_locks()
    assert locks["svg_renderer_implementation_authorized"] is True
    assert locks["canvas_renderer_implementation_authorized"] is True
    assert locks["webgl_renderer_implementation_authorized"] is True


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


def test_default_blocked_scopes_metric_computation_not_in() -> None:
    assert "metric_computation" not in default_blocked_scopes()


def test_default_renderer_output_declaration_emits_metric_values_false() -> None:
    od = default_renderer_output_declaration()
    assert od["emits_metric_values"] is False


def test_default_renderer_output_declaration_forecast_influence_false() -> None:
    od = default_renderer_output_declaration()
    assert od["forecast_influence"] is False


def test_default_renderer_output_declaration_false_flags() -> None:
    od = default_renderer_output_declaration()
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        assert od[flag] is False, flag


def test_default_renderer_output_declaration_emits_planning_metadata() -> None:
    od = default_renderer_output_declaration()
    assert od["emits_planning_metadata"] is True


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


def test_default_validation_rules_covers_all_allowed() -> None:
    rules = set(default_validation_rules())
    for rule in ALLOWED_VALIDATION_RULES:
        assert rule in rules, f"missing rule: {rule}"


def test_default_validation_rules_contains_preflight_compliance() -> None:
    assert "PREFLIGHT_PROJECTION_COMPLIANCE" in default_validation_rules()


def test_default_validation_rules_contains_acknowledgement_check() -> None:
    assert "PREFLIGHT_GOVERNANCE_ACKNOWLEDGEMENT_CHECK" in default_validation_rules()


def test_default_preflight_governance_acknowledgements_all_true() -> None:
    ack = default_preflight_governance_acknowledgements()
    for key in REQUIRED_PREFLIGHT_ACKNOWLEDGEMENT_KEYS:
        assert ack[key] is True, key


def test_default_preflight_governance_acknowledgements_forecast_authority() -> None:
    ack = default_preflight_governance_acknowledgements()
    assert ack["metric_computation_authorized_does_not_grant_forecast_authority"] is True


def test_default_preflight_governance_acknowledgements_inference_authority() -> None:
    ack = default_preflight_governance_acknowledgements()
    assert ack["metric_computation_authorized_does_not_grant_inference_authority"] is True


def test_default_preflight_governance_acknowledgements_emits_metric_values_false() -> None:
    ack = default_preflight_governance_acknowledgements()
    assert ack["emits_metric_values_is_false"] is True


def test_default_metric_intake_record_defaults() -> None:
    record = default_metric_intake_record()
    assert record["execution_authority"] is False
    assert record["projection_only"] is True
    assert record["metric_computation_status"] == "PREFLIGHT_BOUNDARY_ONLY"
    assert record["ordering_applied"] == "CANONICAL_JSON_SORT"
    assert record["registered_operator_count"] == 12
    assert record["input_fields_accepted"] == [
        "metric_registry_ref",
        "preflight_boundary_id",
        "viewmodel_ref",
    ]


# ---------------------------------------------------------------------------
# build_preflight_projection
# ---------------------------------------------------------------------------


def test_preflight_projection_snapshot() -> None:
    projection = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert projection == _EXPECTED_PREFLIGHT_PROJECTION_SNAPSHOT


def test_preflight_projection_advisory_only() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["advisory_only"] is True


def test_preflight_projection_execution_authority_false() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["execution_authority"] is False


def test_preflight_projection_emits_metric_values_false() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["emits_metric_values"] is False


def test_preflight_projection_forecast_influence_false() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["forecast_influence"] is False


def test_preflight_projection_metric_computation_status() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["metric_computation_status"] == "PREFLIGHT_BOUNDARY_ONLY"


def test_preflight_projection_preflight_only() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["preflight_only"] is True


def test_preflight_projection_projection_only() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["projection_only"] is True


def test_preflight_projection_registered_operator_count() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["registered_operator_count"] == REGISTERED_OPERATOR_COUNT


def test_preflight_projection_data_source_hash_pinned() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["data_source_hash"] == _GEO_SPEC_SOURCE_HASH


def test_preflight_projection_title_preserved() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert proj["title"] == "Geometric Projection Spec \u2014 advisory-only scaffold"


def test_preflight_projection_is_deterministic() -> None:
    a = build_preflight_projection(_BASE_VIEWMODEL_REF)
    b = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert a == b


def test_preflight_projection_canonical_dumps_stable() -> None:
    proj = build_preflight_projection(_BASE_VIEWMODEL_REF)
    assert canonical_dumps(proj) == canonical_dumps(
        build_preflight_projection(_BASE_VIEWMODEL_REF)
    )


def test_preflight_projection_special_char_passthrough() -> None:
    vr = {**_BASE_VIEWMODEL_REF, "title": "Test <>&\""}
    proj = build_preflight_projection(vr)
    for ch in ['<', '>', '&', '"']:
        assert ch in proj["title"], f"special char {ch!r} should pass through"


# ---------------------------------------------------------------------------
# build_metric_computation_preflight
# ---------------------------------------------------------------------------


def test_build_sets_schema_version() -> None:
    art = _build()
    assert art["schema_version"] == SCHEMA_VERSION


def test_build_sets_preflight_type() -> None:
    art = _build()
    assert art["preflight_type"] == PREFLIGHT_TYPE


def test_build_sets_preflight_status() -> None:
    art = _build()
    assert art["preflight_status"] == PREFLIGHT_STATUS


def test_build_sets_preflight_id() -> None:
    art = _build()
    assert art["preflight_id"] == PREFLIGHT_ID


def test_build_pins_webgl_boundary_hash() -> None:
    art = _build()
    assert art["source_webgl_renderer_boundary_hash"] == _WEBGL_BOUNDARY_HASH


def test_build_pins_metric_registry_hash() -> None:
    art = _build()
    assert art["source_metric_registry_hash"] == _METRIC_REGISTRY_HASH


def test_build_pins_baseline_vector_pack_hash() -> None:
    art = _build()
    assert art["source_baseline_vector_pack_hash"] == _BASELINE_VECTOR_PACK_HASH


def test_build_metric_computation_authorized_true() -> None:
    art = _build()
    assert art["authority_locks"]["metric_computation_authorized"] is True


def test_build_renderer_surfaces_preserved() -> None:
    art = _build()
    assert art["authority_locks"]["svg_renderer_implementation_authorized"] is True
    assert art["authority_locks"]["canvas_renderer_implementation_authorized"] is True
    assert art["authority_locks"]["webgl_renderer_implementation_authorized"] is True


def test_build_emits_metric_values_false() -> None:
    art = _build()
    assert art["renderer_output_declaration"]["emits_metric_values"] is False


def test_build_forecast_influence_false() -> None:
    art = _build()
    assert art["renderer_output_declaration"]["forecast_influence"] is False


def test_build_p43_surface_lanes_still_false() -> None:
    art = _build()
    assert art["authority_locks"]["p43_surface_lanes_authorized"] is False


def test_build_production_activation_still_false() -> None:
    art = _build()
    assert art["authority_locks"]["production_activation"] is False


def test_build_preflight_projection_embedded() -> None:
    art = _build()
    assert art["preflight_projection"] == _EXPECTED_PREFLIGHT_PROJECTION_SNAPSHOT


def test_build_all_acknowledgements_true() -> None:
    art = _build()
    ack = art["preflight_governance_acknowledgements"]
    for key in REQUIRED_PREFLIGHT_ACKNOWLEDGEMENT_KEYS:
        assert ack[key] is True, key


def test_build_blocked_scopes_sorted() -> None:
    art = _build()
    assert art["blocked_scopes"] == sorted(art["blocked_scopes"])


def test_build_metric_computation_not_in_blocked_scopes() -> None:
    art = _build()
    assert "metric_computation" not in art["blocked_scopes"]


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


def test_build_viewmodel_ref_stripped() -> None:
    art = _build()
    assert "viewmodel_ref" not in art


# ---------------------------------------------------------------------------
# RENDERER_BOUNDARY_CHAIN_CHECK — hash pin enforcement
# ---------------------------------------------------------------------------


def test_webgl_boundary_hash_pin_enforced() -> None:
    art = _build()
    tampered = dict(art)
    tampered["source_webgl_renderer_boundary_hash"] = "a" * 64
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="source_webgl_renderer_boundary_hash_mismatch",
    ):
        validate_metric_computation_preflight(tampered)


def test_metric_registry_hash_pin_enforced() -> None:
    art = _build()
    tampered = dict(art)
    tampered["source_metric_registry_hash"] = "b" * 64
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="source_metric_registry_hash_mismatch",
    ):
        validate_metric_computation_preflight(tampered)


def test_baseline_vector_pack_hash_pin_enforced() -> None:
    art = _build()
    tampered = dict(art)
    tampered["source_baseline_vector_pack_hash"] = "c" * 64
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="source_baseline_vector_pack_hash_mismatch",
    ):
        validate_metric_computation_preflight(tampered)


# ---------------------------------------------------------------------------
# PREFLIGHT_PROJECTION_COMPLIANCE — rejection tests
# ---------------------------------------------------------------------------


def test_preflight_projection_advisory_only_false_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["preflight_projection"] = {**art["preflight_projection"], "advisory_only": False}
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="preflight_projection_advisory_only_must_be_true",
    ):
        validate_metric_computation_preflight(tampered)


def test_preflight_projection_execution_authority_true_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["preflight_projection"] = {
        **art["preflight_projection"], "execution_authority": True
    }
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="preflight_projection_execution_authority_must_be_false",
    ):
        validate_metric_computation_preflight(tampered)


def test_preflight_projection_emits_metric_values_true_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["preflight_projection"] = {
        **art["preflight_projection"], "emits_metric_values": True
    }
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="preflight_projection_emits_metric_values_must_be_false",
    ):
        validate_metric_computation_preflight(tampered)


def test_preflight_projection_forecast_influence_true_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["preflight_projection"] = {
        **art["preflight_projection"], "forecast_influence": True
    }
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="preflight_projection_forecast_influence_must_be_false",
    ):
        validate_metric_computation_preflight(tampered)


def test_preflight_projection_wrong_computation_status_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["preflight_projection"] = {
        **art["preflight_projection"], "metric_computation_status": "ACTIVE"
    }
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="metric_computation_status_must_be_PREFLIGHT_BOUNDARY_ONLY",
    ):
        validate_metric_computation_preflight(tampered)


def test_preflight_projection_projection_only_false_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["preflight_projection"] = {
        **art["preflight_projection"], "projection_only": False
    }
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="preflight_projection_projection_only_must_be_true",
    ):
        validate_metric_computation_preflight(tampered)


def test_preflight_projection_preflight_only_false_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["preflight_projection"] = {
        **art["preflight_projection"], "preflight_only": False
    }
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="preflight_projection_preflight_only_must_be_true",
    ):
        validate_metric_computation_preflight(tampered)


# ---------------------------------------------------------------------------
# PREFLIGHT_GOVERNANCE_ACKNOWLEDGEMENT_CHECK — rejection tests
# ---------------------------------------------------------------------------


def test_acknowledgement_false_rejected() -> None:
    art = _build()
    for key in REQUIRED_PREFLIGHT_ACKNOWLEDGEMENT_KEYS:
        tampered = dict(art)
        tampered["preflight_governance_acknowledgements"] = {
            **art["preflight_governance_acknowledgements"], key: False
        }
        with pytest.raises(
            MetricComputationPreflightValidationError,
            match=f"preflight_governance_acknowledgement_must_be_true:{key}",
        ):
            validate_metric_computation_preflight(tampered)


# ---------------------------------------------------------------------------
# AUTHORITY_LOCK_SCAN
# ---------------------------------------------------------------------------


def test_authority_lock_false_keys_enforced() -> None:
    art = _build()
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        tampered = dict(art)
        tampered["authority_locks"] = {**art["authority_locks"], key: True}
        with pytest.raises(
            MetricComputationPreflightValidationError,
            match=f"authority_lock_must_be_false:{key}",
        ):
            validate_metric_computation_preflight(tampered)


def test_authority_lock_true_keys_enforced() -> None:
    art = _build()
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        tampered = dict(art)
        tampered["authority_locks"] = {**art["authority_locks"], key: False}
        with pytest.raises(
            MetricComputationPreflightValidationError,
            match=f"authority_lock_must_be_true:{key}",
        ):
            validate_metric_computation_preflight(tampered)


# ---------------------------------------------------------------------------
# OUTPUT_DECLARATION_COMPLIANCE
# ---------------------------------------------------------------------------


def test_output_declaration_false_flags_enforced() -> None:
    art = _build()
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        tampered = dict(art)
        tampered["renderer_output_declaration"] = {
            **art["renderer_output_declaration"], flag: True
        }
        with pytest.raises(
            MetricComputationPreflightValidationError,
            match=f"renderer_output_declaration_{flag}_must_be_false",
        ):
            validate_metric_computation_preflight(tampered)


def test_output_declaration_forecast_influence_true_rejected() -> None:
    art = _build()
    tampered = dict(art)
    tampered["renderer_output_declaration"] = {
        **art["renderer_output_declaration"], "forecast_influence": True
    }
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="renderer_output_declaration_forecast_influence_must_be_false",
    ):
        validate_metric_computation_preflight(tampered)


# ---------------------------------------------------------------------------
# SOURCE_REF_PRESERVATION_CHECK — blocked scopes
# ---------------------------------------------------------------------------


def test_missing_required_blocked_scope_rejected() -> None:
    art = _build()
    for scope in REQUIRED_BLOCKED_SCOPES:
        tampered = dict(art)
        tampered["blocked_scopes"] = [s for s in art["blocked_scopes"] if s != scope]
        with pytest.raises(
            MetricComputationPreflightValidationError,
            match=f"missing_required_blocked_scope:{scope}",
        ):
            validate_metric_computation_preflight(tampered)


# ---------------------------------------------------------------------------
# GOVERNANCE_FALSE_FLAG_SCAN
# ---------------------------------------------------------------------------


def test_governance_false_flags_enforced() -> None:
    art = _build()
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        tampered = dict(art)
        tampered["governance_flags"] = {**art["governance_flags"], flag: True}
        with pytest.raises(
            MetricComputationPreflightValidationError,
            match=f"governance_flag_must_be_false:{flag}",
        ):
            validate_metric_computation_preflight(tampered)


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
        "metric-value",
        "route-control",
        "scoring",
        "ui",
    ],
)
def test_forbidden_provenance_token_rejected(token: str) -> None:
    art = _build()
    tampered = dict(art)
    tampered["provenance"] = {**art["provenance"], "source": f"FORBIDDEN_{token}_NODE"}
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="forbidden_provenance_reference_detected",
    ):
        validate_metric_computation_preflight(tampered)


# ---------------------------------------------------------------------------
# Misc validation
# ---------------------------------------------------------------------------


def test_empty_recommended_next_step_rejected() -> None:
    payload = _base_payload()
    payload["recommended_next_step"] = "   "
    with pytest.raises(
        MetricComputationPreflightValidationError,
        match="recommended_next_step_must_be_non_empty_string",
    ):
        build_metric_computation_preflight(payload)


# ---------------------------------------------------------------------------
# Hash and serialization
# ---------------------------------------------------------------------------


def test_compute_hash_excludes_canonical_hash_field() -> None:
    art = _build()
    computed = compute_metric_computation_preflight_hash(art)
    assert computed == _ARTIFACT_CANONICAL_HASH


def test_preflight_round_trip_hash_verification() -> None:
    artifact_path = Path(
        "out/projections/metric_computation_preflight_001.latest.json"
    )
    if not artifact_path.exists():
        pytest.skip("artifact not present — run runner first")
    art = json.loads(artifact_path.read_text(encoding="utf-8"))
    stored_hash = art["canonical_hash"]
    preimage = {k: v for k, v in art.items() if k != "canonical_hash"}
    recomputed = canonical_hash(preimage)
    assert recomputed == stored_hash, (
        f"round-trip hash mismatch: stored={stored_hash} recomputed={recomputed}"
    )
    assert stored_hash == _ARTIFACT_CANONICAL_HASH, (
        f"artifact canonical_hash has drifted from pinned value: "
        f"got {stored_hash!r}, expected {_ARTIFACT_CANONICAL_HASH!r}"
    )


def test_serialize_is_valid_json() -> None:
    art = _build()
    raw = serialize_metric_computation_preflight(art)
    parsed = json.loads(raw)
    assert parsed["canonical_hash"] == _ARTIFACT_CANONICAL_HASH


def test_serialize_ends_with_newline() -> None:
    art = _build()
    raw = serialize_metric_computation_preflight(art)
    assert raw.endswith("\n")


def test_serialize_is_byte_stable() -> None:
    art = _build()
    assert (
        serialize_metric_computation_preflight(art)
        == serialize_metric_computation_preflight(art)
    )


# ---------------------------------------------------------------------------
# Schema fixture validation
# ---------------------------------------------------------------------------


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/metric_computation_preflight.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = _build()
    jsonschema.validate(packet, schema)
