from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_module_surface_plan import (
    OUT_JSON as SOURCE_MODULE_SURFACE_PLAN_JSON,
)
from core.abx_codegen_intelligence_spine_phase1_code_detail_plan import (
    OUT_JSON as SOURCE_PHASE1_CODE_DETAIL_PLAN_JSON,
)
from core.abx_codegen_intelligence_spine_phase1_implementation_boundary_review import (
    OUT_JSON as SOURCE_PHASE1_BOUNDARY_REVIEW_JSON,
)
from core.abx_codegen_intelligence_spine_phase1_operator_authorization_request_plan import (
    OUT_JSON as SOURCE_OPERATOR_REQUEST_PLAN_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpinePhase1OperatorEvidencePacket.v1"
PACKET_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_PHASE1_OPERATOR_EVIDENCE_PACKET_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_phase1_operator_evidence_packet_001.latest.md"

EXPECTED_REQUEST_PLAN_STATUS = (
    "ABX_CODEGEN_PHASE1_OPERATOR_AUTHORIZATION_REQUEST_PLAN_HELD_FOR_OPERATOR"
)


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


def _evidence_item(
    *,
    root: Path,
    evidence_id: str,
    path: str,
    purpose: str,
    source_ready: bool,
) -> dict[str, Any]:
    target = root / path
    observed = target.exists()
    return {
        "evidence_id": evidence_id,
        "path": path,
        "hash": _sha256(target),
        "purpose": purpose,
        "observed": observed,
        "evidence_status": (
            "OBSERVED_FOR_OPERATOR_REVIEW"
            if source_ready and observed
            else "NOT_COMPUTABLE"
        ),
        "grants_authority": False,
    }


def _operator_review_checklist(source_ready: bool) -> list[dict[str, Any]]:
    status = "PENDING_HUMAN_OPERATOR_REVIEW" if source_ready else "NOT_COMPUTABLE"
    items = [
        "confirm_phase1_scope_is_limited_to_skeleton_and_validation_only",
        "confirm_no_shadow_replay_execution_is_authorized_by_this_packet",
        "confirm_no_operator_attestation_is_present_in_this_packet",
        "confirm_no_authorization_record_is_created_by_this_packet",
        "confirm_future_decision_requires_human_rationale",
        "confirm_any_approval_requires_separate_authorization_record",
    ]
    return [
        {
            "check": item,
            "check_status": status,
            "satisfied_by_packet": False,
            "requires_human_review": True,
        }
        for item in items
    ]


def _explicit_denials() -> list[dict[str, Any]]:
    denied = [
        "operator_decision_record_creation",
        "operator_attestation",
        "authorization_record_creation",
        "phase1_implementation",
        "core_codegen_shadow_replay_harness_creation",
        "shadow_replay_execution",
        "shadow_improvement_receipt_creation",
        "artifact_registry_registration",
        "promotion_routing",
        "notion_writeback",
        "github_writeback",
    ]
    return [{"action": action, "authorized": False} for action in denied]


def build_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
    *,
    repo_root: str | Path,
    source_operator_authorization_request_plan_path: str
    | Path = SOURCE_OPERATOR_REQUEST_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_operator_authorization_request_plan_path).as_posix()
    source = _read_json(root / source_operator_authorization_request_plan_path)
    source_ready = (
        source.get("artifact_type")
        == "AbxCodegenIntelligenceSpinePhase1OperatorAuthorizationRequestPlan.v1"
        and source.get("phase1_operator_authorization_request_plan_status")
        == EXPECTED_REQUEST_PLAN_STATUS
        and source.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and source.get("safe_to_auto_continue") is False
        and source.get("execution_authority") is False
        and source.get("valid_for_implementation") is False
    )

    evidence_specs = [
        (
            "phase1_operator_authorization_request_plan",
            Path(source_operator_authorization_request_plan_path).as_posix(),
            "operator request scope and required decision fields",
        ),
        (
            "phase1_implementation_boundary_review",
            SOURCE_PHASE1_BOUNDARY_REVIEW_JSON,
            "repo authority boundary and blocked Phase 1 actions",
        ),
        (
            "phase1_code_detail_plan",
            SOURCE_PHASE1_CODE_DETAIL_PLAN_JSON,
            "Notion-derived Phase 1 code outline converted to planning artifact",
        ),
        (
            "module_surface_plan",
            SOURCE_MODULE_SURFACE_PLAN_JSON,
            "planned module surface and core/codegen namespace denial",
        ),
    ]
    evidence_items = [
        _evidence_item(
            root=root,
            evidence_id=evidence_id,
            path=path,
            purpose=purpose,
            source_ready=source_ready,
        )
        for evidence_id, path, purpose in evidence_specs
    ]
    missing_evidence = [
        item["evidence_id"] for item in evidence_items if item["observed"] is not True
    ]
    packet_ready = source_ready and not missing_evidence

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "packet_id": PACKET_ID,
        "phase1_operator_evidence_packet_status": (
            "ABX_CODEGEN_PHASE1_OPERATOR_EVIDENCE_PACKET_HELD_FOR_OPERATOR"
            if packet_ready
            else "NOT_COMPUTABLE"
        ),
        "source_operator_authorization_request_plan": {
            "path": source_path,
            "hash": _sha256(root / source_operator_authorization_request_plan_path),
            "phase1_operator_authorization_request_plan_status": str(
                source.get(
                    "phase1_operator_authorization_request_plan_status",
                    "NOT_COMPUTABLE",
                )
            ),
            "source_ready": source_ready,
        },
        "evidence_items": evidence_items,
        "operator_review_checklist": _operator_review_checklist(packet_ready),
        "missing_evidence": missing_evidence,
        "explicit_denials": _explicit_denials(),
        "recommended_next_lane": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": {
            "artifact_registry_registration": False,
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


def write_abx_codegen_intelligence_spine_phase1_operator_evidence_packet(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_abx_codegen_intelligence_spine_phase1_operator_evidence_packet_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Intelligence Spine Phase 1 Operator Evidence Packet",
        "",
        f"- packet_id: {packet['packet_id']}",
        f"- phase1_operator_evidence_packet_status: {packet['phase1_operator_evidence_packet_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        "",
        "## Evidence Items",
    ]
    for item in packet.get("evidence_items", []):
        if isinstance(item, Mapping):
            lines.append(
                f"- {item['evidence_id']}: {item['evidence_status']} "
                f"(observed={item['observed']})"
            )
    lines.extend(["", "## Operator Review Checklist"])
    for item in packet.get("operator_review_checklist", []):
        if isinstance(item, Mapping):
            lines.append(f"- {item['check']}: {item['check_status']}")
    lines.extend(["", "## Explicit Denials"])
    for denial in packet.get("explicit_denials", []):
        if isinstance(denial, Mapping):
            lines.append(f"- {denial['action']}: authorized={denial['authorized']}")
    return lines


def write_abx_codegen_intelligence_spine_phase1_operator_evidence_packet_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(
            render_abx_codegen_intelligence_spine_phase1_operator_evidence_packet_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
