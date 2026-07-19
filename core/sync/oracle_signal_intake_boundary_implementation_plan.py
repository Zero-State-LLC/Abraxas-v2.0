from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.oracle_signal_intake_boundary_alignment_plan import OUT_JSON as ALIGNMENT_PLAN_JSON

ARTIFACT_TYPE = "OracleSignalIntakeBoundaryImplementationPlan.v1"
PLAN_ID = "ORACLE_SIGNAL_INTAKE_BOUNDARY_IMPLEMENTATION_PLAN_001"
PATCH_ID = "PATCH-ABX-ORACLE-SIGNAL-INTAKE-BOUNDARY-001"
OUT_JSON = "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.json"
OUT_MD = "out/sync/oracle_signal_intake_boundary_implementation_plan/latest.md"

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_PLANNED_CONTRACT_PATHS = (
    "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
    "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
    "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
)
_PLANNED_RUNNER_PATHS = ("scripts/ingest/run_oracle_signal_intake_boundary.py",)
_PRESERVED_LEGACY_SURFACES = (
    "scripts/ingest/run_oracle_intake.py",
    "core/oracle/runtime.py",
    "core/oracle/intake.py",
    "contracts/ingest/oracle_intake_queue.v1.schema.json",
    "out/ingest/oracle_intake_queue_001.latest.json",
)


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return _NOT_COMPUTABLE


def _load_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _implementation_phases() -> list[dict[str, Any]]:
    return [
        {
            "phase_id": "ORACLE-PLAN-001",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Candidate contract formalization",
            "planned_outputs": list(_PLANNED_CONTRACT_PATHS),
            "boundary_guard": "contract-only additions; no oracle runtime replacement",
        },
        {
            "phase_id": "ORACLE-PLAN-002",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Candidate boundary runner",
            "planned_outputs": list(_PLANNED_RUNNER_PATHS),
            "boundary_guard": "read-only intake from governed oracle_intake_queue input",
        },
        {
            "phase_id": "ORACLE-PLAN-003",
            "phase_status": "PLANNED_ADVISORY_ONLY",
            "title": "Boundary verification",
            "planned_outputs": [
                "tests/test_oracle_signal_intake_boundary.py",
                "out/oracle/oracle_signal_intake_receipt.latest.json",
            ],
            "boundary_guard": "projection-only receipt validation with no forecast or execution authority",
        },
    ]


def _acceptance_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_id": "ORACLE-IMPL-GATE-001",
            "required_before": "candidate boundary implementation PR",
            "status": "PLANNING_ONLY",
        },
        {
            "gate_id": "ORACLE-IMPL-GATE-002",
            "required_before": "legacy oracle runtime mutation",
            "status": "PRESERVE_AS_OBSERVED",
        },
        {
            "gate_id": "ORACLE-IMPL-GATE-003",
            "required_before": "forecast, canon, runtime, queue, or execution authority",
            "status": "AUTHORITY_DENIED",
        },
    ]


