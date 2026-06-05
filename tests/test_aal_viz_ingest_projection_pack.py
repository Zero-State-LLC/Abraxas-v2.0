from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.generated_artifact_registry import build_generated_artifact_registry
from core.ingest.aal_viz_ingest_projection_pack import (
    AUTHORITY,
    PATCH_ID,
    SCHEMA_VERSION,
    build_aal_viz_ingest_projection_pack,
    write_aal_viz_ingest_projection_pack,
)


def test_projection_pack_is_deterministic_and_projection_only() -> None:
    packet_a = build_aal_viz_ingest_projection_pack()
    packet_b = build_aal_viz_ingest_projection_pack()

    assert packet_a == packet_b
    assert packet_a["schema_version"] == SCHEMA_VERSION
    assert packet_a["patch_id"] == PATCH_ID
    assert packet_a["authority"] == AUTHORITY
    assert packet_a["projection_only"] is True
    assert packet_a["advisory_only"] is True
    assert packet_a["non_authoritative"] is True
    assert packet_a["forecast_authority"] is False
    assert packet_a["execution_authority"] is False


def test_projection_pack_surfaces_current_blocked_candidate_state() -> None:
    packet = build_aal_viz_ingest_projection_pack()
    tiles = {tile["tile_id"]: tile for tile in packet["tiles"]}

    assert tiles["ingest_scheduler"]["status"] == "ACTIVE"
    assert tiles["oracle_queue"]["status"] == "READY"
    assert tiles["candidate_outcome_binding"]["status"] == "BLOCKED_PENDING_OUTCOME_BINDING"
    assert tiles["brier_readiness"]["status"] == "BLOCKED_PENDING_OUTCOME_BINDING"
    assert tiles["authority_lock_panel"]["status"] == "LOCKED"
    assert packet["authority_badges"] == ["DATA", "SHADOW", "FORECAST_CANDIDATE", "PROJECTION_ONLY"]


def test_projection_pack_contract_writer_and_registry() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    packet = build_aal_viz_ingest_projection_pack()

    schema = json.loads(
        Path("contracts/ingest/aal_viz_ingest_projection_pack.v1.schema.json").read_text(encoding="utf-8")
    )
    jsonschema.validate(packet, schema)

    out = Path("out/projections/_tmp_aal_viz_ingest_projection_pack.latest.json")
    write_aal_viz_ingest_projection_pack(out, packet)
    assert out.with_suffix(".md").read_text(encoding="utf-8").endswith("\n")

    registry = build_generated_artifact_registry(Path(__file__).resolve().parents[1])
    emap = {entry.artifact_path: entry for entry in registry.entries}
    assert emap["out/projections/aal_viz_ingest_projection_pack_001.latest.json"].determinism_class == "DERIVED_OPTIONAL"
    assert emap["out/projections/aal_viz_ingest_projection_pack_001.latest.md"].determinism_class == "DERIVED_OPTIONAL"

    out.unlink(missing_ok=True)
    out.with_suffix(".md").unlink(missing_ok=True)
