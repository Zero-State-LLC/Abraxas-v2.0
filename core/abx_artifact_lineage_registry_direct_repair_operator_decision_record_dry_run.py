from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordDryRun.v1"
PLAN_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.json")
DRY_RUN_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.json")
DRY_RUN_MD_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001.latest.md")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / PLAN_JSON_PATH)
    plan_observed = plan is not None

    target_surface = "ABX Artifact Lineage Registry Direct Repair"
    decision_scope = "DIRECT_REPAIR_EXECUTION_DECISION_REQUIRED"
    source_plan_hash = "NOT_COMPUTABLE"
    source_request_id = "NOT_COMPUTABLE"
    source_hashes = {
        "abx_artifact_lineage_registry_direct_repair_operator_decision_request": "NOT_COMPUTABLE",
        "direct_repair_completion_hold_plan": "NOT_COMPUTABLE",
    }
    required_operator_identity_fields: list[str] = []
    required_decision_fields: list[str] = []
    required_acknowledgement_fields: list[str] = []
    required_evidence_fields: list[str] = []
    required_output_fields: list[str] = []
    source_review_artifacts: list[str] = []
    selected_decision = "HOLD"
    status = "NOT_COMPUTABLE"
    validation_blockers = [
        "source_plan_missing_or_unreadable",
        f"source_path:{PLAN_JSON_PATH}",
    ]
    shape_valid = False

    if plan is not None:
        target_surface = str(plan["target_surface"])
        decision_scope = str(plan["decision_scope"])
        source_plan_hash = str(plan["decision_record_plan_hash"])
        source_request_id = str(plan["source_request_id"])
        source_hashes = {str(key): str(value) for key, value in dict(plan["source_hashes"]).items()}
        required_operator_identity_fields = [str(item) for item in plan["required_operator_identity_fields"]]
        required_decision_fields = [str(item) for item in plan["required_decision_fields"]]
        required_acknowledgement_fields = [str(item) for item in plan["required_acknowledgement_fields"]]
        required_evidence_fields = [str(item) for item in plan["required_evidence_fields"]]
        required_output_fields = [str(item) for item in plan["required_output_fields"]]
        source_review_artifacts = [str(item) for item in plan.get("required_review_artifacts", [])]
        selected_decision = str(plan["recommended_default_decision"])
        status = "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
        validation_blockers = [
            "operator_identity_missing",
            "operator_decision_not_attested",
            "operator_acknowledgements_not_attested",
            "operator_evidence_bundle_not_attested",
        ]
        shape_valid = True

    simulated_record = {
        "artifact_type": "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecord.v1.simulated",
        "simulated_only": True,
        "decision_record_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.simulated",
        "decision_record_hash": "SIMULATED_PENDING_OPERATOR_INPUT",
        "decision_outcome_summary": "SIMULATED_HOLD_PENDING_OPERATOR_INPUT",
        "selected_decision": selected_decision,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "valid_for_execution": False,
        "required_operator_identity_fields": required_operator_identity_fields,
        "required_decision_fields": required_decision_fields,
        "required_acknowledgement_fields": required_acknowledgement_fields,
        "required_evidence_fields": required_evidence_fields,
        "required_output_fields": required_output_fields,
    }

    validation_summary = {
        "shape_valid": shape_valid,
        "simulated_only": True,
        "operator_input_required": True,
        "decision_authority_granted": False,
        "execution_authority_granted": False,
        "valid_for_execution": False,
        "validation_blockers": validation_blockers,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_001",
        "dry_run_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_DRY_RUN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "simulated_only": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "operator_input_required": True,
        "valid_for_execution": False,
        "target_surface": target_surface,
        "decision_scope": decision_scope,
        "recommended_next_action": "collect explicit operator decision evidence and bind it to the simulated direct-repair record shape before any separate execution spec can exist",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_plan_path": str(PLAN_JSON_PATH),
        "source_plan_observed": plan_observed,
        "source_plan_hash": source_plan_hash,
        "source_request_id": source_request_id,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "simulated_decision_record": simulated_record,
        "validation_summary": validation_summary,
        "validation_blockers": validation_blockers,
    }
    packet["dry_run_hash"] = canonical_hash({k: v for k, v in packet.items() if k != "dry_run_hash"})
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    for item in packet["validation_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_dry_run_markdown(packet),
    )
    return packet
