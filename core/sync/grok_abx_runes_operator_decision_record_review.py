from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.grok_abx_runes_operator_decision_record_dry_run import (
    DRY_RUN_JSON_PATH as SOURCE_DRY_RUN_JSON_PATH,
)

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

SCHEMA_VERSION = "GrokAbxRunesOperatorDecisionRecordReview.v1"
REVIEW_ID = "grok_abx_runes_operator_decision_record_review_001"
REVIEW_JSON_PATH = Path(
    "out/operator_review/grok_abx_runes_operator_decision_record_review_001.latest.json"
)
REVIEW_MD_PATH = REVIEW_JSON_PATH.with_suffix(".md")
EXPECTED_SOURCE_STATUS = "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_DRY_RUN_READY"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return NOT_COMPUTABLE


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _authority_locks() -> dict[str, bool]:
    return {
        "authorization_record_creation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "backlog_acceptance_auto_apply": False,
        "canon_mutation": False,
        "catalog_mutation": False,
        "code_creation": False,
        "decision_record_creation": False,
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


def build_grok_abx_runes_operator_decision_record_review(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source_path = root / SOURCE_DRY_RUN_JSON_PATH
    dry_run = _read_json(source_path)
    dry_run_observed = dry_run is not None
    dry_run = dry_run or {}
    validation_blockers = _string_list(dry_run.get("validation_blockers"))
    simulated = dry_run.get("simulated_decision_record", {})
    source_ready = (
        dry_run.get("schema_version") == "GrokAbxRunesOperatorDecisionRecordDryRun.v1"
        and dry_run.get("status") == EXPECTED_SOURCE_STATUS
        and dry_run.get("validation_passed") is True
        and dry_run.get("simulated_only") is True
        and dry_run.get("operator_input_required") is True
        and dry_run.get("operator_decision_attested") is False
        and dry_run.get("decision_record_created") is False
        and dry_run.get("external_backlog_accepted") is False
        and dry_run.get("separate_registration_planning_authorized") is False
        and dry_run.get("rune_registration_authorized") is False
        and dry_run.get("catalog_mutation_authorized") is False
        and dry_run.get("yggdrasil_binding_mutation_authorized") is False
        and dry_run.get("valid_for_execution") is False
        and dry_run.get("safe_to_auto_continue") is False
        and isinstance(simulated, Mapping)
        and simulated.get("selected_follow_on_action")
        == "MAINTAIN_GROK_ABX_RUNES_OPERATOR_REVIEW_HOLD"
        and simulated.get("missing_attested_field_count", 0) > 0
        and bool(validation_blockers)
    )

    if not dry_run_observed:
        status = NOT_COMPUTABLE
        source_readiness = "SOURCE_DRY_RUN_MISSING"
        review_findings = [
            {
                "finding_id": "source_dry_run_missing",
                "finding_status": NOT_COMPUTABLE,
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = "source dry-run evidence is missing or unreadable"
    elif not source_ready:
        status = "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_REVIEW_BLOCKED"
        source_readiness = "SOURCE_DRY_RUN_NOT_READY"
        review_findings = [
            {
                "finding_id": "source_dry_run_not_ready",
                "finding_status": "BLOCKED",
                "authority_granted": False,
            }
        ]
        terminal_hold_reason = "source dry-run evidence is not ready for operator review"
    else:
        status = "GROK_ABX_RUNES_OPERATOR_DECISION_RECORD_REVIEW_HELD_FOR_OPERATOR"
        source_readiness = "SOURCE_DRY_RUN_READY"
        review_findings = [
            {
                "finding_id": "simulated_decision_record_shape_validated",
                "finding_status": "OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "operator_attestations_missing",
                "finding_status": "HELD_FOR_OPERATOR",
                "authority_granted": False,
            },
            {
                "finding_id": "external_backlog_acceptance_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "rune_registration_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "catalog_and_yggdrasil_mutation_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ]
        terminal_hold_reason = (
            "operator attestations are missing; this review cannot accept Grok "
            "ABX-Runes as backlog, create a decision record, authorize registration "
            "planning, register runes, mutate catalog or YGGDRASIL surfaces, write back, "
            "merge PRs, or execute"
        )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "review_id": REVIEW_ID,
        "status": status,
        "source_dry_run_path": SOURCE_DRY_RUN_JSON_PATH.as_posix(),
        "source_dry_run_file_hash": _sha256(source_path),
        "source_dry_run_packet_hash": str(dry_run.get("dry_run_hash", NOT_COMPUTABLE)),
        "source_dry_run_ready": source_ready,
        "source_readiness": source_readiness,
        "validation_blockers": validation_blockers,
        "review_findings": review_findings,
        "selected_operator_decision": (
            "HOLD_FOR_OPERATOR_REVIEW" if source_ready else NOT_COMPUTABLE
        ),
        "selected_follow_on_action": (
            "MAINTAIN_GROK_ABX_RUNES_OPERATOR_REVIEW_HOLD"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "terminal_hold_reason": terminal_hold_reason,
        "operator_review_required": True,
        "operator_input_required": True,
        "operator_attestations_present": False,
        "operator_decision_attested": False,
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
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_action": (
            "collect explicit external operator attestation evidence before any "
            "future Grok ABX-Runes decision-record lane; do not auto-create records "
            "or prepare catalog, rune, YGGDRASIL, writeback, PR, or execution changes"
            if source_ready
            else "repair source dry-run evidence before review"
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
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "review_hash": canonical_hash(packet)}


def render_grok_abx_runes_operator_decision_record_review_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# Grok ABX-Runes Operator Decision Record Review",
        "",
        f"- review_id: {packet['review_id']}",
        f"- status: {packet['status']}",
        f"- source_dry_run_ready: {packet['source_dry_run_ready']}",
        f"- selected_operator_decision: {packet['selected_operator_decision']}",
        f"- selected_follow_on_action: {packet['selected_follow_on_action']}",
        f"- operator_attestations_present: {packet['operator_attestations_present']}",
        f"- decision_record_created: {packet['decision_record_created']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Review Findings",
    ]
    for finding in packet["review_findings"]:
        if isinstance(finding, Mapping):
            lines.append(
                f"- {finding['finding_id']}: {finding['finding_status']} "
                f"(authority_granted={finding['authority_granted']})"
            )
    lines.extend(["", "## Source Validation Blockers"])
    for blocker in packet["validation_blockers"]:
        lines.append(f"- {blocker}")
    return lines


def write_grok_abx_runes_operator_decision_record_review(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_grok_abx_runes_operator_decision_record_review(repo_root)
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / REVIEW_JSON_PATH, packet)
    md_path = root / REVIEW_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(render_grok_abx_runes_operator_decision_record_review_markdown(packet))
        + "\n",
        encoding="utf-8",
    )
    return packet