def build_oracle_signal_intake_boundary_implementation_plan(
    *,
    repo_root: str | Path,
    alignment_plan_path: str | Path = ALIGNMENT_PLAN_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    alignment_target = root / alignment_plan_path
    alignment_packet = _load_json(alignment_target)

    alignment_ready = (
        alignment_packet.get("artifact_type") == "OracleSignalIntakeBoundaryAlignmentPlan.v1"
        and alignment_packet.get("plan_status")
        in {
            "ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY",
            "ALIGNMENT_PLAN_BOUNDARY_OBSERVED_ADVISORY_ONLY",
        }
    )
    preserved_surfaces_observed = all((root / rel_path).exists() for rel_path in _PRESERVED_LEGACY_SURFACES)
    boundary_paths = [
        *_PLANNED_CONTRACT_PATHS,
        *_PLANNED_RUNNER_PATHS,
    ]
    missing_boundary_paths = [
        rel_path
        for rel_path in boundary_paths
        if not (root / rel_path).exists()
    ]
    implemented_boundary_paths = [
        rel_path
        for rel_path in boundary_paths
        if (root / rel_path).exists()
    ]
    all_boundary_paths_observed = len(implemented_boundary_paths) == len(boundary_paths)
    plan_ready = alignment_ready and preserved_surfaces_observed and bool(missing_boundary_paths)
    planning_pr_consumed = alignment_ready and preserved_surfaces_observed and all_boundary_paths_observed
    safe_to_prepare_planning_pr = plan_ready and not planning_pr_consumed

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": (
            "IMPLEMENTATION_PLAN_BOUNDARY_OBSERVED_ADVISORY_ONLY"
            if planning_pr_consumed
            else "IMPLEMENTATION_PLAN_EMITTED_ADVISORY_ONLY"
            if plan_ready
            else _NOT_COMPUTABLE
        ),
        "patch_id": PATCH_ID,
        "depends_on_artifacts": [Path(alignment_plan_path).as_posix()],
        "source_artifact_hashes": {
            Path(alignment_plan_path).as_posix(): _sha256(alignment_target),
        },
        "target_surface": "Oracle Signal Intake Boundary",
        "alignment_ready": alignment_ready,
        "preserved_surfaces_observed": preserved_surfaces_observed,
        "preserved_legacy_surfaces": list(_PRESERVED_LEGACY_SURFACES),
        "planned_contract_paths": list(_PLANNED_CONTRACT_PATHS),
        "planned_runner_paths": list(_PLANNED_RUNNER_PATHS),
        "missing_boundary_paths": missing_boundary_paths,
        "implemented_boundary_paths": implemented_boundary_paths,
        "all_boundary_paths_observed": all_boundary_paths_observed,
        "planning_pr_consumed": planning_pr_consumed,
        "implementation_phases": _implementation_phases(),
        "acceptance_gates": _acceptance_gates(),
        "blocked_actions": [
            "AUTO_CREATE_NEXT_PATCH",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "ORACLE_FORECAST_ROUTING",
            "ORACLE_EXECUTION_AUTHORITY",
            "ORACLE_CANON_MUTATION",
            "ORACLE_RUNTIME_MUTATION",
            "ORACLE_QUEUE_MUTATION",
            "LEGACY_RUNTIME_REPLACEMENT",
        ],
        "recommended_next_patch": PATCH_ID if safe_to_prepare_planning_pr else _NOT_COMPUTABLE,
        "recommended_next_action": (
            "prepare a separate planning-only boundary PR with additive contracts and a candidate-only runner"
            if safe_to_prepare_planning_pr
            else "hold; oracle intake boundary implementation paths are already repo-observed as advisory-only evidence"
            if planning_pr_consumed
            else "repair oracle intake boundary implementation-plan evidence"
        ),
        "required_operator_input": (
            "preserve advisory-only candidate intake posture and keep legacy oracle runtime surfaces observed-only"
        ),
        "safe_to_prepare_planning_pr": safe_to_prepare_planning_pr,
        "safe_to_prepare_implementation_pr": False,
        "safe_to_auto_continue": False,
        "auto_patch_generation_allowed": False,
        "implementation_allowed": False,
        "notion_writeback_allowed": False,
        "github_writeback_allowed": False,
        "advisory_only": True,
        "projection_only": True,
        "evidence_only": True,
        "non_authoritative": True,
        "forecast_routing": False,
        "canon_mutation": False,
        "runtime_mutation": False,
        "scheduler_mutation": False,
        "queue_mutation": False,
        "execution_authority": False,
        "valid_for_execution": False,
        "authority_locks": {
            "auto_patch_generation": False,
            "canon_mutation": False,
            "execution_authority": False,
            "forecast_routing": False,
            "github_writeback": False,
            "implementation": False,
            "notion_writeback": False,
            "queue_mutation": False,
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_oracle_signal_intake_boundary_implementation_plan(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)


def write_oracle_signal_intake_boundary_implementation_plan_markdown(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    lines = [
        "# Oracle Signal Intake Boundary Implementation Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- patch_id: {packet['patch_id']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- recommended_next_action: {packet['recommended_next_action']}",
        f"- safe_to_prepare_planning_pr: {packet['safe_to_prepare_planning_pr']}",
        f"- safe_to_prepare_implementation_pr: {packet['safe_to_prepare_implementation_pr']}",
        f"- implementation_allowed: {packet['implementation_allowed']}",
        f"- valid_for_execution: {packet['valid_for_execution']}",
        "",
        "## Planned Contract Paths",
    ]
    for rel_path in packet.get("planned_contract_paths", []):
        lines.append(f"- {rel_path}")
    lines.extend(["", "## Planned Runner Paths"])
    for rel_path in packet.get("planned_runner_paths", []):
        lines.append(f"- {rel_path}")
    lines.extend(["", "## Missing Boundary Paths"])
    for rel_path in packet.get("missing_boundary_paths", []):
        lines.append(f"- {rel_path}")
    lines.extend(["", "## Implemented Boundary Paths"])
    for rel_path in packet.get("implemented_boundary_paths", []):
        lines.append(f"- {rel_path}")
    lines.extend(["", "## Preserved Legacy Surfaces"])
    for rel_path in packet.get("preserved_legacy_surfaces", []):
        lines.append(f"- {rel_path}")
    lines.extend(["", "## Implementation Phases"])
    for phase in packet.get("implementation_phases", []):
        lines.append(f"- {phase['phase_id']}: {phase['title']}")
    lines.extend(["", "## Acceptance Gates"])
    for gate in packet.get("acceptance_gates", []):
        lines.append(f"- {gate['gate_id']}: {gate['status']} before {gate['required_before']}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
