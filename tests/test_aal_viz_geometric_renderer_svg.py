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
    _xml_escape,
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

_GEO_SPEC_SOURCE_HASH = "fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080"
_ARTIFACT_CANONICAL_HASH = "8ed1cc538d8743c24f3c4eb79b0ed66dc4bc6324b43900ca207603dacf289bff"

_EXPECTED_SVG_SNAPSHOT = (
    '<?xml version="1.0" encoding="utf-8"?>\n'
    "<!-- advisory-only projection surface: no display rendering authorized -->\n"
    '<svg xmlns="http://www.w3.org/2000/svg" version="1.1"\n'
    '     data-advisory-only="true"\n'
    '     data-projection-only="true"\n'
    '     data-schema-version="GeometricProjectionSpec.v1"\n'
    '     data-source-hash="fb546c6efea020673e0b9065ecc363915762eaa926af2eb72d30b8420fc14080">\n'
    "  <title>Geometric Projection Spec \u2014 advisory-only scaffold</title>\n"
    "  <desc>projection-only | advisory-only | no display rendering authorized</desc>\n"
    '  <g id="boundary-projection">\n'
    '    <text id="schema-version-label">GeometricProjectionSpec.v1</text>\n'
    "  </g>\n"
    "</svg>"
)


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


# ---------------------------------------------------------------------------
# GAP-001: committed snapshot reference
# ---------------------------------------------------------------------------

def test_svg_projection_matches_committed_snapshot() -> None:
    result = build_svg_projection(_VIEWMODEL_REF)
    assert result == _EXPECTED_SVG_SNAPSHOT, (
        "SVG output has diverged from the committed snapshot. "
        "Update _EXPECTED_SVG_SNAPSHOT only after deliberate operator review."
    )


# ---------------------------------------------------------------------------
# GAP-002: data-source-hash attribute pinned
# ---------------------------------------------------------------------------

def test_svg_data_source_hash_attribute_pinned() -> None:
    svg_str = build_svg_projection(_VIEWMODEL_REF)
    body = svg_str.split("?>", 1)[-1].strip()
    root = ET.fromstring(body)
    attr = root.get("data-source-hash")
    assert attr == _GEO_SPEC_SOURCE_HASH, (
        f"data-source-hash mismatch: got {attr!r}, expected {_GEO_SPEC_SOURCE_HASH!r}"
    )


# ---------------------------------------------------------------------------
# GAP-003: element-level structural assertions
# ---------------------------------------------------------------------------

def test_svg_element_structure_and_ids() -> None:
    svg_str = build_svg_projection(_VIEWMODEL_REF)
    body = svg_str.split("?>", 1)[-1].strip()
    root = ET.fromstring(body)
    ns = {"svg": "http://www.w3.org/2000/svg"}

    assert root.get("data-advisory-only") == "true"
    assert root.get("data-projection-only") == "true"
    assert root.get("data-schema-version") == "GeometricProjectionSpec.v1"
    assert root.get("data-source-hash") == _GEO_SPEC_SOURCE_HASH

    title_el = root.find("svg:title", ns)
    if title_el is None:
        title_el = root.find("title")
    assert title_el is not None, "missing <title> element"
    assert title_el.text and "Geometric Projection Spec" in title_el.text

    desc_el = root.find("svg:desc", ns)
    if desc_el is None:
        desc_el = root.find("desc")
    assert desc_el is not None, "missing <desc> element"
    assert desc_el.text and "advisory-only" in desc_el.text

    g_el = root.find("svg:g[@id='boundary-projection']", ns)
    if g_el is None:
        g_el = root.find("g[@id='boundary-projection']")
    assert g_el is not None, "missing <g id='boundary-projection'>"

    text_el = g_el.find("svg:text[@id='schema-version-label']", ns)
    if text_el is None:
        text_el = g_el.find("text[@id='schema-version-label']")
    assert text_el is not None, "missing <text id='schema-version-label'>"
    assert text_el.text == "GeometricProjectionSpec.v1"


# ---------------------------------------------------------------------------
# GAP-004: cross-run round-trip hash verification
# ---------------------------------------------------------------------------

def test_svg_round_trip_hash_verification() -> None:
    artifact_path = Path(
        "out/projections/aal_viz_geometric_renderer_svg_001.latest.json"
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
# GAP-005: _xml_escape correctness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw,expected",
    [
        ("plain", "plain"),
        ("a&b", "a&amp;b"),
        ("<tag>", "&lt;tag&gt;"),
        ('"quoted"', "&quot;quoted&quot;"),
        ("a&<b>\"c", "a&amp;&lt;b&gt;&quot;c"),
        ("no special chars 123", "no special chars 123"),
    ],
)
def test_xml_escape_special_characters(raw: str, expected: str) -> None:
    assert _xml_escape(raw) == expected


def test_svg_with_special_char_input_is_well_formed() -> None:
    vr = dict(_VIEWMODEL_REF)
    vr["title"] = 'Title with <special> & "chars"'
    svg_str = build_svg_projection(vr)
    validate_svg_wellformedness(svg_str)
    assert "&lt;special&gt;" in svg_str
    assert "&amp;" in svg_str
    assert "&quot;chars&quot;" in svg_str
