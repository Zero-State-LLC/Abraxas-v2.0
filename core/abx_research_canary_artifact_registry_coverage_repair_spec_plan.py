from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from core.abx_research_canary_artifact_registry_coverage_audit import (
    AUDIT_ID,
    AUTHORITY_LOCKS,
    BLOCKED_ACTIONS as AUDIT_BLOCKED_ACTIONS,
)
from core.canonical.json import canonical_hash, write_canonical_json

SCHEMA_VERSION = "AbxResearchCanaryArtifactRegistryCoverageRepairSpecPlan.v1"
SPEC_PLAN_ID = "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_001"
ARTIFACT_ID = SPEC_PLAN_ID
SOURCE_AUDIT_PATH = "out/operator_review/abx_research_canary_artifact_registry_coverage_audit_001.latest.json"
OUT_JSON = "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.json"
OUT_MD = "out/operator_review/abx_research_canary_artifact_registry_coverage_repair_spec_plan_001.latest.md"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
OPERATOR_DECISION_REQUEST_LANE = (
    "ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_OPERATOR_DECISION_REQUEST_001"
)

BLOCKED_ACTIONS: tuple[str, ...] = (
    *AUDIT_BLOCKED_ACTIONS,
    "REPAIR_SPEC_EXECUTION",
    "SCOPE_PREFIX_MUTATION_WITHOUT_OPERATOR_DECISION",
)

SAMPLE_CAP = 5

PROPOSED_PHASES: tuple[dict[str, Any], ...] = (
    {
        "phase_id": "REPAIR_SPEC_PHASE_001",
        "phase_name": "classify_canonical_lane_output_path_gaps",
        "execution_allowed": False,
        "repair_execution_performed": False,
    },
    {
        "phase_id": "REPAIR_SPEC_PHASE_002",
        "phase_name": "classify_lane_id_traceability_gaps",
        "execution_allowed": False,
        "repair_execution_performed": False,
    },
    {
        "phase_id": "REPAIR_SPEC_PHASE_003",
        "phase_name": "resolve_scope_prefix_vs_derived_optional_policy",
        "execution_allowed": False,
        "repair_execution_performed": False,
    },
    {
        "phase_id": "REPAIR_SPEC_PHASE_004",
        "phase_name": "orphan_output_exclusion_policy",
        "execution_allowed": False,
        "repair_execution_performed": False,
    },
    {
        "phase_id": "REPAIR_SPEC_PHASE_005",
        "phase_name": "future_operator_authorization_gate_before_registry_mutation",
        "execution_allowed": False,
        "repair_execution_performed": False,
    },
)

BLOCKED_DELIVERY_SURFACES: tuple[str, ...] = (
    "core/generated_artifact_registry.py direct repair mutations",
    "scripts/run_research_canary_artifact_spine_refresh.py spine-refresh runners",
    "out/research_canary_final_activation_authorization_review_hold/ P130 hold surfaces",
    "out/research_canary_*/latest.json research-canary artifact regeneration targets",
    "runtime route or scheduler mutations",
)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _sample_impacted(items: list[str]) -> list[str]:
    return sorted(items)[:SAMPLE_CAP]


def _validate_upstream_audit(audit: Mapping[str, Any]) -> bool:
    governance = audit.get("governance_boundaries", {})
    return (
        audit.get("schema_version") == "AbxResearchCanaryArtifactRegistryCoverageAudit.v1"
        and audit.get("audit_id") == AUDIT_ID
        and audit.get("audit_status") == "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED"
        and audit.get("recommended_next_lane") == SPEC_PLAN_ID
        and audit.get("registry_mutation_performed") is False
        and isinstance(governance, dict)
        and governance.get("research_canary_spine_refresh_performed") is False
    )


