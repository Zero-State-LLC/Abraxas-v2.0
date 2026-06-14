from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_intelligence_spine_phase1_operator_evidence_packet import (
    OUT_JSON as SOURCE_EVIDENCE_PACKET_JSON,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenPhase1OperatorReviewRequest.v1"
REQUEST_JSON_PATH = Path(
    "out/operator_review/abx_codegen_phase1_operator_review_request_001.latest.json"
)
REQUEST_MD_PATH = REQUEST_JSON_PATH.with_suffix(".md")

EXPECTED_EVIDENCE_PACKET_STATUS = "ABX_CODEGEN_PHASE1_OPERATOR_EVIDENCE_PACKET_HELD_FOR_OPERATOR"

DECISION_OPTIONS = [
    "HOLD_FOR_OPERATOR_REVIEW",
    "APPROVE_PHASE1_IMPLEMENTATION_REVIEW_ONLY",
    "REQUEST_ADDITIONAL_EVIDENCE",
    "REJECT_PHASE1_IMPLEMENTATION_SCOPE",
]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _authority_locks() -> dict[str, bool]:
    return {
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
    }


def build_abx_codegen_phase1_operator_review_request(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    evidence = _read_json(root / SOURCE_EVIDENCE_PACKET_JSON)
    evidence_ready = (
        evidence.get("artifact_type")
        == "AbxCodegenIntelligenceSpinePhase1OperatorEvidencePacket.v1"
        and evidence.get("phase1_operator_evidence_packet_status")
        == EXPECTED_EVIDENCE_PACKET_STATUS
        and evidence.get("recommended_next_lane") == "NOT_COMPUTABLE"
        and evidence.get("safe_to_auto_continue") is False
        and evidence.get("execution_authority") is False
        and evidence.get("valid_for_implementation") is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "ABX_CODEGEN_PHASE1_OPERATOR_REVIEW_REQUEST_HELD"
            if evidence_ready
            else "ABX_CODEGEN_PHASE1_OPERATOR_REVIEW_REQUEST_BLOCKED"
        ),
        "request_id": "abx_codegen_phase1_operator_review_request_001",
        "request_hash": "",
        "decision_scope": "PHASE1_CODEGEN_IMPLEMENTATION_REVIEW_REQUIRED",
        "decision_question": (
            "Should the Phase 1 Codegen harness implementation scope remain held, "
            "be rejected, request more evidence, or be approved for review-only "
            "progression to a separate authorization-record lane?"
        ),
        "source_evidence_packet_path": SOURCE_EVIDENCE_PACKET_JSON,
        "source_evidence_packet_hash": str(evidence.get("packet_hash", "NOT_COMPUTABLE")),
        "evidence_packet_ready_for_review": evidence_ready,
        "decision_options": DECISION_OPTIONS,
        "recommended_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "required_operator_review_items": [
            "confirm Phase 1 scope remains skeleton and validation-only",
            "confirm no shadow replay execution is authorized",
            "confirm no operator attestation is present in the evidence packet",
            "confirm no authorization record is created by this request",
            "confirm any approval would require a separate authorization-record lane",
            "confirm no Notion or GitHub writeback authority is granted",
        ],
        "blocked_actions": [
            "CODEGEN_PHASE1_IMPLEMENTATION",
            "CORE_CODEGEN_SHADOW_REPLAY_HARNESS_CREATION",
            "SHADOW_REPLAY_EXECUTION",
            "SHADOW_IMPROVEMENT_RECEIPT_CREATION",
            "OPERATOR_DECISION_RECORD_CREATION",
            "OPERATOR_ATTESTATION_CREATION",
            "AUTHORIZATION_RECORD_CREATION",
            "PROMOTION_ROUTING",
            "CANON_OR_RUNTIME_MUTATION",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
        ],
        "authority_locks": _authority_locks(),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
    }
    packet["request_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "request_hash"}
    )
    return packet


def render_abx_codegen_phase1_operator_review_request_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Phase 1 Operator Review Request",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `recommended_decision`: `{packet['recommended_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `implementation_authorized`: `{packet['implementation_authorized']}`",
        f"- `execution_authority`: `{packet['execution_authority']}`",
        f"- `valid_for_implementation`: `{packet['valid_for_implementation']}`",
        "",
        "## Decision Options",
        "",
    ]
    for item in packet["decision_options"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Review Items", ""])
    for item in packet["required_operator_review_items"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Blocked Actions", ""])
    for item in packet["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_codegen_phase1_operator_review_request(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_phase1_operator_review_request(root)
    write_canonical_json(target_root / REQUEST_JSON_PATH, packet)
    _write_markdown(
        target_root / REQUEST_MD_PATH,
        render_abx_codegen_phase1_operator_review_request_markdown(packet),
    )
    return packet
