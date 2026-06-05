from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "GlobalIngestOperatorDecisionRecordTemplate.v1"
REQUEST_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_request_001.latest.json")
TEMPLATE_JSON_PATH = Path("out/operator_review/global_ingest_operator_decision_record_template_001.latest.json")
TEMPLATE_MD_PATH = Path("out/operator_review/global_ingest_operator_decision_record_template_001.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_global_ingest_operator_decision_record_template(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_JSON_PATH)

    template: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "GLOBAL_INGEST_OPERATOR_DECISION_RECORD_TEMPLATE_READY",
        "template_id": "global_ingest_operator_decision_record_template_001",
        "template_hash": "",
        "command": "BUILD_GLOBAL_INGEST_OPERATOR_DECISION_RECORD_TEMPLATE_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "forecast_weight_allowed": False,
        "runtime_mutation_allowed": False,
        "baseline_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "decision_scope": request["decision_scope"],
        "target_pipeline_id": request["target_pipeline_id"],
        "target_display_name": request["target_display_name"],
        "recommended_default_decision": request["recommended_decision"],
        "recommended_next_action": "collect explicit operator decision evidence using the template and keep oracle_signal unimplemented until a governed decision exists",
        "recommended_next_patch": "NOT_COMPUTABLE",
        "safe_to_auto_continue": False,
        "operator_input_required": True,
        "implementation_authorized": False,
        "spec_authoring_only_if_approved": True,
        "decision_options": list(request["decision_options"]),
        "required_operator_identity_fields": [
            "operator_id",
            "operator_name",
            "operator_role",
            "decision_timestamp_utc",
        ],
        "required_decision_fields": [
            "selected_decision",
            "decision_rationale",
            "decision_scope_acknowledged",
            "separate_implementation_spec_required",
        ],
        "required_acknowledgement_fields": [
            "advisory_only_acknowledged",
            "non_authoritative_acknowledged",
            "execution_authority_denied_acknowledged",
            "runtime_mutation_denied_acknowledged",
            "canon_mutation_denied_acknowledged",
            "forecast_weight_denied_acknowledged",
        ],
        "required_evidence_fields": [
            "reviewed_request_id",
            "reviewed_request_hash",
            "reviewed_doctrine_review_hash",
            "reviewed_gap_backlog_hash",
            "reviewed_notion_decision_backlog_hash",
            "reviewed_notion_spec_completion_queue_hash",
        ],
        "required_output_fields": [
            "decision_record_id",
            "decision_record_hash",
            "decision_outcome_summary",
        ],
        "allowed_follow_on_actions": sorted(
            set(
                list(request["follow_on_actions_if_approved"])
                + list(request["follow_on_actions_if_rejected"])
                + list(request["follow_on_actions_if_fresh_spec_requested"])
                + ["MAINTAIN_GLOBAL_INGEST_HOLD"]
            )
        ),
        "disallowed_follow_on_actions": [
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
        ],
        "future_record_output_candidates": [
            "out/operator_review/global_ingest_operator_decision_record_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            "out/operator_review/global_ingest_operator_decision_request_001.latest.json",
            "out/operator_review/global_ingest_operator_decision_record_template_001.latest.json",
            "out/sync/oracle_signal_research_intake_receipt/latest.json",
            "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json",
            "out/sync/oracle_confidence_calibration_plan/latest.json",
            "out/global_pipeline_doctrine_validation/operator_review_packet.latest.json",
        ],
        "source_request_path": str(REQUEST_JSON_PATH),
        "source_request_id": request["request_id"],
        "source_hashes": {
            "global_ingest_operator_decision_request": request["request_id"],
            **request["source_hashes"],
        },
    }
    template["template_hash"] = canonical_hash({k: v for k, v in template.items() if k != "template_hash"})
    return template


def render_global_ingest_operator_decision_record_template_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Global Ingest Operator Decision Record Template",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_pipeline_id`: `{packet['target_pipeline_id']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Required Operator Identity Fields",
        "",
    ]
    for item in packet["required_operator_identity_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Required Decision Fields",
            "",
        ]
    )
    for item in packet["required_decision_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Required Acknowledgement Fields",
            "",
        ]
    )
    for item in packet["required_acknowledgement_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Future Record Output Candidates",
            "",
        ]
    )
    for item in packet["future_record_output_candidates"]:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## Required Review Artifacts",
            "",
        ]
    )
    for item in packet["required_review_artifacts"]:
        lines.append(f"- `{item}`")
    return lines


def write_global_ingest_operator_decision_record_template(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_global_ingest_operator_decision_record_template(root)
    write_canonical_json(target_root / TEMPLATE_JSON_PATH, packet)
    _write_markdown(
        target_root / TEMPLATE_MD_PATH,
        render_global_ingest_operator_decision_record_template_markdown(packet),
    )
    return packet
