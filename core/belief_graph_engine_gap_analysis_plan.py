from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.belief_graph_gap_verification import OUT_JSON as BELIEF_GRAPH_GAP_VERIFICATION_JSON
from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "BeliefGraphEngineGapAnalysisPlan.v1"
PLAN_ID = "BELIEF_GRAPH_ENGINE_GAP_ANALYSIS_PLAN_001"
OUT_JSON = "out/audit/belief_graph_engine_gap_analysis_plan_001.latest.json"
OUT_MD = "out/audit/belief_graph_engine_gap_analysis_plan_001.latest.md"

REPO_NOTION_DIFF_JSON = "docs/audits/abraxas_repo_notion_diff_001.json"
CANON_RESUME_STATE_JSON = "out/canon_resume_state/latest.json"
AUTHORIZATION_RECORD_PLAN_JSON = (
    "out/temporal_continuity_upstream_input_regeneration_authorization_record_plan/latest.json"
)

_ENGINE_REQUIRED_PATHS: tuple[str, ...] = (
    "core/belief_graph_engine.py",
    "contracts/canon/belief_graph_engine.v1.schema.json",
    "scripts/run_belief_graph_engine.py",
    "tests/test_belief_graph_engine.py",
    "out/belief_graph/belief_graph_engine_001.latest.json",
)

