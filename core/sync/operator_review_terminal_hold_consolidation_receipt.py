from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "OperatorReviewTerminalHoldConsolidationReceipt.v1"
RECEIPT_ID = "OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_001"
SOURCE_P102G_PATH = "out/operator_review/p102g_plus_operator_decision_surface_audit_001.latest.json"
SOURCE_BULK_PATH = "out/operator_review/operator_review_required_items_bulk_disposition_001.latest.json"
OUT_JSON = "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.json"
OUT_MD = "out/operator_review/operator_review_terminal_hold_consolidation_receipt_001.latest.md"

READY_STATUS = "OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_READY"
BLOCKED_STATUS = "OPERATOR_REVIEW_TERMINAL_HOLD_CONSOLIDATION_RECEIPT_BLOCKED"

FAMILY_ORDER = (
    "v2_phase1_stabilization",
    "v2_phase1_authorization",
    "codegen",
    "grok_abx_runes",
    "ingest_oracle_runtime",
    "artifact_lineage",
    "pr_review",
    "temporal_seal_review",
    "other_operator_review",
)

SOURCE_READY_STATUSES = {
    "P102G_PLUS_OPERATOR_DECISION_SURFACE_AUDIT_READY",
    "OPERATOR_REVIEW_REQUIRED_ITEMS_BULK_DISPOSITION_REVIEW_ONLY_APPROVED_WITH_HOLDS",
}

AUTHORITY_BOOLEAN_FIELDS = (
    "evidence_bundle_created",
    "evidence_bundle_creation_authorized",
    "operator_attestation_created",
    "decision_record_created",
    "decision_record_creation_authorized",
    "authorization_record_created",
    "authorization_record_creation_authorized",
    "implementation_authorized",
    "writeback_authorized",
    "runtime_mutation",
    "canon_mutation",
    "queue_mutation",
    "scheduler_mutation",
    "activation_authorized",
    "promotion_authorized",
    "registration_authorized",
    "execution_authority",
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
        "evidence_bundle_creation": False,
        "execution": False,
        "file_writeback": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
        "operator_evidence_bundle_creation": False,
        "promotion": False,
        "queue_mutation": False,
        "registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "shadow_replay_execution": False,
        "token_minting": False,
    }


def _all_locks_false(packet: Mapping[str, Any]) -> bool:
    locks = packet.get("authority_locks")
    return isinstance(locks, Mapping) and bool(locks) and all(value is False for value in locks.values())


def _bool_false(packet: Mapping[str, Any], field: str) -> bool:
    return packet.get(field) is False


def _source_ready(p102g: Mapping[str, Any], bulk: Mapping[str, Any]) -> tuple[str, list[str]]:
    blockers: list[str] = []
    if not p102g:
        blockers.append("p102g_plus_source_missing")
    if not bulk:
        blockers.append("bulk_disposition_source_missing")
    if blockers:
        return "SOURCE_AGGREGATES_MISSING", blockers

    if p102g.get("audit_status") not in SOURCE_READY_STATUSES:
        blockers.append("p102g_plus_audit_status_not_ready")
    if bulk.get("disposition_status") not in SOURCE_READY_STATUSES:
        blockers.append("bulk_disposition_status_not_ready")
    for source_id, packet in (("p102g_plus", p102g), ("bulk_disposition", bulk)):
        if packet.get("recommended_next_lane") != NOT_COMPUTABLE:
            blockers.append(f"{source_id}_recommended_next_lane_authorizing")
        if not _bool_false(packet, "valid_for_execution"):
            blockers.append(f"{source_id}_valid_for_execution_not_false")
        if not _bool_false(packet, "safe_to_auto_continue"):
            blockers.append(f"{source_id}_safe_to_auto_continue_not_false")
        if not _all_locks_false(packet):
            blockers.append(f"{source_id}_authority_locks_not_all_false")
    if bulk.get("authority_grant_count") != 0:
        blockers.append("bulk_disposition_authority_grants_present")
    if not isinstance(bulk.get("surface_dispositions"), list):
        blockers.append("bulk_disposition_surfaces_missing")
    if int(bulk.get("operator_review_required_count", 0) or 0) <= 0:
        blockers.append("bulk_disposition_no_operator_review_holds")
    if blockers:
        return "SOURCE_AGGREGATES_NOT_READY", sorted(blockers)
    return "SOURCE_AGGREGATES_READY", []


