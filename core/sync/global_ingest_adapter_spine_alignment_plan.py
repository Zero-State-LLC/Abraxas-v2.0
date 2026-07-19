from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.canonical.json import canonical_hash, write_canonical_json
from core.repo_notion_diff import OUT_JSON as REPO_NOTION_DIFF_JSON
from core.sync.notion_patch_queue_terminal_state import OUT_JSON as TERMINAL_STATE_JSON

ARTIFACT_TYPE = "GlobalIngestAdapterSpineAlignmentPlan.v1"
PLAN_ID = "GLOBAL_INGEST_ADAPTER_SPINE_ALIGNMENT_PLAN_001"
PATCH_ID = "PATCH-ABX-GLOBAL-INGEST-ADAPTER-SPINE-ALIGNMENT-PLAN-001"
OUT_JSON = "out/sync/global_ingest_adapter_spine_alignment_plan/latest.json"
OUT_MD = "out/sync/global_ingest_adapter_spine_alignment_plan/latest.md"

_NOT_COMPUTABLE = "NOT_COMPUTABLE"
_TARGET_SURFACE = "Global Ingest Adapter Spine"
_TARGET_PATHS = (
    "scripts/ingest/run_ingest_once.py",
    "scripts/ingest/run_oracle_intake.py",
    "core/oracle_signal.py",
)
OPERATOR_DECISION_RECORD_PATH = "out/operator_review/global_ingest_operator_decision_record_001.latest.json"
SEPARATE_IMPLEMENTATION_SPEC_PLAN_PATH = (
    "out/operator_review/global_ingest_separate_implementation_spec_plan_001.latest.json"
)
IMPLEMENTATION_SPEC_PATH = "out/operator_review/global_ingest_adapter_spine_implementation_spec_001.latest.json"


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


def _global_ingest_record(diff_packet: dict[str, Any]) -> dict[str, Any]:
    records = diff_packet.get("diff_records", [])
    if not isinstance(records, list):
        return {}
    for record in records:
        if isinstance(record, dict) and record.get("notion_surface") == _TARGET_SURFACE:
            return record
    return {}


def _observed_entrypoints(record: dict[str, Any]) -> list[dict[str, Any]]:
    roles = {
        "scripts/ingest/run_ingest_once.py": "single-run ingest entrypoint",
        "scripts/ingest/run_oracle_intake.py": "oracle intake entrypoint",
    }
    return [
        {
            "path": path,
            "role": roles.get(path, "observed ingest surface"),
            "preserve_as_observed": True,
        }
        for path in sorted(str(path) for path in record.get("observed_paths", []))
        if path in roles
    ]


def _alignment_steps() -> list[dict[str, str]]:
    return [
        {
            "step_id": "INGEST-ALIGN-001",
            "step_status": "PLANNED_ADVISORY_ONLY",
            "description": "Preserve existing ingest runners as observed entrypoints before any shared adapter contract.",
            "authority_boundary": "no runner behavior mutation",
        },
        {
            "step_id": "INGEST-ALIGN-002",
            "step_status": "PLANNED_ADVISORY_ONLY",
            "description": "Define core/oracle_signal.py as the future adapter-spine contract boundary.",
            "authority_boundary": "no module implementation in this plan",
        },
        {
            "step_id": "INGEST-ALIGN-003",
            "step_status": "PLANNED_ADVISORY_ONLY",
            "description": "Require a governed implementation decision before creating adapter code or routing hooks.",
            "authority_boundary": "operator decision required before implementation",
        },
    ]


def _acceptance_gates() -> list[dict[str, str]]:
    return [
        {
            "gate_id": "INGEST-GATE-001",
            "required_before": "core/oracle_signal.py creation",
            "status": "OPERATOR_DECISION_REQUIRED",
        },
        {
            "gate_id": "INGEST-GATE-002",
            "required_before": "runner behavior changes",
            "status": "SEPARATE_IMPLEMENTATION_PR_REQUIRED",
        },
        {
            "gate_id": "INGEST-GATE-003",
            "required_before": "route, scheduler, or runtime integration",
            "status": "AUTHORITY_DENIED",
        },
    ]


