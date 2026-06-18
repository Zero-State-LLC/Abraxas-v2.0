from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json

PACKET_ID = "notion_p131_p133_stale_spec_reconciliation_packet_001"
OUT_PATH = Path("out/sync/notion_p131_p133_stale_spec_reconciliation_packet_001.latest.json")
READY_STATUS = "NOTION_P131_P133_STALE_SPEC_RECONCILIATION_PACKET_READY"
BLOCKED_STATUS = "NOTION_P131_P133_STALE_SPEC_RECONCILIATION_PACKET_BLOCKED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"

P131_ARTIFACT = Path("out/research_canary_final_activation_operator_decision_record/latest.json")
P132_ARTIFACT = Path("out/research_canary_advisory_shadow_activation_record/latest.json")

STALE_LANE_RECONCILIATION: tuple[dict[str, str], ...] = (
    {
        "notion_lane_id": "P131_RESEARCH_CANARY_FINAL_ACTIVATION_AUTHORIZATION_DECISION_RECORD",
        "repo_truth": "P131 operator decision record implemented; per-candidate advisory shadow approval supported",
        "repo_artifact_path": P131_ARTIFACT.as_posix(),
        "repo_lane_id": "P131_RESEARCH_CANARY_FINAL_ACTIVATION_OPERATOR_DECISION_RECORD",
        "repo_authorization_observed": "true",
    },
    {
        "notion_lane_id": "P132_RESEARCH_CANARY_FINAL_ACTIVATION_DENIAL_HOLD_ROUTING",
        "repo_truth": "P132 advisory shadow activation record implemented (not denial-only routing)",
        "repo_artifact_path": P132_ARTIFACT.as_posix(),
        "repo_lane_id": "P132_RESEARCH_CANARY_ADVISORY_SHADOW_ACTIVATION_RECORD",
        "repo_authorization_observed": "true",
    },
    {
        "notion_lane_id": "P133_RESEARCH_CANARY_LIVE_ACTIVATION_PLAN_DRAFT",
        "repo_truth": "P133 production activation lane not implemented; deferred to separate governed design",
        "repo_artifact_path": NOT_COMPUTABLE,
        "repo_lane_id": NOT_COMPUTABLE,
        "repo_authorization_observed": "false",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _artifact_status(path: Path, root: Path) -> str:
    packet = _read_json(root / path)
    if packet is None:
        return "NOT_OBSERVED"
    for field in ("status", "lane_status", "record_status"):
        value = packet.get(field)
        if isinstance(value, str):
            return value
    return "OBSERVED"


def build_notion_p131_p133_stale_spec_reconciliation_packet(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    blockers: list[str] = []
    lane_records: list[dict[str, Any]] = []
    for item in STALE_LANE_RECONCILIATION:
        artifact_path = item["repo_artifact_path"]
        observed_status = (
            _artifact_status(Path(artifact_path), root)
            if artifact_path != NOT_COMPUTABLE
            else NOT_COMPUTABLE
        )
        if item["repo_authorization_observed"] == "true" and observed_status == "NOT_OBSERVED":
            blockers.append(f"{item['notion_lane_id']}_repo_artifact_missing")
        lane_records.append(
            {
                "notion_lane_id": item["notion_lane_id"],
                "repo_truth": item["repo_truth"],
                "repo_artifact_path": artifact_path,
                "repo_lane_id": item["repo_lane_id"],
                "repo_artifact_status": observed_status,
                "repo_authorization_observed": item["repo_authorization_observed"] == "true",
                "recommended_notion_action": (
                    "manual_copy_paste_update"
                    if item["repo_authorization_observed"] == "true"
                    else "mark_deferred_or_archive"
                ),
            }
        )
    blockers = sorted(set(blockers))
    ready = not blockers
    packet_base: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "manual_operator_copy_paste_only": True,
        "operator_review_posture": "ACTIVE",
        "downstream": NOT_COMPUTABLE,
        "packet_blockers": blockers,
        "stale_lane_records": lane_records,
        "recommended_next_action": (
            "copy stale_lane_records into Notion Canon Spine manually after operator review"
            if ready
            else "restore missing repo artifacts before Notion reconciliation packet emission"
        ),
    }
    packet_base["sync_packet_hash"] = canonical_hash(packet_base)
    return json.loads(
        json.dumps(packet_base, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def write_notion_p131_p133_stale_spec_reconciliation_packet(
    repo_root: str | Path = ".",
    *,
    out_path: Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    packet = build_notion_p131_p133_stale_spec_reconciliation_packet(root)
    target = out_path if out_path is not None else root / OUT_PATH
    write_canonical_json(target, packet)
    return packet
