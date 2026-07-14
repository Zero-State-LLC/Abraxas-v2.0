from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "V2UpgradeCompletionReconciliation.v1"
RECONCILIATION_ID = "V2_UPGRADE_COMPLETION_RECONCILIATION_001"
OUT_JSON = "out/sync/v2_upgrade_completion_reconciliation/latest.json"
OUT_MD = "out/sync/v2_upgrade_completion_reconciliation/latest.md"

V2_AUDIT_JSON = "out/sync/v2_hygiene_loop_awareness_audit/latest.json"
V2_ALIGNMENT_PLAN_JSON = "out/sync/v2_hygiene_loop_awareness_alignment_plan/latest.json"
V2_OPERATOR_GATE_JSON = "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"

NOTION_COMPLETION_RECEIPT = {
    "title": "Abraxas v2.0 - Upgrade Completion Receipt (2026-06-13)",
    "notion_page_id": "a64497ce-1a8f-422b-a999-8dcbf252ef7f",
    "observed_as_of": "2026-06-13T16:12:27.751Z",
    "mode": "ADVISORY_ONLY",
    "mutation": "none (receipt only)",
    "expected_module_posture": {
        "lane": "SHADOW",
        "authority": "advisory_only",
        "viz": "display_only",
        "oracle": "shadow_context_only",
        "pse": "none",
    },
    "notion_v2_modules": [
        "Retrocausal Signal Hygiene Module",
        "Mandatory Output Schema Enforcer",
        "Self-Adversarial Testing Loop",
        "Hyperstition Potency Evaluator",
    ],
    "notion_v2_runes": [
        "RUNE.LOOP_AWARENESS",
        "RUNE.HYPERSTITION_TAG",
        "RUNE.PROVENANCE_ENFORCE",
        "RUNE.ADVERSARIAL_AUDIT",
        "RUNE.OUTPUT_REGISTER_ENFORCE",
    ],
}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _source_hash(path: Path) -> str:
    data = _read_json(path)
    return canonical_hash(data) if data else NOT_COMPUTABLE


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
        "operator_authorization_record_creation": False,
        "projection_surface_mutation": False,
        "queue_mutation": False,
        "rune_registration": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "schema_mutation": False,
        "token_minting": False,
        "v2_module_registration": False,
    }


def _source_record(path: str, packet: Mapping[str, Any], status_key: str) -> dict[str, Any]:
    status = packet.get(status_key, NOT_COMPUTABLE)
    return {
        "path": path,
        "observed": bool(packet),
        "status_key": status_key,
        "observed_status": str(status) if isinstance(status, str) else NOT_COMPUTABLE,
    }


def _repo_evidence_summary(
    audit: Mapping[str, Any],
    alignment_plan: Mapping[str, Any],
    operator_gate: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "audit": _source_record(V2_AUDIT_JSON, audit, "audit_status"),
        "alignment_plan": _source_record(V2_ALIGNMENT_PLAN_JSON, alignment_plan, "plan_status"),
        "operator_gate": _source_record(V2_OPERATOR_GATE_JSON, operator_gate, "gate_status"),
        "missing_checks": [
            str(item) for item in audit.get("missing_checks", []) if isinstance(item, str)
        ],
        "partial_checks": [
            str(item) for item in audit.get("partial_checks", []) if isinstance(item, str)
        ],
        "alignment_required_workstreams": [
            str(item)
            for item in alignment_plan.get("alignment_required_workstreams", [])
            if isinstance(item, str)
        ],
        "blocked_actions": [
            str(item) for item in operator_gate.get("blocked_actions", []) if isinstance(item, str)
        ],
        "operator_authorization_observed": operator_gate.get("operator_authorization_observed")
        is True,
        "authorization_granted": operator_gate.get("authorization_granted") is True,
        "authorization_record_created": operator_gate.get("operator_authorization_record_created")
        is True,
    }


