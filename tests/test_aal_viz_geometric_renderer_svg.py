from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer_svg import (
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_FALSE_OUTPUT_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    REQUIRED_BLOCKED_SCOPES,
    SOURCE_RENDERER_BOUNDARY_HASH,
    build_aal_viz_geometric_renderer_svg,
    build_svg_projection,
    default_authority_locks,
    default_blocked_scopes,
    default_governance_flags,
    default_renderer_output_declaration,
    default_validation_rules,
    validate_aal_viz_geometric_renderer_svg,
    validate_svg_wellformedness,
)
from core.canonical.json import canonical_dumps, canonical_hash

_build = build_aal_viz_geometric_renderer_svg

_VIEWMODEL_REF = {
    "schema_version": "GeometricProjectionSpec.v1",
    "title": "Geometric Projection Spec \u2014 advisory-only scaffold",
    "source_hash": "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080",
    "observed_summary": "Advisory-only projection.",
    "governance_flags": {},
    "provenance": {},
    "created_at_utc": "2026-05-29T00:00:00Z",
}


def _valid_payload() -> dict[str, object]:
    return {
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_004",
        "viewmodel_ref": _VIEWMODEL_REF,
        "svg_intake_record": {
            "execution_authority": False,
            "input_fields_accepted": sorted(
                ["adapter_status", "projection_boundary_id", "viewmodel_ref"]
            ),
            "ordering_applied": "CANONICAL_JSON_SORT",
            "projection_only": True,
            "svg_generation_status": "BOUNDARY_PROJECTION_ONLY",
            "viewmodel_schema_version": "GeometricProjectionSpec.v1",
        },
        "renderer_output_declaration": default_renderer_output_declaration(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of RENDERER_SVG_BOUNDARY_DEFINED status, advance to "
            "operator decision for Canvas or WebGL renderer surface authorization."
        ),
        "provenance": {
            "source": "P44_SVG_RENDERER_BOUNDARY_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-RENDERER-SVG-BOUNDARY-001",
            "evidence_refs": [
                "AALVizGeometricRenderer.v1:aal_viz_geometric_renderer_001",
                "GeometricProjectionSpec.v1:geometric_projection_spec_001",
                "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_004",
            ],
            "upstream_schema_refs": [
                "contracts/canon/aal_viz_geometric_renderer_svg.v1.schema.json",
                "contracts/canon/aal_viz_geometric_renderer.v1.schema.json",
            ],
        },
        "created_at_utc": "2026-05-29T00:00:00Z",
    }


def test_hash_deterministic_and_byte_stable() -> None:
    first = _build(_valid_payload())
    second = _build(_valid_payload())
    assert first["canonical_hash"] == second["canonical_hash"]
    assert canonical_dumps(first) == canonical_dumps(second)


def test_svg_renderer_constants() -> None:
    packet = _build(_valid_payload())
    assert packet["schema_version"] == "AALVizGeometricRendererSVG.v1"
    assert packet["renderer_svg_type"] == "AAL_VIZ_GEOMETRIC_RENDERER_SVG_BOUNDARY"
    assert packet["renderer_svg_status"] == "RENDERER_SVG_BOUNDARY_DEFINED"
    assert packet["source_renderer_boundary_hash"] == SOURCE_RENDERER_BOUNDARY_HASH


def test_renderer_boundary_hash_pin_enforced() -> None:
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["source_renderer_boundary_hash"] = "b" * 64
    with pytest.raises(ValueError, match="source_renderer_boundary_hash_mismatch"):
        validate_aal_viz_geometric_renderer_svg(tampered)


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


