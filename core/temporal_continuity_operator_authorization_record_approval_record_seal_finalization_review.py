from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = (
    "TemporalContinuityOperatorAuthorizationRecordApprovalRecordSealFinalizationReview.v1"
)

SOURCE_FINALIZATION_EXECUTION_PATH = (
    "out/temporal_continuity_operator_authorization_record_approval_record_seal_finalization_execution/latest.json"
)

_SOURCE_REQUIRED_STATUS = (
    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION_SIMULATED_COMPLETE"
)

_AUTHORITY_LOCK_FIELDS: tuple[str, ...] = (
    "approval_granted",
    "approval_record_sealed",
    "authorization_granted",
    "finalization_authorized",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "actual_finalization_executed",
    "production_activation",
)

_ADVISORY_TRUE_FIELDS: tuple[str, ...] = (
    "advisory_only",
    "projection_only",
    "simulated_finalization_only",
)

_SIMULATED_FINALIZATION_SENTINEL_FIELDS: tuple[str, ...] = (
    "simulated_finalization_id",
    "simulated_finalization_hash",
    "simulated_finalization_token",
    "simulated_finalization_signature",
    "simulated_finalization_completed_at",
)

_SIMULATED_FINALIZATION_AUTHORITY_FIELDS: tuple[str, ...] = (
    "approval_granted",
    "approval_record_sealed",
    "authorization_granted",
    "finalization_authorized",
    "execution_authority",
    "token_minting_allowed",
    "valid_for_execution",
    "actual_finalization_executed",
)

_FINALIZATION_REVIEW_CHECKLIST: tuple[dict[str, Any], ...] = (
    {
        "item_id": "finalization_simulation_advisory_confirmed",
        "description": (
            "All finalization simulation steps confirmed advisory-only; "
            "no real seal execution occurred."
        ),
        "review_only": True,
    },
    {
        "item_id": "finalization_provenance_chain_intact",
        "description": (
            "Provenance chain P96\u2192P101 hashes present and non-NOT_COMPUTABLE."
        ),
        "review_only": True,
    },
    {
        "item_id": "sentinel_strings_confirmed",
        "description": (
            "All simulated finalization record string fields contain SIMULATED marker; "
            "no real identifiers substituted."
        ),
        "review_only": True,
    },
    {
        "item_id": "authority_locks_all_false_confirmed",
        "description": (
            "All authority lock fields confirmed false across P102 source "
            "and simulated finalization record."
        ),
        "review_only": True,
    },
    {
        "item_id": "finalization_not_executed_confirmed",
        "description": (
            "actual_finalization_executed: false and finalization_authorized: false "
            "confirmed throughout chain."
        ),
        "review_only": True,
    },
)


