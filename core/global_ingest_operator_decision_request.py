from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "GlobalIngestOperatorDecisionRequest.v1"
JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.json")
MD_PATH = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.md")

GAP_BACKLOG_PATH = Path("out/operator_review/global_pipeline_gap_backlog_001.latest.json")
INGEST_ALIGNMENT_PLAN_PATH = Path("out/sync/global_ingest_adapter_spine_alignment_plan/latest.json")
NOTION_DECISION_BACKLOG_PATH = Path("out/sync/notion_operator_decision_backlog/latest.json")
COMPLETION_QUEUE_PATH = Path("out/sync/notion_spec_completion_queue/latest.json")
DOCTRINE_PROOF_PATH = Path("out/global_pipeline_doctrine_validation/latest.json")
ORACLE_IMPLEMENTATION_PLAN_PATH = Path("out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json")
ORACLE_CONFIDENCE_CALIBRATION_PLAN_PATH = Path("out/sync/oracle_confidence_calibration_plan/latest.json")

DECISION_OPTIONS = [
    "HOLD",
    "APPROVE_SEPARATE_IMPLEMENTATION_SPEC",
    "REQUEST_FRESH_NOTION_SPEC",
    "REJECT_IMPLEMENTATION_SPEC",
]


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_hash(data: Mapping[str, Any], field_name: str) -> str:
    payload = dict(data)
    payload.pop(field_name, None)
    return _sha256_text(_canonical_json(payload))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json_and_markdown(
    json_path: Path,
    md_path: Path,
    packet: Mapping[str, Any],
    markdown_lines: list[str],
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(_canonical_json(packet) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")


def _top_completion_item(completion_queue: Mapping[str, Any]) -> Mapping[str, Any]:
    items = completion_queue.get("completion_queue", [])
    if not items:
        raise ValueError("notion spec completion queue is empty")
    return items[0]


def _top_decision_backlog_item(decision_backlog: Mapping[str, Any]) -> Mapping[str, Any]:
    items = decision_backlog.get("decision_backlog", [])
    if not items:
        raise ValueError("notion operator decision backlog is empty")
    return items[0]


def _oracle_gap_item(gap_backlog: Mapping[str, Any]) -> Mapping[str, Any]:
    for item in gap_backlog.get("backlog_items", []):
        if item.get("pipeline_id") == "oracle_signal":
            return item
    raise ValueError("oracle_signal gap item not found in global pipeline gap backlog")


def _blocked_reasons_from_doctrine_proof(proof: Mapping[str, Any]) -> list[str]:
    blocked_reasons: list[str] = []
    if proof.get("authority_violation_count", 0) > 0:
        blocked_reasons.append("AUTHORITY_VIOLATION_PRESENT")
    if proof.get("failed_count", 0) > 0:
        blocked_reasons.append("FAILED_DOCTRINE_VALIDATION_PRESENT")
    if proof.get("repair_required_count", 0) > 0:
        blocked_reasons.append("REPAIR_REQUIRED_VALIDATION_PRESENT")
    if proof.get("missing_contract_count", 0) > 0:
        blocked_reasons.append("MISSING_GLOBAL_PIPELINE_CONTRACTS")
    if proof.get("missing_validation_count", 0) > 0:
        blocked_reasons.append("MISSING_GLOBAL_PIPELINE_VALIDATION_COVERAGE")
    if proof.get("legacy_contract_posture_count", 0) > 0:
        blocked_reasons.append("LEGACY_CONTRACT_POSTURE_PRESENT")
    return blocked_reasons


def build_global_ingest_operator_decision_request(source_root: str | Path = ".") -> dict[str, Any]:
    root = Path(source_root)
    gap_backlog = _read_json(root / GAP_BACKLOG_PATH)
    ingest_alignment_plan = _read_json(root / INGEST_ALIGNMENT_PLAN_PATH)
    notion_decision_backlog = _read_json(root / NOTION_DECISION_BACKLOG_PATH)
    completion_queue = _read_json(root / COMPLETION_QUEUE_PATH)
    doctrine_proof = _read_json(root / DOCTRINE_PROOF_PATH)
    implementation_plan = _read_json(root / ORACLE_IMPLEMENTATION_PLAN_PATH)
    calibration_plan = _read_json(root / ORACLE_CONFIDENCE_CALIBRATION_PLAN_PATH)

    oracle_gap_item = _oracle_gap_item(gap_backlog)
    decision_backlog_item = _top_decision_backlog_item(notion_decision_backlog)
    completion_item = _top_completion_item(completion_queue)
    doctrine_blocked_reasons = _blocked_reasons_from_doctrine_proof(doctrine_proof)
    implementation_plan_ready = (
        implementation_plan.get("artifact_type") == "OracleSignalIntakeBoundaryImplementationPlan.v1"
        and implementation_plan.get("plan_status") == "IMPLEMENTATION_PLAN_EMITTED_ADVISORY_ONLY"
        and implementation_plan.get("recommended_next_patch") == "PATCH-ABX-ORACLE-SIGNAL-INTAKE-BOUNDARY-001"
    )
    calibration_plan_ready = (
        calibration_plan.get("artifact_type") == "OracleConfidenceCalibrationPlan.v1"
        and calibration_plan.get("plan_status") == "PLAN_EMITTED_ADVISORY_ONLY"
        and calibration_plan.get("target_candidate_id") == "ORACLE_CONFIDENCE_CALIBRATION"
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "GLOBAL_INGEST_OPERATOR_DECISION_REQUEST_EMITTED",
        "request_id": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_REQUEST_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "forecast_weight_allowed": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "decision_scope": decision_backlog_item["decision_scope"],
        "decision_question": (
            "Should Abraxas approve a separate governed implementation spec for the "
            "Global Ingest Adapter Spine before any oracle_signal implementation work?"
        ),
        "target_pipeline_id": oracle_gap_item["pipeline_id"],
        "target_display_name": oracle_gap_item["display_name"],
        "notion_surface": decision_backlog_item["notion_surface"],
        "priority": oracle_gap_item["priority"],
        "queue_action": oracle_gap_item["queue_action"],
        "source_completion_status": oracle_gap_item["completion_status"],
        "source_match_strength": decision_backlog_item["source_match_strength"],
        "implementation_authorized": False,
        "spec_authoring_only_if_approved": True,
        "implementation_plan_ready": implementation_plan_ready,
        "calibration_plan_ready": calibration_plan_ready,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "decision_options": DECISION_OPTIONS,
        "recommended_decision": "HOLD",
        "recommended_next_action": (
            "review the fresh oracle intake boundary implementation plan, the Oracle confidence calibration plan, and collect explicit operator decision evidence before any implementation path can exist"
            if implementation_plan_ready and calibration_plan_ready
            else "review the fresh oracle intake boundary implementation plan and collect explicit operator decision evidence before any implementation path can exist"
            if implementation_plan_ready
            else oracle_gap_item["recommended_action"]
        ),
        "required_operator_actions": [
            "review_oracle_signal_research_intake_receipt",
            "review_oracle_signal_intake_boundary_implementation_plan",
            "review_oracle_confidence_calibration_plan",
            "review_global_ingest_operator_decision_evidence_collection_plan",
            "review_global_ingest_operator_decision_evidence_collection_dry_run",
            "review_global_ingest_operator_decision_evidence_collection_validation_plan",
            "review_global_ingest_operator_decision_evidence_collection_validation_dry_run",
            "review_global_ingest_operator_decision_evidence_collection_approval_plan",
            "prepare_global_ingest_operator_decision_record_template",
            "collect_global_ingest_operator_decision",
            "record_global_ingest_operator_decision",
        ],
        "required_inputs": list(oracle_gap_item["required_inputs"]),
        "required_evidence": list(completion_item["required_evidence"]),
        "observed_paths": list(oracle_gap_item["observed_paths"]),
        "missing_paths": list(oracle_gap_item["missing_paths"]),
        "blocked_actions": list(ingest_alignment_plan["blocked_actions"]),
        "acceptance_gates": list(ingest_alignment_plan["acceptance_gates"]),
        "decision_record_template_candidates": [
            "out/operator_review/global_ingest_operator_decision_record_template_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_record_template_001.latest.md",
        ],
        "decision_evidence_collection_plan_candidates": [
            "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.md",
        ],
        "decision_evidence_collection_dry_run_candidates": [
            "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_evidence_collection_dry_run_001.latest.md",
        ],
        "decision_evidence_collection_validation_plan_candidates": [
            "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_plan_001.latest.md",
        ],
        "decision_evidence_collection_validation_dry_run_candidates": [
            "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_dry_run_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_evidence_collection_validation_dry_run_001.latest.md",
        ],
        "decision_evidence_collection_approval_plan_candidates": [
            "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_evidence_collection_approval_plan_001.latest.md",
        ],
        "implementation_plan_candidates": [
            "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json",
            "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.md",
            "out/sync/oracle_confidence_calibration_plan/latest.json",
            "out/sync/oracle_confidence_calibration_plan/latest.md",
        ],
        "follow_on_actions_if_approved": [
            "AUTHOR_SEPARATE_IMPLEMENTATION_SPEC",
            "OPEN_SEPARATE_SPEC_PR",
        ],
        "follow_on_actions_if_held": [
            "REVIEW_DECISION_EVIDENCE_COLLECTION_APPROVAL_PLAN",
            "REVIEW_DECISION_EVIDENCE_COLLECTION_VALIDATION_DRY_RUN",
            "REVIEW_DECISION_EVIDENCE_COLLECTION_VALIDATION_PLAN",
            "REVIEW_DECISION_EVIDENCE_COLLECTION_DRY_RUN",
            "REVIEW_DECISION_EVIDENCE_COLLECTION_PLAN",
            "PREPARE_DECISION_RECORD_TEMPLATE",
            "REVIEW_ORACLE_CONFIDENCE_CALIBRATION_PLAN",
            "COLLECT_OPERATOR_DECISION_EVIDENCE",
            "MAINTAIN_GLOBAL_INGEST_HOLD",
        ],
        "follow_on_actions_if_rejected": [
            "MAINTAIN_GLOBAL_INGEST_HOLD",
            "KEEP_ORACLE_SIGNAL_UNIMPLEMENTED",
        ],
        "follow_on_actions_if_fresh_spec_requested": [
            "REQUEST_FRESH_NOTION_SPEC",
            "MAINTAIN_GLOBAL_INGEST_HOLD",
        ],
        "blocked_reasons": sorted(
            set(
                list(oracle_gap_item["blocked_reasons"])
                + doctrine_blocked_reasons
            )
        ),
        "source_hashes": {
            "global_pipeline_gap_backlog": gap_backlog["backlog_id"],
            "global_ingest_alignment_plan": ingest_alignment_plan["packet_hash"],
            "oracle_signal_intake_boundary_implementation_plan": implementation_plan["packet_hash"],
            "notion_operator_decision_backlog": notion_decision_backlog["packet_hash"],
            "notion_spec_completion_queue": completion_queue["packet_hash"],
            "global_pipeline_doctrine_proof": doctrine_proof["proof_id"],
        },
    }
    packet["request_id"] = _canonical_hash(packet, "request_id")
    return packet


def render_global_ingest_operator_decision_request_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Request",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `decision_scope`: `{packet['decision_scope']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_decision`: `{packet['recommended_decision']}`",
        f"- `recommended_next_action`: `{packet['recommended_next_action']}`",
        "",
        "## Decision Question",
        "",
        packet["decision_question"],
        "",
        "## Required Inputs",
        "",
    ]
    for item in packet["required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
        "## Observed Paths",
        "",
    ]
    )
    for item in packet["observed_paths"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Decision Record Template Candidates",
            "",
        ]
    )
    for item in packet["decision_record_template_candidates"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Implementation Plan Candidates",
            "",
        ]
    )
    for item in packet["implementation_plan_candidates"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Missing Paths",
            "",
        ]
    )
    for item in packet["missing_paths"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_request(source_root: str | Path = ".") -> dict[str, Any]:
    packet = build_global_ingest_operator_decision_request(source_root=source_root)
    markdown = render_global_ingest_operator_decision_request_markdown(packet)
    _write_json_and_markdown(JSON_PATH, MD_PATH, packet, markdown)
    return packet
