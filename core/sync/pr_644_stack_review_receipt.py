from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "Pr644StackReviewReceipt.v1"
RECEIPT_ID = "PR_644_STACK_REVIEW_RECEIPT_001"
SOURCE_SNAPSHOT = "input/github/pr_644_status_snapshot.json"
OUT_JSON = "out/operator_review/pr_644_stack_review_receipt_001.latest.json"
OUT_MD = "out/operator_review/pr_644_stack_review_receipt_001.latest.md"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "auto_approval": False,
        "draft_state_mutation": False,
        "execution": False,
        "github_writeback": False,
        "merge_authority": False,
        "notion_writeback": False,
        "pr_ready_state_change": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
    }


def _check_records(snapshot: Mapping[str, Any]) -> list[dict[str, str]]:
    records = []
    for item in snapshot.get("statusCheckRollup", []):
        if not isinstance(item, Mapping):
            continue
        records.append(
            {
                "name": str(item.get("name", "")),
                "workflow_name": str(item.get("workflowName", "")),
                "status": str(item.get("status", "")),
                "conclusion": str(item.get("conclusion", "")),
                "details_url": str(item.get("detailsUrl", "")),
            }
        )
    return sorted(records, key=lambda item: (item["workflow_name"], item["name"]))


def _check_summary(records: list[dict[str, str]]) -> dict[str, Any]:
    successful = [
        item
        for item in records
        if item["status"] == "COMPLETED" and item["conclusion"] == "SUCCESS"
    ]
    pending = [item for item in records if item["status"] != "COMPLETED"]
    failed = [
        item
        for item in records
        if item["status"] == "COMPLETED" and item["conclusion"] != "SUCCESS"
    ]
    return {
        "total_checks": len(records),
        "successful_checks": len(successful),
        "pending_checks": len(pending),
        "failed_checks": len(failed),
        "all_required_checks_successful": bool(records) and not pending and not failed,
    }


def build_pr_644_stack_review_receipt(
    repo_root: str | Path = ".",
    *,
    source_snapshot_path: str | Path = SOURCE_SNAPSHOT,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_snapshot_path)
    snapshot = _read_json(root / source_path)
    records = _check_records(snapshot)
    summary = _check_summary(records)
    latest_reviews = snapshot.get("latestReviews", [])
    latest_review_count = len(latest_reviews) if isinstance(latest_reviews, list) else 0
    blockers: list[str] = []
    if snapshot.get("state") != "OPEN":
        blockers.append("pr_not_open")
    if snapshot.get("isDraft") is True:
        blockers.append("pr_is_draft")
    if snapshot.get("mergeable") != "MERGEABLE":
        blockers.append("pr_not_mergeable")
    if summary["pending_checks"]:
        blockers.append("checks_pending")
    if summary["failed_checks"]:
        blockers.append("checks_failed")
    if latest_review_count == 0:
        blockers.append("operator_review_not_observed")

    source_observed = bool(snapshot)
    checks_complete = summary["all_required_checks_successful"]
    if not source_observed:
        receipt_status = NOT_COMPUTABLE
    elif not checks_complete:
        receipt_status = "PR_644_STACK_REVIEW_HELD_FOR_CHECK_COMPLETION"
    elif blockers:
        receipt_status = "PR_644_STACK_REVIEW_HELD_FOR_OPERATOR_REVIEW"
    else:
        receipt_status = "PR_644_STACK_REVIEW_READY_FOR_OPERATOR_FINAL_REVIEW"
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": RECEIPT_ID,
        "receipt_status": receipt_status,
        "source_snapshot_path": source_path.as_posix(),
        "source_snapshot_hash": _sha256(root / source_path),
        "pr_number": int(snapshot.get("number", 0) or 0),
        "pr_url": str(snapshot.get("url", NOT_COMPUTABLE)),
        "pr_title": str(snapshot.get("title", NOT_COMPUTABLE)),
        "base_ref": str(snapshot.get("baseRefName", NOT_COMPUTABLE)),
        "head_ref": str(snapshot.get("headRefName", NOT_COMPUTABLE)),
        "state": str(snapshot.get("state", NOT_COMPUTABLE)),
        "is_draft": bool(snapshot.get("isDraft", False)),
        "mergeable": str(snapshot.get("mergeable", NOT_COMPUTABLE)),
        "check_summary": summary,
        "check_records": records,
        "review_summary": {
            "latest_review_count": latest_review_count,
            "review_decision_observed": latest_review_count > 0,
        },
        "blockers": sorted(blockers),
        "recommended_next_action": (
            "hold PR #644 until it is no longer draft and an operator performs final review"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "safe_to_merge": False,
        "safe_to_mark_ready_for_review": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "github_writeback_allowed": False,
        "notion_writeback_allowed": False,
        "merge_authority": False,
        "draft_state_mutation_allowed": False,
        "auto_approval_allowed": False,
        "authority_locks": _authority_locks(),
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_pr_644_stack_review_receipt(path: str | Path, packet: Mapping[str, Any]) -> None:
    write_canonical_json(path, packet)


def render_pr_644_stack_review_receipt_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# PR 644 Stack Review Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- receipt_status: {packet['receipt_status']}",
        f"- pr_number: {packet['pr_number']}",
        f"- head_ref: {packet['head_ref']}",
        f"- base_ref: {packet['base_ref']}",
        f"- is_draft: {packet['is_draft']}",
        f"- mergeable: {packet['mergeable']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_merge: {packet['safe_to_merge']}",
        f"- github_writeback_allowed: {packet['github_writeback_allowed']}",
        "",
        "## Check Summary",
    ]
    summary = packet.get("check_summary", {})
    if isinstance(summary, Mapping):
        for key in sorted(summary):
            lines.append(f"- {key}: {summary[key]}")
    lines.extend(["", "## Checks"])
    for record in packet.get("check_records", []):
        if isinstance(record, Mapping):
            conclusion = str(record["conclusion"])
            suffix = f" {conclusion}" if conclusion else ""
            lines.append(
                "- "
                f"{record['workflow_name']} / {record['name']}: "
                f"{record['status']}{suffix}"
            )
    lines.extend(["", "## Blockers"])
    for blocker in packet.get("blockers", []):
        lines.append(f"- {blocker}")
    return lines


def write_pr_644_stack_review_receipt_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_pr_644_stack_review_receipt_markdown(packet)) + "\n",
        encoding="utf-8",
    )
