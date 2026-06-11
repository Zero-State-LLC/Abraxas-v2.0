from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OracleSignalShadowIntakeOperatorReviewRequest.v1"
RECEIPT_JSON_PATH = Path("out/oracle/oracle_signal_intake_receipt.latest.json")
REQUEST_JSON_PATH = Path("out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.json")
REQUEST_MD_PATH = Path("out/operator_review/oracle_signal_shadow_intake_operator_review_request_001.latest.md")

DECISION_OPTIONS = [
    "HOLD_SHADOW_RECEIPT",
    "APPROVE_REVIEW_ONLY_COMPLETION",
    "REQUEST_ADDITIONAL_EVIDENCE",
    "REJECT_SHADOW_BOUNDARY",
]


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


def build_oracle_signal_shadow_intake_operator_review_request(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    receipt = _read_json(root / RECEIPT_JSON_PATH)
    receipt_ready = (
        receipt.get("schema_version") == "OracleSignalIntakeReceipt.v1"
        and receipt.get("receipt_status") == "ORACLE_SIGNAL_INTAKE_RECEIPT_EMITTED_ADVISORY_ONLY"
        and receipt.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and receipt.get("execution_authority") is False
        and receipt.get("runtime_mutation") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_REQUEST_HELD"
        if receipt_ready
        else "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_REQUEST_BLOCKED",
        "request_id": "oracle_signal_shadow_intake_operator_review_request_001",
        "request_hash": "",
        "command": "BUILD_ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_REQUEST_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": "SHADOW_INTAKE_RECEIPT_REVIEW_REQUIRED",
        "decision_question": "Should the Oracle Signal shadow intake receipt be accepted as review-only evidence, held for more evidence, or rejected before any future governed lane exists?",
        "target_surface": "Oracle Signal Intake Boundary",
        "target_pipeline_id": "oracle_signal",
        "source_receipt_path": str(RECEIPT_JSON_PATH),
        "source_receipt_hash": str(receipt.get("receipt_hash", "NOT_COMPUTABLE")),
        "source_receipt_status": str(receipt.get("receipt_status", "NOT_COMPUTABLE")),
        "source_receipt_authority": str(receipt.get("authority", "NOT_COMPUTABLE")),
        "source_candidate_signal_count": int(receipt.get("candidate_signal_count", 0)),
        "source_input_envelope_ref_count": int(receipt.get("input_envelope_ref_count", 0)),
        "receipt_ready_for_review": receipt_ready,
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
        "decision_options": DECISION_OPTIONS,
        "recommended_decision": "HOLD_SHADOW_RECEIPT",
        "recommended_next_action": "hold for governed operator review of the shadow receipt before any further Oracle Signal implementation, route binding, queue mutation, or runtime integration",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "required_operator_review_items": [
            "confirm candidate signals remain SOURCE_URI_ONLY_NO_FETCH",
            "confirm input envelope refs remain REFERENCE_ONLY_NOT_BOUND",
            "confirm no ingest runner behavior changed",
            "confirm no pipeline or route binding was introduced",
            "confirm no queue, runtime, scheduler, forecast, canon, token, writeback, or execution authority was granted",
        ],
        "blocked_actions": [
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
    }
    packet["request_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "request_hash"})
    return packet


def render_oracle_signal_shadow_intake_operator_review_request_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Oracle Signal Shadow Intake Operator Review Request",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `source_receipt_status`: `{packet['source_receipt_status']}`",
        f"- `recommended_decision`: `{packet['recommended_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        "",
        "## Decision Options",
        "",
    ]
    for item in packet["decision_options"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Review Items", ""])
    for item in packet["required_operator_review_items"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_oracle_signal_shadow_intake_operator_review_request(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_shadow_intake_operator_review_request(root)
    write_canonical_json(target_root / REQUEST_JSON_PATH, packet)
    _write_markdown(
        target_root / REQUEST_MD_PATH,
        render_oracle_signal_shadow_intake_operator_review_request_markdown(packet),
    )
    return packet
