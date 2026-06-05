from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionEvidenceCollectionPlan.v1"
REQUEST_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.json")
TEMPLATE_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_template_001.latest.json")
PLAN_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.json")
PLAN_MD_PATH = Path("out/operator_review/global_ingest_operator_decision_evidence_collection_plan_001.latest.md")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _field_plan(group_id: str, fields: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "step_id": f"{group_id}_{idx:03d}",
            "field": field,
            "required": True,
        }
        for idx, field in enumerate(fields, start=1)
    ]


def build_global_ingest_operator_decision_evidence_collection_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_JSON_PATH)
    template = _read_json(root / TEMPLATE_JSON_PATH)

    request_observed = request is not None
    template_observed = template is not None
    blockers: list[str] = []
    status = "NOT_COMPUTABLE"
    request_id = "NOT_COMPUTABLE"
    request_hash = "NOT_COMPUTABLE"
    template_hash = "NOT_COMPUTABLE"
    decision_scope = "IMPLEMENTATION_SPEC_DECISION_REQUIRED"
    target_pipeline_id = "oracle_signal"
    target_display_name = "Oracle Signal"
    recommended_default_decision = "HOLD"
    decision_options: list[str] = []
    required_operator_identity_fields: list[str] = []
    required_decision_fields: list[str] = []
    required_acknowledgement_fields: list[str] = []
    required_evidence_fields: list[str] = []
    required_output_fields: list[str] = []
    future_record_output_candidates = [
        "out/operator_review/global_ingest_operator_decision_record_001.latest.json",
        "out/operator_review/global_ingest_operator_decision_record_001.latest.md",
    ]
    source_hashes: dict[str, str] = {
        "global_ingest_operator_decision_request": "NOT_COMPUTABLE",
        "global_pipeline_gap_backlog": "NOT_COMPUTABLE",
        "global_ingest_alignment_plan": "NOT_COMPUTABLE",
        "oracle_signal_intake_boundary_implementation_plan": "NOT_COMPUTABLE",
        "notion_operator_decision_backlog": "NOT_COMPUTABLE",
        "notion_spec_completion_queue": "NOT_COMPUTABLE",
        "global_pipeline_doctrine_proof": "NOT_COMPUTABLE",
    }

    if request is None:
        blockers.append(f"missing_request:{REQUEST_JSON_PATH}")
    else:
        request_id = str(request["request_id"])
        request_hash = request_id
        decision_scope = str(request["decision_scope"])
        target_pipeline_id = str(request["target_pipeline_id"])
        target_display_name = str(request["target_display_name"])
        decision_options = [str(item) for item in request["decision_options"]]
        source_hashes = {
            "global_ingest_operator_decision_request": request_id,
            **{str(key): str(value) for key, value in dict(request["source_hashes"]).items()},
        }

    if template is None:
        blockers.append(f"missing_template:{TEMPLATE_JSON_PATH}")
    else:
        template_hash = str(template["template_hash"])
        recommended_default_decision = str(template["recommended_default_decision"])
        required_operator_identity_fields = [
            str(item) for item in template["required_operator_identity_fields"]
        ]
        required_decision_fields = [str(item) for item in template["required_decision_fields"]]
        required_acknowledgement_fields = [
            str(item) for item in template["required_acknowledgement_fields"]
        ]
        required_evidence_fields = [str(item) for item in template["required_evidence_fields"]]
        required_output_fields = [str(item) for item in template["required_output_fields"]]
        future_record_output_candidates = [
            str(item) for item in template["future_record_output_candidates"]
        ]

    if request_observed and template_observed:
        status = "GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "plan_id": "global_ingest_operator_decision_evidence_collection_plan_001",
        "plan_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_001",
        "artifact_type": "GlobalIngestOperatorDecisionEvidenceCollectionPlan.v1",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_collection_only": True,
        "operator_input_required": True,
        "implementation_authorized": False,
        "execution_authority": False,
        "promotion_allowed": False,
        "forecast_weight_allowed": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "valid_for_execution": False,
        "decision_scope": decision_scope,
        "target_pipeline_id": target_pipeline_id,
        "target_display_name": target_display_name,
        "recommended_default_decision": recommended_default_decision,
        "decision_options": decision_options,
        "recommended_next_action": (
            "collect explicit operator decision evidence using the reviewed Oracle research receipt, oracle intake boundary implementation plan, and Oracle confidence calibration plan; keep oracle_signal unimplemented until a governed decision record exists"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "source_request_path": str(REQUEST_JSON_PATH),
        "source_request_observed": request_observed,
        "source_request_id": request_id,
        "source_request_hash": request_hash,
        "source_template_path": str(TEMPLATE_JSON_PATH),
        "source_template_observed": template_observed,
        "source_template_hash": template_hash,
        "evidence_bundle_groups": [
            {
                "group_id": "operator_identity",
                "required_fields": required_operator_identity_fields,
                "collection_steps": _field_plan(
                    "operator_identity", required_operator_identity_fields
                ),
            },
            {
                "group_id": "decision",
                "required_fields": required_decision_fields,
                "collection_steps": _field_plan("decision", required_decision_fields),
            },
            {
                "group_id": "acknowledgements",
                "required_fields": required_acknowledgement_fields,
                "collection_steps": _field_plan(
                    "acknowledgement", required_acknowledgement_fields
                ),
            },
            {
                "group_id": "provenance_evidence",
                "required_fields": required_evidence_fields,
                "collection_steps": _field_plan("evidence", required_evidence_fields),
            },
            {
                "group_id": "record_outputs",
                "required_fields": required_output_fields,
                "collection_steps": _field_plan("output", required_output_fields),
            },
        ],
        "required_review_artifacts": [
            "out/operator_review/global_ingest_operator_decision_request_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_record_template_001.latest.json",
            "out/sync/oracle_signal_research_intake_receipt/latest.json",
            "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json",
            "out/sync/oracle_confidence_calibration_plan/latest.json",
            "out/sync/oracle_confidence_calibration_contract_plan/latest.json",
            "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json",
        ],
        "future_record_output_candidates": future_record_output_candidates,
        "disallowed_follow_on_actions": [
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
        ],
        "evidence_readiness_summary": {
            "request_observed": request_observed,
            "template_observed": template_observed,
            "required_group_count": 5,
            "blocker_count": len(blockers),
        },
        "blockers": blockers,
        "source_hashes": source_hashes,
    }
    packet["plan_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "plan_hash"}
    )
    return packet


def render_global_ingest_operator_decision_evidence_collection_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Evidence Collection Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_state`: `{packet['recommended_next_state']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Required Review Artifacts",
        "",
    ]
    for item in packet["required_review_artifacts"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Evidence Bundle Groups", ""])
    for group in packet["evidence_bundle_groups"]:
        lines.append(f"- `{group['group_id']}`")
        for field in group["required_fields"]:
            lines.append(f"  - `{field}`")
    if packet["blockers"]:
        lines.extend(["", "## Blockers", ""])
        for item in packet["blockers"]:
            lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_evidence_collection_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_evidence_collection_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_global_ingest_operator_decision_evidence_collection_plan_markdown(packet),
    )
    return packet
