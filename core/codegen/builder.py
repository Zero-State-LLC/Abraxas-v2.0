from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash

from contracts.codegen import (
    CodeDropEnvelope,
    LaneSignals,
    PatchContract,
)

DEFAULT_LANE_SIGNALS: dict[str, Any] = {
    "lane": "ADVISORY_STACK_HELD_FOR_OPERATOR",
    "downstream": "NOT_COMPUTABLE",
    "advisory_only": True,
    "projection_only": True,
    "shadow_replay_emphasis": True,
    "safe_to_auto_continue": False,
    "valid_for_execution": False,
}

DEFAULT_PROVENANCE: dict[str, str] = {
    "source_gap_analysis": (
        "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
    ),
    "continuity_lane": "P102G+CODEGEN-ADVISORY",
    "generated_by": "ABX_CODEGEN_INTELLIGENCE_SPINE",
}


def _stable_hex_id(payload: Mapping[str, Any]) -> str:
    return canonical_hash(payload)


def _lane_signals(value: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(DEFAULT_LANE_SIGNALS)
    if value is not None:
        payload.update(dict(value))
    LaneSignals.model_validate(payload)
    return payload


def _provenance(value: Mapping[str, Any] | None = None) -> dict[str, str]:
    payload = dict(DEFAULT_PROVENANCE)
    if value is not None:
        payload.update({key: str(item) for key, item in value.items()})
    return payload


def build_patch_contract(
    *,
    target_path: str,
    change_type: str,
    proposed_content: Mapping[str, Any],
    rationale: str,
    lane_signals: Mapping[str, Any] | None = None,
    provenance: Mapping[str, Any] | None = None,
    patch_id: str | None = None,
) -> PatchContract:
    payload: dict[str, Any] = {
        "schema_version": "PatchContract.v1",
        "target_path": target_path,
        "change_type": change_type,
        "proposed_content": dict(proposed_content),
        "rationale": rationale,
        "lane_signals": _lane_signals(lane_signals),
        "provenance": _provenance(provenance),
    }
    payload["patch_id"] = patch_id or _stable_hex_id(payload)
    return PatchContract.model_validate(payload)


def build_code_drop_envelope(
    *,
    patches: Sequence[PatchContract | Mapping[str, Any]],
    timestamp: str,
    required_fixtures: Sequence[str],
    validation_commands: Sequence[str],
    residual_risks: Sequence[str],
    lane_signals: Mapping[str, Any] | None = None,
    provenance: Mapping[str, Any] | None = None,
    envelope_id: str | None = None,
) -> CodeDropEnvelope:
    patch_payloads = [
        patch.model_dump() if isinstance(patch, PatchContract) else dict(patch)
        for patch in patches
    ]
    payload: dict[str, Any] = {
        "schema_version": "CodeDropEnvelope.v1",
        "timestamp": timestamp,
        "patches": patch_payloads,
        "required_fixtures": tuple(required_fixtures),
        "validation_commands": tuple(validation_commands),
        "residual_risks": tuple(residual_risks),
        "lane_signals": _lane_signals(lane_signals),
        "provenance": _provenance(provenance),
    }
    payload["envelope_id"] = envelope_id or _stable_hex_id(payload)
    normalized = CodeDropEnvelope.model_validate(
        {**payload, "canonical_hash": None}
    ).model_dump()
    normalized.pop("canonical_hash", None)
    payload["canonical_hash"] = canonical_hash(normalized)
    return CodeDropEnvelope.model_validate(payload)
