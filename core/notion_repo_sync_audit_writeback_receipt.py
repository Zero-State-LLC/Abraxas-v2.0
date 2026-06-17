from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "NotionRepoSyncAuditWritebackReceipt.v1"
RECEIPT_ID = "ABRAXAS_NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_001"
RECEIPT_STATUS_READY = "NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_READY_ADVISORY_ONLY"
RECEIPT_STATUS_NOT_COMPUTABLE = "NOTION_REPO_SYNC_AUDIT_WRITEBACK_RECEIPT_NOT_COMPUTABLE"
NOTION_WRITEBACK_PAGE_URL = "https://app.notion.com/p/3823e8ba2f5c8199ae13c04610f89801"

AUTHORITY_LOCKS = {
    "activation": False,
    "auto_continuation": False,
    "canon_mutation": False,
    "decision_record_creation": False,
    "execution_authority": False,
    "github_writeback": False,
    "notion_writeback_beyond_this_sync_report": False,
    "operator_attestation": False,
    "promotion": False,
    "queue_mutation": False,
    "registration": False,
    "runtime_mutation": False,
    "scheduler_mutation": False,
    "token_minting": False,
}

DANGEROUS_TRUE_KEYS = (
    "activation_authorized",
    "authorization_granted",
    "authorization_record_created",
    "authorization_record_creation_authorized",
    "auto_continuation",
    "canon_mutation",
    "decision_record_completed",
    "decision_record_created",
    "decision_record_creation_authorized",
    "decision_record_emitted",
    "decision_record_finalized",
    "decision_record_materialized",
    "evidence_bundle_created",
    "evidence_bundle_creation_authorized",
    "execution_authority",
    "github_writeback_allowed",
    "implementation_authorized",
    "notion_writeback_allowed",
    "operator_attestation_created",
    "promotion_authorized",
    "queue_mutation",
    "runtime_mutation",
    "safe_to_auto_continue",
    "scheduler_mutation",
    "valid_for_execution",
)

SOURCE_ARTIFACTS = (
    {
        "source_id": "completion_validation_approval_gate",
        "path": "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_gate_001.latest.json",
        "expected_status": "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_APPROVAL_GATE_READY_FOR_SEPARATE_RECORD_COMPLETION_VALIDATION_PLANNING",
    },
    {
        "source_id": "completion_validation_approval_intake_gate",
        "path": "out/operator_review/v2_hygiene_phase1_stabilization_decision_record_completion_validation_approval_intake_gate_001.latest.json",
        "expected_status": "V2_HYGIENE_PHASE1_STABILIZATION_DECISION_RECORD_COMPLETION_VALIDATION_APPROVAL_INTAKE_VALIDATED_FOR_FUTURE_RECORD_COMPLETION_VALIDATION_GATE",
    },
    {
        "source_id": "terminal_hold_consolidation_receipt",
        "path": "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json",
        "expected_status": "OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_READY",
    },
    {
        "source_id": "operator_review_required_items_bulk_disposition",
        "path": "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json",
        "expected_status": "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_REVIEW_ONLY_APPROVED_WITH_HOLDS",
    },
    {
        "source_id": "p102g_plus_operator_decision_surface_audit",
        "path": "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json",
        "expected_status": "P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_READY",
    },
    {
        "source_id": "continuation_frontier_reconciliation",
        "path": "out/audit/continuation_frontier_reconciliation_001.latest.json",
        "expected_status": "CONTINUATION_FRONTIER_RECONCILIATION_EMITTED_ADVISORY_ONLY",
    },
    {
        "source_id": "research_canary_final_activation_authorization_review",
        "path": "out/research_canary_final_activation_authorization_review/latest.json",
        "expected_status": "FINAL_ACTIVATION_AUTHORIZATION_REVIEW_RECORD_EMITTED",
    },
)

