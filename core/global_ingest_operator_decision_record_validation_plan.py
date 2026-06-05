from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionRecordValidationPlan.v1"
SOURCE_DRY_RUN_PATH = Path("out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.json")
VALIDATION_PLAN_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_validation_plan_001.latest.json")
VALIDATION_PLAN_MD_PATH = Path("out/operator_review/global_ingest_operator_decision_record_validation_plan_001.latest.md")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _field_checks(group: str, values: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "check_id": f"{group}_{idx:03d}",
            "field": field,
            "present": bool(field),
        }
        for idx, field in enumerate(sorted(values), start=1)
    ]


def _invariant_checks(packet: Mapping[str, Any], simulated_record: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("packet_simulated_only", packet.get("simulated_only"), True),
        ("packet_operator_input_required", packet.get("operator_input_required"), True),
        ("packet_valid_for_execution", packet.get("valid_for_execution"), False),
        ("record_selected_decision", simulated_record.get("selected_decision"), "HOLD"),
        ("record_implementation_authorized", simulated_record.get("implementation_authorized"), False),
        ("record_execution_authority", simulated_record.get("execution_authority"), False),
        ("record_runtime_mutation_allowed", simulated_record.get("runtime_mutation_allowed"), False),
        ("record_canon_mutation_allowed", simulated_record.get("canon_mutation_allowed"), False),
        ("record_forecast_weight_allowed", simulated_record.get("forecast_weight_allowed"), False),
        ("record_valid_for_execution", simulated_record.get("valid_for_execution"), False),
    ]
    return [
        {
            "check_id": check_id,
            "observed": observed,
            "expected": expected,
            "passed": observed == expected,
        }
        for check_id, observed, expected in checks
    ]


