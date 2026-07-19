from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.sync.v2_hygiene_phase1_stabilization_operator_attestation_intake_gate import (  # noqa: E402
    AUTHORITY_EXPANDING_FIELDS,
    DEFAULT_ATTESTATION_PAYLOAD_PATH,
    EXPECTED_LITERAL_FIELDS,
    FALSE_FIELDS,
    REQUIRED_FIELDS,
    REQUIRED_GROUPS,
    SOURCE_DRY_RUN_JSON_PATH,
    TRUE_FIELDS,
)

PLACEHOLDER_PREFIX = "REPLACE_WITH_"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _source_plan_hash(repo_root: Path) -> str | None:
    payload = _read_json(repo_root / SOURCE_DRY_RUN_JSON_PATH)
    if not payload:
        return None
    value = payload.get("source_plan_hash")
    return value if isinstance(value, str) and value else None


def _is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value.startswith(PLACEHOLDER_PREFIX)


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
    expected_source_plan_hash: str | None,
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
        if field == "source_strategy_plan_hash":
            if template_mode and _is_placeholder(value):
                pass
            elif expected_source_plan_hash is None:
                blockers.append(f"{group_id}.source_strategy_plan_hash_source_not_observed")
            elif value != expected_source_plan_hash:
                blockers.append(f"{group_id}.source_strategy_plan_hash_mismatch")
        if field in {
            "operator_id",
            "operator_reviewed_at_source_observed",
            "operator_attestation_hash",
        }:
            if not (isinstance(value, str) and value.strip()):
                blockers.append(f"{group_id}.{field}_blank")
            elif not template_mode and _is_placeholder(value):
                blockers.append(f"{group_id}.{field}_placeholder_not_allowed")
    return blockers


def validate_payload(
    payload: Mapping[str, Any] | None,
    *,
    expected_source_plan_hash: str | None,
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
                expected_source_plan_hash=expected_source_plan_hash,
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
    payload_path: str | Path = DEFAULT_ATTESTATION_PAYLOAD_PATH,
    *,
    repo_root: str | Path = ".",
    template_mode: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root)
    path = Path(payload_path)
    payload = _read_json(path if path.is_absolute() else root / path)
    result = validate_payload(
        payload,
        expected_source_plan_hash=_source_plan_hash(root),
        template_mode=template_mode,
    )
    return {
        "payload_path": path.as_posix(),
        "mode": "template" if template_mode else "real",
        **result,
    }


def render_preflight_lines(result: Mapping[str, Any]) -> list[str]:
    lines = [
        "# v2 hygiene Phase 1 stabilization operator payload preflight",
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
        description="Preflight a v2 stabilization operator attestation payload."
    )
    parser.add_argument(
        "payload_path",
        nargs="?",
        default=DEFAULT_ATTESTATION_PAYLOAD_PATH.as_posix(),
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
