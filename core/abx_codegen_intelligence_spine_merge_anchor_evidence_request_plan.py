from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_merge_anchor_coverage_plan import (
    OUT_JSON as SOURCE_MERGE_ANCHOR_COVERAGE_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineMergeAnchorEvidenceRequestPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_MERGE_ANCHOR_EVIDENCE_REQUEST_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_001.latest.md"
)

EXPECTED_COVERAGE_STATUS = "ABX_CODEGEN_MERGE_ANCHOR_COVERAGE_PLAN_HELD_FOR_OPERATOR"

NORMALIZATION_REQUIREMENTS = [
    "notion_page_id_or_url",
    "source_title",
    "source_role",
    "governance_posture",
    "authority_boundaries",
    "merge_rules",
    "repo_relevance_summary",
    "implementation_constraints",
    "evidence_hash_policy",
    "operator_review_requirement",
]


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _row_status(source_ready: bool) -> str:
    if source_ready:
        return "MERGE_ANCHOR_EVIDENCE_REQUESTED_HELD_FOR_OPERATOR"
    return "NOT_COMPUTABLE"


def build_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
    *,
    repo_root: str | Path,
    source_merge_anchor_coverage_plan_path: str
    | Path = SOURCE_MERGE_ANCHOR_COVERAGE_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_merge_anchor_coverage_plan_path).as_posix()
    source = _read_json(root / source_merge_anchor_coverage_plan_path)

    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpineMergeAnchorCoveragePlan.v1"
        and source.get("merge_anchor_coverage_plan_status") == EXPECTED_COVERAGE_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )
    status = _row_status(source_ready)
    merge_anchors = source.get("merge_anchors", [])
    notion_only = [
        anchor
        for anchor in merge_anchors
        if isinstance(anchor, Mapping)
        and anchor.get("coverage_status") == "MERGE_ANCHOR_NOTION_ONLY_HELD_FOR_OPERATOR"
    ]

    requests = [
        {
            "anchor_id": str(anchor.get("anchor_id", "NOT_COMPUTABLE")),
            "anchor_title": str(anchor.get("anchor_title", "NOT_COMPUTABLE")),
            "anchor_kind": str(anchor.get("anchor_kind", "NOT_COMPUTABLE")),
            "request_status": status,
            "requested_evidence_fields": NORMALIZATION_REQUIREMENTS,
            "repo_file_creation_authorized": False,
            "notion_fetch_required": True,
            "notion_writeback_authorized": False,
            "implementation_unblocked_by_request": False,
        }
        for anchor in notion_only
    ]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "merge_anchor_evidence_request_plan_status": (
            "ABX_CODEGEN_MERGE_ANCHOR_EVIDENCE_REQUEST_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_merge_anchor_coverage_plan": {
            "path": source_path,
            "hash": _sha256(root / source_merge_anchor_coverage_plan_path),
            "merge_anchor_coverage_plan_status": str(
                source.get("merge_anchor_coverage_plan_status", "NOT_COMPUTABLE")
            ),
            "source_ready": source_ready,
        },
        "notion_only_anchor_requests": requests,
        "evidence_normalization_requirements": [
            {
                "requirement": requirement,
                "requirement_status": status,
                "normalization_authorized": False,
            }
            for requirement in NORMALIZATION_REQUIREMENTS
        ],
        "request_summary": {
            "source_anchor_count": int(
                source.get("coverage_summary", {}).get("anchor_count", 0)
                if isinstance(source.get("coverage_summary"), Mapping)
                else 0
            ),
            "notion_only_anchor_count": len(requests),
            "request_ready_for_operator": source_ready,
            "all_requested_evidence_present": False,
            "implementation_unblocked": False,
            "reason": (
                "notion_only_merge_anchors_require_fetch_and_normalization_before_"
                "implementation_preconditions_can_be_reassessed"
            ),
        },
        "blocked_actions": [
            "notion_writeback",
            "notion_anchor_mutation",
            "repo_anchor_file_creation",
            "merge_anchor_promotion",
            "implementation_unblock",
            "contracts_codegen_directory_creation",
            "core_codegen_directory_creation",
            "schema_creation",
            "module_creation",
            "implementation_prompt_emission",
            "patch_application",
            "runtime_mutation",
            "canon_mutation",
            "github_writeback",
        ],
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "anchor_file_creation": False,
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "contracts_codegen_directory_creation": False,
            "core_codegen_directory_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation_prompt_emission": False,
            "implementation_unblock": False,
            "merge_anchor_mutation": False,
            "merge_anchor_promotion": False,
            "module_creation": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "operator_decision_record_creation": False,
            "patch_application": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_creation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Merge Anchor Evidence Request Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- merge_anchor_evidence_request_plan_status: "
        f"{packet['merge_anchor_evidence_request_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Notion-Only Anchor Requests",
    ]
    for request in packet.get("notion_only_anchor_requests", []):
        if isinstance(request, Mapping):
            lines.append(
                f"- {request['anchor_id']}: {request['request_status']} "
                f"(notion_fetch_required={request['notion_fetch_required']})"
            )
    lines.extend(["", "## Normalization Requirements"])
    for requirement in packet.get("evidence_normalization_requirements", []):
        if isinstance(requirement, Mapping):
            lines.append(
                f"- {requirement['requirement']}: {requirement['requirement_status']} "
                f"(normalization_authorized={requirement['normalization_authorized']})"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    return lines


def write_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_merge_anchor_evidence_request_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