_PRIMITIVE_PATHS: tuple[str, ...] = (
    "core/belief_graph/claim_object.py",
    "core/belief_graph/evidence_object.py",
    "core/belief_graph/theory_object.py",
    "core/belief_graph/signal_graph.py",
    "core/belief_graph/belief_graph_packet.py",
    "core/belief_graph/belief_graph_builder.py",
    "contracts/belief_graph/claim_object.v1.schema.json",
    "contracts/belief_graph/evidence_object.v1.schema.json",
    "contracts/belief_graph/theory_object.v1.schema.json",
    "contracts/belief_graph/signal_graph.v1.schema.json",
    "contracts/belief_graph/belief_graph_packet.v1.schema.json",
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return "NOT_COMPUTABLE"


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _notion_surface_record(repo_notion_diff: Mapping[str, Any]) -> Mapping[str, Any]:
    targets = repo_notion_diff.get("notion_targets", [])
    if not isinstance(targets, list):
        return {}
    for target in targets:
        if isinstance(target, dict) and target.get("notion_surface") == "BELIEF_GRAPH_ENGINE_001":
            return target
    return {}


def _path_records(repo_root: Path, paths: tuple[str, ...]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in paths:
        target = repo_root / path
        observed = target.exists()
        records.append(
            {
                "path": path,
                "status": "OBSERVED" if observed else "MISSING",
                "source_hash": _sha256(target) if observed else "NOT_COMPUTABLE",
            }
        )
    return records


def _planning_phases() -> list[dict[str, Any]]:
    return [
        {
            "phase_id": "phase_001_evidence_consolidation",
            "phase_status": "PLANNED_ONLY",
            "required_input": "repo-visible gap and primitive-surface receipts",
            "exit_condition": "engine gap, primitive scaffold, and authority locks are recorded",
        },
        {
            "phase_id": "phase_002_contract_boundary",
            "phase_status": "PLANNED_ONLY",
            "required_input": "separate governed Belief Graph engine spec",
            "exit_condition": "schema boundaries distinguish advisory graph evidence from truth assignment",
        },
        {
            "phase_id": "phase_003_route_binding_review",
            "phase_status": "PLANNED_ONLY",
            "required_input": "YGGDRASIL route and pipeline contract evidence",
            "exit_condition": "route bindings are proposed without dispatch or runtime mutation",
        },
        {
            "phase_id": "phase_004_fixture_and_test_plan",
            "phase_status": "PLANNED_ONLY",
            "required_input": "deterministic fixtures and validation-only tests",
            "exit_condition": "future implementation tests are scoped before any engine code is added",
        },
        {
            "phase_id": "phase_005_operator_gate_mapping",
            "phase_status": "PLANNED_ONLY",
            "required_input": "explicit operator authorization design in a future lane",
            "exit_condition": "execution remains denied unless a later governed lane grants it",
        },
    ]


def build_belief_graph_engine_gap_analysis_plan(
    *,
    repo_root: str | Path,
    repo_notion_diff_path: str | Path = REPO_NOTION_DIFF_JSON,
    belief_graph_gap_verification_path: str | Path = BELIEF_GRAPH_GAP_VERIFICATION_JSON,
    canon_resume_state_path: str | Path = CANON_RESUME_STATE_JSON,
    authorization_record_plan_path: str | Path = AUTHORIZATION_RECORD_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    repo_notion_diff = _read_json(root / repo_notion_diff_path)
    gap_verification = _read_json(root / belief_graph_gap_verification_path)
    canon_resume = _read_json(root / canon_resume_state_path)
    authorization_record_plan = _read_json(root / authorization_record_plan_path)
    notion_record = _notion_surface_record(repo_notion_diff)

    engine_path_records = _path_records(root, _ENGINE_REQUIRED_PATHS)
    primitive_path_records = _path_records(root, _PRIMITIVE_PATHS)
    engine_missing_count = sum(1 for record in engine_path_records if record["status"] == "MISSING")
    primitive_observed_count = sum(1 for record in primitive_path_records if record["status"] == "OBSERVED")
    required_source_statuses = {
        "repo_notion_diff": "OBSERVED" if repo_notion_diff else "MISSING",
        "belief_graph_gap_verification": "OBSERVED" if gap_verification else "MISSING",
        "canon_resume_state": "OBSERVED" if canon_resume else "MISSING",
        "authorization_record_plan": "OBSERVED" if authorization_record_plan else "MISSING",
    }
    required_sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    plan_status = (
        "BELIEF_GRAPH_ENGINE_GAP_ANALYSIS_PLAN_READY"
        if required_sources_observed and engine_missing_count > 0
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "target_surface": "BELIEF_GRAPH_ENGINE_001",
        "target_surface_status": "ENGINE_MISSING_PRIMITIVES_OBSERVED",
        "notion_source": "ABRAXAS_REPO_NOTION_DIFF_001",
        "patch_id": "PATCH-ABX-BELIEF-GRAPH-ENGINE-GAP-ANALYSIS-PLAN-001",
        "source_paths": {
            "repo_notion_diff": Path(repo_notion_diff_path).as_posix(),
            "belief_graph_gap_verification": Path(belief_graph_gap_verification_path).as_posix(),
            "canon_resume_state": Path(canon_resume_state_path).as_posix(),
            "authorization_record_plan": Path(authorization_record_plan_path).as_posix(),
        },
        "source_hashes": {
            "repo_notion_diff": _sha256(root / repo_notion_diff_path),
            "belief_graph_gap_verification": _sha256(root / belief_graph_gap_verification_path),
            "canon_resume_state": _sha256(root / canon_resume_state_path),
            "authorization_record_plan": _sha256(root / authorization_record_plan_path),
        },
        "required_source_statuses": required_source_statuses,
        "notion_gap_evidence": {
            "repo_equivalent_found": bool(notion_record.get("repo_equivalent_found", False)),
            "implementation_status": str(notion_record.get("implementation_status", "NOT_COMPUTABLE")),
            "match_strength": str(notion_record.get("match_strength", "NOT_COMPUTABLE")),
            "recommended_action": str(notion_record.get("recommended_action", "NOT_COMPUTABLE")),
            "missing_elements": [
                str(item)
                for item in notion_record.get("missing_elements", [])
                if isinstance(item, str)
            ],
        },
        "primitive_scaffold_evidence": {
            "belief_graph_equivalent_observed": bool(
                gap_verification.get("belief_graph_equivalent_observed", False)
            ),
            "observed_components": int(gap_verification.get("summary", {}).get("observed_components", 0))
            if isinstance(gap_verification.get("summary"), dict)
            else 0,
            "missing_components": int(gap_verification.get("summary", {}).get("missing_components", 0))
            if isinstance(gap_verification.get("summary"), dict)
            else 0,
            "primitive_paths_observed": primitive_observed_count,
            "primitive_paths_total": len(primitive_path_records),
        },
        "engine_required_path_records": engine_path_records,
        "primitive_path_records": primitive_path_records,
        "gap_summary": {
            "engine_required_paths": len(engine_path_records),
            "engine_missing_paths": engine_missing_count,
            "primitive_required_paths": len(primitive_path_records),
            "primitive_observed_paths": primitive_observed_count,
        },
        "planning_phases": _planning_phases(),
        "blocked_actions": [
            "belief_graph_engine_implementation",
            "runtime_dispatch_mutation",
            "canon_mutation",
            "queue_mutation",
            "scheduler_mutation",
            "truth_assignment",
            "belief_promotion",
            "forecast_routing",
            "notion_writeback",
            "github_writeback",
            "activation_or_execution",
        ],
        "continuity_boundary": {
            "canon_resume_recommended_resume_lane": str(
                canon_resume.get("recommended_resume_lane", "NOT_COMPUTABLE")
            ),
            "authorization_record_plan_status": str(
                authorization_record_plan.get("authorization_record_plan_status", "NOT_COMPUTABLE")
            ),
            "preflight_sources_are_advisory_only": True,
            "preflight_grants_execution_authority": False,
        },
        "recommended_next_lane": "BELIEF_GRAPH_ENGINE_ADVISORY_SPEC_PLAN",
        "recommended_next_action": (
            "author a separate advisory spec plan before any Belief Graph engine implementation"
        ),
        "belief_graph_engine_implementation_performed": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "forecast_routing_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": {
            "belief_promotion": False,
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "truth_assignment": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_belief_graph_engine_gap_analysis_plan(path: str | Path, packet: Mapping[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_belief_graph_engine_gap_analysis_plan_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# Belief Graph Engine Gap Analysis Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_surface_status: {packet['target_surface_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- belief_graph_engine_implementation_performed: {packet['belief_graph_engine_implementation_performed']}",
        f"- execution_authority: {packet['execution_authority']}",
        f"- valid_for_implementation: {packet['valid_for_implementation']}",
        f"- notion_writeback_allowed: {packet['notion_writeback_allowed']}",
        f"- github_writeback_allowed: {packet['github_writeback_allowed']}",
        "",
        "## Gap Summary",
    ]
    gap_summary = packet.get("gap_summary", {})
    if isinstance(gap_summary, dict):
        for key in sorted(gap_summary):
            lines.append(f"- {key}: {gap_summary[key]}")
    lines.extend(["", "## Planning Phases"])
    for phase in packet.get("planning_phases", []):
        if isinstance(phase, dict):
            lines.append(
                "- "
                f"{phase['phase_id']}: {phase['phase_status']} "
                f"(exit_condition={phase['exit_condition']})"
            )
    lines.extend(["", "## Blocked Actions"])
    for action in packet.get("blocked_actions", []):
        lines.append(f"- {action}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
