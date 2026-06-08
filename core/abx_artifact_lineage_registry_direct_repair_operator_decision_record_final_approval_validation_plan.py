from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordFinalApprovalValidationPlan.v1"
SOURCE_DRY_RUN_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_dry_run_001.latest.json"
)
PLAN_JSON_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_001.latest.json"
)
PLAN_MD_PATH = Path(
    "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_001.latest.md"
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


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    dry_run = _read_json(root / SOURCE_DRY_RUN_PATH)
    dry_run_observed = dry_run is not None

    target_surface = "ABX Artifact Lineage Registry Direct Repair"
    decision_scope = "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    source_dry_run_hash = "NOT_COMPUTABLE"
    source_request_id = "NOT_COMPUTABLE"
    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_hashes = {
        "abx_artifact_lineage_registry_direct_repair_operator_decision_record_operator_decision_request": "NOT_COMPUTABLE",
        "operator_decision_record_completion_hold_plan": "NOT_COMPUTABLE",
    }
    validation_checks: list[dict[str, Any]] = []
    invariants_verified = {
        "simulated_only": True,
        "execution_authority_denied": True,
        "recommended_next_patch_not_computable": True,
    }
    validation_passed = False
    status = "NOT_COMPUTABLE"
    blockers = [
        "source_final_approval_dry_run_missing_or_unreadable",
        f"source_path:{SOURCE_DRY_RUN_PATH}",
    ]

    if dry_run is not None:
        target_surface = str(dry_run["target_surface"])
        decision_scope = str(dry_run["decision_scope"])
        source_dry_run_hash = str(dry_run["dry_run_hash"])
        source_request_id = str(dry_run["source_request_id"])
        source_validation_plan_hash = str(dry_run.get("source_validation_plan_hash", "NOT_COMPUTABLE"))
        source_hashes = {str(key): str(value) for key, value in dict(dry_run["source_hashes"]).items()}
        validation_checks = [
            {
                "check_id": "final_approval_ready",
                "passed": bool(dry_run.get("final_approval_ready", False)),
            },
            {
                "check_id": "simulated_only",
                "passed": bool(dry_run.get("simulated_only", False)),
            },
            {
                "check_id": "execution_authority_denied",
                "passed": dry_run.get("execution_authority") is False,
            },
            {
                "check_id": "recommended_next_patch_not_computable",
                "passed": dry_run.get("recommended_next_patch") == "NOT_COMPUTABLE",
            },
        ]
        invariants_verified = {
            "simulated_only": bool(dry_run.get("simulated_only", False)),
            "execution_authority_denied": dry_run.get("execution_authority") is False,
            "recommended_next_patch_not_computable": dry_run.get("recommended_next_patch") == "NOT_COMPUTABLE",
        }
        validation_passed = all(item["passed"] for item in validation_checks)
        status = (
            "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_VALIDATION_PLAN_READY"
        )
        blockers = [] if validation_passed else ["final_approval_dry_run_validation_checks_failed"]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "validation_plan_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_001",
        "validation_plan_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_FINAL_APPROVAL_VALIDATION_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "valid_for_execution": False,
        "target_surface": target_surface,
        "decision_scope": decision_scope,
        "recommended_next_action": "validate the simulated ABX direct-repair final approval surface only; explicit operator decision evidence is still required before any separate execution path can exist",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_dry_run_path": str(SOURCE_DRY_RUN_PATH),
        "source_dry_run_observed": dry_run_observed,
        "source_dry_run_hash": source_dry_run_hash,
        "source_request_id": source_request_id,
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_hashes": source_hashes,
        "validation_checks": validation_checks,
        "invariants_verified": invariants_verified,
        "validation_passed": validation_passed,
        "blockers": blockers,
    }
    packet["validation_plan_hash"] = canonical_hash({k: v for k, v in packet.items() if k != "validation_plan_hash"})
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Final Approval Validation Plan",
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
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = (
        build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan(
            root
        )
    )
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_final_approval_validation_plan_markdown(
            packet
        ),
    )
    return packet
