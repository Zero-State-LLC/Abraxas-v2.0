from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.v2_hygiene_loop_awareness_audit import OUT_JSON as SOURCE_AUDIT_JSON

ARTIFACT_TYPE = "V2HygieneLoopAwarenessAlignmentPlan.v1"
PLAN_ID = "V2_HYGIENE_LOOP_AWARENESS_ALIGNMENT_PLAN_001"
OUT_JSON = "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json"
OUT_MD = "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.md"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
EXPECTED_AUDIT_STATUSES = {
    "V2_HYGIENE_LOOP_AWARENESS_AUDIT_DEGRADED",
    "V2_HYGIENE_LOOP_AWARENESS_AUDIT_READY",
}

_CHECK_ACTIONS = {
    "output_registers_present": {
        "workstream": "output_registers",
        "planned_scope": "define repo-visible OBSERVED / INFERRED / SPECULATIVE register coverage for high-signal outputs",
        "blocked_until": "advisory register contract and operator review are explicitly approved",
    },
    "loop_dynamics_assessment_present": {
        "workstream": "loop_dynamics",
        "planned_scope": "define deterministic loop_dynamics assessment semantics before applying them to projection surfaces",
        "blocked_until": "loop assessment contract is reviewed as advisory-only evidence",
    },
    "hyperstitional_charge_tagged": {
        "workstream": "hyperstitional_charge",
        "planned_scope": "define hyperstitional_charge and evaluation fields without activating scoring or routing",
        "blocked_until": "hyperstition evaluator scope is reviewed without implementation authority",
    },
    "v2_modules_registered": {
        "workstream": "v2_module_registry",
        "planned_scope": "plan Canon Spine registry entries for Retrocausal Hygiene, Output Schema Enforcer, Self-Adversarial Loop, and Hyperstition Evaluator",
        "blocked_until": "separate module-registration authorization gate exists",
    },
    "core_directive_linked": {
        "workstream": "core_directive_linkage",
        "planned_scope": "plan repo-visible linkage to the Abraxas v2.0 Core Directive without Notion writeback",
        "blocked_until": "documentation alignment scope is explicitly reviewed",
    },
    "v2_runes_documented": {
        "workstream": "v2_rune_registry",
        "planned_scope": "plan ABX-Runes registry entries for LOOP_AWARENESS, HYPERSTITION_TAG, PROVENANCE_ENFORCE, ADVERSARIAL_AUDIT, and OUTPUT_REGISTER_ENFORCE",
        "blocked_until": "separate rune-registration authorization gate exists",
    },
    "projection_surfaces_have_v2_notes": {
        "workstream": "projection_freshness",
        "planned_scope": "plan projection-surface v2.0 compliance notes and freshness sync evidence",
        "blocked_until": "projection surface update scope is explicitly reviewed",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    try:
        return canonical_hash(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return NOT_COMPUTABLE


def _authority_locks() -> dict[str, bool]:
    return {
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "notion_writeback": False,
        "operator_attestation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def _check_results_by_id(audit: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    results = audit.get("check_results", [])
    if not isinstance(results, list):
        return {}
    return {
        str(item.get("check_id")): item
        for item in results
        if isinstance(item, Mapping) and item.get("check_id")
    }


def _planned_work_items(audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    results_by_id = _check_results_by_id(audit)
    items: list[dict[str, Any]] = []
    for check_id in sorted(_CHECK_ACTIONS):
        result = results_by_id.get(check_id, {})
        action = _CHECK_ACTIONS[check_id]
        status = str(result.get("status", "MISSING"))
        requires_alignment = status in {"MISSING", "PARTIAL"}
        items.append(
            {
                "check_id": check_id,
                "workstream": action["workstream"],
                "source_check_status": status,
                "alignment_required": requires_alignment,
                "missing_terms": [str(term) for term in result.get("missing_terms", [])]
                if isinstance(result.get("missing_terms", []), list)
                else [],
                "planned_scope": action["planned_scope"],
                "blocked_until": action["blocked_until"],
                "authority_granted": False,
            }
        )
    return items


def build_v2_hygiene_loop_awareness_alignment_plan(
    repo_root: str | Path = ".",
    source_audit_path: str | Path = SOURCE_AUDIT_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    audit_path = root / source_audit_path
    audit = _load_json(audit_path)
    source_observed = bool(audit)
    source_ready = (
        audit.get("artifact_type") == "V2HygieneLoopAwarenessAudit.v1"
        and audit.get("audit_status") in EXPECTED_AUDIT_STATUSES
        and audit.get("advisory_only") is True
        and audit.get("valid_for_execution") is False
        and audit.get("recommended_next_patch") == NOT_COMPUTABLE
    )
    work_items = _planned_work_items(audit) if source_ready else []
    alignment_required = [item for item in work_items if item["alignment_required"]]
    plan_status = (
        "V2_HYGIENE_LOOP_AWARENESS_ALIGNMENT_PLAN_READY"
        if source_ready
        else NOT_COMPUTABLE
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "source_audit_path": Path(source_audit_path).as_posix(),
        "source_audit_observed": source_observed,
        "source_audit_ready": source_ready,
        "source_audit_status": str(audit.get("audit_status", NOT_COMPUTABLE)),
        "source_audit_hash": _source_hash(audit_path),
        "source_missing_checks": [str(item) for item in audit.get("missing_checks", [])]
        if isinstance(audit.get("missing_checks", []), list)
        else [],
        "source_partial_checks": [str(item) for item in audit.get("partial_checks", [])]
        if isinstance(audit.get("partial_checks", []), list)
        else [],
        "planned_work_items": work_items,
        "alignment_required_count": len(alignment_required),
        "alignment_required_workstreams": [
            str(item["workstream"]) for item in alignment_required
        ],
        "planned_delivery_surfaces": [
            "future advisory register contract plan",
            "future v2 module registry plan",
            "future v2 rune registry plan",
            "future projection freshness notes plan",
            "future operator review gate before any mutation",
        ],
        "acceptance_gates": [
            {
                "gate_id": "V2-HYGIENE-GATE-001",
                "required_before": "any v2 module registration",
                "status": "SEPARATE_OPERATOR_AUTHORIZATION_REQUIRED",
            },
            {
                "gate_id": "V2-HYGIENE-GATE-002",
                "required_before": "any rune registry mutation",
                "status": "SEPARATE_OPERATOR_AUTHORIZATION_REQUIRED",
            },
            {
                "gate_id": "V2-HYGIENE-GATE-003",
                "required_before": "any projection or schema mutation",
                "status": "SEPARATE_OPERATOR_AUTHORIZATION_REQUIRED",
            },
        ],
        "blocked_actions": [
            "V2_MODULE_REGISTRATION",
            "RUNE_REGISTRATION",
            "CANON_SPINE_MUTATION",
            "PROJECTION_SURFACE_MUTATION",
            "SCHEMA_MUTATION",
            "OUTPUT_SCHEMA_ENFORCEMENT_ACTIVATION",
            "NOTION_WRITEBACK",
            "GITHUB_WRITEBACK",
            "AUTO_CONTINUATION",
            "EXECUTION",
        ],
        "recommended_next_action": (
            "hold for a separate governed operator authorization gate before applying "
            "any v2 hygiene module, rune, projection, schema, or documentation mutation"
            if source_ready
            else "repair v2 hygiene audit evidence before alignment planning"
        ),
        "recommended_next_patch": NOT_COMPUTABLE,
        "safe_to_prepare_patch": False,
        "safe_to_auto_continue": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**base, "plan_hash": canonical_hash(base)}


def write_v2_hygiene_loop_awareness_alignment_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def render_v2_hygiene_loop_awareness_alignment_plan_markdown(packet: dict[str, Any]) -> list[str]:
    lines = [
        "# v2.0 Hygiene Loop-Awareness Alignment Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- source_audit_ready: {packet['source_audit_ready']}",
        f"- alignment_required_count: {packet['alignment_required_count']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- safe_to_prepare_patch: {packet['safe_to_prepare_patch']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Planned Work Items",
    ]
    for item in packet["planned_work_items"]:
        lines.append(
            "- "
            f"{item['workstream']}: {item['source_check_status']} "
            f"(alignment_required={item['alignment_required']})"
        )
        if item["missing_terms"]:
            lines.append(f"  missing: {', '.join(item['missing_terms'])}")
    lines.extend(["", "## Acceptance Gates"])
    for gate in packet["acceptance_gates"]:
        lines.append(f"- {gate['gate_id']}: {gate['status']}")
    lines.extend(["", "## Authority"])
    lines.append("- advisory_only: True")
    lines.append("- valid_for_execution: False")
    lines.append("- notion_writeback_allowed: False")
    lines.append("- github_writeback_allowed: False")
    return lines


def write_v2_hygiene_loop_awareness_alignment_plan_markdown(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_v2_hygiene_loop_awareness_alignment_plan_markdown(packet)) + "\n",
        encoding="utf-8",
    )
