from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealOperatorReview.v1"
SOURCE_APPROVAL_RECORD_SEAL_DRY_RUN_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_dry_run/latest.json"
)

_OPERATOR_REVIEW_CHECKLIST: tuple[dict[str, Any], ...] = (
    {
        "item_id": "seal_construction_advisory_confirmed",
        "description": (
            "All seal construction requirements confirmed advisory-only; "
            "no real record creation or sealing occurred in dry-run."
        ),
        "review_only": True,
    },
    {
        "item_id": "seal_provenance_chain_intact",
        "description": (
            "Provenance chain hash present in P93 (sourced from P92); "
            "P94 confirmed hash non-empty and non-NOT_COMPUTABLE."
        ),
        "review_only": True,
    },
    {
        "item_id": "seal_hash_canonical_confirmed",
        "description": (
            "Canonical JSON serialization with sorted keys and SHA-256 hashing "
            "confirmed in dry-run."
        ),
        "review_only": True,
    },
    {
        "item_id": "seal_blocker_requirements_satisfiable",
        "description": (
            "Fail-closed behavior confirmed: missing source yields NOT_COMPUTABLE, "
            "non-ready status yields BLOCKED, validation failure yields BLOCKED."
        ),
        "review_only": True,
    },
    {
        "item_id": "seal_authority_invariants_held",
        "description": (
            "All authority invariant checks in P94 passed; "
            "approval_granted, authorization_granted, execution_authority, "
            "token_minting_allowed, valid_for_execution all false across dry-run."
        ),
        "review_only": True,
    },
    {
        "item_id": "simulated_seal_sentinels_correct",
        "description": (
            "All simulated_seal_dry_run fields carry SIMULATED_ONLY markers; "
            "no real hash, token, or signature material present."
        ),
        "review_only": True,
    },
    {
        "item_id": "cross_lane_authority_posture_clean",
        "description": (
            "P94 output carries no elevated authority lock; "
            "all output lock fields false."
        ),
        "review_only": True,
    },
    {
        "item_id": "operator_approval_required_confirmed",
        "description": (
            "operator_approval_required: true confirmed in P94; "
            "any real sealing requires explicit operator decision outside this lane chain."
        ),
        "review_only": True,
    },
)

_AUTHORITY_LOCK_FIELDS: tuple[str, ...] = (
    "approval_granted",
    "approval_record_created",
    "approval_record_sealed",
    "authorization_authority",
    "authorization_granted",
    "authorization_record_creation_authority",
    "execution_authority",
    "mutation_allowed",
    "token_minting_allowed",
    "valid_for_execution",
)

