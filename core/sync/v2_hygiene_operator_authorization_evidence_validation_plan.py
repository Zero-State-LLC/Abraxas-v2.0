from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_dry_run import (
    DRY_RUN_JSON_PATH as SOURCE_DRY_RUN_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygieneOperatorAuthorizationEvidenceValidationPlan.v1"
VALIDATION_PLAN_ID = "v2_hygiene_operator_authorization_evidence_validation_plan_001"
VALIDATION_PLAN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_plan_001.latest.json"
)
VALIDATION_PLAN_MD_PATH = VALIDATION_PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN_READY"


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


def _mapping_list(value: Any) -> list[dict[str, Any]]:
    return [dict(item) for item in value if isinstance(item, Mapping)] if isinstance(value, list) else []


def _bundle_group_checks(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for idx, group in enumerate(groups, start=1):
        missing_fields = _string_list(group.get("missing_fields"))
        field_count = group.get("field_count")
        checks.append(
            {
                "check_id": f"group_{idx:03d}",
                "group_id": str(group.get("group_id", NOT_COMPUTABLE)),
                "attested": group.get("attested"),
                "field_count": field_count,
                "missing_field_count": len(missing_fields),
                "passed": (
                    group.get("attested") is False
                    and isinstance(field_count, int)
                    and field_count == len(missing_fields)
                    and bool(missing_fields)
                ),
            }
        )
    return checks


def _invariant_checks(
    packet: Mapping[str, Any],
    readiness_summary: Mapping[str, Any],
) -> list[dict[str, Any]]:
    checks = [
        ("packet_simulated_only", packet.get("simulated_only"), True),
        ("packet_operator_input_required", packet.get("operator_input_required"), True),
        (
            "packet_operator_attestations_present",
            packet.get("operator_attestations_present"),
            False,
        ),
        (
            "packet_operator_evidence_bundle_created",
            packet.get("operator_evidence_bundle_created"),
            False,
        ),
        ("packet_authorization_record_created", packet.get("authorization_record_created"), False),
        (
            "packet_authorization_record_creation_authorized",
            packet.get("authorization_record_creation_authorized"),
            False,
        ),
        ("packet_implementation_authorized", packet.get("implementation_authorized"), False),
        (
            "packet_v2_module_registration_authorized",
            packet.get("v2_module_registration_authorized"),
            False,
        ),
        ("packet_rune_registration_authorized", packet.get("rune_registration_authorized"), False),
        (
            "packet_projection_surface_mutation_authorized",
            packet.get("projection_surface_mutation_authorized"),
            False,
        ),
        ("packet_schema_mutation_authorized", packet.get("schema_mutation_authorized"), False),
        ("packet_execution_authority", packet.get("execution_authority"), False),
        (
            "packet_valid_for_authorization_record",
            packet.get("valid_for_authorization_record"),
            False,
        ),
        ("packet_valid_for_implementation", packet.get("valid_for_implementation"), False),
        ("packet_valid_for_execution", packet.get("valid_for_execution"), False),
        ("packet_recommended_next_patch", packet.get("recommended_next_patch"), NOT_COMPUTABLE),
        ("summary_simulated_only", readiness_summary.get("simulated_only"), True),
        (
            "summary_operator_input_required",
            readiness_summary.get("operator_input_required"),
            True,
        ),
        ("summary_groups_ready", readiness_summary.get("groups_ready"), 0),
        (
            "summary_evidence_bundle_complete",
            readiness_summary.get("evidence_bundle_complete"),
            False,
        ),
        (
            "summary_valid_for_authorization_record",
            readiness_summary.get("valid_for_authorization_record"),
            False,
        ),
    ]
    return [
        {
            "check_id": check_id,
            "observed": observed,
            "expected": expected,
            "passed": observed == expected,
        }
        for check_id, observed, expected in checks
    ]


def _authority_lock_checks(locks: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": f"authority_lock_{key}",
            "lock_name": key,
            "observed": value,
            "expected": False,
            "passed": value is False,
        }
        for key, value in sorted(locks.items())
    ]


