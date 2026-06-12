from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalPipelineDoctrineDashboardReviewRecord.v1"
RECORD_JSON_PATH = Path("out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.json")
RECORD_MD_PATH = Path("out/operator_review/global_pipeline_doctrine_dashboard_review_record_001.latest.md")

DOCTRINE_PROOF_PATH = Path("out/global_pipeline_doctrine_validation/latest.json")
DOCTRINE_REVIEW_PATH = Path("out/global_pipeline_doctrine_validation/operator_review_packet.latest.json")
DASHBOARD_PATH = Path("out/global_pipeline_aal_viz/dashboard_packet.latest.json")
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


def build_global_pipeline_doctrine_dashboard_review_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    doctrine = _read_json(root / DOCTRINE_PROOF_PATH)
    doctrine_review = _read_json(root / DOCTRINE_REVIEW_PATH)
    dashboard = _read_json(root / DASHBOARD_PATH)
    backlog = _read_json(root / GAP_BACKLOG_PATH)

    doctrine_ready = (
        doctrine.get("status") == "GLOBAL_PIPELINE_DOCTRINE_VALIDATION_PROOF_EMITTED"
        and doctrine.get("execution_authority") is False
        and doctrine.get("physical_repo_implementation_ready") is False
    )
    review_ready = (
        doctrine_review.get("status") == "GLOBAL_PIPELINE_DOCTRINE_VALIDATION_OPERATOR_REVIEW_PACKET_EMITTED"
        and doctrine_review.get("state") == "held"
        and doctrine_review.get("execution_authority") is False
    )
    dashboard_ready = (
        dashboard.get("status") == "GLOBAL_PIPELINE_AAL_VIZ_DASHBOARD_PACKET_EMITTED"
        and dashboard.get("recommended_next_state") == "review"
        and dashboard.get("execution_authority") is False
        and dashboard.get("physical_repo_implementation_ready") is False
    )
    backlog_ready = (
        backlog.get("status") == "GLOBAL_PIPELINE_GAP_BACKLOG_EMITTED"
        and backlog.get("execution_authority") is False
        and backlog.get("blocked_count") == 1
    )
    review_accepted = doctrine_ready and review_ready and dashboard_ready and backlog_ready

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "GLOBAL_PIPELINE_DOCTRINE_DASHBOARD_REVIEW_ACCEPTED"
            if review_accepted
            else "GLOBAL_PIPELINE_DOCTRINE_DASHBOARD_REVIEW_BLOCKED"
        ),
        "record_id": "global_pipeline_doctrine_dashboard_review_record_001",
        "record_hash": "",
        "command": "BUILD_GLOBAL_PIPELINE_DOCTRINE_DASHBOARD_REVIEW_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": "DOCTRINE_DASHBOARD_REVIEW_ONLY",
        "selected_decision": "ACCEPT_REVIEW_EVIDENCE_ONLY" if review_accepted else "NOT_COMPUTABLE",
        "operator_instruction_observed": "this seems redundant",
        "dashboard_review_accepted_as_reviewed_evidence": review_accepted,
        "doctrine_review_accepted_as_reviewed_evidence": review_accepted,
        "gap_backlog_accepted_as_reviewed_evidence": review_accepted,
        "source_doctrine_path": DOCTRINE_PROOF_PATH.as_posix(),
        "source_doctrine_hash": str(doctrine.get("proof_id", "NOT_COMPUTABLE")),
        "source_doctrine_review_path": DOCTRINE_REVIEW_PATH.as_posix(),
        "source_doctrine_review_hash": str(doctrine_review.get("review_packet_id", "NOT_COMPUTABLE")),
        "source_dashboard_path": DASHBOARD_PATH.as_posix(),
        "source_dashboard_hash": str(dashboard.get("dashboard_id", "NOT_COMPUTABLE")),
        "source_gap_backlog_path": GAP_BACKLOG_PATH.as_posix(),
        "source_gap_backlog_hash": str(backlog.get("backlog_id", "NOT_COMPUTABLE")),
        "observed_counts": {
            "missing_contract_count": doctrine.get("missing_contract_count"),
            "additive_shadow_contract_coverage_count": doctrine.get("additive_shadow_contract_coverage_count"),
            "missing_validation_count": doctrine.get("missing_validation_count"),
            "additive_shadow_validation_coverage_count": doctrine.get("additive_shadow_validation_coverage_count"),
            "gap_count": backlog.get("gap_count"),
            "blocked_count": backlog.get("blocked_count"),
            "deferred_count": backlog.get("deferred_count"),
        },
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
        "safe_to_prepare_planning_pr": False,
        "authority_locks": _authority_locks(),
        "decision_outcome_summary": (
            "Doctrine and dashboard evidence is accepted as reviewed evidence only; Oracle Signal physical "
            "implementation remains held for an explicit Global Ingest operator decision."
        ),
        "allowed_follow_on_actions": [
            "MAINTAIN_DOCTRINE_DASHBOARD_AS_REVIEWED_EVIDENCE",
            "REQUEST_GLOBAL_INGEST_OPERATOR_DECISION",
            "KEEP_ORACLE_SIGNAL_IMPLEMENTATION_HELD",
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
            "stop adding duplicate doctrine/dashboard review receipts; collect explicit Global Ingest operator "
            "decision evidence before any physical implementation path"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
    }
    packet["record_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "record_hash"})
    return packet


def render_global_pipeline_doctrine_dashboard_review_record_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# Global Pipeline Doctrine Dashboard Review Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `dashboard_review_accepted_as_reviewed_evidence`: `{packet['dashboard_review_accepted_as_reviewed_evidence']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Decision Boundary",
        "",
        str(packet["decision_outcome_summary"]),
        "",
        "## Observed Counts",
    ]
    for key, value in packet["observed_counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Allowed Follow-On Actions", ""])
    for item in packet["allowed_follow_on_actions"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_pipeline_doctrine_dashboard_review_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_pipeline_doctrine_dashboard_review_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / RECORD_MD_PATH,
        render_global_pipeline_doctrine_dashboard_review_record_markdown(packet),
    )
    return packet
