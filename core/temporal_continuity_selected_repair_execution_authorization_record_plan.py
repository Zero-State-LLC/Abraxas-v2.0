from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuitySelectedRepairExecutionAuthorizationRecordPlan.v1"
SOURCE_P102D_AUTHORIZATION_GATE_PATH = (
    "out/temporal_continuity_selected_repair_execution_authorization_gate/latest.json"
)

_P102E_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_P102E_DENIED = "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN_DENIED"
_P102E_READY = "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN_READY"

_P102D_ELIGIBLE = "SELECTED_REPAIR_EXECUTION_AUTHORIZATION_ELIGIBLE"
_P102D_REGENERATION_LANE = "P102D_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_GATE_REGENERATION"
_OPERATOR_DECISION = "OPERATOR_AUTHORIZATION_RECORD_DECISION_REQUIRED"

_DENIED_AUTHORITY: tuple[str, ...] = (
    "authorization_authority",
    "authorization_record_creation_authority",
    "canon_promotion",
    "execution_authority",
    "forecast_influence",
    "production_activation",
    "regeneration_authority",
    "regeneration_execution_authority",
    "repair_authority",
    "repair_execution_authority",
    "runtime_authority",
    "scheduler_mutation",
    "token_minting_authority",
)


def _preserve_list(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return list(value)


def _observe_source(*, root: Path) -> dict[str, Any]:
    source_path = root / SOURCE_P102D_AUTHORIZATION_GATE_PATH
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
        "path": SOURCE_P102D_AUTHORIZATION_GATE_PATH,
        "observed": observed,
        "readable": readable,
        "malformed_json": malformed_json,
        "file_hash": file_hash,
        "payload": payload,
    }


def _classify(source: dict[str, Any]) -> dict[str, Any]:
    if not bool(source["observed"]):
        return {
            "status": _P102E_NOT_COMPUTABLE,
            "record_required": False,
            "recommended_next_lane": _P102D_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P102D authorization gate source is missing; regenerate P102D before deriving an authorization record plan."
            ),
            "blocking_reasons": ["P102D_SOURCE_MISSING"],
        }

    if not bool(source["readable"]):
        return {
            "status": _P102E_NOT_COMPUTABLE,
            "record_required": False,
            "recommended_next_lane": _P102D_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P102D authorization gate source is unreadable; regenerate P102D before deriving an authorization record plan."
            ),
            "blocking_reasons": ["P102D_SOURCE_UNREADABLE"],
        }

    if bool(source["malformed_json"]):
        return {
            "status": _P102E_NOT_COMPUTABLE,
            "record_required": False,
            "recommended_next_lane": _P102D_REGENERATION_LANE,
            "recommended_next_lane_reason": (
                "P102D authorization gate source is malformed JSON; regenerate P102D before deriving an authorization record plan."
            ),
            "blocking_reasons": ["P102D_SOURCE_MALFORMED_JSON"],
        }

    payload = source["payload"] if isinstance(source["payload"], dict) else {}
    p102d_status = str(payload.get("p102d_authorization_gate_status", "NOT_COMPUTABLE"))
    authorization_eligible = bool(payload.get("authorization_eligible", False))
    authorization_granted = bool(payload.get("authorization_granted", False))
    token_minting_allowed = bool(payload.get("token_minting_allowed", False))
    valid_for_execution = bool(payload.get("valid_for_execution", False))
    execution_authority = bool(payload.get("execution_authority", False))

    if (
        p102d_status == _P102D_ELIGIBLE
        and authorization_eligible
        and not authorization_granted
        and not token_minting_allowed
        and not valid_for_execution
        and not execution_authority
    ):
        return {
            "status": _P102E_READY,
            "record_required": True,
            "recommended_next_lane": _OPERATOR_DECISION,
            "recommended_next_lane_reason": (
                "P102D is eligibility-only with all execution and token locks false; an explicit human/operator authorization record decision is required before any future lane may be considered."
            ),
            "blocking_reasons": [
                "AUTHORIZATION_RECORD_NOT_CREATED",
                "OPERATOR_DECISION_REQUIRED",
            ],
        }

    return {
        "status": _P102E_DENIED,
        "record_required": False,
        "recommended_next_lane": _P102D_REGENERATION_LANE,
        "recommended_next_lane_reason": (
            "P102D is not eligible or authority locks drifted; regenerate P102D before deriving an authorization record plan."
        ),
        "blocking_reasons": ["P102D_NOT_ELIGIBLE_OR_AUTHORITY_LOCK_DRIFT"],
    }


def build_temporal_continuity_selected_repair_execution_authorization_record_plan(
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
        "selected_repair_execution_authorization_record_plan_only": True,
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
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "authorization_record_required": bool(classification["record_required"]),
        "authorization_record_created": False,
        "authorization_granted": False,
        "token_minting_allowed": False,
        "token_minting_authority": False,
        "valid_for_execution": False,
        "source_p102d_authorization_gate_path": SOURCE_P102D_AUTHORIZATION_GATE_PATH,
        "source_p102d_authorization_gate_observed": bool(source["observed"]),
        "source_p102d_authorization_gate_readable": bool(source["readable"]),
        "source_p102d_authorization_gate_hash": str(source["file_hash"]),
        "source_p102d_authorization_gate_status": str(
            payload.get("p102d_authorization_gate_status", "NOT_COMPUTABLE")
        ),
        "source_authorization_eligible": bool(payload.get("authorization_eligible", False)),
        "source_authorization_granted": bool(payload.get("authorization_granted", False)),
        "source_token_minting_allowed": bool(payload.get("token_minting_allowed", False)),
        "source_valid_for_execution": bool(payload.get("valid_for_execution", False)),
        "source_recommended_next_lane": str(
            payload.get("recommended_next_lane", "NOT_COMPUTABLE")
        ),
        "p102e_record_plan_status": str(classification["status"]),
        "terminal_lane": "P102E_SELECTED_REPAIR_EXECUTION_AUTHORIZATION_RECORD_PLAN",
        "observed_source_surfaces": [SOURCE_P102D_AUTHORIZATION_GATE_PATH],
        "missing_evidence": [],
        "blocking_reasons": [str(reason) for reason in classification["blocking_reasons"]],
        "degraded_evidence_inputs": _preserve_list(payload.get("degraded_evidence_inputs")),
        "inherited_blockers": _preserve_list(payload.get("inherited_blockers")),
        "inherited_drift_flags": _preserve_list(payload.get("inherited_drift_flags")),
        "semantic_overlap_flags": _preserve_list(payload.get("semantic_overlap_flags")),
        "recommended_next_lane": str(classification["recommended_next_lane"]),
        "recommended_next_lane_reason": str(classification["recommended_next_lane_reason"]),
        "recommended_operator_decision": "CREATE_EXPLICIT_AUTHORIZATION_RECORD_OR_HOLD",
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }

    if not bool(source["observed"]):
        packet_base["missing_evidence"] = [SOURCE_P102D_AUTHORIZATION_GATE_PATH]

    packet = {**packet_base, "packet_hash": canonical_hash(packet_base)}
    return json.loads(
        json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_temporal_continuity_selected_repair_execution_authorization_record_plan(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)
