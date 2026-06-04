from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "NotionWritebackDryRunPlan.v1"
PLAN_ID = "NOTION_WRITEBACK_DRY_RUN_PLAN_001"
OUT_JSON = "out/sync/notion_writeback_dry_run_plan/latest.json"
OUT_MD = "out/sync/notion_writeback_dry_run_plan/latest.md"
DEFAULT_SOURCE_ARTIFACTS: tuple[str, ...] = (
    "docs/status/badges.json",
    "docs/status/continuity-spine.json",
    "out/continuity_namespace_alias_plan/latest.json",
)

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_ALLOWED_FIELDS: tuple[str, ...] = (
    "canon_status",
    "ci_status",
    "continuity_lane_count",
    "governance_status",
    "last_sync_packet_hash",
    "merge_status",
    "milestone",
    "repo",
    "source_artifact_hashes",
)
_FORBIDDEN_ACTIONS: tuple[str, ...] = (
    "unverified_notion_write",
    "database_schema_mutation",
    "page_deletion",
    "content_replacement_without_old_str",
    "runtime_mutation",
    "canon_promotion",
    "scheduler_mutation",
    "token_minting",
    "forecast_authority_grant",
)


def _file_hash(repo_root: Path, rel_path: str) -> str:
    try:
        return hashlib.sha256((repo_root / rel_path).read_bytes()).hexdigest()
    except OSError:
        return _NOT_COMPUTABLE


def _artifact_hashes(repo_root: Path, artifact_paths: tuple[str, ...]) -> dict[str, str]:
    return {path: _file_hash(repo_root, path) for path in sorted(artifact_paths)}


def _missing_artifacts(hashes: dict[str, str]) -> list[str]:
    return [path for path, digest in hashes.items() if digest == _NOT_COMPUTABLE]


def _target_status(target_page_id: str, target_label: str) -> str:
    if target_page_id == _NOT_COMPUTABLE or not target_page_id.strip():
        return "TARGET_NOT_CONFIGURED"
    if target_label == _NOT_COMPUTABLE or not target_label.strip():
        return "TARGET_NOT_CONFIGURED"
    return "TARGET_CONFIGURED"


def _planned_operations(target_page_id: str, target_label: str, hashes: dict[str, str]) -> list[dict[str, Any]]:
    if _target_status(target_page_id, target_label) != "TARGET_CONFIGURED":
        return []
    return [
        {
            "operation_id": "notion_update_allowed_properties",
            "operation_type": "update_page_properties",
            "target_page_id": target_page_id,
            "target_label": target_label,
            "allowed_fields": list(_ALLOWED_FIELDS),
            "source_artifact_hashes": hashes,
            "requires_exact_target_match": True,
            "requires_operator_authorization_record": True,
            "dry_run_only": True,
        },
        {
            "operation_id": "notion_append_sync_receipt",
            "operation_type": "append_page_content",
            "target_page_id": target_page_id,
            "target_label": target_label,
            "content_mode": "append_only",
            "requires_operator_authorization_record": True,
            "dry_run_only": True,
        },
    ]


def build_notion_writeback_dry_run_plan(
    *,
    repo_root: str | Path,
    target_page_id: str = _NOT_COMPUTABLE,
    target_label: str = _NOT_COMPUTABLE,
    source_artifacts: tuple[str, ...] = DEFAULT_SOURCE_ARTIFACTS,
) -> dict[str, Any]:
    root = Path(repo_root)
    normalized_target_page_id = target_page_id.strip() or _NOT_COMPUTABLE
    normalized_target_label = target_label.strip() or _NOT_COMPUTABLE
    hashes = _artifact_hashes(root, tuple(sorted(source_artifacts)))
    missing = _missing_artifacts(hashes)
    target_state = _target_status(normalized_target_page_id, normalized_target_label)
    plan_status = (
        "DRY_RUN_PLAN_READY"
        if target_state == "TARGET_CONFIGURED" and not missing
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "target_state": target_state,
        "target_page_id": normalized_target_page_id,
        "target_label": normalized_target_label,
        "source_artifact_hashes": hashes,
        "missing_evidence": missing,
        "allowed_fields": list(_ALLOWED_FIELDS),
        "planned_operations": _planned_operations(
            normalized_target_page_id,
            normalized_target_label,
            hashes,
        ),
        "writeback_performed": False,
        "writeback_authorized": False,
        "notion_writeback": False,
        "github_writeback": False,
        "dry_run_only": True,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "valid_for_execution": False,
        "recommended_next_lane": "NOTION_WRITEBACK_AUTHORIZATION_GATE_REQUIRED",
        "authority_locks": {
            "canon_promotion": False,
            "execution_authority": False,
            "forecast_authority": False,
            "notion_mutation_authority": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
        },
        "forbidden_actions": list(_FORBIDDEN_ACTIONS),
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_notion_writeback_dry_run_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_notion_writeback_dry_run_plan_markdown(path: str | Path, packet: dict[str, Any]) -> None:
    lines = [
        "# Notion Writeback Dry-Run Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_state: {packet['target_state']}",
        f"- target_label: {packet['target_label']}",
        f"- dry_run_only: {packet['dry_run_only']}",
        f"- writeback_performed: {packet['writeback_performed']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        "",
        "## Source Artifact Hashes",
    ]
    hashes = packet.get("source_artifact_hashes", {})
    if isinstance(hashes, dict):
        for rel_path in sorted(hashes):
            lines.append(f"- {rel_path}: {hashes[rel_path]}")
    missing = packet.get("missing_evidence", [])
    lines.extend(["", "## Missing Evidence"])
    if isinstance(missing, list) and missing:
        lines.extend(f"- {item}" for item in missing)
    else:
        lines.append("- none")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