def _classify_family(surface_id: str, path: str) -> str:
    text = f"{surface_id} {path}".lower()
    if "stabilization" in text or "dependency_cycle_audit" in text:
        return "v2_phase1_stabilization"
    if "v2_hygiene_phase1_authorization" in text or "v2_hygiene_operator_authorization" in text:
        return "v2_phase1_authorization"
    if "v2_hygiene_schema_contract" in text or "v2_hygiene_phase2_governance" in text:
        return "v2_phase1_authorization"
    if "codegen" in text:
        return "codegen"
    if "grok_abx_runes" in text:
        return "grok_abx_runes"
    if any(token in text for token in ("ingest", "oracle", "runtime_integration")):
        return "ingest_oracle_runtime"
    if "artifact_lineage" in text:
        return "artifact_lineage"
    if "pr_644" in text:
        return "pr_review"
    if "temporal" in text:
        return "temporal_seal_review"
    return "other_operator_review"


def _surface_is_held(surface: Mapping[str, Any]) -> bool:
    return bool(surface.get("operator_review_required")) or "HELD" in str(
        surface.get("observed_status", "")
    ) or "HOLD" in str(surface.get("observed_status", ""))


def _missing_attestation(surface: Mapping[str, Any]) -> bool:
    blockers = surface.get("source_blockers")
    if not isinstance(blockers, list):
        blockers = []
    blocker_text = " ".join(str(item) for item in blockers).lower()
    status_text = str(surface.get("disposition_status", "")).upper()
    return "not_attested" in blocker_text or "EXTERNAL_ATTESTATIONS" in status_text


