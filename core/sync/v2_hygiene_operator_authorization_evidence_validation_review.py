from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_validation_plan import (
    VALIDATION_PLAN_JSON_PATH as SOURCE_VALIDATION_PLAN_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygieneOperatorAuthorizationEvidenceValidationReview.v1"
REVIEW_ID = "v2_hygiene_operator_authorization_evidence_validation_review_001"
REVIEW_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_001.latest.json"
)
REVIEW_MD_PATH = REVIEW_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_READY"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _checks_passed(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    return all(isinstance(item, Mapping) and item.get("passed") is True for item in value)


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _source_ready(packet: Mapping[str, Any]) -> bool:
    return (
        packet.get("schema_version")
        == "V2HygieneOperatorAuthorizationEvidenceValidationPlan.v1"
        and packet.get("status") == EXPECTED_SOURCE_STATUS
        and packet.get("source_dry_run_ready") is True
        and packet.get("validation_plan_only") is True
        and packet.get("simulated_only") is True
        and packet.get("operator_input_required") is True
        and packet.get("operator_attestations_present") is False
        and packet.get("operator_evidence_bundle_created") is False
        and packet.get("authorization_record_created") is False
        and packet.get("authorization_record_creation_authorized") is False
        and packet.get("implementation_authorized") is False
        and packet.get("v2_module_registration_authorized") is False
        and packet.get("rune_registration_authorized") is False
        and packet.get("projection_surface_mutation_authorized") is False
        and packet.get("schema_mutation_authorized") is False
        and packet.get("execution_authority") is False
        and packet.get("valid_for_authorization_record") is False
        and packet.get("valid_for_implementation") is False
        and packet.get("valid_for_execution") is False
        and packet.get("recommended_next_patch") == NOT_COMPUTABLE
        and packet.get("recommended_next_lane") == NOT_COMPUTABLE
        and packet.get("recommended_next_state") == "hold"
        and packet.get("notion_writeback_allowed") is False
        and packet.get("github_writeback_allowed") is False
        and packet.get("validation_blockers") == []
        and _checks_passed(packet.get("bundle_group_checks"))
        and _checks_passed(packet.get("invariant_checks"))
        and _checks_passed(packet.get("authority_lock_checks"))
        and _checks_passed(packet.get("validation_checks"))
        and _locks_all_false(packet.get("authority_locks"))
    )


def build_v2_hygiene_operator_authorization_evidence_validation_review(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_VALIDATION_PLAN_JSON
    validation_plan = _read_json(source_path)
    source_observed = validation_plan is not None
    validation_plan = validation_plan or {}
    source_ready = source_observed and _source_ready(validation_plan)
    source_status = str(validation_plan.get("status", NOT_COMPUTABLE))
    source_validation_blockers = _string_list(
        validation_plan.get("validation_blockers")
    )
    source_blockers = _string_list(validation_plan.get("blockers"))

    if not source_observed:
        status = NOT_COMPUTABLE
        source_readiness = "SOURCE_VALIDATION_PLAN_MISSING"
        review_findings = [
            {
                "finding_id": "source_validation_plan_missing",
                "finding_status": NOT_COMPUTABLE,
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source v2 hygiene operator authorization evidence validation plan "
            "is missing or unreadable"
        )
    elif not source_ready:
        status = (
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_BLOCKED"
        )
        source_readiness = "SOURCE_VALIDATION_PLAN_NOT_READY"
        review_findings = [
            {
                "finding_id": "source_validation_plan_not_ready",
                "finding_status": "BLOCKED",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source v2 hygiene operator authorization evidence validation plan "
            "is not ready for held operator review"
        )
    else:
        status = (
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_HELD_FOR_OPERATOR"
        )
        source_readiness = "SOURCE_VALIDATION_PLAN_READY"
        review_findings = [
            {
                "finding_id": "validation_plan_ready",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "external_operator_attestations_missing",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "evidence_bundle_creation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "authorization_record_creation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "implementation_and_execution_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ]
        terminal_hold_reason = (
            "the validation plan proves the simulated dry-run bundle and authority "
            "locks are fail-closed, but external operator attestations remain "
            "missing; this review cannot create evidence, create records, register "
            "modules or runes, authorize implementation, or continue automatically"
        )

    authority_locks = dict(validation_plan.get("authority_locks", {}))
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "review_id": REVIEW_ID,
        "review_hash": "",
        "source_validation_plan_path": str(SOURCE_VALIDATION_PLAN_JSON),
        "source_validation_plan_observed": source_observed,
        "source_validation_plan_ready": source_ready,
        "source_validation_plan_file_hash": _sha256(source_path),
        "source_validation_plan_packet_hash": str(
            validation_plan.get("validation_plan_hash", NOT_COMPUTABLE)
        ),
        "source_validation_plan_status": source_status,
        "source_readiness": source_readiness,
        "source_validation_blockers": source_validation_blockers,
        "source_blockers": source_blockers,
        "source_bundle_group_check_count": len(
            validation_plan.get("bundle_group_checks", [])
            if isinstance(validation_plan.get("bundle_group_checks"), list)
            else []
        ),
        "source_invariant_check_count": len(
            validation_plan.get("invariant_checks", [])
            if isinstance(validation_plan.get("invariant_checks"), list)
            else []
        ),
        "source_authority_lock_check_count": len(
            validation_plan.get("authority_lock_checks", [])
            if isinstance(validation_plan.get("authority_lock_checks"), list)
            else []
        ),
        "review_findings": review_findings,
        "selected_operator_decision": "HOLD_FOR_OPERATOR_REVIEW"
        if source_ready
        else NOT_COMPUTABLE,
        "selected_follow_on_action": "MAINTAIN_V2_HYGIENE_OPERATOR_AUTHORIZATION_HOLD"
        if source_ready
        else NOT_COMPUTABLE,
        "terminal_hold_reason": terminal_hold_reason,
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_evidence_bundle_created": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "recommended_next_action": (
            "collect explicit external operator attestations before any future "
            "authorization-record, implementation, registration, writeback, or "
            "execution lane"
        )
        if source_ready
        else "repair the source validation plan before operator review",
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": authority_locks,
    }
    packet_without_hash = dict(packet)
    packet_without_hash.pop("review_hash")
    packet["review_hash"] = canonical_hash(packet_without_hash)
    return packet


def render_v2_hygiene_operator_authorization_evidence_validation_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Operator Authorization Evidence Validation Review",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_validation_plan_ready`: `{packet['source_validation_plan_ready']}`",
        f"- `selected_operator_decision`: `{packet['selected_operator_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `valid_for_authorization_record`: `{packet['valid_for_authorization_record']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Review Findings",
        "",
    ]
    for finding in packet["review_findings"]:
        lines.append(
            f"- `{finding['finding_id']}`: `{finding['finding_status']}`"
        )
    lines.extend(
        [
            "",
            "## Terminal Hold",
            "",
            f"- `{packet['terminal_hold_reason']}`",
        ]
    )
    return lines


def write_v2_hygiene_operator_authorization_evidence_validation_review(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = root if out_root is None else Path(out_root)
    packet = build_v2_hygiene_operator_authorization_evidence_validation_review(root)
    write_canonical_json(target_root / REVIEW_JSON_PATH, packet)
    _write_markdown(
        target_root / REVIEW_MD_PATH,
        render_v2_hygiene_operator_authorization_evidence_validation_review_markdown(
            packet
        ),
    )
    return packet
