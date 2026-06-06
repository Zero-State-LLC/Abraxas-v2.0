from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordFinalApprovalValidationDryRun.v1"
VALIDATION_PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_001.latest.json"
)
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_001.latest.md"
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


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    validation_plan = _read_json(root / VALIDATION_PLAN_JSON_PATH)
    source_validation_plan_observed = validation_plan is not None

    target_surface = "ABX Artifact Lineage Registry Direct Repair"
    decision_scope = "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_request_id = "NOT_COMPUTABLE"
    source_hashes = {
        "abx_artifact_lineage_registry_direct_repair_operator_decision_request": "NOT_COMPUTABLE",
        "direct_repair_completion_hold_plan": "NOT_COMPUTABLE",
    }
    validation_checks: list[dict[str, Any]] = []
    validation_summary = {
        "shape_valid": False,
        "simulated_only": True,
        "validation_plan_ready": False,
        "execution_authority_granted": False,
        "recommended_next_patch_not_computable": True,
    }
    validation_blockers = [
        "source_validation_plan_missing_or_unreadable",
        f"source_path:{VALIDATION_PLAN_JSON_PATH}",
    ]
    status = "NOT_COMPUTABLE"
    validation_passed = False

    if validation_plan is not None:
        target_surface = str(validation_plan["target_surface"])
        decision_scope = str(validation_plan["decision_scope"])
        source_validation_plan_hash = str(validation_plan["validation_plan_hash"])
        source_request_id = str(validation_plan["source_request_id"])
        source_hashes = {str(key): str(value) for key, value in dict(validation_plan["source_hashes"]).items()}
        validation_checks = [
            {
                "check_id": "validation_plan_ready",
                "passed": validation_plan.get("status")
                == "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_VALIDATION_PLAN_READY",
            },
            {
                "check_id": "validation_passed",
                "passed": bool(validation_plan.get("validation_passed", False)),
            },
            {
                "check_id": "execution_authority_denied",
                "passed": validation_plan.get("execution_authority") is False,
            },
            {
                "check_id": "recommended_next_patch_not_computable",
                "passed": validation_plan.get("recommended_next_patch") == "NOT_COMPUTABLE",
            },
        ]
        validation_passed = all(item["passed"] for item in validation_checks)
        validation_summary = {
            "shape_valid": True,
            "simulated_only": True,
            "validation_plan_ready": bool(validation_checks[0]["passed"]),
            "execution_authority_granted": False,
            "recommended_next_patch_not_computable": bool(validation_checks[3]["passed"]),
        }
        validation_blockers = [] if validation_passed else ["validation_plan_checks_failed"]
        status = (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_VALIDATION_DRY_RUN_READY"
            if validation_passed
            else "NOT_COMPUTABLE"
        )

    simulated_validation_execution = {
        "artifact_type": "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordFinalApprovalValidationDryRun.v1.simulated",
        "simulated_only": True,
        "validation_run_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_001.simulated",
        "validation_run_hash": "SIMULATED_VALIDATION_PENDING_OPERATOR_INPUT",
        "validation_outcome_summary": "SIMULATED_VALIDATION_HOLD_PENDING_OPERATOR_INPUT",
        "validation_passed": validation_passed,
        "execution_authority": False,
        "valid_for_execution": False,
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_001",
        "dry_run_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_VALIDATION_DRY_RUN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "simulated_only": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "valid_for_execution": False,
        "target_surface": target_surface,
        "decision_scope": decision_scope,
        "recommended_next_action": "simulate validation of the ABX direct-repair final approval surface only; explicit operator decision evidence is still required before any separate execution path can exist",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_validation_plan_path": str(VALIDATION_PLAN_JSON_PATH),
        "source_validation_plan_observed": source_validation_plan_observed,
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_request_id": source_request_id,
        "source_hashes": source_hashes,
        "validation_checks": validation_checks,
        "validation_summary": validation_summary,
        "validation_passed": validation_passed,
        "simulated_validation_execution": simulated_validation_execution,
        "validation_blockers": validation_blockers,
    }
    packet["dry_run_hash"] = canonical_hash({k: v for k, v in packet.items() if k != "dry_run_hash"})
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Final Approval Validation Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        "",
        "## Validation Checks",
        "",
    ]
    for item in packet["validation_checks"]:
        lines.append(f"- `{item['check_id']}`: `{item['passed']}`")
    lines.extend(["", "## Validation Blockers", ""])
    for item in packet["validation_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run(
        root
    )
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_dry_run_markdown(
            packet
        ),
    )
    return packet
