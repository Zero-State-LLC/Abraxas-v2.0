from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.sync.global_ingest_adapter_spine_alignment_plan import (
    OUT_JSON as GLOBAL_INGEST_ALIGNMENT_JSON,
)

ARTIFACT_TYPE = "OracleSignalIntakeBoundaryAlignmentPlan.v1"
PLAN_ID = "ORACLE_SIGNAL_INTAKE_BOUNDARY_ALIGNMENT_PLAN_001"
PATCH_ID = "PATCH-ABX-ORACLE-SIGNAL-INTAKE-BOUNDARY-001"
OUT_JSON = "out/sync/oracle_signal_intake_boundary_alignment_plan/latest.json"
OUT_MD = "out/sync/oracle_signal_intake_boundary_alignment_plan/latest.md"

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_LEGACY_RUNTIME_PATHS = (
    "scripts/run_oracle_intake.py",
    "core/oracle/runtime.py",
    "core/oracle/intake.py",
    "contracts/ingest/oracle_intake_queue.v1.schema.json",
    "out/ingest/oracle_intake_queue_001.latest.json",
)
_TARGET_BOUNDARY_PATHS = (
    "contracts/oracle/oracle_candidate_signal_packet.v1.schema.json",
    "contracts/oracle/oracle_signal_input_envelope_ref.v1.schema.json",
    "contracts/oracle/oracle_signal_intake_receipt.v1.schema.json",
    "scripts/run_oracle_signal_intake_boundary.py",
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


def _observed_surfaces(root: Path) -> list[dict[str, str]]:
    roles = {
        "scripts/run_oracle_intake.py": "legacy oracle intake runner",
        "core/oracle/runtime.py": "legacy oracle intake packet emitter",
        "core/oracle/intake.py": "legacy oracle intake envelope model",
        "contracts/ingest/oracle_intake_queue.v1.schema.json": "governed ingest queue contract",
        "out/ingest/oracle_intake_queue_001.latest.json": "governed ingest queue artifact",
    }
    observed: list[dict[str, str]] = []
    for rel_path in _LEGACY_RUNTIME_PATHS:
        if (root / rel_path).exists():
            observed.append(
                {
                    "path": rel_path,
                    "role": roles[rel_path],
                    "preserve_as_observed": "true",
                }
            )
    return observed


def _missing_boundary_paths(root: Path) -> list[str]:
    return [rel_path for rel_path in _TARGET_BOUNDARY_PATHS if not (root / rel_path).exists()]


def _implemented_boundary_paths(root: Path) -> list[str]:
    return [rel_path for rel_path in _TARGET_BOUNDARY_PATHS if (root / rel_path).exists()]


def _alignment_steps() -> list[dict[str, str]]:
    return [
        {
            "step_id": "ORACLE-ALIGN-001",
            "step_status": "PLANNED_ADVISORY_ONLY",
            "description": "Audit and preserve legacy oracle intake surfaces before introducing candidate-only boundary artifacts.",
            "authority_boundary": "no legacy oracle runtime mutation in this audit lane",
        },
        {
            "step_id": "ORACLE-ALIGN-002",
            "step_status": "PLANNED_ADVISORY_ONLY",
            "description": "Define candidate packet, envelope reference, and intake receipt surfaces as additive boundary contracts.",
            "authority_boundary": "no Oracle authority expansion and no forecast routing",
        },
        {
            "step_id": "ORACLE-ALIGN-003",
            "step_status": "PLANNED_ADVISORY_ONLY",
            "description": "Align future boundary runner with governed ingest queue inputs rather than rebuilding Oracle Signal Layer v2.",
            "authority_boundary": "candidate-only, SHADOW-only, fail-closed",
        },
    ]


def _acceptance_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_id": "ORACLE-GATE-001",
            "required_before": "legacy oracle runtime mutation",
            "status": "AUDIT_REQUIRED",
        },
        {
            "gate_id": "ORACLE-GATE-002",
            "required_before": "candidate boundary implementation",
            "status": "IMPLEMENTATION_PLAN_ONLY",
        },
        {
            "gate_id": "ORACLE-GATE-003",
            "required_before": "forecast, canon, runtime, or execution authority",
            "status": "AUTHORITY_DENIED",
        },
    ]


