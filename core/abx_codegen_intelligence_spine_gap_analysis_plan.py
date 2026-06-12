from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from core.canonical.json import canonical_hash, write_canonical_json

ARTIFACT_TYPE = "AbxCodegenIntelligenceSpineGapAnalysisPlan.v1"
PLAN_ID = "ABX_CODEGEN_INTELLIGENCE_SPINE_GAP_ANALYSIS_PLAN_001"
OUT_JSON = "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.json"
OUT_MD = "out/audit/abx_codegen_intelligence_spine_gap_analysis_plan_001.latest.md"

REPO_NOTION_DIFF_JSON = "docs/audits/abraxas_repo_notion_diff_001.json"
CANON_RESUME_STATE_JSON = "out/canon_resume_state/latest.json"

_SPINE_REQUIRED_PATHS: tuple[str, ...] = (
    "core/abx_codegen_intelligence_spine.py",
    "contracts/canon/abx_codegen_intelligence_spine.v1.schema.json",
    "scripts/run_abx_codegen_intelligence_spine.py",
    "tests/test_abx_codegen_intelligence_spine.py",
    "out/audit/abx_codegen_intelligence_spine_001.latest.json",
)

_GENERATED_ARTIFACT_CONTROL_PATHS: tuple[str, ...] = (
    "core/generated_artifact_registry.py",
    "scripts/run_artifact_regeneration.py",
    "tests/test_generated_artifact_registry.py",
    "out/audit/artifact_regeneration_001.latest.json",
    "out/audit/artifact_regeneration_001.latest.md",
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
        if (
            isinstance(target, dict)
            and target.get("notion_surface") == "ABX_CODEGEN_INTELLIGENCE_SPINE_001"
        ):
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
            "phase_id": "phase_001_gap_and_control_inventory",
            "phase_status": "PLANNED_ONLY",
            "required_input": "repo-visible Codegen Spine gap and generated artifact controls",
            "exit_condition": "missing codegen spine paths and observed policy controls are recorded",
        },
        {
            "phase_id": "phase_002_contract_boundary",
            "phase_status": "PLANNED_ONLY",
            "required_input": "separate governed Codegen Spine advisory spec",
            "exit_condition": "schema denies code mutation, writeback, execution, and auto-approval",
        },
        {
            "phase_id": "phase_003_generator_policy_mapping",
            "phase_status": "PLANNED_ONLY",
            "required_input": "generated artifact registry and regeneration policy evidence",
            "exit_condition": "future generator plans map to deterministic artifact policy controls",
        },
        {
            "phase_id": "phase_004_fixture_and_validation_plan",
            "phase_status": "PLANNED_ONLY",
            "required_input": "deterministic fixtures and validation-only tests",
            "exit_condition": "future codegen-spine checks are scoped before any spine code is added",
        },
        {
            "phase_id": "phase_005_operator_gate_mapping",
            "phase_status": "PLANNED_ONLY",
            "required_input": "explicit operator authorization design in a future lane",
            "exit_condition": "code generation and repository mutation remain denied unless a later governed lane grants them",
        },
    ]


