"""Core builder for AAL-Viz Geometric Renderer Contract Specification artifact."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererContractSpec.v1"
CONTRACT_SPEC_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_CONTRACT_SPEC"
CONTRACT_SPEC_ID = "aal_viz_geometric_renderer_contract_spec_001"
CONTRACT_SPEC_STATUS = "RENDERER_CONTRACT_SPEC_DEFINED"

SOURCE_VIEWMODEL_ADAPTER_SPEC_HASH = (
    "90306c734bd9bbf252bd680899f80ac06ab14562683c999e9580b8631eff4c0f"
)
SOURCE_WP001_BOUNDARY_HASH = (
    "10575bc70392c81dd1fe2245277734a462e1f13dd4802bbeab3adac5cf9e585a"
)
SOURCE_P44_PLAN_HASH = (
    "e747808d3a94586fd682ece6a0824b666ac0aa326c0368799d736d85c11864f1"
)

VIEWMODEL_REQUIRED_FIELDS = (
    "created_at_utc",
    "governance_flags",
    "observed_summary",
    "provenance",
    "schema_version",
    "source_hash",
    "title",
)

VIEWMODEL_ACCEPTED_ADAPTER_STATUS = "VIEWMODEL_ADAPTER_SPEC_DEFINED"
VIEWMODEL_REQUIRED_SCHEMA_VERSION = "GeometricProjectionSpec.v1"

ALLOWED_VALIDATION_RULES = (
    "AUTHORITY_LOCK_SCAN",
    "FIELD_MAPPING_COMPLETENESS",
    "GOVERNANCE_FALSE_FLAG_SCAN",
    "NO_RUNTIME_MUTATION_SCAN",
    "OUTPUT_CONTRACT_COMPLIANCE",
    "SCHEMA_VALIDATION",
    "SOURCE_REF_PRESERVATION_CHECK",
    "VIEWMODEL_ADAPTER_SPEC_CHAIN_CHECK",
)

REQUIRED_BLOCKED_SCOPES = (
    "canvas_renderer_implementation",
    "canon_promotion",
    "forecast_authority",
    "inference_authority",
    "metric_computation",
    "p43_surface_lanes",
    "production_activation",
    "renderer_code",
    "runtime_mutation",
    "svg_renderer_implementation",
    "webgl_renderer_implementation",
)

LOCKED_FALSE_AUTHORITY_KEYS = (
    "baseline_mutation",
    "canon_promotion",
    "governance_authority_mutation",
    "metric_computation_authorized",
    "p43_surface_lanes_authorized",
    "production_activation",
    "renderer_code_authorized",
    "runtime_mutation",
    "scheduler_mutation",
)

LOCKED_TRUE_AUTHORITY_KEYS = (
    "advisory_only",
    "projection_only",
    "work_package_definition_only",
)

LOCKED_FALSE_GOVERNANCE_FLAGS = (
    "activation_approved",
    "authorization_granted",
    "canon_promotion",
    "execution_authority",
    "forecast_influence",
    "production_activation",
    "runtime_authority",
    "runtime_mutation",
    "scheduler_mutation",
    "token_minting_allowed",
    "valid_for_execution",
)

LOCKED_FALSE_OUTPUT_FLAGS = (
    "emits_canvas",
    "emits_forecast_inputs",
    "emits_metric_values",
    "emits_rendered_output",
    "emits_runtime_controls",
    "emits_svg",
    "emits_ui_controls",
    "emits_webgl",
)

FORBIDDEN_PROVENANCE_TOKENS = (
    "cache",
    "callable",
    "canvas",
    "executable",
    "forecast",
    "inference",
    "metric-computation",
    "rendering",
    "route-control",
    "runtime",
    "scheduler",
    "svg",
    "ui",
    "webgl",
)


class AALVizGeometricRendererContractSpecValidationError(ValueError):
    pass


def _finalize(item: dict[str, Any]) -> dict[str, Any]:
    return json.loads(canonical_dumps(item))


def _preimage(item: dict[str, Any]) -> dict[str, Any]:
    out = dict(item)
    out.pop("canonical_hash", None)
    return out


def _assert_provenance_safe(provenance: dict[str, Any]) -> None:
    lowered = json.dumps(provenance).lower()
    for token in FORBIDDEN_PROVENANCE_TOKENS:
        if token in lowered:
            raise AALVizGeometricRendererContractSpecValidationError(
                f"forbidden_provenance_reference_detected:{token}"
            )


def default_renderer_input_contract() -> dict[str, Any]:
    return {
        "allowed_input_fields": sorted(
            ["adapter_status", "projection_boundary_id", "viewmodel_ref"]
        ),
        "allowed_input_schema": "GeometricProjectionSpec.v1",
        "execution_authority": False,
        "input_description": (
            "The renderer contract MAY receive only the three declared output fields "
            "from the ViewModel Adapter Spec: adapter_status, projection_boundary_id, viewmodel_ref. "
            "These carry the eight GeometricProjectionSpec.v1 source fields via PASSTHROUGH_DECLARED_ONLY mapping. "
            "No additional fields are permitted. No executable input is permitted."
        ),
        "input_source": "VIEWMODEL_ADAPTER_SPEC_OUTPUT",
        "metric_computation": False,
        "renderer_code": False,
    }


def default_renderer_output_contract() -> dict[str, Any]:
    return {
        "emits_canvas": False,
        "emits_forecast_inputs": False,
        "emits_metric_values": False,
        "emits_planning_metadata": True,
        "emits_rendered_output": False,
        "emits_runtime_controls": False,
        "emits_svg": False,
        "emits_ui_controls": False,
        "emits_webgl": False,
        "execution_authority": False,
    }


def default_viewmodel_acceptance_rules() -> dict[str, Any]:
    return {
        "accepted_adapter_status": VIEWMODEL_ACCEPTED_ADAPTER_STATUS,
        "accepted_source_schema_version": VIEWMODEL_REQUIRED_SCHEMA_VERSION,
        "execution_authority": False,
        "governance_flags_must_all_be_false": True,
        "projection_boundary_id_must_match_source_item_id": True,
        "provenance_forbidden_token_scan_required": True,
        "required_viewmodel_ref_fields": sorted(VIEWMODEL_REQUIRED_FIELDS),
    }


def default_deterministic_ordering_contract() -> dict[str, Any]:
    return {
        "contract_id": "ordering-002-renderer-contract-canonical",
        "determinism_guarantee": "BYTE_STABLE_ACROSS_RUNS",
        "execution_authority": False,
        "hash_algorithm": "SHA-256",
        "hash_input": "canonical_preimage_excluding_canonical_hash",
        "ordering_basis": "CANONICAL_JSON_SORT",
        "ordering_status": "CONTRACT_DECLARED_ONLY",
        "surface_family_sort_key": "surface_family_id_lexicographic",
        "within_family_sort_key": "item_id_lexicographic",
    }


def default_source_ref_preservation_rules() -> dict[str, Any]:
    return {
        "evidence_refs_must_include_all_upstream_refs": True,
        "execution_authority": False,
        "required_upstream_hashes": {
            "source_p44_plan_hash": SOURCE_P44_PLAN_HASH,
            "source_viewmodel_adapter_spec_hash": SOURCE_VIEWMODEL_ADAPTER_SPEC_HASH,
            "source_wp001_boundary_hash": SOURCE_WP001_BOUNDARY_HASH,
        },
        "upstream_refs_may_not_be_dropped": True,
        "upstream_refs_may_not_be_mutated": True,
    }


def default_blocked_scopes() -> list[str]:
    return sorted(REQUIRED_BLOCKED_SCOPES)


def default_validation_rules() -> list[str]:
    return sorted(ALLOWED_VALIDATION_RULES)


def default_authority_locks() -> dict[str, Any]:
    return {
        "advisory_only": True,
        "baseline_mutation": False,
        "canon_promotion": False,
        "governance_authority_mutation": False,
        "metric_computation_authorized": False,
        "p43_surface_lanes_authorized": False,
        "production_activation": False,
        "projection_only": True,
        "renderer_code_authorized": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "work_package_definition_only": True,
    }


def default_governance_flags() -> dict[str, Any]:
    return {
        "activation_approved": False,
        "authorization_granted": False,
        "canon_promotion": False,
        "execution_authority": False,
        "forecast_influence": False,
        "production_activation": False,
        "runtime_authority": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
    }


def validate_aal_viz_geometric_renderer_contract_spec(
    packet: dict[str, Any],
) -> None:
    required = {
        "authority_locks",
        "blocked_scopes",
        "canonical_hash",
        "contract_spec_id",
        "contract_spec_status",
        "contract_spec_type",
        "created_at_utc",
        "deterministic_ordering_contract",
        "governance_flags",
        "provenance",
        "recommended_next_step",
        "renderer_input_contract",
        "renderer_output_contract",
        "schema_version",
        "source_operator_decision_ref",
        "source_p44_plan_hash",
        "source_ref_preservation_rules",
        "source_viewmodel_adapter_spec_hash",
        "source_wp001_boundary_hash",
        "validation_rules",
        "viewmodel_acceptance_rules",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererContractSpecValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererContractSpecValidationError("invalid_schema_version")
    if packet["contract_spec_type"] != CONTRACT_SPEC_TYPE:
        raise AALVizGeometricRendererContractSpecValidationError("invalid_contract_spec_type")
    if packet["contract_spec_status"] != CONTRACT_SPEC_STATUS:
        raise AALVizGeometricRendererContractSpecValidationError("invalid_contract_spec_status")

    # VIEWMODEL_ADAPTER_SPEC_CHAIN_CHECK
    if packet["source_viewmodel_adapter_spec_hash"] != SOURCE_VIEWMODEL_ADAPTER_SPEC_HASH:
        raise AALVizGeometricRendererContractSpecValidationError(
            "source_viewmodel_adapter_spec_hash_mismatch"
        )

    # SOURCE_REF_PRESERVATION_CHECK
    if packet["source_wp001_boundary_hash"] != SOURCE_WP001_BOUNDARY_HASH:
        raise AALVizGeometricRendererContractSpecValidationError(
            "source_wp001_boundary_hash_mismatch"
        )
    if packet["source_p44_plan_hash"] != SOURCE_P44_PLAN_HASH:
        raise AALVizGeometricRendererContractSpecValidationError(
            "source_p44_plan_hash_mismatch"
        )

    # OUTPUT_CONTRACT_COMPLIANCE
    oc = packet["renderer_output_contract"]
    for flag in LOCKED_FALSE_OUTPUT_FLAGS:
        if oc.get(flag) is not False:
            raise AALVizGeometricRendererContractSpecValidationError(
                f"renderer_output_contract_{flag}_must_be_false"
            )
    if oc.get("emits_planning_metadata") is not True:
        raise AALVizGeometricRendererContractSpecValidationError(
            "renderer_output_contract_emits_planning_metadata_must_be_true"
        )
    if oc.get("execution_authority") is not False:
        raise AALVizGeometricRendererContractSpecValidationError(
            "renderer_output_contract_execution_authority_must_be_false"
        )

    # blocked_scopes
    present_scopes = set(packet["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        if scope not in present_scopes:
            raise AALVizGeometricRendererContractSpecValidationError(
                f"missing_required_blocked_scope:{scope}"
            )

    # AUTHORITY_LOCK_SCAN
    locks = packet["authority_locks"]
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(key) is not False:
            raise AALVizGeometricRendererContractSpecValidationError(
                f"authority_lock_must_be_false:{key}"
            )
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(key) is not True:
            raise AALVizGeometricRendererContractSpecValidationError(
                f"authority_lock_must_be_true:{key}"
            )

    # GOVERNANCE_FALSE_FLAG_SCAN
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererContractSpecValidationError(
                f"governance_flag_must_be_false:{flag}"
            )

    if (
        not isinstance(packet.get("recommended_next_step"), str)
        or not packet["recommended_next_step"].strip()
    ):
        raise AALVizGeometricRendererContractSpecValidationError(
            "recommended_next_step_must_be_non_empty_string"
        )

    # NO_RUNTIME_MUTATION_SCAN
    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_contract_spec_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_contract_spec(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_contract_spec(
    payload: dict[str, Any],
) -> dict[str, Any]:
    blocked_scopes = sorted(payload.get("blocked_scopes", default_blocked_scopes()))
    validation_rules = sorted(payload.get("validation_rules", default_validation_rules()))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "contract_spec_type": CONTRACT_SPEC_TYPE,
        "contract_spec_id": payload.get("contract_spec_id", CONTRACT_SPEC_ID),
        "contract_spec_status": CONTRACT_SPEC_STATUS,
        "source_viewmodel_adapter_spec_hash": SOURCE_VIEWMODEL_ADAPTER_SPEC_HASH,
        "source_wp001_boundary_hash": SOURCE_WP001_BOUNDARY_HASH,
        "source_p44_plan_hash": SOURCE_P44_PLAN_HASH,
        "blocked_scopes": blocked_scopes,
        "validation_rules": validation_rules,
    }
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_contract_spec_hash(base)
    validate_aal_viz_geometric_renderer_contract_spec(base)
    return _finalize(base)
