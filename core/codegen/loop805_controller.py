from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID


LOOP_CONTROLLER_SCHEMA_VERSION = "AbxLoop805ControllerPlan.v1"
LOOP_STEPS: tuple[str, ...] = ("PLAN", "EXECUTE", "MEASURE", "ADJUST")


def build_loop805_controller_plan(
    *,
    timestamp: str,
    task: str,
    measurements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": LOOP_CONTROLLER_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "controller_status": "PLAN_EXECUTE_MEASURE_ADJUST_SKELETON_READY",
        "timestamp": timestamp,
        "task": task,
        "cycle": [
            {
                "step": step,
                "status": "PROJECTED_ONLY",
                "operator_gate_required": True,
                "valid_for_execution": False,
                "brier_score": 0.1,
            }
            for step in LOOP_STEPS
        ],
        "measurements": [dict(item) for item in measurements],
        "quality_gates": {
            "max_tokens_per_full_loop": 420_000,
            "pyright_errors": 0,
            "ruff_errors": 0,
            "brier_improvement_or_revert": "OPERATOR_REVIEW_REQUIRED",
            "token_optimizer_required": "PLANNED_NOT_ENFORCED",
            "ccusage_required": "PLANNED_NOT_ENFORCED",
            "caveman_squeez_hooks": "PLANNED_NOT_ENFORCED",
        },
        "auto_pr_generation": {
            "authorized": False,
            "mode": "PROPOSAL_ONLY",
            "operator_gate_required": True,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_runtime_activation": False,
        "valid_for_auto_pr_generation": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
