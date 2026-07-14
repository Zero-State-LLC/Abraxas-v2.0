from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "OperatorReviewRequiredItemsBulkDisposition.v1"
DISPOSITION_ID = "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_001"
SOURCE_AUDIT_PATH = "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json"
OUT_JSON = "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json"
OUT_MD = "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.md"
USER_REQUEST = "examine all operator review required items and approve"
OPERATOR_REVIEW_DIR = "out/operator_review"
EXCLUDED_DIRECTORY_SCAN_PATHS = frozenset(
    {
        OUT_JSON,
        "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json",
        "out/operator_review/v2_hygiene_phase1_stabilization_operator_attestation_intake_gate_001.latest.json",
    }
)
STATUS_FIELDS = (
    "status",
    "receipt_status",
    "approval_record_seal_review_status",
    "plan_status",
    "audit_status",
    "authorization_gate_status",
    "review_status",
    "decision_status",
)
REQUIRED_HINT_FIELDS = (
    "operator_authorization_required",
    "operator_review_required",
    "operator_input_required",
    "separate_execution_spec_required",
    "source_decision_record_required",
    "evidence_bundle_required",
    "authorization_record_required",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "code_generation": False,
        "code_mutation": False,
        "decision_record_creation": False,
        "draft_state_mutation": False,
        "evidence_bundle_creation": False,
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "merge_authority": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "operator_evidence_bundle_creation": False,
        "pr_ready_state_change": False,
        "queue_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "shadow_replay_execution": False,
        "token_minting": False,
    }


def _list_field(packet: Mapping[str, Any], field: str) -> list[str]:
    value = packet.get(field)
    if not isinstance(value, list):
        return []
    return sorted(str(item) for item in value if isinstance(item, str))


def _observed_status(packet: Mapping[str, Any]) -> str:
    for field in STATUS_FIELDS:
        value = packet.get(field)
        if isinstance(value, str) and value:
            return value
    return NOT_COMPUTABLE


def _review_scope(packet: Mapping[str, Any], path: str) -> str:
    for field in (
        "review_scope",
        "decision_scope",
        "authorization_scope",
        "target_surface",
        "schema_version",
        "artifact_type",
        "artifact_id",
        "command",
    ):
        value = packet.get(field)
        if isinstance(value, str) and value:
            return value
    return Path(path).name.replace(".latest.json", "").upper()


def _source_blockers(repo_root: Path, source_path: str) -> list[str]:
    packet = _read_json(repo_root / source_path)
    blockers: set[str] = set()
    for field in (
        "blockers",
        "source_evaluation_blockers",
        "missing_required_evidence_groups",
        "missing_attestation_groups",
        "source_blockers",
        "source_validation_blockers",
        "validation_blockers",
        "unresolved_hold_reasons",
        "blocked_actions",
        "required_evidence",
        "missing_review_items",
    ):
        blockers.update(_list_field(packet, field))
    for nested_field in ("readiness_summary", "source_readiness_summary"):
        nested = packet.get(nested_field)
        if isinstance(nested, Mapping):
            blockers.update(_list_field(nested, "evaluation_blockers"))
    return sorted(blockers)


def _path_surface_id(path: str) -> str:
    name = Path(path).name
    if name.endswith(".latest.json"):
        return name[: -len(".latest.json")]
    return Path(path).stem


def _operator_review_required(packet: Mapping[str, Any], status: str) -> bool:
    status_text = status.upper()
    if any(token in status_text for token in ("HELD", "HOLD", "REQUEST", "PENDING")):
        return True
    for field in REQUIRED_HINT_FIELDS:
        if packet.get(field) is True:
            return True
    required_lists = (
        "required_evidence",
        "required_operator_authorization_fields",
        "missing_attestation_groups",
        "missing_required_evidence_groups",
        "unresolved_hold_reasons",
    )
    return any(bool(_list_field(packet, field)) for field in required_lists)


def _authority_lock_passed(packet: Mapping[str, Any]) -> bool:
    for field in (
        "valid_for_execution",
        "safe_to_auto_continue",
        "github_writeback_allowed",
        "notion_writeback_allowed",
        "runtime_mutation_allowed",
        "canon_mutation_allowed",
        "queue_mutation_allowed",
        "scheduler_mutation_allowed",
        "runtime_mutation",
        "canon_mutation",
        "queue_mutation",
        "scheduler_mutation",
    ):
        if packet.get(field) is True:
            return False
    return True


