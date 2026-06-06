from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordApprovalPlan.v1"
SOURCE_VALIDATION_DRY_RUN_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_validation_dry_run_001.latest.json"
)
APPROVAL_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan_001.latest.json"
)
APPROVAL_PLAN_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan_001.latest.md"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_VALIDATION_DRY_RUN_PATH
    source_payload = _read_json(source_path)
    source_observed = source_payload is not None

    status = "NOT_COMPUTABLE"
    source_validation_dry_run_hash = "NOT_COMPUTABLE"
    source_validation_dry_run_status = "NOT_COMPUTABLE"
    validation_passed = False
    target_surface = "ABX Artifact Lineage Registry Direct Repair"
    decision_scope = "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    source_request_id = "NOT_COMPUTABLE"
    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_hashes = {
        "abx_artifact_lineage_registry_direct_repair_operator_decision_request": "NOT_COMPUTABLE",
        "direct_repair_completion_hold_plan": "NOT_COMPUTABLE",
    }
    blockers = [
        "source_validation_dry_run_missing_or_unreadable",
        f"source_path:{SOURCE_VALIDATION_DRY_RUN_PATH}",
    ]
    approval_blockers = list(blockers)
    source_review_artifacts: list[str] = []

    required_operator_acknowledgements = sorted(
        [
            "ack_advisory_only_non_authoritative_surface",
            "ack_no_operator_decision_has_been_recorded_yet",
            "ack_no_execution_authority_is_granted",
            "ack_no_runtime_or_canon_mutation_is_granted",
            "ack_separate_direct_repair_execution_spec_stays_blocked_without_explicit_operator_input",
        ]
    )
    required_operator_approval_fields = sorted(
        [
            "operator_id",
            "operator_name",
            "operator_role",
            "approval_timestamp_utc",
            "approval_scope_acknowledged",
            "approval_rationale",
        ]
    )
    approval_constraints = sorted(
        [
            "approval_plan_only_no_decision_record_creation",
            "no_direct_repair_implementation_authorization_grant",
            "no_execution_authority_grant",
            "no_registry_or_docs_mutation_authority",
            "no_runtime_or_canon_mutation",
            "no_queue_mutation",
        ]
    )
    approval_provenance_requirements = sorted(
        [
            "source_validation_dry_run_path_must_match",
            "source_validation_dry_run_hash_must_match",
            "source_request_id_must_match",
            "source_validation_plan_hash_must_match",
        ]
    )
    approval_hash_requirements = sorted(
        [
            "approval_plan_hash_must_match",
            "source_validation_dry_run_hash_must_match",
            "canonical_json_sha256_required",
        ]
    )

    if source_payload is not None:
        source_validation_dry_run_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_validation_dry_run_status = str(source_payload.get("status", "NOT_COMPUTABLE"))
        validation_passed = bool(source_payload.get("validation_passed", False))
        target_surface = str(source_payload.get("target_surface", target_surface))
        decision_scope = str(source_payload.get("decision_scope", decision_scope))
        source_request_id = str(source_payload.get("source_request_id", source_request_id))
        source_validation_plan_hash = str(
            source_payload.get("source_validation_plan_hash", source_validation_plan_hash)
        )
        source_hashes = {str(key): str(value) for key, value in dict(source_payload.get("source_hashes", {})).items()}
        source_review_artifacts = [
            str(SOURCE_VALIDATION_DRY_RUN_PATH),
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_validation_plan_001.latest.json",
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request_001.latest.json",
            "out/sync/abx_artifact_lineage_registry_direct_repair_completion_hold_plan/latest.json",
        ]

        if (
            source_validation_dry_run_status
            != "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_VALIDATION_DRY_RUN_READY"
        ):
            status = "BLOCKED_BY_ABX_OPERATOR_DECISION_RECORD_VALIDATION_DRY_RUN"
            blockers = [f"source_validation_dry_run_status:{source_validation_dry_run_status}"]
            approval_blockers = list(blockers)
        elif not validation_passed:
            status = "BLOCKED_BY_FAILED_ABX_VALIDATION_DRY_RUN"
            blockers = ["validation_passed=false"]
            approval_blockers = list(blockers)
        else:
            status = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_APPROVAL_PLAN_READY"
            blockers = []
            approval_blockers = []

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "approval_plan_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan_001",
        "approval_plan_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_APPROVAL_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "approval_plan_only": True,
        "validation_dry_run_only": False,
        "simulated_only": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "operator_approval_required": True,
        "valid_for_execution": False,
        "approval_granted": False,
        "authorization_granted": False,
        "target_surface": target_surface,
        "decision_scope": decision_scope,
        "recommended_next_action": "preserve the ABX direct-repair hold and prepare only the approval-surface requirements; explicit operator decision evidence is still required before any separate execution path can exist",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_validation_dry_run_path": str(SOURCE_VALIDATION_DRY_RUN_PATH),
        "source_validation_dry_run_observed": source_observed,
        "source_validation_dry_run_hash": source_validation_dry_run_hash,
        "source_validation_dry_run_status": source_validation_dry_run_status,
        "source_request_id": source_request_id,
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "validation_passed": validation_passed,
        "required_operator_acknowledgements": required_operator_acknowledgements,
        "required_operator_approval_fields": required_operator_approval_fields,
        "approval_constraints": approval_constraints,
        "approval_provenance_requirements": approval_provenance_requirements,
        "approval_hash_requirements": approval_hash_requirements,
        "approval_blockers": approval_blockers,
        "blockers": blockers,
    }
    packet["approval_plan_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "approval_plan_hash"})
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Approval Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Approval Blockers",
        "",
    ]
    for item in packet["approval_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan(root)
    write_canonical_json(target_root / APPROVAL_PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / APPROVAL_PLAN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_plan_markdown(packet),
    )
    return packet
