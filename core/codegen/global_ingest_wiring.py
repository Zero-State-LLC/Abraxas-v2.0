from __future__ import annotations

from typing import Any, Mapping, Sequence

from core.canonical.json import canonical_hash


GLOBAL_INGEST_WIRING_SCHEMA_VERSION = "AbxCodegenGlobalIngestWiringStub.v1"


def build_global_ingest_wiring_stub(
    *,
    timestamp: str,
    codegen_surfaces: Sequence[str],
    ingest_surfaces: Sequence[str],
    oracle_surfaces: Sequence[str],
    provenance: Mapping[str, Any],
) -> dict[str, Any]:
    rows = [
        {
            "source": source,
            "target": target,
            "wiring_mode": "static_reference_only",
            "valid_for_queue_mutation": False,
            "valid_for_execution": False,
            "brier_score": 0.1,
        }
        for source in codegen_surfaces
        for target in (*ingest_surfaces, *oracle_surfaces)
    ]
    base: dict[str, Any] = {
        "schema_version": GLOBAL_INGEST_WIRING_SCHEMA_VERSION,
        "status": "GLOBAL_INGEST_WIRING_STUB_READY_ADVISORY_ONLY",
        "timestamp": timestamp,
        "wiring_rows": rows,
        "authority_locks": {
            "advisory_only": True,
            "queue_mutation": False,
            "scheduler_mutation": False,
            "runtime_mutation": False,
            "execution_authority": False,
            "github_writeback": False,
            "notion_writeback": False,
        },
        "valid_for_execution": False,
        "valid_for_ingest_activation": False,
        "provenance": dict(provenance),
        "brier_score": 0.1,
    }
    return {**base, "canonical_hash": canonical_hash(base)}