def _load_json_dict(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _file_sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except (FileNotFoundError, OSError):
        return "NOT_COMPUTABLE"


def _finalize(packet_base: dict[str, Any]) -> dict[str, Any]:
    packet = {
        **packet_base,
        "approval_record_seal_finalization_review_hash": canonical_hash(packet_base),
    }
    return json.loads(json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _echo_check_list(source: list[Any]) -> list[dict[str, Any]]:
    result = []
    for item in source:
        if isinstance(item, dict):
            result.append({
                "check_id": str(item.get("check_id", "")),
                "passed": item.get("passed") is True,
            })
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


def _cross_lane_authority_posture(source: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for field in sorted(_AUTHORITY_LOCK_FIELDS):
        val = source.get(field)
        entries.append({"field": field, "value": val, "posture_ok": val is False})
    for field in sorted(_ADVISORY_TRUE_FIELDS):
        val = source.get(field)
        entries.append({"field": field, "value": val, "posture_ok": val is True})
    return entries


def _simulated_finalization_review(sim: dict[str, Any]) -> dict[str, Any]:
    authority_fields_clear = all(
        sim.get(f) is False for f in _SIMULATED_FINALIZATION_AUTHORITY_FIELDS
    )
    sentinel_fields_ok = all(
        isinstance(sim.get(f), str) and "SIMULATED" in sim.get(f, "")
        for f in _SIMULATED_FINALIZATION_SENTINEL_FIELDS
    )
    simulated_only_set = sim.get("simulated_only") is True
    actual_not_executed = sim.get("actual_finalization_executed") is False
    finalization_not_authorized = sim.get("finalization_authorized") is False
    review_passed = (
        authority_fields_clear
        and sentinel_fields_ok
        and simulated_only_set
        and actual_not_executed
        and finalization_not_authorized
    )
    return {
        "authority_fields_all_false": authority_fields_clear,
        "sentinel_strings_contain_simulated_marker": sentinel_fields_ok,
        "simulated_only_flag_set": simulated_only_set,
        "actual_finalization_executed_is_false": actual_not_executed,
        "finalization_authorized_is_false": finalization_not_authorized,
        "review_passed": review_passed,
    }


def _finalization_provenance_review(chain: dict[str, Any]) -> list[dict[str, Any]]:
    def _hash_ok(val: Any) -> bool:
        return isinstance(val, str) and val not in ("", "NOT_COMPUTABLE", "NOT_PROVIDED")

    return [
        {
            "check_id": "finalization_provenance_autonomous_approval_is_false",
            "passed": chain.get("autonomous_approval") is False,
        },
        {
            "check_id": "finalization_provenance_p96_hash_present",
            "passed": _hash_ok(chain.get("p96_seal_operator_decision_hash")),
        },
        {
            "check_id": "finalization_provenance_p100_hash_present",
            "passed": _hash_ok(chain.get("p100_authorization_record_hash")),
        },
        {
            "check_id": "finalization_provenance_p101_hash_present",
            "passed": _hash_ok(chain.get("p101_finalization_plan_hash")),
        },
        {
            "check_id": "finalization_provenance_operator_id_present",
            "passed": _hash_ok(chain.get("operator_id")),
        },
        {
            "check_id": "finalization_provenance_decision_value_present",
            "passed": _hash_ok(chain.get("decision_value")),
        },
    ]


def build_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review(
    *,
    repo_root: str | Path = ".",
    source_finalization_execution_path: str = SOURCE_FINALIZATION_EXECUTION_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / source_finalization_execution_path
    source_observed = source_path.exists()
    source_payload = _load_json_dict(source_path)

    source_hash = "NOT_COMPUTABLE"
    source_status = "NOT_COMPUTABLE"
    finalization_review_status = "NOT_COMPUTABLE"
    recommended_next_lane = (
        "P102_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION"
    )
    review_passed = False
    review_blockers: list[str] = []
    blockers: list[str] = []

    finalization_chain_review: list[dict[str, Any]] = []
    finalization_authority_invariant_review: list[dict[str, Any]] = []
    simulated_finalization_review_result: dict[str, Any] = {}
    finalization_sentinel_check_review: dict[str, Any] = {}
    finalization_provenance_review_result: list[dict[str, Any]] = []
    finalization_check_summary: dict[str, int] = {"total": 0, "passed": 0, "failed": 0}
    cross_lane_authority_posture: list[dict[str, Any]] = []
    finalization_review_checklist = list(_FINALIZATION_REVIEW_CHECKLIST)

    p102_finalization_execution_hash_anchor = "NOT_COMPUTABLE"
    p102_simulated_finalization_only_anchor = False
    p102_actual_finalization_executed_anchor = True
    p102_finalization_recorded_anchor = False

    if source_payload is None:
        review_blockers = [
            "source_finalization_execution_missing_or_unreadable",
            f"source_path:{source_finalization_execution_path}",
        ]
        blockers = sorted(review_blockers)
    else:
        source_hash = _file_sha256(source_path)
        source_status = str(
            source_payload.get("finalization_execution_status", "NOT_COMPUTABLE")
        )
        p102_finalization_execution_hash_anchor = str(
            source_payload.get("approval_record_seal_finalization_execution_hash", "NOT_COMPUTABLE")
        )
        p102_simulated_finalization_only_anchor = (
            source_payload.get("simulated_finalization_only") is True
        )
        p102_actual_finalization_executed_anchor = (
            source_payload.get("actual_finalization_executed") is not False
        )
        p102_finalization_recorded_anchor = (
            source_payload.get("finalization_recorded") is True
        )

        source_finalization_recorded = source_payload.get("finalization_recorded") is True

        if source_status != _SOURCE_REQUIRED_STATUS or not source_finalization_recorded:
            finalization_review_status = (
                "BLOCKED_BY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_EXECUTION"
            )
            if source_status != _SOURCE_REQUIRED_STATUS:
                review_blockers.append(f"source_finalization_execution_status:{source_status}")
            if not source_finalization_recorded:
                review_blockers.append(
                    f"finalization_recorded_must_be_true:found_{source_payload.get('finalization_recorded')!r}"
                )
            blockers = sorted(review_blockers)
        else:
            finalization_chain_review = _echo_check_list(
                source_payload.get("finalization_chain_verification", [])
            )
            finalization_authority_invariant_review = _echo_check_list(
                source_payload.get("finalization_authority_invariant_checks", [])
            )

            sim_dict = source_payload.get("simulated_finalization_record", {})
            simulated_finalization_review_result = _simulated_finalization_review(
                sim_dict if isinstance(sim_dict, dict) else {}
            )

            sentinel_check = source_payload.get("simulated_sentinel_check", {})
            finalization_sentinel_check_review = {
                "source_check_passed": sentinel_check.get("check_passed") is True,
                "sentinel_strings_all_contain_simulated_marker": (
                    sentinel_check.get("sentinel_strings_all_contain_simulated_marker") is True
                ),
                "actual_finalization_executed_is_false": (
                    sentinel_check.get("actual_finalization_executed_is_false") is True
                ),
                "approval_record_sealed_is_false": (
                    sentinel_check.get("approval_record_sealed_is_false") is True
                ),
                "finalization_authorized_is_false": (
                    sentinel_check.get("finalization_authorized_is_false") is True
                ),
            }

            prov_chain = source_payload.get("finalization_provenance_chain", {})
            finalization_provenance_review_result = _finalization_provenance_review(
                prov_chain if isinstance(prov_chain, dict) else {}
            )

            finalization_check_summary = _check_summary([
                finalization_chain_review,
                finalization_authority_invariant_review,
                finalization_provenance_review_result,
            ])

            cross_lane_authority_posture = _cross_lane_authority_posture(source_payload)
            posture_failures = [
                e["field"] for e in cross_lane_authority_posture if not e.get("posture_ok")
            ]

            sim_review_failures: list[str] = []
            if not simulated_finalization_review_result.get("authority_fields_all_false"):
                sim_review_failures.append(
                    "simulated_finalization_record_authority_fields_not_all_false"
                )
            if not simulated_finalization_review_result.get("sentinel_strings_contain_simulated_marker"):
                sim_review_failures.append(
                    "simulated_finalization_record_sentinel_strings_missing_simulated_marker"
                )
            if not simulated_finalization_review_result.get("simulated_only_flag_set"):
                sim_review_failures.append(
                    "simulated_finalization_record_simulated_only_not_set"
                )
            if not simulated_finalization_review_result.get("actual_finalization_executed_is_false"):
                sim_review_failures.append(
                    "simulated_finalization_record_actual_finalization_executed_not_false"
                )
            if not simulated_finalization_review_result.get("finalization_authorized_is_false"):
                sim_review_failures.append(
                    "simulated_finalization_record_finalization_authorized_not_false"
                )

            all_failures = sorted(
                [f"cross_lane_authority_posture_failed:{f}" for f in posture_failures]
                + sim_review_failures
                + [f"finalization_chain_check_failed:{c['check_id']}" for c in finalization_chain_review if not c.get("passed")]
                + [f"finalization_authority_invariant_failed:{c['check_id']}" for c in finalization_authority_invariant_review if not c.get("passed")]
                + [f"finalization_provenance_check_failed:{c['check_id']}" for c in finalization_provenance_review_result if not c.get("passed")]
            )

            if all_failures:
                finalization_review_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW_FAILED"
                )
                review_blockers = all_failures
                blockers = sorted(review_blockers)
            else:
                finalization_review_status = (
                    "OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_REVIEW_READY"
                )
                recommended_next_lane = (
                    "P104_TEMPORAL_CONTINUITY_OPERATOR_AUTHORIZATION_RECORD_APPROVAL_RECORD_SEAL_FINALIZATION_DECISION"
                )
                review_passed = True

    packet_base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "approval_record_seal_finalization_review_id": (
            "temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review_001"
        ),
        "source_finalization_execution_path": source_finalization_execution_path,
        "source_finalization_execution_hash": source_hash,
        "source_finalization_execution_status": source_status,
        "source_finalization_execution_observed": source_observed,
        "finalization_review_status": finalization_review_status,
        "review_passed": review_passed,
        "review_blockers": sorted(review_blockers),
        "blockers": sorted(blockers),
        "finalization_chain_review": finalization_chain_review,
        "finalization_authority_invariant_review": finalization_authority_invariant_review,
        "simulated_finalization_review": simulated_finalization_review_result,
        "finalization_sentinel_check_review": finalization_sentinel_check_review,
        "finalization_provenance_review": finalization_provenance_review_result,
        "finalization_check_summary": finalization_check_summary,
        "cross_lane_authority_posture": cross_lane_authority_posture,
        "finalization_review_checklist": finalization_review_checklist,
        "p102_finalization_execution_hash_anchor": p102_finalization_execution_hash_anchor,
        "p102_simulated_finalization_only_anchor": p102_simulated_finalization_only_anchor,
        "p102_actual_finalization_executed_anchor": p102_actual_finalization_executed_anchor,
        "p102_finalization_recorded_anchor": p102_finalization_recorded_anchor,
        "recommended_next_lane": recommended_next_lane,
        "review_only": True,
        "finalization_review_only": True,
        "approval_record_seal_finalization_review_only": True,
        "advisory_only": True,
        "projection_only": True,
        "operator_approval_required": True,
        "approval_record_sealed": False,
        "approval_record_created": False,
        "approval_granted": False,
        "authorization_granted": False,
        "finalization_authorized": False,
        "actual_finalization_executed": False,
        "execution_authority": False,
        "authorization_authority": False,
        "plan_creation_authority": False,
        "mutation_allowed": False,
        "forecast_authority": False,
        "canon_mutation_allowed": False,
        "runtime_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "production_activation": False,
        "canon_promotion": False,
        "scheduler_mutation": False,
        "baseline_mutation": False,
        "runtime_mutation": False,
        "governance_authority_mutation": False,
    }
    return _finalize(packet_base)


def write_temporal_continuity_operator_authorization_record_approval_record_seal_finalization_review(
    path: str | Path, packet: dict[str, Any]
) -> None:
    write_canonical_json(path, packet)
