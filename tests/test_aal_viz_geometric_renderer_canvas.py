from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer_canvas import (
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_FALSE_OUTPUT_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    REQUIRED_BLOCKED_SCOPES,
    SOURCE_SVG_RENDERER_BOUNDARY_HASH,
    build_aal_viz_geometric_renderer_canvas,
    build_canvas_projection,
    default_authority_locks,
    default_blocked_scopes,
    default_canvas_intake_record,
    default_governance_flags,
    default_renderer_output_declaration,
    default_validation_rules,
    validate_aal_viz_geometric_renderer_canvas,
)
from core.canonical.json import canonical_dumps, canonical_hash

_build = build_aal_viz_geometric_renderer_canvas

_VIEWMODEL_REF = {
    "schema_version": "GeometricProjectionSpec.v1",
    "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
    "source_hash": "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080",
    "observed_summary": "Advisory-only projection.",
    "governance_flags": {},
    "provenance": {},
    "created_at_utc": "2026-05-29T00:00:00Z",
}

_GEO_SPEC_SOURCE_HASH = "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080"
_SVG_BOUNDARY_HASH = "8ed1cc538d8743c24f3c4eb79b0ed66dc4bc6324b43900ca207603dacf289bff"
_ARTIFACT_CANONICAL_HASH = (
    "f22a540c6fab6b45fe301339d6b28471489be3725078e4c8942d64afa2550d1d"
)

_EXPECTED_CANVAS_PROJECTION_SNAPSHOT = {
    "advisory_only": True,
    "canvas_generation_status": "BOUNDARY_PROJECTION_ONLY",
    "data_source_hash": "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080",
    "execution_authority": False,
    "projection_only": True,
    "schema_version": "GeometricProjectionSpec.v1",
    "surface_type": "CANVAS_BOUNDARY",
    "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
}


