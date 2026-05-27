from __future__ import annotations

import json
from typing import Any

from core.canonical.json import canonical_dumps, canonical_hash

INTENDED_LANES = {"SHADOW", "REPLAY", "PROJECTION", "OBSERVATION_ONLY"}
RESERVOIR_FAMILIES = {"ECHO_STATE", "RANDOM_FEATURE_RESERVOIR", "KERNEL_RESERVOIR", "STATE_SPACE_RESERVOIR", "GEOMETRIC_RESERVOIR", "NOT_COMPUTABLE_RESERVOIR"}
RESERVOIR_TYPES = {"STATE_SPACE_REFERENCE", "SPECTRAL_DIAGNOSTIC_REFERENCE", "KRYLOV_ALIGNMENT_REFERENCE", "CONCENTRATION_DIAGNOSTIC_REFERENCE", "GEOMETRY_CONDITIONED_REFERENCE", "BASELINE_RESERVOIR_REFERENCE", "NOT_COMPUTABLE_REFERENCE"}
DECLARED_USES = {"STATE_SPACE_CONTEXT", "SPECTRAL_CONTEXT", "KRYLOV_CONTEXT", "CONCENTRATION_CONTEXT", "GEOMETRY_CONDITIONED_CONTEXT", "BASELINE_COMPARISON_CONTEXT", "NOT_COMPUTABLE_CONTEXT"}
EVIDENCE_REQUIRED = {"BASELINE_COMPARATOR_REQUIRED", "SOURCE_PACKET_REF_REQUIRED", "REPLAY_VALIDATION_REQUIRED", "PROVENANCE_REF_REQUIRED", "SHADOW_OBSERVATION_REQUIRED", "NO_RUNTIME_EFFECT_REQUIRED"}
IMPLEMENTATION_STATUSES = {"DECLARED_ONLY", "METADATA_ONLY", "NOT_IMPLEMENTED", "SHADOW_STUB_ONLY"}
COMPUTATION_STATUSES = IMPLEMENTATION_STATUSES
_GOV_FALSE = ("production_activation", "canon_promotion", "scheduler_mutation", "runtime_authority", "runtime_mutation", "forecast_influence", "execution_authority", "token_minting_allowed", "valid_for_execution", "activation_approved", "authorization_granted")
_STATE_SPACE_POLICY = {"state_space_declared": True, "state_space_computed": False, "state_space_simulated": False, "state_space_affects_runtime": False, "state_space_affects_forecast": False}
_SPECTRAL_POLICY = {"spectral_declared": True, "spectral_computed": False, "spectral_pollution_diagnostic_computed": False, "spectral_affects_routing": False, "spectral_affects_forecast": False}
_KRYLOV_POLICY = {"krylov_declared": True, "krylov_alignment_computed": False, "krylov_chain_generated": False, "krylov_affects_runtime": False, "krylov_affects_scheduler": False}
_FORECASTING_POLICY = {"geometry_conditioned_forecasting_declared": True, "forecast_generated": False, "forecast_probability_updated": False, "forecast_lane_influence": False, "pse_output_influence": False}
_OUTPUT_CONTRACT = {"emits_diagnostic_scores": False, "emits_state_space_outputs": False, "emits_spectral_outputs": False, "emits_krylov_outputs": False, "emits_forecast_outputs": False, "emits_context_labels": True, "emits_observation_notes": True, "emits_runtime_controls": False, "emits_authority_tokens": False}
_FORBIDDEN_TEXT = ("callable", "execute", "runtime", "scheduler", "cache", "forecast", "scoring", "probability", "state-space-simulation", "spectral", "krylov")


def default_reservoir_declarations() -> list[dict[str, Any]]:
    return [{"reservoir_id": "RGD-RESERVOIR-BASELINE", "reservoir_type": "BASELINE_RESERVOIR_REFERENCE", "description": "Baseline reservoir declaration for metadata-only diagnostics.", "declared_use": "BASELINE_COMPARISON_CONTEXT", "evidence_required": ["BASELINE_COMPARATOR_REQUIRED", "NO_RUNTIME_EFFECT_REQUIRED"], "implementation_status": "DECLARED_ONLY"}]


def default_state_space_policy() -> dict[str, bool]: return dict(_STATE_SPACE_POLICY)
def default_spectral_policy() -> dict[str, bool]: return dict(_SPECTRAL_POLICY)
def default_krylov_policy() -> dict[str, bool]: return dict(_KRYLOV_POLICY)
def default_forecasting_policy() -> dict[str, bool]: return dict(_FORECASTING_POLICY)
def default_output_contract() -> dict[str, bool]: return dict(_OUTPUT_CONTRACT)


def compute_reservoir_geometry_diagnostic_hash(packet_without_hash: dict[str, Any]) -> str:
    body = {k: v for k, v in packet_without_hash.items() if k != "canonical_hash"}
    return canonical_hash(body)


