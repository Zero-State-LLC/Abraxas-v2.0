from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageNotionMappingEvidenceRequest.v1"
TRACEABILITY_AUDIT_PATH = Path("out/sync/abx_artifact_lineage_registry_traceability_audit/latest.json")
JSON_PATH = Path("out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.json")
MD_PATH = Path("out/operator_review/abx_artifact_lineage_notion_mapping_evidence_request_001.latest.md")

BLOCKED_ACTIONS = [
    "NOTION_WRITEBACK",
    "GITHUB_WRITEBACK",
    "NOTION_MAPPING_COMPLETENESS_ASSERTION",
    "CANON_MUTATION",
    "RUNTIME_MUTATION",
    "QUEUE_MUTATION",
    "SCHEDULER_MUTATION",
]

REQUIRED_EVIDENCE_FIELDS = [
    "notion_page_id_or_url",
    "notion_surface_title",
    "mapped_repo_output_family",
    "evidence_capture_method",
    "operator_or_import_receipt_id",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _notion_gap_finding(audit: Mapping[str, Any]) -> dict[str, Any]:
    for finding in audit.get("notion_mapping_findings", []):
        if finding.get("finding_id") == "detect_generated_outputs_with_no_notion_surface":
            return dict(finding)
    return {
        "finding_id": "detect_generated_outputs_with_no_notion_surface",
        "status": "NOT_COMPUTABLE",
        "checked_count": 0,
        "impacted_count": 0,
        "sample_impacted": [],
        "reason": "repo-local evidence cannot prove Notion mapping completeness for generated sync outputs",
        "evidence_required": "deterministic repo-visible Notion mapping index or governed external evidence import",
    }


def build_abx_artifact_lineage_notion_mapping_evidence_request(source_root: str | Path = ".") -> dict[str, Any]:
    root = Path(source_root)
    audit = _read_json(root / TRACEABILITY_AUDIT_PATH)
    finding = _notion_gap_finding(audit)
    impacted_outputs = sorted(str(item) for item in finding.get("sample_impacted", []))
    impacted_count = int(finding.get("impacted_count", len(impacted_outputs)))
    source_audit_ready = (
        audit.get("artifact_type") == "AbxArtifactLineageRegistryTraceabilityAudit.v1"
        and finding.get("status") == "NOT_COMPUTABLE"
        and impacted_count > 0
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_HELD"
        if source_audit_ready
        else "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_BLOCKED",
        "artifact_id": "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_001",
        "request_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_REQUEST_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_request_only": True,
        "source_traceability_audit": {
            "path": str(TRACEABILITY_AUDIT_PATH),
            "packet_hash": str(audit.get("packet_hash", "NOT_COMPUTABLE")),
            "audit_id": str(audit.get("audit_id", "NOT_COMPUTABLE")),
            "source_audit_ready": source_audit_ready,
        },
        "request_scope": "NOTION_MAPPING_EVIDENCE_COLLECTION_ONLY",
        "target_finding_id": str(finding.get("finding_id", "detect_generated_outputs_with_no_notion_surface")),
        "target_status": str(finding.get("status", "NOT_COMPUTABLE")),
        "impacted_output_count": impacted_count,
        "impacted_outputs": impacted_outputs,
        "required_evidence": str(
            finding.get(
                "evidence_required",
                "deterministic repo-visible Notion mapping index or governed external evidence import",
            )
        ),
        "required_evidence_fields": list(REQUIRED_EVIDENCE_FIELDS),
        "accepted_evidence_routes": [
            "DETERMINISTIC_REPO_VISIBLE_NOTION_MAPPING_INDEX",
            "GOVERNED_EXTERNAL_EVIDENCE_IMPORT_RECEIPT",
        ],
        "rejected_evidence_routes": [
            "UNRECORDED_LIVE_NOTION_LOOKUP",
            "INFERRED_COMPLETENESS_FROM_OUTPUT_NAMES",
            "AUTOMATED_WRITEBACK_WITHOUT_OPERATOR_AUTHORIZATION",
        ],
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "notion_completeness_claim_allowed": False,
        "execution_authority": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_writeback_pr": False,
        "blocked_actions": list(BLOCKED_ACTIONS),
        "acceptance_gates": [
            {
                "gate_id": "repo_visible_mapping_index_or_import_receipt_required",
                "status": "PENDING_EVIDENCE",
                "required_before": "any Notion mapping completeness claim",
            },
            {
                "gate_id": "live_writeback_denied",
                "status": "DENIED",
                "required_before": "any Notion or GitHub writeback",
            },
            {
                "gate_id": "traceability_audit_replay_required",
                "status": "PENDING_AFTER_EVIDENCE",
                "required_before": "clearing the Notion mapping NOT_COMPUTABLE finding",
            },
        ],
        "recommended_next_action": (
            "collect a deterministic repo-visible Notion mapping index or governed external evidence import receipt "
            "for the impacted output families, then rerun the artifact-lineage traceability audit"
        ),
        "recommended_next_lane": "ABX_ARTIFACT_LINEAGE_NOTION_MAPPING_EVIDENCE_COLLECTION_PLAN",
        "downstream_status": "HELD_FOR_EVIDENCE",
    }
    packet["request_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "request_hash"})
    return packet


def render_abx_artifact_lineage_notion_mapping_evidence_request_markdown(packet: Mapping[str, Any]) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Notion Mapping Evidence Request",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `artifact_id`: `{packet['artifact_id']}`",
        f"- `request_scope`: `{packet['request_scope']}`",
        f"- `impacted_output_count`: `{packet['impacted_output_count']}`",
        f"- `notion_writeback_allowed`: `{packet['notion_writeback_allowed']}`",
        f"- `notion_completeness_claim_allowed`: `{packet['notion_completeness_claim_allowed']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        "",
        "## Required Evidence Fields",
        "",
    ]
    for item in packet["required_evidence_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Impacted Outputs", ""])
    for item in packet["impacted_outputs"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_notion_mapping_evidence_request(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_notion_mapping_evidence_request(root)
    write_canonical_json(target_root / JSON_PATH, packet)
    _write_markdown(target_root / MD_PATH, render_abx_artifact_lineage_notion_mapping_evidence_request_markdown(packet))
    return packet