def build_abx_codegen_intelligence_spine_gap_analysis_plan(
    *,
    repo_root: str | Path,
    repo_notion_diff_path: str | Path = REPO_NOTION_DIFF_JSON,
    canon_resume_state_path: str | Path = CANON_RESUME_STATE_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    repo_notion_diff = _read_json(root / repo_notion_diff_path)
    canon_resume = _read_json(root / canon_resume_state_path)
    notion_record = _notion_surface_record(repo_notion_diff)

    spine_path_records = _path_records(root, _SPINE_REQUIRED_PATHS)
    control_path_records = _path_records(root, _GENERATED_ARTIFACT_CONTROL_PATHS)
    spine_missing_count = sum(1 for record in spine_path_records if record["status"] == "MISSING")
    control_observed_count = sum(1 for record in control_path_records if record["status"] == "OBSERVED")
    required_source_statuses = {
        "repo_notion_diff": "OBSERVED" if repo_notion_diff else "MISSING",
        "canon_resume_state": "OBSERVED" if canon_resume else "MISSING",
    }
    required_sources_observed = all(status == "OBSERVED" for status in required_source_statuses.values())
    plan_status = (
        "ABX_CODEGEN_INTELLIGENCE_SPINE_GAP_ANALYSIS_PLAN_READY"
        if required_sources_observed and spine_missing_count > 0
        else "NOT_COMPUTABLE"
    )

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": plan_status,
        "target_surface": "ABX_CODEGEN_INTELLIGENCE_SPINE_001",
        "target_surface_status": "SPINE_MISSING_GENERATED_ARTIFACT_CONTROLS_OBSERVED",
        "notion_source": "ABRAXAS_REPO_NOTION_DIFF_001",
        "patch_id": "PATCH-ABX-CODEGEN-INTELLIGENCE-SPINE-GAP-ANALYSIS-PLAN-001",
        "source_paths": {
            "repo_notion_diff": Path(repo_notion_diff_path).as_posix(),
            "canon_resume_state": Path(canon_resume_state_path).as_posix(),
        },
        "source_hashes": {
            "repo_notion_diff": _sha256(root / repo_notion_diff_path),
            "canon_resume_state": _sha256(root / canon_resume_state_path),
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
        "generated_artifact_control_evidence": {
            "control_paths_observed": control_observed_count,
            "control_paths_total": len(control_path_records),
            "policy_control_surface": "GENERATED_ARTIFACT_POLICY_V1",
            "regeneration_policy_is_advisory_only": True,
            "regeneration_policy_grants_code_mutation": False,
        },
        "spine_required_path_records": spine_path_records,
        "generated_artifact_control_path_records": control_path_records,
        "gap_summary": {
            "spine_required_paths": len(spine_path_records),
            "spine_missing_paths": spine_missing_count,
            "control_required_paths": len(control_path_records),
            "control_observed_paths": control_observed_count,
        },
        "planning_phases": _planning_phases(),
        "blocked_actions": [
            "codegen_spine_implementation",
            "code_generation",
            "code_mutation",
            "file_writeback",
            "runtime_dispatch_mutation",
            "canon_mutation",
            "queue_mutation",
            "scheduler_mutation",
            "forecast_routing",
            "notion_writeback",
            "github_writeback",
            "auto_approval",
            "activation_or_execution",
        ],
        "continuity_boundary": {
            "canon_resume_recommended_resume_lane": str(
                canon_resume.get("recommended_resume_lane", "NOT_COMPUTABLE")
            ),
            "preflight_sources_are_advisory_only": True,
            "preflight_grants_execution_authority": False,
        },
        "recommended_next_lane": "ABX_CODEGEN_INTELLIGENCE_SPINE_ADVISORY_SPEC_PLAN",
        "recommended_next_action": (
            "author a separate advisory spec plan before any codegen spine implementation"
        ),
        "codegen_spine_implementation_performed": False,
        "advisory_only": True,
        "projection_only": True,
        "non_authoritative": True,
        "execution_authority": False,
        "valid_for_execution": False,
        "valid_for_implementation": False,
        "code_generation_allowed": False,
        "code_mutation_allowed": False,
        "file_writeback_allowed": False,
        "runtime_mutation_allowed": False,
        "canon_mutation_allowed": False,
        "queue_mutation_allowed": False,
        "scheduler_mutation_allowed": False,
        "forecast_routing_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "authority_locks": {
            "auto_approval": False,
            "canon_mutation": False,
            "code_generation": False,
            "code_mutation": False,
            "execution_authority": False,
            "file_writeback": False,
            "forecast_routing": False,
            "github_writeback": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_abx_codegen_intelligence_spine_gap_analysis_plan(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    write_canonical_json(path, packet)


def write_abx_codegen_intelligence_spine_gap_analysis_plan_markdown(
    path: str | Path, packet: Mapping[str, Any]
) -> None:
    lines = [
        "# ABX Codegen Intelligence Spine Gap Analysis Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- target_surface: {packet['target_surface']}",
        f"- target_surface_status: {packet['target_surface_status']}",
        f"- recommended_next_lane: {packet['recommended_next_lane']}",
        f"- codegen_spine_implementation_performed: {packet['codegen_spine_implementation_performed']}",
        f"- code_generation_allowed: {packet['code_generation_allowed']}",
        f"- code_mutation_allowed: {packet['code_mutation_allowed']}",
        f"- file_writeback_allowed: {packet['file_writeback_allowed']}",
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
