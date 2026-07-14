from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

from core.status_result import STATUS_NOT_COMPUTABLE as NOT_COMPUTABLE

ARTIFACT_TYPE = "V2LiveNotionSurfaceReconciliation.v1"
RECONCILIATION_ID = "V2_LIVE_NOTION_SURFACE_RECONCILIATION_001"
OUT_JSON = "out/sync/v2_live_notion_surface_reconciliation/latest.json"
OUT_MD = "out/sync/v2_live_notion_surface_reconciliation/latest.md"

V2_UPGRADE_RECONCILIATION_JSON = "out/sync/v2_upgrade_completion_reconciliation/latest.json"
V2_REGISTRATION_READINESS_JSON = "out/sync/v2_hygiene_registration_readiness_audit/latest.json"
V2_OPERATOR_GATE_JSON = "out/operator_review/v2_hygiene_loop_awareness_operator_authorization_gate_001.latest.json"

LIVE_NOTION_SURFACES = (
    {
        "page_id": "a64497ce-1a8f-422b-a999-8dcbf252ef7f",
        "title": "Abraxas v2.0 - Upgrade Completion Receipt (2026-06-13)",
        "observed_as_of": "2026-06-13T16:12:27.751Z",
        "mode": "ADVISORY_ONLY",
        "mutation": "none (receipt only)",
        "status": "LINK_RECEIPT_ONLY",
        "authority_statement": "no promotion, execution, writeback, runtime mutation, or canon mutation authority",
    },
    {
        "page_id": "37e3e8ba-2f5c-811a-96f9-cdd0cc09bf7f",
        "title": "v2.0 Implementation Surfaces",
        "observed_as_of": "2026-06-13T16:43:43.834Z",
        "mode": "LOCAL_CANON_GATE",
        "mutation": "navigation hub only",
        "status": "PHASE1_READY_FOR_WORK",
        "authority_statement": "central index for planning and repo surfaces; no implementation authority observed",
    },
    {
        "page_id": "37d3e8ba-2f5c-81bf-bd4f-cdfba9f1e2ea",
        "title": "ABRAXAS v2.0 - Repo Notion Sync Receipt 2026-06-12",
        "observed_as_of": "2026-06-13T15:57:17.734Z",
        "mode": "ADVISORY_ONLY",
        "mutation": "none",
        "status": "SAFE_CONTINUATION_GUIDANCE_OBSERVED",
        "authority_statement": "execution, canon, runtime, and writeback authority denied",
    },
)

LIVE_NOTION_PHASES = (
    {"phase": "Phase 1: Foundations & Hygiene Layer", "notion_status": "Ready for work"},
    {"phase": "Phase 2: Module Skeletons & Governance Hooks", "notion_status": "Placeholder"},
    {"phase": "Phase 3: Output Surface Integration", "notion_status": "Placeholder"},
    {"phase": "Phase 4: Full Integration & Promotion", "notion_status": "Placeholder"},
)


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
        "activation": False,
        "auto_continuation": False,
        "auto_patch_generation": False,
        "canon_mutation": False,
        "execution_authority": False,
        "forecast_routing": False,
        "github_writeback": False,
        "implementation_authorization": False,
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


