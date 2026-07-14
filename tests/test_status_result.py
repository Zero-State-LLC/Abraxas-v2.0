from __future__ import annotations

from core.status_result import (
    STATUS_BLOCKED,
    STATUS_FAILED,
    STATUS_NOT_COMPUTABLE,
    STATUS_PASSED,
    aggregate_check_status,
    blocked_result,
    blocking_advisory_status,
    failed_result,
    not_computable_result,
    not_computable_unless_blocked,
    passed_result,
    status_from_bool,
)


def test_status_from_bool_returns_canonical_check_statuses() -> None:
    assert status_from_bool(True) == STATUS_PASSED
    assert status_from_bool(False) == STATUS_FAILED


def test_aggregate_check_status_returns_passed_for_empty_input() -> None:
    assert aggregate_check_status(()) == STATUS_PASSED


def test_aggregate_check_status_returns_passed_when_all_inputs_pass() -> None:
    assert aggregate_check_status((STATUS_PASSED, STATUS_PASSED)) == STATUS_PASSED


def test_aggregate_check_status_returns_failed_when_any_input_fails() -> None:
    assert aggregate_check_status((STATUS_PASSED, STATUS_FAILED, STATUS_PASSED)) == STATUS_FAILED


def test_blocking_advisory_status_prioritizes_not_computable() -> None:
    assert (
        blocking_advisory_status((STATUS_BLOCKED,), not_computable=True)
        == STATUS_NOT_COMPUTABLE
    )


def test_blocking_advisory_status_detects_blocked_source() -> None:
    assert blocking_advisory_status(("ADVISORY_ONLY", STATUS_BLOCKED)) == STATUS_BLOCKED


def test_blocking_advisory_status_returns_none_without_terminal_advisory_status() -> None:
    assert blocking_advisory_status(("ADVISORY_ONLY", "PROJECTION_DEGRADED")) is None


def test_not_computable_unless_blocked_preserves_blocked_status() -> None:
    assert not_computable_unless_blocked(STATUS_BLOCKED) == STATUS_BLOCKED


def test_not_computable_unless_blocked_marks_non_blocked_status_not_computable() -> None:
    assert not_computable_unless_blocked("PASS") == STATUS_NOT_COMPUTABLE


def test_result_constructors_emit_stable_payloads() -> None:
    assert passed_result("ok", count=1).model_dump() == {
        "status": STATUS_PASSED,
        "reason": "ok",
        "details": {"count": 1},
    }
    assert failed_result("bad", path="x").model_dump() == {
        "status": STATUS_FAILED,
        "reason": "bad",
        "details": {"path": "x"},
    }
    assert not_computable_result("missing input").model_dump() == {
        "status": STATUS_NOT_COMPUTABLE,
        "reason": "missing input",
        "details": {},
    }
    assert blocked_result("operator hold", lane="review").model_dump() == {
        "status": STATUS_BLOCKED,
        "reason": "operator hold",
        "details": {"lane": "review"},
    }
