from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "TemporalContinuityBinderReadinessAudit.v1"
SOURCE_BINDER_CONTRACT_PATH = "out/temporal_continuity_spine_binder_contract/latest.json"

_DENIED_AUTHORITY = (
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


def _partition_groups(
    continuity_groups: list[dict[str, Any]],
) -> tuple[list[str], list[str], list[str], list[str]]:
    ready: list[str] = []
    degraded: list[str] = []
    partial: list[str] = []
    not_computable: list[str] = []
    for group in continuity_groups:
        gid = str(group.get("group_id", ""))
        status = str(group.get("status", ""))
        if status == "READY":
            ready.append(gid)
        elif status == "DEGRADED":
            degraded.append(gid)
        elif status == "PARTIAL":
            partial.append(gid)
        else:
            not_computable.append(gid)
    return sorted(ready), sorted(degraded), sorted(partial), sorted(not_computable)


def build_temporal_continuity_binder_readiness_audit(
    *,
    repo_root: str | Path = ".",
    source_binder_contract_path: str = SOURCE_BINDER_CONTRACT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    contract_path = root / source_binder_contract_path
    contract_observed = contract_path.exists()
    contract_payload = _load_json_dict(contract_path)
    contract_usable = contract_payload is not None
    contract_hash = _sha256_file(contract_path) if contract_usable else "NOT_COMPUTABLE"

    if not contract_usable:
        readiness_status = "NOT_COMPUTABLE"
        recommended_next_lane = "P71_BINDER_CONTRACT_REGENERATION"
        recommended_next_lane_reason = (
            "P71 binder contract is missing or unreadable; regenerate before readiness audit."
        )
        source_binder_contract_status = "NOT_COMPUTABLE"
        continuity_group_statuses: list[dict[str, Any]] = []
        ready_groups: list[str] = []
        degraded_groups: list[str] = []
        partial_groups: list[str] = []
        not_computable_groups: list[str] = []
        degraded_inputs: list[str] = []
        missing_or_not_computable_inputs: list[str] = [source_binder_contract_path]
        semantic_overlap_flags: list[str] = []
        blockers: list[str] = [f"source_binder_contract_not_computable:{source_binder_contract_path}"]
        drift_flags: list[str] = ["SOURCE_BINDER_CONTRACT_NOT_COMPUTABLE"]
    else:
        source_binder_contract_status = str(
            contract_payload.get("binder_contract_status", "NOT_COMPUTABLE")
        )
        raw_groups = contract_payload.get("continuity_groups", [])
        if not isinstance(raw_groups, list):
            raw_groups = []
        continuity_group_statuses = sorted(
            (
                json.loads(
                    json.dumps(g, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                )
                for g in raw_groups
                if isinstance(g, dict)
            ),
            key=lambda g: str(g.get("group_id", "")),
        )

        ready_groups, degraded_groups, partial_groups, not_computable_groups = _partition_groups(
            continuity_group_statuses
        )

        degraded_inputs = _as_sorted_str_list(contract_payload.get("degraded_inputs"))
        missing_or_not_computable_inputs = _as_sorted_str_list(
            contract_payload.get("missing_or_not_computable_inputs")
        )
        semantic_overlap_flags = _as_sorted_str_list(
            contract_payload.get("semantic_overlap_flags")
        )
        blockers = _as_sorted_str_list(contract_payload.get("blockers"))
        drift_flags = _as_sorted_str_list(contract_payload.get("drift_flags"))

        if source_binder_contract_status in ("NOT_COMPUTABLE",):
            readiness_status = "NOT_COMPUTABLE"
            recommended_next_lane = "P71_BINDER_CONTRACT_REPAIR"
            recommended_next_lane_reason = (
                "P71 binder contract status is NOT_COMPUTABLE; repair required before readiness audit."
            )
        elif source_binder_contract_status == "BLOCKED":
            readiness_status = "BLOCKED"
            recommended_next_lane = "P71_BINDER_CONTRACT_REPAIR"
            recommended_next_lane_reason = (
                "P71 binder contract status is BLOCKED; repair required before readiness audit."
            )
        elif source_binder_contract_status == "CONTRACT_READY_WITH_DEGRADED_EVIDENCE":
            readiness_status = "READY_WITH_DEGRADED_EVIDENCE"
            if partial_groups or not_computable_groups:
                recommended_next_lane = "P73_TEMPORAL_CONTINUITY_EVIDENCE_INDEX"
                recommended_next_lane_reason = (
                    "P71 binder contract is CONTRACT_READY_WITH_DEGRADED_EVIDENCE and one or more "
                    "continuity groups are PARTIAL or NOT_COMPUTABLE; evidence indexing required "
                    "before spine implementation."
                )
            else:
                recommended_next_lane = "P73_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"
                recommended_next_lane_reason = (
                    "P71 binder contract is CONTRACT_READY_WITH_DEGRADED_EVIDENCE and all groups "
                    "are READY or DEGRADED; degraded evidence repair planning is the safe next step."
                )
        elif source_binder_contract_status == "CONTRACT_READY":
            if not degraded_groups and not partial_groups and not not_computable_groups:
                readiness_status = "READY"
                recommended_next_lane = "P73_TEMPORAL_CONTINUITY_SPINE_IMPLEMENTATION_PLANNING"
                recommended_next_lane_reason = (
                    "P71 binder contract is CONTRACT_READY and all continuity groups are READY; "
                    "safe to proceed to spine implementation planning."
                )
            else:
                readiness_status = "READY_WITH_DEGRADED_EVIDENCE"
                if partial_groups or not_computable_groups:
                    recommended_next_lane = "P73_TEMPORAL_CONTINUITY_EVIDENCE_INDEX"
                    recommended_next_lane_reason = (
                        "P71 binder contract is CONTRACT_READY but one or more continuity groups "
                        "are PARTIAL or NOT_COMPUTABLE; evidence indexing recommended."
                    )
                else:
                    recommended_next_lane = "P73_TEMPORAL_CONTINUITY_DEGRADED_EVIDENCE_REPAIR_PLAN"
                    recommended_next_lane_reason = (
                        "P71 binder contract is CONTRACT_READY but some groups are DEGRADED; "
                        "degraded evidence repair planning recommended."
                    )
        else:
            readiness_status = "NOT_COMPUTABLE"
            recommended_next_lane = "P71_BINDER_CONTRACT_REPAIR"
            recommended_next_lane_reason = (
                f"P71 binder contract status is unrecognised ({source_binder_contract_status!r}); "
                "repair required."
            )

    packet_base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "canonical_status": "ADVISORY_ONLY",
        "audit_only": True,
        "projection_only": True,
        "production_activation": False,
        "canon_promotion": False,
        "forecast_influence": False,
        "scheduler_mutation": False,
        "runtime_authority": False,
        "repair_authority": False,
        "spine_implementation_authority": False,
        "source_binder_contract_path": source_binder_contract_path,
        "source_binder_contract_observed": contract_observed,
        "source_binder_contract_hash": contract_hash,
        "readiness_status": readiness_status,
        "source_binder_contract_status": source_binder_contract_status,
        "continuity_group_statuses": continuity_group_statuses,
        "ready_groups": ready_groups,
        "degraded_groups": degraded_groups,
        "partial_groups": partial_groups,
        "not_computable_groups": not_computable_groups,
        "degraded_inputs": degraded_inputs,
        "missing_or_not_computable_inputs": missing_or_not_computable_inputs,
        "semantic_overlap_flags": semantic_overlap_flags,
        "blockers": blockers,
        "drift_flags": drift_flags,
        "denied_authority": sorted(_DENIED_AUTHORITY),
        "recommended_next_lane": recommended_next_lane,
        "recommended_next_lane_reason": recommended_next_lane_reason,
    }
    packet = {
        **packet_base,
        "packet_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def write_temporal_continuity_binder_readiness_audit(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
