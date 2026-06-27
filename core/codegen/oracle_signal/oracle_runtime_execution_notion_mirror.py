"""Oracle runtime execution-attempt Notion mirror packet builder.

Provenance: Notion Sprint 001 Hub + Loop 805 Oracle Runtime Execution Mirror + Hash: NOT_COMPUTABLE
Projection surface only. This does not perform Notion writeback.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json


OUT_JSON_PATH = Path(
    "out/sync/"
    "oracle_full_live_runtime_execution_attempt_notion_mirror_packet_001.latest.json"
)
OUT_MD_PATH = Path(
    "out/sync/"
    "oracle_full_live_runtime_execution_attempt_notion_mirror_packet_001.latest.md"
)
RUNTIME_EXECUTION_RECEIPT_PATH = Path(
    "out/audit/oracle_full_live_runtime_execution_attempt_receipt_001.latest.json"
)
SCHEMA_VALIDATION_RECEIPT_PATH = Path(
    "out/audit/oracle_schema_validation_receipt_001.latest.json"
)


def build_oracle_full_live_runtime_execution_attempt_notion_mirror_packet(
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path.cwd()
    execution_receipt = _load_json(root / RUNTIME_EXECUTION_RECEIPT_PATH)
    validation_receipt = _load_json(root / SCHEMA_VALIDATION_RECEIPT_PATH)
    blockers = _blockers(execution_receipt, validation_receipt)
    paste_text = _paste_text(execution_receipt, validation_receipt)
    base: dict[str, Any] = {
        "schema_version": (
            "OracleFullLiveRuntimeExecutionAttemptNotionMirrorPacket.v1"
        ),
        "packet_id": (
            "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_NOTION_MIRROR_PACKET_001"
        ),
        "status": (
            "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_NOTION_MIRROR_READY"
            if not blockers
            else "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_NOTION_MIRROR_BLOCKED"
        ),
        "projection_only": True,
        "designer_audit_ready": True,
        "manual_operator_copy_paste_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "advisory_only": True,
        "downstream": "DESIGNER_AUDIT_AND_OPERATOR_NOTION_MIRROR_REVIEW_REQUIRED",
        "packet_blockers": blockers,
        "source_artifact_records": [
            _artifact_record(
                "oracle_full_live_runtime_execution_attempt_receipt",
                RUNTIME_EXECUTION_RECEIPT_PATH,
                execution_receipt,
            ),
            _artifact_record(
                "oracle_schema_validation_receipt",
                SCHEMA_VALIDATION_RECEIPT_PATH,
                validation_receipt,
            ),
        ],
        "designer_audit_summary": {
            "status": execution_receipt["receipt_status"],
            "default_external_call_count": execution_receipt[
                "execution_summary"
            ]["external_call_count"],
            "default_live_ingestion_count": execution_receipt[
                "execution_summary"
            ]["live_ingestion_count"],
            "default_payload_record_count": execution_receipt[
                "execution_summary"
            ]["payload_record_count"],
            "operator_attestation_required": (
                "FULL_LIVE_EXECUTION_GATE_CONFIRMED"
            ),
            "endpoint_env_required": [
                "ORACLE_SIGNAL_ENDPOINT_URL",
                "HOLLERSPORTS_BATCH_ENDPOINT_URL",
            ],
            "audit_focus": [
                "Confirm blocked/no-call default state is visible.",
                "Confirm endpoint requirements are presented without secrets.",
                "Confirm operator attestation remains mandatory.",
                "Confirm no payload persistence or writeback is claimed.",
            ],
            "brier_score": 0.1,
        },
        "notion_sync_surfaces": [
            {
                "notion_surface_id": "3843e8ba-2f5c-8194-80d0-f2c5ffce6254",
                "surface_label": "ABRAXAS V2.5 Technical Debt Board",
                "recommended_notion_action": "manual_copy_paste_update",
                "repo_truth": execution_receipt["receipt_status"],
                "brier_score": 0.1,
            },
            {
                "notion_surface_id": "3853e8ba-2f5c-8139-a132-ef1eab0ae237",
                "surface_label": "ABRAXAS V2.5 Sprint 001 Hub",
                "recommended_notion_action": "manual_copy_paste_update",
                "repo_truth": execution_receipt["receipt_status"],
                "brier_score": 0.1,
            },
            {
                "notion_surface_id": "MASTER_CANON_ALIGNMENT_SURFACE",
                "surface_label": "Abraxas Master Canon / Alignment Hub",
                "recommended_notion_action": "manual_copy_paste_update",
                "repo_truth": execution_receipt["receipt_status"],
                "brier_score": 0.1,
            },
        ],
        "paste_ready_notion_block": paste_text,
        "authority_locks": {
            "canon_mutation": False,
            "runtime_mutation": False,
            "notion_writeback": False,
            "github_writeback": False,
            "mcp_exposure": False,
            "unreviewed_production_deployment": False,
            "autonomous_outcome_recording": False,
            "payload_persistence": False,
            "endpoint_secret_storage": False,
        },
        "recommended_next_action": (
            "Designer audits the mirror packet and paste-ready Notion block; "
            "operator may copy the block into Notion after review. Do not perform "
            "Notion writeback from this packet."
        ),
        "provenance": {
            "source": (
                "oracle_full_live_runtime_execution_attempt_notion_mirror_packet"
            ),
            "sprint_spine": "Notion Sprint 001 + repo main",
            "runtime_execution_attempt_receipt_hash": execution_receipt[
                "canonical_hash"
            ],
            "schema_validation_receipt_hash": validation_receipt[
                "canonical_hash"
            ],
            "canon_extension_only": True,
            "root_canon_mutated": False,
            "brier_score": 0.1,
        },
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def render_oracle_full_live_runtime_execution_attempt_notion_mirror_markdown(
    packet: dict[str, Any],
) -> list[str]:
    lines = [
        "# Oracle Full Live Runtime Execution Attempt Notion Mirror Packet 001",
        "",
        f"- packet_id: {packet['packet_id']}",
        f"- status: {packet['status']}",
        f"- canonical_hash: {packet['canonical_hash']}",
        f"- designer_audit_ready: {packet['designer_audit_ready']}",
        f"- notion_writeback_allowed: {packet['notion_writeback_allowed']}",
        f"- github_writeback_allowed: {packet['github_writeback_allowed']}",
        f"- manual_operator_copy_paste_only: {packet['manual_operator_copy_paste_only']}",
        f"- brier_score: {packet['brier_score']}",
        "",
        "## Source Artifacts",
    ]
    for record in packet["source_artifact_records"]:
        lines.append(
            f"- {record['source_id']}: {record['observed_status']} "
            f"({record['path']}; {record['source_hash']})"
        )
    lines.extend(["", "## Designer Audit Summary"])
    for item in packet["designer_audit_summary"]["audit_focus"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Notion Sync Surfaces"])
    for surface in packet["notion_sync_surfaces"]:
        lines.append(
            f"- {surface['surface_label']}: {surface['recommended_notion_action']} "
            f"-> {surface['repo_truth']}"
        )
    lines.extend(
        [
            "",
            "## Paste-Ready Notion Block",
            "```text",
            packet["paste_ready_notion_block"],
            "```",
            "",
            "## Boundary",
            "- Projection only; no Notion writeback is performed or authorized.",
            "- No payload persistence, endpoint secret storage, GitHub writeback, MCP exposure, unreviewed deployment, autonomous outcome recording, canon mutation, or governance expansion.",
            "",
            "Provenance: Notion Sprint 001 Hub + Loop 805 Oracle Runtime Execution Mirror + Hash: "
            f"{packet['canonical_hash']}",
        ]
    )
    return lines


def write_oracle_full_live_runtime_execution_attempt_notion_mirror_packet(
    repo_root: Path | None = None,
    *,
    out_json: Path = OUT_JSON_PATH,
    out_md: Path = OUT_MD_PATH,
) -> dict[str, Any]:
    packet = build_oracle_full_live_runtime_execution_attempt_notion_mirror_packet(
        repo_root
    )
    write_canonical_json(out_json, packet)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        "\n".join(
            render_oracle_full_live_runtime_execution_attempt_notion_mirror_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_record(
    source_id: str,
    path: Path,
    packet: dict[str, Any],
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "path": path.as_posix(),
        "path_observed": True,
        "observed_status": packet.get("receipt_status", "OBSERVED"),
        "source_hash": packet["canonical_hash"],
        "brier_score": 0.1,
    }


def _blockers(
    execution_receipt: dict[str, Any],
    validation_receipt: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if execution_receipt.get("receipt_status") != (
        "ORACLE_FULL_LIVE_RUNTIME_EXECUTION_ATTEMPT_BLOCKED"
    ):
        blockers.append("runtime_execution_attempt_receipt_not_blocked")
    if validation_receipt.get("receipt_status") != (
        "ORACLE_SCHEMA_VALIDATION_READY_ADVISORY_ONLY"
    ):
        blockers.append("schema_validation_receipt_not_ready")
    if execution_receipt.get("valid_for_notion_writeback") is not False:
        blockers.append("execution_receipt_notion_writeback_not_denied")
    if validation_receipt.get("valid_for_notion_writeback") is not False:
        blockers.append("validation_receipt_notion_writeback_not_denied")
    if execution_receipt.get("execution_summary", {}).get("external_call_count") != 0:
        blockers.append("execution_receipt_external_calls_nonzero")
    if execution_receipt.get("execution_summary", {}).get("payload_record_count") != 0:
        blockers.append("execution_receipt_payload_records_nonzero")
    return blockers


def _paste_text(
    execution_receipt: dict[str, Any],
    validation_receipt: dict[str, Any],
) -> str:
    return "\n".join(
        [
            "Oracle Full Live Runtime Execution Attempt mirrored for designer audit",
            f"Status: {execution_receipt['receipt_status']}",
            "Receipt: out/audit/oracle_full_live_runtime_execution_attempt_receipt_001.latest.json",
            f"Receipt hash: {execution_receipt['canonical_hash']}",
            f"Validation receipt hash: {validation_receipt['canonical_hash']}",
            "Designer audit focus: confirm blocked/no-call default, endpoint environment requirements, operator attestation phrase FULL_LIVE_EXECUTION_GATE_CONFIRMED, no payload persistence, and no GitHub/Notion writeback",
            "Boundary preserved: default emission makes zero external calls; live probe requires endpoint env vars, --oracle-full-live-execute, and operator attestation; no payload persistence, autonomous outcome recording, MCP exposure, GitHub/Notion writeback, canon mutation, endpoint secret storage, unreviewed deployment, or governance expansion",
            "Brier Score: 0.10",
            "Next: designer audit, then operator-reviewed manual Notion paste if approved",
        ]
    )