def build_v2_upgrade_completion_reconciliation(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    audit = _read_json(root / V2_AUDIT_JSON)
    alignment_plan = _read_json(root / V2_ALIGNMENT_PLAN_JSON)
    operator_gate = _read_json(root / V2_OPERATOR_GATE_JSON)
    repo_summary = _repo_evidence_summary(audit, alignment_plan, operator_gate)

    source_ready = all(
        record["observed"]
        for record in [
            repo_summary["audit"],
            repo_summary["alignment_plan"],
            repo_summary["operator_gate"],
        ]
    )
    gate_holds_authority = (
        repo_summary["operator_gate"]["observed_status"]
        == "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and repo_summary["authorization_granted"] is False
        and repo_summary["authorization_record_created"] is False
    )
    repo_still_requires_alignment = bool(
        repo_summary["missing_checks"] or repo_summary["partial_checks"]
    )
    reconciliation_status = (
        "V2_UPGRADE_COMPLETION_RECONCILIATION_READY_HELD_FOR_OPERATOR"
        if source_ready and gate_holds_authority
        else "NOT_COMPUTABLE"
    )

    findings = [
        {
            "finding_id": "notion_completion_receipt_observed",
            "finding_status": "OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "repo_v2_hygiene_still_requires_alignment",
            "finding_status": "OBSERVED" if repo_still_requires_alignment else "NOT_OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "operator_gate_held",
            "finding_status": "PASS" if gate_holds_authority else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "notion_receipt_does_not_override_repo_gate",
            "finding_status": "ENFORCED" if gate_holds_authority else "FAIL_CLOSED",
            "authority_granted": False,
        },
    ]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "reconciliation_id": RECONCILIATION_ID,
        "reconciliation_status": reconciliation_status,
        "notion_completion_receipt": NOTION_COMPLETION_RECEIPT,
        "repo_evidence_summary": repo_summary,
        "source_artifact_hashes": {
            V2_AUDIT_JSON: _source_hash(root / V2_AUDIT_JSON),
            V2_ALIGNMENT_PLAN_JSON: _source_hash(root / V2_ALIGNMENT_PLAN_JSON),
            V2_OPERATOR_GATE_JSON: _source_hash(root / V2_OPERATOR_GATE_JSON),
        },
        "reconciliation_findings": findings,
        "reconciled_interpretation": (
            "Notion completion links are observed as advisory-only external context; "
            "repo-visible v2 hygiene work remains held behind the operator authorization gate."
        ),
        "recommended_next_action": (
            "collect explicit external operator authorization evidence before any repo-side "
            "v2 module registration, rune registration, projection/schema mutation, writeback, or execution"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "operator_authorization_observed": False,
        "operator_authorization_record_created": False,
        "authorization_granted": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "projection_surface_mutation_authorized": False,
        "schema_mutation_authorized": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_patch": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "queue_mutation": False,
        "scheduler_mutation": False,
        "forecast_routing": False,
        "authority_locks": _authority_locks(),
        "downstream": NOT_COMPUTABLE,
    }
    return {**base, "reconciliation_hash": canonical_hash(base)}


def write_v2_upgrade_completion_reconciliation(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_v2_upgrade_completion_reconciliation_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Upgrade Completion Reconciliation",
        "",
        f"- reconciliation_id: {packet['reconciliation_id']}",
        f"- reconciliation_status: {packet['reconciliation_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        "",
        "## Findings",
    ]
    for finding in packet.get("reconciliation_findings", []):
        if isinstance(finding, Mapping):
            lines.append(f"- {finding['finding_id']}: {finding['finding_status']}")
    lines.extend(["", "## Notion Modules"])
    notion = packet.get("notion_completion_receipt", {})
    if isinstance(notion, Mapping):
        for module in notion.get("notion_v2_modules", []):
            lines.append(f"- {module}")
    lines.extend(["", "## Repo Gate"])
    repo = packet.get("repo_evidence_summary", {})
    if isinstance(repo, Mapping):
        gate = repo.get("operator_gate", {})
        if isinstance(gate, Mapping):
            lines.append(f"- observed_status: {gate['observed_status']}")
        lines.append(f"- missing_checks: {', '.join(repo.get('missing_checks', []))}")
        lines.append(f"- partial_checks: {', '.join(repo.get('partial_checks', []))}")
    return lines


def write_v2_upgrade_completion_reconciliation_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_v2_upgrade_completion_reconciliation_markdown(packet)) + "\n",
        encoding="utf-8",
    )
