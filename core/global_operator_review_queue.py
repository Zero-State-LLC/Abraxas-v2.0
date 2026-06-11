from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

QUEUE_RUN_SCHEMA_VERSION = "OperatorReviewQueueRun.v1"
QUEUE_ITEM_SCHEMA_VERSION = "OperatorReviewQueueItem.v1"
PROJECTION_SCHEMA_VERSION = "GlobalPipelineAALVizProjectionPacket.v1"
SYNC_RECEIPT_SCHEMA_VERSION = "PipelineCanonSyncReceiptCandidate.v1"

QUEUE_JSON_PATH = Path("out/operator_review_queue/latest.json")
QUEUE_MD_PATH = Path("out/operator_review_queue/latest.md")
PROJECTION_JSON_PATH = Path("out/projections/global_pipeline_aal_viz_projection_packet_001.latest.json")
PROJECTION_MD_PATH = Path("out/projections/global_pipeline_aal_viz_projection_packet_001.latest.md")
SYNC_JSON_PATH = Path("out/sync/operator_review_queue_canon_sync_receipt_candidate_001.latest.json")
SYNC_MD_PATH = Path("out/sync/operator_review_queue_canon_sync_receipt_candidate_001.latest.md")

SCHEDULER_AUDIT_PATH = Path("out/audit/controlled_ingest_scheduler_governance_audit_001.latest.json")
SCHEDULER_REVIEW_RECORD_PATH = Path(
    "out/operator_review/controlled_ingest_scheduler_operator_review_record_001.latest.json"
)
VALIDATION_PACK_PATH = Path("out/audit/abx_auto_ingest_validation_pack_001.latest.json")
VALIDATION_PACK_REVIEW_RECORD_PATH = Path(
    "out/operator_review/abx_auto_ingest_shadow_stabilization_review_record_001.latest.json"
)
INGEST_PROJECTION_PATH = Path("out/projections/aal_viz_ingest_projection_pack_001.latest.json")
GLOBAL_INGEST_DECISION_REQUEST_PATH = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.json")
ORACLE_SIGNAL_SHADOW_REVIEW_RECORD_PATH = Path(
    "out/operator_review/oracle_signal_shadow_intake_operator_review_decision_record_001.latest.json"
)

ALLOWED_QUEUE_STATES = (
    "needs_review",
    "repair_required",
    "held",
    "rejected",
    "eligible_for_shadow_stabilization",
    "eligible_for_operator_review",
    "review_completed",
    "approved_for_repo_execution",
    "approved_for_promotion_review",
    "repo_execution_required",
    "repo_execution_attached",
    "not_computable",
)

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
FORBIDDEN_AUTHORITY_FIELDS = (
    "promotion_allowed",
    "forecast_weight_allowed",
    "forecast_authority",
    "runtime_mutation_allowed",
    "runtime_mutation",
    "baseline_mutation_allowed",
    "canon_mutation_allowed",
    "canon_mutation",
    "execution_authority",
    "production_activation_allowed",
    "adapter_activation_allowed",
)


def _canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canonical_hash(data: object, field_name: str) -> str:
    if isinstance(data, Mapping):
        payload = dict(data)
        payload.pop(field_name, None)
        return _sha256_text(_canonical_json(payload))
    raise TypeError("canonical hash requires mapping payload")


def _read_json(root: Path, rel_path: Path) -> dict[str, Any]:
    return json.loads((root / rel_path).read_text(encoding="utf-8"))


