from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageNotionMappingScopeResolutionRecord.v1"
REQUEST_PATH = Path("out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.json")
JSON_PATH = Path("out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.json")
MD_PATH = Path("out/operator_review/abx_artifact_lineage_notion_mapping_scope_resolution_record_001.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sync_output_families(root: Path) -> list[str]:
    families: set[str] = set()
    for suffix in (".json", ".md"):
        for path in (root / "out" / "sync").rglob(f"*{suffix}"):
            rel = str(path.relative_to(root)).replace("\\", "/")
            if "/latest." in rel:
                families.add(str(Path(rel).parent).replace("\\", "/"))
    return sorted(families)


def build_abx_artifact_lineage_notion_mapping_scope_resolution_record(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_PATH)
    impacted_outputs = _sync_output_families(root)
    source_request_ready = (
        request.get("schema_version") == "AbxArtifactLineageNotionMappingEvidenceRequest.v1"
        and request.get("status") == "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_HELD"
        and request.get("notion_writeback_allowed") is False
        and request.get("notion_completeness_claim_allowed") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_SCOPE_RESOLUTION_RECORD_ACCEPTED"
        if source_request_ready
        else "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_SCOPE_RESOLUTION_RECORD_BLOCKED",
        "record_id": "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_SCOPE_RESOLUTION_RECORD_001",
        "record_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_SCOPE_RESOLUTION_RECORD_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "scope_resolution_record_only": True,
        "source_request": {
            "path": str(REQUEST_PATH),
            "request_hash": str(request.get("request_hash", "NOT_COMPUTABLE")),
            "source_status": str(request.get("status", "NOT_COMPUTABLE")),
            "source_request_ready": source_request_ready,
        },
        "operator_instruction_source": "current_codex_thread_user_request_resolve_blockers",
        "resolution_scope": "TRACEABILITY_AUDIT_NOTION_MAPPING_SCOPE_ONLY",
        "resolution_decision": "EXCLUDE_SYNC_OUTPUT_FAMILIES_FROM_MANDATORY_NOTION_SURFACE_MAPPING",
        "resolution_rationale": (
            "The impacted out/sync output families are deterministic repo-generated advisory artifacts. "
            "This record resolves the traceability-audit blocker by explicit scope disposition only; "
            "it does not claim Notion workspace completeness and does not perform or authorize writeback."
        ),
        "resolved_finding_id": "detect_generated_outputs_with_no_notion_surface",
        "resolved_output_count": len(impacted_outputs),
        "resolved_outputs": impacted_outputs,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "notion_completeness_claim_allowed": False,
        "external_notion_evidence_imported": False,
        "execution_authority": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "traceability_audit_consumption_allowed": source_request_ready,
        "blocked_actions": [
            "NOTION_WRITEBACK",
            "GITHUB_WRITEBACK",
            "NOTION_WORKSPACE_COMPLETENESS_CLAIM",
            "CANON_MUTATION",
            "RUNTIME_MUTATION",
            "QUEUE_MUTATION",
            "SCHEDULER_MUTATION",
        ],
        "acceptance_gates": [
            {
                "gate_id": "source_request_ready",
                "status": "PASS" if source_request_ready else "FAIL",
                "required_before": "traceability audit can consume this scope resolution",
            },
            {
                "gate_id": "no_live_writeback",
                "status": "PASS",
                "required_before": "record remains audit-only",
            },
            {
                "gate_id": "no_notion_completeness_claim",
                "status": "PASS",
                "required_before": "record remains a scope disposition rather than workspace proof",
            },
        ],
        "downstream_status": "READY_FOR_TRACEABILITY_AUDIT_REPLAY" if source_request_ready else "NOT_COMPUTABLE",
        "recommended_next_lane": "ABX_ARTIFACT_LINEAGE_REGISTRY_TRACEABILITY_AUDIT_REPLAY",
    }
    packet["record_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "record_hash"})
    return packet


def render_abx_artifact_lineage_notion_mapping_scope_resolution_record_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Notion Mapping Scope Resolution Record",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `record_id`: `{packet['record_id']}`",
        f"- `resolution_scope`: `{packet['resolution_scope']}`",
        f"- `resolution_decision`: `{packet['resolution_decision']}`",
        f"- `resolved_output_count`: `{packet['resolved_output_count']}`",
        f"- `notion_writeback_allowed`: `{packet['notion_writeback_allowed']}`",
        f"- `notion_completeness_claim_allowed`: `{packet['notion_completeness_claim_allowed']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        "",
        "## Resolved Outputs",
        "",
    ]
    for item in packet["resolved_outputs"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_notion_mapping_scope_resolution_record(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_notion_mapping_scope_resolution_record(root)
    write_canonical_json(target_root / JSON_PATH, packet)
    _write_markdown(
        target_root / MD_PATH,
        render_abx_artifact_lineage_notion_mapping_scope_resolution_record_markdown(packet),
    )
    return packet
