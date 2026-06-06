from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordFinalApprovalDryRun.v1"
SOURCE_FINAL_APPROVAL_PLAN_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_plan_001.latest.json"
)
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.md"
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


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    final_approval_plan = _read_json(root / SOURCE_FINAL_APPROVAL_PLAN_PATH)
    source_final_approval_plan_observed = final_approval_plan is not None

    target_surface = "ABX Artifact Lineage Registry Direct Repair"
    decision_scope = "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    source_final_approval_plan_hash = "NOT_COMPUTABLE"
    source_request_id = "NOT_COMPUTABLE"
    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_hashes = {
        "abx_artifact_lineage_registry_direct_repair_operator_decision_request": "NOT_COMPUTABLE",
        "direct_repair_completion_hold_plan": "NOT_COMPUTABLE",
    }
    source_review_artifacts: list[str] = []
    final_approval_blockers = [
        "source_final_approval_plan_missing_or_unreadable",
        f"source_path:{SOURCE_FINAL_APPROVAL_PLAN_PATH}",
    ]
    status = "NOT_COMPUTABLE"
    final_approval_ready = False

    if final_approval_plan is not None:
        target_surface = str(final_approval_plan.get("target_surface", target_surface))
        decision_scope = str(final_approval_plan.get("decision_scope", decision_scope))
        source_final_approval_plan_hash = str(
            final_approval_plan.get("final_approval_plan_hash", source_final_approval_plan_hash)
        )
        source_request_id = str(final_approval_plan.get("source_request_id", source_request_id))
        source_validation_plan_hash = str(
            final_approval_plan.get("source_validation_plan_hash", source_validation_plan_hash)
        )
        source_hashes = {
            str(key): str(value) for key, value in dict(final_approval_plan.get("source_hashes", {})).items()
        }
        source_review_artifacts = [str(item) for item in final_approval_plan.get("source_review_artifacts", [])]
        required_operator_acknowledgements = [
            str(item) for item in final_approval_plan.get("required_operator_acknowledgements", [])
        ]
        required_operator_approval_fields = [
            str(item) for item in final_approval_plan.get("required_operator_approval_fields", [])
        ]
        final_approval_constraints = [
            str(item) for item in final_approval_plan.get("final_approval_constraints", [])
        ]
        final_approval_provenance_requirements = [
            str(item) for item in final_approval_plan.get("final_approval_provenance_requirements", [])
        ]
        final_approval_hash_requirements = [
            str(item) for item in final_approval_plan.get("final_approval_hash_requirements", [])
        ]

        final_approval_ready = bool(
            final_approval_plan.get("status")
            == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_PLAN_READY"
            and final_approval_plan.get("validation_passed", False)
            and required_operator_acknowledgements
            and required_operator_approval_fields
            and final_approval_constraints
            and final_approval_provenance_requirements
            and final_approval_hash_requirements
        )
        final_approval_blockers = [] if final_approval_ready else ["final_approval_plan_prerequisites_not_satisfied"]
        status = (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_DRY_RUN_READY"
            if final_approval_ready
            else "NOT_COMPUTABLE"
        )
    else:
        required_operator_acknowledgements = []
        required_operator_approval_fields = []
        final_approval_constraints = []
        final_approval_provenance_requirements = []
        final_approval_hash_requirements = []

    simulated_final_approval_execution = {
        "artifact_type": "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordFinalApprovalDryRun.v1.simulated",
        "simulated_only": True,
        "operator_input_required": True,
        "final_approval_ready": final_approval_ready,
        "valid_for_execution": False,
        "approval_granted": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "required_operator_acknowledgements": required_operator_acknowledgements,
        "required_operator_approval_fields": required_operator_approval_fields,
        "final_approval_constraints": final_approval_constraints,
        "final_approval_provenance_requirements": final_approval_provenance_requirements,
        "final_approval_hash_requirements": final_approval_hash_requirements,
        "final_approval_blockers": final_approval_blockers,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001",
        "dry_run_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_DRY_RUN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "final_approval_dry_run_only": True,
        "simulated_only": True,
        "approval_granted": False,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "valid_for_execution": False,
        "target_surface": target_surface,
        "decision_scope": decision_scope,
        "recommended_next_action": "treat the final approval dry run as advisory-only simulated evidence; do not treat dry-run readiness as a final operator approval record or repair execution authorization",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_final_approval_plan_path": str(SOURCE_FINAL_APPROVAL_PLAN_PATH),
        "source_final_approval_plan_observed": source_final_approval_plan_observed,
        "source_final_approval_plan_hash": source_final_approval_plan_hash,
        "source_request_id": source_request_id,
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "final_approval_ready": final_approval_ready,
        "simulated_final_approval_execution": simulated_final_approval_execution,
        "final_approval_blockers": final_approval_blockers,
    }
    packet["dry_run_hash"] = canonical_hash({k: v for k, v in packet.items() if k != "dry_run_hash"})
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Final Approval Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Final Approval Blockers",
        "",
    ]
    for item in packet["final_approval_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_markdown(
            packet
        ),
    )
    return packet
