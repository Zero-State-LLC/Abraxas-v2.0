from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionRecordValidationDryRun.v1"
SOURCE_VALIDATION_PLAN_PATH = Path("out/operator_review/global_ingest_operator_decision_record_validation_plan_001.latest.json")
VALIDATION_DRY_RUN_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_validation_dry_run_001.latest.json")
VALIDATION_DRY_RUN_MD_PATH = Path("out/operator_review/global_ingest_operator_decision_record_validation_dry_run_001.latest.md")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _normalize_check_results(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": str(item.get("check_id", "NOT_COMPUTABLE")),
            "passed": bool(item.get("passed", False)),
        }
        for item in sorted(checks, key=lambda item: str(item.get("check_id", "NOT_COMPUTABLE")))
    ]


def build_global_ingest_operator_decision_record_validation_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_VALIDATION_PLAN_PATH
    source_payload = _read_json(source_path)
    source_observed = source_payload is not None

    status = "NOT_COMPUTABLE"
    source_validation_plan_hash = "NOT_COMPUTABLE"
    source_validation_plan_status = "NOT_COMPUTABLE"
    target_pipeline_id = "oracle_signal"
    decision_scope = "IMPLEMENTATION_SPEC_DECISION_REQUIRED"
    source_request_id = "NOT_COMPUTABLE"
    source_template_hash = "NOT_COMPUTABLE"
    source_hashes = {
        "global_ingest_operator_decision_request": "NOT_COMPUTABLE",
        "global_pipeline_gap_backlog": "NOT_COMPUTABLE",
        "global_ingest_alignment_plan": "NOT_COMPUTABLE",
        "notion_operator_decision_backlog": "NOT_COMPUTABLE",
        "notion_spec_completion_queue": "NOT_COMPUTABLE",
        "global_pipeline_doctrine_proof": "NOT_COMPUTABLE",
    }
    executed_validation_checks: list[dict[str, Any]] = []
    required_operator_identity_results: list[dict[str, Any]] = []
    required_decision_field_results: list[dict[str, Any]] = []
    required_acknowledgement_field_results: list[dict[str, Any]] = []
    required_evidence_field_results: list[dict[str, Any]] = []
    required_output_field_results: list[dict[str, Any]] = []
    invariant_results: list[dict[str, Any]] = []
    source_review_artifacts: list[str] = []
    source_validation_summary: dict[str, Any] = {
        "shape_valid": False,
        "validation_blockers": ["source_validation_plan_missing_or_unreadable"],
    }
    validation_passed = False
    simulated_validation_blockers = ["source_validation_plan_missing_or_unreadable"]
    blockers = [
        "source_validation_plan_missing_or_unreadable",
        f"source_path:{SOURCE_VALIDATION_PLAN_PATH}",
    ]

    if source_payload is not None:
        source_validation_plan_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_validation_plan_status = str(source_payload.get("status", "NOT_COMPUTABLE"))
        target_pipeline_id = str(source_payload.get("target_pipeline_id", target_pipeline_id))
        decision_scope = str(source_payload.get("decision_scope", decision_scope))
        source_request_id = str(source_payload.get("source_request_id", source_request_id))
        source_template_hash = str(source_payload.get("source_template_hash", source_template_hash))
        source_hashes = {str(key): str(value) for key, value in dict(source_payload.get("source_hashes", {})).items()}
        source_review_artifacts = [str(item) for item in source_payload.get("source_review_artifacts", [])]
        executed_validation_checks = _normalize_check_results(list(source_payload.get("validation_checks", [])))
        required_operator_identity_results = list(source_payload.get("required_operator_identity_checks", []))
        required_decision_field_results = list(source_payload.get("required_decision_field_checks", []))
        required_acknowledgement_field_results = list(source_payload.get("required_acknowledgement_field_checks", []))
        required_evidence_field_results = list(source_payload.get("required_evidence_field_checks", []))
        required_output_field_results = list(source_payload.get("required_output_field_checks", []))
        invariant_results = list(source_payload.get("invariant_checks", []))
        source_validation_summary = dict(source_payload.get("source_validation_summary", source_validation_summary))

        if source_validation_plan_status != "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_PLAN_READY":
            status = "BLOCKED_BY_GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_PLAN"
            blockers = [f"source_validation_plan_status:{source_validation_plan_status}"]
        else:
            group_presence = all(
                [
                    executed_validation_checks,
                    required_operator_identity_results,
                    required_decision_field_results,
                    required_acknowledgement_field_results,
                    required_evidence_field_results,
                    required_output_field_results,
                    invariant_results,
                ]
            )
            checks_passed = all(item.get("passed", False) for item in executed_validation_checks)
            invariants_passed = all(item.get("passed", False) for item in invariant_results)
            shape_valid = bool(source_validation_summary.get("shape_valid", False))

            validation_passed = group_presence and checks_passed and invariants_passed and shape_valid

            if validation_passed:
                status = "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_DRY_RUN_READY"
                blockers = []
                simulated_validation_blockers = []
            else:
                status = "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_DRY_RUN_FAILED"
                simulated_validation_blockers = sorted(
                    [
                        *([] if group_presence else ["missing_validation_check_group"]),
                        *([] if checks_passed else ["planned_validation_check_failed"]),
                        *([] if invariants_passed else ["validation_plan_invariant_check_failed"]),
                        *([] if shape_valid else ["source_validation_summary_not_shape_valid"]),
                    ]
                )

    simulated_validation_execution = {
        "simulated_only": True,
        "operator_input_required": True,
        "validation_passed": validation_passed,
        "valid_for_execution": False,
        "decision_authority_granted": False,
        "execution_authority_granted": False,
        "validation_blockers": simulated_validation_blockers,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "validation_dry_run_id": "global_ingest_operator_decision_record_validation_dry_run_001",
        "validation_dry_run_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_DRY_RUN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "validation_dry_run_only": True,
        "validation_plan_only": False,
        "simulated_only": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "forecast_weight_allowed": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "operator_input_required": True,
        "valid_for_execution": False,
        "target_pipeline_id": target_pipeline_id,
        "decision_scope": decision_scope,
        "recommended_next_action": "preserve the oracle_signal hold and treat the validation dry run as advisory-only evidence until explicit operator decision input exists",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_validation_plan_path": str(SOURCE_VALIDATION_PLAN_PATH),
        "source_validation_plan_observed": source_observed,
        "source_validation_plan_hash": source_validation_plan_hash,
        "source_validation_plan_status": source_validation_plan_status,
        "source_request_id": source_request_id,
        "source_template_hash": source_template_hash,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "executed_validation_checks": executed_validation_checks,
        "required_operator_identity_results": required_operator_identity_results,
        "required_decision_field_results": required_decision_field_results,
        "required_acknowledgement_field_results": required_acknowledgement_field_results,
        "required_evidence_field_results": required_evidence_field_results,
        "required_output_field_results": required_output_field_results,
        "invariant_results": invariant_results,
        "source_validation_summary": source_validation_summary,
        "simulated_validation_execution": simulated_validation_execution,
        "validation_passed": validation_passed,
        "validation_blockers": simulated_validation_blockers,
        "blockers": blockers,
    }
    packet["validation_dry_run_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "validation_dry_run_hash"})
    return packet


def render_global_ingest_operator_decision_record_validation_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Record Validation Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `validation_passed`: `{packet['validation_passed']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    for item in packet["validation_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_record_validation_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_record_validation_dry_run(root)
    write_canonical_json(target_root / VALIDATION_DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / VALIDATION_DRY_RUN_MD_PATH,
        render_global_ingest_operator_decision_record_validation_dry_run_markdown(packet),
    )
    return packet
