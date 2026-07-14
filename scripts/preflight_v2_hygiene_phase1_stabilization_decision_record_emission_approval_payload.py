from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_EMISSION_APPROVAL_PAYLOAD_PATH = Path(
    "operator_input/"
    "v2_hygiene_phase1_stabilization_decision_record_emission_approval_payload_001.json"
)
SOURCE_EMISSION_AUTHORIZATION_GATE_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_emission_authorization_gate_001.latest.json"
)
SOURCE_EMISSION_PLAN_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_stabilization_decision_record_emission_plan_001.latest.json"
)
PLACEHOLDER_PREFIX = "REPLACE_WITH_"
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")

REQUIRED_GROUPS = (
    "operator_identity",
    "emission_scope_acknowledgement",
    "emission_disposition",
    "authority_boundary_acknowledgement",
    "terminal_output_controls",
)
REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "operator_identity": (
        "operator_id",
        "operator_reviewed_at_source_observed",
        "operator_approval_hash",
    ),
    "emission_scope_acknowledgement": (
        "source_emission_authorization_gate_path",
        "source_emission_authorization_gate_hash",
        "source_emission_plan_path",
        "source_emission_plan_hash",
        "terminal_emission_hold_acknowledged",
    ),
    "emission_disposition": (
        "approved_record_id",
        "approved_record_output_path",
        "selected_emission_disposition",
        "decision_record_emission_now_allowed",
        "decision_record_auto_emission_allowed",
        "separate_record_finalization_lane_required",
    ),
    "authority_boundary_acknowledgement": (
        "no_decision_record_auto_emission",
        "no_hygiene_implementation_authority",
        "no_execution_authority",
        "no_runtime_canon_queue_scheduler_mutation",
        "no_notion_or_github_writeback",
        "no_registration_or_promotion",
        "no_activation",
        "no_auto_continuation",
    ),
    "terminal_output_controls": (
        "downstream_lane_disposition",
        "future_record_finalization_gate_required",
        "future_record_emission_allowed_by_this_payload",
        "rollback_or_supersession_policy",
    ),
}
TRUE_FIELDS = {
    "terminal_emission_hold_acknowledged",
    "separate_record_finalization_lane_required",
    "no_decision_record_auto_emission",
    "no_hygiene_implementation_authority",
    "no_execution_authority",
    "no_runtime_canon_queue_scheduler_mutation",
    "no_notion_or_github_writeback",
    "no_registration_or_promotion",
    "no_activation",
    "no_auto_continuation",
    "future_record_finalization_gate_required",
}
FALSE_FIELDS = {
    "decision_record_emission_now_allowed",
    "decision_record_auto_emission_allowed",
    "future_record_emission_allowed_by_this_payload",
}
EXPECTED_LITERAL_FIELDS = {
    "source_emission_authorization_gate_path": (
        SOURCE_EMISSION_AUTHORIZATION_GATE_PATH.as_posix()
    ),
    "source_emission_plan_path": SOURCE_EMISSION_PLAN_PATH.as_posix(),
    "approved_record_id": "v2_hygiene_phase1_stabilization_decision_record_001",
    "approved_record_output_path": (
        "out/operator_review/"
        "v2_hygiene_phase1_stabilization_decision_record_001.latest.json"
    ),
    "selected_emission_disposition": (
        "APPROVE_DECISION_RECORD_EMISSION_FOR_SEPARATE_GOVERNED_"
        "RECORD_FINALIZATION_LANE"
    ),
    "downstream_lane_disposition": (
        "NOT_COMPUTABLE_UNTIL_GOVERNED_DECISION_RECORD_EMISSION_FINALIZATION"
    ),
    "rollback_or_supersession_policy": "fresh governed operator decision required",
}
AUTHORITY_EXPANDING_FIELDS = (
    "decision_record_created",
    "decision_record_creation_authorized",
    "decision_record_emitted",
    "decision_record_materialized",
    "decision_record_emission_authorized",
    "authorization_record_created",
    "authorization_record_creation_authorized",
    "evidence_bundle_created",
    "evidence_bundle_creation_authorized",
    "operator_attestation_created",
    "implementation_authorized",
    "hygiene_code_creation_authorized",
    "schema_file_creation_authorized",
    "v2_module_registration_authorized",
    "rune_registration_authorized",
    "strict_mode_enablement_authorized",
    "notion_writeback_allowed",
    "github_writeback_allowed",
    "runtime_mutation",
    "queue_mutation",
    "scheduler_mutation",
    "canon_mutation",
    "schema_mutation",
    "execution_authority",
    "valid_for_execution",
    "valid_for_implementation",
    "valid_for_decision_record_creation",
    "valid_for_decision_record_emission",
    "safe_to_auto_continue",
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _source_hashes(repo_root: Path) -> dict[str, str | None]:
    gate = _read_json(repo_root / SOURCE_EMISSION_AUTHORIZATION_GATE_PATH) or {}
    plan = _read_json(repo_root / SOURCE_EMISSION_PLAN_PATH) or {}
    gate_hash = gate.get("gate_hash")
    plan_hash = plan.get("plan_hash")
    return {
        "source_emission_authorization_gate_hash": (
            gate_hash if isinstance(gate_hash, str) and gate_hash else None
        ),
        "source_emission_plan_hash": (
            plan_hash if isinstance(plan_hash, str) and plan_hash else None
        ),
    }


def _is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(PLACEHOLDER_PREFIX)


def _is_sha256_digest(value: Any) -> bool:
    return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None


def _placeholder_blockers(value: Any, prefix: str) -> list[str]:
    blockers: list[str] = []
    if _is_placeholder(value):
        blockers.append(f"{prefix}_placeholder_not_allowed")
    if isinstance(value, Mapping):
        for key, item in value.items():
            blockers.extend(_placeholder_blockers(item, f"{prefix}.{key}"))
    return blockers


def _authority_expansion_blockers(payload: Mapping[str, Any]) -> list[str]:
    blockers = [
        f"payload_authority_expanding_field:{field}"
        for field in AUTHORITY_EXPANDING_FIELDS
        if payload.get(field) is True
    ]
    locks = payload.get("authority_locks")
    if isinstance(locks, Mapping):
        blockers.extend(
            f"payload_authority_lock_true:{field}"
            for field, value in sorted(locks.items())
            if value is True
        )
    return blockers


def _field_blockers(
    group_id: str,
    group: Mapping[str, Any],
    *,
    expected_hashes: Mapping[str, str | None],
    template_mode: bool,
) -> list[str]:
    blockers: list[str] = []
    for field in REQUIRED_FIELDS[group_id]:
        if field not in group:
            blockers.append(f"{group_id}.{field}_missing")
            continue
        value = group[field]
        if field in TRUE_FIELDS and value is not True:
            blockers.append(f"{group_id}.{field}_must_be_true")
        if field in FALSE_FIELDS and value is not False:
            blockers.append(f"{group_id}.{field}_must_be_false")
        if field in EXPECTED_LITERAL_FIELDS and value != EXPECTED_LITERAL_FIELDS[field]:
            blockers.append(f"{group_id}.{field}_unexpected_value")
        if field in expected_hashes:
            expected = expected_hashes[field]
            if template_mode and _is_placeholder(value):
                pass
            elif expected is None:
                blockers.append(f"{group_id}.{field}_source_not_observed")
            elif value != expected:
                blockers.append(f"{group_id}.{field}_mismatch")
        if field in {
            "operator_id",
            "operator_reviewed_at_source_observed",
            "operator_approval_hash",
        }:
            if not (isinstance(value, str) and value.strip()):
                blockers.append(f"{group_id}.{field}_blank")
            elif not template_mode and _is_placeholder(value):
                blockers.append(f"{group_id}.{field}_placeholder_not_allowed")
        if field == "operator_approval_hash":
            if template_mode and _is_placeholder(value):
                pass
            elif not _is_sha256_digest(value):
                blockers.append(f"{group_id}.{field}_must_be_sha256_digest")
    return blockers


def validate_payload(
    payload: Mapping[str, Any] | None,
    *,
    expected_hashes: Mapping[str, str | None],
    template_mode: bool = False,
) -> dict[str, Any]:
    if payload is None:
        return {
            "payload_observed": False,
            "template_mode": template_mode,
            "valid": False,
            "group_records": [],
            "authority_expansion_blockers": [],
            "validation_blockers": ["payload_missing_or_unreadable"],
        }

    group_records: list[dict[str, Any]] = []
    blockers: list[str] = []
    for group_id in REQUIRED_GROUPS:
        group = payload.get(group_id)
        observed = isinstance(group, Mapping)
        field_blockers = (
            _field_blockers(
                group_id,
                group,
                expected_hashes=expected_hashes,
                template_mode=template_mode,
            )
            if observed
            else [f"{group_id}_missing"]
        )
        blockers.extend(field_blockers)
        group_records.append(
            {
                "group_id": group_id,
                "group_observed": observed,
                "group_validated": observed and not field_blockers,
                "field_blockers": field_blockers,
            }
        )

    authority_blockers = _authority_expansion_blockers(payload)
    blockers.extend(authority_blockers)
    if not template_mode:
        blockers.extend(_placeholder_blockers(payload, "payload"))

    blockers = sorted(set(blockers))
    return {
        "payload_observed": True,
        "template_mode": template_mode,
        "valid": not blockers,
        "group_records": group_records,
        "authority_expansion_blockers": sorted(authority_blockers),
        "validation_blockers": blockers,
    }


def preflight_payload(
    payload_path: str | Path = DEFAULT_EMISSION_APPROVAL_PAYLOAD_PATH,
    *,
    repo_root: str | Path = ".",
    template_mode: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root)
    path = Path(payload_path)
    payload = _read_json(path if path.is_absolute() else root / path)
    result = validate_payload(
        payload,
        expected_hashes=_source_hashes(root),
        template_mode=template_mode,
    )
    return {
        "payload_path": path.as_posix(),
        "mode": "template" if template_mode else "real",
        **result,
    }


def render_preflight_lines(result: Mapping[str, Any]) -> list[str]:
    lines = [
        "# v2 hygiene Phase 1 stabilization decision-record emission approval preflight",
        f"payload_path: {result['payload_path']}",
        f"mode: {result['mode']}",
        f"payload_observed: {result['payload_observed']}",
        f"valid: {result['valid']}",
        "groups:",
    ]
    for record in result.get("group_records", []):
        if isinstance(record, Mapping):
            lines.append(
                "- "
                f"{record['group_id']}: observed={record['group_observed']}, "
                f"validated={record['group_validated']}, "
                f"blockers={len(record['field_blockers'])}"
            )
    lines.append("validation_blockers:")
    blockers = result.get("validation_blockers", [])
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- none")
    lines.append("authority_granted: False")
    lines.append("valid_for_execution: False")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight a v2 stabilization decision-record emission approval payload."
        )
    )
    parser.add_argument(
        "payload_path",
        nargs="?",
        default=DEFAULT_EMISSION_APPROVAL_PAYLOAD_PATH.as_posix(),
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Allow REPLACE_WITH_ placeholders for external fields.",
    )
    args = parser.parse_args()
    result = preflight_payload(args.payload_path, template_mode=args.template)
    print("\n".join(render_preflight_lines(result)))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