def _terminal_hold_matrix(surface_dispositions: list[Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[Mapping[str, Any]]] = {family: [] for family in FAMILY_ORDER}
    for item in surface_dispositions:
        if not isinstance(item, Mapping):
            continue
        surface_id = str(item.get("surface_id", NOT_COMPUTABLE))
        path = str(item.get("path", ""))
        grouped[_classify_family(surface_id, path)].append(item)

    matrix: list[dict[str, Any]] = []
    for family_id in FAMILY_ORDER:
        surfaces = sorted(grouped[family_id], key=lambda item: str(item.get("surface_id", "")))
        source_surface_ids = [str(item.get("surface_id", NOT_COMPUTABLE)) for item in surfaces]
        held_surface_ids = [
            str(item.get("surface_id", NOT_COMPUTABLE))
            for item in surfaces
            if _surface_is_held(item)
        ]
        missing_attestation_surface_ids = [
            str(item.get("surface_id", NOT_COMPUTABLE))
            for item in surfaces
            if _missing_attestation(item)
        ]
        matrix.append(
            {
                "family_id": family_id,
                "surface_count": len(source_surface_ids),
                "held_surface_count": len(held_surface_ids),
                "missing_attestation_surface_count": len(missing_attestation_surface_ids),
                "source_surface_ids": source_surface_ids,
                "held_surface_ids": held_surface_ids,
                "missing_attestation_surface_ids": missing_attestation_surface_ids,
                "authority_grant_count": sum(
                    1 for item in surfaces if item.get("authority_granted") is True
                ),
                "authority_locks": _authority_locks(),
                "valid_for_execution": False,
                "safe_to_auto_continue": False,
            }
        )
    return matrix


def build_operator_review_terminal_hold_consolidation_receipt(
    repo_root: str | Path = ".",
    *,
    source_p102g_path: str | Path = SOURCE_P102G_PATH,
    source_bulk_path: str | Path = SOURCE_BULK_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    p102g_rel = Path(source_p102g_path).as_posix()
    bulk_rel = Path(source_bulk_path).as_posix()
    p102g = _read_json(root / p102g_rel)
    bulk = _read_json(root / bulk_rel)
    source_readiness, source_blockers = _source_ready(p102g, bulk)
    ready = source_readiness == "SOURCE_AGGREGATES_READY"
    missing = source_readiness == "SOURCE_AGGREGATES_MISSING"

    surfaces = bulk.get("surface_dispositions", []) if isinstance(bulk, Mapping) else []
    if not isinstance(surfaces, list):
        surfaces = []
    matrix = _terminal_hold_matrix(surfaces) if ready else _terminal_hold_matrix([])
    terminal_hold_surface_count = sum(item["held_surface_count"] for item in matrix)
    missing_attestation_surface_count = sum(
        item["missing_attestation_surface_count"] for item in matrix
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "receipt_id": RECEIPT_ID,
        "receipt_status": READY_STATUS if ready else (NOT_COMPUTABLE if missing else BLOCKED_STATUS),
        "source_p102g_path": p102g_rel,
        "source_bulk_disposition_path": bulk_rel,
        "source_p102g_observed": bool(p102g),
        "source_bulk_disposition_observed": bool(bulk),
        "source_p102g_hash": str(p102g.get("audit_hash", NOT_COMPUTABLE)),
        "source_bulk_disposition_hash": str(bulk.get("disposition_hash", NOT_COMPUTABLE)),
        "source_readiness": source_readiness,
        "source_blockers": source_blockers,
        "source_surface_count": int(bulk.get("surface_count", 0) or 0),
        "source_operator_review_required_count": int(
            bulk.get("operator_review_required_count", 0) or 0
        ),
        "source_authority_grant_count": int(bulk.get("authority_grant_count", 0) or 0),
        "terminal_hold_matrix_ready": ready,
        "terminal_hold_matrix": matrix,
        "terminal_hold_family_count": sum(1 for item in matrix if item["surface_count"] > 0),
        "terminal_hold_surface_count": terminal_hold_surface_count,
        "missing_attestation_surface_count": missing_attestation_surface_count,
        "consolidation_recommendation": (
            "MAINTAIN_TERMINAL_OPERATOR_REVIEW_HOLDS" if ready else NOT_COMPUTABLE
        ),
        "consolidation_findings": [
            {
                "finding_id": "source_aggregates_observed",
                "finding_status": "PASS" if ready else "FAIL_CLOSED",
                "authority_granted": False,
            },
            {
                "finding_id": "terminal_hold_families_classified",
                "finding_status": "PASS" if ready else "NOT_COMPUTABLE",
                "authority_granted": False,
            },
            {
                "finding_id": "external_attestations_absent",
                "finding_status": "OBSERVED" if ready else "NOT_COMPUTABLE",
                "authority_granted": False,
            },
            {
                "finding_id": "downstream_lane_not_computable",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "authority_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ],
        "recommended_next_action": (
            "collect explicit external operator attestations before any future "
            "decision, authorization, implementation, activation, promotion, "
            "writeback, mutation, or execution lane; do not add recursive "
            "review/evidence lanes"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "terminal_operator_review_hold",
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "safe_to_auto_continue": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    for field in AUTHORITY_BOOLEAN_FIELDS:
        base[field] = False
    return {**base, "receipt_hash": canonical_hash(base)}


def write_operator_review_terminal_hold_consolidation_receipt(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_operator_review_terminal_hold_consolidation_receipt_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Operator Review Terminal Hold Consolidation Receipt",
        "",
        f"- receipt_id: {packet['receipt_id']}",
        f"- receipt_status: {packet['receipt_status']}",
        f"- source_readiness: {packet['source_readiness']}",
        f"- source_surface_count: {packet['source_surface_count']}",
        f"- source_operator_review_required_count: {packet['source_operator_review_required_count']}",
        f"- terminal_hold_surface_count: {packet['terminal_hold_surface_count']}",
        f"- missing_attestation_surface_count: {packet['missing_attestation_surface_count']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Terminal Hold Matrix",
    ]
    for item in packet.get("terminal_hold_matrix", []):
        if isinstance(item, Mapping):
            lines.append(
                "- "
                f"{item['family_id']}: surfaces={item['surface_count']}, "
                f"held={item['held_surface_count']}, "
                f"missing_attestations={item['missing_attestation_surface_count']}, "
                f"authority_grants={item['authority_grant_count']}"
            )
    lines.extend(["", "## Findings"])
    for finding in packet.get("consolidation_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    return lines


def write_operator_review_terminal_hold_consolidation_receipt_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_operator_review_terminal_hold_consolidation_receipt_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
