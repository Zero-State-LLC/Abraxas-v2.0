from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "V2HygienePhase1OperatorReviewStabilizationStrategyPlan.v1"
PLAN_ID = "v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001"
PLAN_JSON_PATH = Path(
    "out/operator_review/"
    "v2_hygiene_phase1_operator_review_stabilization_strategy_plan_001.latest.json"
)
PLAN_MD_PATH = PLAN_JSON_PATH.with_suffix(".md")
NOT_COMPUTABLE = "NOT_COMPUTABLE"

SOURCE_CYCLE_AUDIT_PATH = (
    "out/operator_review/"
    "v2_hygiene_phase1_operator_review_dependency_cycle_audit_001.latest.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _authority_locks() -> dict[str, bool]:
    return {
        "activation": False,
        "auto_approval": False,
        "auto_continuation": False,
        "canon_mutation": False,
        "code_creation": False,
        "evidence_bundle_creation": False,
        "execution_authority": False,
        "github_writeback": False,
        "hygiene_code_creation": False,
        "implementation_authorization": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "operator_authorization_record_creation": False,
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


def _source_status(packet: Mapping[str, Any]) -> str:
    value = packet.get("audit_status")
    return value if isinstance(value, str) and value else NOT_COMPUTABLE


def _source_record(packet: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": SOURCE_CYCLE_AUDIT_PATH,
        "source_observed": bool(packet),
        "source_hash": canonical_hash(packet) if packet else NOT_COMPUTABLE,
        "source_status": _source_status(packet),
        "cycle_observed": bool(packet.get("cycle_observed", False)),
        "naive_regeneration_safe": bool(packet.get("naive_regeneration_safe", True)),
        "implementation_authorized": bool(
            packet.get("implementation_authorized", False)
        ),
        "valid_for_execution": bool(packet.get("valid_for_execution", False)),
    }


def _strategy_options() -> list[dict[str, Any]]:
    return [
        {
            "strategy_id": "terminal_snapshot_strategy",
            "strategy_label": "emit terminal reviewed snapshot outside closure scan",
            "recommended": True,
            "operator_decision_required": True,
            "description": (
                "Create a future terminal snapshot/receipt that freezes the reviewed "
                "bulk disposition inputs without re-scanning the generated Phase 1 "
                "downstream artifacts that consume it."
            ),
            "authority_granted": False,
        },
        {
            "strategy_id": "scan_exclusion_strategy",
            "strategy_label": "exclude self-dependent downstream artifacts from scan",
            "recommended": False,
            "operator_decision_required": True,
            "description": (
                "Adjust a future bulk disposition generator so it records an explicit "
                "exclusion set for artifacts whose hashes depend on the bulk packet."
            ),
            "authority_granted": False,
        },
        {
            "strategy_id": "two_phase_manifest_strategy",
            "strategy_label": "split inventory manifest from disposition receipt",
            "recommended": False,
            "operator_decision_required": True,
            "description": (
                "Separate the full-directory inventory manifest from review "
                "disposition semantics so downstream Phase 1 records consume a "
                "stable manifest instead of a self-referential disposition packet."
            ),
            "authority_granted": False,
        },
    ]


def build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    source = _read_json(root / SOURCE_CYCLE_AUDIT_PATH)
    source_record = _source_record(source)
    source_ready = (
        source_record["source_observed"]
        and source_record["source_status"]
        == "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_DEPENDENCY_CYCLE_AUDIT_HELD_FOR_OPERATOR"
        and source_record["cycle_observed"] is True
        and source_record["naive_regeneration_safe"] is False
        and source_record["implementation_authorized"] is False
        and source_record["valid_for_execution"] is False
    )

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "plan_id": PLAN_ID,
        "strategy_plan_status": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_READY"
            if source_ready
            else "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_STRATEGY_PLAN_BLOCKED"
        ),
        "source_cycle_audit": source_record,
        "selected_strategy_id": (
            "terminal_snapshot_strategy" if source_ready else NOT_COMPUTABLE
        ),
        "strategy_options": _strategy_options(),
        "operator_decision_required": True,
        "operator_decision_record_created": False,
        "recommended_next_lane": (
            "V2_HYGIENE_PHASE1_OPERATOR_REVIEW_STABILIZATION_DECISION_RECORD_PLAN"
            if source_ready
            else NOT_COMPUTABLE
        ),
        "recommended_next_action": (
            "plan the external operator decision record for the selected "
            "stabilization strategy; do not regenerate the bulk disposition and "
            "Phase 1 chain in alternating sequence"
            if source_ready
            else "restore the dependency cycle audit before planning stabilization"
        ),
        "plan_findings": [
            {
                "finding_id": "dependency_cycle_requires_stabilization_strategy",
                "finding_status": "OBSERVED" if source_ready else "NOT_OBSERVED",
                "authority_granted": False,
            },
            {
                "finding_id": "naive_regeneration_remains_denied",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
            {
                "finding_id": "operator_decision_record_required_but_not_created",
                "finding_status": "ENFORCED",
                "authority_granted": False,
            },
        ],
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "authorization_granted": False,
        "authorization_record_created": False,
        "operator_attestation_created": False,
        "operator_evidence_bundle_created": False,
        "implementation_authorized": False,
        "valid_for_implementation": False,
        "valid_for_execution": False,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "hygiene_code_creation_authorized": False,
        "schema_file_creation_authorized": False,
        "rune_registration_authorized": False,
        "v2_module_registration_authorized": False,
        "strict_mode_enablement_authorized": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "canon_mutation": False,
        "schema_mutation": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**packet, "strategy_plan_hash": canonical_hash(packet)}


def render_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Hygiene Phase 1 Operator Review Stabilization Strategy Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- strategy_plan_status: {packet['strategy_plan_status']}",
        f"- selected_strategy_id: {packet['selected_strategy_id']}",
        f"- operator_decision_required: {packet['operator_decision_required']}",
        f"- operator_decision_record_created: {packet['operator_decision_record_created']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Strategy Options",
    ]
    for option in packet.get("strategy_options", []):
        if isinstance(option, Mapping):
            lines.append(
                "- "
                f"{option['strategy_id']}: recommended={option['recommended']}; "
                f"operator_decision_required={option['operator_decision_required']}"
            )
    lines.extend(["", "## Findings"])
    for finding in packet.get("plan_findings", []):
        if isinstance(finding, Mapping):
            lines.append(
                f"- {finding['finding_id']}: {finding['finding_status']} "
                f"(authority_granted={finding['authority_granted']})"
            )
    return lines


def write_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
    repo_root: str | Path = ".",
    *,
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    packet = build_v2_hygiene_phase1_operator_review_stabilization_strategy_plan(
        repo_root
    )
    root = Path(out_root) if out_root is not None else Path(repo_root)
    write_canonical_json(root / PLAN_JSON_PATH, packet)
    md_path = root / PLAN_MD_PATH
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(
        "\n".join(
            render_v2_hygiene_phase1_operator_review_stabilization_strategy_plan_markdown(
                packet
            )
        )
        + "\n",
        encoding="utf-8",
    )
    return packet