def build_oracle_signal_intake_boundary_alignment_plan(
    *,
    repo_root: str | Path,
    global_ingest_alignment_path: str | Path = GLOBAL_INGEST_ALIGNMENT_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    ingest_alignment_target = root / global_ingest_alignment_path
    ingest_alignment_packet = _load_json(ingest_alignment_target)
    observed_surfaces = _observed_surfaces(root)
    missing_boundary_paths = _missing_boundary_paths(root)
    implemented_boundary_paths = _implemented_boundary_paths(root)

    legacy_runtime_observed = len(observed_surfaces) >= 4
    governed_ingest_aligned = (
        ingest_alignment_packet.get("artifact_type")
        == "GlobalIngestAdapterSpineAlignmentPlan.v1"
        and ingest_alignment_packet.get("plan_status") == "ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY"
    )
    missing_boundary_observed = bool(missing_boundary_paths)
    implemented_boundary_observed = bool(implemented_boundary_paths)
    boundary_state_observed = missing_boundary_observed or implemented_boundary_observed
    plan_ready = legacy_runtime_observed and governed_ingest_aligned and boundary_state_observed

    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": "ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY" if plan_ready else _NOT_COMPUTABLE,
        "patch_id": PATCH_ID,
        "depends_on_artifacts": [Path(global_ingest_alignment_path).as_posix()],
        "source_artifact_hashes": {
            Path(global_ingest_alignment_path).as_posix(): _sha256(ingest_alignment_target),
        },
        "target_surface": "Oracle Signal Intake Boundary",
        "legacy_runtime_observed": legacy_runtime_observed,
        "governed_ingest_aligned": governed_ingest_aligned,
        "missing_boundary_observed": missing_boundary_observed,
        "implemented_boundary_observed": implemented_boundary_observed,
        "observed_surfaces": observed_surfaces,
        "missing_boundary_paths": missing_boundary_paths,
        "implemented_boundary_paths": implemented_boundary_paths,
        "alignment_steps": _alignment_steps(),
        "acceptance_gates": _acceptance_gates(),
        "blocked_actions": [
            "AUTO_CREATE_NEXT_PATCH",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "ORACLE_FORECAST_ROUTING",
            "ORACLE_EXECUTION_AUTHORITY",
            "ORACLE_CANON_MUTATION",
            "ORACLE_RUNTIME_MUTATION",
            "LEGACY_RUNTIME_REPLACEMENT_WITHOUT_AUDIT",
        ],
        "recommended_next_patch": PATCH_ID if plan_ready else _NOT_COMPUTABLE,
        "recommended_next_action": (
            "prepare implementation-plan-first oracle intake boundary lane"
            if plan_ready
            else "repair oracle intake boundary alignment evidence"
        ),
        "required_operator_input": (
            "preserve advisory-only candidate intake posture; do not grant forecast, canon, runtime, or execution authority"
        ),
        "safe_to_prepare_planning_pr": plan_ready,
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
            "runtime_mutation": False,
            "scheduler_mutation": False,
            "token_minting": False,
        },
    }
    return {**base, "packet_hash": canonical_hash(base)}


def write_oracle_signal_intake_boundary_alignment_plan(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    write_canonical_json(path, packet)


def write_oracle_signal_intake_boundary_alignment_plan_markdown(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    lines = [
        "# Oracle Signal Intake Boundary Alignment Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- patch_id: {packet['patch_id']}",
        f"- target_surface: {packet['target_surface']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- recommended_next_action: {packet['recommended_next_action']}",
        f"- safe_to_prepare_planning_pr: {packet['safe_to_prepare_planning_pr']}",
        f"- implementation_allowed: {packet['implementation_allowed']}",
        "",
        "## Observed Surfaces",
    ]
    for entry in packet.get("observed_surfaces", []):
        lines.append(f"- {entry['path']} - {entry['role']}")
    lines.extend(["", "## Missing Boundary Paths"])
    for rel_path in packet.get("missing_boundary_paths", []):
        lines.append(f"- {rel_path}")
    lines.extend(["", "## Implemented Boundary Paths"])
    for rel_path in packet.get("implemented_boundary_paths", []):
        lines.append(f"- {rel_path}")
    lines.extend(["", "## Alignment Steps"])
    for step in packet.get("alignment_steps", []):
        lines.append(f"- {step['step_id']}: {step['description']}")
    lines.extend(["", "## Acceptance Gates"])
    for gate in packet.get("acceptance_gates", []):
        lines.append(f"- {gate['gate_id']}: {gate['status']} before {gate['required_before']}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