def test_output_declaration_emits_svg_false_rejected() -> None:
    payload = _valid_payload()
    payload["renderer_output_declaration"]["emits_svg"] = False  # type: ignore[index]
    with pytest.raises(
        ValueError, match="renderer_output_declaration_emits_svg_must_be_true"
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


@pytest.mark.parametrize("token", ["executable", "runtime", "forecast", "inference", "scheduler"])
def test_forbidden_provenance_token_rejected(token: str) -> None:
    payload = _valid_payload()
    payload["provenance"]["source"] = f"test_{token}_source"  # type: ignore[index]
    with pytest.raises(ValueError, match="forbidden_provenance_reference_detected"):
        _build(payload)


def test_hash_excludes_canonical_hash_and_changes_on_change() -> None:
    packet = _build(_valid_payload())
    preimage = {k: v for k, v in packet.items() if k != "canonical_hash"}
    assert canonical_hash(preimage) == packet["canonical_hash"]
    payload2 = _valid_payload()
    payload2["source_operator_decision_ref"] = "DIFFERENT_DECISION_REF"  # type: ignore[assignment]
    packet2 = _build(payload2)
    assert packet2["canonical_hash"] != packet["canonical_hash"]


def test_schema_validates_fixture() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        Path("contracts/canon/aal_viz_geometric_renderer_svg.v1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    packet = _build(_valid_payload())
    jsonschema.validate(packet, schema)


def test_svg_projection_is_well_formed_xml() -> None:
    packet = _build(_valid_payload())
    svg_str = packet["svg_projection"]
    assert svg_str
    validate_svg_wellformedness(svg_str)
    body = svg_str.split("?>", 1)[-1].strip()
    root = ET.fromstring(body)
    assert root.tag.endswith("svg") or "svg" in root.tag


def test_svg_projection_contains_schema_version() -> None:
    svg_str = build_svg_projection(_VIEWMODEL_REF)
    assert "GeometricProjectionSpec.v1" in svg_str


def test_svg_projection_contains_advisory_annotation() -> None:
    svg_str = build_svg_projection(_VIEWMODEL_REF)
    assert "advisory-only" in svg_str
    assert "no display rendering authorized" in svg_str


def test_svg_projection_contains_title() -> None:
    svg_str = build_svg_projection(_VIEWMODEL_REF)
    assert "Geometric Projection Spec" in svg_str


def test_svg_projection_is_byte_stable() -> None:
    first = build_svg_projection(_VIEWMODEL_REF)
    second = build_svg_projection(_VIEWMODEL_REF)
    assert first == second


def test_svg_renderer_implementation_authorized_true() -> None:
    locks = default_authority_locks()
    assert locks["svg_renderer_implementation_authorized"] is True
    assert locks["advisory_only"] is True
    assert locks["projection_only"] is True
    assert locks["renderer_boundary_implementation"] is True
    assert locks["work_package_definition_only"] is False


def test_webgl_canvas_remain_false() -> None:
    locks = default_authority_locks()
    assert locks["webgl_renderer_implementation_authorized"] is False
    assert locks["canvas_renderer_implementation_authorized"] is False


def test_default_blocked_scopes_does_not_include_svg_renderer_implementation() -> None:
    scopes = default_blocked_scopes()
    assert "svg_renderer_implementation" not in scopes


def test_default_blocked_scopes_covers_all_required() -> None:
    scopes = set(default_blocked_scopes())
    for scope in REQUIRED_BLOCKED_SCOPES:
        assert scope in scopes


def test_default_validation_rules_covers_all_allowed() -> None:
    from core.aal_viz_geometric_renderer_svg import ALLOWED_VALIDATION_RULES

    rules = set(default_validation_rules())
    for rule in ALLOWED_VALIDATION_RULES:
        assert rule in rules


def test_empty_recommended_next_step_rejected() -> None:
    payload = _valid_payload()
    payload["recommended_next_step"] = "   "  # type: ignore[assignment]
    with pytest.raises(ValueError, match="recommended_next_step_must_be_non_empty_string"):
        _build(payload)


def test_viewmodel_ref_stripped_from_output_artifact() -> None:
    packet = _build(_valid_payload())
    assert "viewmodel_ref" not in packet


def test_emits_svg_true_in_default_output_declaration() -> None:
    od = default_renderer_output_declaration()
    assert od["emits_svg"] is True
    assert od["emits_rendered_output"] is False
    assert od["emits_webgl"] is False
    assert od["emits_canvas"] is False