def build_v2_hygiene_operator_authorization_evidence_validation_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_DRY_RUN_JSON
    dry_run = _read_json(source_path)
    source_observed = dry_run is not None
    dry_run = dry_run or {}

    source_status = str(dry_run.get("status", NOT_COMPUTABLE))
    source_ready = (
        dry_run.get("schema_version")
        == "V2HygieneOperatorAuthorizationEvidenceDryRun.v1"
        and source_status == EXPECTED_SOURCE_STATUS
    )
    readiness_summary = dict(dry_run.get("readiness_summary", {}))
    simulated_bundle = _mapping_list(dry_run.get("simulated_evidence_bundle"))
    authority_locks = dict(dry_run.get("authority_locks", {}))

    bundle_group_checks = _bundle_group_checks(simulated_bundle)
    invariant_checks = _invariant_checks(dry_run, readiness_summary)
    authority_lock_checks = _authority_lock_checks(authority_locks)
    validation_checks = [
        {
            "check_id": "source_dry_run_file_hash_present",
            "passed": _sha256(source_path) != NOT_COMPUTABLE,
        },
        {
            "check_id": "source_dry_run_packet_hash_present",
            "passed": dry_run.get("dry_run_hash") != NOT_COMPUTABLE,
        },
        {
            "check_id": "simulated_evidence_bundle_present",
            "passed": bool(simulated_bundle),
        },
        {
            "check_id": "evaluation_blockers_present",
            "passed": bool(dry_run.get("evaluation_blockers")),
        },
        {
            "check_id": "authority_locks_present",
            "passed": bool(authority_locks),
        },
    ]

    validation_blockers = sorted(
        {
            *(["source_dry_run_missing_or_not_ready"] if not source_ready else []),
            *(["simulated_evidence_bundle_missing"] if not simulated_bundle else []),
            *(check["check_id"] for check in bundle_group_checks if not check["passed"]),
            *(check["check_id"] for check in invariant_checks if not check["passed"]),
            *(check["check_id"] for check in authority_lock_checks if not check["passed"]),
            *(check["check_id"] for check in validation_checks if not check["passed"]),
        }
    )

    if not source_observed:
        status = "NOT_COMPUTABLE"
        blockers = [
            "source_dry_run_missing_or_unreadable",
            f"source_path:{SOURCE_DRY_RUN_JSON}",
        ]
    elif not source_ready:
        status = "BLOCKED_BY_V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_DRY_RUN"
        blockers = [f"source_dry_run_status:{source_status}"]
    elif validation_blockers:
        status = "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_BLOCKED_BY_DRY_RUN"
        blockers = validation_blockers
    else:
        status = "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_PLAN_READY"
        blockers = []

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "validation_plan_id": VALIDATION_PLAN_ID,
        "validation_plan_hash": "",
        "source_dry_run_path": str(SOURCE_DRY_RUN_JSON),
        "source_dry_run_observed": source_observed,
        "source_dry_run_ready": source_ready,
        "source_dry_run_file_hash": _sha256(source_path),
        "source_dry_run_packet_hash": str(dry_run.get("dry_run_hash", NOT_COMPUTABLE)),
        "source_dry_run_status": source_status,
        "source_review_artifacts": [
            str(item) for item in dry_run.get("source_review_artifacts", [])
        ],
        "bundle_group_checks": bundle_group_checks,
        "invariant_checks": invariant_checks,
        "authority_lock_checks": authority_lock_checks,
        "validation_checks": validation_checks,
        "source_readiness_summary": readiness_summary,
        "validation_blockers": validation_blockers,
        "blockers": blockers,
        "validation_plan_only": True,
        "simulated_only": True,
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
            "validate the simulated v2 hygiene operator authorization evidence dry run "
            "as fail-closed evidence only; do not create evidence, attestations, "
            "authorization records, implementation patches, writeback, or execution"
        ),
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": authority_locks,
    }
    packet_without_hash = dict(packet)
    packet_without_hash.pop("validation_plan_hash")
    packet["validation_plan_hash"] = canonical_hash(packet_without_hash)
    return packet


def render_v2_hygiene_operator_authorization_evidence_validation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Operator Authorization Evidence Validation Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_dry_run_ready`: `{packet['source_dry_run_ready']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `valid_for_authorization_record`: `{packet['valid_for_authorization_record']}`",
        f"- `valid_for_execution`: `{packet['valid_for_execution']}`",
        "",
        "## Bundle Group Checks",
        "",
    ]
    for check in packet["bundle_group_checks"]:
        lines.append(f"- `{check['group_id']}`: passed=`{check['passed']}`")
    lines.extend(["", "## Validation Blockers", ""])
    blockers = packet["validation_blockers"]
    if blockers:
        for item in blockers:
            lines.append(f"- `{item}`")
    else:
        lines.append("- `NONE`")
    return lines


def write_v2_hygiene_operator_authorization_evidence_validation_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = root if out_root is None else Path(out_root)
    packet = build_v2_hygiene_operator_authorization_evidence_validation_plan(root)
    write_canonical_json(target_root / VALIDATION_PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / VALIDATION_PLAN_MD_PATH,
        render_v2_hygiene_operator_authorization_evidence_validation_plan_markdown(
            packet
        ),
    )
    return packet
