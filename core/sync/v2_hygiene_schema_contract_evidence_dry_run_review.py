from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_schema_contract_evidence_dry_run import (
    DRY_RUN_JSON_PATH as SOURCE_DRY_RUN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "V2HygieneSchemaContractEvidenceDryRunReview.v1"
REVIEW_ID = "v2_hygiene_schema_contract_evidence_dry_run_review_001"
REVIEW_JSON_PATH = Path(
    "out/operator_review/v2_hygiene_schema_contract_evidence_dry_run_review_001.latest.json"
)
REVIEW_MD_PATH = REVIEW_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_READY"

EXPECTED_BLOCKERS = [
    "operator_identity_not_attested",
    "review_scope_acknowledgement_not_attested",
    "authority_acknowledgements_not_attested",
    "schema_contract_disposition_not_attested",
    "terminal_output_controls_not_attested",
]
EXPECTED_MISSING_CONTRACT_IDS = [
    "loop_dynamics",
    "v2_output",
    "v2_hygiene_rune_base",
    "hygiene_mode",
    "individual_hygiene_rune_contracts",
]


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _locks_all_false(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value) and all(
        item is False for item in value.values()
    )


def _simulated_groups(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return []
    groups = value.get("groups", [])
    if not isinstance(groups, list):
        return []
    return [
        str(group.get("group_id", NOT_COMPUTABLE))
        for group in groups
        if isinstance(group, Mapping)
    ]


def _source_ready(dry_run: Mapping[str, Any]) -> bool:
    readiness_summary = dry_run.get("readiness_summary", {})
    evaluation_blockers = _string_list(dry_run.get("evaluation_blockers"))
    missing_contract_ids = _string_list(dry_run.get("source_missing_schema_contract_ids"))
    return (
        dry_run.get("schema_version") == "V2HygieneSchemaContractEvidenceDryRun.v1"
        and dry_run.get("status") == EXPECTED_SOURCE_STATUS
        and dry_run.get("source_evidence_plan_ready") is True
        and dry_run.get("simulated_only") is True
        and dry_run.get("operator_input_required") is True
        and dry_run.get("operator_attestations_present") is False
        and dry_run.get("operator_decision_attested") is False
        and dry_run.get("operator_attestation_created") is False
        and dry_run.get("evidence_bundle_created") is False
        and dry_run.get("operator_evidence_bundle_created") is False
        and dry_run.get("authorization_record_created") is False
        and dry_run.get("authorization_record_creation_authorized") is False
        and dry_run.get("implementation_authorized") is False
        and dry_run.get("schema_file_creation_authorized") is False
        and dry_run.get("schema_mutation_authorized") is False
        and dry_run.get("hygiene_code_creation_authorized") is False
        and dry_run.get("v2_module_registration_authorized") is False
        and dry_run.get("rune_registration_authorized") is False
        and dry_run.get("strict_mode_enablement_authorized") is False
        and dry_run.get("execution_authority") is False
        and dry_run.get("valid_for_authorization_record") is False
        and dry_run.get("valid_for_execution") is False
        and dry_run.get("valid_for_implementation") is False
        and dry_run.get("recommended_next_patch") == NOT_COMPUTABLE
        and dry_run.get("recommended_next_lane") == NOT_COMPUTABLE
        and dry_run.get("recommended_next_state") == "hold"
        and dry_run.get("safe_to_auto_continue") is False
        and dry_run.get("safe_to_prepare_patch") is False
        and isinstance(readiness_summary, Mapping)
        and readiness_summary.get("required_group_count") == 5
        and readiness_summary.get("required_field_count") == 36
        and readiness_summary.get("attested_group_count") == 0
        and readiness_summary.get("attested_field_count") == 0
        and readiness_summary.get("source_missing_contract_count") == 5
        and readiness_summary.get("evidence_bundle_complete") is False
        and readiness_summary.get("valid_for_authorization_record") is False
        and evaluation_blockers == EXPECTED_BLOCKERS
        and missing_contract_ids == EXPECTED_MISSING_CONTRACT_IDS
        and _locks_all_false(dry_run.get("authority_locks"))
    )


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_evidence_bundle_creation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_file_creation": False,
        "schema_mutation": False,
        "strict_mode_enablement": False,
        "v2_module_registration": False,
    }


def build_v2_hygiene_schema_contract_evidence_dry_run_review(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / SOURCE_DRY_RUN_JSON_PATH
    dry_run = _read_json(source_path)
    source_observed = dry_run is not None
    dry_run = dry_run or {}
    source_ready = source_observed and _source_ready(dry_run)
    source_evaluation_blockers = _string_list(dry_run.get("evaluation_blockers"))
    source_missing_contract_ids = _string_list(
        dry_run.get("source_missing_schema_contract_ids")
    )
    source_simulated_group_ids = _simulated_groups(
        dry_run.get("simulated_evidence_bundle")
    )

    if not source_observed:
        status = "NOT_COMPUTABLE"
        source_readiness = "SOURCE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_MISSING"
        review_findings = [
            {
                "finding_id": "source_schema_contract_evidence_dry_run_missing",
                "finding_status": "NOT_COMPUTABLE",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source schema-contract evidence dry run is missing or unreadable"
        )
    elif not source_ready:
        status = "V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_REVIEW_BLOCKED"
        source_readiness = "SOURCE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_NOT_READY"
        review_findings = [
            {
                "finding_id": "source_schema_contract_evidence_dry_run_not_ready",
                "finding_status": "BLOCKED",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = (
            "source schema-contract evidence dry-run packet is not ready for "
            "held operator review"
        )
    else:
        status = "V2_HYGIENE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_REVIEW_HELD_FOR_OPERATOR"
        source_readiness = "SOURCE_SCHEMA_CONTRACT_EVIDENCE_DRY_RUN_READY"
        review_findings = [
            {
                "finding_id": "source_schema_contract_evidence_dry_run_ready",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "simulated_schema_contract_evidence_bundle_observed",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "external_operator_attestations_missing",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "schema_contracts_still_missing",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "authority_locks_enforced",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ]
        terminal_hold_reason = (
            "Schema-contract evidence dry run is deterministic and complete only "
            "as a simulation. External operator attestations remain missing for "
            "all required review groups, and the five schema contracts remain "
            "unimplemented; this review cannot approve, create evidence, create "
            "attestations, create authorization records, create schemas, create "
            "hygiene code, register modules or runes, enable strict mode, write "
            "back, execute, or continue automatically"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "review_id": REVIEW_ID,
        "source_evidence_dry_run_path": str(SOURCE_DRY_RUN_JSON_PATH),
        "source_evidence_dry_run_observed": source_observed,
        "source_evidence_dry_run_file_hash": _sha256(source_path),
        "source_evidence_dry_run_packet_hash": str(
            dry_run.get("dry_run_hash", NOT_COMPUTABLE)
        ),
        "source_evidence_dry_run_ready": source_ready,
        "source_evidence_dry_run_status": str(dry_run.get("status", NOT_COMPUTABLE)),
        "source_readiness": source_readiness,
        "source_evaluation_blockers": source_evaluation_blockers,
        "source_missing_schema_contract_ids": source_missing_contract_ids,
        "source_simulated_evidence_group_ids": source_simulated_group_ids,
        "review_findings": review_findings,
        "selected_operator_decision": "HOLD_FOR_OPERATOR_REVIEW"
        if source_ready
        else NOT_COMPUTABLE,
        "selected_follow_on_action": "MAINTAIN_SCHEMA_CONTRACT_EVIDENCE_HOLD"
        if source_ready
        else NOT_COMPUTABLE,
        "terminal_hold_reason": terminal_hold_reason,
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
        "operator_attestation_created": False,
        "evidence_bundle_created": False,
        "operator_evidence_bundle_created": False,
        "authorization_record_created": False,
        "authorization_record_creation_authorized": False,
        "implementation_authorized": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "recommended_next_state": "hold",
        "recommended_next_action": (
            "collect explicit external operator attestations before any future "
            "schema-contract evidence bundle, authorization-record, schema file, "
            "hygiene implementation, module/rune registration, strict-mode, "
            "writeback, activation, or execution lane"
            if source_ready
            else "repair source schema-contract evidence dry run before review"
        ),
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_authorization_record": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "authority_locks": _authority_locks(),
        "review_hash": "",
    }
    packet["review_hash"] = canonical_hash(
        {key: value for key, value in packet.items() if key != "review_hash"}
    )
    return packet


def render_v2_hygiene_schema_contract_evidence_dry_run_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Schema Contract Evidence Dry Run Review",
        "",
        f"- review_id: {packet['review_id']}",
        f"- status: {packet['status']}",
        f"- source_evidence_dry_run_ready: {packet['source_evidence_dry_run_ready']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- safe_to_prepare_patch: {packet['safe_to_prepare_patch']}",
        "",
        "## Terminal Hold Reason",
        "",
        str(packet["terminal_hold_reason"]),
        "",
        "## Review Findings",
    ]
    for finding in packet["review_findings"]:
        lines.append(
            f"- {finding['finding_id']}: {finding['finding_status']} "
            f"(authority_granted={finding['authority_granted']})"
        )
    lines.extend(["", "## Source Evaluation Blockers"])
    if packet["source_evaluation_blockers"]:
        for blocker in packet["source_evaluation_blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    lines.extend(["", "## Missing Schema Contracts"])
    if packet["source_missing_schema_contract_ids"]:
        for contract_id in packet["source_missing_schema_contract_ids"]:
            lines.append(f"- {contract_id}")
    else:
        lines.append("- none")
    lines.extend(["", "## Source Simulated Evidence Groups"])
    if packet["source_simulated_evidence_group_ids"]:
        for group_id in packet["source_simulated_evidence_group_ids"]:
            lines.append(f"- {group_id}")
    else:
        lines.append("- none")
    return lines


def write_v2_hygiene_schema_contract_evidence_dry_run_review(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_schema_contract_evidence_dry_run_review(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / REVIEW_JSON_PATH, packet)
    md_path = root / REVIEW_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_schema_contract_evidence_dry_run_review_markdown(packet)
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
