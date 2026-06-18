from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "OracleSignalPhysicalImplementationAuthorizationReview.v1"
REVIEW_JSON_PATH = Path("out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.json")
REVIEW_MD_PATH = Path("out/operator_review/oracle_signal_physical_implementation_authorization_review_001.latest.md")

PREP_PATH = Path("out/operator_review/global_pipeline_repo_execution_prep_001.latest.json")
DECISION_RECORD_PATH = Path("out/operator_review/global_ingest_operator_decision_record_001.latest.json")
IMPLEMENTATION_SPEC_PATH = Path("out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json")
GAP_BACKLOG_PATH = Path("out/operator_review/global_pipeline_gap_backlog_001.latest.json")


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


def build_oracle_signal_physical_implementation_authorization_review(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    prep = _read_json(root / PREP_PATH)
    decision = _read_json(root / DECISION_RECORD_PATH)
    spec = _read_json(root / IMPLEMENTATION_SPEC_PATH)
    backlog = _read_json(root / GAP_BACKLOG_PATH)

    oracle_backlog_item = next(
        (item for item in backlog.get("backlog_items", []) if item.get("pipeline_id") == "oracle_signal"),
        {},
    )
    decision_status = decision.get("status")
    oracle_module_observed = (root / "core/oracle_signal.py").exists()
    oracle_missing_paths = list(oracle_backlog_item.get("missing_paths", []))
    source_ready = (
        prep.get("status") == "REPO_EXECUTION_PREP_PACKET_BLOCKED"
        and bool(
            {
                "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REQUIRED",
                "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_HELD",
            }
            & set(prep.get("not_computable_reasons", []))
        )
        and decision_status
        in {
            "GLOBAL_INGEST_OPERATOR_DECISION_RECORDED",
            "GLOBAL_INGEST_OPERATOR_DECISION_CONSUMED_BY_SEPARATE_IMPLEMENTATION_SPEC_PLAN",
        }
        and decision.get("selected_decision") == "APPROVE_SEPARATE_IMPLEMENTATION_SPEC"
        and decision.get("implementation_authorized") is False
        and decision.get("execution_authority") is False
        and spec.get("status")
        in {
            "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_READY",
            "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY",
        }
        and spec.get("implementation_authorized") is False
        and spec.get("execution_authority") is False
        and oracle_missing_paths == []
        and oracle_module_observed
        and oracle_backlog_item.get("implementation_allowed") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_HELD_FOR_OPERATOR"
            if source_ready
            else "ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_BLOCKED"
        ),
        "review_id": "oracle_signal_physical_implementation_authorization_review_001",
        "review_hash": "",
        "command": "BUILD_ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_001",
        "target_pipeline_id": "oracle_signal",
        "target_display_name": "Oracle Signal Layer Pipeline",
        "decision_scope": "PHYSICAL_IMPLEMENTATION_AUTHORIZATION_REVIEW_ONLY",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "review_requested": source_ready,
        "selected_decision": "HOLD_FOR_OPERATOR" if source_ready else "NOT_COMPUTABLE",
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
        "safe_to_prepare_implementation_pr": False,
        "authority_locks": _authority_locks(),
        "source_paths": {
            "repo_execution_prep": PREP_PATH.as_posix(),
            "global_ingest_operator_decision_record": DECISION_RECORD_PATH.as_posix(),
            "global_ingest_adapter_spine_implementation_spec": IMPLEMENTATION_SPEC_PATH.as_posix(),
            "global_pipeline_gap_backlog": GAP_BACKLOG_PATH.as_posix(),
        },
        "source_hashes": {
            "repo_execution_prep": str(prep.get("prep_packet_id", "NOT_COMPUTABLE")),
            "global_ingest_operator_decision_record": str(decision.get("decision_record_hash", "NOT_COMPUTABLE")),
            "global_ingest_adapter_spine_implementation_spec": str(spec.get("spec_hash", "NOT_COMPUTABLE")),
            "global_pipeline_gap_backlog": str(backlog.get("backlog_id", "NOT_COMPUTABLE")),
        },
        "review_findings": [
            {
                "finding_id": "ORACLE-PHYS-001",
                "status": "HELD",
                "summary": (
                    "core/oracle_signal.py is observed as advisory-only shadow processing; "
                    "execution authority remains denied without explicit operator authorization."
                    if oracle_module_observed
                    else "core/oracle_signal.py remains absent and must not be created without a future explicit authorization record."
                ),
            },
            {
                "finding_id": "ORACLE-PHYS-002",
                "status": "HELD",
                "summary": "Existing decision/spec evidence authorizes planning and additive shadow contracts only, not physical implementation.",
            },
            {
                "finding_id": "ORACLE-PHYS-003",
                "status": "DENIED",
                "summary": "Execution, runtime, scheduler, route, queue, canon, forecast, writeback, and token authority remain denied.",
            },
        ],
        "allowed_follow_on_actions": [
            "MAINTAIN_ORACLE_SIGNAL_PHYSICAL_IMPLEMENTATION_HOLD",
            "COLLECT_EXPLICIT_PHYSICAL_IMPLEMENTATION_OPERATOR_AUTHORIZATION",
            "PREPARE_PHYSICAL_IMPLEMENTATION_AUTHORIZATION_RECORD_PLAN",
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
        "recommended_next_action": (
            "observe advisory core/oracle_signal.py receipts while collecting explicit physical "
            "implementation operator authorization before any runner behavior mutation or execution grant"
            if oracle_module_observed
            else "collect explicit physical implementation operator authorization before any core/oracle_signal.py "
            "creation or runner behavior mutation"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
    }
    packet["review_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "review_hash"})
    return packet


def render_oracle_signal_physical_implementation_authorization_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Oracle Signal Physical Implementation Authorization Review",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `review_requested`: `{packet['review_requested']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Findings",
    ]
    for finding in packet["review_findings"]:
        lines.append(f"- `{finding['finding_id']}` `{finding['status']}`: {finding['summary']}")
    lines.extend(["", "## Allowed Follow-On Actions", ""])
    for item in packet["allowed_follow_on_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_oracle_signal_physical_implementation_authorization_review(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_oracle_signal_physical_implementation_authorization_review(root)
    write_canonical_json(target_root / REVIEW_JSON_PATH, packet)
    _write_markdown(
        target_root / REVIEW_MD_PATH,
        render_oracle_signal_physical_implementation_authorization_review_markdown(packet),
    )
    return packet