def build_v2_live_notion_surface_reconciliation(
    repo_root: str | Path = ".",
) -> dict[str, Any]:
    root = Path(repo_root)
    upgrade = _read_json(root / V2_UPGRADE_RECONCILIATION_JSON)
    registration = _read_json(root / V2_REGISTRATION_READINESS_JSON)
    operator_gate = _read_json(root / V2_OPERATOR_GATE_JSON)
    source_records = [
        _source_record(V2_UPGRADE_RECONCILIATION_JSON, upgrade, "reconciliation_status"),
        _source_record(V2_REGISTRATION_READINESS_JSON, registration, "audit_status"),
        _source_record(V2_OPERATOR_GATE_JSON, operator_gate, "gate_status"),
    ]

    source_ready = all(record["observed"] for record in source_records)
    live_pages_deny_authority = all(
        "authority" in surface["authority_statement"] for surface in LIVE_NOTION_SURFACES
    )
    phase1_ready = any(
        item["phase"] == "Phase 1: Foundations & Hygiene Layer"
        and item["notion_status"] == "Ready for work"
        for item in LIVE_NOTION_PHASES
    )
    repo_gate_held = (
        operator_gate.get("gate_status")
        == "V2_HYGIENE_LOOP_AWARENESS_OPERATOR_AUTHORIZATION_GATE_HELD_FOR_OPERATOR"
        and operator_gate.get("authorization_granted") is False
    )
    reconciliation_status = (
        "V2_LIVE_NOTION_SURFACE_RECONCILIATION_READY_HELD_FOR_OPERATOR"
        if source_ready and live_pages_deny_authority and phase1_ready and repo_gate_held
        else "NOT_COMPUTABLE"
    )

    findings = [
        {
            "finding_id": "live_notion_v2_surfaces_observed",
            "finding_status": "PASS" if live_pages_deny_authority else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "notion_phase1_ready_for_work_observed",
            "finding_status": "OBSERVED" if phase1_ready else "NOT_OBSERVED",
            "authority_granted": False,
        },
        {
            "finding_id": "repo_operator_gate_still_held",
            "finding_status": "PASS" if repo_gate_held else "FAIL_CLOSED",
            "authority_granted": False,
        },
        {
            "finding_id": "ready_for_work_does_not_grant_repo_authority",
            "finding_status": "ENFORCED" if repo_gate_held else "FAIL_CLOSED",
            "authority_granted": False,
        },
    ]

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "reconciliation_id": RECONCILIATION_ID,
        "reconciliation_status": reconciliation_status,
        "live_notion_surfaces": list(LIVE_NOTION_SURFACES),
        "live_notion_phases": list(LIVE_NOTION_PHASES),
        "repo_source_records": source_records,
        "source_artifact_hashes": {
            V2_UPGRADE_RECONCILIATION_JSON: _source_hash(root / V2_UPGRADE_RECONCILIATION_JSON),
            V2_REGISTRATION_READINESS_JSON: _source_hash(root / V2_REGISTRATION_READINESS_JSON),
            V2_OPERATOR_GATE_JSON: _source_hash(root / V2_OPERATOR_GATE_JSON),
        },
        "reconciliation_findings": findings,
        "reconciled_interpretation": (
            "Live Notion says v2 Phase 1 is ready for work, but the same live surfaces "
            "and repo evidence keep authority advisory-only; repo-side registration, "
            "implementation, writeback, and execution remain held for explicit operator authorization."
        ),
        "recommended_next_action": (
            "prepare only advisory validation or evidence-collection surfaces until a separate "
            "operator authorization record explicitly permits v2 hygiene implementation or registration"
        ),
        "recommended_next_lane": NOT_COMPUTABLE,
        "recommended_next_patch": NOT_COMPUTABLE,
        "operator_authorization_observed": False,
        "operator_authorization_record_created": False,
        "authorization_granted": False,
        "v2_module_registration_authorized": False,
        "rune_registration_authorized": False,
        "implementation_authorized": False,
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


def write_v2_live_notion_surface_reconciliation(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    write_canonical_json(path, packet)


def render_v2_live_notion_surface_reconciliation_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# v2.0 Live Notion Surface Reconciliation",
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
    lines.extend(["", "## Live Notion Phases"])
    for phase in packet.get("live_notion_phases", []):
        if isinstance(phase, Mapping):
            lines.append(f"- {phase['phase']}: {phase['notion_status']}")
    lines.extend(["", "## Live Notion Surfaces"])
    for surface in packet.get("live_notion_surfaces", []):
        if isinstance(surface, Mapping):
            lines.append(f"- {surface['title']}: {surface['status']}")
    return lines


def write_v2_live_notion_surface_reconciliation_markdown(
    path: str | Path,
    packet: Mapping[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "\n".join(render_v2_live_notion_surface_reconciliation_markdown(packet)) + "\n",
        encoding="utf-8",
    )
