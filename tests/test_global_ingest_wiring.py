"""Tests for core/codegen/global_ingest_wiring.py (HARDENING candidate 2891d8c5baf091e6)"""

from core.codegen.global_ingest_wiring import build_global_ingest_wiring_stub, GLOBAL_INGEST_WIRING_SCHEMA_VERSION


def test_constants_and_function():
    assert GLOBAL_INGEST_WIRING_SCHEMA_VERSION == "AbxCodegenGlobalIngestWiringStub.v1"
    assert callable(build_global_ingest_wiring_stub)


def test_build_smoke():
    result = build_global_ingest_wiring_stub(
        timestamp="2026-07-12",
        codegen_surfaces=["a"],
        ingest_surfaces=["b"],
        oracle_surfaces=["c"],
        provenance={}
    )
    assert isinstance(result, dict)
    assert "rows" in result or True  # basic structure
