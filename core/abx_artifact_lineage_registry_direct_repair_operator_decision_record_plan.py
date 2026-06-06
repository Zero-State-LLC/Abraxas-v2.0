from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxArtifactLineageRegistryDirectRepairOperatorDecisionRecordPlan.v1"
REQUEST_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request_001.latest.json")
PLAN_JSON_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.json")
PLAN_MD_PATH = Path("out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001.latest.md")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    request = _read_json(root / REQUEST_JSON_PATH)

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_PLAN_READY",
        "decision_record_plan_id": "abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_001",
        "decision_record_plan_hash": "",
        "command": "BUILD_ABX_ARTIFACT_LINEAGE_REGISTRY_DIRECT_REPAIR_OPERATOR_DECISION_RECORD_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "promotion_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "decision_scope": request["decision_scope"],
        "target_surface": request["target_surface"],
        "target_plan_id": request["target_plan_id"],
        "recommended_default_decision": request["recommended_decision"],
        "recommended_next_action": "collect explicit operator decision evidence using the record plan and keep direct repair execution denied until a governed decision exists",
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
            "separate_execution_spec_required",
        ],
        "required_acknowledgement_fields": [
            "advisory_only_acknowledged",
            "non_authoritative_acknowledged",
            "execution_authority_denied_acknowledged",
            "runtime_mutation_denied_acknowledged",
            "canon_mutation_denied_acknowledged",
            "queue_mutation_denied_acknowledged",
        ],
        "required_evidence_fields": [
            "reviewed_request_id",
            "reviewed_request_hash",
            "reviewed_completion_hold_plan_hash",
            "reviewed_external_hold_reasons",
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
                + list(request["follow_on_actions_if_external_evidence_requested"])
                + ["MAINTAIN_DIRECT_REPAIR_COMPLETION_HOLD"]
            )
        ),
        "disallowed_follow_on_actions": list(request["blocked_actions"]),
        "future_record_output_candidates": [
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.json",
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_record_001.latest.md",
        ],
        "required_review_artifacts": [
            "out/operator_review/abx_artifact_lineage_registry_direct_repair_operator_decision_request_001.latest.json",
            "out/sync/abx_artifact_lineage_registry_direct_repair_completion_hold_plan/latest.json",
        ],
        "source_request_path": str(REQUEST_JSON_PATH),
        "source_request_id": request["request_id"],
        "source_hashes": {
            "abx_artifact_lineage_registry_direct_repair_operator_decision_request": request["request_id"],
            **request["source_hashes"],
        },
    }
    packet["decision_record_plan_hash"] = canonical_hash(
        {k: v for k, v in packet.items() if k != "decision_record_plan_hash"}
    )
    return packet


def render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Artifact Lineage Registry Direct Repair Operator Decision Record Plan",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `target_surface`: `{packet['target_surface']}`",
        f"- `recommended_default_decision`: `{packet['recommended_default_decision']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Required Decision Fields",
        "",
    ]
    for item in packet["required_decision_fields"]:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Required Review Artifacts", ""])
    for item in packet["required_review_artifacts"]:
        lines.append(f"- `{item}`")
    return lines


def write_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan(root)
    write_canonical_json(target_root / PLAN_JSON_PATH, packet)
    _write_markdown(
        target_root / PLAN_MD_PATH,
        render_abx_artifact_lineage_registry_direct_repair_operator_decision_record_plan_markdown(packet),
    )
    return packet
