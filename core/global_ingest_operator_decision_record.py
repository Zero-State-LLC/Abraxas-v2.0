from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionRecord.v1"
TEMPLATE_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_template_001.latest.json")
REQUEST_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.json")
RECORD_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_001.latest.json")
RECORD_MD_PATH = Path("out/operator_review/global_ingest_operator_decision_record_001.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_global_ingest_operator_decision_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    template = _read_json(root / TEMPLATE_JSON_PATH)
    request = _read_json(root / REQUEST_JSON_PATH)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "GLOBAL_INGEST_OPERATOR_DECISION_RECORDED",
        "decision_record_id": "global_ingest_operator_decision_record_001",
        "decision_record_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": "IMPLEMENTATION_SPEC_DECISION_REQUIRED",
        "selected_decision": "APPROVE_SEPARATE_IMPLEMENTATION_SPEC",
        "decision_outcome_summary": "Separate governed implementation spec authoring is approved; Oracle Signal implementation, ingest runner mutation, route/runtime integration, and execution remain denied.",
        "decision_rationale": "Operator approved the backlog recommendation to prepare a separate governed implementation specification before any Global Ingest Adapter Spine implementation work.",
        "operator_id": "thread_operator",
        "operator_name": "appliedalchemylabs",
        "operator_role": "governed_operator",
        "decision_timestamp_utc": "2026-06-11T00:00:00Z",
        "decision_scope_acknowledged": True,
        "separate_implementation_spec_required": True,
        "advisory_only_acknowledged": True,
        "non_authoritative_acknowledged": True,
        "execution_authority_denied_acknowledged": True,
        "runtime_mutation_denied_acknowledged": True,
        "canon_mutation_denied_acknowledged": True,
        "forecast_weight_denied_acknowledged": True,
        "implementation_spec_authoring_approved": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": True,
        "allowed_follow_on_actions": [
            "AUTHOR_SEPARATE_IMPLEMENTATION_SPEC",
            "OPEN_SEPARATE_SPEC_PR",
            "MAINTAIN_GLOBAL_INGEST_HOLD",
        ],
        "disallowed_follow_on_actions": list(template["disallowed_follow_on_actions"]),
        "blocked_actions": [
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
        ],
        "recommended_next_action": "author a separate governed Global Ingest Adapter Spine implementation specification before any code or runner behavior changes",
        "recommended_next_patch": "GLOBAL_INGEST_ADAPTER_SPINE_SEPARATE_IMPLEMENTATION_SPEC_PLAN",
        "target_pipeline_id": "oracle_signal",
        "target_display_name": str(request["target_display_name"]),
        "reviewed_request_id": str(request["request_id"]),
        "reviewed_request_hash": str(template["source_hashes"]["global_ingest_operator_decision_request"]),
        "reviewed_doctrine_review_hash": str(template["source_hashes"]["global_pipeline_doctrine_proof"]),
        "reviewed_gap_backlog_hash": str(template["source_hashes"]["global_pipeline_gap_backlog"]),
        "reviewed_notion_decision_backlog_hash": str(template["source_hashes"]["notion_operator_decision_backlog"]),
        "reviewed_notion_spec_completion_queue_hash": str(template["source_hashes"]["notion_spec_completion_queue"]),
        "source_template_path": str(TEMPLATE_JSON_PATH),
        "source_template_hash": str(template["template_hash"]),
        "source_request_path": str(REQUEST_JSON_PATH),
        "source_hashes": {
            "global_ingest_operator_decision_record_template": str(template["template_hash"]),
            "global_ingest_operator_decision_request": str(request["request_id"]),
            **{str(key): str(value) for key, value in template["source_hashes"].items()},
        },
    }
    packet["decision_record_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "decision_record_hash"}
    )
    return packet


def render_global_ingest_operator_decision_record_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `implementation_spec_authoring_approved`: `{packet['implementation_spec_authoring_approved']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Decision Boundary",
        "",
        packet["decision_outcome_summary"],
        "",
        "## Allowed Follow-On Actions",
        "",
    ]
    for item in packet["allowed_follow_on_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(target_root / RECORD_MD_PATH, render_global_ingest_operator_decision_record_markdown(packet))
    return packet
