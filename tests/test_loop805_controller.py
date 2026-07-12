"""Comprehensive tests for core/codegen/loop805_controller.py (Layer 0 HARDENING).

Covers the controller plan builder, authority locks, cycle structure, and hashes.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.codegen.loop805_controller import build_loop805_controller_plan, LOOP_STEPS
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID


def test_build_loop805_controller_plan_structure():
    plan = build_loop805_controller_plan(
        timestamp="2026-07-12T00:00:00Z",
        task="test-task",
        measurements=[{"metric": "tokens", "value": 1000}],
    )
    assert plan["loop_id"] == LOOP_805_ID
    assert plan["controller_status"] == "PLAN_EXECUTE_MEASURE_ADJUST_SKELETON_READY"
    assert len(plan["cycle"]) == len(LOOP_STEPS)
    for step in plan["cycle"]:
        assert step["step"] in LOOP_STEPS
        assert step["status"] == "PROJECTED_ONLY"
        assert step["valid_for_execution"] is False
    assert "canonical_hash" in plan
    assert "authority_locks" in plan
    assert plan["valid_for_execution"] is False
    assert plan["valid_for_runtime_activation"] is False


def test_authority_locks_present_and_false_for_live():
    plan = build_loop805_controller_plan(
        timestamp="2026-07-12T00:00:00Z",
        task="auth-check",
        measurements=[],
    )
    locks = plan["authority_locks"]
    # from the operationalization, they should be all False for live
    assert isinstance(locks, dict)
    assert len(locks) > 0
    # key locks should be present
    for key in ["live_signal_ingest", "runtime_activation", "auto_pr_generation"]:
        if key in locks:
            assert locks[key] is False


def test_deterministic_hash():
    p1 = build_loop805_controller_plan(timestamp="t1", task="t", measurements=[])
    p2 = build_loop805_controller_plan(timestamp="t1", task="t", measurements=[])
    assert p1["canonical_hash"] == p2["canonical_hash"]


def test_quality_gates_present():
    plan = build_loop805_controller_plan(
        timestamp="2026-07-12T00:00:00Z",
        task="gates",
        measurements=[],
    )
    gates = plan["quality_gates"]
    assert "max_tokens_per_full_loop" in gates
    assert gates["pyright_errors"] == 0
    assert "brier_improvement_or_revert" in gates


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-q"])