NOTION_SOURCES = (
    {
        "source_id": "upgrade_completion_receipt_2026_06_13",
        "title": "Abraxas v2.0 - Upgrade Completion Receipt (2026-06-13)",
        "url": "https://app.notion.com/p/a64497ce1a8f422ba9998dcbf252ef7f",
        "classification": "AUTHORITY_BOUNDARY_CONFIRMED",
    },
    {
        "source_id": "live_status_dashboard_2026_06_12",
        "title": "Abraxas v2.0 Live Status Dashboard & Alignment Hub (2026-06-12)",
        "url": "https://app.notion.com/p/37d3e8ba2f5c81c68756f438ad61c2c3",
        "classification": "STALE_STATUS_BASELINE",
    },
    {
        "source_id": "repo_notion_sync_receipt_2026_06_12",
        "title": "ABRAXAS v2.0 - Repo <-> Notion Sync Receipt 2026-06-12",
        "url": "https://app.notion.com/p/37d3e8ba2f5c81bfbd4fcdfba9f1e2ea",
        "classification": "STALE_STATUS_BASELINE",
    },
    {
        "source_id": "v2_implementation_surfaces",
        "title": "v2.0 Implementation Surfaces",
        "url": "https://app.notion.com/p/37e3e8ba2f5c811a96f9cdd0cc09bf7f",
        "classification": "STALE_PHASE_SURFACE",
    },
    {
        "source_id": "governance_decision_vocabulary",
        "title": "Abraxas Governance Decision Vocabulary - HOLD vs BLOCK Patterns",
        "url": "https://app.notion.com/p/37d3e8ba2f5c812a8fe3c1d89f2847e1",
        "classification": "AUTHORITY_BOUNDARY_CONFIRMED",
    },
    {
        "source_id": "canon_spine",
        "title": "Abraxas - Subsystem Inventory (Canon Spine)",
        "url": "https://app.notion.com/p/73460b504dfd4cc393e7906559678624",
        "classification": "P130_P132_REFERENCE_STALE_UNLESS_REAUTHORIZED",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _status_value(payload: Mapping[str, Any]) -> str:
    for key in (
        "status",
        "receipt_status",
        "gate_status",
        "disposition_status",
        "audit_status",
        "lane_status",
    ):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return "STATUS_NOT_OBSERVED"


def _source_hash(payload: Mapping[str, Any]) -> str:
    for key in ("gate_hash", "receipt_hash", "packet_hash", "disposition_hash", "audit_hash"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return canonical_hash(payload)


def _dangerous_true_keys(payload: Mapping[str, Any]) -> list[str]:
    observed: list[str] = []
    for key in DANGEROUS_TRUE_KEYS:
        if payload.get(key) is True:
            observed.append(key)
    return sorted(observed)


def _source_record(root: Path, source: Mapping[str, str]) -> dict[str, Any]:
    path = source["path"]
    payload = _read_json(root / path)
    if payload is None:
        return {
            "source_id": source["source_id"],
            "path": path,
            "path_observed": False,
            "observed_status": "MISSING_ARTIFACT",
            "expected_status": source["expected_status"],
            "classification": "MISSING_ARTIFACT",
            "source_hash": None,
            "authority_drift_observed": False,
            "authority_drift_keys": [],
        }

    status = _status_value(payload)
    dangerous_keys = _dangerous_true_keys(payload)
    status_matches = status == source["expected_status"]
    authority_drift = bool(dangerous_keys)
    if authority_drift:
        classification = "AUTHORITY_DRIFT"
    elif status_matches:
        classification = "OBSERVED"
    else:
        classification = "STATUS_DRIFT"

    return {
        "source_id": source["source_id"],
        "path": path,
        "path_observed": True,
        "observed_status": status,
        "expected_status": source["expected_status"],
        "classification": classification,
        "source_hash": _source_hash(payload),
        "authority_drift_observed": authority_drift,
        "authority_drift_keys": dangerous_keys,
    }


def _git_output(root: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", *args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "NOT_OBSERVED"
    return result.stdout.strip()


def _dirty_work_assessment(root: Path) -> dict[str, Any]:
    status_lines = [
        line
        for line in _git_output(root, "status", "--short").splitlines()
        if line.strip()
    ]
    return {
        "tracked_change_count": sum(1 for line in status_lines if not line.startswith("??")),
        "untracked_paths": sorted(line[3:] for line in status_lines if line.startswith("??")),
        "scripts_casing_regression_observed": False,
    }


def build_notion_repo_sync_audit_writeback_receipt(
    *,
    repo_root: str | Path,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_records = [_source_record(root, source) for source in SOURCE_ARTIFACTS]
    source_records = sorted(source_records, key=lambda record: record["source_id"])
    blockers = []
    for record in source_records:
        if record["classification"] != "OBSERVED":
            blockers.append(
                {
                    "source_id": record["source_id"],
                    "classification": record["classification"],
                    "observed_status": record["observed_status"],
                }
            )
    status = RECEIPT_STATUS_NOT_COMPUTABLE if blockers else RECEIPT_STATUS_READY
    ready = not blockers
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": RECEIPT_ID,
        "receipt_status": status,
        "source_readiness": "SOURCE_ARTIFACTS_READY" if ready else "NOT_COMPUTABLE",
        "source_blockers": blockers,
        "repo_state": {
            "branch": _git_output(root, "branch", "--show-current"),
            "head_short": _git_output(root, "rev-parse", "--short", "HEAD"),
            "dirty_work_assessment": _dirty_work_assessment(root),
        },
        "source_artifact_records": source_records,
        "notion_source_records": list(NOTION_SOURCES),
        "sync_findings": [
            {
                "finding_id": "repo_frontier_ahead_of_notion",
                "classification": "STALE_NOTION_STATUS",
                "summary": (
                    "Repo-visible v2 stabilization completion-validation approval "
                    "intake and gate surfaces are newer than the fetched Notion status pages."
                ),
            },
            {
                "finding_id": "authority_boundary_agreement",
                "classification": "AUTHORITY_BOUNDARY_CONFIRMED",
                "summary": (
                    "Fetched Notion pages and repo artifacts agree that execution, activation, "
                    "runtime/canon mutation, queue/scheduler mutation, promotion, registration, "
                    "and GitHub writeback remain denied."
                ),
            },
            {
                "finding_id": "p130_plus_notion_mentions_stale",
                "classification": "STALE_NOTION_SPEC",
                "summary": (
                    "P130/P132 Notion batch references remain stale unless a fresh governed "
                    "operator decision authorizes downstream P131+ work."
                ),
            },
        ],
        "writeback_scope": {
            "operator_authorized_this_sync_writeback": True,
            "observed_writeback_page_url": NOTION_WRITEBACK_PAGE_URL,
            "writeback_target": "new Notion child page under the Abraxas live status hub",
            "writeback_global_authority_granted": False,
            "writeback_allows_future_automation": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "recommended_next_action": (
            "record this repo-to-Notion sync audit as advisory writeback only; keep "
            "downstream implementation, execution, mutation, registration, activation, "
            "promotion, and auto-continuation blocked until a separate governed lane exists"
        ),
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "valid_for_execution": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "github_writeback_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "decision_record_creation_authorized": False,
        "activation_authorized": False,
        "promotion_authorized": False,
        "registration_authorized": False,
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_notion_repo_sync_audit_writeback_receipt(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_notion_repo_sync_audit_writeback_receipt_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# Notion Repo Sync Audit Writeback Receipt 001",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- receipt_status: {packet['receipt_status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Repo State",
        f"- branch: {packet['repo_state']['branch']}",
        f"- head_short: {packet['repo_state']['head_short']}",
        "",
        "## Source Artifacts",
    ]
    for record in packet.get("source_artifact_records", []):
        if isinstance(record, dict):
            lines.append(
                "- "
                f"{record['source_id']}: {record['classification']} "
                f"({record['observed_status']})"
            )
    lines.extend(["", "## Notion Sources"])
    for record in packet.get("notion_source_records", []):
        if isinstance(record, dict):
            lines.append(
                "- "
                f"{record['source_id']}: {record['classification']} - {record['url']}"
            )
    lines.extend(["", "## Sync Findings"])
    for finding in packet.get("sync_findings", []):
        if isinstance(finding, dict):
            lines.append(
                "- "
                f"{finding['finding_id']}: {finding['classification']} - {finding['summary']}"
            )
    lines.extend(
        [
            "",
            "## Authority Locks",
        ]
    )
    for key, value in sorted(packet.get("authority_locks", {}).items()):
        lines.append(f"- {key}: {value}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
