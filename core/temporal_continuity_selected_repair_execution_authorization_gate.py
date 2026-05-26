from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuitySelectedRepairExecutionAuthorizationGate.v1"
SOURCE_P102C_EXECUTION_PLAN_PATH = (
    "out/temporal_continuity_selected_repair_execution_plan/latest.json"
)

_P102D_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_P102D_BLOCKED = "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_BLOCKED"
_P102D_ELIGIBLE = "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_ELIGIBLE"

_P102C_READY = "SELECTED_REPAIR_EXECUTION_PLAN_READY"
_EXPECTED_BRANCH = "P101_GATE_ONLY"
_EXPECTED_LANE = "P102B_P101_GATE_REGENERATION_EXECUTION_PLAN"

_P102C_REGENERATION_LANE = "P102C_SELECTED_REPAIR_EXECUTION_PLAN_REGENERATION"
_P102E_RECORD_PLAN_LANE = "P102E_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN"

_DENIED_AUTHORITY: tuple[str, ...] = (
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "repair_execution_authority",
    "regeneration_authority",
    "regeneration_execution_authority",
    "execution_authority",
)


def _preserve_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)


def _observe_source(*, root: Path) -> dict[str, Any]:
    source_path = root / SOURCE_P102C_EXECUTION_PLAN_PATH
    observed = source_path.exists()
    readable = False
    malformed_json = False
    file_hash = "NOT_COMPUTABLE"
    payload: dict[str, Any] | None = None

    if observed:
        try:
            source_bytes = source_path.read_bytes()
            readable = True
            file_hash = hashlib.sha256(source_bytes).hexdigest()
        except OSError:
            readable = False
            source_bytes = b""

        if readable:
            try:
                parsed = json.loads(source_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                malformed_json = True
                parsed = None

            if isinstance(parsed, dict):
                payload = parsed
            else:
                malformed_json = True

    return {
        "path": SOURCE_P102C_EXECUTION_PLAN_PATH,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "payload": payload,
    }


def _classify(source: dict[str, Any]) -> dict[str, Any]:
    if not bool(source["observed"]):
        return {
            "status": _P102D_NOT_COMPUTABLE,
            "eligible": False,
            "recommended_next_lane": _P102C_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P102C source is missing; regenerate P102C before deriving a selected repair execution authorization gate."
            ),
            "blocking_reasons": ["P102C_SOURCE_MISSING"],
        }

    if not bool(source["readable"]):
        return {
            "status": _P102D_NOT_COMPUTABLE,
            "eligible": False,
            "recommended_next_lane": _P102C_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P102C source is unreadable; regenerate P102C before deriving a selected repair execution authorization gate."
            ),
            "blocking_reasons": ["P102C_SOURCE_UNREADABLE"],
        }

    if bool(source["malformed_json"]):
        return {
            "status": _P102D_NOT_COMPUTABLE,
            "eligible": False,
            "recommended_next_lane": _P102C_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P102C source is malformed JSON; regenerate P102C before deriving a selected repair execution authorization gate."
            ),
            "blocking_reasons": ["P102C_SOURCE_MALFORMED_JSON"],
        }

    payload = source["payload"] if isinstance(source["payload"], dict) else {}
    p102c_status = str(payload.get("p102c_execution_plan_status", "NOT_COMPUTABLE"))
    selected_branch_type = str(payload.get("selected_branch_type", "NOT_COMPUTABLE"))
    selected_execution_plan_lane = str(
        payload.get("selected_execution_plan_lane", "NOT_COMPUTABLE")
    )

    if (
        p102c_status == _P102C_READY
        and selected_branch_type == _EXPECTED_BRANCH
        and selected_execution_plan_lane == _EXPECTED_LANE
    ):
        return {
            "status": _P102D_ELIGIBLE,
            "eligible": True,
            "recommended_next_lane": _P102E_RECORD_PLAN_LANE,
            "recommended_next_lane_reason": (
                "P102C is ready on the expected P101-only selected repair execution branch; proceed to P102E authorization record planning while remaining advisory-only."
            ),
            "blocking_reasons": [
                "AUTHORIZATION_GRANT_REQUIRES_DOWNSTREAM_RECORD_AND_SEPARATE_GOVERNED_APPROVAL"
            ],
        }

    return {
        "status": _P102D_BLOCKED,
        "eligible": False,
        "recommended_next_lane": _P102C_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P102C is blocked, not computable, or inconsistent with the expected ready branch; regenerate P102C before P102D can be eligible."
        ),
        "blocking_reasons": ["P102C_STATUS_NOT_READY_OR_INCONSISTENT"],
    }


def build_temporal_continuity_selected_repair_execution_authorization_gate(
    *,
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _observe_source(root=root)
    payload = source["payload"] if isinstance(source["payload"], dict) else {}
    classification = _classify(source)

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "selected_repair_execution_authorization_gate_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "repair_execution_authority": False,
        "regeneration_authority": False,
        "regeneration_execution_authority": False,
        "execution_authority": False,
        "authorization_eligible": bool(classification["eligible"]),
        "authorization_granted": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "source_p102c_execution_plan_path": SOURCE_P102C_EXECUTION_PLAN_PATH,
        "source_p102c_execution_plan_observed": bool(source["observed"]),
        "source_p102c_execution_plan_readable": bool(source["readable"]),
        "source_p102c_execution_plan_hash": str(source["file_hash"]),
        "source_p102c_execution_plan_status": str(
            payload.get("p102c_execution_plan_status", "NOT_COMPUTABLE")
        ),
        "source_selected_branch_type": str(
            payload.get("selected_branch_type", "NOT_COMPUTABLE")
        ),
        "source_selected_execution_plan_lane": str(
            payload.get("selected_execution_plan_lane", "NOT_COMPUTABLE")
        ),
        "source_recommended_next_lane": str(
            payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p102d_authorization_gate_status": str(classification["status"]),
        "blocking_reasons": [str(reason) for reason in classification["blocking_reasons"]],
        "degraded_evidence_inputs": _preserve_list(
            payload.get("degraded_evidence_inputs")
        ),
        "inherited_blockers": _preserve_list(payload.get("inherited_blockers")),
        "inherited_drift_flags": _preserve_list(payload.get("inherited_drift_flags")),
        "semantic_overlap_flags": _preserve_list(payload.get("semantic_overlap_flags")),
        "recommended_next_lane": str(classification["recommended_next_lane"]),
        "recommended_next_lane_reason": str(classification["recommended_next_lane_reason"]),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }

    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_selected_repair_execution_authorization_gate(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