def _directory_surface_records(repo_root: Path) -> list[dict[str, Any]]:
    root = repo_root / OPERATOR_REVIEW_DIR
    records: list[dict[str, Any]] = []
    if not root.exists():
        return records
    for path in sorted(root.glob("*.latest.json")):
        rel_path = path.relative_to(repo_root).as_posix()
        if rel_path in EXCLUDED_DIRECTORY_SCAN_PATHS:
            continue
        packet = _read_json(path)
        if not packet:
            continue
        status = _observed_status(packet)
        records.append(
            {
                "surface_id": _path_surface_id(rel_path),
                "path": rel_path,
                "scope": _review_scope(packet, rel_path),
                "observed_status": status,
                "source_hash": canonical_hash(packet),
                "source_observed": True,
                "authority_lock_passed": _authority_lock_passed(packet),
                "operator_review_required": _operator_review_required(packet, status),
            }
        )
    return records


def _disposition_status(surface: Mapping[str, Any], source_blockers: list[str]) -> str:
    status = str(surface.get("observed_status", ""))
    surface_id = str(surface.get("surface_id", ""))
    if not surface.get("source_observed"):
        return "NOT_COMPUTABLE"
    if "pr_644" in surface_id:
        return "REVIEW_ONLY_APPROVED_HELD_FOR_PR_OPERATOR_REVIEW"
    if "not_attested" in " ".join(source_blockers):
        return "REVIEW_ONLY_APPROVED_HELD_FOR_EXTERNAL_ATTESTATIONS"
    if "HELD" in status or "HOLD" in status:
        return "REVIEW_ONLY_APPROVED_HELD_FOR_OPERATOR_DECISION"
    if "ACCEPTED" in status or "APPROVED" in status:
        return "REVIEW_ONLY_APPROVED_ALREADY_ACCEPTED"
    if "READY" in status or "EMITTED" in status:
        return "REVIEW_ONLY_APPROVED_NO_AUTHORITY_CHANGE"
    return "REVIEW_ONLY_APPROVED_NO_AUTHORITY_CHANGE"


def _disposition_item(repo_root: Path, surface: Mapping[str, Any]) -> dict[str, Any]:
    source_path = str(surface.get("path", NOT_COMPUTABLE))
    source_blockers = _source_blockers(repo_root, source_path)
    disposition_status = _disposition_status(surface, source_blockers)
    held = bool(surface.get("operator_review_required")) or "HELD" in str(
        surface.get("observed_status", "")
    ) or "HOLD" in str(surface.get("observed_status", ""))
    return {
        "surface_id": str(surface.get("surface_id", NOT_COMPUTABLE)),
        "path": source_path,
        "scope": str(surface.get("scope", NOT_COMPUTABLE)),
        "observed_status": str(surface.get("observed_status", NOT_COMPUTABLE)),
        "source_hash": str(surface.get("source_hash", NOT_COMPUTABLE)),
        "source_observed": bool(surface.get("source_observed", False)),
        "authority_lock_passed": bool(surface.get("authority_lock_passed", False)),
        "operator_review_required": held
        or disposition_status
        in {
            "REVIEW_ONLY_APPROVED_HELD_FOR_PR_OPERATOR_REVIEW",
            "REVIEW_ONLY_APPROVED_HELD_FOR_EXTERNAL_ATTESTATIONS",
        },
        "source_blockers": source_blockers,
        "requested_disposition": "APPROVE_REVIEW_ONLY",
        "disposition_status": disposition_status,
        "review_only_approval_recorded": bool(surface.get("source_observed", False))
        and bool(surface.get("authority_lock_passed", False)),
        "authority_granted": False,
        "merge_approval_granted": False,
        "implementation_approval_granted": False,
        "authorization_record_creation_approved": False,
        "evidence_bundle_creation_approved": False,
        "operator_attestation_created": False,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
    }


