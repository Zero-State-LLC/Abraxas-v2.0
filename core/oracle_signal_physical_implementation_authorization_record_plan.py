from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OracleSignalPhysicalImplementationAuthorizationRecordPlan.v1"
PLAN_JSON_PATH = Path("out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.json")
PLAN_MD_PATH = Path("out/operator_review/oracle_signal_physical_implementation_authorization_record_plan_001.latest.md")

SOURCE_REVIEW_PATH = Path("out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.json")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_weight": False,
        "github_writeback": False,
        "implementation_authority": False,
        "ingest_runner_mutation": False,
        "notion_writeback": False,
        "pipeline_or_route_mutation": False,
        "queue_mutation": False,
        "record_creation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting": False,
    }


def build_oracle_signal_physical_implementation_authorization_record_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    review = _read_json(root / SOURCE_REVIEW_PATH)
    review_ready = (
        review.get("status") == "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR"
        and review.get("selected_decision") == "HOLD_FOR_OPERATOR"
        and review.get("implementation_authorized") is False
        and review.get("execution_authority") is False
        and review.get("valid_for_execution") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_READY"
            if review_ready
            else "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_BLOCKED"
        ),
        "plan_id": "oracle_signal_physical_implementation_authorization_record_plan_001",
        "plan_hash": "",
        "command": "BUILD_ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN_001",
        "target_pipeline_id": "oracle_signal",
        "decision_scope": "PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLANNING_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "source_review_path": SOURCE_REVIEW_PATH.as_posix(),
        "source_review_hash": str(review.get("review_hash", "NOT_COMPUTABLE")),
        "record_plan_ready": review_ready,
        "record_creation_authorized": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "ingest_runner_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_create_authorization_record": False,
        "safe_to_prepare_implementation_pr": False,
        "authority_locks": _authority_locks(),
        "required_operator_authorization_fields": [
            "operator_id",
            "operator_role",
            "decision_timestamp_utc",
            "selected_decision",
            "target_pipeline_id",
            "source_review_hash",
            "implementation_scope",
            "authority_boundaries_acknowledged",
            "execution_authority_denied_acknowledged",
            "runtime_route_queue_scheduler_denied_acknowledged",
            "rollback_and_fail_closed_acknowledged",
        ],
        "allowed_follow_on_actions": [
            "COLLECT_EXPLICIT_PHYSICAL_IMPLEMENTATION_OPERATOR_AUTHORIZATION",
            "PREPARE_AUTHORIZATION_RECORD_DRY_RUN_AFTER_OPERATOR_EVIDENCE",
            "MAINTAIN_ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_HOLD",
        ],
        "blocked_actions": [
            "CREATE_AUTHORIZATION_RECORD_WITHOUT_OPERATOR_EVIDENCE",
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "QUEUE_MUTATION",
            "FORECAST_WEIGHTING",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "TOKEN_MINTING",
        ],
        "recommended_next_action": (
            "collect explicit operator authorization evidence before any authorization record dry run, "
            "record creation, or physical implementation PR"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
    }
    packet["plan_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "plan_hash"})
    return packet


def render_oracle_signal_physical_implementation_authorization_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Oracle Signal Physical Implementation Authorization Record Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `record_plan_ready`: `{packet['record_plan_ready']}`",
        f"- `record_creation_authorized`: `{packet['record_creation_authorized']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Required Operator Authorization Fields",
    ]
    for field in packet["required_operator_authorization_fields"]:
        lines.append(f"- `{field}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_oracle_signal_physical_implementation_authorization_record_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_physical_implementation_authorization_record_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_oracle_signal_physical_implementation_authorization_record_plan_markdown(packet),
    )
    return packet