def _valid_payload() -> dict[str, object]:
    return {
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_005",
        "viewmodel_ref": _VIEWMODEL_REF,
        "canvas_intake_record": default_canvas_intake_record(_VIEWMODEL_REF),
        "renderer_output_declaration": default_renderer_output_declaration(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of RENDERER_CANVAS_BOUNDARY_DEFINED status, advance to "
            "operator decision for WebGL renderer surface authorization."
        ),
        "provenance": {
            "source": "P44_CANVAS_RENDERER_BOUNDARY_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-RENDERER-CANVAS-BOUNDARY-001",
            "evidence_refs": [
                "AALVizGeometricRendererSVG.v1:aal_viz_geometric_renderer_svg_001",
            ],
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_canvas.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Hash stability
# ---------------------------------------------------------------------------

def test_hash_deterministic_and_byte_stable() -> None:
    first = _build(_valid_payload())
    second = _build(_valid_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert canonical_dumps(first) == canonical_dumps(second)


def test_hash_excludes_canonical_hash_and_changes_on_change() -> None:
    packet = _build(_valid_payload())
    preimage = {k: v for k, v in packet.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == packet["canonical_hash"]
    payload2 = _valid_payload()
    payload2["source_operator_decision_ref"] = "DIFFERENT_DECISION_REF"  # type: ignore[assignment]
    packet2 = _build(payload2)
    assert packet2["canonical_hash"] != packet["canonical_hash"]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_canvas_renderer_constants() -> None:
    packet = _build(_valid_payload())
    assert packet["schema_version"] == "AALVizGeometricRendererCanvas.v1"
    assert packet["renderer_canvas_type"] == "AAL_VIZ_GEOMETRIC_RENDERER_CANVAS_BOUNDARY"
    assert packet["renderer_canvas_status"] == "RENDERER_CANVAS_BOUNDARY_DEFINED"
    assert packet["source_svg_renderer_boundary_hash"] == SOURCE_SVG_RENDERER_BOUNDARY_HASH


def test_source_svg_boundary_hash_pin_enforced() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["source_svg_renderer_boundary_hash"] = "b" * 64
    with pytest.raises(ValueError, match="source_svg_renderer_boundary_hash_mismatch"):
        validate_aal_viz_geometric_renderer_canvas(tampered)


# ---------------------------------------------------------------------------
# Authority locks
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Governance flags
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("flag", LOCKED_FALSE_GOVERNANCE_FLAGS)
def test_governance_flags_locked_false(flag: str) -> None:
    payload = _valid_payload()
    payload["governance_flags"][flag] = True  # type: ignore[index]
    with pytest.raises(ValueError, match="governance_flag_must_be_false"):
        _build(payload)


# ---------------------------------------------------------------------------
# Blocked scopes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("scope", REQUIRED_BLOCKED_SCOPES)
def test_missing_required_blocked_scope(scope: str) -> None:
    payload = _valid_payload()
    payload["blocked_scopes"] = [s for s in default_blocked_scopes() if s != scope]  # type: ignore[assignment]
    with pytest.raises(ValueError, match="missing_required_blocked_scope"):
        _build(payload)


def test_canvas_renderer_implementation_not_in_blocked_scopes() -> None:
    scopes = default_blocked_scopes()
    assert "canvas_renderer_implementation" not in scopes


def test_default_blocked_scopes_covers_all_required() -> None:
    scopes = set(default_blocked_scopes())
    for scope in REQUIRED_BLOCKED_SCOPES:
        assert scope in scopes


# ---------------------------------------------------------------------------
# Output declaration
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("flag", LOCKED_FALSE_OUTPUT_FLAGS)
def test_output_declaration_disallowed_flag_true_rejected(flag: str) -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"][flag] = True  # type: ignore[index]
    with pytest.raises(
        ValueError, match=f"renderer_output_declaration_{flag}_must_be_false"
    ):
        _build(payload)


def test_output_declaration_emits_canvas_false_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"]["emits_canvas"] = False  # type: ignore[index]
    with pytest.raises(
        ValueError, match="renderer_output_declaration_emits_canvas_must_be_true"
    ):
        _build(payload)


def test_output_declaration_planning_metadata_false_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"]["emits_planning_metadata"] = False  # type: ignore[index]
    with pytest.raises(
        ValueError, match="renderer_output_declaration_emits_planning_metadata_must_be_true"
    ):
        _build(payload)


def test_output_declaration_execution_authority_true_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"]["execution_authority"] = True  # type: ignore[index]
    with pytest.raises(
        ValueError, match="renderer_output_declaration_execution_authority_must_be_false"
    ):
        _build(payload)


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("token", ["executable", "runtime", "forecast", "inference", "scheduler"])
def test_forbidden_provenance_token_rejected(token: str) -> None:
    payload = _valid_payload()
    payload["provenance"]["source"] = f"test_{token}_source"  # type: ignore[index]
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        _build(payload)


# ---------------------------------------------------------------------------
# Canvas projection — snapshot and structural assertions
# ---------------------------------------------------------------------------

def test_canvas_projection_matches_committed_snapshot() -> None:
    result = build_canvas_projection(_VIEWMODEL_REF)
    assert result == _EXPECTED_CANVAS_PROJECTION_SNAPSHOT, (
        "Canvas projection has diverged from the committed snapshot. "
        "Update _EXPECTED_CANVAS_PROJECTION_SNAPSHOT only after deliberate operator review."
    )


def test_canvas_projection_is_deterministic() -> None:
    first = build_canvas_projection(_VIEWMODEL_REF)
    second = build_canvas_projection(_VIEWMODEL_REF)
    assert canonical_dumps(first) == canonical_dumps(second)


def test_canvas_projection_advisory_only() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert cp["advisory_only"] is True


def test_canvas_projection_execution_authority_false() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert cp["execution_authority"] is False


def test_canvas_projection_projection_only() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert cp["projection_only"] is True


def test_canvas_projection_canvas_generation_status() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert cp["canvas_generation_status"] == "BOUNDARY_PROJECTION_ONLY"


def test_canvas_projection_surface_type() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert cp["surface_type"] == "CANVAS_BOUNDARY"


def test_canvas_projection_schema_version() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert cp["schema_version"] == "GeometricProjectionSpec.v1"


def test_canvas_projection_data_source_hash_pinned() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert cp["data_source_hash"] == _GEO_SPEC_SOURCE_HASH


def test_canvas_projection_title_preserved() -> None:
    cp = build_canvas_projection(_VIEWMODEL_REF)
    assert "Geometric Projection Spec" in cp["title"]


# ---------------------------------------------------------------------------
# Canvas projection — CANVAS_PROJECTION_COMPLIANCE enforcement
# ---------------------------------------------------------------------------

def test_canvas_projection_advisory_only_false_rejected() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["canvas_projection"] = {**packet["canvas_projection"], "advisory_only": False}
    with pytest.raises(ValueError, match="canvas_projection_advisory_only_must_be_true"):
        validate_aal_viz_geometric_renderer_canvas(tampered)


def test_canvas_projection_execution_authority_true_rejected() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["canvas_projection"] = {**packet["canvas_projection"], "execution_authority": True}
    with pytest.raises(ValueError, match="canvas_projection_execution_authority_must_be_false"):
        validate_aal_viz_geometric_renderer_canvas(tampered)


def test_canvas_projection_wrong_generation_status_rejected() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["canvas_projection"] = {
        **packet["canvas_projection"], "canvas_generation_status": "ACTIVE"
    }
    with pytest.raises(
        ValueError,
        match="canvas_projection_canvas_generation_status_must_be_BOUNDARY_PROJECTION_ONLY",
    ):
        validate_aal_viz_geometric_renderer_canvas(tampered)


def test_canvas_projection_wrong_surface_type_rejected() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["canvas_projection"] = {**packet["canvas_projection"], "surface_type": "WEBGL"}
    with pytest.raises(ValueError, match="canvas_projection_surface_type_must_be_CANVAS_BOUNDARY"):
        validate_aal_viz_geometric_renderer_canvas(tampered)


def test_canvas_projection_projection_only_false_rejected() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["canvas_projection"] = {**packet["canvas_projection"], "projection_only": False}
    with pytest.raises(ValueError, match="canvas_projection_projection_only_must_be_true"):
        validate_aal_viz_geometric_renderer_canvas(tampered)


# ---------------------------------------------------------------------------
# Round-trip hash verification (cross-run)
# ---------------------------------------------------------------------------

def test_canvas_round_trip_hash_verification() -> None:
    artifact_path = Path(
        "out/projections/aal_viz_geometric_renderer_canvas_001.latest.json"
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


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/aal_viz_geometric_renderer_canvas.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = _build(_valid_payload())
    jsonschema.validate(packet, schema)


# ---------------------------------------------------------------------------
# Authority posture assertions
# ---------------------------------------------------------------------------

def test_canvas_renderer_implementation_authorized_true() -> None:
    locks = default_authority_locks()
    assert locks["canvas_renderer_implementation_authorized"] is True
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["renderer_boundary_implementation"] is True
    assert locks["svg_renderer_implementation_authorized"] is True


def test_webgl_remains_false() -> None:
    locks = default_authority_locks()
    assert locks["webgl_renderer_implementation_authorized"] is False


def test_emits_canvas_true_in_default_output_declaration() -> None:
    od = default_renderer_output_declaration()
    assert od["emits_canvas"] is True
    assert od["emits_rendered_output"] is False
    assert od["emits_webgl"] is False
    assert od["emits_svg"] is False
    assert od["execution_authority"] is False


def test_source_svg_boundary_hash_constant() -> None:
    assert SOURCE_SVG_RENDERER_BOUNDARY_HASH == _SVG_BOUNDARY_HASH


# ---------------------------------------------------------------------------
# Misc validation
# ---------------------------------------------------------------------------

def test_empty_recommended_next_step_rejected() -> None:
    payload = _valid_payload()
    payload["recommended_next_step"] = "   "  # type: ignore[assignment]
    with pytest.raises(ValueError, match="recommended_next_step_must_be_non_empty_string"):
        _build(payload)


def test_viewmodel_ref_stripped_from_output_artifact() -> None:
    packet = _build(_valid_payload())
    assert "viewmodel_ref" not in packet


def test_default_validation_rules_covers_all_allowed() -> None:
    from core.aal_viz_geometric_renderer_canvas import ALLOWED_VALIDATION_RULES

    rules = set(default_validation_rules())
    for rule in ALLOWED_VALIDATION_RULES:
        assert rule in rules


def test_canvas_intake_record_defaults() -> None:
    rec = default_canvas_intake_record(_VIEWMODEL_REF)
    assert rec["execution_authority"] is False
    assert rec["projection_only"] is True
    assert rec["canvas_generation_status"] == "BOUNDARY_PROJECTION_ONLY"
    assert rec["ordering_applied"] == "CANONICAL_JSON_SORT"
    assert rec["viewmodel_schema_version"] == "GeometricProjectionSpec.v1"
