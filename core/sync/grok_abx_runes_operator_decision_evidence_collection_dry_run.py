from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.grok_abx_runes_operator_decision_evidence_collection_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON_PATH,
    _authority_locks,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "GrokAbxRunesOperatorDecisionEvidenceCollectionDryRun.v1"
DRY_RUN_ID = "grok_abx_runes_operator_decision_evidence_collection_dry_run_001"
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _plan_ready(plan: Mapping[str, Any]) -> bool:
    return (
        plan.get("schema_version")
        == "GrokAbxRunesOperatorDecisionEvidenceCollectionPlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("source_review_ready") is True
        and plan.get("evidence_collection_only") is True
        and plan.get("operator_input_required") is True
        and plan.get("operator_evidence_collected") is False
        and plan.get("operator_attestation_created") is False
        and plan.get("evidence_bundle_created") is False
        and plan.get("decision_record_created") is False
        and plan.get("authorization_record_created") is False
        and plan.get("external_backlog_accepted") is False
        and plan.get("separate_registration_planning_authorized") is False
        and plan.get("catalog_mutation_authorized") is False
        and plan.get("rune_registration_authorized") is False
        and plan.get("yggdrasil_binding_mutation_authorized") is False
        and plan.get("recommended_next_lane") == NOT_COMPUTABLE
        and plan.get("safe_to_auto_continue") is False
        and plan.get("valid_for_execution") is False
        and plan.get("valid_for_implementation") is False
    )


def _simulated_bundle(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    groups = plan.get("evidence_bundle_groups")
    if not isinstance(groups, list):
        return []

    bundle: list[dict[str, Any]] = []
    for group in groups:
        if not isinstance(group, Mapping):
            continue
        required_fields = _string_list(group.get("required_fields"))
        bundle.append(
            {
                "group_id": str(group.get("group_id", NOT_COMPUTABLE)),
                "attested": False,
                "field_count": len(required_fields),
                "missing_fields": required_fields,
            }
        )
    return bundle


def build_grok_abx_runes_operator_decision_evidence_collection_dry_run(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    plan = _read_json(root / SOURCE_PLAN_JSON_PATH)
    source_observed = plan is not None
    plan = plan or {}
    source_ready = source_observed and _plan_ready(plan)

    if source_ready:
        status = "GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_DRY_RUN_READY"
        evaluation_blockers = [
            "operator_identity_not_attested",
            "grok_claim_disposition_not_attested",
            "authority_acknowledgements_not_attested",
            "provenance_evidence_not_attested",
            "evidence_outputs_not_attested",
        ]
    else:
        status = NOT_COMPUTABLE
        evaluation_blockers = [
            "source_evidence_collection_plan_missing_or_not_ready",
            f"source_path:{SOURCE_PLAN_JSON_PATH.as_posix()}",
        ]

    simulated_bundle = _simulated_bundle(plan) if source_ready else []
    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dry_run_id": DRY_RUN_ID,
        "status": status,
        "source_evidence_collection_plan_path": SOURCE_PLAN_JSON_PATH.as_posix(),
        "source_evidence_collection_plan_observed": source_observed,
        "source_evidence_collection_plan_ready": source_ready,
        "source_evidence_collection_plan_hash": str(
            plan.get("plan_hash", NOT_COMPUTABLE)
        ),
        "source_review_artifacts": _string_list(plan.get("required_review_artifacts")),
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_evidence_collected": False,
        "evidence_bundle_created": False,
        "decision_record_created": False,
        "authorization_record_created": False,
        "external_backlog_accepted": False,
        "separate_registration_planning_authorized": False,
        "catalog_mutation_authorized": False,
        "rune_registration_authorized": False,
        "yggdrasil_binding_mutation_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "pr_merge_authority": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "simulated_evidence_bundle": simulated_bundle,
        "readiness_summary": {
            "simulated_only": True,
            "operator_input_required": True,
            "groups_ready": 0,
            "groups_total": len(simulated_bundle),
            "required_field_count": sum(
                int(item["field_count"]) for item in simulated_bundle
            ),
            "evidence_bundle_complete": False,
            "valid_for_decision_record": False,
            "evaluation_blockers": evaluation_blockers,
        },
        "evaluation_blockers": evaluation_blockers,
        "recommended_next_action": (
            "preserve the Grok ABX-Runes operator review hold and use this "
            "simulated missing-attestation bundle only as an external evidence "
            "collection checklist; do not create evidence bundles, decision records, "
            "rune registrations, catalog changes, YGGDRASIL mutations, writebacks, "
            "PR merges, runtime changes, or execution changes"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "implementation_authorized": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "valid_for_decision_record": False,
        "disallowed_follow_on_actions": _string_list(
            plan.get("disallowed_follow_on_actions")
        ),
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {
        **packet,
        "dry_run_hash": canonical_hash(packet),
    }


def render_grok_abx_runes_operator_decision_evidence_collection_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Grok ABX-Runes Operator Decision Evidence Collection Dry Run",
        "",
        f"- dry_run_id: {packet['dry_run_id']}",
        f"- status: {packet['status']}",
        f"- source_evidence_collection_plan_ready: {packet['source_evidence_collection_plan_ready']}",
        f"- simulated_only: {packet['simulated_only']}",
        f"- evidence_bundle_created: {packet['evidence_bundle_created']}",
        f"- valid_for_decision_record: {packet['valid_for_decision_record']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Evaluation Blockers",
    ]
    for blocker in packet["evaluation_blockers"]:
        lines.append(f"- {blocker}")

    lines.extend(["", "## Simulated Evidence Bundle"])
    for item in packet["simulated_evidence_bundle"]:
        lines.append(
            f"- {item['group_id']}: {item['field_count']} required fields missing"
        )
    return lines


def write_grok_abx_runes_operator_decision_evidence_collection_dry_run(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_grok_abx_runes_operator_decision_evidence_collection_dry_run(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / DRY_RUN_JSON_PATH, packet)
    md_path = root / DRY_RUN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_grok_abx_runes_operator_decision_evidence_collection_dry_run_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