def build_global_ingest_adapter_spine_alignment_plan(
    *,
    repo_root: str | Path,
    terminal_state_path: str | Path = TERMINAL_STATE_JSON,
    repo_notion_diff_path: str | Path = REPO_NOTION_DIFF_JSON,
) -> dict[str, Any]:
    root = Path(repo_root)
    terminal_target = root / terminal_state_path
    diff_target = root / repo_notion_diff_path
    terminal_state = _load_json(terminal_target)
    diff_packet = _load_json(diff_target)
    operator_decision = _load_json(root / OPERATOR_DECISION_RECORD_PATH)
    separate_spec_plan = _load_json(root / SEPARATE_IMPLEMENTATION_SPEC_PLAN_PATH)
    implementation_spec = _load_json(root / IMPLEMENTATION_SPEC_PATH)
    record = _global_ingest_record(diff_packet)
    terminal_state_allows_planning = (
        terminal_state.get("artifact_type") == "NotionPatchQueueTerminalState.v1"
        and terminal_state.get("queue_is_terminal") is True
        and terminal_state.get("valid_for_execution") is False
    )
    diff_observes_partial = (
        record.get("match_strength") == "PARTIAL"
        and record.get("implementation_blocked") is not True
        and "core/oracle_signal.py" in record.get("missing_paths", [])
    )
    plan_ready = terminal_state_allows_planning and diff_observes_partial
    operator_decision_observed = (
        operator_decision.get("schema_version") == "GlobalIngestOperatorDecisionRecord.v1"
        and operator_decision.get("selected_decision") == "APPROVE_SEPARATE_IMPLEMENTATION_SPEC"
        and operator_decision.get("implementation_authorized") is False
        and operator_decision.get("execution_authority") is False
        and operator_decision.get("valid_for_execution") is False
    )
    separate_spec_plan_observed = (
        separate_spec_plan.get("schema_version") == "GlobalIngestSeparateImplementationSpecPlan.v1"
        and separate_spec_plan.get("status")
        in {
            "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_READY",
            "GLOBAL_INGEST_SEPARATE_IMPLEMENTATION_SPEC_PLAN_CONSUMED_BY_IMPLEMENTATION_SPEC",
        }
        and separate_spec_plan.get("implementation_authorized") is False
        and separate_spec_plan.get("execution_authority") is False
        and separate_spec_plan.get("valid_for_execution") is False
    )
    implementation_spec_observed = (
        implementation_spec.get("schema_version") == "GlobalIngestAdapterSpineImplementationSpec.v1"
        and implementation_spec.get("status") == "GLOBAL_INGEST_ADAPTER_SPINE_IMPLEMENTATION_SPEC_CONSUMED_ADVISORY_ONLY"
        and implementation_spec.get("implementation_pr_consumed") is True
        and implementation_spec.get("implementation_authorized") is False
        and implementation_spec.get("execution_authority") is False
        and implementation_spec.get("valid_for_execution") is False
    )
    downstream_spec_chain_observed = (
        plan_ready
        and operator_decision_observed
        and separate_spec_plan_observed
        and implementation_spec_observed
    )
    base: dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "plan_id": PLAN_ID,
        "plan_status": "ALIGNMENT_PLAN_EMITTED_ADVISORY_ONLY" if plan_ready else _NOT_COMPUTABLE,
        "patch_id": PATCH_ID,
        "notion_source": "ABRAXAS_PATCH_QUEUE_REVISED_001",
        "depends_on_artifacts": [
            Path(terminal_state_path).as_posix(),
            Path(repo_notion_diff_path).as_posix(),
        ],
        "source_artifact_hashes": {
            Path(terminal_state_path).as_posix(): _sha256(terminal_target),
            Path(repo_notion_diff_path).as_posix(): _sha256(diff_target),
            OPERATOR_DECISION_RECORD_PATH: _sha256(root / OPERATOR_DECISION_RECORD_PATH),
            SEPARATE_IMPLEMENTATION_SPEC_PLAN_PATH: _sha256(root / SEPARATE_IMPLEMENTATION_SPEC_PLAN_PATH),
            IMPLEMENTATION_SPEC_PATH: _sha256(root / IMPLEMENTATION_SPEC_PATH),
        },
        "target_surface": _TARGET_SURFACE,
        "target_paths": list(_TARGET_PATHS),
        "observed_entrypoints": _observed_entrypoints(record),
        "missing_paths": sorted(str(path) for path in record.get("missing_paths", [])),
        "alignment_steps": _alignment_steps(),
        "acceptance_gates": _acceptance_gates(),
        "blocked_actions": [
            "AUTO_CREATE_NEXT_PATCH",
            "LIVE_NOTION_WRITEBACK",
            "GITHUB_WRITEBACK_AUTOMATION",
            "CORE_ORACLE_SIGNAL_IMPLEMENTATION",
            "INGEST_RUNNER_BEHAVIOR_MUTATION",
            "PIPELINE_OR_ROUTE_MUTATION",
            "RUNTIME_OR_SCHEDULER_MUTATION",
            "CANON_PROMOTION",
            "EXECUTION_AUTHORITY_GRANT",
        ],
        "recommended_next_patch": _NOT_COMPUTABLE,
        "recommended_next_action": (
            "Global Ingest operator decision and implementation spec chain are already observed; hold with implementation authority denied"
            if downstream_spec_chain_observed
            else "hold for explicit governed operator decision before any Global Ingest implementation"
        ),
        "required_operator_input": (
            "no additional planning PR should be prepared from this alignment plan while downstream Global Ingest spec evidence is observed"
            if downstream_spec_chain_observed
            else "explicit governed operator decision approving a separate implementation spec is required "
            "before creating core/oracle_signal.py or mutating ingest runners"
        ),
        "safe_to_prepare_planning_pr": plan_ready and not downstream_spec_chain_observed,
        "downstream_spec_chain_observed": downstream_spec_chain_observed,
        "downstream_spec_chain": {
            "operator_decision_record": {
                "path": OPERATOR_DECISION_RECORD_PATH,
                "status": str(operator_decision.get("status", "NOT_COMPUTABLE")),
                "observed": operator_decision_observed,
            },
            "separate_implementation_spec_plan": {
                "path": SEPARATE_IMPLEMENTATION_SPEC_PLAN_PATH,
                "status": str(separate_spec_plan.get("status", "NOT_COMPUTABLE")),
                "observed": separate_spec_plan_observed,
            },
            "implementation_spec": {
                "path": IMPLEMENTATION_SPEC_PATH,
                "status": str(implementation_spec.get("status", "NOT_COMPUTABLE")),
                "observed": implementation_spec_observed,
            },
        },
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