def _repair_batches(audit: Mapping[str, Any]) -> list[dict[str, Any]]:
    lane_records = [record for record in audit.get("lane_records", []) if isinstance(record, dict)]
    orphan_outputs = [
        record for record in audit.get("orphan_research_outputs", []) if isinstance(record, dict)
    ]
    governance = audit.get("governance_boundaries", {})
    if not isinstance(governance, dict):
        governance = {}

    output_path_gaps = [
        str(record["output_json_path"])
        for record in lane_records
        if not record.get("output_json_in_registry_entries")
        and record.get("output_json_path") not in {None, NOT_COMPUTABLE}
    ]
    lane_id_gaps = [
        str(record["lane_id"])
        for record in lane_records
        if not record.get("lane_id_in_registry_source")
    ]
    all_output_paths = sorted(
        {
            str(record["output_json_path"])
            for record in lane_records
            if record.get("output_json_path") not in {None, NOT_COMPUTABLE}
        }
    )
    partial_scope_prefix_lanes = [
        str(record["lane_id"])
        for record in lane_records
        if record.get("output_json_in_registry_entries") is True
    ]
    siblings_missing_prefix = [
        str(record["lane_id"])
        for record in lane_records
        if record.get("output_json_in_registry_entries") is False
    ]
    orphan_paths = sorted(
        {
            str(record["output_json_path"])
            for record in orphan_outputs
            if record.get("output_json_path") not in {None, NOT_COMPUTABLE}
        }
    )
    p130_lane_ids = [
        str(record["lane_id"])
        for record in lane_records
        if str(record.get("lane_id", "")).startswith("P130_")
    ]

    return [
        {
            "batch_id": "CANONICAL_LANE_OUTPUT_PATH_REGISTRY_BATCH",
            "batch_status": "ACTIVE" if output_path_gaps else "PASS",
            "repair_mode": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "impacted_count": len(output_path_gaps),
            "sample_impacted": _sample_impacted(output_path_gaps),
            "source_output_paths": all_output_paths,
            "proposed_actions": [
                "classify all 28 canonical lane output_json_path values for registry visibility",
                "propose per-path _DERIVED_OPTIONAL_ARTIFACTS entries for lanes missing registry entries",
                "or propose governed out/research_*/ and out/research_canary_*/ scope-prefix expansion",
                "do not mutate registry entries from this planning lane",
            ],
        },
        {
            "batch_id": "LANE_ID_TRACEABILITY_METADATA_BATCH",
            "batch_status": "ACTIVE" if lane_id_gaps else "PASS",
            "repair_mode": "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE",
            "impacted_count": len(lane_id_gaps),
            "sample_impacted": _sample_impacted(lane_id_gaps),
            "source_lane_ids": sorted(lane_id_gaps),
            "proposed_actions": [
                "propose lane-id visibility block in generated_artifact_registry.py source",
                "use comments or structured metadata without changing runtime behavior",
                "preserve deterministic registry build semantics",
            ],
        },
        {
            "batch_id": "PARTIAL_SCOPE_PREFIX_NORMALIZATION_BATCH",
            "batch_status": "ACTIVE" if siblings_missing_prefix else "PASS",
            "repair_mode": "OPERATOR_REVIEW_REQUIRED",
            "impacted_count": len(siblings_missing_prefix),
            "sample_impacted": _sample_impacted(siblings_missing_prefix),
            "source_lane_ids": sorted(partial_scope_prefix_lanes + siblings_missing_prefix),
            "partial_scope_prefix_lane_ids": sorted(partial_scope_prefix_lanes),
            "proposed_actions": [
                "require operator choice between bulk scope-prefix registration and explicit per-family entries",
                "document that P113 and P130 are partially covered by hard-coded scope prefixes today",
                "do not apply scope-prefix normalization without operator decision",
            ],
        },
        {
            "batch_id": "ORPHAN_RESEARCH_OUTPUT_POLICY_BATCH",
            "batch_status": "ACTIVE" if orphan_paths else "PASS",
            "repair_mode": "OPERATOR_REVIEW_REQUIRED",
            "impacted_count": len(orphan_paths),
            "sample_impacted": _sample_impacted(orphan_paths),
            "source_output_paths": orphan_paths,
            "proposed_actions": [
                "exclude orphan research outputs from P103-P130 canonical repair unless separately governed",
                "treat fold and stabilization lanes in the P94-P102 namespace as operator-review-only",
                "do not auto-promote orphan outputs into the research-canary spine chain",
            ],
        },
        {
            "batch_id": "P130_ADVISORY_HOLD_PRESERVATION_BATCH",
            "batch_status": "ACTIVE" if p130_lane_ids else "PASS",
            "repair_mode": "GOVERNANCE_BOUNDARY",
            "impacted_count": len(p130_lane_ids),
            "sample_impacted": _sample_impacted(p130_lane_ids),
            "source_lane_ids": sorted(p130_lane_ids),
            "proposed_actions": [
                "registry repair must not alter P130 hold routing",
                "registry repair must not imply activation authority for P130",
                "preserve p130_advisory_frontier_only governance boundary",
            ],
        },
        {
            "batch_id": "P102G_NAMESPACE_COLLISION_BATCH",
            "batch_status": "ACTIVE"
            if governance.get("p102g_temporal_continuity_spine_edge_preserved") is True
            else "PASS",
            "repair_mode": "GOVERNANCE_BOUNDARY",
            "impacted_count": 1,
            "sample_impacted": ["P102G_TEMPORAL_CONTINUITY_SPINE_EDGE"],
            "source_lane_ids": ["P102G_TEMPORAL_CONTINUITY_SPINE_EDGE", "P103_RESEARCH_SHADOW_REPLAY_AUDIT"],
            "proposed_actions": [
                "document P102G temporal-continuity edge versus research P103 branch separation",
                "preserve research_canary_not_promoted_to_temporal_continuity boundary",
                "do not collapse namespace collision into registry repair execution",
            ],
        },
    ]


