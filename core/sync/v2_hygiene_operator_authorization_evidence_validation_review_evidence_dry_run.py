from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_operator_authorization_evidence_validation_review_evidence_plan import (
    PLAN_JSON_PATH as SOURCE_PLAN_JSON,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = (
    "V2HygieneOperatorAuthorizationEvidenceValidationReviewEvidenceDryRun.v1"
)
DRY_RUN_ID = (
    "v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_001"
)
DRY_RUN_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_001.latest.json"
)
DRY_RUN_MD_PATH = DRY_RUN_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = (
    "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_PLAN_READY"
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


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _plan_ready(plan: Mapping[str, Any]) -> bool:
    return (
        plan.get("schema_version")
        == "V2HygieneOperatorAuthorizationEvidenceValidationReviewEvidencePlan.v1"
        and plan.get("status") == EXPECTED_SOURCE_STATUS
        and plan.get("source_review_ready") is True
        and plan.get("evidence_plan_only") is True
        and plan.get("operator_input_required") is True
        and plan.get("recommended_next_patch") == NOT_COMPUTABLE
        and plan.get("recommended_next_lane") == NOT_COMPUTABLE
        and plan.get("safe_to_auto_continue") is False
        and plan.get("operator_attestations_present") is False
        and plan.get("operator_decision_attested") is False
        and plan.get("evidence_bundle_created") is False
        and plan.get("operator_evidence_bundle_created") is False
        and plan.get("operator_attestation_created") is False
        and plan.get("authorization_record_created") is False
        and plan.get("authorization_record_creation_authorized") is False
        and plan.get("implementation_authorized") is False
        and plan.get("v2_module_registration_authorized") is False
        and plan.get("rune_registration_authorized") is False
        and plan.get("projection_surface_mutation_authorized") is False
        and plan.get("schema_mutation_authorized") is False
        and plan.get("execution_authority") is False
        and plan.get("valid_for_execution") is False
        and plan.get("valid_for_implementation") is False
        and plan.get("valid_for_authorization_record") is False
        and _locks_all_false(plan.get("authority_locks"))
    )


def _simulated_evidence_bundle(plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    groups = plan.get("evidence_bundle_groups", [])
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


def _evaluation_blockers(bundle: list[Mapping[str, Any]]) -> list[str]:
    blocker_map = {
        "operator_identity": "operator_identity_not_attested",
        "review_scope_acknowledgement": "review_scope_acknowledgement_not_attested",
        "authority_acknowledgements": "authority_acknowledgements_not_attested",
        "source_packet_confirmation": "source_packet_confirmation_not_attested",
        "operator_disposition": "operator_disposition_not_attested",
    }
    blockers: list[str] = []
    for group in bundle:
        group_id = str(group.get("group_id", ""))
        blocker = blocker_map.get(group_id)
        if blocker is not None:
            blockers.append(blocker)
    return blockers


def build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run(
    source_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(source_root)
    plan = _read_json(root / SOURCE_PLAN_JSON)
    source_observed = plan is not None
    plan = plan or {}
    source_ready = source_observed and _plan_ready(plan)

    if source_ready:
        status = (
            "V2_HYGIENE_OPERATOR_AUTHORIZATION_EVIDENCE_VALIDATION_REVIEW_EVIDENCE_DRY_RUN_READY"
        )
        simulated_bundle = _simulated_evidence_bundle(plan)
        evaluation_blockers = _evaluation_blockers(simulated_bundle)
    else:
        status = NOT_COMPUTABLE
        simulated_bundle = []
        evaluation_blockers = [
            "source_validation_review_evidence_plan_missing_or_not_ready",
            f"source_path:{SOURCE_PLAN_JSON}",
        ]

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "dry_run_id": DRY_RUN_ID,
        "dry_run_hash": "",
        "source_validation_review_evidence_plan_path": str(SOURCE_PLAN_JSON),
        "source_validation_review_evidence_plan_observed": source_observed,
        "source_validation_review_evidence_plan_ready": source_ready,
        "source_validation_review_evidence_plan_hash": str(
            plan.get("plan_hash", NOT_COMPUTABLE)
        ),
        "source_review_artifacts": _string_list(plan.get("required_review_artifacts")),
        "simulated_evidence_bundle": simulated_bundle,
        "readiness_summary": {
            "simulated_only": True,
            "operator_input_required": True,
            "groups_ready": 0,
            "groups_total": len(simulated_bundle),
            "evidence_bundle_complete": False,
            "valid_for_authorization_record": False,
            "evaluation_blockers": evaluation_blockers,
        },
        "evaluation_blockers": evaluation_blockers,
        "simulated_only": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
        "evidence_bundle_created": False,
        "operator_evidence_bundle_created": False,
        "operator_attestation_created": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "recommended_next_action": (
            "preserve the v2 hygiene validation-review evidence hold and use this "
            "simulated missing-evidence bundle to guide external operator evidence "
            "collection; do not create evidence, attestations, authorization records, "
            "registrations, implementation patches, writeback, or execution"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "disallowed_follow_on_actions": _string_list(
            plan.get("disallowed_follow_on_actions")
        ),
        "authority_locks": {
            "activation": False,
            "authorization_record_creation": False,
            "auto_approval": False,
            "auto_continuation": False,
            "canon_mutation": False,
            "decision_record_creation": False,
            "evidence_bundle_creation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation_authorization": False,
            "notion_writeback": False,
            "operator_attestation": False,
            "projection_surface_mutation": False,
            "queue_mutation": False,
            "rune_registration": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "schema_mutation": False,
            "strict_mode_enablement": False,
            "token_minting": False,
            "v2_module_registration": False,
        },
    }
    packet["dry_run_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "dry_run_hash"}
    )
    return packet


def render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Operator Authorization Evidence Validation Review Evidence Dry Run",
        "",
        f"- `status`: `{packet['status']}`",
        f"- `source_validation_review_evidence_plan_ready`: `{packet['source_validation_review_evidence_plan_ready']}`",
        f"- `simulated_only`: `{packet['simulated_only']}`",
        f"- `valid_for_authorization_record`: `{packet['valid_for_authorization_record']}`",
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


def write_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = (
        build_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run(
            root
        )
    )
    write_canonical_json(target_root / DRY_RUN_JSON_PATH, packet)
    _write_markdown(
        target_root / DRY_RUN_MD_PATH,
        render_v2_hygiene_operator_authorization_evidence_validation_review_evidence_dry_run_markdown(
            packet
        ),
    )
    return packet
