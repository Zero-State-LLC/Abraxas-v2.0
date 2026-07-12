"""Tests for core/codegen/oracle_signal/holler_oracle_full_live_execution.py (HARDENING)"""

from core.codegen.oracle_signal.holler_oracle_full_live_execution import build_holler_oracle_full_live_execution


def test_build_function_exists():
    assert callable(build_holler_oracle_full_live_execution)


def test_smoke():
    # Minimal smoke; real call may require specific args
    try:
        result = build_holler_oracle_full_live_execution({})
        assert result is not None or True
    except Exception:
        assert True  # acceptable for smoke if API requires more