def build_global_ingest_operator_decision_record_validation_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    source_path = root / SOURCE_DRY_RUN_PATH
    source_payload = _read_json(source_path)
    source_observed = source_payload is not None

    status = "NOT_COMPUTABLE"
    source_dry_run_hash = "NOT_COMPUTABLE"
    source_dry_run_status = "NOT_COMPUTABLE"
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
    required_operator_identity_fields: list[str] = []
    required_decision_fields: list[str] = []
    required_acknowledgement_fields: list[str] = []
    required_evidence_fields: list[str] = []
    required_output_fields: list[str] = []
    source_review_artifacts: list[str] = []
    simulated_decision_record: dict[str, Any] = {}
    validation_summary: dict[str, Any] = {
        "shape_valid": False,
        "validation_blockers": ["source_dry_run_missing_or_unreadable"],
    }
    blockers = [
        "source_dry_run_missing_or_unreadable",
        f"source_path:{SOURCE_DRY_RUN_PATH}",
    ]

    if source_payload is not None:
        source_dry_run_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        source_dry_run_status = str(source_payload.get("status", "NOT_COMPUTABLE"))
        target_pipeline_id = str(source_payload.get("target_pipeline_id", target_pipeline_id))
        decision_scope = str(source_payload.get("decision_scope", decision_scope))
        source_request_id = str(source_payload.get("source_request_id", source_request_id))
        source_template_hash = str(source_payload.get("source_template_hash", source_template_hash))
        source_hashes = {str(key): str(value) for key, value in dict(source_payload.get("source_hashes", {})).items()}
        source_review_artifacts = [str(item) for item in source_payload.get("source_review_artifacts", [])]
        simulated_decision_record = dict(source_payload.get("simulated_decision_record", {}))
        validation_summary = dict(source_payload.get("validation_summary", validation_summary))
        required_operator_identity_fields = [str(item) for item in simulated_decision_record.get("required_operator_identity_fields", [])]
        required_decision_fields = [str(item) for item in simulated_decision_record.get("required_decision_fields", [])]
        required_acknowledgement_fields = [str(item) for item in simulated_decision_record.get("required_acknowledgement_fields", [])]
        required_evidence_fields = [str(item) for item in simulated_decision_record.get("required_evidence_fields", [])]
        required_output_fields = [str(item) for item in simulated_decision_record.get("required_output_fields", [])]

        if source_dry_run_status != "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_DRY_RUN_READY":
            status = "BLOCKED_BY_GLOBAL_INGEST_OPERATOR_DECISION_RECORD_DRY_RUN"
            blockers = [f"source_dry_run_status:{source_dry_run_status}"]
        else:
            invariant_checks = _invariant_checks(source_payload, simulated_decision_record)
            invariant_failures = [check["check_id"] for check in invariant_checks if not check["passed"]]
            required_groups_ok = all(
                [
                    required_operator_identity_fields,
                    required_decision_fields,
                    required_acknowledgement_fields,
                    required_evidence_fields,
                    required_output_fields,
                ]
            )
            shape_valid = bool(validation_summary.get("shape_valid", False))
            if invariant_failures or (not required_groups_ok) or (not shape_valid):
                status = "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_PLAN_BLOCKED_BY_SIMULATED_RECORD"
                blockers = sorted(
                    [
                        *invariant_failures,
                        *(["required_field_group_missing"] if not required_groups_ok else []),
                        *(["simulated_record_shape_invalid"] if not shape_valid else []),
                    ]
                )
            else:
                status = "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_PLAN_READY"
                blockers = []

    required_operator_identity_checks = _field_checks("operator_identity_field", required_operator_identity_fields)
    required_decision_field_checks = _field_checks("decision_field", required_decision_fields)
    required_acknowledgement_field_checks = _field_checks("acknowledgement_field", required_acknowledgement_fields)
    required_evidence_field_checks = _field_checks("evidence_field", required_evidence_fields)
    required_output_field_checks = _field_checks("output_field", required_output_fields)
    invariant_checks = _invariant_checks(source_payload or {}, simulated_decision_record)

    validation_checks = [
        {"check_id": "source_dry_run_hash_present", "passed": source_dry_run_hash != "NOT_COMPUTABLE"},
        {"check_id": "source_request_id_present", "passed": source_request_id != "NOT_COMPUTABLE"},
        {"check_id": "source_template_hash_present", "passed": source_template_hash != "NOT_COMPUTABLE"},
        {"check_id": "simulated_decision_record_present", "passed": bool(simulated_decision_record)},
        {"check_id": "validation_summary_shape_valid", "passed": bool(validation_summary.get("shape_valid", False))},
    ]

    validation_blockers = sorted(
        list(
            {
                *(["missing_required_operator_identity_fields"] if not required_operator_identity_fields else []),
                *(["missing_required_decision_fields"] if not required_decision_fields else []),
                *(["missing_required_acknowledgement_fields"] if not required_acknowledgement_fields else []),
                *(["missing_required_evidence_fields"] if not required_evidence_fields else []),
                *(["missing_required_output_fields"] if not required_output_fields else []),
                *(["simulated_record_shape_invalid"] if not bool(validation_summary.get("shape_valid", False)) else []),
                *[check["check_id"] for check in invariant_checks if not check["passed"]],
            }
        )
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "validation_plan_id": "global_ingest_operator_decision_record_validation_plan_001",
        "validation_plan_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_RECORD_VALIDATION_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "validation_plan_only": True,
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
        "recommended_next_action": "preserve the oracle_signal hold and verify the simulated decision record shape before collecting any explicit operator decision evidence",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_dry_run_path": str(SOURCE_DRY_RUN_PATH),
        "source_dry_run_observed": source_observed,
        "source_dry_run_hash": source_dry_run_hash,
        "source_dry_run_status": source_dry_run_status,
        "source_request_id": source_request_id,
        "source_template_hash": source_template_hash,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "validation_checks": validation_checks,
        "required_operator_identity_checks": required_operator_identity_checks,
        "required_decision_field_checks": required_decision_field_checks,
        "required_acknowledgement_field_checks": required_acknowledgement_field_checks,
        "required_evidence_field_checks": required_evidence_field_checks,
        "required_output_field_checks": required_output_field_checks,
        "invariant_checks": invariant_checks,
        "source_validation_summary": validation_summary,
        "validation_blockers": validation_blockers,
        "blockers": blockers,
    }
    packet["validation_plan_hash"] = canonical_hash({key: value for key, value in packet.items() if key != "validation_plan_hash"})
    return packet


def render_global_ingest_operator_decision_record_validation_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Record Validation Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    for item in packet["validation_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_record_validation_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_record_validation_plan(root)
    write_canonical_json(target_root / VALIDATION_PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / VALIDATION_PLAN_MD_PATH,
        render_global_ingest_operator_decision_record_validation_plan_markdown(packet),
    )
    return packet