def _active_batches(repair_batches: list[dict[str, Any]], repair_mode: str) -> list[str]:
    return [
        str(batch["batch_id"])
        for batch in repair_batches
        if batch.get("repair_mode") == repair_mode and batch.get("batch_status") == "ACTIVE"
    ]


def build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(
    *,
    repo_root: str | Path = ".",
    source_audit_path: str | Path = SOURCE_AUDIT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    audit_path = root / source_audit_path
    audit = _read_json(audit_path)
    source_observed = _validate_upstream_audit(audit)
    source_audit_hash = canonical_hash(audit) if audit else NOT_COMPUTABLE

    gap_confirmed = audit.get("audit_status") == "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED"
    repair_batches = _repair_batches(audit) if source_observed else []
    direct_repairable_batches = _active_batches(repair_batches, "REPO_LOCAL_DIRECT_REPAIR_CANDIDATE")
    operator_review_batches = _active_batches(repair_batches, "OPERATOR_REVIEW_REQUIRED")
    governance_boundary_batches = _active_batches(repair_batches, "GOVERNANCE_BOUNDARY")
    active_repair_batch_count = (
        len(direct_repairable_batches)
        + len(operator_review_batches)
        + len(governance_boundary_batches)
    )

    if source_observed and gap_confirmed and active_repair_batch_count > 0:
        spec_plan_status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_READY"
        recommended_next_lane = OPERATOR_DECISION_REQUEST_LANE
        downstream_status = "READY_FOR_OPERATOR_DECISION_REQUEST"
    elif source_observed and not gap_confirmed:
        spec_plan_status = NOT_COMPUTABLE
        recommended_next_lane = NOT_COMPUTABLE
        downstream_status = NOT_COMPUTABLE
    else:
        spec_plan_status = "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_BLOCKED"
        recommended_next_lane = NOT_COMPUTABLE
        downstream_status = NOT_COMPUTABLE

    governance_boundaries = {
        "p102g_temporal_continuity_spine_edge_preserved": True,
        "p130_advisory_frontier_only": True,
        "research_canary_not_promoted_to_temporal_continuity": True,
        "registry_repair_performed": False,
        "research_canary_spine_refresh_performed": False,
    }

    validation_gates = [
        {
            "gate_id": "source_audit_chain_gate",
            "required_audit_id": AUDIT_ID,
            "required_audit_status": "RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_GAP_CONFIRMED",
            "required_recommended_next_lane": SPEC_PLAN_ID,
            "passed": source_observed,
        },
        {
            "gate_id": "no_repair_execution_gate",
            "required_value": False,
            "observed_value": False,
            "passed": True,
        },
        {
            "gate_id": "blocked_actions_preserved_gate",
            "required_blocked_actions": list(BLOCKED_ACTIONS),
            "passed": True,
        },
        {
            "gate_id": "operator_authorization_required_before_registry_mutation_gate",
            "required_before": "any registry mutation for P103-P130 lanes",
            "passed": True,
        },
    ]

    base: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_id": ARTIFACT_ID,
        "spec_plan_id": SPEC_PLAN_ID,
        "spec_plan_status": spec_plan_status,
        "command": "BUILD_ABX_RESEARCH_CANARY_ARTIFACT_REGISTRY_COVERAGE_REPAIR_SPEC_PLAN_001",
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "evidence_only": True,
        "source_audit": {
            "source_audit_path": Path(source_audit_path).as_posix(),
            "source_audit_id": audit.get("audit_id", NOT_COMPUTABLE),
            "source_audit_status": audit.get("audit_status", NOT_COMPUTABLE),
            "source_audit_hash": source_audit_hash,
            "source_audit_observed": source_observed,
            "source_recommended_next_lane": audit.get("recommended_next_lane", NOT_COMPUTABLE),
        },
        "authorization_scope": "RESEARCH_CANARY_REGISTRY_COVERAGE_REPAIR_SPEC_AUTHORING_ONLY",
        "repair_batches": repair_batches,
        "direct_repairable_batches": direct_repairable_batches,
        "operator_review_batches": operator_review_batches,
        "governance_boundary_batches": governance_boundary_batches,
        "active_repair_batch_count": active_repair_batch_count,
        "proposed_phases": [dict(phase) for phase in PROPOSED_PHASES],
        "validation_gates": validation_gates,
        "governance_boundaries": governance_boundaries,
        "authority_locks": dict(AUTHORITY_LOCKS),
        "blocked_actions": list(BLOCKED_ACTIONS),
        "blocked_delivery_surfaces": list(BLOCKED_DELIVERY_SURFACES),
        "approval_granted": False,
        "authorization_granted": False,
        "authority_granted": False,
        "execution_allowed": False,
        "execution_authority": False,
        "implementation_authorized": False,
        "repair_execution_performed": False,
        "registry_mutation_performed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "token_minting_allowed": False,
        "valid_for_execution": False,
        "valid_for_repair": False,
        "valid_for_implementation": False,
        "safe_to_auto_continue": False,
        "safe_to_prepare_planning_pr": False,
        "recommended_next_action": (
            "review this repair spec plan as advisory evidence only; require explicit operator "
            "authorization before any registry mutation for P103-P130 research-canary lanes"
        ),
        "recommended_next_lane": recommended_next_lane,
        "downstream_status": downstream_status,
        "downstream": downstream_status,
    }
    return {**base, "spec_plan_hash": canonical_hash(base)}