_ADVISORY_TRUE_FIELDS: tuple[str, ...] = (
    "advisory_only",
    "projection_only",
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {**packet_base, "approval_record_seal_operator_review_hash": canonical_hash(packet_base)}
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _echo_check_list(source: list[Any]) -> list[dict[str, Any]]:
    result = []
    for item in source:
        if isinstance(item, dict):
            result.append({"check_id": str(item.get("check_id", "")), "passed": item.get("passed") is True})
    return result


def _check_summary(lists: list[list[dict[str, Any]]]) -> dict[str, int]:
    total = passed = failed = 0
    for lst in lists:
        for item in lst:
            total += 1
            if item.get("passed") is True:
                passed += 1
            else:
                failed += 1
    return {"total": total, "passed": passed, "failed": failed}


def _cross_lane_authority_posture(source_payload: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for field in sorted(_AUTHORITY_LOCK_FIELDS):
        val = source_payload.get(field)
        entries.append({"field": field, "value": val, "posture_ok": val is False})
    for field in sorted(_ADVISORY_TRUE_FIELDS):
        val = source_payload.get(field)
        entries.append({"field": field, "value": val, "posture_ok": val is True})
    return entries


def _simulated_seal_review(sim: dict[str, Any]) -> dict[str, Any]:
    authority_fields_clear = all(
        sim.get(f) is False
        for f in (
            "approval_granted",
            "approval_record_created",
            "approval_record_sealed",
            "authorization_granted",
            "execution_authority",
            "token_minting_allowed",
            "valid_for_execution",
        )
    )
    sentinel_fields_ok = all(
        isinstance(sim.get(f), str) and "SIMULATED" in sim.get(f, "")
        for f in (
            "simulated_seal_hash",
            "simulated_seal_token",
            "simulated_seal_signature",
            "simulated_seal_created_at",
            "approval_record_seal_dry_run_id",
        )
    )
    simulated_only_set = sim.get("simulated_only") is True
    return {
        "authority_fields_all_false": authority_fields_clear,
        "sentinel_strings_contain_simulated_marker": sentinel_fields_ok,
        "simulated_only_flag_set": simulated_only_set,
        "review_passed": authority_fields_clear and sentinel_fields_ok and simulated_only_set,
    }


def build_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
    *,
    repo_root: str | Path = ".",
    source_approval_record_seal_dry_run_path: str = SOURCE_APPROVAL_RECORD_SEAL_DRY_RUN_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_approval_record_seal_dry_run_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    approval_record_seal_operator_review_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P94_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
    )
    review_passed = False
    review_blockers: list[str] = []
    blockers: list[str] = []

    seal_construction_review: list[dict[str, Any]] = []
    seal_provenance_review: list[dict[str, Any]] = []
    seal_hash_review: list[dict[str, Any]] = []
    seal_blocker_review: list[dict[str, Any]] = []
    seal_authority_invariant_review: list[dict[str, Any]] = []
    dry_run_check_summary: dict[str, int] = {"total": 0, "passed": 0, "failed": 0}
    cross_lane_authority_posture: list[dict[str, Any]] = []
    simulated_seal_review: dict[str, Any] = {}
    operator_review_checklist: list[dict[str, Any]] = list(_OPERATOR_REVIEW_CHECKLIST)

    if source_payload is None:
        review_blockers = [
            "source_approval_record_seal_dry_run_missing_or_unreadable",
            f"source_path:{source_approval_record_seal_dry_run_path}",
        ]
        blockers = sorted(review_blockers)
    else:
        source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_status = str(source_payload.get("approval_record_seal_dry_run_status", "NOT_COMPUTABLE"))
        source_dry_run_passed = source_payload.get("dry_run_passed") is True

        seal_construction_review = _echo_check_list(
            source_payload.get("seal_construction_dry_run_results", [])
        )
        seal_provenance_review = _echo_check_list(
            source_payload.get("seal_provenance_dry_run_results", [])
        )
        seal_hash_review = _echo_check_list(
            source_payload.get("seal_hash_dry_run_results", [])
        )
        seal_blocker_review = _echo_check_list(
            source_payload.get("seal_blocker_dry_run_results", [])
        )
        seal_authority_invariant_review = _echo_check_list(
            source_payload.get("seal_authority_invariant_dry_run_results", [])
        )
        dry_run_check_summary = _check_summary([
            seal_construction_review,
            seal_provenance_review,
            seal_hash_review,
            seal_blocker_review,
            seal_authority_invariant_review,
        ])

        cross_lane_authority_posture = _cross_lane_authority_posture(source_payload)
        posture_failures = [
            e["field"] for e in cross_lane_authority_posture if not e.get("posture_ok")
        ]

        sim_dict = source_payload.get("simulated_seal_dry_run", {})
        simulated_seal_review = _simulated_seal_review(sim_dict if isinstance(sim_dict, dict) else {})
        sim_failures: list[str] = []
        if not simulated_seal_review.get("authority_fields_all_false"):
            sim_failures.append("simulated_seal_dry_run_authority_fields_not_all_false")
        if not simulated_seal_review.get("sentinel_strings_contain_simulated_marker"):
            sim_failures.append("simulated_seal_dry_run_sentinel_strings_missing_simulated_marker")
        if not simulated_seal_review.get("simulated_only_flag_set"):
            sim_failures.append("simulated_seal_dry_run_simulated_only_not_set")

        if source_status != "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN_READY":
            approval_record_seal_operator_review_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
            )
            review_blockers = [f"source_approval_record_seal_dry_run_status:{source_status}"]
            blockers = sorted(review_blockers)
        elif not source_dry_run_passed:
            approval_record_seal_operator_review_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_DRY_RUN"
            )
            review_blockers = ["source_dry_run_passed:false"]
            blockers = sorted(review_blockers)
        elif posture_failures or sim_failures:
            approval_record_seal_operator_review_status = "APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_FAILED"
            review_blockers = sorted(
                [f"cross_lane_authority_posture_failed:{f}" for f in posture_failures]
                + sim_failures
            )
            blockers = sorted(review_blockers)
        else:
            approval_record_seal_operator_review_status = (
                "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_REVIEW_READY"
            )
            recommended_next_lane = (
                "P96_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_OPERATOR_DECISION"
            )
            review_passed = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_operator_review_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_operator_review_001"
        ),
        "source_approval_record_seal_dry_run_path": source_approval_record_seal_dry_run_path,
        "source_approval_record_seal_dry_run_hash": source_hash,
        "source_approval_record_seal_dry_run_status": source_status,
        "approval_record_seal_operator_review_status": approval_record_seal_operator_review_status,
        "dry_run_check_summary": dry_run_check_summary,
        "seal_construction_review": seal_construction_review,
        "seal_provenance_review": seal_provenance_review,
        "seal_hash_review": seal_hash_review,
        "seal_blocker_review": seal_blocker_review,
        "seal_authority_invariant_review": seal_authority_invariant_review,
        "cross_lane_authority_posture": cross_lane_authority_posture,
        "simulated_seal_review": simulated_seal_review,
        "operator_review_checklist": operator_review_checklist,
        "review_passed": review_passed,
        "review_blockers": sorted(review_blockers),
        "blockers": sorted(blockers),
        "recommended_next_lane": recommended_next_lane,
        "source_approval_record_seal_dry_run_observed": source_observed,
        "advisory_only": True,
        "projection_only": True,
        "approval_record_seal_operator_review_only": True,
        "operator_review_only": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "execution_authority": False,
        "authorization_authority": False,
        "authorization_record_creation_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "operator_approval_required": True,
        "valid_for_execution": False,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_operator_review(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
