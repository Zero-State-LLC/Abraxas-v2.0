from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.grok_abx_runes_operator_decision_record_review import (
    REVIEW_JSON_PATH as SOURCE_REVIEW_JSON_PATH,
)

SCHEMA_VERSION = "GrokAbxRunesOperatorDecisionEvidenceCollectionPlan.v1"
PLAN_ID = "grok_abx_runes_operator_decision_evidence_collection_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/grok_abx_runes_operator_decision_evidence_collection_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
NOT_COMPUTABLE = "NOT_COMPUTABLE"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _field_plan(group_id: str, fields: list[str]) -> list[dict[str, Any]]:
    return [
        {"step_id": f"{group_id}_{idx:03d}", "field": field, "required": True}
        for idx, field in enumerate(fields, start=1)
    ]


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "backlog_acceptance": False,
        "backlog_acceptance_auto_apply": False,
        "canon_mutation": False,
        "catalog_mutation": False,
        "code_creation": False,
        "decision_record_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "pr_merge_authority": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "yggdrasil_binding_mutation": False,
    }


def build_grok_abx_runes_operator_decision_evidence_collection_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    review = _read_json(root / SOURCE_REVIEW_JSON_PATH)
    review_observed = review is not None
    review = review or {}
    source_ready = (
        review.get("schema_version") == "GrokAbxRunesOperatorDecisionRecordReview.v1"
        and review.get("status") == EXPECTED_SOURCE_STATUS
        and review.get("source_dry_run_ready") is True
        and review.get("operator_input_required") is True
        and review.get("operator_attestations_present") is False
        and review.get("operator_decision_attested") is False
        and review.get("decision_record_created") is False
        and review.get("external_backlog_accepted") is False
        and review.get("rune_registration_authorized") is False
        and review.get("catalog_mutation_authorized") is False
        and review.get("yggdrasil_binding_mutation_authorized") is False
        and review.get("recommended_next_lane") == NOT_COMPUTABLE
        and review.get("safe_to_auto_continue") is False
    )
    blockers = [] if source_ready else ["source_grok_abx_runes_decision_record_review_not_ready"]
    if not review_observed:
        blockers = [
            "source_grok_abx_runes_decision_record_review_missing_or_unreadable",
            f"source_path:{SOURCE_REVIEW_JSON_PATH}",
        ]

    operator_identity_fields = [
        "operator_id",
        "operator_name",
        "operator_role",
        "decision_timestamp_source_observed",
    ]
    disposition_fields = [
        "selected_decision",
        "decision_rationale",
        "grok_share_reviewed",
        "external_backlog_acceptance_selected",
        "rejected_claim_classes",
        "additional_evidence_requested",
    ]
    authority_acknowledgement_fields = [
        "external_source_non_authoritative_acknowledged",
        "grok_merge_claims_denied_acknowledged",
        "catalog_mutation_denied_acknowledged",
        "rune_registration_denied_acknowledged",
        "yggdrasil_binding_mutation_denied_acknowledged",
        "notion_writeback_denied_acknowledged",
        "github_writeback_denied_acknowledged",
        "pr_merge_authority_denied_acknowledged",
        "runtime_mutation_denied_acknowledged",
        "execution_authority_denied_acknowledged",
    ]
    provenance_fields = [
        "reviewed_reconciliation_plan_hash",
        "reviewed_decision_record_plan_hash",
        "reviewed_decision_record_dry_run_hash",
        "reviewed_decision_record_review_hash",
        "reviewed_validation_blockers",
    ]
    output_fields = [
        "operator_evidence_bundle_id",
        "operator_evidence_bundle_hash",
        "evidence_collection_outcome_summary",
        "terminal_authority_summary",
    ]

    evidence_bundle_groups = [
        {
            "group_id": "operator_identity",
            "required_fields": operator_identity_fields,
            "collection_steps": _field_plan("operator_identity", operator_identity_fields),
        },
        {
            "group_id": "grok_claim_disposition",
            "required_fields": disposition_fields,
            "collection_steps": _field_plan("disposition", disposition_fields),
        },
        {
            "group_id": "authority_acknowledgements",
            "required_fields": authority_acknowledgement_fields,
            "collection_steps": _field_plan(
                "acknowledgement", authority_acknowledgement_fields
            ),
        },
        {
            "group_id": "provenance_evidence",
            "required_fields": provenance_fields,
            "collection_steps": _field_plan("provenance", provenance_fields),
        },
        {
            "group_id": "evidence_outputs",
            "required_fields": output_fields,
            "collection_steps": _field_plan("output", output_fields),
        },
    ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "status": (
            "GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_READY"
            if source_ready
            else "GROK_ABX_RUNES_OPERATOR_DECISION_EVIDENCE_COLLECTION_PLAN_BLOCKED"
        ),
        "source_review_path": SOURCE_REVIEW_JSON_PATH.as_posix(),
        "source_review_hash": str(review.get("review_hash", NOT_COMPUTABLE)),
        "source_review_ready": source_ready,
        "evidence_collection_only": True,
        "operator_input_required": True,
        "operator_evidence_collected": False,
        "operator_attestation_created": False,
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
        "recommended_default_decision": "HOLD_FOR_OPERATOR_REVIEW",
        "recommended_next_lane": "NOT_COMPUTABLE",
        "recommended_next_action": (
            "collect explicit external operator evidence outside this repo surface "
            "before any future Grok ABX-Runes decision-record lane; do not create "
            "evidence bundles, decision records, catalog changes, rune registrations, "
            "YGGDRASIL mutations, writebacks, PR merges, or execution changes"
        ),
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "implementation_authorized": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "evidence_bundle_groups": evidence_bundle_groups,
        "required_review_artifacts": [
            SOURCE_REVIEW_JSON_PATH.as_posix(),
            "out/operator_review/grok_abx_runes_operator_decision_record_dry_run_001.latest.json",
            "out/operator_review/grok_abx_runes_operator_decision_record_plan_001.latest.json",
            "out/operator_review/grok_abx_runes_reconciliation_plan_001.latest.json",
            "contracts/runes/catalog.v1.json",
        ],
        "future_evidence_output_candidates": [
            "out/operator_review/grok_abx_runes_operator_decision_evidence_bundle_001.latest.json",
            "out/operator_review/grok_abx_runes_operator_decision_evidence_bundle_001.latest.md",
        ],
        "future_record_output_candidates": [
            "out/operator_review/grok_abx_runes_operator_decision_record_001.latest.json",
            "out/operator_review/grok_abx_runes_operator_decision_record_001.latest.md",
        ],
        "disallowed_follow_on_actions": [
            "OPERATOR_DECISION_RECORD_CREATION",
            "OPERATOR_ATTESTATION_CREATION",
            "OPERATOR_EVIDENCE_BUNDLE_CREATION",
            "EXTERNAL_BACKLOG_ACCEPTANCE",
            "SEPARATE_REGISTRATION_PLANNING_AUTHORIZATION",
            "RUNE_REGISTRATION",
            "CATALOG_MUTATION",
            "YGGDRASIL_BINDING_MUTATION",
            "NOTION_WRITEBACK",
            "GITHUB_WRITEBACK",
            "PR_MERGE",
            "RUNTIME_MUTATION",
            "CANON_MUTATION",
            "QUEUE_MUTATION",
            "SCHEDULER_MUTATION",
            "EXECUTION",
        ],
        "evidence_readiness_summary": {
            "source_review_observed": review_observed,
            "source_review_ready": source_ready,
            "required_group_count": len(evidence_bundle_groups),
            "required_field_count": sum(
                len(group["required_fields"]) for group in evidence_bundle_groups
            ),
            "blocker_count": len(blockers),
        },
        "blockers": blockers,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "plan_hash": canonical_hash(packet)}


def render_grok_abx_runes_operator_decision_evidence_collection_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Grok ABX-Runes Operator Decision Evidence Collection Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- status: {packet['status']}",
        f"- source_review_ready: {packet['source_review_ready']}",
        f"- evidence_collection_only: {packet['evidence_collection_only']}",
        f"- evidence_bundle_created: {packet['evidence_bundle_created']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Evidence Bundle Groups",
    ]
    for group in packet["evidence_bundle_groups"]:
        lines.append(f"- {group['group_id']}")
        for field in group["required_fields"]:
            lines.append(f"  - {field}")
    if packet["blockers"]:
        lines.extend(["", "## Blockers"])
        for blocker in packet["blockers"]:
            lines.append(f"- {blocker}")
    return lines


def write_grok_abx_runes_operator_decision_evidence_collection_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_grok_abx_runes_operator_decision_evidence_collection_plan(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_grok_abx_runes_operator_decision_evidence_collection_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