def write_global_ingest_adapter_spine_alignment_plan(path: str | Path, packet: dict[str, Any]) -> None:
    write_canonical_json(path, packet)


def write_global_ingest_adapter_spine_alignment_plan_markdown(
    path: str | Path,
    packet: dict[str, Any],
) -> None:
    lines = [
        "# Global Ingest Adapter Spine Alignment Plan",
        "",
        f"- plan_id: {packet['plan_id']}",
        f"- plan_status: {packet['plan_status']}",
        f"- patch_id: {packet['patch_id']}",
        f"- target_surface: {packet['target_surface']}",
        f"- recommended_next_patch: {packet['recommended_next_patch']}",
        f"- recommended_next_action: {packet['recommended_next_action']}",
        f"- safe_to_auto_continue: {packet['safe_to_auto_continue']}",
        f"- implementation_allowed: {packet['implementation_allowed']}",
        f"- notion_writeback_allowed: {packet['notion_writeback_allowed']}",
        f"- github_writeback_allowed: {packet['github_writeback_allowed']}",
        "",
        "## Observed Entrypoints",
    ]
    for entrypoint in packet.get("observed_entrypoints", []):
        lines.append(f"- {entrypoint['path']} - {entrypoint['role']}")
    lines.extend(["", "## Missing Paths"])
    for missing_path in packet.get("missing_paths", []):
        lines.append(f"- {missing_path}")
    lines.extend(["", "## Alignment Steps"])
    for step in packet.get("alignment_steps", []):
        lines.append(f"- {step['step_id']}: {step['description']}")
    lines.extend(["", "## Acceptance Gates"])
    for gate in packet.get("acceptance_gates", []):
        lines.append(f"- {gate['gate_id']}: {gate['status']} before {gate['required_before']}")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