def _write_json_and_markdown(json_path: Path, md_path: Path, packet: Mapping[str, Any], markdown_lines: list[str]) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(_canonical_json(packet) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")


def scan_authority_violations(packet: Mapping[str, Any]) -> list[str]:
    violations: list[str] = []
    authority = packet.get("authority", {})
    if isinstance(authority, Mapping):
        for key, value in authority.items():
            if value not in (False, None):
                violations.append(f"authority.{key}")
    for key in FORBIDDEN_AUTHORITY_FIELDS:
        if packet.get(key) not in (False, None):
            violations.append(key)
    return sorted(set(violations))


def classify_normalized_review_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    authority_violations = scan_authority_violations(packet)
    failed_gates = list(packet.get("failed_gates", ()))
    negative_proof_complete = bool(packet.get("negative_proof_complete", False))
    validation_passed = bool(packet.get("validation_passed", False))
    operator_review_ready = bool(packet.get("operator_review_ready", False))
    requires_repo_execution_receipt = bool(packet.get("requires_repo_execution_receipt", False))
    repo_execution_receipt_hash = packet.get("repo_execution_receipt_hash")

    state = "held"
    priority = "P3"
    required_actions = list(packet.get("required_operator_actions", ()))
    allowed_decisions = list(packet.get("allowed_decisions", ("HOLD", "REJECT")))
    not_computable_reasons = list(packet.get("not_computable_reasons", ()))

    if authority_violations:
        state = "rejected"
        priority = "P0"
        required_actions = sorted(set(required_actions + ["remove_authority_leakage"]))
        allowed_decisions = ["REJECT", "HOLD"]
    elif packet.get("hold_for_operator_decision"):
        state = "held"
        priority = "P0"
        required_actions = sorted(set(required_actions + ["collect_operator_decision_evidence"]))
    elif packet.get("review_completed"):
        state = "review_completed"
        priority = "P3"
        required_actions = []
        allowed_decisions = ["HOLD"]
    elif requires_repo_execution_receipt and not repo_execution_receipt_hash:
        state = "repo_execution_required"
        priority = "P0"
        required_actions = sorted(set(required_actions + ["attach_repo_execution_receipt"]))
        allowed_decisions = ["HOLD", "APPROVE_REPO_EXECUTION_RECEIPT_ATTACHMENT", "REJECT"]
    elif not negative_proof_complete:
        state = "repair_required"
        priority = "P1"
        required_actions = sorted(set(required_actions + ["provide_negative_proof"]))
        allowed_decisions = ["HOLD", "REQUEST_REPAIR", "REJECT"]
    elif failed_gates or not validation_passed:
        state = "repair_required"
        priority = "P1"
        required_actions = sorted(set(required_actions + ["repair_failed_gates"]))
        allowed_decisions = ["HOLD", "REQUEST_REPAIR", "REJECT"]
    elif operator_review_ready and packet.get("lane") == "SHADOW" and not requires_repo_execution_receipt:
        state = "eligible_for_shadow_stabilization"
        priority = "P2"
        allowed_decisions = ["HOLD", "APPROVE_SHADOW_STABILIZATION_REVIEW", "REJECT"]
    elif operator_review_ready:
        state = "eligible_for_operator_review"
        priority = "P2"
        allowed_decisions = ["HOLD", "APPROVE_OPERATOR_REVIEW", "REJECT"]
    elif not_computable_reasons:
        state = "not_computable"
        priority = "P2"

    return {
        "state": state,
        "priority": priority,
        "authority_violations": authority_violations,
        "failed_gates": failed_gates,
        "required_operator_actions": required_actions,
        "allowed_decisions": allowed_decisions,
        "not_computable_reasons": not_computable_reasons,
    }


def normalize_scheduler_audit(
    packet: Mapping[str, Any],
    review_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    review_record = review_record or {}
    review_completed = (
        review_record.get("schema_version") == "ControlledIngestSchedulerOperatorReviewRecord.v1"
        and review_record.get("status") == "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW_ACCEPTED"
        and review_record.get("audit_accepted_as_reviewed_evidence") is True
        and review_record.get("execution_authority") is False
        and review_record.get("scheduler_mutation_allowed") is False
        and review_record.get("recommended_next_patch") == "NOT_COMPUTABLE"
    )
    return {
        "title": "Controlled ingest scheduler governance audit",
        "pipeline_id": "abx_controlled_ingest_scheduler_v1",
        "source_run_id": packet.get("audit_id"),
        "source_review_packet_hash": review_record.get("record_hash") if review_completed else packet.get("audit_hash"),
        "lane": "GOVERNANCE",
        "authority": {
            "promotion_allowed": False,
            "forecast_weight_allowed": False,
            "runtime_mutation_allowed": False,
            "baseline_mutation_allowed": False,
            "canon_mutation_allowed": False,
        },
        "validation_passed": packet.get("final_status") == "PASS",
        "negative_proof_complete": True,
        "operator_review_ready": (
            packet.get("recommended_next_step") == "CONTROLLED_INGEST_SCHEDULER_OPERATOR_REVIEW"
            and not review_completed
        ),
        "review_completed": review_completed,
        "required_operator_actions": []
        if review_completed
        else [
            "review_controlled_ingest_scheduler_governance_audit",
            "confirm_scheduler_handoff_target_patch",
        ],
        "allowed_decisions": ["HOLD"] if review_completed else ["HOLD", "APPROVE_OPERATOR_REVIEW", "REJECT"],
        "repo_execution_receipt_hash": None,
        "requires_repo_execution_receipt": False,
        "stabilization_window": {
            "required": True,
            "status": "review_only_completed" if review_completed else "not_started",
        },
        "conflicts": [],
        "failed_gates": [],
    }


def normalize_validation_pack(
    packet: Mapping[str, Any],
    projection_packet: Mapping[str, Any],
    review_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    review_record = review_record or {}
    review_completed = (
        review_record.get("schema_version") == "ABXAutoIngestShadowStabilizationReviewRecord.v1"
        and review_record.get("status") == "ABX_AUTO_INGEST_SHADOW_STABILIZATION_REVIEW_ACCEPTED"
        and review_record.get("shadow_stabilization_review_completed") is True
        and review_record.get("activation_authority") is False
        and review_record.get("execution_authority") is False
        and review_record.get("runtime_mutation_allowed") is False
        and review_record.get("recommended_next_patch") == "NOT_COMPUTABLE"
    )
    check_results = packet.get("check_results", {})
    projection_tile = next(
        (tile for tile in projection_packet.get("tiles", []) if tile.get("tile_id") == "authority_lock_panel"),
        {},
    )
    return {
        "title": "Auto ingest full-stack validation pack",
        "pipeline_id": "abx_auto_ingest_v1",
        "source_run_id": packet.get("validation_id"),
        "source_review_packet_hash": review_record.get("record_hash") if review_completed else packet.get("validation_hash"),
        "lane": "SHADOW",
        "authority": {
            "promotion_allowed": False,
            "forecast_weight_allowed": False,
            "runtime_mutation_allowed": bool(packet.get("runtime_mutation", False)),
            "baseline_mutation_allowed": False,
            "canon_mutation_allowed": bool(packet.get("canon_mutation", False)),
        },
        "validation_passed": packet.get("final_status") == "PASS",
        "negative_proof_complete": (
            packet.get("success_criteria", {}).get("forecast_activation") == "PASS_BLOCKED"
            and packet.get("success_criteria", {}).get("canon_mutation") == "PASS_BLOCKED"
        ),
        "operator_review_ready": (
            check_results.get("authority_leakage_scan") == "PASS_NO_FORBIDDEN_FIELDS"
            and check_results.get("viz_projection_only") == "PASS_PROJECTION_ONLY"
            and projection_tile.get("status") == "LOCKED"
            and not review_completed
        ),
        "review_completed": review_completed,
        "required_operator_actions": []
        if review_completed
        else [
            "review_auto_ingest_validation_pack",
            "acknowledge_projection_only_boundary",
        ],
        "allowed_decisions": ["HOLD"] if review_completed else ["HOLD", "APPROVE_SHADOW_STABILIZATION_REVIEW", "REJECT"],
        "repo_execution_receipt_hash": None,
        "requires_repo_execution_receipt": False,
        "stabilization_window": {
            "required": True,
            "status": "review_only_completed" if review_completed else "not_started",
        },
        "conflicts": [],
        "failed_gates": [],
    }


def normalize_global_ingest_operator_decision_request(
    packet: Mapping[str, Any],
    review_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    review_record = review_record or {}
    review_completed = (
        review_record.get("schema_version") == "OracleSignalShadowIntakeOperatorReviewDecisionRecord.v1"
        and review_record.get("status") == "ORACLE_SIGNAL_SHADOW_INTAKE_OPERATOR_REVIEW_COMPLETION_APPROVED"
        and review_record.get("review_only_completion_approved") is True
        and review_record.get("receipt_accepted_as_review_only_evidence") is True
        and review_record.get("implementation_authorized") is False
        and review_record.get("execution_authority") is False
        and review_record.get("runtime_mutation_allowed") is False
        and review_record.get("recommended_next_patch") == "NOT_COMPUTABLE"
    )
    return {
        "title": "Global ingest operator decision request",
        "pipeline_id": packet.get("target_pipeline_id", "oracle_signal"),
        "source_run_id": packet.get("request_id"),
        "source_review_packet_hash": review_record.get("decision_record_hash") if review_completed else packet.get("request_id"),
        "lane": "SHADOW",
        "authority": {
            "promotion_allowed": False,
            "forecast_weight_allowed": False,
            "runtime_mutation_allowed": False,
            "baseline_mutation_allowed": False,
            "canon_mutation_allowed": False,
        },
        "validation_passed": True,
        "negative_proof_complete": True,
        "operator_review_ready": False,
        "hold_for_operator_decision": not review_completed,
        "review_completed": review_completed,
        "required_operator_actions": list(
            packet.get(
                "required_operator_actions",
                [
                    "collect_global_ingest_operator_decision",
                    "record_global_ingest_operator_decision",
                ],
            )
        )
        if not review_completed
        else [],
        "allowed_decisions": ["HOLD"] if review_completed else list(packet.get("decision_options", ("HOLD", "REJECT_IMPLEMENTATION_SPEC"))),
        "repo_execution_receipt_hash": None,
        "requires_repo_execution_receipt": False,
        "stabilization_window": {
            "required": False,
            "status": "review_only_completed" if review_completed else "not_required",
        },
        "conflicts": [],
        "failed_gates": [],
        "not_computable_reasons": [] if review_completed else list(packet.get("blocked_reasons", ())),
    }


def build_queue_item(normalized_packet: Mapping[str, Any]) -> dict[str, Any]:
    classification = classify_normalized_review_packet(normalized_packet)
    item = {
        "schema_version": QUEUE_ITEM_SCHEMA_VERSION,
        "queue_item_id": _sha256_text(
            _canonical_json(
                {
                    "pipeline_id": normalized_packet["pipeline_id"],
                    "source_review_packet_hash": normalized_packet["source_review_packet_hash"],
                    "state": classification["state"],
                }
            )
        ),
        "source_review_packet_hash": normalized_packet["source_review_packet_hash"],
        "pipeline_id": normalized_packet["pipeline_id"],
        "source_run_id": normalized_packet.get("source_run_id"),
        "title": normalized_packet["title"],
        "priority": classification["priority"],
        "state": classification["state"],
        "lane": normalized_packet["lane"],
        "failed_gates": classification["failed_gates"],
        "authority_violations": classification["authority_violations"],
        "conflicts": list(normalized_packet.get("conflicts", ())),
        "not_computable_reasons": classification["not_computable_reasons"],
        "required_operator_actions": classification["required_operator_actions"],
        "allowed_decisions": classification["allowed_decisions"],
        "repo_execution_receipt_hash": normalized_packet.get("repo_execution_receipt_hash"),
        "stabilization_window": dict(normalized_packet.get("stabilization_window", {"required": True, "status": "not_started"})),
        "authority": {
            "promotion_allowed": False,
            "forecast_weight_allowed": False,
            "runtime_mutation_allowed": False,
            "baseline_mutation_allowed": False,
            "canon_mutation_allowed": False,
        },
        "recommended_next_state": classification["state"],
    }
    return item


def compute_recommended_next_state(items: list[Mapping[str, Any]]) -> str:
    if any(item["priority"] == "P0" for item in items):
        if any(item["state"] == "repo_execution_required" for item in items):
            return "execute_repo"
        if any(item["state"] == "held" for item in items):
            return "review"
        return "repair"
    if any(item["priority"] == "P1" for item in items):
        return "repair"
    if any(item["state"] == "eligible_for_operator_review" for item in items):
        return "review"
    if any(item["state"] == "eligible_for_shadow_stabilization" for item in items):
        return "stabilize"
    if any(item["state"] == "held" for item in items):
        return "hold"
    if items and all(item["state"] == "review_completed" for item in items):
        return "review_completed"
    return "not_computable"


def build_queue_run(items: list[Mapping[str, Any]], source_packets: list[Mapping[str, Any]]) -> dict[str, Any]:
    sorted_items = sorted(items, key=lambda item: (PRIORITY_ORDER[item["priority"]], item["title"], item["queue_item_id"]))
    state_counts: dict[str, int] = {}
    for item in sorted_items:
        state_counts[item["state"]] = state_counts.get(item["state"], 0) + 1

    payload = {
        "schema_version": QUEUE_RUN_SCHEMA_VERSION,
        "run_id": "PENDING",
        "status": "completed",
        "queue_item_count": len(sorted_items),
        "state_counts": {key: state_counts[key] for key in sorted(state_counts)},
        "p0_count": sum(1 for item in sorted_items if item["priority"] == "P0"),
        "p1_count": sum(1 for item in sorted_items if item["priority"] == "P1"),
        "authority_violation_count": sum(len(item["authority_violations"]) for item in sorted_items),
        "repo_execution_required_count": sum(1 for item in sorted_items if item["state"] == "repo_execution_required"),
        "stabilization_ready_count": sum(1 for item in sorted_items if item["state"] == "eligible_for_shadow_stabilization"),
        "items": sorted_items,
        "source_packets": [
            {
                "path": source["path"],
                "schema_version": source["schema_version"],
                "source_hash": source["source_hash"],
            }
            for source in sorted(source_packets, key=lambda value: value["path"])
        ],
        "authority": {
            "promotion_allowed": False,
            "forecast_weight_allowed": False,
            "runtime_mutation_allowed": False,
            "baseline_mutation_allowed": False,
            "canon_mutation_allowed": False,
        },
        "recommended_next_state": compute_recommended_next_state(sorted_items),
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "forecast_authority": False,
    }
    payload["run_id"] = _canonical_hash(payload, "run_id")
    return payload


def build_projection_packet(queue_run: Mapping[str, Any]) -> dict[str, Any]:
    items = list(queue_run["items"])
    payload = {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "projection_id": "PENDING",
        "queue_run_hash": queue_run["run_id"],
        "queue_item_count": queue_run["queue_item_count"],
        "priority_counts": {
            "P0": queue_run["p0_count"],
            "P1": queue_run["p1_count"],
            "P2": sum(1 for item in items if item["priority"] == "P2"),
            "P3": sum(1 for item in items if item["priority"] == "P3"),
        },
        "state_counts": dict(queue_run["state_counts"]),
        "p0_authority_risks": [
            {
                "title": item["title"],
                "authority_violations": item["authority_violations"],
            }
            for item in items
            if item["priority"] == "P0"
        ],
        "repo_execution_required_count": queue_run["repo_execution_required_count"],
        "stabilization_ready_count": queue_run["stabilization_ready_count"],
        "repair_required_count": queue_run["state_counts"].get("repair_required", 0),
        "held_or_rejected_count": queue_run["state_counts"].get("held", 0) + queue_run["state_counts"].get("rejected", 0),
        "recommended_next_state": queue_run["recommended_next_state"],
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "forecast_authority": False,
    }
    payload["projection_id"] = _canonical_hash(payload, "projection_id")
    return payload


def build_canon_sync_receipt_candidate(queue_run: Mapping[str, Any]) -> dict[str, Any]:
    payload = {
        "schema_version": SYNC_RECEIPT_SCHEMA_VERSION,
        "receipt_id": "PENDING",
        "queue_run_hash": queue_run["run_id"],
        "source_packet_hashes": [source["source_hash"] for source in queue_run["source_packets"]],
        "repo_receipts_linked": [
            item["repo_execution_receipt_hash"]
            for item in queue_run["items"]
            if item["repo_execution_receipt_hash"] is not None
        ],
        "authority_violations_detected": queue_run["authority_violation_count"],
        "recommended_next_state": queue_run["recommended_next_state"],
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation": False,
        "canon_mutation": False,
        "forecast_authority": False,
    }
    payload["receipt_id"] = _canonical_hash(payload, "receipt_id")
    return payload


def build_global_operator_review_queue_artifacts(root: Path | str = ".", source_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    base = Path(root)
    source_base = Path(source_root) if source_root is not None else base
    scheduler_audit = _read_json(source_base, SCHEDULER_AUDIT_PATH)
    scheduler_review_record = (
        _read_json(source_base, SCHEDULER_REVIEW_RECORD_PATH)
        if (source_base / SCHEDULER_REVIEW_RECORD_PATH).exists()
        else {}
    )
    validation_pack = _read_json(source_base, VALIDATION_PACK_PATH)
    validation_pack_review_record = (
        _read_json(source_base, VALIDATION_PACK_REVIEW_RECORD_PATH)
        if (source_base / VALIDATION_PACK_REVIEW_RECORD_PATH).exists()
        else {}
    )
    ingest_projection = _read_json(source_base, INGEST_PROJECTION_PATH)
    global_ingest_decision_request = _read_json(source_base, GLOBAL_INGEST_DECISION_REQUEST_PATH)
    oracle_signal_shadow_review_record = (
        _read_json(source_base, ORACLE_SIGNAL_SHADOW_REVIEW_RECORD_PATH)
        if (source_base / ORACLE_SIGNAL_SHADOW_REVIEW_RECORD_PATH).exists()
        else {}
    )

    normalized_packets = [
        normalize_scheduler_audit(scheduler_audit, scheduler_review_record),
        normalize_validation_pack(validation_pack, ingest_projection, validation_pack_review_record),
        normalize_global_ingest_operator_decision_request(
            global_ingest_decision_request,
            oracle_signal_shadow_review_record,
        ),
    ]
    queue_items = [build_queue_item(packet) for packet in normalized_packets]
    source_packets = [
        {
            "path": SCHEDULER_AUDIT_PATH.as_posix(),
            "schema_version": scheduler_audit["schema_version"],
            "source_hash": scheduler_audit["audit_hash"],
        },
        *(
            [
                {
                    "path": SCHEDULER_REVIEW_RECORD_PATH.as_posix(),
                    "schema_version": scheduler_review_record["schema_version"],
                    "source_hash": scheduler_review_record["record_hash"],
                }
            ]
            if scheduler_review_record
            else []
        ),
        {
            "path": VALIDATION_PACK_PATH.as_posix(),
            "schema_version": validation_pack["schema_version"],
            "source_hash": validation_pack["validation_hash"],
        },
        *(
            [
                {
                    "path": VALIDATION_PACK_REVIEW_RECORD_PATH.as_posix(),
                    "schema_version": validation_pack_review_record["schema_version"],
                    "source_hash": validation_pack_review_record["record_hash"],
                }
            ]
            if validation_pack_review_record
            else []
        ),
        {
            "path": INGEST_PROJECTION_PATH.as_posix(),
            "schema_version": ingest_projection["schema_version"],
            "source_hash": ingest_projection["projection_hash"],
        },
        {
            "path": GLOBAL_INGEST_DECISION_REQUEST_PATH.as_posix(),
            "schema_version": global_ingest_decision_request["schema_version"],
            "source_hash": global_ingest_decision_request["request_id"],
        },
        *(
            [
                {
                    "path": ORACLE_SIGNAL_SHADOW_REVIEW_RECORD_PATH.as_posix(),
                    "schema_version": oracle_signal_shadow_review_record["schema_version"],
                    "source_hash": oracle_signal_shadow_review_record["decision_record_hash"],
                }
            ]
            if oracle_signal_shadow_review_record
            else []
        ),
    ]
    queue_run = build_queue_run(queue_items, source_packets)
    projection_packet = build_projection_packet(queue_run)
    sync_receipt = build_canon_sync_receipt_candidate(queue_run)
    return {"queue_run": queue_run, "projection_packet": projection_packet, "sync_receipt": sync_receipt}


def write_global_operator_review_queue_artifacts(root: Path | str = ".", source_root: Path | str | None = None) -> dict[str, dict[str, Any]]:
    base = Path(root)
    artifacts = build_global_operator_review_queue_artifacts(base, source_root=source_root)
    queue_run = artifacts["queue_run"]
    projection_packet = artifacts["projection_packet"]
    sync_receipt = artifacts["sync_receipt"]

    _write_json_and_markdown(
        base / QUEUE_JSON_PATH,
        base / QUEUE_MD_PATH,
        queue_run,
        [
            "# Global Operator Review Queue",
            "",
            f"- run_id: `{queue_run['run_id']}`",
            f"- queue_item_count: `{queue_run['queue_item_count']}`",
            f"- recommended_next_state: `{queue_run['recommended_next_state']}`",
        ],
    )
    _write_json_and_markdown(
        base / PROJECTION_JSON_PATH,
        base / PROJECTION_MD_PATH,
        projection_packet,
        [
            "# Global Pipeline AAL-Viz Projection Packet",
            "",
            f"- projection_id: `{projection_packet['projection_id']}`",
            f"- queue_run_hash: `{projection_packet['queue_run_hash']}`",
            f"- recommended_next_state: `{projection_packet['recommended_next_state']}`",
        ],
    )
    _write_json_and_markdown(
        base / SYNC_JSON_PATH,
        base / SYNC_MD_PATH,
        sync_receipt,
        [
            "# Operator Review Queue Canon Sync Receipt Candidate",
            "",
            f"- receipt_id: `{sync_receipt['receipt_id']}`",
            f"- queue_run_hash: `{sync_receipt['queue_run_hash']}`",
            f"- recommended_next_state: `{sync_receipt['recommended_next_state']}`",
        ],
    )
    return artifacts
