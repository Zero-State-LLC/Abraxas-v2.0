from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from .models import AuthorityScope, GovernanceLane


def _lane_decorator(
    lane: GovernanceLane,
    scope: AuthorityScope,
    projection_only: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return fn(*args, **kwargs)

        wrapped.__abx_lane__ = lane.value
        wrapped.__abx_authority_scope__ = scope.value
        if projection_only:
            wrapped.__abx_projection_only__ = True
        return wrapped

    return decorator


shadow_only = _lane_decorator(GovernanceLane.SHADOW, AuthorityScope.OBSERVATION)
forecast_only = _lane_decorator(GovernanceLane.FORECAST, AuthorityScope.FORECAST)
projection_only = _lane_decorator(
    GovernanceLane.PROJECTION,
    AuthorityScope.RENDER,
    projection_only=True,
)
canon_only = _lane_decorator(GovernanceLane.CANON, AuthorityScope.CANON)
operator_only = _lane_decorator(GovernanceLane.OPERATOR, AuthorityScope.OPERATOR)