def validate_reservoir_geometry_diagnostic(packet: dict[str, Any]) -> None:
    if packet.get("diagnostic_type") != "RESERVOIR_GEOMETRY_DIAGNOSTIC":
        raise ValueError("diagnostic_type must be RESERVOIR_GEOMETRY_DIAGNOSTIC")
    scope = packet.get("diagnostic_scope", {})
    if scope.get("intended_lane") not in INTENDED_LANES:
        raise ValueError("unknown intended_lane")
    if scope.get("reservoir_family") not in RESERVOIR_FAMILIES:
        raise ValueError("unknown reservoir_family")

    declarations = packet.get("reservoir_declarations", [])
    if not declarations:
        raise ValueError("reservoir_declarations must be non-empty")
    ids = [d.get("reservoir_id") for d in declarations]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate reservoir_id")
    for d in declarations:
        if d.get("reservoir_type") not in RESERVOIR_TYPES:
            raise ValueError("unknown reservoir_type")
        if d.get("declared_use") not in DECLARED_USES:
            raise ValueError("unknown declared_use")
        if d.get("implementation_status") not in IMPLEMENTATION_STATUSES:
            raise ValueError("unknown implementation_status")
        for e in d.get("evidence_required", []):
            if e not in EVIDENCE_REQUIRED:
                raise ValueError("unknown evidence_required")

    for name, value, expected in (
        ("state_space_policy", packet.get("state_space_policy", {}), _STATE_SPACE_POLICY),
        ("spectral_policy", packet.get("spectral_policy", {}), _SPECTRAL_POLICY),
        ("krylov_policy", packet.get("krylov_policy", {}), _KRYLOV_POLICY),
        ("forecasting_policy", packet.get("forecasting_policy", {}), _FORECASTING_POLICY),
        ("output_contract", packet.get("output_contract", {}), _OUTPUT_CONTRACT),
    ):
        for k, v in expected.items():
            if value.get(k) is not v:
                raise ValueError(f"{name}.{k} must be {str(v).lower()}")

    if packet.get("computation_status") not in COMPUTATION_STATUSES:
        raise ValueError("unknown computation_status")

    gov = packet.get("governance_flags", {})
    for key in _GOV_FALSE:
        if gov.get(key) is not False:
            raise ValueError(f"governance_flags.{key} must be false")

    prov = packet.get("provenance", {})
    blob_parts = []
    for key in ("source", "generated_by"):
        v = prov.get(key)
        if isinstance(v, str):
            blob_parts.append(v.lower())
    for item in prov.get("evidence_refs", []):
        if isinstance(item, str):
            blob_parts.append(item.lower())
    blob = " ".join(blob_parts)
    if any(term in blob for term in _FORBIDDEN_TEXT):
        raise ValueError("forbidden executable/runtime/scheduler/forecast/scoring/probability/simulation/spectral/Krylov references")

    expected_hash = compute_reservoir_geometry_diagnostic_hash(packet)
    if packet.get("canonical_hash") != expected_hash:
        raise ValueError("canonical_hash mismatch")


def build_reservoir_geometry_diagnostic(*, diagnostic_id: str, source_attachment_refs: list[str], source_signal_packet_refs: list[str], source_metric_registry_refs: list[str], source_projection_refs: list[str], source_route_metadata_refs: list[str], diagnostic_scope: dict[str, str], reservoir_declarations: list[dict[str, Any]], computation_status: str, provenance: dict[str, Any], created_at_utc: str, schema_version: str = "ReservoirGeometryDiagnostic.v1") -> dict[str, Any]:
    normalized = [{**d, "evidence_required": sorted(d.get("evidence_required", []))} for d in reservoir_declarations]
    packet_no_hash = {
        "schema_version": schema_version,
        "diagnostic_id": diagnostic_id,
        "diagnostic_type": "RESERVOIR_GEOMETRY_DIAGNOSTIC",
        "source_attachment_refs": sorted(source_attachment_refs),
        "source_signal_packet_refs": sorted(source_signal_packet_refs),
        "source_metric_registry_refs": sorted(source_metric_registry_refs),
        "source_projection_refs": sorted(source_projection_refs),
        "source_route_metadata_refs": sorted(source_route_metadata_refs),
        "diagnostic_scope": diagnostic_scope,
        "reservoir_declarations": sorted(normalized, key=lambda x: str(x.get("reservoir_id", ""))),
        "state_space_policy": default_state_space_policy(),
        "spectral_policy": default_spectral_policy(),
        "krylov_policy": default_krylov_policy(),
        "forecasting_policy": default_forecasting_policy(),
        "output_contract": default_output_contract(),
        "computation_status": computation_status,
        "governance_flags": {k: False for k in _GOV_FALSE},
        "provenance": provenance,
        "created_at_utc": created_at_utc,
    }
    packet = {**packet_no_hash, "canonical_hash": compute_reservoir_geometry_diagnostic_hash(packet_no_hash)}
    validate_reservoir_geometry_diagnostic(packet)
    return json.loads(canonical_dumps(packet))


def serialize_reservoir_geometry_diagnostic(packet: dict[str, Any]) -> str:
    validate_reservoir_geometry_diagnostic(packet)
    return canonical_dumps(packet) + "\n"
