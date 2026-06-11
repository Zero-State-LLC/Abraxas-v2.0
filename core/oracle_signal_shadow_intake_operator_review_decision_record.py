from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OracleSignalShadowIntakeOperatorReviewDecisionRecord.v1"
REQUEST_JSON_PATH = Path("out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json")
DECISION_JSON_PATH = Path("out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json")
DECISION_MD_PATH = Path("out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.md")


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
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "token_minting": False,
    }


def build_oracle_signal_shadow_intake_operator_review_decision_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_JSON_PATH)
    request_ready = (
        request.get("schema_version") == "OracleSignalShadowIntakeOperatorReviewRequest.v1"
        and request.get("status") == "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_REQUEST_HELD"
        and "APPROVE_REVIEW_ONLY_COMPLETION" in request.get("decision_options", [])
        and request.get("implementation_authorized") is False
        and request.get("execution_authority") is False
        and request.get("valid_for_execution") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_COMPLETION_APPROVED"
        if request_ready
        else "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_COMPLETION_BLOCKED",
        "decision_record_id": "oracle_signal_shadow_intake_operator_review_decision_record_001",
        "decision_record_hash": "",
        "command": "BUILD_ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_DECISION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": "SHADOW_INTAKE_RECEIPT_REVIEW_ONLY",
        "selected_decision": "APPROVE_REVIEW_ONLY_COMPLETION" if request_ready else "NOT_COMPUTABLE",
        "operator_id": "thread_operator",
        "operator_name": "appliedalchemylabs",
        "operator_role": "governed_operator",
        "operator_instruction_observed": "merge and approve all work",
        "decision_timestamp_utc": "2026-06-11T00:00:00Z",
        "review_only_completion_approved": request_ready,
        "receipt_accepted_as_review_only_evidence": request_ready,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "pipeline_or_route_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "authority_locks": _authority_locks(),
        "decision_outcome_summary": (
            "Oracle Signal shadow intake receipt is accepted as review-only evidence; no implementation, "
            "queue, route, runtime, scheduler, forecast, canon, token, writeback, or execution authority is granted."
        ),
        "recommended_next_action": (
            "maintain shadow receipt as reviewed evidence until a separate future governed lane explicitly "
            "authorizes any additional planning or implementation work"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
        "allowed_follow_on_actions": [
            "MAINTAIN_SHADOW_RECEIPT_AS_REVIEWED_EVIDENCE",
            "KEEP_ORACLE_SIGNAL_UNIMPLEMENTED",
            "MAINTAIN_GLOBAL_INGEST_HOLD",
        ],
        "blocked_actions": list(request.get("blocked_actions", [])),
        "reviewed_request_id": str(request.get("request_id", "NOT_COMPUTABLE")),
        "reviewed_request_hash": str(request.get("request_hash", "NOT_COMPUTABLE")),
        "reviewed_request_path": str(REQUEST_JSON_PATH),
        "reviewed_source_receipt_path": str(request.get("source_receipt_path", "NOT_COMPUTABLE")),
        "reviewed_source_receipt_hash": str(request.get("source_receipt_hash", "NOT_COMPUTABLE")),
        "required_operator_review_items_confirmed": list(request.get("required_operator_review_items", [])),
    }
    packet["decision_record_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "decision_record_hash"}
    )
    return packet


def render_oracle_signal_shadow_intake_operator_review_decision_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Oracle Signal Shadow Intake Operator Review Decision Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `review_only_completion_approved`: `{packet['review_only_completion_approved']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Decision Boundary",
        "",
        str(packet["decision_outcome_summary"]),
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


def write_oracle_signal_shadow_intake_operator_review_decision_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_shadow_intake_operator_review_decision_record(root)
    write_canonical_json(target_root / DECISION_JSON_PATH, packet)
    _write_markdown(
        target_root / DECISION_MD_PATH,
        render_oracle_signal_shadow_intake_operator_review_decision_record_markdown(packet),
    )
    return packet
