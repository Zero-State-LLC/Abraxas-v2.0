"""Core builder for AAL-Viz Geometric Renderer ViewModel Adapter Specification artifact."""

from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

SCHEMA_VERSION = "AALVizGeometricRendererViewmodelAdapterSpec.v1"
ADAPTER_SPEC_TYPE = "AAL_VIZ_GEOMETRIC_RENDERER_VIEWMODEL_ADAPTER_SPEC"
ADAPTER_SPEC_ID = "aal_viz_geometric_renderer_viewmodel_adapter_spec_001"
ADAPTER_SPEC_STATUS = "VIEWMODEL_ADAPTER_SPEC_DEFINED"
SOURCE_WP001_BOUNDARY_HASH = (
    "10575bc70392c81dd1fe2245277734a462e1f13dd4802bbeab3adac5cf9e585a"
)

DECLARED_INPUT_FIELDS = (
    "canonical_hash",
    "created_at_utc",
    "governance_flags",
    "item_id",
    "observed_summary",
    "provenance",
    "schema_version",
    "title",
)

DECLARED_OUTPUT_FIELDS = (
    "adapter_status",
    "projection_boundary_id",
    "viewmodel_ref",
)

ALLOWED_MAPPING_TYPES = ("PASSTHROUGH_DECLARED_ONLY",)

ALLOWED_VALIDATION_RULES = (
    "AUTHORITY_LOCK_SCAN",
    "FIELD_MAPPING_COMPLETENESS",
    "GOVERNANCE_FALSE_FLAG_SCAN",
    "NO_RUNTIME_MUTATION_SCAN",
    "OUTPUT_FIELDS_COMPLETENESS",
    "SCHEMA_VALIDATION",
    "WORK_PACKAGE_BOUNDARY_CHECK",
)

REQUIRED_BLOCKED_SCOPES = (
    "canon_promotion",
    "forecast_authority",
    "inference_authority",
    "metric_computation",
    "p43_surface_lanes",
    "production_activation",
    "renderer_code",
    "runtime_mutation",
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


class AALVizGeometricRendererViewmodelAdapterSpecValidationError(ValueError):
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
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"forbidden_provenance_reference_detected:{token}"
            )


def default_field_mapping_table() -> list[dict[str, Any]]:
    return [
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "canonical_hash",
            "target_field": "viewmodel_ref.source_hash",
        },
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "created_at_utc",
            "target_field": "viewmodel_ref.created_at_utc",
        },
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "governance_flags",
            "target_field": "viewmodel_ref.governance_flags",
        },
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "item_id",
            "target_field": "projection_boundary_id",
        },
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "observed_summary",
            "target_field": "viewmodel_ref.observed_summary",
        },
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "provenance",
            "target_field": "viewmodel_ref.provenance",
        },
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "schema_version",
            "target_field": "viewmodel_ref.schema_version",
        },
        {
            "execution_authority": False,
            "mapping_type": "PASSTHROUGH_DECLARED_ONLY",
            "source_field": "title",
            "target_field": "viewmodel_ref.title",
        },
    ]


def default_output_contract() -> dict[str, Any]:
    return {
        "declared_output_fields": sorted(DECLARED_OUTPUT_FIELDS),
        "emits_metric_values": False,
        "emits_planning_metadata": True,
        "emits_rendered_output": False,
        "emits_ui_controls": False,
        "output_type": ADAPTER_SPEC_STATUS,
    }


def default_validation_rules() -> list[str]:
    return sorted(ALLOWED_VALIDATION_RULES)


def default_blocked_scopes() -> list[str]:
    return sorted(REQUIRED_BLOCKED_SCOPES)


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


