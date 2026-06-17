from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_codegen_phase1_operator_decision_evidence_collection_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON,
    _authority_locks,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxCodegenPhase1OperatorDecisionEvidenceCollectionDryRun.v1"
DRY_RUN_ID = "abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/abx_codegen_phase1_operator_decision_evidence_collection_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")

EXPECTED_SOURCE_STATUS = (
    "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"
)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _plan_ready(plan: Mapping[str, Any]) -> bool:
    return (
        plan.get("schema_version")
        == "AbxCodegenPhase1OperatorDecisionEvidenceCollectionPlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("evidence_collection_only") is True
        and plan.get("operator_input_required") is True
        and plan.get("recommended_next_patch") == "NOT_COMPUTABLE"
        and plan.get("safe_to_auto_continue") is False
        and plan.get("decision_record_created") is False
        and plan.get("authorization_record_lane_authorized") is False
        and plan.get("implementation_unblocked") is False
        and plan.get("execution_authority") is False
        and plan.get("valid_for_execution") is False
        and plan.get("valid_for_implementation") is False
    )


def _simulated_evidence_bundle(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    bundle: list[dict[str, Any]] = []
    groups = plan.get("evidence_bundle_groups", [])
    if not isinstance(groups, list):
        return bundle
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        required_fields = _string_list(group.get("required_fields"))
        bundle.append(
            {
                "group_id": str(group.get("group_id", "NOT_COMPUTABLE")),
                "attested": False,
                "field_count": len(required_fields),
                "missing_fields": required_fields,
            }
        )
    return bundle


def build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / SOURCE_PLAN_JSON)
    source_observed = plan is not None
    plan = plan or {}
    source_ready = source_observed and _plan_ready(plan)

    if source_ready:
        status = "ABX_CODEGEN_PHASE1_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY"
        evaluation_blockers = [
            "operator_identity_not_attested",
            "operator_decision_not_attested",
            "operator_acknowledgements_not_attested",
            "operator_provenance_evidence_not_attested",
            "operator_evidence_output_not_attested",
        ]
    else:
        status = "NOT_COMPUTABLE"
        evaluation_blockers = [
            "source_evidence_collection_plan_missing_or_not_ready",
            f"source_path:{SOURCE_PLAN_JSON}",
        ]

    simulated_bundle = _simulated_evidence_bundle(plan) if source_ready else []
    source_review_artifacts = _string_list(plan.get("required_review_artifacts"))

    readiness_summary = {
        "simulated_only": True,
        "operator_input_required": True,
        "groups_ready": 0,
        "groups_total": len(simulated_bundle),
        "evidence_bundle_complete": False,
        "valid_for_decision_record": False,
        "evaluation_blockers": evaluation_blockers,
    }

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": DRY_RUN_ID,
        "dry_run_hash": "",
        "source_evidence_collection_plan_path": str(SOURCE_PLAN_JSON),
        "source_evidence_collection_plan_observed": source_observed,
        "source_evidence_collection_plan_ready": source_ready,
        "source_evidence_collection_plan_hash": str(
            plan.get("plan_hash", "NOT_COMPUTABLE")
        ),
        "source_review_artifacts": source_review_artifacts,
        "simulated_evidence_bundle": simulated_bundle,
        "readiness_summary": readiness_summary,
        "evaluation_blockers": evaluation_blockers,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "evidence_bundle_created": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "authorization_record_lane_authorized": False,
        "implementation_authorized": False,
        "implementation_unblocked": False,
        "shadow_replay_execution_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "valid_for_decision_record": False,
        "recommended_next_action": (
            "preserve the Codegen Phase 1 operator review hold and use this "
            "simulated evidence bundle to guide external operator evidence collection; "
            "do not create evidence, attestations, decision records, authorization "
            "records, implementation patches, shadow replay, or Codegen execution"
        ),
        "recommended_next_patch": "NOT_COMPUTABLE",
        "recommended_next_state": "hold",
        "disallowed_follow_on_actions": _string_list(
            plan.get("disallowed_follow_on_actions")
        ),
        "authority_locks": _authority_locks(),
    }
    packet["dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dry_run_hash"}
    )
    return packet


def render_abx_codegen_phase1_operator_decision_evidence_collection_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Codegen Phase 1 Operator Decision Evidence Collection Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_evidence_collection_plan_ready`: `{packet['source_evidence_collection_plan_ready']}`",
        f"- `simulated_only`: `{packet['simulated_only']}`",
        f"- `valid_for_decision_record`: `{packet['valid_for_decision_record']}`",
        f"- `recommended_next_patch`: `{packet['recommended_next_patch']}`",
        "",
        "## Evaluation Blockers",
        "",
    ]
    for blocker in packet["evaluation_blockers"]:
        lines.append(f"- `{blocker}`")
    lines.extend(["", "## Simulated Evidence Bundle", ""])
    for item in packet["simulated_evidence_bundle"]:
        lines.append(f"- `{item['group_id']}`: `{item['field_count']}` required fields")
    return lines


def write_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_codegen_phase1_operator_decision_evidence_collection_dry_run(root)
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_abx_codegen_phase1_operator_decision_evidence_collection_dry_run_markdown(
            packet
        ),
    )
    return packet
