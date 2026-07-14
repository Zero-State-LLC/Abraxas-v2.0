from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Literal

CheckStatus = Literal["passed", "failed"]
AdvisoryStatus = Literal["NOT_COMPUTABLE", "BLOCKED"]

STATUS_PASSED: CheckStatus = "passed"
STATUS_FAILED: CheckStatus = "failed"
STATUS_NOT_COMPUTABLE: AdvisoryStatus = "NOT_COMPUTABLE"
STATUS_BLOCKED: AdvisoryStatus = "BLOCKED"


@dataclass(frozen=True)
class StatusResult:
    status: CheckStatus | AdvisoryStatus
    reason: str
    details: dict[str, Any] = field(default_factory=dict)

    def model_dump(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "details": self.details,
        }


def status_from_bool(passed: bool) -> CheckStatus:
    return STATUS_PASSED if passed else STATUS_FAILED


def aggregate_check_status(statuses: Iterable[CheckStatus]) -> CheckStatus:
    return STATUS_FAILED if any(status != STATUS_PASSED for status in statuses) else STATUS_PASSED


def blocking_advisory_status(
    statuses: Iterable[str],
    *,
    not_computable: bool = False,
) -> AdvisoryStatus | None:
    if not_computable:
        return STATUS_NOT_COMPUTABLE
    if any(status == STATUS_BLOCKED for status in statuses):
        return STATUS_BLOCKED
    return None


def not_computable_unless_blocked(status: str) -> AdvisoryStatus:
    return STATUS_BLOCKED if status == STATUS_BLOCKED else STATUS_NOT_COMPUTABLE


def passed_result(reason: str = "passed", **details: Any) -> StatusResult:
    return StatusResult(status=STATUS_PASSED, reason=reason, details=details)


def failed_result(reason: str = "failed", **details: Any) -> StatusResult:
    return StatusResult(status=STATUS_FAILED, reason=reason, details=details)


def not_computable_result(reason: str, **details: Any) -> StatusResult:
    return StatusResult(status=STATUS_NOT_COMPUTABLE, reason=reason, details=details)


def blocked_result(reason: str, **details: Any) -> StatusResult:
    return StatusResult(status=STATUS_BLOCKED, reason=reason, details=details)
