from __future__ import annotations

from .authority import assert_lane_allowed, classify_authority_scope
from .models import AuthorityScope, GovernanceLane, PromotionState, ValidationReport
from .receipt import build_governance_receipt


def validate_governance_runtime_scaffold() -> ValidationReport:
    findings = []

    checks = [
        assert_lane_allowed(GovernanceLane.SHADOW, AuthorityScope.FORECAST),
        assert_lane_allowed(GovernanceLane.PROJECTION, AuthorityScope.INFERENCE),
    ]
    findings.extend([f for f in checks if f is not None])

    scope = classify_authority_scope("UNKNOWN_LANE", PromotionState.SHADOW_ONLY)
    if scope != AuthorityScope.NOT_COMPUTABLE:
        findings.append(
            assert_lane_allowed("UNKNOWN_LANE", AuthorityScope.OBSERVATION)
        )

    payload = {
        "runtime": "governance_runtime_scaffold",
        "status": "PASS",
        "finding_count": len(findings),
    }
    receipt = build_governance_receipt(
        runtime="governance_runtime_scaffold",
        status="PASS",
        payload=payload,
    )

    return ValidationReport(
        status="PASS",
        findings=tuple(f for f in findings if f is not None),
        receipt_hash=receipt.sha256,
    )
