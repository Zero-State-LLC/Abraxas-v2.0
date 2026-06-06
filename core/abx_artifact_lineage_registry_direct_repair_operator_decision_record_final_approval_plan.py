from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordFinalApprovalPlan.v1"
SOURCE_VALIDATION_DRY_RUN_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_validation_dry_run_001.latest.json"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_001.latest.json"
)
PLAN_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_001.latest.md"
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


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_dry_run = _read_json(root / SOURCE_VALIDATION_DRY_RUN_PATH)
    source_validation_dry_run_observed = source_dry_run is not None

    target_surface = "ABX Artifact Lineage Registry Direct Repair"
    decision_scope = "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    source_validation_dry_run_hash = "NOT_COMPUTABLE"
    source_request_id = "NOT_COMPUTABLE"
    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_hashes = {
        "abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request": "NOT_COMPUTABLE",
        "operator_decision_record_completion_hold_plan": "NOT_COMPUTABLE",
    }
    blockers = [
        "source_final_approval_validation_dry_run_missing_or_unreadable",
        f"source_path:{SOURCE_VALIDATION_DRY_RUN_PATH}",
    ]
    validation_passed = False
    source_review_artifacts: list[str] = []

    required_operator_acknowledgements = [
        "ack_advisory_only_non_authoritative_surface",
        "ack_final_approval_scope_is_repo_local_only",
        "ack_runner_casing_policy_remains_out_of_scope",
        "ack_notion_mapping_evidence_remains_not_computable",
        "ack_no_repair_or_execution_authority_is_granted",
        "ack_final_operator_record_is_still_missing",
    ]
    required_operator_approval_fields = [
        "operator_id",
        "operator_name",
        "operator_role",
        "approval_timestamp_utc",
        "approval_scope_acknowledged",
        "approval_rationale",
        "final_boundary_acknowledged",
    ]
    final_approval_constraints = [
        "final_approval_plan_only_no_execution",
        "no_registry_mutation_from_plan_alone",
        "no_output_pairing_repair_from_plan_alone",
        "no_docs_reference_repair_from_plan_alone",
        "no_runner_policy_override",
        "no_notion_evidence_import",
        "no_final_approval_record_creation",
    ]
    final_approval_provenance_requirements = [
        "source_validation_dry_run_path_must_match",
        "source_validation_dry_run_hash_must_match",
        "source_validation_dry_run_status_must_be_ready",
        "validation_passed_must_remain_true",
    ]
    final_approval_hash_requirements = [
        "final_approval_plan_hash_must_match",
        "source_validation_dry_run_hash_must_match",
        "canonical_json_sha256_required",
    ]

    status = "NOT_COMPUTABLE"
    if source_dry_run is not None:
        target_surface = str(source_dry_run["target_surface"])
        decision_scope = str(source_dry_run["decision_scope"])
        source_validation_dry_run_hash = str(source_dry_run["dry_run_hash"])
        source_request_id = str(source_dry_run["source_request_id"])
        source_validation_plan_hash = str(source_dry_run.get("source_validation_plan_hash", "NOT_COMPUTABLE"))
        source_hashes = {str(key): str(value) for key, value in dict(source_dry_run["source_hashes"]).items()}
        source_review_artifacts = [
            str(SOURCE_VALIDATION_DRY_RUN_PATH),
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_validation_plan_001.latest.json",
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_approval_dry_run_001.latest.json",
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request_001.latest.json",
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_completion_hold_plan_001.latest.json",
        ]
        validation_passed = bool(source_dry_run.get("validation_passed", False))
        ready = (
            source_dry_run.get("status")
            == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_APPROVAL_VALIDATION_DRY_RUN_READY"
            and validation_passed
        )
        blockers = [] if ready else ["source_final_approval_validation_dry_run_not_ready"]
        status = (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_PLAN_READY"
            if ready
            else "NOT_COMPUTABLE"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "final_approval_plan_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_001",
        "final_approval_plan_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "final_approval_plan_only": True,
        "simulated_only": True,
        "approval_granted": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "target_surface": target_surface,
        "decision_scope": decision_scope,
        "recommended_next_action": "prepare only the final operator approval surface for ABX direct repair; do not execute registry, output-pairing, or docs-reference changes from final-approval readiness alone",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_validation_dry_run_path": str(SOURCE_VALIDATION_DRY_RUN_PATH),
        "source_validation_dry_run_observed": source_validation_dry_run_observed,
        "source_validation_dry_run_hash": source_validation_dry_run_hash,
        "source_request_id": source_request_id,
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "validation_passed": validation_passed,
        "required_operator_acknowledgements": required_operator_acknowledgements,
        "required_operator_approval_fields": required_operator_approval_fields,
        "final_approval_constraints": final_approval_constraints,
        "final_approval_provenance_requirements": final_approval_provenance_requirements,
        "final_approval_hash_requirements": final_approval_hash_requirements,
        "blockers": blockers,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
    }
    packet["final_approval_plan_hash"] = canonical_hash(
        {k: v for k, v in packet.items() if k != "final_approval_plan_hash"}
    )
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Final Approval Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Final Approval Blockers",
        "",
    ]
    for item in packet["blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_markdown(
            packet
        ),
    )
    return packet
