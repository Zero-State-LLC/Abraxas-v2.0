from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.aal_viz_geometric_renderer_viewmodel_adapter_spec import (
    DECLARED_INPUT_FIELDS,
    DECLARED_OUTPUT_FIELDS,
    LOCKED_FALSE_AUTHORITY_KEYS,
    LOCKED_FALSE_GOVERNANCE_FLAGS,
    LOCKED_TRUE_AUTHORITY_KEYS,
    REQUIRED_BLOCKED_SCOPES,
    SOURCE_WP001_BOUNDARY_HASH,
    build_aal_viz_geometric_renderer_viewmodel_adapter_spec,
    default_authority_locks,
    default_blocked_scopes,
    default_field_mapping_table,
    default_governance_flags,
    default_output_contract,
    default_validation_rules,
    validate_aal_viz_geometric_renderer_viewmodel_adapter_spec,
)
from core.canonical.json import canonical_dumps, canonical_hash

_build = build_aal_viz_geometric_renderer_viewmodel_adapter_spec


def _valid_payload() -> dict[str, object]:
    return {
        "source_p44_plan_hash": "e747808d3a94586fd682ece6a0824b666ac0aa326c0368799d736d85c11864f1",
        "source_operator_decision_ref": "P44_OPERATOR_DECISION_2026_05_29_002",
        "field_mapping_table": default_field_mapping_table(),
        "output_contract": default_output_contract(),
        "validation_rules": default_validation_rules(),
        "blocked_scopes": default_blocked_scopes(),
        "authority_locks": default_authority_locks(),
        "governance_flags": default_governance_flags(),
        "recommended_next_step": (
            "After operator review of VIEWMODEL_ADAPTER_SPEC_DEFINED status, "
            "advance to work package implementation planning for the declared adapter boundary. "
            "Renderer code, metric computation, and P43 surface lanes remain blocked."
        ),
        "provenance": {
            "source": "P44_VIEWMODEL_ADAPTER_SPEC_GATE",
            "advisory_only": True,
            "generated_by": "PATCH-P44-VIEWMODEL-ADAPTER-SPEC-001",
            "evidence_refs": [
                "AALVizGeometricRendererWP001ImplementationBoundary.v1:wp001_implementation_boundary_001",
                "AALVizGeometricRendererImplementationPlan.v1:aal_viz_geometric_renderer_implementation_plan_001",
                "GeometricProjectionSpec.v1:geometric_projection_spec_001",
                "P44OperatorReviewDecision.v1:P44_OPERATOR_DECISION_2026_05_29_002",
            ],
            "upstream_schema_refs": [
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


def test_adapter_spec_constants() -> None:
    packet = _build(_valid_payload())
    assert packet["schema_version"] == "AALVizGeometricRendererViewmodelAdapterSpec.v1"
    assert packet["adapter_spec_type"] == "AAL_VIZ_GEOMETRIC_RENDERER_VIEWMODEL_ADAPTER_SPEC"
    assert packet["adapter_spec_status"] == "VIEWMODEL_ADAPTER_SPEC_DEFINED"
    assert packet["source_wp001_boundary_hash"] == SOURCE_WP001_BOUNDARY_HASH


def test_wp001_boundary_hash_mismatch_rejected() -> None:
    # build_* always stamps the canonical hash; test validate_* directly with a tampered packet
    packet = _build(_valid_payload())
    tampered = dict(packet)
    tampered["source_wp001_boundary_hash"] = "a" * 64
    with pytest.raises(ValueError, match="source_wp001_boundary_hash_mismatch"):
        validate_aal_viz_geometric_renderer_viewmodel_adapter_spec(tampered)


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


@pytest.mark.parametrize("field", DECLARED_INPUT_FIELDS)
def test_missing_field_mapping_for_declared_input(field: str) -> None:
    payload = _valid_payload()
    payload["field_mapping_table"] = [  # type: ignore[assignment]
        e for e in default_field_mapping_table() if e["source_field"] != field
    ]
    with pytest.raises(ValueError, match="missing_field_mapping_for_declared_input"):
        _build(payload)


def test_invalid_mapping_type_rejected() -> None:
    payload = _valid_payload()
    table = [dict(e) for e in default_field_mapping_table()]
    table[0]["mapping_type"] = "EXECUTABLE_TRANSFORM"
    payload["field_mapping_table"] = table  # type: ignore[assignment]
    with pytest.raises(ValueError, match="invalid_mapping_type"):
        _build(payload)


def test_mapping_execution_authority_true_rejected() -> None:
    payload = _valid_payload()
    table = [dict(e) for e in default_field_mapping_table()]
    table[0]["execution_authority"] = True
    payload["field_mapping_table"] = table  # type: ignore[assignment]
    with pytest.raises(ValueError, match="mapping_execution_authority_must_be_false"):
        _build(payload)


@pytest.mark.parametrize("field", DECLARED_OUTPUT_FIELDS)
def test_missing_declared_output_field_rejected(field: str) -> None:
    payload = _valid_payload()
    oc = dict(default_output_contract())
    oc["declared_output_fields"] = [f for f in DECLARED_OUTPUT_FIELDS if f != field]
    payload["output_contract"] = oc  # type: ignore[assignment]
    with pytest.raises(ValueError, match="missing_declared_output_field"):
        _build(payload)


def test_output_contract_emits_rendered_output_true_rejected() -> None:
    payload = _valid_payload()
    oc = dict(default_output_contract())
    oc["emits_rendered_output"] = True
    payload["output_contract"] = oc  # type: ignore[assignment]
    with pytest.raises(ValueError, match="output_contract_emits_rendered_output_must_be_false"):
        _build(payload)


def test_output_contract_emits_metric_values_true_rejected() -> None:
    payload = _valid_payload()
    oc = dict(default_output_contract())
    oc["emits_metric_values"] = True
    payload["output_contract"] = oc  # type: ignore[assignment]
    with pytest.raises(ValueError, match="output_contract_emits_metric_values_must_be_false"):
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
            "contracts/canon/aal_viz_geometric_renderer_viewmodel_adapter_spec.v1.schema.json"
        ).read_text(encoding="utf-8")
    )
    packet = _build(_valid_payload())
    jsonschema.validate(packet, schema)


def test_field_mapping_table_sorted_by_source_field() -> None:
    packet = _build(_valid_payload())
    source_fields = [e["source_field"] for e in packet["field_mapping_table"]]
    assert source_fields == sorted(source_fields)


def test_all_declared_input_fields_covered_in_default_table() -> None:
    covered = {e["source_field"] for e in default_field_mapping_table()}
    for field in DECLARED_INPUT_FIELDS:
        assert field in covered


def test_all_declared_output_fields_in_default_output_contract() -> None:
    oc = default_output_contract()
    covered = set(oc["declared_output_fields"])
    for field in DECLARED_OUTPUT_FIELDS:
        assert field in covered


def test_all_default_mapping_types_are_passthrough_declared_only() -> None:
    for entry in default_field_mapping_table():
        assert entry["mapping_type"] == "PASSTHROUGH_DECLARED_ONLY"
        assert entry["execution_authority"] is False


def test_empty_recommended_next_step_rejected() -> None:
    payload = _valid_payload()
    payload["recommended_next_step"] = "   "  # type: ignore[assignment]
    with pytest.raises(ValueError, match="recommended_next_step_must_be_non_empty_string"):
        _build(payload)