def render_abx_research_canary_artifact_registry_coverage_repair_spec_plan_markdown(
    packet: Mapping[str, Any],
) -> list[str]:
    lines = [
        "# ABX Research Canary Artifact Registry Coverage Repair Spec Plan 001",
        "",
        f"- `spec_plan_id`: `{packet['spec_plan_id']}`",
        f"- `spec_plan_status`: `{packet['spec_plan_status']}`",
        f"- `recommended_next_lane`: `{packet['recommended_next_lane']}`",
        f"- `downstream_status`: `{packet['downstream_status']}`",
        f"- `registry_mutation_performed`: `{packet['registry_mutation_performed']}`",
        f"- `research_canary_spine_refresh_performed`: `{packet['governance_boundaries']['research_canary_spine_refresh_performed']}`",
        "",
        "## Source Audit",
    ]
    source_audit = packet.get("source_audit", {})
    if isinstance(source_audit, dict):
        for key in sorted(source_audit):
            lines.append(f"- `{key}`: `{source_audit[key]}`")
    lines.extend(["", "## Repair Batches"])
    for batch in packet.get("repair_batches", []):
        if isinstance(batch, dict):
            lines.append(
                f"- `{batch['batch_id']}`: `{batch['batch_status']}` via `{batch['repair_mode']}` "
                f"({batch['impacted_count']} impacted)"
            )
    lines.extend(["", "## Proposed Phases"])
    for phase in packet.get("proposed_phases", []):
        if isinstance(phase, dict):
            lines.append(f"- `{phase['phase_id']}`: `{phase['phase_name']}`")
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- `{action}`")
    lines.extend(["", "## Blocked Delivery Surfaces"])
    for surface in packet.get("blocked_delivery_surfaces", []):
        lines.append(f"- `{surface}`")
    return lines


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_abx_research_canary_artifact_registry_coverage_repair_spec_plan(
    source_root: str | Path = ".",
    out_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(source_root)
    target_root = Path(out_root) if out_root is not None else root
    packet = build_abx_research_canary_artifact_registry_coverage_repair_spec_plan(repo_root=root)
    write_canonical_json(target_root / OUT_JSON, packet)
    _write_markdown(
        target_root / OUT_MD,
        render_abx_research_canary_artifact_registry_coverage_repair_spec_plan_markdown(packet),
    )
    return packet