def validate_aal_viz_geometric_renderer_viewmodel_adapter_spec(
    packet: dict[str, Any],
) -> None:
    required = {
        "adapter_spec_id",
        "adapter_spec_status",
        "adapter_spec_type",
        "authority_locks",
        "blocked_scopes",
        "canonical_hash",
        "created_at_utc",
        "field_mapping_table",
        "governance_flags",
        "output_contract",
        "provenance",
        "recommended_next_step",
        "schema_version",
        "source_operator_decision_ref",
        "source_p44_plan_hash",
        "source_wp001_boundary_hash",
        "validation_rules",
    }
    missing = sorted(required - packet.keys())
    if missing:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
            f"missing_required_fields:{missing}"
        )
    if packet["schema_version"] != SCHEMA_VERSION:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError("invalid_schema_version")
    if packet["adapter_spec_type"] != ADAPTER_SPEC_TYPE:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError("invalid_adapter_spec_type")
    if packet["adapter_spec_status"] != ADAPTER_SPEC_STATUS:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError("invalid_adapter_spec_status")

    # WORK_PACKAGE_BOUNDARY_CHECK — source_wp001_boundary_hash must equal the canonical WP-001 hash
    if packet["source_wp001_boundary_hash"] != SOURCE_WP001_BOUNDARY_HASH:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
            "source_wp001_boundary_hash_mismatch"
        )

    # FIELD_MAPPING_COMPLETENESS — all declared input fields must appear as source_field
    mapped_sources = {entry["source_field"] for entry in packet["field_mapping_table"]}
    for field in DECLARED_INPUT_FIELDS:
        if field not in mapped_sources:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"missing_field_mapping_for_declared_input:{field}"
            )

    # mapping_type and execution_authority on each entry
    for entry in packet["field_mapping_table"]:
        if entry.get("mapping_type") not in ALLOWED_MAPPING_TYPES:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"invalid_mapping_type:{entry.get('mapping_type')}"
            )
        if entry.get("execution_authority") is not False:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"mapping_execution_authority_must_be_false:{entry.get('source_field')}"
            )

    # OUTPUT_FIELDS_COMPLETENESS
    oc = packet["output_contract"]
    declared_out = set(oc.get("declared_output_fields", []))
    for field in DECLARED_OUTPUT_FIELDS:
        if field not in declared_out:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"missing_declared_output_field:{field}"
            )
    if oc.get("emits_rendered_output") is not False:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
            "output_contract_emits_rendered_output_must_be_false"
        )
    if oc.get("emits_metric_values") is not False:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
            "output_contract_emits_metric_values_must_be_false"
        )
    if oc.get("emits_ui_controls") is not False:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
            "output_contract_emits_ui_controls_must_be_false"
        )
    if oc.get("emits_planning_metadata") is not True:
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
            "output_contract_emits_planning_metadata_must_be_true"
        )

    # blocked_scopes
    present_scopes = set(packet["blocked_scopes"])
    for scope in REQUIRED_BLOCKED_SCOPES:
        if scope not in present_scopes:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"missing_required_blocked_scope:{scope}"
            )

    # AUTHORITY_LOCK_SCAN
    locks = packet["authority_locks"]
    for key in LOCKED_FALSE_AUTHORITY_KEYS:
        if locks.get(key) is not False:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"authority_lock_must_be_false:{key}"
            )
    for key in LOCKED_TRUE_AUTHORITY_KEYS:
        if locks.get(key) is not True:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"authority_lock_must_be_true:{key}"
            )

    # GOVERNANCE_FALSE_FLAG_SCAN
    for flag in LOCKED_FALSE_GOVERNANCE_FLAGS:
        if packet["governance_flags"].get(flag) is not False:
            raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
                f"governance_flag_must_be_false:{flag}"
            )

    if not isinstance(packet.get("recommended_next_step"), str) or not packet["recommended_next_step"].strip():
        raise AALVizGeometricRendererViewmodelAdapterSpecValidationError(
            "recommended_next_step_must_be_non_empty_string"
        )

    # NO_RUNTIME_MUTATION_SCAN
    _assert_provenance_safe(packet["provenance"])


def compute_aal_viz_geometric_renderer_viewmodel_adapter_spec_hash(
    packet: dict[str, Any],
) -> str:
    return canonical_hash(_preimage(packet))


def serialize_aal_viz_geometric_renderer_viewmodel_adapter_spec(
    packet: dict[str, Any],
) -> str:
    return canonical_dumps(_finalize(packet)) + "\n"


def build_aal_viz_geometric_renderer_viewmodel_adapter_spec(
    payload: dict[str, Any],
) -> dict[str, Any]:
    field_mapping_table = sorted(
        payload.get("field_mapping_table", default_field_mapping_table()),
        key=lambda x: x["source_field"],
    )
    blocked_scopes = sorted(payload.get("blocked_scopes", default_blocked_scopes()))
    validation_rules = sorted(payload.get("validation_rules", default_validation_rules()))
    base = {
        **payload,
        "schema_version": SCHEMA_VERSION,
        "adapter_spec_type": ADAPTER_SPEC_TYPE,
        "adapter_spec_id": payload.get("adapter_spec_id", ADAPTER_SPEC_ID),
        "adapter_spec_status": ADAPTER_SPEC_STATUS,
        "source_wp001_boundary_hash": SOURCE_WP001_BOUNDARY_HASH,
        "field_mapping_table": field_mapping_table,
        "blocked_scopes": blocked_scopes,
        "validation_rules": validation_rules,
    }
    base["canonical_hash"] = compute_aal_viz_geometric_renderer_viewmodel_adapter_spec_hash(base)
    validate_aal_viz_geometric_renderer_viewmodel_adapter_spec(base)
    return _finalize(base)
