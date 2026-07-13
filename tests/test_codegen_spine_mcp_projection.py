"""Tests for core/codegen/spine_mcp_projection.py (candidate fdc5e202e687f7b6)"""

import pytest
from core.codegen.spine_mcp_projection import (
    SPINE_MCP_SCHEMA_VERSION,
    SPINE_TOOLS,
    build_spine_mcp_projection,
    build_spine_query_projection,
    build_spine_forecast_projection,
)

def test_constants():
    assert SPINE_MCP_SCHEMA_VERSION == "AbxLoop805SpineMcpProjection.v1"
    assert "/spine/query" in SPINE_TOOLS
    assert "/spine/forecast" in SPINE_TOOLS

def test_build_query_projection():
    proj = build_spine_query_projection(timestamp="2026-07-12T00:00:00Z", query="test query")
    assert proj["schema_version"] == SPINE_MCP_SCHEMA_VERSION
    assert proj["tool_name"] == "/spine/query"
    assert proj["projection_status"] == "MCP_TOOL_PROJECTION_READY_NOT_EXPOSED"
    assert proj["valid_for_execution"] is False

def test_build_forecast_projection():
    proj = build_spine_forecast_projection(
        timestamp="2026-07-12T00:00:00Z",
        forecast_question="will it rain?",
        probability=0.42,
    )
    assert proj["tool_name"] == "/spine/forecast"
    assert proj["response_contract"]["brier_telemetry_required"] is True

def test_unsupported_tool_raises():
    with pytest.raises(ValueError):
        build_spine_mcp_projection(
            timestamp="2026-07-12T00:00:00Z",
            tool_name="/spine/unknown",
            request={},
        )
