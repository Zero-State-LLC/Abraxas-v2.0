"""Tests for core/codegen/spine_mcp_projection.py (candidate fdc5e202e687f7b6)"""

import pytest
from core.codegen.spine_mcp_projection import (
    build_spine_mcp_projection,
    build_spine_query_projection,
    build_spine_forecast_projection,
    SPINE_TOOLS,
)

def test_supported_tools():
    assert "/spine/query" in SPINE_TOOLS
    assert "/spine/forecast" in SPINE_TOOLS

def test_build_mcp_projection_basic():
    proj = build_spine_mcp_projection(
        timestamp="2026-07-12T00:00:00Z",
        tool_name="/spine/query",
        request={"query": "test"},
    )
    assert proj["schema_version"] == "AbxLoop805SpineMcpProjection.v1"
    assert proj["tool_name"] == "/spine/query"
    assert proj["projection_status"] == "MCP_TOOL_PROJECTION_READY_NOT_EXPOSED"
    assert proj["valid_for_live_mcp_exposure"] is False
    assert "canonical_hash" in proj

def test_query_projection():
    proj = build_spine_query_projection(timestamp="2026-07-12T00:00:00Z", query="foo")
    assert proj["tool_name"] == "/spine/query"

def test_forecast_projection():
    proj = build_spine_forecast_projection(
        timestamp="2026-07-12T00:00:00Z",
        forecast_question="will it rain?",
        probability=0.7,
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
