from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_phase1_implementation_boundary_review import (
    OUT_JSON as SOURCE_PHASE1_BOUNDARY_REVIEW_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpinePhase1OperatorAuthorizationRequestPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_PHASE1_OPERATOR_AUTHORIZATION_REQUEST_PLAN_001"
OUT_JSON = (
    "out/audit/"
    "abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_001.latest.json"
)
OUT_MD = (
    "out/audit/"
    "abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_001.latest.md"
)

EXPECTED_BOUNDARY_STATUS = (
    "ABX_CODEGEN_PHASE1_IMPLEMENTATION_BOUNDARY_REVIEW_HELD_FOR_OPERATOR"
)

NOTION_OPERATOR_SOURCES = [
    {
        "title": "ABX_CODEGEN_INTELLIGENCE_SPINE_001 - Governed Recursive Self-Improvement Spec",
        "page_id": "37d3e8ba-2f5c-816d-8ccc-c0b46b9a2760",
        "observed_as_of": "2026-06-12",
        "source_role": "requires_operator_decision_records_before_implementation",
    },
    {
        "title": "Operator Decision Record Templates - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-819a-9f0b-e6eb1b53b0f5",
        "observed_as_of": "2026-06-12",
        "source_role": "standard_operator_decision_shape",
    },
    {
        "title": "Meta-Gate Authorization Record Template - Codegen Intelligence Spine",
        "page_id": "37d3e8ba-2f5c-816c-a655-e99aaeb3652d",
        "observed_as_of": "2026-06-12",
        "source_role": "self_improvement_authorization_constraints",
    },
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


def _required_fields(source_ready: bool) -> list[dict[str, Any]]:
    status = "REQUIRED_FOR_OPERATOR_REVIEW" if source_ready else "NOT_COMPUTABLE"
    rows = [
        ("record_id", "deterministic operator request identifier"),
        ("decision_type", "Phase 1 implementation authorization request"),
        ("target_surface", "ABX_CODEGEN_INTELLIGENCE_SPINE_001"),
        ("target_module", "core/codegen_shadow_replay_harness.py"),
        ("requested_scope", "Phase 1 skeleton and validation-only harness scope"),
        ("explicit_non_authority", "execution, promotion, mutation, and writeback denied"),
        ("operator_decision", "APPROVE_PHASE1_IMPLEMENTATION, REJECT, DEFER, or REQUEST_REFINEMENT"),
        ("human_rationale", "operator-written rationale required"),
        ("operator_attestation", "human identity and confirmation required"),
    ]
    return [
        {"field": field, "requirement": requirement, "field_status": status}
        for field, requirement in rows
    ]


def _evidence_bundle(source_ready: bool) -> list[dict[str, Any]]:
    status = "REQUIRED_FOR_OPERATOR_REVIEW" if source_ready else "NOT_COMPUTABLE"
    rows = [
        (
            "phase1_boundary_review",
            "out/audit/abx_codegen_intelligence_spine_phase1_implementation_boundary_review_001.latest.json",
        ),
        (
            "phase1_code_detail_plan",
            "out/audit/abx_codegen_intelligence_spine_phase1_code_detail_plan_001.latest.json",
        ),
        (
            "module_surface_plan",
            "out/audit/abx_codegen_intelligence_spine_module_surface_plan_001.latest.json",
        ),
        (
            "operator_decision_template",
            "Notion Operator Decision Record Templates - Codegen Intelligence Spine",
        ),
    ]
    return [
        {"evidence": evidence, "source": source, "evidence_status": status}
        for evidence, source in rows
    ]


def _allowed_decisions(source_ready: bool) -> list[dict[str, Any]]:
    status = "REQUEST_PLAN_ONLY" if source_ready else "NOT_COMPUTABLE"
    return [
        {
            "decision": "APPROVE_PHASE1_IMPLEMENTATION",
            "decision_status": status,
            "effect": "would require a separate authorization record before implementation",
            "grants_authority_in_this_artifact": False,
        },
        {
            "decision": "REJECT",
            "decision_status": status,
            "effect": "keeps Phase 1 implementation blocked",
            "grants_authority_in_this_artifact": False,
        },
        {
            "decision": "DEFER",
            "decision_status": status,
            "effect": "holds for more evidence without authorization",
            "grants_authority_in_this_artifact": False,
        },
        {
            "decision": "REQUEST_REFINEMENT",
            "decision_status": status,
            "effect": "routes back to advisory planning refinement",
            "grants_authority_in_this_artifact": False,
        },
    ]


def _explicit_denials() -> list[dict[str, Any]]:
    denied = [
        "operator_decision_record_creation",
        "operator_attestation",
        "authorization_record_creation",
        "phase1_implementation",
        "core_codegen_shadow_replay_harness_creation",
        "shadow_replay_execution",
        "receipt_creation",
        "promotion_routing",
        "notion_writeback",
        "github_writeback",
    ]
    return [{"action": action, "authorized": False} for action in denied]


def build_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
    *,
    repo_root: str | Path,
    source_phase1_boundary_review_path: str
    | Path = SOURCE_PHASE1_BOUNDARY_REVIEW_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_phase1_boundary_review_path).as_posix()
    source = _read_json(root / source_phase1_boundary_review_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpinePhase1ImplementationBoundaryReview.v1"
        and source.get("phase1_implementation_boundary_review_status")
        == EXPECTED_BOUNDARY_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "phase1_operator_authorization_request_plan_status": (
            "ABX_CODEGEN_PHASE1_OPERATOR_AUTHORIZATION_REQUEST_PLAN_HELD_FOR_OPERATOR"
            if source_ready
            else "NOT_COMPUTABLE"
        ),
        "source_phase1_boundary_review": {
            "path": source_path,
            "hash": _sha256(root / source_phase1_boundary_review_path),
            "phase1_implementation_boundary_review_status": str(
                source.get(
                    "phase1_implementation_boundary_review_status",
                    "NOT_COMPUTABLE",
                )
            ),
            "source_ready": source_ready,
        },
        "notion_operator_sources": NOTION_OPERATOR_SOURCES,
        "authorization_request_scope": {
            "request_type": "phase1_implementation_authorization_request",
            "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
            "target_module": "core/codegen_shadow_replay_harness.py",
            "requested_scope": "Phase 1 skeleton, proposal validation, deterministic config planning, and receipt-shape preparation",
            "request_creates_authorization": False,
            "request_creates_operator_decision_record": False,
            "operator_attestation_present": False,
        },
        "required_operator_decision_fields": _required_fields(source_ready),
        "required_evidence_bundle": _evidence_bundle(source_ready),
        "allowed_operator_decisions": _allowed_decisions(source_ready),
        "explicit_denials": _explicit_denials(),
        "implementation_blockers": [
            "phase1_boundary_review_held_for_operator",
            "operator_decision_record_missing",
            "operator_attestation_missing",
            "authorization_record_missing",
            "phase1_implementation_authorization_missing",
            "core_codegen_shadow_replay_harness_creation_denied",
            "shadow_replay_execution_denied",
            "receipt_creation_denied",
            "notion_writeback_denied",
            "github_writeback_denied",
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
            "authorization_record_creation": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "core_harness_file_creation": False,
            "execution": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation_authorization": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "operator_decision_record_creation": False,
            "promotion_to_canary": False,
            "receipt_creation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "shadow_replay_execution": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Phase 1 Operator Authorization Request Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        "- phase1_operator_authorization_request_plan_status: "
        f"{packet['phase1_operator_authorization_request_plan_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Required Evidence",
    ]
    for evidence in packet.get("required_evidence_bundle", []):
        if isinstance(evidence, Mapping):
            lines.append(f"- {evidence['evidence']}: {evidence['evidence_status']}")
    lines.extend(["", "## Allowed Operator Decisions"])
    for decision in packet.get("allowed_operator_decisions", []):
        if isinstance(decision, Mapping):
            lines.append(
                f"- {decision['decision']}: "
                f"grants_authority={decision['grants_authority_in_this_artifact']}"
            )
    lines.extend(["", "## Explicit Denials"])
    for denial in packet.get("explicit_denials", []):
        if isinstance(denial, Mapping):
            lines.append(f"- {denial['action']}: authorized={denial['authorized']}")
    return lines


def write_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
