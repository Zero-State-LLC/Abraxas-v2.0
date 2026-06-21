from __future__ import annotations

from typing import Any, Mapping

from core.canonical.json import canonical_hash
from core.codegen.loop805_operationalization import AUTHORITY_LOCKS, LOOP_805_ID


SPINE_MCP_SCHEMA_VERSION = "AbxLoop805SpineMcpProjection.v1"
SPINE_TOOLS: tuple[str, ...] = ("/spine/query", "/spine/forecast", "/spine/audit")


def build_spine_mcp_projection(
    *,
    timestamp: str,
    tool_name: str,
    request: Mapping[str, Any],
) -> dict[str, Any]:
    if tool_name not in SPINE_TOOLS:
        raise ValueError(f"unsupported spine projection tool: {tool_name}")

    base: dict[str, Any] = {
        "schema_version": SPINE_MCP_SCHEMA_VERSION,
        "loop_id": LOOP_805_ID,
        "tool_name": tool_name,
        "timestamp": timestamp,
        "request": dict(request),
        "projection_status": "MCP_TOOL_PROJECTION_READY_NOT_EXPOSED",
        "response_contract": {
            "provenance_required": True,
            "token_delta_required": True,
            "brier_telemetry_required": tool_name == "/spine/forecast",
            "live_tool_exposure": False,
        },
        "authority_locks": dict(AUTHORITY_LOCKS),
        "valid_for_execution": False,
        "valid_for_live_mcp_exposure": False,
        "valid_for_forecast_routing": False,
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}


def build_spine_query_projection(*, timestamp: str, query: str) -> dict[str, Any]:
    return build_spine_mcp_projection(
        timestamp=timestamp,
        tool_name="/spine/query",
        request={"query": query},
    )


def build_spine_forecast_projection(
    *,
    timestamp: str,
    forecast_question: str,
    probability: float,
) -> dict[str, Any]:
    return build_spine_mcp_projection(
        timestamp=timestamp,
        tool_name="/spine/forecast",
        request={
            "forecast_question": forecast_question,
            "probability": probability,
            "resolution_authorized": False,
        },
    )


def build_spine_audit_projection(*, timestamp: str, surface: str) -> dict[str, Any]:
    return build_spine_mcp_projection(
        timestamp=timestamp,
        tool_name="/spine/audit",
        request={"surface": surface},
    )
