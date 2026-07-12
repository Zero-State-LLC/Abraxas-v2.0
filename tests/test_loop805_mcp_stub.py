"""Tests for core/codegen/loop805_mcp_stub.py (HARDENING candidate 14308e91004d997f)

Covers module load and constants.
"""

from core.codegen.loop805_mcp_stub import LOOP_805_MCP_STUB_SCHEMA_VERSION


def test_schema_version():
    assert LOOP_805_MCP_STUB_SCHEMA_VERSION.startswith("AbxLoop805McpExposureStub")


def test_module_loads():
    import core.codegen.loop805_mcp_stub as m
    assert hasattr(m, "build_loop805_mcp_exposure_stub")
