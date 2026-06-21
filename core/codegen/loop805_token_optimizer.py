from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash
from core.codegen.loop805_observability import (
    BASELINE_TOKENS_PER_TURN,
    TARGET_TOKENS_PER_TURN,
)
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID


LOOP_805_TOKEN_OPTIMIZER_SCHEMA_VERSION = "AbxLoop805TokenOptimizerStub.v1"


def build_loop805_token_optimizer_stub(
    *,
    timestamp: str,
    route_decisions: Sequence[Mapping[str, Any]],
    optimizer_names: Sequence[str],
) -> dict[str, Any]:
    observed_tokens = [
        int(decision["token_telemetry"]["estimated_total_tokens"])
        for decision in route_decisions
    ]
    average_tokens = (
        sum(observed_tokens) // len(observed_tokens)
        if observed_tokens
        else BASELINE_TOKENS_PER_TURN
    )
    base: dict[str, Any] = {
        "schema_version": LOOP_805_TOKEN_OPTIMIZER_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "stub_id": "ABX_LOOP_805_TOKEN_OPTIMIZER_STUB",
        "stub_status": "TOKEN_OPTIMIZER_STUB_READY_NOT_ENFORCED",
        "timestamp": timestamp,
        "optimizer_names": list(optimizer_names),
        "baseline_tokens_per_agent_turn": BASELINE_TOKENS_PER_TURN,
        "target_tokens_per_agent_turn": TARGET_TOKENS_PER_TURN,
        "observed_average_tokens": average_tokens,
        "observed_delta_vs_baseline": average_tokens - BASELINE_TOKENS_PER_TURN,
        "observed_reduction_ratio": _ratio_delta(
            average_tokens,
            BASELINE_TOKENS_PER_TURN,
        ),
        "target_met": average_tokens <= TARGET_TOKENS_PER_TURN,
        "enforcement": {
            "enabled": False,
            "mode": "ADVISORY_MATH_ONLY",
            "operator_gate_required": True,
            "brier_score": 0.1,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_ci_enforcement": False,
        "valid_for_token_rewrite": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def _ratio_delta(value: int, baseline: int) -> float:
    if baseline == 0:
        raise ValueError("baseline must be non-zero")
    return round((value - baseline) / baseline, 6)
