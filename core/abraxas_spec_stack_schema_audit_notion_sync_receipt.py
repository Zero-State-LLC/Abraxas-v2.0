from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.abraxas_spec_stack_schema_audit_common import (
    NOT_COMPUTABLE,
    authority_locks,
    spec_stack_governance_envelope,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbraxasSpecStackSchemaAuditNotionSyncReceipt.v1"
RECEIPT_ID = "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_NOTION_SYNC_RECEIPT_001"
PLAN_DOC_PATH = "docs/audits/ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_IMPLEMENTATION_PLAN_001.md"
COMPOSITE_RECEIPT_PATH = "out/audit/abraxas_spec_stack_schema_audit_receipt_001.latest.json"
READY_STATUS = "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_NOTION_SYNC_RECEIPT_READY"
BLOCKED_STATUS = "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_NOTION_SYNC_RECEIPT_BLOCKED"
OUT_PATH = Path("out/sync/abraxas_spec_stack_schema_audit_notion_sync_receipt_001.latest.json")

DOMAIN_AUDIT_PATHS: tuple[tuple[str, str], ...] = (
    ("belief_graph", "out/audit/abraxas_spec_stack_belief_graph_schema_audit_001.latest.json"),
    ("codegen_spine", "out/audit/abraxas_spec_stack_codegen_spine_schema_audit_001.latest.json"),
    ("ingest", "out/audit/abraxas_spec_stack_ingest_schema_audit_001.latest.json"),
    ("binding", "out/audit/abraxas_spec_stack_binding_schema_audit_001.latest.json"),
    (
        "situation_runtime",
        "out/audit/abraxas_spec_stack_situation_runtime_schema_audit_001.latest.json",
    ),
)

NOTION_SYNC_SURFACES: tuple[dict[str, str], ...] = (
    {
        "notion_surface_id": "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_IMPLEMENTATION_PLAN_001",
        "recommended_notion_action": "manual_copy_paste_update",
        "repo_doc_path": PLAN_DOC_PATH,
        "repo_truth": "Five-domain advisory schema audit lane emitted; gaps documented without repair",
    },
    {
        "notion_surface_id": "BELIEF_GRAPH_ENGINE_001",
        "recommended_notion_action": "manual_copy_paste_update",
        "repo_doc_path": "out/audit/abraxas_spec_stack_belief_graph_schema_audit_001.latest.json",
        "repo_truth": "Belief graph schema contracts observed; shadow binding gap documented",
    },
    {
        "notion_surface_id": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "recommended_notion_action": "manual_copy_paste_update",
        "repo_doc_path": "out/audit/abraxas_spec_stack_codegen_spine_schema_audit_001.latest.json",
        "repo_truth": "Codegen spine schema contracts observed; shadow binding cross-check recorded",
    },
    {
        "notion_surface_id": "GLOBAL_INGEST_ADAPTER_SPINE_001",
        "recommended_notion_action": "manual_copy_paste_update",
        "repo_doc_path": "out/audit/abraxas_spec_stack_ingest_schema_audit_001.latest.json",
        "repo_truth": "Ingest schema contracts and alignment surfaces observed; shadow binding gap documented",
    },
    {
        "notion_surface_id": "YGGDRASIL_BINDING_MATRIX",
        "recommended_notion_action": "manual_copy_paste_update",
        "repo_doc_path": "out/audit/abraxas_spec_stack_binding_schema_audit_001.latest.json",
        "repo_truth": "Binding matrix schemas observed; cross-spine shadow binding inventory emitted",
    },
    {
        "notion_surface_id": "SITUATION_RUNTIME_ENGINE_001",
        "recommended_notion_action": "manual_copy_paste_update",
        "repo_doc_path": "out/audit/abraxas_spec_stack_situation_runtime_schema_audit_001.latest.json",
        "repo_truth": "Situation runtime schema contracts observed; shadow binding gap documented",
    },
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _artifact_hash(path: Path) -> str:
    payload = _read_json(path)
    if payload is None:
        return NOT_COMPUTABLE
    for key in ("receipt_hash", "audit_hash", "sync_packet_hash"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return canonical_hash(payload)


def _source_record(root: Path, source_id: str, path: str) -> dict[str, Any]:
    target = root / path
    if path.endswith(".md"):
        observed = target.exists()
        return {
            "source_id": source_id,
            "path": path,
            "path_observed": observed,
            "observed_status": "OBSERVED" if observed else "MISSING",
            "source_hash": canonical_hash({"path": path}) if observed else NOT_COMPUTABLE,
        }
    payload = _read_json(target)
    return {
        "source_id": source_id,
        "path": path,
        "path_observed": payload is not None,
        "observed_status": str(payload.get("status", "NOT_OBSERVED")) if payload else "MISSING",
        "source_hash": _artifact_hash(target),
    }


def build_abraxas_spec_stack_schema_audit_notion_sync_receipt(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_records = [
        _source_record(root, "implementation_plan_doc", PLAN_DOC_PATH),
        _source_record(root, "composite_schema_audit_receipt", COMPOSITE_RECEIPT_PATH),
        *[
            _source_record(root, f"{domain}_schema_audit", path)
            for domain, path in DOMAIN_AUDIT_PATHS
        ],
    ]
    blockers = sorted(
        record["source_id"]
        for record in source_records
        if not record["path_observed"]
    )
    composite = _read_json(root / COMPOSITE_RECEIPT_PATH) or {}
    ready = not blockers and composite.get("status") == (
        "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_RECEIPT_EMITTED_ADVISORY_ONLY"
    )
    if composite and composite.get("status") != (
        "ABRAXAS_SPEC_STACK_SCHEMA_AUDIT_RECEIPT_EMITTED_ADVISORY_ONLY"
    ):
        blockers.append("composite_receipt_status_not_ready")
    blockers = sorted(set(blockers))
    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "receipt_id": RECEIPT_ID,
        "status": READY_STATUS if ready else BLOCKED_STATUS,
        **spec_stack_governance_envelope(),
        "projection_only": True,
        "non_authoritative": True,
        "manual_operator_copy_paste_only": True,
        "operator_review_posture": "ACTIVE",
        "implementation_plan_path": PLAN_DOC_PATH,
        "composite_receipt_path": COMPOSITE_RECEIPT_PATH,
        "composite_receipt_hash": _artifact_hash(root / COMPOSITE_RECEIPT_PATH),
        "source_artifact_records": source_records,
        "notion_sync_surfaces": list(NOTION_SYNC_SURFACES),
        "sync_findings": [
            {
                "finding_id": "spec_stack_schema_audit_lane_observed",
                "finding_status": "OBSERVED" if ready else "BLOCKED",
                "summary": (
                    "Repo-visible spec-stack schema audit receipt and five domain audits "
                    "are ready for manual Notion copy-paste handoff."
                ),
            },
            {
                "finding_id": "shadow_binding_gaps_not_repaired",
                "finding_status": "OBSERVED",
                "summary": (
                    "Missing shadow bindings remain documented gaps only; this receipt "
                    "does not authorize binding creation or promotion."
                ),
            },
        ],
        "packet_blockers": blockers,
        "recommended_next_action": (
            "copy notion_sync_surfaces into Notion manually after operator review"
            if ready
            else "restore missing spec-stack schema audit artifacts before Notion sync receipt emission"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "authority_locks": authority_locks(),
    }
    return {**base, "sync_receipt_hash": canonical_hash(base)}


def render_abraxas_spec_stack_schema_audit_notion_sync_receipt_markdown(
    packet: dict[str, Any],
) -> list[str]:
    lines = [
        "# Abraxas Spec Stack Schema Audit — Notion Sync Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- status: {packet['status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- manual_operator_copy_paste_only: {packet['manual_operator_copy_paste_only']}",
        "",
        "## Source Artifacts",
    ]
    for record in packet["source_artifact_records"]:
        lines.append(
            f"- {record['source_id']}: {record['observed_status']} ({record['path']})"
        )
    lines.extend(["", "## Notion Sync Surfaces"])
    for surface in packet["notion_sync_surfaces"]:
        lines.append(
            f"- {surface['notion_surface_id']}: {surface['recommended_notion_action']}"
        )
    lines.extend(["", "## Sync Findings"])
    for finding in packet["sync_findings"]:
        lines.append(f"- {finding['finding_id']}: {finding['summary']}")
    return lines


def write_abraxas_spec_stack_schema_audit_notion_sync_receipt(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(out_root) if out_root is not None else Path(repo_root)
    packet = build_abraxas_spec_stack_schema_audit_notion_sync_receipt(repo_root)
    out_json = root / OUT_PATH
    write_canonical_json(out_json, packet)
    out_md = out_json.with_suffix(".md")
    out_md.write_text(
        "\n".join(render_abraxas_spec_stack_schema_audit_notion_sync_receipt_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
