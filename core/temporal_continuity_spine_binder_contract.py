from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuitySpineBinderContract.v1"
SOURCE_PRECHECK_PATH = "out/temporal_continuity_spine_precheck/latest.json"
RECOMMENDED_BINDER_LANE = "P71_TEMPORAL_CONTINUITY_SPINE_BINDER_CONTRACT"
RECOMMENDED_REPAIR_INDEX_LANE = "P71_TEMPORAL_CONTINUITY_EVIDENCE_REPAIR_INDEX"
RECOMMENDED_P69_REPAIR_LANE = "P69_CANON_RESUME_STATE_REPAIR"
_BLOCKING_LANES = frozenset({RECOMMENDED_P69_REPAIR_LANE, RECOMMENDED_REPAIR_INDEX_LANE})
_DENIED_AUTHORITY = (
    "approval_granted",
    "authorization_granted",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "production_activation",
    "canon_promotion",
    "forecast_influence",
    "scheduler_mutation",
    "runtime_authority",
    "repair_authority",
    "spine_implementation_authority",
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_sorted_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value)


def _as_sorted_group_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    groups = [item for item in value if isinstance(item, dict)]
    return sorted(
        (json.loads(json.dumps(group, sort_keys=True, separators=(",", ":"), ensure_ascii=False)) for group in groups),
        key=lambda group: str(group.get("group_id", "")),
    )


def build_temporal_continuity_spine_binder_contract(
    *,
    repo_root: str | Path = ".",
    source_precheck_path: str = SOURCE_PRECHECK_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    precheck_path = root / source_precheck_path
    precheck_payload = _load_json_dict(precheck_path)
    precheck_observed = precheck_path.exists()
    precheck_usable = precheck_payload is not None
    precheck_hash = _sha256_file(precheck_path) if precheck_usable else "NOT_COMPUTABLE"

    continuity_groups = _as_sorted_group_list(
        precheck_payload.get("continuity_surface_groups") if precheck_usable else None
    )
    binder_inputs = _as_sorted_str_list(
        precheck_payload.get("binder_candidate_inputs") if precheck_usable else None
    )
    blockers = _as_sorted_str_list(precheck_payload.get("blockers") if precheck_usable else None)
    drift_flags = _as_sorted_str_list(precheck_payload.get("drift_flags") if precheck_usable else None)
    semantic_overlap_flags = _as_sorted_str_list(
        precheck_payload.get("semantic_overlap_flags") if precheck_usable else None
    )
    missing_or_not_computable_inputs = _as_sorted_str_list(
        precheck_payload.get("missing_or_not_computable_inputs") if precheck_usable else None
    )
    degraded_inputs = sorted(
        blocker for blocker in blockers if ":degraded:" in blocker
    )
    recommended_next_lane = (
        str(precheck_payload.get("recommended_next_lane", "NOT_COMPUTABLE"))
        if precheck_usable
        else "NOT_COMPUTABLE"
    )

    if not precheck_usable:
        binder_contract_status = "NOT_COMPUTABLE"
        next_allowed_lanes = [RECOMMENDED_P69_REPAIR_LANE]
        blockers = sorted(
            set(blockers) | {f"source_precheck_not_computable:{source_precheck_path}"}
        )
        drift_flags = sorted(set(drift_flags) | {"SOURCE_PRECHECK_NOT_COMPUTABLE"})
        missing_or_not_computable_inputs = sorted(
            set(missing_or_not_computable_inputs) | {source_precheck_path}
        )
    elif recommended_next_lane in _BLOCKING_LANES:
        binder_contract_status = "BLOCKED"
        next_allowed_lanes = [recommended_next_lane]
    elif recommended_next_lane == RECOMMENDED_BINDER_LANE:
        next_allowed_lanes = [RECOMMENDED_BINDER_LANE]
        if degraded_inputs or missing_or_not_computable_inputs:
            binder_contract_status = "CONTRACT_READY_WITH_DEGRADED_EVIDENCE"
        else:
            binder_contract_status = "CONTRACT_READY"
    else:
        binder_contract_status = "BLOCKED"
        next_allowed_lanes = [recommended_next_lane]
        blockers = sorted(
            set(blockers)
            | {f"unexpected_precheck_recommendation:{recommended_next_lane}"}
        )

    packet_base = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "approval_granted": False,
        "authorization_granted": False,
        "execution_authority": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "spine_implementation_authority": False,
        "source_precheck_path": source_precheck_path,
        "source_precheck_hash": precheck_hash,
        "source_precheck_observed": precheck_observed,
        "binder_contract_status": binder_contract_status,
        "continuity_groups": continuity_groups,
        "binder_inputs": binder_inputs,
        "degraded_inputs": degraded_inputs,
        "missing_or_not_computable_inputs": missing_or_not_computable_inputs,
        "semantic_overlap_flags": semantic_overlap_flags,
        "blockers": blockers,
        "drift_flags": drift_flags,
        "next_allowed_lanes": sorted(set(next_allowed_lanes)),
        "denied_authority": sorted(_DENIED_AUTHORITY),
    }
    packet = {
        **packet_base,
        "packet_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_spine_binder_contract(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)
