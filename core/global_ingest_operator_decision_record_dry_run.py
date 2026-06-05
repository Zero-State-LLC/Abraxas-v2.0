from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionRecordDryRun.v1"
TEMPLATE_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_template_001.latest.json")
DRY_RUN_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.json")
DRY_RUN_MD_PATH = Path("out/operator_review/global_ingest_operator_decision_record_dry_run_001.latest.md")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_global_ingest_operator_decision_record_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    template = _read_json(root / TEMPLATE_JSON_PATH)
    template_observed = template is not None

    target_pipeline_id = "oracle_signal"
    decision_scope = "IMPLEMENTATION_SPEC_DECISION_REQUIRED"
    source_template_hash = "NOT_COMPUTABLE"
    source_request_id = "NOT_COMPUTABLE"
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
    selected_decision = "HOLD"
    status = "NOT_COMPUTABLE"
    validation_blockers = [
        "source_template_missing_or_unreadable",
        f"source_path:{TEMPLATE_JSON_PATH}",
    ]
    shape_valid = False

    if template is not None:
        target_pipeline_id = str(template["target_pipeline_id"])
        decision_scope = str(template["decision_scope"])
        source_template_hash = str(template["template_hash"])
        source_request_id = str(template["source_request_id"])
        source_hashes = {str(key): str(value) for key, value in dict(template["source_hashes"]).items()}
        required_operator_identity_fields = [str(item) for item in template["required_operator_identity_fields"]]
        required_decision_fields = [str(item) for item in template["required_decision_fields"]]
        required_acknowledgement_fields = [str(item) for item in template["required_acknowledgement_fields"]]
        required_evidence_fields = [str(item) for item in template["required_evidence_fields"]]
        required_output_fields = [str(item) for item in template["required_output_fields"]]
        source_review_artifacts = [str(item) for item in template.get("required_review_artifacts", [])]
        selected_decision = str(template["recommended_default_decision"])
        status = "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_DRY_RUN_READY"
        validation_blockers = [
            "operator_identity_missing",
            "operator_decision_not_attested",
            "operator_acknowledgements_not_attested",
            "operator_evidence_bundle_not_attested",
        ]
        shape_valid = True

    simulated_record = {
        "artifact_type": "GlobalIngestOperatorDecisionRecord.v1.simulated",
        "simulated_only": True,
        "decision_record_id": "global_ingest_operator_decision_record_001.simulated",
        "decision_record_hash": "SIMULATED_PENDING_OPERATOR_INPUT",
        "decision_outcome_summary": "SIMULATED_HOLD_PENDING_OPERATOR_INPUT",
        "selected_decision": selected_decision,
        "implementation_authorized": False,
        "execution_authority": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "forecast_weight_allowed": False,
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
        "dry_run_id": "global_ingest_operator_decision_record_dry_run_001",
        "dry_run_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_RECORD_DRY_RUN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
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
        "recommended_next_action": "collect explicit operator decision evidence and bind it to the simulated record shape before any separate implementation spec or oracle_signal work",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_template_path": str(TEMPLATE_JSON_PATH),
        "source_template_observed": template_observed,
        "source_template_hash": source_template_hash,
        "source_request_id": source_request_id,
        "source_hashes": source_hashes,
        "source_review_artifacts": source_review_artifacts,
        "simulated_decision_record": simulated_record,
        "validation_summary": validation_summary,
        "validation_blockers": validation_blockers,
    }
    packet["dry_run_hash"] = canonical_hash({k: v for k, v in packet.items() if k != "dry_run_hash"})
    return packet


def render_global_ingest_operator_decision_record_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Record Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        "",
        "## Validation Blockers",
        "",
    ]
    for item in packet["validation_blockers"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_record_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_record_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_global_ingest_operator_decision_record_dry_run_markdown(packet),
    )
    return packet
