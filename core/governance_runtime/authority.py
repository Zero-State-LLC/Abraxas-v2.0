from __future__ import annotations

from collections.abc import Callable

from .models import (
    AuthorityScope,
    GovernanceLane,
    PromotionState,
    ValidationFinding,
    ValidationReport,
)
from .receipt import build_governance_receipt

LANE_COMPATIBILITY_MATRIX: dict[GovernanceLane, tuple[AuthorityScope, ...]] = {
    GovernanceLane.SHADOW: (
        AuthorityScope.OBSERVATION,
        AuthorityScope.DIAGNOSE,
        AuthorityScope.ANNOTATE,
    ),
    GovernanceLane.FORECAST: (AuthorityScope.FORECAST,),
    GovernanceLane.PROJECTION: (AuthorityScope.RENDER,),
    GovernanceLane.CANON: (AuthorityScope.DOCTRINE, AuthorityScope.REGISTRY, AuthorityScope.CANON),
    GovernanceLane.OPERATOR: (
        AuthorityScope.APPROVE,
        AuthorityScope.DENY,
        AuthorityScope.MANUAL_OVERRIDE,
        AuthorityScope.OPERATOR,
    ),
}


def classify_authority_scope(lane: GovernanceLane | str | None, promotion_state: PromotionState | str | None) -> AuthorityScope:
    try:
        lane_enum = lane if isinstance(lane, GovernanceLane) else GovernanceLane(str(lane))
    except Exception:
        return AuthorityScope.NOT_COMPUTABLE
    try:
        promotion_enum = promotion_state if isinstance(promotion_state, PromotionState) else PromotionState(str(promotion_state))
    except Exception:
        return AuthorityScope.NOT_COMPUTABLE

    if lane_enum == GovernanceLane.SHADOW:
        return AuthorityScope.OBSERVATION
    if lane_enum == GovernanceLane.FORECAST and promotion_enum in {PromotionState.CANARY, PromotionState.LIMITED_PROMOTION, PromotionState.CANON_ACTIVE}:
        return AuthorityScope.FORECAST
    if lane_enum == GovernanceLane.PROJECTION:
        return AuthorityScope.RENDER
    if lane_enum == GovernanceLane.CANON and promotion_enum == PromotionState.CANON_ACTIVE:
        return AuthorityScope.CANON
    if lane_enum == GovernanceLane.OPERATOR:
        return AuthorityScope.OPERATOR
    return AuthorityScope.NOT_COMPUTABLE


def assert_lane_allowed(source_lane: GovernanceLane | str | None, target_scope: AuthorityScope | str | None) -> ValidationFinding | None:
    try:
        lane_enum = source_lane if isinstance(source_lane, GovernanceLane) else GovernanceLane(str(source_lane))
    except Exception:
        return ValidationFinding("LANE_UNKNOWN", "Lane is unknown and cannot be validated.", severity="not_computable", source_lane=str(source_lane), target_scope=str(target_scope))
    try:
        scope_enum = target_scope if isinstance(target_scope, AuthorityScope) else AuthorityScope(str(target_scope))
    except Exception:
        return ValidationFinding("SCOPE_UNKNOWN", "Target scope is unknown and cannot be validated.", severity="not_computable", source_lane=lane_enum.value, target_scope=str(target_scope))

    if scope_enum not in LANE_COMPATIBILITY_MATRIX[lane_enum]:
        return ValidationFinding("LANE_SCOPE_DENIED", "Lane is not allowed to claim target authority scope.", source_lane=lane_enum.value, target_scope=scope_enum.value)
    return None


def validate_lane_metadata(callable_obj: Callable[..., object]) -> ValidationReport:
    findings: list[ValidationFinding] = []
    lane = getattr(callable_obj, "__abx_lane__", None)
    scope = getattr(callable_obj, "__abx_authority_scope__", None)
    projection_only = bool(getattr(callable_obj, "__abx_projection_only__", False))

    finding = assert_lane_allowed(lane, scope)
    if finding is not None:
        findings.append(finding)

    if lane == GovernanceLane.PROJECTION.value and scope != AuthorityScope.RENDER.value:
        findings.append(ValidationFinding("PROJECTION_SCOPE_VIOLATION", "Projection lane must remain render-only.", source_lane=lane, target_scope=str(scope)))
    if projection_only and scope == AuthorityScope.INFERENCE.value:
        findings.append(ValidationFinding("PROJECTION_INFERENCE_DENIED", "Projection-only callable cannot claim inference authority.", source_lane=lane, target_scope=str(scope)))

    payload = {"runtime": "lane_enforcement", "callable": getattr(callable_obj, "__name__", "unknown"), "finding_count": len(findings), "status": "PASS" if not findings else "FAIL"}
    receipt = build_governance_receipt("lane_enforcement", payload["status"], payload)
    return ValidationReport(status=payload["status"], findings=tuple(findings), receipt_hash=receipt.sha256)
