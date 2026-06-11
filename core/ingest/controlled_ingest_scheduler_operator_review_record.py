from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "ControlledIngestSchedulerOperatorReviewRecord.v1"
AUDIT_JSON_PATH = Path("out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json")
RECORD_JSON_PATH = Path("out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json")
RECORD_MD_PATH = Path("out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.md")


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


def build_controlled_ingest_scheduler_operator_review_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    audit = _read_json(root / AUDIT_JSON_PATH)
    audit_ready = (
        audit.get("schema_version") == "ControlledIngestSchedulerGovernanceAudit.v1"
        and audit.get("final_status") == "PASS"
        and audit.get("audit_posture") == "CLEAN"
        and audit.get("recommended_next_step") == "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW"
        and audit.get("finding_counts", {}).get("FAIL") == 0
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_ACCEPTED"
        if audit_ready
        else "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_BLOCKED",
        "record_id": "controlled_ingest_scheduler_operator_review_record_001",
        "record_hash": "",
        "command": "BUILD_CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "decision_scope": "CONTROLLED_INGEST_SCHEDULER_AUDIT_REVIEW_ONLY",
        "selected_decision": "APPROVE_OPERATOR_REVIEW" if audit_ready else "NOT_COMPUTABLE",
        "operator_instruction_observed": "yes approve",
        "audit_accepted_as_reviewed_evidence": audit_ready,
        "scheduler_handoff_target_patch_confirmed": audit_ready,
        "source_audit_path": str(AUDIT_JSON_PATH),
        "source_audit_hash": str(audit.get("audit_hash", "NOT_COMPUTABLE")),
        "source_audit_status": str(audit.get("final_status", "NOT_COMPUTABLE")),
        "source_audit_posture": str(audit.get("audit_posture", "NOT_COMPUTABLE")),
        "source_recommended_next_step": str(audit.get("recommended_next_step", "NOT_COMPUTABLE")),
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
            "Controlled ingest scheduler governance audit is accepted as review-only evidence; no scheduler, "
            "runtime, queue, route, forecast, canon, token, writeback, ingest-runner, or execution authority is granted."
        ),
        "allowed_follow_on_actions": [
            "MAINTAIN_CONTROLLED_INGEST_SCHEDULER_AUDIT_AS_REVIEWED_EVIDENCE",
            "MAINTAIN_SHADOW_ONLY_SCHEDULER_BOUNDARY",
            "KEEP_RUNTIME_AND_SCHEDULER_MUTATION_BLOCKED",
        ],
        "blocked_actions": [
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
            "maintain controlled ingest scheduler audit as reviewed evidence until a separate governed lane "
            "explicitly authorizes stabilization-window design or runtime integration"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
    }
    packet["record_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "record_hash"})
    return packet


def render_controlled_ingest_scheduler_operator_review_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Controlled Ingest Scheduler Operator Review Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `selected_decision`: `{packet['selected_decision']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `audit_accepted_as_reviewed_evidence`: `{packet['audit_accepted_as_reviewed_evidence']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Decision Boundary",
        "",
        str(packet["decision_outcome_summary"]),
        "",
        "## Blocked Actions",
        "",
    ]
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_controlled_ingest_scheduler_operator_review_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_controlled_ingest_scheduler_operator_review_record(root)
    write_canonical_json(target_root / RECORD_JSON_PATH, packet)
    _write_markdown(
        target_root / RECORD_MD_PATH,
        render_controlled_ingest_scheduler_operator_review_record_markdown(packet),
    )
    return packet