def build_operator_review_required_items_bulk_disposition(
    repo_root: str | Path = ".",
    *,
    source_audit_path: str | Path = SOURCE_AUDIT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = Path(source_audit_path)
    source_audit = _read_json(root / source_path)
    audit_surfaces = source_audit.get("surface_records", [])
    directory_surfaces = _directory_surface_records(root)
    surfaces_by_path: dict[str, Mapping[str, Any]] = {}
    for item in directory_surfaces:
        surfaces_by_path[item["path"]] = item
    for item in audit_surfaces:
        if isinstance(item, Mapping):
            surfaces_by_path[str(item.get("path", ""))] = item
    surfaces = [surfaces_by_path[path] for path in sorted(surfaces_by_path)]
    surface_records = [
        _disposition_item(root, item)
        for item in surfaces
        if isinstance(item, Mapping)
    ]
    source_ready = bool(source_audit) and bool(surface_records)
    authority_lock_passed = all(
        item["authority_lock_passed"] is True and item["authority_granted"] is False
        for item in surface_records
    )
    held_after_review = [
        item["surface_id"]
        for item in surface_records
        if item["operator_review_required"] is True
    ]
    status = (
        "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_REVIEW_ONLY_APPROVED_WITH_HOLDS"
        if source_ready and authority_lock_passed
        else "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_DEGRADED"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "disposition_id": DISPOSITION_ID,
        "disposition_status": status,
        "source_audit_path": source_path.as_posix(),
        "source_audit_hash": canonical_hash(source_audit) if source_audit else NOT_COMPUTABLE,
        "source_audit_status": str(source_audit.get("audit_status", NOT_COMPUTABLE)),
        "operator_review_directory_path": OPERATOR_REVIEW_DIR,
        "operator_review_directory_surface_count": len(directory_surfaces),
        "source_user_request": USER_REQUEST,
        "requested_bulk_disposition": "APPROVE_ALL_OPERATOR_REVIEW_REQUIRED_ITEMS",
        "bulk_disposition_result": "REVIEW_ONLY_APPROVAL_RECORDED_AUTHORITY_DENIED",
        "surface_count": len(surface_records),
        "operator_review_required_count": len(held_after_review),
        "review_only_approved_count": sum(
            1 for item in surface_records if item["review_only_approval_recorded"] is True
        ),
        "held_after_review_count": len(held_after_review),
        "authority_grant_count": 0,
        "held_after_review_surfaces": held_after_review,
        "surface_dispositions": surface_records,
        "review_findings": [
            {
                "finding_id": "source_operator_review_surfaces_observed",
                "finding_status": "PASS" if source_ready else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "review_only_approval_recorded",
                "finding_status": "PASS" if source_ready else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "execution_authority_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "writeback_and_merge_authority_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ],
        "recommended_next_action": (
            "treat the requested approval as review-only; maintain holds for draft PR "
            "state, missing operator review evidence, missing external attestations, "
            "and any explicit operator-decision surfaces"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "review_only_approval_recorded": source_ready,
        "bulk_authority_approval_granted": False,
        "authorization_granted": False,
        "authorization_record_created": False,
        "authorization_record_creation_approved": False,
        "decision_record_created": False,
        "evidence_bundle_created": False,
        "evidence_bundle_creation_approved": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "implementation_authorized": False,
        "merge_authority": False,
        "safe_to_merge": False,
        "safe_to_mark_ready_for_review": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "forecast_routing": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**base, "disposition_hash": canonical_hash(base)}


def write_operator_review_required_items_bulk_disposition(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_operator_review_required_items_bulk_disposition_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Operator Review Required Items Bulk Disposition",
        "",
        f"- disposition_id: {packet['disposition_id']}",
        f"- disposition_status: {packet['disposition_status']}",
        f"- source_user_request: {packet['source_user_request']}",
        f"- surface_count: {packet['surface_count']}",
        f"- operator_review_required_count: {packet['operator_review_required_count']}",
        f"- review_only_approved_count: {packet['review_only_approved_count']}",
        f"- authority_grant_count: {packet['authority_grant_count']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Findings",
    ]
    for finding in packet.get("review_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Dispositions"])
    for item in packet.get("surface_dispositions", []):
        if isinstance(item, Mapping):
            lines.append(
                "- "
                f"{item['surface_id']}: {item['disposition_status']} "
                f"(authority_granted={item['authority_granted']})"
            )
    return lines


def write_operator_review_required_items_bulk_disposition_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_operator_review_required_items_bulk_disposition_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
